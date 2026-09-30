#!/usr/bin/env bash

# Blocks commits while frontend files fail Prettier.
# Bypass: PRETTIER_OK=1 before git commit.

HOOK_DIR=$(CDPATH='' cd -- "$(dirname -- "${0}")" && pwd)
source "${HOOK_DIR}/pretooluse-common.sh"

require_git_commit_command
bypassed PRETTIER_OK && exit 0

command -v pnpm > /dev/null 2>&1 || exit 0

FORMAT_OUTPUT=$(cd frontend && pnpm exec prettier --check . 2>&1)
FORMAT_STATUS=$?
[ "${FORMAT_STATUS}" -eq 0 ] && exit 0

{
  echo "Commit blocked by prettier: frontend files are not formatted:"
  printf '%s\n' "${FORMAT_OUTPUT}"
  echo
  echo "Run pnpm --dir frontend exec prettier --write ., then commit again."
  echo "To deliberately bypass this check, prefix the commit with PRETTIER_OK=1."
} >&2

exit 2
