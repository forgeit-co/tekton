# ADR 02: Compose scope for the scaffold

**Status:** Accepted
**Date:** 2026-09-30

## Context

The M0 platform slice has a backend API, worker lifecycle, SQLite migrations, local object storage, and a built SPA. The internal service plane, session control, and edge proxy services are separate later milestones.

## Decision

The default Compose stack implements `s3`, `s3-init`, `migrate`, `backend-api`, `backend-worker`, and `frontend`. `backend-control`, `backend-mcp`, `knowledge-git`, `llm-proxy`, `launcher`, `extractor`, and `egress-proxy` are omitted with a comment in `deploy/compose.yaml`; they will be added with their milestone-specific networks and credentials.

## Consequences

- `just up` can run the current scaffold without exposing services that do not have an implementation yet.
- The `edge` network remains externally routed so Docker can publish the frontend port; the API is attached to both `edge` and internal `data`, while the frontend is attached only to `edge`.
- The `control`, `extract`, `internet`, and `gateway` network definitions are present for the later service groups; they are unused by current services.
- The worker entrypoint remains an idle lifecycle placeholder until its queue and job consumers arrive.
