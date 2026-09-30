# ADR 05: Observability posture

**Status:** Accepted
**Date:** 2026-09-30

## Context

Tekton is a local Compose application with a Python backend and worker. The technical specification §18 already defines JSON logs to stdout, stable named log codes, bound context fields, and a health page; operational visibility must not introduce a second application-owned collection pipeline.

## Decision

Backend services emit structured JSON logs to stdout. Log event codes and their meanings follow the vocabulary in [`docs/technical-spec.md`](../technical-spec.md) §18; adding or changing a code updates that specification as part of the same change. Logs carry the specified non-secret context fields, never request or agent payloads, tokens, credentials, or personal data. The container engine and local operator tooling collect and read stdout; the application does not ship or aggregate logs.

The §18 log-code vocabulary is the stable operational contract. Durable database state remains the source for correctness and audit questions. A metrics endpoint, exporter, collector, tracing stack, or app-side telemetry store is not adopted without demonstrated need and an explicit deployment decision.

## Consequences

- Container logs and named codes are the day-one operational surface.
- Code-level errors and state transitions must use stable codes rather than free-form-only messages.
- The application remains independent of a telemetry vendor or collection service.
- Any later observability expansion is additive and records a new decision tied to its actual deployment need.
