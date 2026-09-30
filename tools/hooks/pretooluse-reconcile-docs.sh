#!/usr/bin/env bash

# Blocks commits that change code without documentation.
# Bypass: RECONCILE_DOCS_OK=1 before git commit.

HOOK_DIR=$(CDPATH='' cd -- "$(dirname -- "${0}")" && pwd)
source "${HOOK_DIR}/pretooluse-common.sh"

require_git_commit_command
bypassed RECONCILE_DOCS_OK && exit 0

CHECK_SCRIPT="${HOOK_DIR}/reconcile-docs-check.sh"
[ -x "${CHECK_SCRIPT}" ] || exit 0

CODE_FILES=$("${CHECK_SCRIPT}" --working-tree)
CHECK_STATUS=$?
[ "${CHECK_STATUS}" -eq 3 ] || exit 0

{
  echo "Commit blocked by reconcile-docs: the change set touches code but no documentation:"
  printf '%s\n' "${CODE_FILES}" | sed 's/^/  /'
  echo
  echo "Run the reconcile-docs skill to update warranted docs (ADRs, API references, READMEs, ROADMAP, gaps/)."
  echo "If no docs are genuinely needed, re-run the commit prefixed with RECONCILE_DOCS_OK=1."
} >&2

exit 2
