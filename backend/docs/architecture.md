# Backend architecture

The backend is a layer-first Python package whose detailed module map is [`../project_structure.md`](../project_structure.md). The normative product module DAG, module responsibilities, against-DAG ports, and Unit-of-Work commit boundary are in [`../../docs/technical-spec.md`](../../docs/technical-spec.md) §5.

The current scaffold has API, worker, and migration entrypoints. Implementations follow `presentation → application → domain → kernel`; infrastructure implements ports and composition wires adapters. All tests live under `backend/tests/`, never in `src/`. See the backend [instructions](../CLAUDE.md) for exact quality commands.
