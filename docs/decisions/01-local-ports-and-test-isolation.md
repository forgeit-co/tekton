# ADR 01: Local ports and test isolation

**Status:** Accepted
**Date:** 2026-09-30

## Context

Tekton runs a local Docker Compose stack and supports parallel developer worktrees. A shared host port would prevent concurrent stacks from starting. Python tests use pytest-xdist processes, so any mutable shared test database would create cross-test interference.

## Decision

Host-only service ports use the 8080 base and an optional worktree offset. Set `TEKTON_PORT_OFFSET` per worktree; each unit adds 20, so offset 1 maps the UI to 8100, offset 2 to 8120, and so on. `TEKTON_HOST_PORT` is the explicit override. Internal container ports remain conventional. The UI is published only on `127.0.0.1`.

Each backend test creates its SQLite database under pytest's per-test `tmp_path`; the API and support fixtures run migrations against those private paths. Pytest-xdist workers therefore share no database files. Edge and conventions tests are isolated by their test fixtures and have no external mutable state. The local deployment has a per-worktree SQLite file under ignored `data/db/`.

## Consequences

- Parallel worktrees can choose non-overlapping 20-port slots without editing Compose.
- New host port mappings must be added to this ADR and projected through `deploy/.env.example`.
- Container-to-container ports are not offset.
- Backend integration tests can run with `pytest -n auto` because each test owns its database file. A test that needs S3 or another shared mutable service must isolate its bucket/object names per test before joining that gate.
- This scaffold currently has no deployment-check category because no tests inspect an operator-provisioned deployment.
