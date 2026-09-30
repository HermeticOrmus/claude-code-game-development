# Changelog

All notable changes to this repository are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- A public pantry in [`pantry/`](pantry/README.md): a competitor map, an X mine, a people mine and a pantry queue of Goal atoms, each row with its source, plus the templates for the next run.
- [`pantry/MENU.md`](pantry/MENU.md), generated from the pantry queue, which names one up-next item with a Done-when anyone can check.
- Two issue forms: routing miss (Claude picked the wrong agent or skill) and plugin proposal, with the `routing-miss` and `plugin-proposal` labels.
- A "Ways to contribute" section at the top of `CONTRIBUTING.md` (Menu items, routing misses, new plugins and their layout, translations, sharing what you built) with the local test loop, and a short "Contribute" section in the README.
- Grok Build support: `.grok-plugin/marketplace.json`, generated from the Claude manifest by `scripts/sync-grok-manifest.py`, so `grok plugin marketplace add HermeticOrmus/claude-code-game-development` then `grok plugin install <plugin>@claude-code-game-development` works, as does `grok plugin install HermeticOrmus/claude-code-game-development#plugins/<plugin>`. CI checks the generated file, runs `grok plugin validate` on every plugin, and installs all 87 into a clean Grok home. The README shows the Grok Build install; `libre-gamedev-hooks` is not yet verified in a live Grok session.
- `./setup.sh --grok` installs through the `grok` CLI instead of `claude`, with the same `--only`, `--list`, and `--uninstall` behavior. Because grok uninstalls by name and 66 names are shared with LibreUIUX, `--uninstall` removes this pack's marketplace and `--uninstall --only` skips a name installed from somewhere else too.
- `LEDGER.md`, the kintsugi ledger: every crack the 2.0.0 release found and sealed, with its evidence, and the cracks still open.

### Fixed

- The 17 derived plugins that had no `.claude-plugin/plugin.json` now have one, copied from their marketplace entries, which move to `strict: true`. Grok Build names a plugin from its `plugin.json`, so it had installed them under hashed names with no version. Claude Code loads the same components as before.

## [2.0.0] - 2026-09-30

This is a major version because the plugin marketplace changes its name. In 1.x it was `claude-code-workflows`, the same name as [wshobson/agents](https://github.com/wshobson/agents), which meant you could not add both. It is now `claude-code-game-development`. If you added this repo before, read [Migrating from 1.x](README.md#migrating-from-1x): check where `claude-code-workflows` points, remove it only if it points here, then add this repo again.

### Added

- 20 game development plugins from [LibreGameDev](https://github.com/HermeticOrmus/LibreGameDev-Claude-Code), each with an agent, a slash command with focused actions, and a skill: `godot-development`, `unity-development`, `unreal-engine`, `game-architecture`, `input-systems`, `save-systems`, `localization`, `shader-programming`, `animation-systems`, `audio-systems`, `ui-game-design`, `ai-game-behavior`, `physics-simulation`, `procedural-generation`, `level-design`, `playtesting`, `performance-optimization`, `asset-pipelines`, `multiplayer-networking`, `monetization-ethics`. Before this release the only game plugin was `game-development`.
- `libre-gamedev-hooks`, an optional hooks plugin: one line of context at session start for Godot, Unity, Unreal, and web game projects; a confirmation prompt before a tool touches `.env` files, keys, Android keystores, or Godot export credentials, and before `rm -rf`, force pushes, hard resets, or `git clean -f`; a note after a write leaves a file empty, and a once-per-session reminder to run the tests.
- `NOTICE.md`, listing the 66 plugins and the `.github` files that come from wshobson/agents, the manifest-only changes made to them here, and the upstream MIT notice in full.
- `setup.sh`, which installs from a checkout through the Claude Code plugin CLI (`--only`, `--list`, `--scope`, `--uninstall`).
- A CI workflow that validates the marketplace and all 87 plugins, installs every one into a clean config, and fails if any plugin reports load errors.
- A feedback issue form.
- README sections: install instructions, Game Plugins (every game plugin's agent, command, and skill, plus a table of the other 65), Migrating from 1.x, and Feedback.

### Changed

- The marketplace is renamed from `claude-code-workflows` to `claude-code-game-development`, owned by Diego Bodart, with a description of this repo. Install plugins as `<plugin>@claude-code-game-development`.
- The 66 plugins derived from wshobson/agents keep their names, versions, content, and Seth Hobson as author. 49 of them gained a `.claude-plugin/plugin.json` copied from their marketplace entry (with the entry set to `strict: true`) so that `claude plugin validate` passes on every plugin directory. They load the same agents, commands, and skills as before.
- `LICENSE` keeps its existing copyright line and adds `Copyright (c) 2024 Seth Hobson` for the derived plugins. The README acknowledgments now credit Seth Hobson and wshobson/agents first.
- The issue chooser's contact links point at this repo instead of wshobson/agents.
- The README's counts match the repo: 87 plugins (22 for games), 180,000+ words across 80 documentation files, and per-section word counts. Directories the README described but that were never added (`examples/`, `templates/`, `prompts/`, `resources/`, `community/`) are marked as not added yet instead of being presented as present.

### Fixed

- `shell-scripting` failed to load its three skills because its marketplace entry pointed at the `SKILL.md` files instead of the skill directories.
- The Quick Start told you to `cd examples/01-simple-games/pong`, which does not exist. It now points at the Pong tutorial in `docs/01-getting-started/first-game-in-10-minutes.md`.
- A Quick Start link to `docs/10-performance-optimization/spatial-partitioning.md` now points at `docs/09-advanced-patterns/spatial-partitioning.md`, where the file is.
- Clone commands in the README and `docs/01-getting-started/installation-setup.md` used `github.com/yourusername/...`; they now use `HermeticOrmus`.

### Known warnings

- `claude plugin validate` reports 67 warnings on derived plugins: those command files have no YAML frontmatter. They validate and load; the files are left as they came from wshobson/agents.

## [1.x]

The marketplace was named `claude-code-workflows` and carried 66 plugins imported from wshobson/agents, alongside the `docs/` curriculum and `tools/meta-prompting-framework/`. No changelog was kept for 1.x.
