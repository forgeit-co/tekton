# ADR 10: Configuration authority and secret-delivery tier

**Status:** Accepted
**Date:** 2026-09-30

## Context

ADR 04 selects file-based Compose secret delivery for the current local stack, but does not enumerate all configuration authority classes or state triggers for changing secret-delivery tier. Tekton is a single-operator, local-only product, with typed deployment policy in `backend/deploy/backend.toml` and Compose-provided file secrets in `deploy/secrets/`. The configuration authority pattern calls for recording both classifications without adding an unnecessary secret store.

## Decision

Every process setting belongs to exactly one of these authority classes:

| Authority class | Tekton authority |
| --- | --- |
| Secret material | A distinct typed secret input, delivered as service-scoped files for the local deployment. |
| Bootstrap configuration | Process environment values needed to select configuration/secret inputs and basic process identity only. |
| Deployment policy and tunables | The typed TOML document owned by the process; Compose selects and mounts the document but is not a second policy source. |
| Runtime product policy | Durable authenticated application state only when an operator must change a value without replacing the process. This class starts empty except for product policy explicitly modeled in the technical specification. |
| Safety and protocol mechanics | Source-owned constants or shared wire contracts; never deployment knobs. |

No setting has two authorities and consumers receive typed, validated values rather than source lookups. Environment reads are confined to the configuration boundary, `backend/src/tekton/infrastructure/config/`; current Compose selectors are limited to the configuration path and secrets directory.

The local Compose deployment uses **Tier 1 file delivery** per the explicit choice in ADR 04: service-scoped secret files are created by the host/repository setup (including `just init`), and no external secret store is adopted. The component `.toml` policy is a separate authority from file secret material. Move to Tier 2 only when a deployment control plane owns the secret object; consider Tier 3 only when a concrete requirement such as audited/dynamic rotation or an existing required fleet secret store justifies its operational lifecycle. A tier change requires an explicit deployment decision, not an automatic application fallback.

## Consequences

- The configuration document and secret files remain separate authorities; secret values do not move into deployment policy or logs.
- Runtime product policy is not a generic home for every convenient live-editable setting; the product must require durable, authorized, auditable change.
- There is no Tier-3 secret-store service or dependency at this stage.
- When deployment facts cross a trigger above, update this ADR before implementing a different delivery tier.
