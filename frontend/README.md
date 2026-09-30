# Tekton Frontend

Vue 3 + TypeScript application for Tekton's local operator interface. Its feature and shared-domain dependency map is [`project_structure.md`](project_structure.md).

From the repository root, `just dev` starts API and Vite together; `just up` starts the local Compose stack and `just down` stops it. From `frontend/`, install with `pnpm install --frozen-lockfile`; use `pnpm dev`, `pnpm build`, `pnpm lint`, `pnpm typecheck`, and `pnpm test` as needed. Generated REST types are refreshed by root `just api-types` and checked by `just api-types-check`.

Frontend tests live in `frontend/tests/`, outside `src/`. See the root [contributor guide](../CONTRIBUTING.md) before contributing.
