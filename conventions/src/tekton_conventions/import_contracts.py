from pathlib import Path
from typing import cast

DOMAIN_LAYER_FORBIDDEN = (
    "tekton.application",
    "tekton.presentation",
    "tekton.infrastructure",
    "tekton.composition",
    "tekton.entrypoints",
)
DOMAIN_MODULE_FORBIDDEN = (
    "tekton.infrastructure",
    "tekton.composition",
    "tekton.entrypoints",
)
APPLICATION_LAYER_FORBIDDEN = (
    "tekton.presentation",
    "tekton.infrastructure",
    "tekton.composition",
    "tekton.entrypoints",
)
FRAMEWORK_MODULES = ("fastapi", "sqlalchemy", "pydantic", "starlette", "httpx", "alembic")
# Domainless application modules receive no business-domain capabilities.
APPLICATION_SHARED_MODULES = ("shared", "eventlog.contracts")
APPLICATION_MODULES = ("auth", "backup", "health", "settings", "eventlog")
APPLICATION_COMMIT_MODULES = ("shared", "projections")
APPLICATION_ONLY_MODULES = ("commit",)
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SPECIFICATION_PATH = REPOSITORY_ROOT / "docs" / "technical-spec.md"
BACKEND_MANIFEST_PATH = REPOSITORY_ROOT / "backend" / "pyproject.toml"


def domain_dependencies(specification: str) -> dict[str, tuple[str, ...]]:
    dependencies_by_module: dict[str, tuple[str, ...]] = {}
    reading_domain_dag = False
    for line in specification.splitlines():
        if line.startswith("| Module | May import"):
            reading_domain_dag = True
            continue
        if reading_domain_dag and not line.startswith("|"):
            break
        if reading_domain_dag:
            columns = [column.strip() for column in line.strip().split("|")]
            if len(columns) < 3 or columns[1].startswith("-"):
                continue
            module_names = tuple(
                module.strip().strip("`") for module in columns[1].split(",") if module.strip()
            )
            dependency_names = tuple(
                dependency.strip().strip("`")
                for dependency in columns[2].split(",")
                if dependency.strip() and dependency.strip() != "—"
            )
            if not module_names or module_names[0] == "Module":
                continue
            for module in module_names:
                dependencies_by_module[module] = dependency_names
    return dependencies_by_module


def contracts_from_specification(specification: str) -> list[dict[str, object]]:
    modules = domain_dependencies(specification)
    application_modules = tuple(
        dict.fromkeys(
            (
                *modules,
                *APPLICATION_MODULES,
                *APPLICATION_SHARED_MODULES,
                *APPLICATION_ONLY_MODULES,
            )
        )
    )
    contracts: list[dict[str, object]] = [
        {
            "name": "Backend layers",
            "type": "layers",
            "layers": [
                "tekton.presentation",
                "tekton.application",
                "tekton.domain",
                "tekton.kernel",
            ],
        },
        {
            "name": "Domain and kernel import no frameworks",
            "type": "forbidden",
            "source_modules": ["tekton.domain", "tekton.kernel"],
            "forbidden_modules": list(FRAMEWORK_MODULES),
        },
    ]
    for module, allowed_dependencies in modules.items():
        forbidden_modules = [
            f"tekton.domain.{other_module}"
            for other_module in modules
            if other_module != module and other_module not in allowed_dependencies
        ]
        forbidden_modules.extend(DOMAIN_MODULE_FORBIDDEN)
        contracts.append(
            {
                "name": f"Domain {module} follows its DAG row",
                "type": "forbidden",
                "source_modules": [f"tekton.domain.{module}"],
                "forbidden_modules": forbidden_modules,
            }
        )

    for module in application_modules:
        allowed_dependencies = modules.get(module, ())
        if module == "commit":
            allowed_dependencies = APPLICATION_COMMIT_MODULES
        allowed_dependencies = (*allowed_dependencies, *APPLICATION_SHARED_MODULES)
        forbidden_modules = [
            f"tekton.application.{other_module}"
            for other_module in application_modules
            if other_module != module and other_module not in allowed_dependencies
        ]
        forbidden_domain_modules = (
            set(modules) - set(modules.get(module, ())) if module in modules else set(modules)
        )
        forbidden_modules.extend(
            f"tekton.domain.{domain_module}" for domain_module in sorted(forbidden_domain_modules)
        )
        forbidden_modules.extend(APPLICATION_LAYER_FORBIDDEN)
        if module in APPLICATION_SHARED_MODULES:
            forbidden_modules.extend(
                f"tekton.application.{other_module}"
                for other_module in APPLICATION_SHARED_MODULES
                if other_module != module
            )
        contracts.append(
            {
                "name": f"Application {module} follows its DAG row",
                "type": "forbidden",
                "source_modules": [f"tekton.application.{module}"],
                "forbidden_modules": forbidden_modules,
            }
        )

    contracts.append(
        {
            "name": "Only composition imports application commit",
            "type": "forbidden",
            "source_modules": [
                "tekton.application",
                "tekton.domain",
                "tekton.presentation",
                "tekton.infrastructure",
                "tekton.entrypoints",
            ],
            "forbidden_modules": ["tekton.application.commit"],
        }
    )
    return contracts


def render_contracts(specification: str) -> str:
    lines = [
        "[tool.importlinter]",
        'root_package = "tekton"',
        "include_external_packages = true",
        "",
    ]
    for contract in contracts_from_specification(specification):
        lines.extend(
            [
                "[[tool.importlinter.contracts]]",
                f'name = "{contract["name"]}"',
                f'type = "{contract["type"]}"',
            ]
        )
        for key in ("layers", "source_modules", "forbidden_modules"):
            value = contract.get(key)
            if isinstance(value, list):
                string_values = cast(list[str], value)
                rendered = ", ".join(f'"{item}"' for item in string_values)
                lines.append(f"{key} = [{rendered}]")
        if contract.get("allow_indirect_imports") is True:
            lines.append("allow_indirect_imports = true")
        ignore_imports = contract.get("ignore_imports")
        if isinstance(ignore_imports, list):
            string_imports = cast(list[str], ignore_imports)
            lines.append("ignore_imports = [")
            lines.extend(f'    "{item}",' for item in string_imports)
            lines.append("]")
        lines.append("")
    return "\n".join(lines)


def update_backend_manifest():
    manifest = BACKEND_MANIFEST_PATH.read_text(encoding="utf-8")
    marker = "[tool.importlinter]"
    if marker not in manifest:
        raise RuntimeError(f"{BACKEND_MANIFEST_PATH} has no {marker} section")
    specification = SPECIFICATION_PATH.read_text(encoding="utf-8")
    BACKEND_MANIFEST_PATH.write_text(
        manifest.split(marker, maxsplit=1)[0] + render_contracts(specification),
        encoding="utf-8",
    )


if __name__ == "__main__":
    update_backend_manifest()
