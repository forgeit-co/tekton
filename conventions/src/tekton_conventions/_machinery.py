import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Violation:
    path: Path
    message: str


@dataclass(frozen=True, slots=True)
class Rule:
    description: str
    check: Callable[[Path], list[Violation]]

    def enforce(self, root: Path) -> None:
        violations = self.check(root)
        if violations:
            details = "\n".join(
                f"{violation.path}: {violation.message}" for violation in violations
            )
            raise AssertionError(f"{self.description}:\n{details}")


def package_root(marker: str) -> Path:
    for candidate in Path(marker).resolve().parents:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise RuntimeError(f"No pyproject.toml above {marker}")


def workspace_members(root: Path) -> list[Path]:
    lockfile_data = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    member_names = lockfile_data.get("manifest", {}).get("members", [])
    package_paths = {
        package["name"]: package["source"].get("editable", package["source"].get("virtual"))
        for package in lockfile_data.get("package", [])
        if "editable" in package.get("source", {}) or "virtual" in package.get("source", {})
    }
    return [root / package_paths[name] for name in member_names]
