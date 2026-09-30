# ADR 06: Frontend API type mirroring

**Status:** Accepted
**Date:** 2026-09-30

## Context

The Vue frontend consumes the backend's REST API and server-sent event contracts. Hand-maintained TypeScript mirrors can silently drift as backend fields evolve. The technical specification §14.5 already makes OpenAPI the wire contract and names the generator and generated type output.

## Decision

The backend OpenAPI contract is authoritative; frontend REST wire types are generated with `openapi-typescript`. Run `just api-types` to refresh `frontend/src/shared/foundation/api/schema.d.ts`. Generated output is read-only and must never be hand-edited. Run `just api-types-check` (also included in `just test-all`) to regenerate and fail if committed output drifts. The `openapi-fetch` client consumes the generated schema.

Server-sent event message types remain represented by the OpenAPI schema operation described in technical-spec §§14.4–14.5; any stream-specific constructs not expressible by the generator must be explicit, narrow exceptions rather than duplicated REST DTOs.

## Consequences

- A backend API change that affects frontend types includes a generator refresh in the same change.
- Type drift is a blocking local check through the task runner.
- Generated declarations are distinguishable from application-owned frontend types and are not a manual source of truth.
