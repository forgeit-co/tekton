import ast
from pathlib import Path


def test_application_outside_commit_pipeline_never_calls_commit():
    application_root = Path(__file__).resolve().parents[4] / "backend/src/tekton/application"
    allowed_commit_directory = application_root / "commit"
    violations: list[str] = []
    for source_path in application_root.rglob("*.py"):
        if source_path.is_relative_to(allowed_commit_directory):
            continue
        module = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(module):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "commit"
            ):
                violations.append(f"{source_path}:{node.lineno}")

    assert not violations, f"Commit calls outside application/commit: {violations}"
