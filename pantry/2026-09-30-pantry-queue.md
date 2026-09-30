# Pantry queue: Claude Code Game Dev

## How this fills

1. Read the latest competitor map, X mine and people mine.
2. Propose 5 to 8 Goal atoms that answer their themes. The Menu needs at least 3.
3. Each atom needs a Done predicate someone else can check on this repo, a surface, the evidence rows it answers, and a confidence (high, medium or low).
4. Save as `YYYY-MM-DD-pantry-queue.md`; the Menu reads the newest one.
5. Retire an atom only with a bullet under "Explicitly not stocked" of the form `<Title>: shipped, PR #N` or `<Title>: parked, <reason>`.

Sources for this run: [competitor map](2026-09-30-competitor-map.md), [X mine](2026-09-30-x-mine.md), [people mine](2026-09-30-people-mine.md).

## Atoms

| # | Title | Done predicate | Surface | Evidence | Confidence |
|---|-------|----------------|---------|----------|------------|
| 1 | Add a `web-game-development` plugin for Phaser and Three.js | `claude plugin validate --strict plugins/web-game-development` exits 0; `.claude-plugin/marketplace.json` lists it with `category: "gaming"`; after `claude plugin marketplace add ./` in a clean `CLAUDE_CONFIG_DIR`, `claude plugin details web-game-development@claude-code-game-development` lists its agent and its skill; the skill links `docs/08-game-engines/phaser-integration.md` and `docs/08-game-engines/three-js-games.md`; the README Game Plugins tables have its row | repo | Map rows game-creator, threejs-game-skills and awesome-gamedev-agent-skills; matrix row "Web game frameworks" (Us P: the manual covers Phaser, Three.js and Babylon.js, and `libre-gamedev-hooks` already detects web game projects, but no plugin exists); X row threejs-game-skills | high |
| 2 | Add frontmatter to the 67 derived command files (`derived-command-frontmatter`) | For every plugin in `.claude-plugin/marketplace.json`, `claude plugin validate --strict plugins/<name>` exits 0 (40 plugins on `main` fail it on 67 "No frontmatter block found" warnings); 66 of the files take their frontmatter from the same path in wshobson/agents, and `plugins/code-review-ai/commands/ai-review.md`, which upstream no longer has, gets a written `description:`; `NOTICE.md` "Changes made here to derived files" names the upstream commit used; the CHANGELOG "Known warnings" note is updated | repo | Map row wshobson/agents (upstream command files now open with `description:` frontmatter; 66 of our 67 paths still exist upstream, all with frontmatter); matrix row "Validated in CI" | high |
| 3 | Document pairing the engine plugins with an editor MCP server (`editor-mcp-guide`) | A README section, linked from Game Plugins, shows the `claude mcp add` (or official install) steps for one Godot editor server and one Unity editor server named in the competitor map, says which of our agents to use with each, and every `claude` command in it matches `claude mcp add --help` | repo | Matrix row "Live editor control" (Us N; Unity's plugin, unity-mcp and godot-ai Y); Map rows Unreal MCP (Epic) and Roblox Studio MCP; X rows unity-mcp, MCP Unity and Unreal MCP | medium |
| 4 | Add a `roblox-development` plugin for Luau and Roblox Studio | `claude plugin validate --strict plugins/roblox-development` exits 0; `.claude-plugin/marketplace.json` lists it with `category: "gaming"`; `claude plugin details roblox-development@claude-code-game-development` in a clean `CLAUDE_CONFIG_DIR` lists its agent and its skill; the skill names the Roblox Studio MCP server as the way to act on a live place; the README Game Plugins tables have its row | repo | Matrix row "Other engines" (Us N, awesome-gamedev-agent-skills Y); Map row Roblox Studio MCP (first-party, quick connect for Claude Code) | medium |
| 5 | Teach the asset-pipelines skill glTF import from Blender (`gltf-import-patterns`) | `plugins/asset-pipelines/skills/asset-pipeline-patterns/SKILL.md` has a section on exporting glTF 2.0 from Blender and importing it into Godot 4 and Unity (scale, axes, materials, animations, import settings), and the `asset-pipeline-engineer` agent's source formats include glTF; `claude plugin validate --strict plugins/asset-pipelines` exits 0 | repo | Matrix row "Asset generation or asset tooling" (Us P: the skill has no glTF or Blender handoff); Map row mcp-for-blender; X row Blender MCP | medium |
| 6 | Add the Pong example the README describes (`pong-example`) | `examples/01-simple-games/pong/` holds `index.html` that plays in a browser with no build step (AI opponent and scoring, as in `docs/01-getting-started/first-game-in-10-minutes.md`), a `README.md` on its architecture and a `PROMPTS.md` with the Claude Code prompts used; the README's `/examples` section links it | repo | Matrix row "Learning material" (Us Y for the manual, but README "Described here, not in the repository yet" lists `examples/` as missing); Map row game-creator (ships playable example games) | medium |

## Explicitly not stocked (and why)

- Japanese README: parked, invitation to its author pending
- Add frontmatter to the 67 derived command files (`derived-command-frontmatter`): parked, the same work is already open as good first issue #4
- Our own engine MCP server: not stocked. Unity, Epic and Roblox ship first-party editor bridges and community servers are well established (competitor map), so the pairing docs in atom 3 come first.
- Changes inside `tools/meta-prompting-framework/`: not stocked. It is third-party code credited in `NOTICE.md`; fixes belong upstream.
- `templates/`, `prompts/`, `resources/` and `community/` directories: not stocked this run. The README lists them as not added yet, but no competitor, X or people row asks for them.
