# Install from Claude Code

A user adds claude-code-game-development as a plugin marketplace in Claude Code and installs plugins from it by name. Each installed plugin shows as enabled under the `claude-code-game-development` marketplace and its components are available after a restart.

## Sub-features

- `claude-marketplace-add` registers the repo as the `claude-code-game-development` marketplace.
- `claude-install-one` installs one plugin as `<plugin>@claude-code-game-development`.
- `claude-install-all` installs every plugin in the pack (87 in total).
- `claude-list` shows each installed plugin as enabled.

## How to get to it (user POV)

- Inside Claude Code: `/plugin marketplace add HermeticOrmus/claude-code-game-development`, then `/plugin install godot-development@claude-code-game-development`.
- From a terminal: `claude plugin marketplace add HermeticOrmus/claude-code-game-development`, then `claude plugin install godot-development@claude-code-game-development`.
- `/plugin` inside Claude Code opens the plugin manager to browse the rest of the pack.

## Driving it with control-claude-code-game-development

Preconditions:

- `.grok/skills/verify-claude-code-game-development/bin/control-claude-code-game-development doctor` reports `worth_driving: true`.

- **Add the marketplace and install one plugin.** Run `.grok/skills/verify-claude-code-game-development/bin/control-claude-code-game-development install --claude --only godot-development`. `evidence/claude-marketplace-add.log` and `evidence/claude-install-godot-development.log` end in `exit 0`.
- **Confirm it is enabled.** The same command prints `result.json`: `claude.enabled` is 1, `claude.missing` and `claude.load_errors` are empty. `evidence/claude-list.json` has `godot-development@claude-code-game-development` with `"enabled": true`.
- **Install the whole pack.** Run `.grok/skills/verify-claude-code-game-development/bin/control-claude-code-game-development run`. `result.json` has `claude.wanted` equal to `claude.enabled` (87) and `ok: true`.
- **Proof.** Keep `evidence/claude-list.json` and `evidence/result.json` from the run.

## Gotchas

- The marketplace name is `claude-code-game-development` (from `.claude-plugin/marketplace.json`), not the repo name. `<plugin>@claude-code-game-development` fails in Claude Code.
- Installing from `HermeticOrmus/claude-code-game-development` installs what is on GitHub's default branch. To prove a change, install from the tree under test, which is what the helper does.
- Claude Code loads new plugins at the next session start. The proof is the list and details read back, not a live session.
