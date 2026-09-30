# Tekton Backend

The backend owns the Python API, worker, database adapters, migrations, and product application logic. Its target module layout and boundaries are described in [`project_structure.md`](project_structure.md) and technical-spec §5.

From the repository root, start the local stack with `just up`, stop it with `just down`, and run the full workspace checks with `just test-all`. For package-local checks, run `uv run basedpyright -p pyproject.toml`, `uv run lint-imports`, and `uv run pytest -n auto` from `backend/`.

All tests stay under `backend/tests/`, outside `src/`. See the root [contributor guide](../CONTRIBUTING.md) for change and gate expectations.
