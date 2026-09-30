# ADR 08: Worker queue topology and identity

**Status:** Accepted
**Date:** 2026-09-30

## Context

The product is explicitly local-only on one operator's Linux workstation. The technical specification §7.2 defines the backend worker's durable run queue, claims, leases, and 15-second heartbeat; its system overview and §4.1 assign local state to SQLite and mount `data/db/` into the worker. The operator decides that the queue will remain SQLite-backed without a network broker at this local-only stage. This does not reject a broker for a future product that changes its deployment model.

## Decision

The run queue is the durable `runs` table in the local SQLite database. No separate message broker is deployed for the local-only product. The worker claims queued rows with leases, performs work, and records run state and outcomes through the backend's defined application/database boundaries. This is an execution queue, not a license for arbitrary fire-and-forget work in API request handlers.

**Implementation status:** the SQLite-backed queue and claim logic are planned for M0a/M1, per technical-spec §§19–20; they are not present in the current scaffold.

Worker identity is the local deployment's process identity, not a remotely enrolled fleet identity. There is one local operator-controlled stack; no worker CA, enrollment ceremony, or per-replica provisioning is introduced. Today, the worker writes an ephemeral heartbeat file at `/tmp/tekton-worker-heartbeat`, which the Compose healthcheck checks. The specification's durable `worker_heartbeat` row and health-page stale report are planned, not yet implemented.

## Consequences

- Queue durability and restart recovery come from SQLite and worker reconciliation, with no broker service or broker credential.
- Work requiring network, S3, or other external I/O runs outside a write UoW and records durable outcome state through the backend.
- Worker topology remains suited to one local installation. A requirement for multi-host scaling or independently deployed fleets requires an explicit reconsideration before adopting a broker and fleet identity model.
- Heartbeat liveness is observable in durable state; it is distinct from task progress.
