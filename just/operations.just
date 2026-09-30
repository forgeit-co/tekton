# ── Operator commands staged for later milestones ────────────────────────────

# Create local directories and file-based secrets without replacing existing secrets.
init:
  #!/usr/bin/env bash
  set -euo pipefail
  umask 077
  mkdir -p data/db data/secrets data/operator data/llm-proxy state s3
  mkdir -p deploy/secrets
  for name in s3-root-user s3-root-password s3-api-user s3-api-password s3-worker-user s3-worker-password; do
    if [[ ! -e "deploy/secrets/$name" ]]; then
      if [[ "$name" == s3-root-user ]]; then secret="tekton-root"; else secret="$(openssl rand -hex 24)"; fi
      (umask 077 && printf '%s\n' "$secret" > "deploy/secrets/$name")
    fi
    chmod 0600 "deploy/secrets/$name"
  done
  chmod 0700 deploy/secrets
  if [[ ! -e deploy/.env ]]; then
    port="$(just --evaluate host_port)"
    uid="$(id -u)"
    gid="$(id -g)"
    sed -e "s/^TEKTON_HOST_PORT=.*/TEKTON_HOST_PORT=$port/" \
      -e "s/^TEKTON_UID=.*/TEKTON_UID=$uid/" \
      -e "s/^TEKTON_GID=.*/TEKTON_GID=$gid/" deploy/.env.example > deploy/.env
    chmod 0600 deploy/.env
  fi
  echo 'Created private runtime directories and file-based secrets.'

# Start the implemented local services in dependency order.
up:
  just init
  docker compose -f deploy/compose.yaml up --build -d

# Stop the local stack without deleting operator data.
down:
  docker compose -f deploy/compose.yaml down

# Show service status and published URLs.
open:
  @port="$(just --evaluate host_port)"; echo "Tekton: http://127.0.0.1:$port/"
  @echo 'MinIO API is internal to the compose network.'

# Follow compose logs for all services, or one named service.
logs service='':
  @if [[ -n '{{service}}' ]]; then docker compose -f deploy/compose.yaml logs -f '{{service}}'; else docker compose -f deploy/compose.yaml logs -f; fi

# Back up application data. Planned for M0a.
backup:
  @echo 'not implemented yet (milestone M0a)' >&2
  @exit 1

# Restore application data. Planned for M0a.
restore:
  @echo 'not implemented yet (milestone M0a)' >&2
  @exit 1

# Upgrade application release. Planned for M0a.
upgrade:
  @echo 'not implemented yet (milestone M0a)' >&2
  @exit 1

# Roll back application release. Planned for M0a.
rollback:
  @echo 'not implemented yet (milestone M0a)' >&2
  @exit 1

# Rotate per-service credentials. Planned for M0a.
rotate-secrets:
  @echo 'not implemented yet (milestone M0a)' >&2
  @exit 1

# Fetch the pinned map extract. Planned for M3.
map-fetch:
  @echo 'not implemented yet (milestone M3)' >&2
  @exit 1

# Run agent evaluation suites. Planned for M0b.
eval:
  @echo 'not implemented yet (milestone M0b)' >&2
  @exit 1

# Build a release migration fixture. Planned for M0a.
release-fixture tag:
  @echo 'not implemented yet (milestone M0a)' >&2
  @exit 1

# Check the committed knowledge tree against its baseline. Planned for M0c.
knowledge-check:
  @echo 'not implemented yet (milestone M0c)' >&2
  @exit 1
