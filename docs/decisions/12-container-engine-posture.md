# ADR 12: Container engine posture

**Status:** Proposed — operator decision pending
**Date:** 2026-09-30

## Context

The product specification targets a local Linux workstation and supports Docker or Podman. The technical specification §4.1 references rootless Podman (reference) or rootless Docker, while also noting rootful operation as a weaker boundary. Container-engine behavior affects security controls and local deployment usability, so the choice should be made by the operator rather than inferred by implementation.

## Decision

No final rootful-versus-rootless engine decision is made in this ADR; the operator decision is pending. The intended secure default is a rootless engine (Podman or Docker), consistent with the technical specification. Rootful use weakens the isolation posture and must be visible in the health surface as specified; it must not be silently represented as equivalent to rootless operation.

## Consequences

- Deployment instructions and checks must distinguish engine mode rather than assume one.
- Do not claim that rootless Podman is selected as a settled project decision until the operator confirms.
- Resolve this ADR before relying on engine-specific behavior or publishing a definitive installation recommendation.
