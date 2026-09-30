#!/usr/bin/env bash

# Blocks commits while Python files fail ruff format --check.
# Bypass: RUFF_FORMAT_OK=1 before git commit.

HOOK_DIR=$(CDPATH='' cd -- "$(dirname -- "${0}")" && pwd)
source "${HOOK_DIR}/pretooluse-common.sh"

require_git_commit_command
bypassed RUFF_FORMAT_OK && exit 0

command -v uv > /dev/null 2>&1 || exit 0

FORMAT_OUTPUT=$(uv run --locked ruff format --check . 2>&1)
FORMAT_STATUS=$?
[ "${FORMAT_STATUS}" -eq 0 ] && exit 0

{
  echo "Commit blocked by ruff-format: Python files are not formatted:"
  printf '%s\n' "${FORMAT_OUTPUT}"
  echo
  echo "Run uv run ruff format ., then commit again."
  echo "To deliberately bypass this check, prefix the commit with RUFF_FORMAT_OK=1."
} >&2

exit 2
