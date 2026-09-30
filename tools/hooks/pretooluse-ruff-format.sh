#!/usr/bin/env bash

# Blocks commits while Python files fail ruff format --check.

source "$(dirname -- "${BASH_SOURCE[0]}")/pretooluse-common.sh"

require_git_commit_command

command -v uv > /dev/null 2>&1 || {
  echo "Commit guard blocked: uv is not available for the required ruff format check." >&2
  exit 2
}

FORMAT_OUTPUT=$(uv run --locked ruff format --check . 2>&1)
FORMAT_STATUS=$?
[ "${FORMAT_STATUS}" -eq 0 ] && exit 0

{
  echo "Commit blocked by ruff-format: Python files are not formatted:"
  printf '%s\n' "${FORMAT_OUTPUT}"
  echo
  echo "Run uv run ruff format ., then commit again."
} >&2

exit 2
