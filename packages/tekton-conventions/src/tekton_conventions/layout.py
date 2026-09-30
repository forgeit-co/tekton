import ast
from pathlib import Path

from tekton_conventions._machinery import Rule, Violation

TEST_MODULE_GLOB = "test_*.py"
NON_CANONICAL_TEST_MODULE_GLOB = "*_test.py"
PYTEST_MODULES = {"pytest", "pytest_asyncio"}


def modules_contain_only_tests() -> Rule:
    return Rule(
        "Test modules contain only test functions and test classes",
        _check_test_module_contents,
    )


def no_tests_under_src() -> Rule:
    return Rule("Source trees do not contain tests directories", _check_no_tests_under_src)


def module_filenames_follow_canonical_pattern() -> Rule:
    return Rule(
        "Test modules use the canonical test_*.py filename pattern",
        _check_test_module_filenames,
    )


def pytest_references_use_canonical_names() -> Rule:
    return Rule(
        "Pytest modules are imported without aliases",
        _check_pytest_imports,
    )


def _check_no_tests_under_src(root: Path) -> list[Violation]:
    source_directory = root / "src"
    if not source_directory.is_dir():
        raise RuntimeError(f"{root} has no src/ directory")

    return [
        Violation(tests_directory, "Move tests outside src/")
        for tests_directory in sorted(source_directory.rglob("tests"))
        if tests_directory.is_dir()
    ]


def _test_modules(root: Path) -> list[Path]:
    tests_directory = root / "tests"
    if not tests_directory.is_dir():
        raise RuntimeError(f"{root} has no tests/ directory")
    return sorted(tests_directory.rglob("*.py"))


def _check_test_module_contents(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    for source_path in _test_modules(root):
        if not source_path.name.startswith("test_"):
            continue
        try:
            module = ast.parse(source_path.read_bytes(), filename=str(source_path))
        except (OSError, SyntaxError, ValueError) as error:
            violations.append(Violation(source_path, f"Cannot parse test module: {error}"))
            continue
        for node in module.body:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Pass)):
                continue
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                continue
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                "test_"
            ):
                continue
            if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                continue
            violations.append(
                Violation(source_path, f"Module-level {type(node).__name__} is not a test")
            )
    return violations


def _check_test_module_filenames(root: Path) -> list[Violation]:
    return [
        Violation(source_path, "Rename test module to use the test_*.py pattern")
        for source_path in _test_modules(root)
        if source_path.name.endswith("_test.py") and not source_path.name.startswith("test_")
    ]


def _check_pytest_imports(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    for source_path in _test_modules(root):
        try:
            module = ast.parse(source_path.read_bytes(), filename=str(source_path))
        except (OSError, SyntaxError, ValueError) as error:
            violations.append(Violation(source_path, f"Cannot parse test module: {error}"))
            continue
        for node in module.body:
            if isinstance(node, ast.Import):
                violations.extend(
                    Violation(source_path, f"Import {alias.name} without an alias")
                    for alias in node.names
                    if alias.name in PYTEST_MODULES and alias.asname is not None
                )
            elif isinstance(node, ast.ImportFrom) and node.module in PYTEST_MODULES:
                violations.extend(
                    Violation(source_path, f"Import {alias.name} without an alias")
                    for alias in node.names
                    if alias.asname is not None
                )
    return violations
