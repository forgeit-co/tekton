# ── Local runtime deployment ─────────────────────────────────────────────────

# Build and start the local production-like compose stack.
local-deploy-up:
  just up

# Stop the local production-like compose stack.
local-deploy-down:
  just down

# Build the production backend image.
prod-backend-build:
  docker build -f images/backend/Dockerfile -t tekton-backend:local .

# Build the production frontend image.
prod-frontend-build:
  docker build -f images/frontend/Dockerfile -t tekton-frontend:local .
