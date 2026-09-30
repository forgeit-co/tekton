# Frontend project structure

## Source layout

- `src/app/` — application shell, router, plugin registration and app-level wiring.
- `src/features/` — route-owning UI and orchestration. Features do not import one another.
- `src/shared/domains/` — reusable business presenters and composables; domain dependencies follow the declared v1 DAG below.
- `src/shared/foundation/` — domain-agnostic infrastructure such as API types, i18n, routing, formatting, stream and UI primitives.
- `tests/unit/`, `tests/component/`, `tests/e2e/` — focused logic, user-visible component behavior and browser journeys.

## v1 feature folders

`home`, `steps`, `plots`, `tasks`, `documents`, `mail`, `knowledge`, `agents`, `approvals`, and `settings` each expose their public API from `index.ts`.

## Dependency direction

`app → features → shared/domains → shared/foundation`. Features never import other features. Shared domains may import other domains only along this v1 dependency DAG; all undeclared domain dependencies are forbidden and domains may always import the shared foundation.

| Domain             | Allowed domain dependencies |
| ------------------ | --------------------------- |
| `decisions`        | `value-types`, `sources`    |
| `proposals`        | `value-types`, `sources`    |
| `tasks`            | `documents`, `budget`       |
| `approvals`        | `sources`                   |
| Every other domain | None (foundation only)      |

`eslint.config.js` parses this table at load time to generate the domain-boundary rule. Lint fails if the table is missing, malformed, duplicated, or does not cover every shared domain folder.
