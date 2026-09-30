#!/usr/bin/env bash

# Shared preamble for the PreToolUse hooks. Source it; do not run it.

function payload_field() {
  local PAYLOAD=${1}
  local FIELD=${2}

  command -v jq > /dev/null 2>&1 || return 1
  printf '%s' "${PAYLOAD}" | jq -r "${FIELD} // empty" 2> /dev/null
}

function is_git_commit_command() {
  local command_text=${1}
  local word
  local token=""
  local quote=""
  local escaped=0

  # Tokenize shell words without evaluating expansions, substitutions, or commands.
  local -a words=()
  local index=0
  local length=${#command_text}
  while [ "${index}" -lt "${length}" ]; do
    local char=${command_text:${index}:1}
    if [ "${escaped}" -eq 1 ]; then
      token+="${char}"
      escaped=0
    elif [ -n "${quote}" ]; then
      if [ "${char}" = "${quote}" ]; then quote=""; else token+="${char}"; fi
    else
      case "${char}" in
        "'"|"\"") quote=${char} ;;
        \\) escaped=1 ;;
        " "|$'\t')
          if [ -n "${token}" ]; then words+=("${token}"); token=""; fi
          ;;
        $'\n')
          if [ -n "${token}" ]; then words+=("${token}"); token=""; fi
          words+=(";")
          ;;
        \#)
          if [ -z "${token}" ]; then
            while [ "${index}" -lt "${length}" ] && [ "${command_text:${index}:1}" != $'\n' ]; do
              index=$((index + 1))
            done
          else
            token+="${char}"
          fi
          ;;
        \;|\&|\|)
          if [ -n "${token}" ]; then words+=("${token}"); token=""; fi
          if [ "${command_text:${index}:2}" = '&&' ] || [ "${command_text:${index}:2}" = '||' ]; then
            words+=("${command_text:${index}:2}")
            index=$((index + 1))
          else
            words+=("${char}")
          fi
          ;;
        *) token+="${char}" ;;
      esac
    fi
    index=$((index + 1))
  done
  [ -n "${token}" ] && words+=("${token}")
  [ -n "${quote}" ] && return 1

  local command_index=0
  while [ "${command_index}" -lt "${#words[@]}" ]; do
    word=${words[${command_index}]}
    case "${word}" in
      ';'|'&'|'|'|'&&'|'||'|'('|')')
        command_index=$((command_index + 1))
        continue
        ;;
      env|command|builtin|exec)
        command_index=$((command_index + 1))
        continue
        ;;
    esac

    if [[ "${word}" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
      command_index=$((command_index + 1))
      continue
    fi

    [ "${word##*/}" = git ] || {
      while [ "${command_index}" -lt "${#words[@]}" ]; do
        case "${words[${command_index}]}" in
          ';'|'&'|'|'|'&&'|'||'|'('|')') break ;;
        esac
        command_index=$((command_index + 1))
      done
      continue
    }

    command_index=$((command_index + 1))
    while [ "${command_index}" -lt "${#words[@]}" ]; do
      word=${words[${command_index}]}
      case "${word}" in
        -C|-c|--git-dir|--work-tree|--namespace|--exec-path|--config-env)
          command_index=$((command_index + 2))
          ;;
        --)
          command_index=$((command_index + 1))
          break
          ;;
        -*) command_index=$((command_index + 1)) ;;
        *) break ;;
      esac
    done

    [ "${command_index}" -lt "${#words[@]}" ] && [ "${words[${command_index}]}" = commit ] && return 0
    while [ "${command_index}" -lt "${#words[@]}" ]; do
      case "${words[${command_index}]}" in
        ';'|'&'|'|'|'&&'|'||'|'('|')') break ;;
      esac
      command_index=$((command_index + 1))
    done
  done
  return 1
}

function require_git_commit_command() {
  local PAYLOAD
  PAYLOAD=$(cat)

  COMMAND=$(payload_field "${PAYLOAD}" '.tool_input.command') || COMMAND=${PAYLOAD}
  [ -z "${COMMAND}" ] && exit 0
  is_git_commit_command "${COMMAND}" || exit 0

  local SESSION_CWD
  SESSION_CWD=$(payload_field "${PAYLOAD}" '.cwd')
  if [ -z "${SESSION_CWD}" ] || [ ! -d "${SESSION_CWD}" ]; then
    echo "Commit guard blocked: session working directory is missing." >&2
    exit 2
  fi

  command -v git > /dev/null 2>&1 || {
    echo "Commit guard blocked: git is not available." >&2
    exit 2
  }
  command -v just > /dev/null 2>&1 || {
    echo "Commit guard blocked: just is not available for commit checks." >&2
    exit 2
  }

  local REPO_ROOT
  REPO_ROOT=$(git -C "${SESSION_CWD}" rev-parse --show-toplevel 2>/dev/null) || {
    echo "Commit guard blocked: cannot resolve repository root from '${SESSION_CWD}'." >&2
    exit 2
  }
  cd "${REPO_ROOT}" || {
    echo "Commit guard blocked: cannot enter repository root '${REPO_ROOT}'." >&2
    exit 2
  }
}
