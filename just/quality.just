# ── Quality gates ────────────────────────────────────────────────────────────

# Install locked dependencies for Python workspace gates.
python-install:
  uv sync --all-packages --all-groups --locked --no-install-workspace

# Install locked dependencies for frontend gates.
frontend-install:
  corepack enable
  pnpm --dir frontend install --frozen-lockfile

# Install locked dependencies across all workspace ecosystems.
ci-install:
  just python-install
  just frontend-install

# Check Python formatting, lint, types, architecture and tests.
python-check:
  uv run ruff check .
  uv run ruff format --check .
  cd backend && uv run basedpyright -p pyproject.toml
  cd backend && uv run lint-imports
  cd backend && uv run pytest -n auto
  cd edge && uv run basedpyright -p pyproject.toml
  cd edge && uv run lint-imports
  cd edge && uv run pytest -n auto

# Check frontend architecture, lint, types, formatting and tests.
frontend-check:
  cd frontend && pnpm lint
  cd frontend && pnpm typecheck
  cd frontend && pnpm format:check
  cd frontend && pnpm test

# Check secrets policy and workspace convention-gate coverage.
repo-check:
  just secrets-check
  just secrets-check-test
  cd packages/tekton-conventions && uv run basedpyright -p pyproject.toml
  cd packages/tekton-conventions && uv run lint-imports
  cd packages/tekton-conventions && uv run pytest -n auto

# Match Git's option ordering for commands in Claude Code commit hooks.
commit-matcher-test:
  bash tools/hooks/test-commit-matcher.sh

# Refresh generated frontend API types from the backend OpenAPI schema.
api-types:
  cd frontend && pnpm api-types

# Regenerate the OpenAPI client types and fail on any schema drift.
contract-check:
  cd frontend && pnpm api-types:check

# TODO: Validate public_knowledge/ once that directory is introduced.

# Fail if secrets or private keys have entered the Git index or worktree.
secrets-check:
  #!/usr/bin/env bash
  set -euo pipefail
  declare -a repo_files=()
  while IFS= read -r -d '' path; do repo_files+=("$path"); done < <(git ls-files --cached --others --exclude-standard -z)
  while IFS= read -r -d '' path; do repo_files+=("$path"); done < <(git diff --cached --name-only -z)
  if [[ -d deploy/secrets ]]; then
    while IFS= read -r -d '' path; do repo_files+=("$path"); done < <(find deploy/secrets -type f ! -name .gitkeep -print0)
  fi
  while IFS= read -r -d '' path; do repo_files+=("${path#./}"); done < <(find . -type f -name '*.key' -not -path './.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -print0)
  violations=()
  for path in "${repo_files[@]}"; do
    if [[ "$path" == deploy/secrets/* && "$path" != deploy/secrets/.gitkeep ]]; then violations+=("$path"); fi
    if [[ "$path" == *.key ]]; then violations+=("$path"); fi
  done
  if ((${#violations[@]} > 0)); then
    printf 'Secret paths must not be tracked or staged:\n' >&2
    printf '  %s\n' "${violations[@]}" >&2
    exit 1
  fi

# Validate the task runner itself and reject any untracked secret paths too.
secrets-check-test:
  #!/usr/bin/env bash
  set -euo pipefail
  probe="deploy/secrets/.cycle6-secrets-probe"
  tmp_payload="$(mktemp)"
  cleanup() { rm -f "$probe" "$tmp_payload"; }
  trap cleanup EXIT
  rm -f "$probe"
  if ! just secrets-check; then
    echo 'baseline secrets check unexpectedly failed' >&2
    exit 1
  fi
  : > "$probe"
  if just secrets-check; then
    echo 'secrets-check failed to reject an untracked secret path' >&2
    exit 1
  fi
  jq -cn --arg cwd "$PWD" --arg command "git -C \"$PWD\" commit -m probe" '{cwd:$cwd,tool_input:{command:$command}}' > "$tmp_payload"
  hook_status=0
  tools/hooks/pretooluse-secrets-check.sh < "$tmp_payload" || hook_status=$?
  if [[ "$hook_status" -ne 2 ]]; then
    echo "Claude secrets hook expected exit 2, got $hook_status" >&2
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
