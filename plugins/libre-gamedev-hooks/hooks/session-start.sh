#!/usr/bin/env bash
# SessionStart hook - Game Development
# Detects the game engine in the project and prints one line of context.
# Claude Code sends the hook input as JSON on stdin; stdout becomes session context.
# Prints nothing when the project is not a game project.

input="$(cat 2>/dev/null || true)"
dir=""
if command -v jq >/dev/null 2>&1 && [ -n "$input" ]; then
  dir="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null || true)"
fi
[ -n "$dir" ] && [ -d "$dir" ] || dir="$PWD"

engines=()
[ -f "$dir/project.godot" ] && engines+=("Godot (project.godot)")
[ -d "$dir/Assets" ] && [ -d "$dir/ProjectSettings" ] && engines+=("Unity (Assets/ + ProjectSettings/)")
compgen -G "$dir/*.uproject" >/dev/null 2>&1 && engines+=("Unreal (.uproject)")
if [ -f "$dir/package.json" ] && grep -qE '"(phaser|pixi\.js|three|@babylonjs/core|kaboom|kaplay)"' "$dir/package.json" 2>/dev/null; then
  engines+=("web game (package.json)")
fi

if [ "${#engines[@]}" -gt 0 ]; then
  list="$(printf '%s, ' "${engines[@]}")"
  echo "[LibreGameDev] Game project detected: ${list%, }. The game dev agents, commands, and skills apply here."
fi
exit 0
