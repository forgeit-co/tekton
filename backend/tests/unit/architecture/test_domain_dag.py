import tomllib
from pathlib import Path

from tekton_conventions import contracts_from_specification, domain_dependencies

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
EXPECTED_DOMAIN_MODULES = {
    "workflow",
    "projections",
    "decisions",
    "proposals",
    "eligibility",
    "plots",
    "localities",
    "budget",
    "fx",
    "tasks",
    "approvals",
    "privacy",
    "documents",
    "sources",
    "runs",
    "sessions",
    "metering",
    "mail",
    "knowledge",
    "deadlines",
    "scheduling",
    "notifications",
}


def test_every_domain_package_has_a_specification_dag_row():
    specification = (REPOSITORY_ROOT / "docs/technical-spec.md").read_text(encoding="utf-8")
    dag_modules = set(domain_dependencies(specification))

    package_modules = {
        package.name
        for package in (REPOSITORY_ROOT / "backend/src/tekton/domain").iterdir()
        if package.is_dir()
    }
    assert package_modules == dag_modules & EXPECTED_DOMAIN_MODULES, (
        f"Domain package/DAG mismatch: packages={package_modules}, DAG={dag_modules}"
    )


def test_generated_import_contracts_match_backend_manifest():
    backend_manifest = tomllib.loads(
        (REPOSITORY_ROOT / "backend/pyproject.toml").read_text(encoding="utf-8")
    )
    committed_contracts = backend_manifest["tool"]["importlinter"]["contracts"]
    specification = (REPOSITORY_ROOT / "docs/technical-spec.md").read_text(encoding="utf-8")
    generated_contracts = contracts_from_specification(specification)
    assert committed_contracts == generated_contracts, (
        "Generated import contracts differ from backend/pyproject.toml"
    )
    application_contract_names = {
        contract["name"]
        for contract in committed_contracts
        if contract["name"].startswith("Application ")
    }
    expected_application_modules = set(domain_dependencies(specification)) | {
        "auth",
        "backup",
        "health",
        "settings",
        "eventlog",
        "eventlog.contracts",
        "shared",
        "commit",
    }
    assert application_contract_names == {
        f"Application {module} follows its DAG row" for module in expected_application_modules
    }, "Every application module requires an explicit DAG contract"
    assert any(
        contract["name"] == "Only composition imports application commit"
        and set(contract["source_modules"])
        == {
            "tekton.application",
            "tekton.domain",
            "tekton.presentation",
            "tekton.infrastructure",
            "tekton.entrypoints",
        }
        for contract in committed_contracts
    ), "Application commit must be restricted to composition"
    assert any(
        contract["name"] == "Application commit follows its DAG row"
        and {
            "tekton.application.auth",
            "tekton.application.eventlog",
            "tekton.domain.decisions",
        }
        <= set(contract["forbidden_modules"])
        for contract in committed_contracts
    ), "Application commit may only depend on shared, projections, and kernel"
