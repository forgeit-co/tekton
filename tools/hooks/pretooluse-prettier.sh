#!/usr/bin/env bash

# Blocks commits while frontend files fail Prettier.

source "$(dirname -- "${BASH_SOURCE[0]}")/pretooluse-common.sh"

require_git_commit_command

command -v pnpm > /dev/null 2>&1 || {
  echo "Commit guard blocked: pnpm is not available for the required Prettier check." >&2
  exit 2
}

FORMAT_OUTPUT=$(cd frontend && pnpm exec prettier --check . 2>&1)
FORMAT_STATUS=$?
[ "${FORMAT_STATUS}" -eq 0 ] && exit 0

{
  echo "Commit blocked by prettier: frontend files are not formatted:"
  printf '%s\n' "${FORMAT_OUTPUT}"
  echo
  echo "Run pnpm --dir frontend exec prettier --write ., then commit again."
} >&2

exit 2
