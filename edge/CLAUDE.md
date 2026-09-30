# Tekton Edge Services

Separate Python package for Tekton edge-facing proxy and launcher services; it does not own product-domain state or depend on the backend package.

## Repo map

```text
edge/
├── pyproject.toml             # uv workspace member
├── src/tekton_edge/           # Edge service package (scaffold currently minimal)
└── tests/                     # Package import and architecture checks
```

## Runtime modes

- Local development/testing: run package commands from `edge/` using `uv run`.
- Local Compose deployment: root `just up` / `just down`; current default Compose does not yet include later edge services.
- Production images: edge-specific builds live under `images/edge/` when implemented; do not assume a current service image is runnable.

## Working rules

IMPORTANT: Before adding edge source, use the component's relevant service design practice and review the edge boundary in `docs/technical-spec.md` §§2, 4.3, 7.3, and 7.7.

- Tests always live outside `src/`, in `edge/tests/`.
- `basedpyright` must run with `-p pyproject.toml` from this directory so host `~/pyrightconfig.json` cannot hijack discovery.
- Keep the package independent: no imports from `tekton` or backend internals. No product-domain code belongs here.
- Do not read process environment in edge domain or service logic; environment configuration belongs at a dedicated configuration boundary if one is introduced.
- The technical specification is the source of truth for future edge service responsibilities and security boundaries.

## Commands

From the repository root:

- `just lint`
- `just test-all`
- `just python-arch`
- `just api-types`
- `just up` / `just down`

From `edge/`:

- `uv run basedpyright -p pyproject.toml`
- `uv run lint-imports`
- `uv run pytest -n auto`

## Quality gate and practice

Run `just lint`, `just python-arch`, and the relevant `edge/` tests before handoff; `just test-all` is the full workspace gate. Use `python-code-style`, `python-testing`, `python-commands`, and `reconcile-docs` whenever applicable. Never disable or weaken an architecture gate.
