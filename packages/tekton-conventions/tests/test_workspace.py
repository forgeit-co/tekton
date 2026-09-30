from pathlib import Path

import pytest

from tekton_conventions import members_carry_convention_gates


def test_workspace_coverage_flags_member_without_gate(tmp_path: Path):
    (tmp_path / "uv.lock").write_text(
        'version = 1\n[manifest]\nmembers = ["alpha", "beta"]\n'
        '[[package]]\nname = "alpha"\nsource = { editable = "alpha" }\n'
        '[[package]]\nname = "beta"\nsource = { virtual = "beta" }\n',
        encoding="utf-8",
    )
    alpha_gate = tmp_path / "alpha/tests/architecture/test_conventions.py"
    alpha_gate.parent.mkdir(parents=True)
    alpha_gate.touch()
    (tmp_path / "beta").mkdir()

    with pytest.raises(AssertionError, match="beta"):
        members_carry_convention_gates().enforce(tmp_path / "alpha")


def test_workspace_coverage_passes_when_every_member_has_gate(tmp_path: Path):
    (tmp_path / "uv.lock").write_text(
        'version = 1\n[manifest]\nmembers = ["alpha", "beta"]\n'
        '[[package]]\nname = "alpha"\nsource = { editable = "alpha" }\n'
        '[[package]]\nname = "beta"\nsource = { virtual = "beta" }\n',
        encoding="utf-8",
    )
    for member in ("alpha", "beta"):
        gate = tmp_path / member / "tests/architecture/test_conventions.py"
        gate.parent.mkdir(parents=True)
        gate.touch()

    members_carry_convention_gates().enforce(tmp_path / "alpha")
