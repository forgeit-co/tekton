# ── Per-worktree port allocation (host ports only) ───────────────────────────

# Use a stable private port offset for this checkout; override at invocation time if needed.
[private]
port_offset := `value="${TEKTON_PORT_OFFSET:-0}"; [[ "$value" =~ ^[0-9]+$ ]] || { echo 'TEKTON_PORT_OFFSET must be an integer' >&2; exit 2; }; printf '%s' "$value"`

# Public UI port, resolved from the worktree's generated deploy/.env.
[private]
host_port := `if [[ -f deploy/.env ]]; then set -a; source deploy/.env; set +a; fi; if [[ -n "${TEKTON_HOST_PORT:-}" ]]; then printf '%s' "$TEKTON_HOST_PORT"; else value="${TEKTON_PORT_OFFSET:-0}"; [[ "$value" =~ ^[0-9]+$ ]] || { echo 'TEKTON_PORT_OFFSET must be an integer' >&2; exit 2; }; port=$((8080 + 20 * value)); (( port <= 65000 )) || { echo 'TEKTON_PORT_OFFSET is out of range' >&2; exit 2; }; printf '%s' "$port"; fi`
