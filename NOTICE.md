# Notice

This repository combines original work with work derived from other MIT-licensed projects. This file says which is which, so the credit stays with the people who wrote it.

## Plugins derived from wshobson/agents

The following 66 plugins, and the marketplace entries that describe them, come from [wshobson/agents](https://github.com/wshobson/agents) by [Seth Hobson](https://github.com/wshobson), imported in commit `50bf83d` ("Add Claude Code plugins and agents from wshobson/agents"). Each keeps Seth Hobson as its author and the upstream repository as its homepage. They are used under the MIT License reproduced at the end of this file.

| Plugin | Version | Category |
|---|---|---|
| `code-documentation` | 1.2.0 | documentation |
| `debugging-toolkit` | 1.2.0 | development |
| `git-pr-workflows` | 1.2.1 | workflows |
| `backend-development` | 1.2.3 | development |
| `frontend-mobile-development` | 1.2.0 | development |
| `full-stack-orchestration` | 1.2.1 | workflows |
| `unit-testing` | 1.2.0 | testing |
| `tdd-workflows` | 1.2.1 | workflows |
| `code-review-ai` | 1.2.0 | quality |
| `code-refactoring` | 1.2.0 | utilities |
| `dependency-management` | 1.2.0 | utilities |
| `error-debugging` | 1.2.0 | utilities |
| `team-collaboration` | 1.2.0 | utilities |
| `llm-application-dev` | 1.2.1 | ai-ml |
| `agent-orchestration` | 1.2.0 | ai-ml |
| `context-management` | 1.2.0 | ai-ml |
| `machine-learning-ops` | 1.2.1 | ai-ml |
| `data-engineering` | 1.2.1 | data |
| `incident-response` | 1.2.1 | operations |
| `error-diagnostics` | 1.2.0 | operations |
| `distributed-debugging` | 1.2.0 | operations |
| `observability-monitoring` | 1.2.1 | operations |
| `deployment-strategies` | 1.2.0 | infrastructure |
| `deployment-validation` | 1.2.0 | infrastructure |
| `kubernetes-operations` | 1.2.1 | infrastructure |
| `cloud-infrastructure` | 1.2.1 | infrastructure |
| `cicd-automation` | 1.2.1 | infrastructure |
| `application-performance` | 1.2.1 | performance |
| `database-cloud-optimization` | 1.2.0 | performance |
| `comprehensive-review` | 1.2.1 | quality |
| `performance-testing-review` | 1.2.0 | quality |
| `framework-migration` | 1.2.2 | modernization |
| `codebase-cleanup` | 1.2.0 | modernization |
| `database-design` | 1.2.0 | database |
| `database-migrations` | 1.2.0 | database |
| `security-scanning` | 1.2.2 | security |
| `security-compliance` | 1.2.0 | security |
| `backend-api-security` | 1.2.0 | security |
| `frontend-mobile-security` | 1.2.0 | security |
| `data-validation-suite` | 1.2.0 | data |
| `api-scaffolding` | 1.2.1 | api |
| `api-testing-observability` | 1.2.0 | api |
| `seo-content-creation` | 1.2.0 | marketing |
| `seo-technical-optimization` | 1.2.0 | marketing |
| `seo-analysis-monitoring` | 1.2.0 | marketing |
| `documentation-generation` | 1.2.0 | documentation |
| `multi-platform-apps` | 1.2.1 | development |
| `business-analytics` | 1.2.0 | business |
| `hr-legal-compliance` | 1.2.0 | business |
| `customer-sales-automation` | 1.2.0 | business |
| `content-marketing` | 1.2.0 | marketing |
| `blockchain-web3` | 1.2.1 | blockchain |
| `quantitative-trading` | 1.2.0 | finance |
| `payment-processing` | 1.2.1 | payments |
| `game-development` | 1.2.0 | gaming |
| `accessibility-compliance` | 1.2.0 | accessibility |
| `python-development` | 1.2.1 | languages |
| `javascript-typescript` | 1.2.1 | languages |
| `systems-programming` | 1.2.0 | languages |
| `jvm-languages` | 1.2.0 | languages |
| `web-scripting` | 1.2.0 | languages |
| `functional-programming` | 1.2.0 | languages |
| `julia-development` | 1.0.0 | languages |
| `arm-cortex-microcontrollers` | 1.2.0 | languages |
| `shell-scripting` | 1.2.1 | languages |
| `developer-essentials` | 1.0.0 | development |

The same commit also brought these repository files from wshobson/agents: `.github/CODE_OF_CONDUCT.md`, `.github/CONTRIBUTING.md`, `.github/FUNDING.yml`, and the issue forms in `.github/ISSUE_TEMPLATE/` (`bug_report.yml`, `config.yml`, `feature_request.yml`, `moderation_report.yml`, `new_subagent.yml`).

### Changes made here to derived files

The agent, command, and skill files of the derived plugins are unchanged. The only changes are to manifests, so that every plugin validates and loads:

- Added `.claude-plugin/plugin.json` to 49 plugins that had none, copied from their marketplace entries, and set those entries to `strict: true`: `accessibility-compliance`, `agent-orchestration`, `api-testing-observability`, `application-performance`, `arm-cortex-microcontrollers`, `backend-api-security`, `business-analytics`, `code-documentation`, `code-refactoring`, `code-review-ai`, `codebase-cleanup`, `comprehensive-review`, `content-marketing`, `context-management`, `customer-sales-automation`, `data-engineering`, `data-validation-suite`, `database-cloud-optimization`, `database-migrations`, `debugging-toolkit`, `dependency-management`, `deployment-strategies`, `deployment-validation`, `distributed-debugging`, `documentation-generation`, `error-debugging`, `error-diagnostics`, `frontend-mobile-development`, `frontend-mobile-security`, `full-stack-orchestration`, `functional-programming`, `game-development`, `git-pr-workflows`, `hr-legal-compliance`, `incident-response`, `julia-development`, `jvm-languages`, `multi-platform-apps`, `performance-testing-review`, `quantitative-trading`, `security-compliance`, `seo-analysis-monitoring`, `seo-content-creation`, `seo-technical-optimization`, `systems-programming`, `tdd-workflows`, `team-collaboration`, `unit-testing`, `web-scripting`.
- `shell-scripting`: the marketplace entry's skill paths point at the skill directories instead of the `SKILL.md` files, which Claude Code rejects.
- Added `.claude-plugin/plugin.json` to the other 17 derived plugins, copied from their marketplace entries in the same way, and set those entries to `strict: true`, because Grok Build takes a plugin's name from its `plugin.json` and installed these under a hashed name: `api-scaffolding`, `backend-development`, `blockchain-web3`, `cicd-automation`, `cloud-infrastructure`, `database-design`, `developer-essentials`, `framework-migration`, `javascript-typescript`, `kubernetes-operations`, `llm-application-dev`, `machine-learning-ops`, `observability-monitoring`, `payment-processing`, `python-development`, `security-scanning`, `shell-scripting`.
- The marketplace itself is renamed from `claude-code-workflows` (the upstream name) to `claude-code-game-development`, with its own owner and description.
- `.github/ISSUE_TEMPLATE/config.yml`: the contact links point at this repository instead of the upstream one.

## Game plugins from LibreGameDev-Claude-Code

These 21 plugins come from [LibreGameDev-Claude-Code](https://github.com/HermeticOrmus/LibreGameDev-Claude-Code) (MIT, Copyright (c) 2025-2026 Hermetic Ormus, the same author as this repository), where they were written and first released:

`godot-development`, `unity-development`, `unreal-engine`, `game-architecture`, `input-systems`, `save-systems`, `localization`, `shader-programming`, `animation-systems`, `audio-systems`, `ui-game-design`, `ai-game-behavior`, `physics-simulation`, `procedural-generation`, `level-design`, `playtesting`, `performance-optimization`, `asset-pipelines`, `multiplayer-networking`, `monetization-ethics`, `libre-gamedev-hooks`.

## Other third-party content

- `tools/meta-prompting-framework/` comes from [manutej/meta-prompting-framework](https://github.com/manutej/meta-prompting-framework) and carries its own MIT license in `tools/meta-prompting-framework/LICENSE` (Copyright (c) 2025 Meta-Prompting Framework Contributors).

## Original to this repository

The `docs/` curriculum, `DOCUMENTATION_SUMMARY.md`, `tools/README.md`, the root `README.md`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md`, and the release tooling (`setup.sh`, `scripts/check.sh`, `.github/workflows/check.yml`, `.github/ISSUE_TEMPLATE/feedback.yml`) are covered by the repository [LICENSE](LICENSE).

## wshobson/agents license

```
MIT License

Copyright (c) 2024 Seth Hobson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
