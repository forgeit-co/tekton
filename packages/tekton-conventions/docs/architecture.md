# Conventions package architecture

`tekton-conventions` is a dev-only rule library in the uv workspace. Its public surface provides reusable rule constructors; each consumer's local architecture suite applies rules to that package's own source tree. Workspace coverage is checked from the conventions package's own gate.

Rule mechanics and policy live in `src/tekton_conventions/`; rule fixtures and tests live in `tests/`, outside `src/`. See the package [instructions](../CLAUDE.md), the [Python conventions pattern](https://github.com/forgeit-co/agent-skills/blob/main/patterns/conventions/python.md), and [ADR 07](../../docs/decisions/07-convention-enforcement-and-permissions.md).
