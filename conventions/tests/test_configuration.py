from pathlib import Path

import pytest

from tekton_conventions import application_and_domain_do_not_read_environment


def test_application_and_domain_environment_rule_flags_os_environ_reads(tmp_path: Path):
    application_directory = tmp_path / "src/tekton/application"
    application_directory.mkdir(parents=True)
    (application_directory / "sample.py").write_text(
        "import os\n\nCONFIG = os.environ.get('SETTING')\n", encoding="utf-8"
    )

    with pytest.raises(AssertionError, match="Process environment read"):
        application_and_domain_do_not_read_environment().enforce(tmp_path)


def test_application_and_domain_environment_rule_allows_reads_in_configuration_boundary(
    tmp_path: Path,
):
    application_directory = tmp_path / "src/tekton/application"
    application_directory.mkdir(parents=True)
    (application_directory / "sample.py").write_text(
        "configuration = load_configuration()\n", encoding="utf-8"
    )

    application_and_domain_do_not_read_environment().enforce(tmp_path)
