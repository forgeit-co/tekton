from tekton_conventions import (
    members_carry_convention_gates,
    module_filenames_follow_canonical_pattern,
    modules_contain_only_tests,
    no_tests_under_src,
    package_root,
    pytest_references_use_canonical_names,
)


def test_test_modules_contain_only_tests():
    modules_contain_only_tests().enforce(package_root(__file__))


def test_no_tests_under_src():
    no_tests_under_src().enforce(package_root(__file__))


def test_test_module_filenames_follow_canonical_pattern():
    module_filenames_follow_canonical_pattern().enforce(package_root(__file__))


def test_pytest_references_use_canonical_names():
    pytest_references_use_canonical_names().enforce(package_root(__file__))


def test_every_workspace_member_has_a_convention_gate():
    members_carry_convention_gates().enforce(package_root(__file__))
