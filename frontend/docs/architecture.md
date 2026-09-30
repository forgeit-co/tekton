# Frontend architecture

The frontend is organized as `app → features → shared/domains → shared/foundation`, with feature independence and an explicit domain dependency DAG. The canonical map and dependency table are in [`../project_structure.md`](../project_structure.md); the ESLint architecture rule is generated from that table. Domain dependencies currently allow `decisions → value-types, sources`, `proposals → value-types, sources`, `tasks → documents, budget`, and `approvals → sources`; every other domain depends only on foundation.

API contracts are generated from backend OpenAPI and consumed through the shared foundation API client. Tests live in `frontend/tests/`, outside `src/`. See the frontend [instructions](../CLAUDE.md) and [ADR 06](../../docs/decisions/06-frontend-api-type-mirroring.md).
