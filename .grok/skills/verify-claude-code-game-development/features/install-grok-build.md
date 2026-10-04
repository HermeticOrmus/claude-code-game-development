# Install in Grok Build

A user installs claude-code-game-development plugins with the Grok Build CLI, which reads the same plugin folders as Claude Code. Each installed plugin shows as installed in `grok plugin list`.

## Sub-features

- `grok-install-one` installs one plugin with `--trust`.
- `grok-install-all` installs every plugin the Grok manifest lists.
- `grok-list` shows each installed plugin with status `installed`.
- `grok-manifest-sync` keeps `.grok-plugin/marketplace.json` matching the Claude manifest, where the repo has one.

## How to get to it (user POV)

- From a terminal: `grok plugin marketplace add HermeticOrmus/claude-code-game-development`, then `grok plugin install godot-development@claude-code-game-development --trust`.
- From a clone: `grok plugin marketplace add <checkout>`, then `grok plugin install godot-development@<checkout folder name> --trust`.

## Driving it with control-claude-code-game-development

Preconditions:

- `.grok/skills/verify-claude-code-game-development/bin/control-claude-code-game-development doctor` reports `worth_driving: true`, including `grok_manifest_in_sync: true`.

- **Add the marketplace and install one plugin.** Run `.grok/skills/verify-claude-code-game-development/bin/control-claude-code-game-development install --grok --only godot-development`. `evidence/grok-marketplace-add.log` and `evidence/grok-install-godot-development.log` end in `exit 0`.
- **Confirm it is installed.** `result.json` has `grok.installed` equal to `grok.wanted` and an empty `grok.missing`. `evidence/grok-list.json` lists the plugin with `"status": "installed"`.
- **Install the whole pack.** Run `.grok/skills/verify-claude-code-game-development/bin/control-claude-code-game-development run`. `result.json` has `grok.missing` empty and `ok: true`.
- **Proof.** Keep `evidence/grok-list.json` and `evidence/result.json` from the run.

## Gotchas

- Grok names a marketplace after the folder it was added from, not after `marketplace.json`. A clone in a folder with another name installs as `<plugin>@<that folder>`; the helper reads the name from the folder for you.
- `--trust` is required for a non-interactive install. Without it Grok stops to ask.
- After changing `.claude-plugin/marketplace.json`, run `python3 scripts/sync-grok-manifest.py` and commit what it writes, or `doctor` and `scripts/check.sh` fail on the sync check.
