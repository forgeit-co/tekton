from tekton_conventions import package_root


def test_edge_has_package_root():
    package_root(__file__)
