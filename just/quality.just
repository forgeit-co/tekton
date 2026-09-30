# ── Quality gates ────────────────────────────────────────────────────────────

# Run all linters, format checks, type checks, and frontend checks.
lint:
  uv run ruff check .
  uv run ruff format --check .
  cd backend && uv run basedpyright -p pyproject.toml
  cd backend && uv run lint-imports
  cd edge && uv run basedpyright -p pyproject.toml
  cd edge && uv run lint-imports
  cd packages/tekton-conventions && uv run basedpyright -p pyproject.toml
  cd packages/tekton-conventions && uv run lint-imports
  cd frontend && pnpm lint
  cd frontend && pnpm typecheck
  cd frontend && pnpm format:check

# Run the architecture gates for all Python workspace members.
python-arch:
  cd backend && uv run lint-imports
  cd backend && uv run pytest tests/architecture
  cd edge && uv run lint-imports
  cd edge && uv run pytest tests/architecture
  cd packages/tekton-conventions && uv run lint-imports
  cd packages/tekton-conventions && uv run pytest tests/architecture

# Run the frontend architecture checks enforced by ESLint.
frontend-arch:
  cd frontend && pnpm lint

# Refresh generated frontend API types from the backend OpenAPI schema.
api-types:
  cd frontend && pnpm api-types

# Check generated frontend API types are up to date.
api-types-check:
  cd frontend && pnpm api-types:check
