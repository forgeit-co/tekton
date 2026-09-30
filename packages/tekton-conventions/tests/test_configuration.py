from pathlib import Path

import pytest

from tekton_conventions import backend_environment_reads_are_confined


def test_backend_environment_rule_flags_os_environ_read_in_composition(tmp_path: Path):
    composition_directory = tmp_path / "src/tekton/composition"
    composition_directory.mkdir(parents=True)
    (composition_directory / "sample.py").write_text(
        "import os\n\nCONFIG = os.environ.get('SETTING')\n", encoding="utf-8"
    )

    with pytest.raises(AssertionError, match="Process environment read"):
        backend_environment_reads_are_confined().enforce(tmp_path)


def test_backend_environment_rule_allows_configuration_boundary_reads(tmp_path: Path):
    configuration_directory = tmp_path / "src/tekton/infrastructure/config"
    configuration_directory.mkdir(parents=True)
    (configuration_directory / "bootstrap.py").write_text(
        "import os\n\nCONFIG = os.environ.get('SETTING')\n", encoding="utf-8"
    )

    backend_environment_reads_are_confined().enforce(tmp_path)


def test_backend_environment_rule_flags_entrypoint_environment_reads(tmp_path: Path):
    entrypoint_directory = tmp_path / "src/tekton/entrypoints"
    entrypoint_directory.mkdir(parents=True)
    (entrypoint_directory / "api.py").write_text(
        "import os\n\nCONFIG = os.environ.get('SETTING')\n", encoding="utf-8"
    )

    with pytest.raises(AssertionError, match="Process environment read"):
        backend_environment_reads_are_confined().enforce(tmp_path)
