# Frontend project structure

## Source layout

- `src/app/` — application shell, router, plugin registration and app-level wiring.
- `src/features/` — route-owning UI and orchestration. Features do not import one another.
- `src/shared/domains/` — reusable business presenters and composables; domain dependencies follow the DAG in `eslint.config.js`.
- `src/shared/foundation/` — domain-agnostic infrastructure such as API types, i18n, routing, formatting, stream and UI primitives.
- `tests/unit/`, `tests/component/`, `tests/e2e/` — focused logic, user-visible component behavior and browser journeys.

## v1 feature folders

`home`, `steps`, `plots`, `tasks`, `documents`, `mail`, `knowledge`, `agents`, `approvals`, and `settings` each expose their public API from `index.ts`.

## Dependency direction

`app → features → shared/domains → shared/foundation`. Features never import other features. Domain-to-domain imports are limited to the dependency list declared in the ESLint config, which generates the boundary check.
