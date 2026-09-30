# ── Local runtime deployment ─────────────────────────────────────────────────

# Build and start the local production-like compose stack.
local-deploy-up:
  just up

# Stop the local production-like compose stack.
local-deploy-down:
  just down

# [python] Read the running local stack and report deployment health.
# Precondition: `just local-deploy-up` completed and the stack is running.
local-backend-deploy-check:
  TEKTON_HOST_PORT="$(just --evaluate host_port)" uv run --directory backend --group dev pytest -n 0 -s deployment_checks

# Build the production backend image.
prod-backend-build:
  docker build -f images/backend/Dockerfile -t tekton-backend:local .

# Build the production frontend image.
prod-frontend-build:
  docker build -f images/frontend/Dockerfile -t tekton-frontend:local .
