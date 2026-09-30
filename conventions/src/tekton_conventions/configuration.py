import ast
from pathlib import Path

from tekton_conventions._machinery import Rule, Violation

APPLICATION_AND_DOMAIN_DIRECTORIES = ("src/tekton/application", "src/tekton/domain")


def application_and_domain_do_not_read_environment() -> Rule:
    return Rule(
        "Application and domain modules do not read the process environment",
        _check_application_and_domain_environment_reads,
    )


def _check_application_and_domain_environment_reads(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    for relative_directory in APPLICATION_AND_DOMAIN_DIRECTORIES:
        source_directory = root / relative_directory
        if not source_directory.is_dir():
            continue
        for source_path in sorted(source_directory.rglob("*.py")):
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
                    if node.value.id in operating_system_names and node.attr in {
                        "environ",
                        "getenv",
                    }:
                        message = f"Process environment read at line {node.lineno}"
                        violations.append(Violation(source_path, message))
                elif isinstance(node, ast.Name) and node.id in environment_names:
                    message = f"Process environment read at line {node.lineno}"
                    violations.append(Violation(source_path, message))

    return violations
