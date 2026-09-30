# Backend project structure

This file describes the intended backend package organization. The normative module dependency graph and all allowed domain dependencies live in [`docs/technical-spec.md`](../docs/technical-spec.md) §5; update that DAG first, then regenerate the backend import contracts.

## Source map

```text
backend/src/tekton/
├── __init__.py                     # Package root
├── kernel/                         # Cross-module value types, errors, protocols, and ports
├── domain/<module>/                # Framework-free entities, value objects, rules, and repository ports
├── application/<module>/           # Use cases, module session protocols, orchestration
│   ├── shared/                     # Shared read/write session and commit protocols
│   └── commit/                     # CommitPipeline: the only application commit capability
├── infrastructure/<module>/       # Persistence, external adapters, config, ORM mappings
├── presentation/                   # HTTP API, control API, MCP, and SSE adapters
├── composition/                    # Application graph and per-entrypoint wiring
└── entrypoints/                    # Process entrypoints (API, worker, migration, etc.)

backend/tests/                      # All test categories; never nested in src/
backend/migrations/                 # Alembic migrations
backend/deploy/backend.toml         # Typed runtime policy, separate from secrets
```

`domain/<module>/`, `application/<module>/`, and `infrastructure/<module>/` share a module name but keep layer ownership. The module inventory, module responsibilities, and exceptions for modules without domain rules are defined in technical-spec §5.1.

## Layers and dependency direction

- Dependencies point inward: `presentation → application → domain → kernel`.
- Domain and kernel remain framework-free. Infrastructure implements ports and is not imported by application or domain.
- Composition is the only place that assembles concrete adapters; it sits outside the import-linter layer chain and connects entrypoints to their graphs.
- The domain and application module DAG is specified by the table in technical-spec §5.1. Each module imports only its listed domain dependencies and its permitted shared application contracts.
- Against-DAG synchronous calls are explicit ports in `kernel/ports.py`; modules implement the ports they own and `composition/core.py` registers them. Do not create direct cross-module imports to avoid a port.
- Generated `backend/pyproject.toml` import contracts derive from the technical-spec DAG. After changing the DAG, run `cd backend && uv run python scripts/gen_import_contracts.py`; never edit generated contract blocks by hand.

## Ports and persistence

- Repository interfaces are domain ports in the owning module. Infrastructure supplies their implementations.
- Cross-module ports whose direction would otherwise violate the DAG live in `kernel/ports.py`. Ordinary concept-specific ports stay with the module that owns the capability.
- Each application module owns its narrow read or write session protocol (`application/<module>/uow.py` when implemented), exposing only that module's repositories and event collection. Application services depend on those protocols, not on SQLAlchemy or infrastructure.
- One concrete SQLAlchemy Unit of Work in `infrastructure/shared/` can satisfy the protocols structurally. It is assembled in composition; application session protocols do not expose a generic commit method.
- `CommitPipeline` in `application/commit/` owns explicit commit and revalidation. Only composition may import it directly; use cases do not call `.commit()` or perform transaction finalization themselves.
- Do not hold a write UoW across network or object-store I/O; technical-spec §5.2 defines the transaction and persistence constraints.

## Tests

All backend tests live in `backend/tests/`, outside `src/`: `unit/`, `application/`, `integration/`, `api/`, `contract/`, `e2e/`, `support/`, and `architecture/`. Test support and fixtures belong in the test tree, never production source. The conventions package enforces `no_tests_under_src`.
