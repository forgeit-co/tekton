# Contributing to Tekton

Thanks for helping improve Tekton. Before making changes, read the root and relevant component `CLAUDE.md`, the applicable project-structure guide, and the relevant specification or ADR. Keep changes within the owning component and update documentation when behavior, architecture, or commands change.

## Development setup

Install the tools listed in the root [README](README.md), then run `uv sync` at the repository root and `pnpm install --frozen-lockfile` in `frontend/`. Start the local production-like stack with `just up`; stop it without deleting operator data with `just down`.

## Checks

Use root recipes as the shared command interface:

- `just lint` — formatting, lint, Python type/import checks, and frontend checks.
- `just python-arch` — Python architecture tests and import contracts.
- `just test-all` — all checks and test suites, including API type drift.
- `just api-types` — regenerate frontend API types after backend OpenAPI changes.

Run component-specific tests from their component directory. For Python type checks, use `uv run basedpyright -p pyproject.toml` from the owning Python package directory; a host `~/pyrightconfig.json` otherwise changes configuration discovery.

## Change expectations

- Python tests live in `tests/` outside `src/`.
- Never hand-edit generated backend import contracts or frontend API declarations; update their source and regenerate.
- Keep backend process-environment reads inside `backend/src/tekton/infrastructure/config/`.
- Do not disable or weaken architecture or quality gates. Discuss a requested exception with the operator before proposing it.
- Do not commit credentials, generated runtime secrets, or personal data.
- Update or add an ADR when making a durable cross-cutting architectural decision; update the technical specification when changing a normative product or API contract.

## License

The repository's licensing has not yet been selected. Do not add or assume a license header or redistribute the work under a selected license until the operator resolves [LICENSE](LICENSE).
