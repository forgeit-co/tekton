# Tekton Edge

`edge/` is an independent Python workspace member reserved for edge-facing proxy and launcher services. The current package is a minimal scaffold and is not included as a runnable service in the default Compose stack.

From this directory, run package checks with `uv run basedpyright -p pyproject.toml`, `uv run lint-imports`, and `uv run pytest -n auto`. From the repository root, `just lint`, `just python-arch`, and `just test-all` include this package.

Tests belong in `edge/tests/`, outside `src/`. Follow the technical specification's service boundaries before adding runtime code.
