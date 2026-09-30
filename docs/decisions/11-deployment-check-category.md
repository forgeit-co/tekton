# ADR 11: Deployment-check category and first member

**Status:** Accepted
**Date:** 2026-09-30

## Context

Tekton has a local production-like Compose deployment started by `just local-deploy-up` (currently an alias for `just up`). The ordinary `just test-all` suite is for code and harness-owned fixtures; its result does not establish that an operator-provisioned Compose deployment is healthy. This decision follows the deployment-check pattern.

## Decision

Create a dedicated backend deployment-check category as a sibling of `backend/tests/`, outside pytest's `testpaths`. Its first member is a deployment smoke check that observes the existing local stack after `just local-deploy-up`: the backend live-health endpoint responds after migrations have completed, and the frontend's published root responds. The check reads the operator-provisioned deployment; it does not provision or tear it down, mount helpers from backend test support, or run in `just test-all`.

The check belongs to the local deployment command family under the name `local-backend-deploy-check`, with its precondition documented as the completed `just local-deploy-up` stack. It runs serially with pytest xdist disabled and visible output. The check implementation and recipe are intentionally not added in this documentation-only cycle; they must land together before this ADR can be treated as implemented.

## Consequences

- A green canonical gate remains independent of whether a local deployment happens to be running.
- Deployment failures can be checked directly against the operator's stack without accidentally booting the test harness.
- The first member is a smoke check, not a general integration test or a substitute for component tests.
- This ADR records the required category and member; a later implementation change must add the sibling test root and matching recipe together, then revise the final paragraph of this decision.
