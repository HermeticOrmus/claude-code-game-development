# LibreGameDev Hooks

> Optional Claude Code hooks for game projects. Install it on its own; the other plugins do not need it.

## What it does

| Event | Script | Behavior |
|---|---|---|
| `SessionStart` | `hooks/session-start.sh` | Looks at the session's working directory. If it finds `project.godot` (Godot), `Assets/` plus `ProjectSettings/` (Unity), a `*.uproject` file (Unreal), or a `package.json` that depends on Phaser, PixiJS, Three.js, Babylon.js, Kaboom, or KAPLAY (web game), it prints one line of context naming the engine. Otherwise it prints nothing. |
| `PreToolUse` (`Read`, `Write`, `Edit`, `MultiEdit`, `Bash`) | `hooks/pre-tool-use.sh` | Asks you to confirm before a tool touches a file whose name suggests secrets or signing keys: `.env` files (not `.env.example`), `*.pem`, `*.key`, `*.p12`, `*.pfx`, Android `*.keystore` and `*.jks`, Godot's `export_credentials.cfg`, `client_secret*.json`, and files named `credentials` or `secrets`. Also asks before `rm -rf`, `git push --force`, `git reset --hard`, and `git clean -f`. Silent for everything else. |
| `PostToolUse` (`Write`, `Edit`, `MultiEdit`) | `hooks/post-tool-use.sh` | Tells Claude when a written file ended up empty. After the first code change in a session (GDScript, C#, C++, shaders, and common scripting languages), reminds Claude once to run the project's tests. |

Matching is on whole file names, so a level called `secret_room.tscn` does not trigger a prompt.

## Install

```
/plugin marketplace add HermeticOrmus/claude-code-game-development
/plugin install libre-gamedev-hooks@claude-code-game-development
```

Or from a checkout: `./setup.sh --only libre-gamedev-hooks`.

## Requirements

- `bash` and `jq` on `PATH`. Without `jq` the tool hooks exit silently and do nothing.

## Notes

- The scripts read the hook input JSON that Claude Code sends on stdin (`tool_name`, `tool_input.file_path`, `tool_input.command`, `cwd`, `session_id`).
- Nothing is written inside the plugin directory. The once-per-session test reminder leaves an empty marker file in `$TMPDIR` (or `/tmp`).
- A prompt is a question, not a block: you can always approve and continue.
