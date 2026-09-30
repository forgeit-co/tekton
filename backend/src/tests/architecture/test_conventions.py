from tekton_conventions import (
    module_filenames_follow_canonical_pattern,
    modules_contain_only_tests,
    package_root,
    pytest_references_use_canonical_names,
)


def test_test_modules_contain_only_tests():
    modules_contain_only_tests().enforce(package_root(__file__))


def test_test_module_filenames_follow_canonical_pattern():
    module_filenames_follow_canonical_pattern().enforce(package_root(__file__))


def test_pytest_references_use_canonical_names():
    pytest_references_use_canonical_names().enforce(package_root(__file__))


def test_backend_has_package_root():
    backend_root = package_root(__file__)
    assert backend_root.name == "backend", "Backend gate resolved a different package"
