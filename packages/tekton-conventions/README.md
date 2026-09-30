# Tekton Conventions

Shared dev-only Python rules for import boundaries, environment configuration, test placement, and uv workspace gates. Every Python member runs its own architecture tests against its own source tree; see the root [ADR 07](../../docs/decisions/07-convention-enforcement-and-permissions.md) and the [conventions pattern](https://github.com/forgeit-co/agent-skills/blob/main/patterns/conventions/python.md) available to maintainers with the shared agent-skills repository.

From this directory, use `uv run basedpyright -p pyproject.toml`, `uv run lint-imports`, and `uv run pytest -n auto`. The root `just lint`, `just python-arch`, and `just test-all` recipes include this member.

Rules and their fixtures live in `src/tekton_conventions/` and `tests/`, respectively. Tests always stay outside `src/`.
