# Documentation map

Tekton documentation is divided by scope. Keep the established specification paths at this level because other documents link to them.

| Path | Contents |
| --- | --- |
| `docs/decisions/` | Cross-cutting architecture decision records, numbered sequentially. |
| `docs/rfd-0001.md` | Product RFD 1; stable path. |
| `docs/functional-spec.md` | Functional specification; stable path. |
| `docs/technical-spec.md` | Technical specification; stable path. |

Create `plans/`, `gaps/`, `guidelines/`, `knowledge-base/`, or `prompts/` when the first artifact of that category is ready. Use `scratches/` for ephemeral notes and `superpowers/` for the brainstorming plugin's working area; both are excluded by the repository root `.gitignore`.

Component-specific documentation belongs under that component's `docs/` tree. Add a subdirectory when its first artifact is ready; do not create empty trees just to mirror every possible category. For example, the backend architecture map is `backend/project_structure.md` as required by technical-spec §3; its detailed module documentation may live in `backend/docs/` when there is content to place there.

Durable decisions go in `decisions/`, not in implementation plans or scratch notes. Do not move the three specification files without updating their inbound links, and do not treat scratch or brainstorming output as an accepted decision.
