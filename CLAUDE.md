# Tekton Monorepo

Tekton is a local-first assistant for planning a house build in Romania. Work is split by runtime responsibility:

| Path | Owns |
| --- | --- |
| `backend/` | Python API, worker, persistence, domain and application services. |
| `edge/` | Separate Python package for future edge services; it must not depend on `backend/`. |
| `packages/tekton-conventions/` | Shared Python architecture and layout rules, enforced locally by each workspace member. |
| `frontend/` | Vue 3 + TypeScript application. |
| `deploy/` | Local Compose stack and deployment inputs. |
| `images/` | Container build definitions and helper images. |
| `just/` | Root task-runner recipes, imported by `justfile`. |
| `docs/` | Product specifications and cross-cutting ADRs. |

## STOP — Command locations

Use the repository root for `just` commands. Run Python checks from the owning component directory so each package owns its test collection; run frontend scripts from `frontend/`.

| Work | Command / location |
| --- | --- |
| Cross-workspace quality | `just lint` |
| Complete local suite | `just test-all` |
| Python architecture gates | `just python-arch` |
| Regenerate/check API types | `just api-types` / `just api-types-check` |
| Start/stop local Compose stack | `just up` / `just down` |
| API + Vite development servers | `just dev` |

`just up` initializes private runtime paths/secrets before starting the stack; `just down` preserves operator data.

## Fast navigation

- Product goals and legal/product context: `docs/rfd-0001.md`.
- User behavior and scope: `docs/functional-spec.md`.
- Implementation architecture, module DAG, and API contract: `docs/technical-spec.md`.
- Cross-cutting decisions: `docs/decisions/` (ADRs 01–13).
- Backend module map and persistence boundaries: `backend/project_structure.md`.
- Frontend feature/domain DAG: `frontend/project_structure.md`.
- Documentation tree and placement: `docs/README.md`.

## Documentation placement

The root `docs/` owns cross-cutting specifications and ADRs. Keep the three existing specification paths stable because other documents link to them. Component-specific architecture notes belong in that component's `docs/`. Create other artifact subdirectories when their first durable artifact is ready; keep throwaway notes out of tracked documentation.

## Global rules

1. Python tests always live outside `src/`; never add tests below a `src/` tree.
2. Backend import contracts are generated from the domain DAG in `docs/technical-spec.md`. Never hand-edit generated contracts; regenerate from `backend/` with `uv run python scripts/gen_import_contracts.py`.
3. Backend process-environment reads belong only in `backend/src/tekton/infrastructure/config/`; do not introduce environment reads elsewhere.
4. All component paths and dependency boundaries must agree with their project-structure document and the technical specification.
5. Never disable, skip, or weaken an architecture or quality gate to make a change pass. Ask the operator before proposing a convention exception.
6. Read the applicable component `CLAUDE.md` before changing that component; preserve the scope of the task and verify commands before claiming success.

## Continuous practices

Load the applicable practices when changing the corresponding area: `python-ddd`, `python-code-style`, `python-testing`, `python-commands`, `frontend-vue-development`, `frontend-vue-code-style`, `frontend-vue-testing`, `rest-api-design`, and `reconcile-docs`. Root instructions orient; component rules and specifications own the detail.
