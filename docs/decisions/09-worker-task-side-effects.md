# ADR 09: Worker task side-effect classes

**Status:** Accepted
**Date:** 2026-09-30

## Context

Worker tasks execute at least once across retries, crashes, and reconciliation. Technical specification §5.3 distinguishes database-only consumers from two-phase consumers that perform I/O, while the worker pattern requires classifying side effects before their first implementation: platform-owned artifact creation versus mutation of an externally owned system. Current implemented scaffold services and all future task kinds must be distinguished; the normative task/consumer names and behaviors are in technical-spec §5.3, §7, and §17.

## Decision

Classify work at the side-effect boundary and use the applicable retry policy below:

| Kind supported by the specification | Side-effect class | Required retry property |
| --- | --- | --- |
| `run-resumer`, `step-activity`, `proof-check-queuer`, `distances-queuer`, `projections-recompute`, `notifier` | Database-only state transition in the authoritative SQLite database | Effect and consumer offset commit in one UoW; repeat guarded by idempotency/CAS. |
| `extraction-queuer` and document extraction | Platform-owned artifact creation in Tekton-managed S3 storage, followed by local database state | Stable operation identity and durable outcome; verify external completion before adopting or repeating it. |
| `source-verifier` and content verification | External read-only request, then a Tekton-owned verification result | Re-fetch is permitted; record result idempotently and do not mutate the source host. |
| `knowledge-committer` | Mutation to the operator-owned Git repository | Two-phase intent/outcome and stable approval/operation identity; re-read approved DB content and make commit creation idempotent before retry. |
| `mail-outbox` / outbound email send | Mutation of an externally owned Gmail mailbox and recipient-visible delivery | Persist an outbox intent and stable provider/idempotency identity where available; never blindly resend after an ambiguous outcome. |
| `remote-images` | External read-only fetch, followed by a Tekton-owned document artifact | Fetch only URLs already recorded for the message through the egress proxy; use stable message/image identity and idempotent artifact/result writes. |
| Backup creation | Platform-owned artifact in the configured restic repository | Stable snapshot/operation identity and durable completion evidence; adopt only a verified completed artifact. |
| Restore, upgrade, rollback, or repository changes that replace or mutate operator data | Mutation of externally/operator-owned state | Stage, validate, and cut over through the smallest atomic boundary available; never implicitly adopt partial changes. |

This ADR classifies side effects only; it does not assert that these future services or tasks exist in the current M0 scaffold, nor does it prescribe their complete staging protocol. Before implementing a new side-effecting kind, add it to the technical specification and this table in the same change.

## Consequences

- SQLite-only consumers can keep state and offset updates atomic.
- Platform-owned artifacts may be reused only after durable proof; operator-owned and third-party mutations require stronger cutover and ambiguity handling.
- Side effects never gain a new identity from wall-clock time or a fresh random value on each retry.
- Network and S3 effects do not occur inside application write UoWs.
