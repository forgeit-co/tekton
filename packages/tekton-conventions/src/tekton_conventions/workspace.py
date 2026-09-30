from pathlib import Path

from tekton_conventions._machinery import Rule, Violation, workspace_members

GATE_PATH = Path("tests/architecture/test_conventions.py")


def members_carry_convention_gates() -> Rule:
    def check(package_root: Path) -> list[Violation]:
        workspace_root = next(
            candidate for candidate in package_root.parents if (candidate / "uv.lock").is_file()
        )
        return [
            Violation(
                member / GATE_PATH,
                f"workspace member {member.relative_to(workspace_root)} has no convention gate",
            )
            for member in workspace_members(workspace_root)
            if not (member / GATE_PATH).is_file()
        ]

    return Rule("Every workspace member carries a convention gate", check)
