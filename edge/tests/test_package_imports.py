import tekton_edge


def test_edge_package_is_importable():
    assert tekton_edge.__name__ == "tekton_edge", "Edge package import resolved incorrectly"
