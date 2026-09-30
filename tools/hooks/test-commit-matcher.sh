#!/usr/bin/env bash
set -euo pipefail

source "$(dirname -- "${BASH_SOURCE[0]}")/pretooluse-common.sh"

expect_match() {
  local command=${1}
  if ! is_git_commit_command "${command}"; then
    printf 'expected commit match: %s\n' "${command}" >&2
    exit 1
  fi
}

expect_no_match() {
  local command=${1}
  if is_git_commit_command "${command}"; then
    printf 'unexpected commit match: %s\n' "${command}" >&2
    exit 1
  fi
}

expect_match 'git commit -m change'
expect_match 'git -C "repo with spaces" commit -m change'
expect_match 'git -c core.hooksPath=hooks commit -m change'
expect_match 'git --git-dir="repo with spaces/.git" --work-tree="repo with spaces" commit -m change'
expect_match 'git -c user.name=Agent -C "repo with spaces" commit -m change'
expect_match 'GIT_OPTIONAL_LOCKS=0 command git -C "repo with spaces" commit -m change'
expect_match 'git -c key=value commit; echo done'
expect_no_match 'echo "git commit -m example"'
expect_no_match 'git status'
expect_no_match 'git -C elsewhere status'
expect_no_match 'git commitish'

printf 'commit matcher tests passed\n'
