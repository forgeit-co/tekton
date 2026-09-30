import ast
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
APPLICATION_ROOT = REPOSITORY_ROOT / "backend/src/tekton/application"
ALLOWED_COMMIT_DIRECTORY = APPLICATION_ROOT / "commit"


def test_application_outside_commit_pipeline_never_calls_commit():
    violations: list[str] = []
    for source_path in APPLICATION_ROOT.rglob("*.py"):
        if source_path.is_relative_to(ALLOWED_COMMIT_DIRECTORY):
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
