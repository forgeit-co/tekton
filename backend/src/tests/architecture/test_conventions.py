from tekton_conventions import package_root


def test_backend_has_package_root():
    assert package_root(__file__).name == "backend", "Backend gate resolved a different package"
