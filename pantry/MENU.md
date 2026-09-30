# Menu: claude-code-game-development

Queue: 2026-09-30-pantry-queue.md
Counts: open 6, in flight 0, shipped 0, parked 0, dropped 0, needs fixing 0

## Steer

- none

## Up next

**derived-command-frontmatter**: Add frontmatter to the 67 derived command files (`derived-command-frontmatter`) (queue #2, high, repo, since 2026-09-30)

- Done when: For every plugin in `.claude-plugin/marketplace.json`, `claude plugin validate --strict plugins/<name>` exits 0 (40 plugins on `main` fail it on 67 "No frontmatter block found" warnings); 66 of the files take their frontmatter from the same path in wshobson/agents, and `plugins/code-review-ai/commands/ai-review.md`, which upstream no longer has, gets a written `description:`; `NOTICE.md` "Changes made here to derived files" names the upstream commit used; the CHANGELOG "Known warnings" note is updated
- Verify on: repo
- Evidence: Map row wshobson/agents (upstream command files now open with `description:` frontmatter; 66 of our 67 paths still exist upstream, all with frontmatter); matrix row "Validated in CI"
- Issue: none yet (promote after merge)
- Order: derived-command-frontmatter, web-game-development, editor-mcp-guide, gltf-import-patterns, pong-example, roblox-development
- Tie: derived-command-frontmatter over web-game-development, by key order (jev off)

## Atoms

| Key | Title | State | Confidence | Class | Since | Queue # | Issue | Because |
|-----|-------|-------|------------|-------|-------|---------|-------|---------|
| derived-command-frontmatter | Add frontmatter to the 67 derived command files (`derived-command-frontmatter`) | open | high | repo | 2026-09-30 | 2 | - | - |
| editor-mcp-guide | Document pairing the engine plugins with an editor MCP server (`editor-mcp-guide`) | open | medium | repo | 2026-09-30 | 3 | - | - |
| gltf-import-patterns | Teach the asset-pipelines skill glTF import from Blender (`gltf-import-patterns`) | open | medium | repo | 2026-09-30 | 5 | - | - |
| pong-example | Add the Pong example the README describes (`pong-example`) | open | medium | repo | 2026-09-30 | 6 | - | - |
| roblox-development | Add a `roblox-development` plugin for Luau and Roblox Studio | open | medium | repo | 2026-09-30 | 4 | - | - |
| web-game-development | Add a `web-game-development` plugin for Phaser and Three.js | open | high | repo | 2026-09-30 | 1 | - | - |

## Retired

| Key | Title | State | Since | Issue | Because |
|-----|-------|-------|-------|-------|---------|
| none | | | | | |

## Notes

- none
