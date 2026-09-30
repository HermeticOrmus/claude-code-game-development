#!/usr/bin/env bash
# PostToolUse hook - Game Development
# After a write or edit: warns when the file ended up empty, and once per
# session reminds Claude to run the project's tests after a code change.
# Claude Code sends the hook input as JSON on stdin. Silent otherwise.

command -v jq >/dev/null 2>&1 || exit 0
input="$(cat 2>/dev/null || true)"
[ -n "$input" ] || exit 0

tool="$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null)"
path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)"
session="$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)"

case "$tool" in Write|Edit|MultiEdit) ;; *) exit 0 ;; esac
[ -n "$path" ] || exit 0

say() {
  jq -n --arg c "$1" '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
  exit 0
}

if [ -f "$path" ] && [ ! -s "$path" ]; then
  say "LibreGameDev: $path is empty after $tool. Check that the write went through as intended."
fi

# Game code: GDScript, C#, C++, shaders, plus common scripting languages.
if printf '%s' "$path" | grep -qiE '\.(gd|cs|cpp|cc|h|hpp|gdshader|hlsl|glsl|js|ts|py|rs|go|java|rb|lua)$'; then
  marker="${TMPDIR:-/tmp}/libre-gamedev-hooks-${session:-nosession}.reminded"
  if [ ! -e "$marker" ]; then
    : > "$marker" 2>/dev/null || true
    say "LibreGameDev: code changed. Before calling it done, run the project's tests (GUT for Godot, the Unity Test Runner, Unreal's Automation system, or the project's own test command)."
  fi
fi
exit 0
