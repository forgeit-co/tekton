import ast
from pathlib import Path

from tekton_conventions._machinery import Rule, Violation


def backend_environment_reads_are_confined() -> Rule:
    return Rule(
        "Backend environment reads are confined to configuration bootstrap",
        _check_backend_environment_reads,
    )


def _check_backend_environment_reads(root: Path) -> list[Violation]:
    package_directory = root / "src/tekton"
    if not package_directory.is_dir():
        raise RuntimeError(f"{root} has no src/tekton package")

    violations: list[Violation] = []
    for source_path in sorted(package_directory.rglob("*.py")):
        relative_path = source_path.relative_to(package_directory)
        is_configuration_module = relative_path.parts[:2] == ("infrastructure", "config")
        if is_configuration_module:
            continue

        try:
            module = ast.parse(source_path.read_bytes(), filename=str(source_path))
        except (OSError, SyntaxError, ValueError) as error:
            violations.append(Violation(source_path, f"Cannot parse source module: {error}"))
            continue

        operating_system_names = {
            alias.asname or "os"
            for node in module.body
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name == "os"
        }
        environment_names = {
            alias.asname or alias.name
            for node in module.body
            if isinstance(node, ast.ImportFrom) and node.module == "os"
            for alias in node.names
            if alias.name in {"environ", "getenv"}
        }

        for node in ast.walk(module):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                if node.value.id in operating_system_names and node.attr in {"environ", "getenv"}:
                    message = f"Process environment read at line {node.lineno}"
                    violations.append(Violation(source_path, message))
            elif isinstance(node, ast.Name) and node.id in environment_names:
                message = f"Process environment read at line {node.lineno}"
                violations.append(Violation(source_path, message))

    return violations
