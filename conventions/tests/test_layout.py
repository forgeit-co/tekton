from pathlib import Path

import pytest

from tekton_conventions import (
    module_filenames_follow_canonical_pattern,
    modules_contain_only_tests,
    pytest_references_use_canonical_names,
)


def test_modules_contain_only_tests_flags_module_helper(tmp_path: Path):
    tests_directory = tmp_path / "tests"
    tests_directory.mkdir()
    (tests_directory / "test_sample.py").write_text(
        "def build_sample():\n    return object()\n\n"
        "def test_sample():\n    assert build_sample()\n",
        encoding="utf-8",
    )

    with pytest.raises(
        AssertionError,
        match="FunctionDef",
    ):
        modules_contain_only_tests().enforce(tmp_path)


def test_modules_contain_only_tests_accepts_test_functions(tmp_path: Path):
    tests_directory = tmp_path / "tests"
    tests_directory.mkdir()
    (tests_directory / "test_sample.py").write_text(
        "def test_sample():\n    assert True\n", encoding="utf-8"
    )

    modules_contain_only_tests().enforce(tmp_path)


def test_module_filenames_follow_canonical_pattern_flags_suffix_test(tmp_path: Path):
    tests_directory = tmp_path / "tests"
    tests_directory.mkdir()
    (tests_directory / "sample_test.py").touch()

    with pytest.raises(AssertionError, match="sample_test.py"):
        module_filenames_follow_canonical_pattern().enforce(tmp_path)


def test_module_filenames_follow_canonical_pattern_accepts_prefix(tmp_path: Path):
    tests_directory = tmp_path / "tests"
    tests_directory.mkdir()
    (tests_directory / "test_sample.py").write_text("", encoding="utf-8")

    module_filenames_follow_canonical_pattern().enforce(tmp_path)


def test_pytest_references_use_canonical_names_flags_alias(tmp_path: Path):
    tests_directory = tmp_path / "tests"
    tests_directory.mkdir()
    (tests_directory / "test_sample.py").write_text("import pytest as pt\n", encoding="utf-8")

    with pytest.raises(AssertionError, match="without an alias"):
        pytest_references_use_canonical_names().enforce(tmp_path)


def test_pytest_references_use_canonical_names_accepts_canonical_import(tmp_path: Path):
    tests_directory = tmp_path / "tests"
    tests_directory.mkdir()
    (tests_directory / "test_sample.py").write_text("import pytest\n", encoding="utf-8")

    pytest_references_use_canonical_names().enforce(tmp_path)
