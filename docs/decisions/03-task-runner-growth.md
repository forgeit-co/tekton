# ADR 03: Task runner growth

**Status:** Accepted
**Date:** 2026-09-30

## Context

The root task runner serves the Python workspace, frontend, local deployment, and later operator commands. Its command names are a stable contributor interface, while individual task families need separate ownership as the recipe set grows.

## Decision

`justfile` imports responsibility-focused `just/*.just` files using `import`, never `mod`. Global settings and the default recipe stay in the root file. Recipe implementations live in one owning file and paths remain repository-root-relative.

## Consequences

- Moving recipes among files does not change their public names or call paths.
- Imports remain explicit; a missing required family fails parsing rather than silently hiding tasks.
- Split further by responsibility if the root justfile grows past 350 lines.
