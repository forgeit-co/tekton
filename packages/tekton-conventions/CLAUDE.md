# Tekton Python Conventions

Shared dev-only Python conventions library: define package-local architecture and layout rules once, then have each uv workspace member run its own gate against its own tree.

## Repo map

```text
packages/tekton-conventions/
├── pyproject.toml                     # Workspace member and rule package config
├── src/tekton_conventions/            # Rule constructors and scanning machinery
│   ├── import_contracts.py            # Technical-spec DAG → backend manifest generator
│   ├── configuration.py               # Environment-boundary rules
│   ├── layout.py                      # Test/source placement and naming rules
│   └── workspace.py                   # Workspace gate coverage rules
└── tests/
    ├── architecture/                  # This package's own conventions gate
    ├── fixtures/                      # should_flag / should_pass source trees
    └── test_*.py                      # Rule behavior tests
```

## Runtime modes

- Local development/testing: invoke `uv run` from this member directory; the workspace root provides the shared environment.
- Local Compose deployment: this dev-only package is not a service; use root `just up` / `just down` for the product stack.
- Production image: the conventions library is not shipped in runtime images.

## Working rules

IMPORTANT: Apply `python-code-style` and `python-testing` when changing convention rules. Read the enforcement design in `/home/cristi/Projects/agent-skills/patterns/conventions/python.md` and the project-specific conventions tests before extending the scanner.

- Tests always live outside `src/`, under `packages/tekton-conventions/tests/`.
- Keep rules local and reusable: each production member's own architecture suite runs rules against that member, rather than centralizing tree scans in this package.
- Rule constructors are zero-knob unless an explicit project decision establishes otherwise. Any rule change must include a violating fixture/test and a compliant fixture/test.
- The backend import contract generator derives contracts from `docs/technical-spec.md`; do not hand-edit its output in `backend/pyproject.toml`. Regenerate from `backend/` with `uv run python scripts/gen_import_contracts.py` after DAG edits.
- No process-environment reads outside backend `infrastructure/config/`; conventions rules may inspect code statically but must not change the rule by introducing permissive exemptions.
- Do not disable or weaken gates. Ask the operator before considering a convention exception; the change proposing an exception must be visible in review and approved before recording it.

## Commands

From the repository root:

- `just lint`
- `just test-all`
- `just python-arch`
- `just api-types`
- `just up` / `just down`

From this package directory:

- `uv run basedpyright -p pyproject.toml`
- `uv run lint-imports`
- `uv run pytest -n auto`

## Quality gate and practice

Run `just lint`, `just python-arch`, and package tests before handoff; `just test-all` runs the full workspace gate. Use `python-code-style`, `python-testing`, `python-commands`, and `reconcile-docs` continuously. Architecture and layout gates are mandatory, never optional.
