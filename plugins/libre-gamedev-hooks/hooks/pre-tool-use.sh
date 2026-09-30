#!/usr/bin/env bash
# PreToolUse hook - Game Development
# Asks for confirmation before a tool touches secrets or signing keys, or before
# a destructive shell command runs. Silent (exit 0, no output) otherwise.
# Claude Code sends the hook input as JSON on stdin.

command -v jq >/dev/null 2>&1 || exit 0
input="$(cat 2>/dev/null || true)"
[ -n "$input" ] || exit 0

tool="$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null)"
path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' 2>/dev/null)"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"

# True when the file name looks like it holds secrets: .env files (not the
# .example/.sample/.template ones), keys and certificates, Android signing
# keystores, Godot export credentials, credentials/secrets files.
# Matches whole file names only, so a level called secret_room.tscn is fine.
is_sensitive() {
  local name="${1##*/}"
  name="${name,,}"
  case "$name" in
    .env.example|.env.sample|.env.template) return 1 ;;
    .env|.env.*) return 0 ;;
    *.pem|*.key|*.p12|*.pfx|*.keystore|*.jks) return 0 ;;
    export_credentials.cfg) return 0 ;;
    client_secret*.json) return 0 ;;
  esac
  [[ "$name" =~ ^\.?(credentials|secrets?)(\.[a-z0-9]+)?$ ]]
}

ask() {
  jq -n --arg r "$1" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"ask",permissionDecisionReason:$r}}'
  exit 0
}

if [ -n "$path" ] && is_sensitive "$path"; then
  ask "LibreGameDev: $tool targets a file that may hold secrets or signing keys ($path). Confirm this is intended."
fi

if [ "$tool" = "Bash" ] && [ -n "$cmd" ]; then
  set -f
  for word in $(printf '%s' "$cmd" | tr ';|&<>()"'\''=' ' '); do
    if is_sensitive "$word"; then
      ask "LibreGameDev: this command references $word, which may hold secrets or signing keys. Confirm this is intended."
    fi
  done
  if printf '%s' "$cmd" | grep -qE '(^|[;&|[:space:]])rm[[:space:]]+-[a-zA-Z]*(rf|fr)|git[[:space:]]+push([[:space:]]+[^;&|]*)?[[:space:]](--force[a-z-]*|-f)([[:space:]]|$)|git[[:space:]]+reset[[:space:]]+--hard|git[[:space:]]+clean[[:space:]]+-[a-zA-Z]*f'; then
    ask "LibreGameDev: destructive command detected (recursive delete, force push, hard reset, or clean). Confirm before it runs."
  fi
fi
exit 0
