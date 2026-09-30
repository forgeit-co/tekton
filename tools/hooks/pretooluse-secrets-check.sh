#!/usr/bin/env bash

# Blocks commits that add tracked secrets or private keys.

source "$(dirname -- "${BASH_SOURCE[0]}")/pretooluse-common.sh"

require_git_commit_command

if ! just secrets-check; then
  echo "Commit guard blocked: secrets-check failed." >&2
  exit 2
fi
