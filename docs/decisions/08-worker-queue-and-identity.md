# ADR 08: Worker queue topology and identity

**Status:** Accepted
**Date:** 2026-09-30

## Context

The product is explicitly local-only on one operator's Linux workstation. The technical specification §7.2 defines the backend worker's durable run queue, claims, leases, and 15-second heartbeat; its system overview and §4.1 assign local state to SQLite and mount `data/db/` into the worker. The operator decides that the queue will remain SQLite-backed without a network broker at this local-only stage. This does not reject a broker for a future product that changes its deployment model.

## Decision

The run queue is the durable `runs` table in the local SQLite database. No separate message broker is deployed for the local-only product. The worker claims queued rows with leases, performs work, and records run state and outcomes through the backend's defined application/database boundaries. This is an execution queue, not a license for arbitrary fire-and-forget work in API request handlers.

Worker identity is the local deployment's process identity, not a remotely enrolled fleet identity. There is one local operator-controlled stack; no worker CA, enrollment ceremony, or per-replica provisioning is introduced. The worker writes `worker_heartbeat` every 15 seconds; the health surface reports it stale after two minutes, as specified in technical-spec §7.2 and §18.

## Consequences

- Queue durability and restart recovery come from SQLite and worker reconciliation, with no broker service or broker credential.
- Work requiring network, S3, or other external I/O runs outside a write UoW and records durable outcome state through the backend.
- Worker topology remains suited to one local installation. A requirement for multi-host scaling or independently deployed fleets requires an explicit reconsideration before adopting a broker and fleet identity model.
- Heartbeat liveness is observable in durable state; it is distinct from task progress.
