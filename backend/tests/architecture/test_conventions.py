from tekton_conventions import (
    backend_environment_reads_are_confined,
    contracts_from_specification,
    module_filenames_follow_canonical_pattern,
    modules_contain_only_tests,
    no_tests_under_src,
    package_root,
    pytest_references_use_canonical_names,
)


def test_import_contracts_allow_indirect_composition_wiring():
    repository_root = package_root(__file__).parent
    specification_path = repository_root / "docs/technical-spec.md"
    contracts = contracts_from_specification(specification_path.read_text(encoding="utf-8"))
    commit_contract = next(
        contract
        for contract in contracts
        if contract["name"] == "Only composition imports application commit"
    )

    assert commit_contract.get("allow_indirect_imports") is True, (
        "Entrypoints must reach the commit pipeline only through composition"
    )


def test_backend_environment_reads_are_confined_to_bootstrap():
    backend_environment_reads_are_confined().enforce(package_root(__file__))


def test_test_modules_contain_only_tests():
    modules_contain_only_tests().enforce(package_root(__file__))


def test_no_tests_under_src():
    no_tests_under_src().enforce(package_root(__file__))


def test_test_module_filenames_follow_canonical_pattern():
    module_filenames_follow_canonical_pattern().enforce(package_root(__file__))


def test_pytest_references_use_canonical_names():
    pytest_references_use_canonical_names().enforce(package_root(__file__))


def test_backend_has_package_root():
    backend_root = package_root(__file__)
    assert backend_root.name == "backend", "Backend gate resolved a different package"
