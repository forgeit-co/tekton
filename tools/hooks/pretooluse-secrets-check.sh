#!/usr/bin/env bash

# Blocks commits that add tracked secrets or private keys.

HOOK_DIR=$(CDPATH='' cd -- "$(dirname -- "${0}")" && pwd)
source "${HOOK_DIR}/pretooluse-common.sh"

require_git_commit_command

command -v just > /dev/null 2>&1 || exit 0
just secrets-check
