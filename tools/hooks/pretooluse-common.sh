#!/usr/bin/env bash

# Shared preamble for the PreToolUse hooks. Source it; do not run it.

function payload_field() {
  local PAYLOAD=${1}
  local FIELD=${2}

  command -v jq > /dev/null 2>&1 || return 1
  printf '%s' "${PAYLOAD}" | jq -r "${FIELD} // empty" 2> /dev/null
}

function require_git_commit_command() {
  local PAYLOAD
  PAYLOAD=$(cat)

  COMMAND=$(payload_field "${PAYLOAD}" '.tool_input.command') || COMMAND=${PAYLOAD}
  [ -z "${COMMAND}" ] && exit 0

  case "${COMMAND}" in
    *"git commit"*) ;;
    *) exit 0 ;;
  esac

  local SESSION_CWD
  SESSION_CWD=$(payload_field "${PAYLOAD}" '.cwd')
  if [ -n "${SESSION_CWD}" ] && [ -d "${SESSION_CWD}" ]; then
    cd "${SESSION_CWD}" || exit 0
  fi

  command -v git > /dev/null 2>&1 || exit 0
}

function bypassed() {
  local TOKEN_NAME=${1}
  local BYPASS_RE="${TOKEN_NAME}=[^[:space:]]+([[:space:]]+[A-Za-z_][A-Za-z0-9_]*=[^[:space:]]+)*[[:space:]]+git[[:space:]]+commit"

  [[ ${COMMAND} =~ ${BYPASS_RE} ]] && return 0
  [ -n "${!TOKEN_NAME}" ] && return 0
  return 1
}
