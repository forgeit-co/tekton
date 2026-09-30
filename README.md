# Tekton

An open-source assistant that runs locally on Linux and guides an owner through building a house in Romania, from budget to land registration.

## Quick start

Prerequisites: Linux, Docker Compose, `just`, `uv`, Node.js 24 with pnpm 10. From the repository root, start the local stack with:

```sh
just up
```

The UI is published on `http://127.0.0.1:8080/` by default. `just up` initializes local runtime directories and file secrets without replacing existing secrets. Stop the stack while preserving operator data with:

```sh
just down
```

Run the complete workspace checks with `just test-all`.

## Components

| Path | Responsibility |
| --- | --- |
| `backend/` | Python API, worker, SQLite persistence, and product logic |
| `edge/` | Independent Python edge services as they are implemented |
| `packages/tekton-conventions/` | Shared Python architecture and source-layout rules |
| `frontend/` | Vue 3 + TypeScript operator interface |
| `deploy/` and `images/` | Local Compose deployment and container images |

Component guides: [backend](backend/README.md), [edge](edge/README.md), [frontend](frontend/README.md), and [conventions](packages/tekton-conventions/README.md).

## Product and architecture

- [RFD 1 — Tekton](docs/rfd-0001.md): goals, legal framework, architecture
- [Functional specification](docs/functional-spec.md): what Tekton does
- [Technical specification](docs/technical-spec.md): how it is built
- [Backend module map](backend/project_structure.md)
- [Frontend module map and domain DAG](frontend/project_structure.md)
- [Architecture decisions](docs/decisions/)
- [Contributor guide](CONTRIBUTING.md)
