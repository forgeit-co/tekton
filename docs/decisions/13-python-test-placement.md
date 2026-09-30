# ADR 13: Python test placement

**Status:** Accepted
**Date:** 2026-09-30

## Context

The backend and its sibling Python packages use a `src/` layout. Tests placed inside `src/` can be accidentally packaged as runtime code, weaken separation between production and verification, and conflict with the conventions package's `no_tests_under_src` gate. The operator explicitly corrected the project guidance: Python tests always live outside `src/`.

## Decision

All Python tests live in top-level component `tests/` trees beside `src/`, never underneath them. Backend categories are under `backend/tests/`; edge tests are under `edge/tests/`; conventions tests are under `packages/tekton-conventions/tests/`. Test-only helpers, fixtures, and support modules remain in the test tree. The `no_tests_under_src` architecture rule enforces the placement.

## Consequences

- Test files are not part of importable production packages.
- Each workspace member owns its own test collection and architecture gate.
- A test added under any member's `src/` tree fails the member's conventions gate and must be moved, not exempted.
