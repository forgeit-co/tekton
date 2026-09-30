# ADR 04: Configuration and secret delivery for the local scaffold

**Status:** Accepted
**Date:** 2026-09-30

## Context

Backend entrypoints already read configuration from a typed TOML document selected by `TEKTON_CONFIGURATION_PATH` and file secrets from the directory selected by `TEKTON_SECRETS_DIRECTORY`. Local Compose needs to pass the same authority boundaries without putting secret values into environment variables.

## Decision

The local Compose runtime uses tier 1 file delivery: a checked-in `backend/deploy/backend.toml` and generated per-service files in ignored `deploy/secrets/`. Compose mounts the files as service-scoped secrets under `/run/secrets`. `just init` creates secret files with mode `0600` without overwriting existing values. The stack uses the current operator's UID/GID for shared SQLite files. No external secret store is adopted at this scaffold stage.

## Consequences

- Runtime settings remain in the typed document; deployment selectors only choose its path and secret directory.
- MinIO root and API/worker credentials do not enter process environment values.
- Any future external secret store requires an explicit phase-8 decision and migration trigger.
