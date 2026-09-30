# ── Quality gates ────────────────────────────────────────────────────────────

# Install locked dependencies into a temporary environment for CI and local gates.
ci-install:
  uv sync --all-packages --all-groups --locked --no-install-workspace
  corepack enable
  pnpm --dir frontend install --frozen-lockfile

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

# TODO: Validate public_knowledge/ once that directory is introduced.

# Fail if secrets or private keys have entered the Git index.
secrets-check:
  #!/usr/bin/env bash
  set -euo pipefail
  tracked_secrets="$(git ls-files -- deploy/secrets | grep -Ev '^deploy/secrets/\.gitkeep$' || true)"
  tracked_keys="$(git ls-files | grep -E '\.key$' || true)"
  if [[ -n "$tracked_secrets" || -n "$tracked_keys" ]]; then
    printf 'Tracked secret files found; remove them from the Git index:\n%s\n%s\n' "$tracked_secrets" "$tracked_keys" >&2
    exit 1
  fi

# Audit all locked Python workspace dependencies and frontend dependencies.
audit:
  #!/usr/bin/env bash
  set -uo pipefail
  audit_status=0
  if ! uv export --all-packages --all-groups --no-emit-workspace --format requirements.txt --no-hashes | uvx --from pip-audit pip-audit --requirement /dev/stdin --no-deps --disable-pip; then
    audit_status=1
  fi
  if ! (cd frontend && pnpm audit); then
    audit_status=1
  fi
  exit "$audit_status"

# Install the versioned Git pre-commit hook for this clone.
hooks:
  git config core.hooksPath tools/hooks
