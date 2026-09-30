# Tekton Frontend

Vue 3 + TypeScript application for the local Tekton operator interface.

## Repo map

```text
frontend/
├── project_structure.md          # Feature/domain dependency DAG and layout rules
├── scripts/                      # API type generation and i18n checks
├── src/
│   ├── app/                      # App shell, router, startup wiring
│   ├── features/<feature>/       # Route-owning UI and orchestration
│   └── shared/
│       ├── domains/              # Cross-feature domain presenters and composables
│       └── foundation/           # API types/client, i18n, UI primitives
└── tests/                        # unit, component, MSW, and e2e suites
```

## Runtime modes

- Local development/testing: from `frontend/`, use pnpm scripts; root `just dev` starts the API and Vite together.
- Local Compose deployment: root `just up` / `just down` starts or stops the production-like UI and backend stack.
- Production image: `images/frontend/Dockerfile`, built from the repository root with `just prod-frontend-build`.

## Working rules

IMPORTANT: Apply `frontend-vue-development` and `frontend-vue-code-style` before Vue changes; follow `frontend/project_structure.md` for the feature and domain dependency DAG.

- The frontend domain DAG lives in `frontend/project_structure.md`; ESLint generates its domain-boundary check from that document. Update the DAG there rather than bypassing the generated rule.
- Keep features independent. Cross-feature UI reuse belongs in `shared/domains/`; domain-agnostic capabilities belong in `shared/foundation/`.
- API wire types are generated from backend OpenAPI using `openapi-typescript`. Do not hand-edit `src/shared/foundation/api/schema.d.ts`; regenerate and verify drift with the task runner.
- Frontend tests live under `frontend/tests/`, outside `src/`.

## Commands

From the repository root:

- `just lint`
- `just test-all`
- `just python-arch`
- `just api-types`
- `just api-types-check`
- `just up` / `just down`

From `frontend/`:

- `pnpm dev`
- `pnpm build`
- `pnpm lint`
- `pnpm typecheck`
- `pnpm test`
- `pnpm test:e2e`
- `pnpm format:check`
- `pnpm api-types` / `pnpm api-types:check`

## Quality gate and practice

Before handoff run `just lint`, `just frontend-arch`, and relevant frontend tests; use `just test-all` for the full workspace gate, including `just api-types-check`. Use `frontend-vue-development`, `frontend-vue-code-style`, `frontend-vue-testing`, `rest-api-design`, and `reconcile-docs` continuously. Never disable or weaken ESLint architecture rules to make a change pass.
