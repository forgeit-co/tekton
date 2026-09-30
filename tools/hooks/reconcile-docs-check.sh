#!/usr/bin/env bash

# Detects a change set that touches code but no documentation.
# Usage: reconcile-docs-check.sh [--staged | --working-tree]

function is_doc_path() {
  local CHANGED_PATH=${1}

  case "${CHANGED_PATH}" in
    docs/* | */docs/*) return 0 ;;
  esac

  case "${CHANGED_PATH##*/}" in
    README.md | ROADMAP.md | CHANGELOG.md | CLAUDE.md) return 0 ;;
  esac

  return 1
}

case "${1:---staged}" in
  --staged) CHANGED_FILES=$(git diff --cached --name-only 2> /dev/null) || exit 0 ;;
  --working-tree) CHANGED_FILES=$(git status --porcelain --untracked-files=all 2> /dev/null | grep -v '^!!' | cut -c4-) || exit 0 ;;
  *) echo "usage: ${0##*/} [--staged | --working-tree]" >&2; exit 0 ;;
esac
[ -z "${CHANGED_FILES}" ] && exit 0

CODE_FILES=""
DOCS_PRESENT=""

while IFS= read -r CHANGED_FILE; do
  [ -z "${CHANGED_FILE}" ] && continue
  if is_doc_path "${CHANGED_FILE}"; then
    DOCS_PRESENT="yes"
  else
    CODE_FILES="${CODE_FILES}${CHANGED_FILE}"$'\n'
  fi
done <<< "${CHANGED_FILES}"

[ -z "${CODE_FILES}" ] && exit 0
[ -n "${DOCS_PRESENT}" ] && exit 0

printf '%s' "${CODE_FILES}"
exit 3
