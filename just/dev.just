# ── Test and development commands ────────────────────────────────────────────

# Run the complete local CI suite through component and repository gates.
test-all:
  just ci-install
  just python-check
  just frontend-check
  just repo-check
  just commit-matcher-test

# Run the API and Vite development server together.
dev:
  #!/usr/bin/env bash
  set -euo pipefail
  api_pid=
  web_pid=
  cleanup() {
    if [[ -n "$api_pid" ]]; then kill "$api_pid" 2>/dev/null || true; fi
    if [[ -n "$web_pid" ]]; then kill "$web_pid" 2>/dev/null || true; fi
    if [[ -n "$api_pid" ]]; then wait "$api_pid" 2>/dev/null || true; fi
    if [[ -n "$web_pid" ]]; then wait "$web_pid" 2>/dev/null || true; fi
  }
  trap cleanup EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  (cd backend && uv run python -m tekton.entrypoints.api) &
  api_pid=$!
  (cd frontend && pnpm dev --host 127.0.0.1 --port "${TEKTON_FRONTEND_DEV_PORT:-4392}") &
  web_pid=$!
  wait -n "$api_pid" "$web_pid"
