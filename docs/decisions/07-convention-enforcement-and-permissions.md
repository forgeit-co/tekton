# ADR 07: Convention enforcement and permission protocol

**Status:** Accepted
**Date:** 2026-09-30

## Context

Tekton is a Python uv workspace with backend, edge, and shared conventions packages. Import boundaries and structural rules must fail in the owning package's local gate instead of depending on review memory. Current enforcement uses generated import-linter contracts plus per-member pytest architecture gates, including the shared `no_tests_under_src` rule.

## Decision

Keep each convention in its most decidable enforcement tier: import graph boundaries are import-linter contracts, and source-tree placement or AST conventions are tests from `tekton-conventions`, run locally by each package. Backend import contracts are generated from the DAG in `docs/technical-spec.md`; the generator is `backend/scripts/gen_import_contracts.py`. The conventions package gate checks workspace member gate coverage. Python tests remain outside `src/`; `no_tests_under_src` is mandatory in each applicable gate.

No architecture, formatting, typing, import, or test gate may be disabled, skipped, weakened, or omitted to land a change. A proposed convention exception requires explicit operator approval before it is recorded. Permission is specific to the stated exception and rationale, must be visible in the review diff, and cannot be inferred from silence, a prior unrelated approval, or an agent's own judgment. Do not add per-package allowlists or blanket suppressions as a substitute for approval. Until approval is explicit, the gate remains unchanged and the work must comply with it.

Every convention rule must have evidence that it flags a violation and accepts its compliant counterpart. Gate tests and their invocation from `just python-arch` / `just test-all` are part of the invariant, not optional cleanup.

## Consequences

- A violation fails within its owning Python member; the conventions package does not centrally scan sibling source trees.
- The spec DAG is edited first, then generated contracts are refreshed; generated TOML must not be hand-edited.
- Fixes preserve enforcement rather than deleting or skipping a failing gate.
- Any explicitly approved exception remains narrow, documented in the same visible change, and reviewable by its exact scope.
