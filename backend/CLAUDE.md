# Tekton Backend

Python backend package owning the API, worker, migrations, composition roots, and persisted product state. Current local runtime includes the API and worker; the technical specification describes later backend entrypoints and modules as they are added.

## Repo map

```text
backend/
├── deploy/backend.toml       # Typed deployment policy; no secrets
├── migrations/               # Alembic schema changes
├── scripts/gen_import_contracts.py # Rebuild import contracts from tech-spec DAG
├── src/tekton/
│   ├── kernel/               # Cross-module primitives and ports
│   ├── domain/<module>/      # Domain models, rules, and repository ports
│   ├── application/<module>/ # Use cases, sessions/UoWs, orchestration
│   ├── infrastructure/      # Adapters, database, config, integrations
│   ├── presentation/        # API, control, MCP, stream adapters
│   ├── composition/         # Entrypoint wiring
│   └── entrypoints/         # api.py, worker.py, migrate.py, others as added
├── tests/                    # unit, application, integration, api, contract, e2e, support
└── project_structure.md      # authoritative module map and rules
```

## Runtime modes

- Local development/testing: run backend commands from `backend/`; use `uv run` in this workspace.
- Local Compose deployment: from the repository root, use `just up` / `just down` (the worker is part of the stack).
- Production image: `images/backend/Dockerfile`, built from the repository root with `just prod-backend-build`.

## Working rules

IMPORTANT: Apply `python-ddd` before Python backend changes and follow `backend/project_structure.md` and `docs/technical-spec.md` §5.

- Tests always live outside `src/`, under `backend/tests/`.
- `basedpyright` must run with `-p pyproject.toml` from `backend/`; host `~/pyrightconfig.json` otherwise hijacks configuration discovery.
- The import-linter contract table in `backend/pyproject.toml` is generated from the technical-spec DAG. Never hand-edit it: from this directory run `uv run python scripts/gen_import_contracts.py`.
- Read environment variables only in `src/tekton/infrastructure/config/`. Secrets and deployment policy follow ADR 04; do not add environment reads elsewhere.
- Use the module DAG in `docs/technical-spec.md` §5 and its allowed-port exceptions. Against-DAG ports live in `tekton/kernel/ports.py`; repositories are domain ports.
- A UoW exposes only its module's repositories. Application use cases never call `commit()`; `CommitPipeline` owns commit and revalidation orchestration, called through composition.
- Keep handlers thin and adapters in infrastructure. Wiring concrete adapters belongs to `composition/`.

## Commands

Run from the repository root:

- `just lint`
- `just test-all`
- `just python-arch`
- `just api-types`
- `just up` / `just down`

Run in this package directory:

- `uv run basedpyright -p pyproject.toml`
- `uv run lint-imports`
- `uv run pytest -n auto`
- `uv run python scripts/gen_import_contracts.py` (only after changing the technical-spec DAG)

## Quality gate and practice

Before handoff run `just lint`, `just python-arch`, and relevant `backend/` pytest suites; `just test-all` is the full workspace gate. Use `python-ddd`, `python-code-style`, `python-testing`, `python-commands`, `rest-api-design`, and `reconcile-docs` continuously. Never disable or weaken a gate to get a green run.
