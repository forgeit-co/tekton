#!/usr/bin/env bash

# Blocks commits touching source until the language structure/style guard has run.
# Bypass: STRUCTURE_STYLE_GUARD_OK=1 before git commit.

HOOK_DIR=$(CDPATH='' cd -- "$(dirname -- "${0}")" && pwd)
source "${HOOK_DIR}/pretooluse-common.sh"

RUST_SOURCE_RE='\.rs$'
WEB_SOURCE_RE='^frontend/src/'
WEB_CONFIG_RE='^frontend/.*\.(ts|tsx|js|jsx|vue|json|html|css|scss|yaml|yml)$'
WEB_FRAMEWORK='vue'
PYTHON_SOURCE_RE='\.py$'

require_git_commit_command
bypassed STRUCTURE_STYLE_GUARD_OK && exit 0

ALL_CHANGED=$(git status --porcelain --untracked-files=all 2> /dev/null | grep -v '^!!' | cut -c4-)
[ -z "${ALL_CHANGED}" ] && exit 0

HAS_RUST=$(printf '%s\n' "${ALL_CHANGED}" | grep -cE "${RUST_SOURCE_RE}" || true)
HAS_WEB=$(printf '%s\n' "${ALL_CHANGED}" | grep -cE "${WEB_SOURCE_RE}|${WEB_CONFIG_RE}" || true)
HAS_PYTHON=$(printf '%s\n' "${ALL_CHANGED}" | grep -cE "${PYTHON_SOURCE_RE}" || true)

[ "${HAS_RUST}" -eq 0 ] && [ "${HAS_WEB}" -eq 0 ] && [ "${HAS_PYTHON}" -eq 0 ] && exit 0

SKILLS=""
if [ "${HAS_RUST}" -gt 0 ]; then
  SKILLS="${SKILLS}  /rust-structure-and-style-guard\n"
fi
if [ "${HAS_WEB}" -gt 0 ]; then
  SKILLS="${SKILLS}  /${WEB_FRAMEWORK}-structure-and-style-guard\n"
fi
if [ "${HAS_PYTHON}" -gt 0 ]; then
  SKILLS="${SKILLS}  /python-structure-and-style-guard\n"
fi

SOURCE_FILES=$(printf '%s\n' "${ALL_CHANGED}" | grep -E "${RUST_SOURCE_RE}|${WEB_SOURCE_RE}|${WEB_CONFIG_RE}|${PYTHON_SOURCE_RE}" | sed 's/^/  /')

{
  echo "Commit blocked by structure-and-style-guard: source has not been reviewed:"
  printf '%s\n' "${SOURCE_FILES}"
  echo
  echo "Run the matching guard skill(s):"
  printf '%b' "${SKILLS}"
  echo "Then address applicable findings and re-commit prefixed with STRUCTURE_STYLE_GUARD_OK=1."
} >&2

exit 2
