# Menu: claude-code-game-development

Queue: 2026-09-30-pantry-queue.md
Counts: open 5, in flight 0, shipped 0, parked 1, dropped 0, needs fixing 0

## Steer

- none

## Up next

**web-game-development**: Add a `web-game-development` plugin for Phaser and Three.js (queue #1, high, repo, since 2026-09-30)

- Done when: `claude plugin validate --strict plugins/web-game-development` exits 0; `.claude-plugin/marketplace.json` lists it with `category: "gaming"`; after `claude plugin marketplace add ./` in a clean `CLAUDE_CONFIG_DIR`, `claude plugin details web-game-development@claude-code-game-development` lists its agent and its skill; the skill links `docs/08-game-engines/phaser-integration.md` and `docs/08-game-engines/three-js-games.md`; the README Game Plugins tables have its row
- Verify on: repo
- Evidence: Map rows game-creator, threejs-game-skills and awesome-gamedev-agent-skills; matrix row "Web game frameworks" (Us P: the manual covers Phaser, Three.js and Babylon.js, and `libre-gamedev-hooks` already detects web game projects, but no plugin exists); X row threejs-game-skills
- Issue: none yet (promote after merge)
- Order: web-game-development, editor-mcp-guide, gltf-import-patterns, pong-example, roblox-development
- Tie: none

## Atoms

| Key | Title | State | Confidence | Class | Since | Queue # | Issue | Because |
|-----|-------|-------|------------|-------|-------|---------|-------|---------|
| editor-mcp-guide | Document pairing the engine plugins with an editor MCP server (`editor-mcp-guide`) | open | medium | repo | 2026-09-30 | 3 | - | - |
| gltf-import-patterns | Teach the asset-pipelines skill glTF import from Blender (`gltf-import-patterns`) | open | medium | repo | 2026-09-30 | 5 | - | - |
| pong-example | Add the Pong example the README describes (`pong-example`) | open | medium | repo | 2026-09-30 | 6 | - | - |
| roblox-development | Add a `roblox-development` plugin for Luau and Roblox Studio | open | medium | repo | 2026-09-30 | 4 | - | - |
| web-game-development | Add a `web-game-development` plugin for Phaser and Three.js | open | high | repo | 2026-09-30 | 1 | - | - |

## Retired

| Key | Title | State | Since | Issue | Because |
|-----|-------|-------|-------|-------|---------|
| derived-command-frontmatter | Add frontmatter to the 67 derived command files (`derived-command-frontmatter`) | parked | 2026-09-30 | - | bullet: Add frontmatter to the 67 derived command files (`derived-command-frontmatter`): parked, the same work is already open as good first issue #4 |

## Notes

- none
