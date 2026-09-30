# Competitor map: Claude Code Game Dev

## How this fills

1. Name the product and its surfaces (plugins, agents, skills, commands, install paths).
2. WebSearch / WebFetch public competitor docs, READMEs and homepages: other Claude Code plugin packs and marketplaces in this domain, Cursor rules and plugins, Codex or Gemini CLI extensions, and standalone tools people use for the same job.
3. One row per competitor; blank unknowns; cite a URL per row.
4. Fill the capabilities matrix (Y / N / P / ?) with the capabilities that matter in this domain, and a source per claimed cell.
5. Save as `YYYY-MM-DD-competitor-map.md` (keep this template).

## Product

- Name: Claude Code Game Dev ([HermeticOrmus/claude-code-game-development](https://github.com/HermeticOrmus/claude-code-game-development)), v2.0.0
- Flagship: the `claude-code-game-development` marketplace: 87 plugins, 22 of them for games (20 domain plugins with an agent, a command and a skill each, the `libre-gamedev-hooks` safety hooks, and `game-development` from wshobson/agents)
- Our surfaces: `/plugin marketplace add HermeticOrmus/claude-code-game-development`, then `/plugin install <plugin>@claude-code-game-development`; `setup.sh`; the 81-file manual in `docs/` (web games: canvas, Phaser, Three.js, Babylon.js, PixiJS); `tools/meta-prompting-framework/` (third party, credited in `NOTICE.md`); CI in `.github/workflows/validate.yml`

Star counts are `stargazers_count` from `https://api.github.com/repos/<owner>/<name>`, read on 2026-09-30.

## Map

| Competitor | What it is | Overlap with us | Watch / differentiator | Source URL |
|------------|------------|-----------------|------------------------|------------|
| Donchitos/Claude-Code-Game-Studios (25,572 stars, MIT) | "Turn a single Claude Code session into a full game development studio." 49 agents, 74 skills, 12 hooks, 39 document templates, used as a cloned `.claude/` template | Godot, Unity and Unreal agent sets; hooks; QA and netcode roles | A studio hierarchy (directors, leads, specialists) and design documents; no marketplace install, no CI workflows found | https://github.com/Donchitos/Claude-Code-Game-Studios |
| Unity-Technologies/unity-agent-plugin (375 stars) | Unity's official plugin for agent platforms; `claude plugin install unity@unity-agent-plugin`, also a Codex version | Unity coverage, marketplace install | First party; skills drive the open Unity Editor through the Unity CLI; the Unity blog says it is "listed among the Claude partner plugins" | https://github.com/Unity-Technologies/unity-agent-plugin, https://unity.com/blog/unity-plugin-for-claude-code |
| gamedev-skills/awesome-gamedev-agent-skills (1,255 stars, Apache-2.0) | "74 game-dev skills for your AI coding agent" with a router that picks skills by engine and task | Godot, Unity, Unreal; Claude Code install; CI validator | Covers Phaser, PixiJS, three.js, Bevy, pygame, LÖVE and Roblox, all engines we have no plugin for; installs into other agents too | https://github.com/gamedev-skills/awesome-gamedev-agent-skills |
| jame581/GodotPrompter (773 stars, MIT) | "Agentic skills framework for Godot 4.x", 56 skills, installable as a Claude Code marketplace | Godot coverage, multiplayer, localization, procgen | Deeper Godot depth than one plugin, a "Mentor mode" for teaching, installs into Copilot, Cursor and Codex as well | https://github.com/jame581/GodotPrompter |
| CoplayDev/unity-mcp (14,625 stars, MIT) | MCP server and Unity package: control the Unity Editor from any MCP client | Unity | Live editor control; v10 adds asset generation (models, images, Sketchfab import) | https://github.com/CoplayDev/unity-mcp, https://coplaydev.github.io/unity-mcp/migrations/v10 |
| hi-godot/godot-ai (2,712 stars, MIT) | MCP server and Godot addon that "connects Claude Code, Claude Desktop, Codex, Hermes Agent, and other MCP clients to a live Godot editor" | Godot | Live Godot editor control, CI with coverage | https://github.com/hi-godot/godot-ai |
| Coding-Solo/godot-mcp (5,893 stars, MIT) | "A Model Context Protocol (MCP) server for interacting with the Godot game engine." | Godot | Launches the editor, runs projects, captures debug output; no workflows directory found | https://github.com/Coding-Solo/godot-mcp |
| Unreal MCP in the Unreal Editor (Epic, UE 5.8) | First-party MCP that "embeds an MCP server inside the Unreal Editor process so that any MCP-compatible AI agent, such as Claude Code, Cursor, or the MCP Inspector, can drive the editor" | Unreal | Official, marked Experimental | https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor?lang=en-US |
| Roblox Studio MCP | "The Roblox Studio MCP server is built into Roblox Studio."; tools include `generate_mesh` | none (we have no Roblox plugin) | First party; quick connect for Claude Code, Codex CLI and Gemini CLI | https://create.roblox.com/docs/studio/mcp |
| ahujasid/mcp-for-blender, formerly blender-mcp (29,751 stars, MIT) | "Community plugin to control Blender 3D with any LLM of your choice" | Asset pipelines (Blender assets feed our engines) | 3D asset creation and import from asset libraries | https://github.com/ahujasid/mcp-for-blender |
| PlayableIntelligence/game-creator (335 stars) | "Opinionated Claude Plugin to make 2D (Phaser) & 3D (ThreeJS) Games" | Web games, Claude Code plugin install | A Phaser or Three.js game from idea to deployed browser game, with Playwright tests in its examples | https://github.com/PlayableIntelligence/game-creator |
| majidmanzarpour/threejs-game-skills (2,399 stars, MIT) | Codex and Claude Code skills "for building playable, polished Three.js browser games" | Web games | Three.js depth, optional AI-generated 3D, image and audio assets | https://github.com/majidmanzarpour/threejs-game-skills |
| wshobson/agents, `game-development` plugin (repo 40,112 stars, MIT) | Our upstream: agents `unity-developer` and `minecraft-bukkit-pro`, now with skills `godot-gdscript-patterns` and `unity-ecs-patterns` | Unity, Minecraft plugins | Upstream command files now carry frontmatter (for example `plugins/code-documentation/commands/code-explain.md` opens with `description:`); our derived copies do not | https://github.com/wshobson/agents/tree/main/plugins/game-development, https://github.com/wshobson/agents/blob/main/plugins/code-documentation/commands/code-explain.md |
| Unity's AI tools (formerly "Unity AI") | In-editor assistant, AI gateway and MCP server, in beta | Unity | Built into the editor, credit priced; the page says "We're retiring the "Unity AI" brand name." | https://unity.com/products/ai |
| Cursor rules for game engines | `awesome-cursorrules` (40,862 stars) has a Unity rule file and a GameMaker rule; `BlueBirdBack/godot-cursorrules` offers Godot 4.4 rules | Unity, Godot guidance | Single-file rules, no agents, commands or hooks | https://github.com/PatrickJS/awesome-cursorrules, https://github.com/BlueBirdBack/godot-cursorrules |

## Capabilities matrix

Mark Y / N / P (partial) / ? and cite. Rows are the capabilities that matter for this domain.

Columns: Us = this repo on `main`; CCGS = Claude-Code-Game-Studios; UnityPl = Unity's official plugin; AGAS = awesome-gamedev-agent-skills; GP = GodotPrompter; UMCP = CoplayDev/unity-mcp; GAI = godot-ai; GC = game-creator.

| Capability | Us | CCGS | UnityPl | AGAS | GP | UMCP | GAI | GC | Source notes |
|------------|----|------|---------|------|----|------|-----|----|--------------|
| Godot coverage | Y | Y | N | Y | Y | N | Y | N | Us: `plugins/godot-development/`. CCGS: README "Engine Specialists". AGAS: README engine list. GP and GAI: READMEs. |
| Unity coverage | Y | Y | Y | Y | N | Y | N | P | Us: `plugins/unity-development/`. UnityPl: repo README. UMCP: README. GC: a `unity-mcp` reference skill only. |
| Unreal coverage | Y | Y | N | Y | N | N | N | N | Us: `plugins/unreal-engine/`. CCGS: README engine agent sets. AGAS: README engine list. |
| Web game frameworks (Phaser, Three.js, Babylon.js) | P | P | N | Y | N | N | N | Y | Us: manual only (`docs/08-game-engines/phaser-integration.md`, `three-js-games.md`, `babylon-js-workflows.md`), no plugin; `libre-gamedev-hooks` already detects web game projects. CCGS: prototyper names Phaser as an alternative. AGAS: "Phaser, PixiJS, three.js". GC: README skills `phaser`, `threejs-game`. |
| Other engines (Bevy, Roblox, pygame, LÖVE, GameMaker) | N | N | N | Y | N | N | N | N | Us: no plugin. AGAS: README "Cross-engine" list. |
| Live editor control (MCP bridge to a running editor) | N | N | Y | N | N | Y | Y | P | Us: no MCP server in any plugin. UnityPl: README "Many skills drive your open Unity Editor directly". UMCP and GAI: READMEs. GC: Playwright screenshots of the browser game, not an editor. |
| Asset generation or asset tooling | P | P | P | P | P | Y | P | Y | Us: `asset-pipelines` (import settings, atlasing, LODs, CI asset validation), no generation. UMCP: v10 migration notes `asset_gen`. GC: README `game-assets`. CCGS: `/asset-spec`, `/asset-audit`. |
| Game design and production roles | P | Y | P | P | P | N | N | P | Us: `level-design`, `playtesting`, `monetization-ethics`; no producer or director roles. CCGS: README "Studio Hierarchy". |
| Multiplayer and netcode | Y | Y | Y | Y | Y | ? | ? | N | Us: `plugins/multiplayer-networking/`. UnityPl: `setup-multiplayer-services` skill. GP: `multiplayer-basics`, `multiplayer-sync`. |
| Installs as a Claude Code plugin from a marketplace | Y | N | Y | Y | Y | N | N | Y | Us: `.claude-plugin/marketplace.json`. CCGS: README "Clone or use as template". UnityPl: `claude plugin install unity@unity-agent-plugin`. GP: `claude plugins marketplace add`. |
| Works in other agents (Codex, Cursor, Copilot) | N | ? | Y | Y | Y | Y | Y | P | Us: Claude Code plugins only. UnityPl: https://unity.com/blog/unity-plugin-codex. GP: README Copilot and Cursor installs. GAI: README client list. |
| Safety guardrails (confirm before secrets or destructive commands) | Y | Y | ? | ? | ? | P | P | ? | Us: `plugins/libre-gamedev-hooks/` PreToolUse asks before `.env`, keys, keystores, `rm -rf`, force pushes. CCGS: README permission rules. UMCP: group-gated high-power tools. |
| Learning material (manual or tutorials) | Y | P | P | P | Y | P | P | ? | Us: 81 files in `docs/`. GP: README "Mentor mode". |
| Validated in CI | Y | P | Y | Y | Y | Y | Y | P | Us: `.github/workflows/validate.yml` validates and clean-installs all 87 plugins. CCGS: no workflows directory. AGAS: `ci.yml`. GAI: `ci.yml`. |
| Translations (non-English docs) | N | ? | ? | ? | ? | ? | ? | ? | Us: English only; a fork added a Japanese guide (see the people mine). Competitors not checked this run. |

## Search log

- WebSearch, 8 queries, all with results: `Claude Code plugin marketplace game development Godot Unity skills github`; `cursor.directory Unity C# cursor rules`; `awesome-cursorrules unity godot gdscript rules`; `Gemini CLI extension Godot OR Unity OR "Unreal Engine" game engine` (no dedicated Gemini CLI game-engine extension confirmed); `hi-godot godot-ai MCP Godot editor`; `Unreal Engine MCP server Claude Code 2026 github stars` (star counts from the summary were not used; stars come from the API); `Codex plugin OR skills Godot Unity game engine "codex" agents skills game development`; `Claude Code skills Phaser Three.js web game plugin`. After these the session's WebSearch budget ran out, so no further queries ran.
- GitHub API: repo metadata, READMEs, `.github/workflows` and `.claude-plugin` listings for every repo in the Map. `Common-ka/godot-cursor-rules` returned 404 and was dropped. `ahujasid/blender-mcp` redirects to `ahujasid/mcp-for-blender`; `OpusGameLabs/game-creator` redirects to `PlayableIntelligence/game-creator`.
- Pages fetched: https://unity.com/blog/unity-plugin-for-claude-code, https://unity.com/blog/unity-plugin-codex, https://docs.unity.com/en-us/ai/unity-plugin/claude-code, https://unity.com/products/ai, https://create.roblox.com/docs/studio/mcp, https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor?lang=en-US, https://coplaydev.github.io/unity-mcp/migrations/v10. `cursor.directory` answered HTTP 429 to both WebFetch and curl, so its rules are not in the Map.
- Found but not profiled (stars from the API): tjboudreaux/cc-plugin-unity-gamedev 9, IvanMurzak/Unity-MCP 4,368, Randroids-Dojo/Godot-Claude-Skills 45, alexmeckes/godot-claude-skills 37, haxqer/godot-skill 159, ChiR24/Unreal_mcp 899, flopperam/unreal-engine-mcp 1,088, chongdashu/unreal-mcp 2,088 (last push 2025-04-22).
- Our own column was read from this repo on `main`: `.claude-plugin/marketplace.json`, `plugins/`, `docs/`, `.github/workflows/validate.yml`, and `claude plugin validate` on every plugin (87 pass; 67 warnings, all "No frontmatter block found" on command files in 40 of the plugins derived from wshobson/agents).
