<p align="center">
  <img src="https://ormus.solutions/mascot/pixellab_liquid_to_n64.gif" alt="Claude Code Game Dev" width="128" style="image-rendering: pixelated;" />
</p>

<h1 align="center">Claude Code Game Dev</h1>

<p align="center">
  <em>Game development for Claude Code — 87 installable plugins (22 for games), an 80-chapter game dev manual, and a meta-prompting toolkit</em>
</p>

<p align="center">
  <a href="https://github.com/HermeticOrmus/claude-code-game-development/stargazers"><img src="https://img.shields.io/github/stars/HermeticOrmus/claude-code-game-development?style=flat-square&color=aa8142" alt="Stars" /></a>
  <a href="https://github.com/HermeticOrmus/claude-code-game-development/blob/main/LICENSE"><img src="https://img.shields.io/github/license/HermeticOrmus/claude-code-game-development?style=flat-square&color=aa8142" alt="License" /></a>
  <a href="https://github.com/HermeticOrmus/claude-code-game-development/commits"><img src="https://img.shields.io/github/last-commit/HermeticOrmus/claude-code-game-development?style=flat-square&color=aa8142" alt="Last Commit" /></a>
  <img src="https://img.shields.io/badge/Python-aa8142?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Claude Code-aa8142?style=flat-square&logo=anthropic&logoColor=white" alt="Claude Code" />
</p>

> **v2.0.0:** the plugin marketplace is now named `claude-code-game-development` and ships 20 game plugins from [LibreGameDev](https://github.com/HermeticOrmus/LibreGameDev-Claude-Code) plus optional hooks: Godot, Unity, Unreal, rendering, AI, netcode, playtesting, shipping. Upgrading from 1.x? Read [Migrating from 1.x](#migrating-from-1x).

---
```
  ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗     ██████╗ ██████╗ ██████╗ ███████╗
 ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
 ██║     ██║     ███████║██║   ██║██║  ██║█████╗      ██║     ██║   ██║██║  ██║█████╗
 ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝      ██║     ██║   ██║██║  ██║██╔══╝
 ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗    ╚██████╗╚██████╔╝██████╔╝███████╗
  ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝

  ██████╗  █████╗ ███╗   ███╗███████╗    ██████╗ ███████╗██╗   ██╗
 ██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██╔══██╗██╔════╝██║   ██║
 ██║  ███╗███████║██╔████╔██║█████╗      ██║  ██║█████╗  ██║   ██║
 ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██║  ██║██╔══╝  ╚██╗ ██╔╝
 ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ██████╔╝███████╗ ╚████╔╝
  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝    ╚═════╝ ╚══════╝  ╚═══╝
```

### Build Complete Games Using AI-Assisted Development

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](#documentation)
[![Plugins](https://img.shields.io/badge/plugins-87-orange.svg)](#game-plugins)

---

## Table of Contents

- [Introduction](#introduction)
- [What You'll Learn](#what-youll-learn)
- [Quick Start](#quick-start)
- [Game Plugins](#game-plugins)
- [Migrating from 1.x](#migrating-from-1x)
- [Repository Structure](#repository-structure)
- [Example Games](#example-games)
- [Documentation](#documentation)
- [Learning Paths](#learning-paths)
- [Technology Stack](#technology-stack)
- [Feedback](#feedback)
- [Contribute](#contribute)
- [Contributing](#contributing)
- [Community](#community)
- [FAQ](#faq)
- [License](#license)

---

## Introduction

Welcome to the most comprehensive resource for learning game development with **Claude Code** - Anthropic's revolutionary AI-powered development tool that transforms how games are built. This repository represents the intersection of artificial intelligence and creative game development, empowering developers to build complete, production-quality games faster and more efficiently than ever before.

### What is Claude Code?

Claude Code is an AI-powered development assistant that understands context, generates high-quality code, and helps developers through every stage of the game development lifecycle - from initial concept to deployment. Unlike traditional coding, where you write every line manually, Claude Code allows you to direct AI to build game systems through natural language prompts, dramatically accelerating development while maintaining code quality and best practices.

### The Paradigm Shift

Traditional game development requires manually writing thousands of lines of code for even simple games. With Claude Code, the development process transforms:

**Traditional Approach:**
- Write boilerplate code manually
- Debug syntax errors for hours
- Research algorithms and implementations
- Build every system from scratch
- Time: Weeks to months for a complete game

**Claude Code Approach:**
- Describe what you want in natural language
- AI generates working code following best practices
- Iterate rapidly with refinement prompts
- Focus on creative direction and game design
- Time: Hours to days for a complete game

**Real-World Impact:**
- Build a polished platformer in **2 hours** instead of **2 weeks**
- Implement complex physics systems in **minutes** instead of **days**
- Create multiplayer networking in **1 hour** instead of **1 week**
- Iterate on game mechanics **10x faster**

### Why This Repository Exists

Despite Claude Code's power, game developers face a learning curve understanding how to effectively use AI assistance for game development workflows. This repository solves that problem by providing:

1. **Installable Claude Code Plugins**: 87 plugins, 22 of them for game development (Godot, Unity, Unreal, rendering, AI, netcode, playtesting, shipping)
2. **Comprehensive Documentation**: 180,000+ words across 80 chapters covering every aspect of game development with Claude Code
3. **Reusable Prompts**: exact Claude Code prompts throughout the docs, plus a meta-prompting framework in `tools/`
4. **Production Patterns**: Advanced architectures used in real games
5. **End-to-End Workflows**: From concept to deployment with AI assistance

### Who This Resource Is For

This repository is designed for:

- **Indie Game Developers** wanting to accelerate development and ship games faster
- **Hobbyist Programmers** learning game development with modern AI-assisted workflows
- **Game Development Students** exploring cutting-edge development methodologies
- **Professional Studios** evaluating AI-assisted development for production pipelines
- **Creative Technologists** building interactive experiences and prototypes
- **Anyone** curious about the future of game development

**Prerequisites:**
- Basic JavaScript/TypeScript knowledge (variables, functions, loops)
- Familiarity with HTML and CSS
- Understanding of basic programming concepts
- No prior game development experience required
- No prior Claude Code experience required

### Learning Philosophy

This repository follows a hands-on, example-driven approach:

1. **Learn by Building**: Every concept is taught through working code examples
2. **Progressive Complexity**: Start simple (Pong) and advance to complex (multiplayer games)
3. **Real-World Patterns**: All code follows production best practices
4. **Prompt Engineering Focus**: Learn to communicate effectively with AI
5. **Complete Workflows**: See entire development processes, not just code snippets
6. **Practical Application**: Every technique is immediately applicable to your projects

---

## What You'll Learn

By working through this repository, you'll master:

### Core Game Development

- Game loops, timing systems, and frame-rate independence
- Input handling for keyboard, mouse, touch, and gamepad
- 2D and 3D rendering with Canvas and WebGL
- Collision detection algorithms and spatial partitioning
- Physics simulation and integration
- Animation systems (sprite, skeletal, procedural)
- Camera systems for 2D and 3D games
- Audio systems with spatial sound and dynamic music
- UI/UX patterns for menus, HUDs, and game interfaces

### AI and Advanced Systems

- Pathfinding algorithms (A*, Dijkstra, navigation meshes)
- Behavior trees and finite state machines
- Procedural generation for levels, terrain, and content
- NPC behaviors and adaptive difficulty systems
- Dialogue and quest systems
- Inventory and crafting mechanics
- Skill trees and progression systems

### Networking and Multiplayer

- Real-time multiplayer with WebSockets
- Client-server architecture and authoritative servers
- State synchronization and network protocols
- Lag compensation, client prediction, and reconciliation
- Matchmaking systems
- Anti-cheat strategies

### Performance and Optimization

- Profiling and debugging game performance
- Rendering optimization (batching, culling, LOD)
- Memory management and garbage collection strategies
- Asset loading and streaming
- Web Worker parallelism
- Mobile optimization for battery and performance

### Production Workflows

- Entity Component System (ECS) architecture
- Design patterns for game development
- Testing strategies for game logic
- CI/CD pipelines for automated deployment
- Cross-platform deployment (web, mobile, desktop)
- Monetization strategies and analytics integration

### Claude Code Mastery

- Prompt engineering specifically for game development
- Iterative refinement techniques
- Debugging with AI assistance
- Code review and optimization with Claude Code
- Architecture design with AI collaboration
- Best practices for AI-assisted development

---

## Quick Start

### Install the plugins from Claude Code

```
/plugin marketplace add HermeticOrmus/claude-code-game-development
/plugin install godot-development@claude-code-game-development
```

Pick any other plugin by name from [Game Plugins](#game-plugins) and install it the same way. From a terminal:

```bash
claude plugin marketplace add HermeticOrmus/claude-code-game-development
claude plugin install godot-development@claude-code-game-development
```

Optional hooks (engine detection at session start, a confirmation prompt before touching secrets or signing keys): `/plugin install libre-gamedev-hooks@claude-code-game-development`.

From a checkout, `./setup.sh --only godot-development,multiplayer-networking` installs a chosen set, `./setup.sh --list` lists all 87, and `./setup.sh` with no flags installs every one. It needs the `claude` CLI and `jq`. Restart Claude Code after installing.

Used 1.x, when this marketplace was named `claude-code-workflows`? Read [Migrating from 1.x](#migrating-from-1x) first.

### Build your first game

Get your first game running in **10 minutes**:

### Step 1: Install Claude Code

If you haven't already, install Claude Code following the official documentation:

```bash
# Visit: https://docs.claude.com/claude-code
```

### Step 2: Clone This Repository

```bash
git clone https://github.com/HermeticOrmus/claude-code-game-development.git
cd claude-code-game-development
```

### Step 3: Build Your First Game

Follow [`docs/01-getting-started/first-game-in-10-minutes.md`](docs/01-getting-started/first-game-in-10-minutes.md). It builds Pong with Claude Code in a new, empty folder, starting from a single prompt, and runs in any modern browser.

**You should see**: A fully functional Pong game with AI opponent, score tracking, and smooth gameplay.

### Step 4: Understanding What You Built

The tutorial shows the exact Claude Code prompts. The development process looks like this:

**Initial Prompt:**
```
Create a complete Pong game using HTML5 Canvas with:
- Two paddles (player and AI)
- Ball physics with collision detection
- Score tracking
- Smooth 60 FPS gameplay
- Reset functionality
```

**Result:** A working Pong game generated in seconds

**Refinement Prompts:**
```
1. "Make the AI adjustable difficulty by adding random prediction errors"
2. "Add particle effects when the ball hits paddles"
3. "Implement sound effects using Web Audio API"
4. "Add a start screen and game over state"
```

**Total Development Time with Claude Code:** ~15 minutes
**Traditional Development Time:** ~4-6 hours

### Step 5: Build Your Own Game

Now try building your own variation:

1. Create a new directory for your game
2. Open Claude Code in it
3. Use this prompt:

```
Using the same structure as the Pong game (HTML5 Canvas and a game loop), create a [YOUR GAME IDEA] game with:
- [Feature 1]
- [Feature 2]
- [Feature 3]
```

### Common Pitfalls and Solutions

**Issue 1: Game runs too fast/slow**
- **Cause:** Not using delta time for frame-rate independence
- **Solution:** See `docs/02-core-game-concepts/game-loops-and-timing.md`
- **Claude Code Fix:** "Implement delta time in this game loop to make it frame-rate independent"

**Issue 2: Collisions not detecting properly**
- **Cause:** Using simple bounding box for complex shapes
- **Solution:** See `docs/02-core-game-concepts/collision-detection.md`
- **Claude Code Fix:** "Improve collision detection using circle-based collision for the ball"

**Issue 3: Performance issues with many objects**
- **Cause:** No spatial partitioning or culling
- **Solution:** See `docs/09-advanced-patterns/spatial-partitioning.md`
- **Claude Code Fix:** "Implement quadtree spatial partitioning to optimize collision checking"

### Next Steps

After your first game, explore:

1. **Simple Games**: Build Snake, Breakout, Tetris, Flappy Bird, or Asteroids next, from the specs in [Example Games](#example-games)
2. **Core Concepts** (`docs/02-core-game-concepts/`): Deep dive into game development fundamentals
3. **Prompt Engineering** (`docs/01-getting-started/prompt-engineering-for-games.md`): Learn advanced prompt engineering for games
4. **Game Plugins** ([Game Plugins](#game-plugins)): Install the engine and system plugins that fit your project, then tackle platformers, tower defense, roguelikes

---

## Game Plugins

22 of the 87 plugins are for game development. 21 come from [LibreGameDev](https://github.com/HermeticOrmus/LibreGameDev-Claude-Code) and ship here at 2.0.0: 20 domain plugins, each with an agent, a slash command with focused actions, and a skill, plus an optional hooks plugin. The 22nd, `game-development`, comes from wshobson/agents. Install any of them with `/plugin install <plugin>@claude-code-game-development`.

### Engines

| Plugin | Agent | Command | Skill | What it covers |
|---|---|---|---|---|
| **godot-development** | `godot-engineer` | `/godot` | `godot-development` | Node tree and scene design, signals, resources, physics, animation, typed GDScript or C#, GDExtension, and GUT tests. |
| **unity-development** | `unity-engineer` | `/unity` | `unity-development` | MonoBehaviour or DOTS architecture, URP and HDRP, Addressables, the Input System, ScriptableObjects, and idiomatic C#. |
| **unreal-engine** | `unreal-developer` | `/unreal` | `unreal-patterns` | Gameplay Framework, Blueprint or C++, the Gameplay Ability System, Enhanced Input, replication, and Lumen and Nanite. |

### Core systems

| Plugin | Agent | Command | Skill | What it covers |
|---|---|---|---|---|
| **game-architecture** | `game-architect` | `/game-arch` | `game-arch-patterns` | Game loops, ECS, event buses, data resources, service locators, scene management, and state stacks. |
| **input-systems** | `input-engineer` | `/input-system` | `input-patterns` | Action maps, gamepad deadzones, input buffering, rebinding, touch controls, and rumble across Godot, Unity, and Unreal. |
| **save-systems** | `save-system-engineer` | `/save-system` | `save-system-patterns` | Serialization, save file versioning and migration, atomic writes, slots, settings persistence, and platform cloud saves. |
| **localization** | `localization-engineer` | `/localize` | `localization-patterns` | String extraction, gettext PO files, ICU plurals, right-to-left layout, CJK font fallback, and pseudo-localization. |

### Rendering + audio

| Plugin | Agent | Command | Skill | What it covers |
|---|---|---|---|---|
| **shader-programming** | `shader-programmer` | `/shader` | `shader-patterns` | Godot shading language, vertex and fragment stages, common effects, post-processing, and shader performance. |
| **animation-systems** | `animation-engineer` | `/animate` | `animation-patterns` | Blend trees, state machines, IK, root motion, and animation events across Godot AnimationTree, Unity Animator, and Unreal AnimGraph. |
| **audio-systems** | `game-audio-engineer` | `/game-audio` | `audio-patterns` | Bus architecture, spatial audio, dynamic music, sound pooling, and FMOD or Wwise integration. |
| **ui-game-design** | `game-ui-designer` | `/game-ui` | `game-ui-patterns` | HUDs, menu stacks, inventory grids, dialogue boxes, settings screens, and accessibility with Godot Control nodes. |

### Gameplay

| Plugin | Agent | Command | Skill | What it covers |
|---|---|---|---|---|
| **ai-game-behavior** | `game-ai-engineer` | `/game-ai` | `game-ai-patterns` | Behavior trees, state machines, utility AI, GOAP, navmesh pathfinding, and perception systems. |
| **physics-simulation** | `physics-engineer` | `/physics` | `physics-patterns` | Body types, collision layers, character controllers, raycasts, triggers, joints, and physics performance in Godot and Unity. |
| **procedural-generation** | `procgen-engineer` | `/procgen` | `procgen-patterns` | Noise terrain, BSP and cellular automata dungeons, Wave Function Collapse, seeded randomness, and solvability checks. |
| **level-design** | `level-designer` | `/level-design` | `level-design-patterns` | Greyboxing, TileMaps, modular kits, navmesh baking, level streaming, and environmental storytelling. |

### Quality + ops

| Plugin | Agent | Command | Skill | What it covers |
|---|---|---|---|---|
| **playtesting** | `playtest-coordinator` | `/playtest` | `playtest-patterns` | Session design, observation protocols, telemetry schemas, death heatmaps, funnels, and A/B tests. |
| **performance-optimization** | `game-perf-engineer` | `/game-perf` | `game-perf-patterns` | Profiling methodology, draw call batching, LODs, occlusion culling, object pooling, and GDScript hot path fixes. |
| **asset-pipelines** | `asset-pipeline-engineer` | `/assets` | `asset-pipeline-patterns` | Import settings, texture atlasing, LOD generation, audio compression, and CI asset validation for Godot and Unity. |
| **multiplayer-networking** | `network-engineer` | `/multiplayer` | `multiplayer-networking` | Rollback, lockstep, client prediction with reconciliation, lag compensation, bandwidth budgets, NAT traversal, and Godot or Unity networking. |
| **monetization-ethics** | `monetization-advisor` | `/monetize` | `ethical-monetization-patterns` | Dark pattern audits, cosmetics-only stores, fair battle passes, platform IAP flows, and player spending protection. |

### Hooks

| Plugin | Events | What it does |
|---|---|---|
| **libre-gamedev-hooks** | `SessionStart`, `PreToolUse`, `PostToolUse` | Prints one line of context when the project is Godot, Unity, Unreal, or a web game; asks before a tool touches `.env` files, keys, Android keystores, or Godot export credentials, and before `rm -rf` or force pushes; flags empty writes and reminds once per session to run the tests. See [its README](plugins/libre-gamedev-hooks/README.md). |

### From wshobson/agents

| Plugin | Agents | What it covers |
|---|---|---|
| **game-development** | `unity-developer`, `minecraft-bukkit-pro` | Unity game development with C# scripting, Minecraft server plugin development with Bukkit/Spigot APIs |

`game-development` and `unity-development` are different plugins: `game-development` carries a general Unity C# agent and a Minecraft Bukkit/Spigot plugin agent, while `unity-development` is the Unity 6 architecture plugin with its own agent, command, and skill.

The skills cross-reference the [reference manual](docs/), which lives in this repo.

### The other 65 plugins

The rest of the catalog covers general software work (backend, frontend, testing, security, infrastructure, data, languages, and more). These plugins come from [wshobson/agents](https://github.com/wshobson/agents) by Seth Hobson and are unchanged apart from their manifests; see [NOTICE.md](NOTICE.md).

<details>
<summary>All 65, by category</summary>

| Plugin | Category | Agents | Commands | Skills | Description |
|---|---|---|---|---|---|
| `accessibility-compliance` | accessibility | 1 | 1 | 0 | WCAG accessibility auditing, compliance validation, UI testing for screen readers, keyboard navigation, and inclusive design |
| `agent-orchestration` | ai-ml | 1 | 2 | 0 | Multi-agent system optimization, agent improvement workflows, and context management |
| `context-management` | ai-ml | 1 | 2 | 0 | Context persistence, restoration, and long-running conversation management |
| `llm-application-dev` | ai-ml | 2 | 3 | 4 | LLM application development, prompt engineering, and AI assistant optimization |
| `machine-learning-ops` | ai-ml | 3 | 1 | 1 | ML model training pipelines, hyperparameter tuning, model deployment automation, experiment tracking, and MLOps workflows |
| `api-scaffolding` | api | 4 | 0 | 1 | REST and GraphQL API scaffolding, framework selection, backend architecture, and API generation |
| `api-testing-observability` | api | 1 | 1 | 0 | API testing automation, request mocking, OpenAPI documentation generation, observability setup, and monitoring |
| `blockchain-web3` | blockchain | 1 | 0 | 4 | Smart contract development with Solidity, DeFi protocol implementation, NFT platforms, and Web3 application architecture |
| `business-analytics` | business | 1 | 0 | 0 | Business metrics analysis, KPI tracking, financial reporting, and data-driven decision making |
| `customer-sales-automation` | business | 2 | 0 | 0 | Customer support workflow automation, sales pipeline management, email campaigns, and CRM integration |
| `hr-legal-compliance` | business | 2 | 0 | 0 | HR policy documentation, legal compliance templates (GDPR/SOC2/HIPAA), employment contracts, and regulatory documentation |
| `data-engineering` | data | 2 | 2 | 0 | ETL pipeline construction, data warehouse design, batch processing workflows, and data-driven feature development |
| `data-validation-suite` | data | 1 | 0 | 0 | Schema validation, data quality monitoring, streaming validation pipelines, and input validation for backend APIs |
| `database-design` | database | 2 | 0 | 1 | Database architecture, schema design, and SQL optimization for production systems |
| `database-migrations` | database | 2 | 2 | 0 | Database migration automation, observability, and cross-database migration strategies |
| `backend-development` | development | 4 | 1 | 5 | Backend API design, GraphQL architecture, workflow orchestration with Temporal, and test-driven backend development |
| `debugging-toolkit` | development | 2 | 1 | 0 | Interactive debugging, developer experience optimization, and smart debugging workflows |
| `developer-essentials` | development | 0 | 0 | 8 | Essential developer skills including Git workflows, SQL optimization, error handling, code review, E2E testing, authentication, debugging, and monorepo management |
| `frontend-mobile-development` | development | 2 | 1 | 0 | Frontend UI development and mobile application implementation across platforms |
| `multi-platform-apps` | development | 6 | 1 | 0 | Cross-platform application development coordinating web, iOS, Android, and desktop implementations |
| `code-documentation` | documentation | 3 | 2 | 0 | Documentation generation, code explanation, and technical writing with automated doc generation and tutorial creation |
| `documentation-generation` | documentation | 5 | 1 | 0 | OpenAPI specification generation, Mermaid diagram creation, tutorial writing, API reference documentation |
| `quantitative-trading` | finance | 2 | 0 | 0 | Quantitative analysis, algorithmic trading strategies, financial modeling, portfolio risk management, and backtesting |
| `cicd-automation` | infrastructure | 5 | 1 | 4 | CI/CD pipeline configuration, GitHub Actions/GitLab CI workflow setup, and automated deployment pipeline orchestration |
| `cloud-infrastructure` | infrastructure | 6 | 0 | 4 | Cloud architecture design for AWS/Azure/GCP, Kubernetes cluster configuration, Terraform infrastructure-as-code, hybrid cloud networking, and multi-cloud cost optimization |
| `deployment-strategies` | infrastructure | 2 | 0 | 0 | Deployment patterns, rollback automation, and infrastructure templates |
| `deployment-validation` | infrastructure | 1 | 1 | 0 | Pre-deployment checks, configuration validation, and deployment readiness assessment |
| `kubernetes-operations` | infrastructure | 1 | 0 | 4 | Kubernetes manifest generation, networking configuration, security policies, observability setup, GitOps workflows, and auto-scaling |
| `arm-cortex-microcontrollers` | languages | 1 | 0 | 0 | ARM Cortex-M firmware development for Teensy, STM32, nRF52, and SAMD with peripheral drivers and memory safety patterns |
| `functional-programming` | languages | 1 | 0 | 0 | Functional programming with Elixir, OTP patterns, Phoenix framework, and distributed systems |
| `javascript-typescript` | languages | 2 | 1 | 4 | JavaScript and TypeScript development with ES6+, Node.js, React, and modern web frameworks |
| `julia-development` | languages | 1 | 0 | 0 | Modern Julia development with Julia 1.10+, package management, scientific computing, high-performance numerical code, and production best practices |
| `jvm-languages` | languages | 3 | 0 | 0 | JVM language development including Java, Scala, and C# with enterprise patterns and frameworks |
| `python-development` | languages | 3 | 1 | 5 | Modern Python development with Python 3.12+, Django, FastAPI, async patterns, and production best practices |
| `shell-scripting` | languages | 2 | 0 | 3 | Production-grade Bash scripting with defensive programming, POSIX compliance, and comprehensive testing |
| `systems-programming` | languages | 4 | 1 | 0 | Systems programming with Rust, Go, C, and C++ for performance-critical and low-level development |
| `web-scripting` | languages | 2 | 0 | 0 | Web scripting with PHP and Ruby for web applications, CMS development, and backend services |
| `content-marketing` | marketing | 2 | 0 | 0 | Content marketing strategy, web research, and information synthesis for marketing operations |
| `seo-analysis-monitoring` | marketing | 3 | 0 | 0 | Content freshness analysis, cannibalization detection, and authority building for SEO |
| `seo-content-creation` | marketing | 3 | 0 | 0 | SEO content writing, planning, and quality auditing with E-E-A-T optimization |
| `seo-technical-optimization` | marketing | 4 | 0 | 0 | Technical SEO optimization including meta tags, keywords, structure, and featured snippets |
| `codebase-cleanup` | modernization | 2 | 3 | 0 | Technical debt reduction, dependency updates, and code refactoring automation |
| `framework-migration` | modernization | 2 | 3 | 4 | Framework updates, migration planning, and architectural transformation workflows |
| `distributed-debugging` | operations | 2 | 1 | 0 | Distributed system tracing and debugging across microservices |
| `error-diagnostics` | operations | 2 | 3 | 0 | Error tracing, root cause analysis, and smart debugging for production systems |
| `incident-response` | operations | 2 | 2 | 0 | Production incident management, triage workflows, and automated incident resolution |
| `observability-monitoring` | operations | 4 | 2 | 4 | Metrics collection, logging infrastructure, distributed tracing, SLO implementation, and monitoring dashboards |
| `payment-processing` | payments | 1 | 0 | 4 | Payment gateway integration with Stripe, PayPal, checkout flow implementation, subscription billing, and PCI compliance |
| `application-performance` | performance | 3 | 1 | 0 | Application profiling, performance optimization, and observability for frontend and backend systems |
| `database-cloud-optimization` | performance | 4 | 1 | 0 | Database query optimization, cloud cost optimization, and scalability improvements |
| `code-review-ai` | quality | 1 | 1 | 0 | AI-powered architectural review and code quality analysis |
| `comprehensive-review` | quality | 3 | 2 | 0 | Multi-perspective code analysis covering architecture, security, and best practices |
| `performance-testing-review` | quality | 2 | 2 | 0 | Performance analysis, test coverage review, and AI-powered code quality assessment |
| `backend-api-security` | security | 2 | 0 | 0 | API security hardening, authentication implementation, authorization patterns, rate limiting, and input validation |
| `frontend-mobile-security` | security | 3 | 1 | 0 | XSS prevention, CSRF protection, content security policies, mobile app security, and secure storage patterns |
| `security-compliance` | security | 1 | 1 | 0 | SOC2, HIPAA, and GDPR compliance validation, secrets scanning, compliance checklists, and regulatory documentation |
| `security-scanning` | security | 1 | 3 | 1 | SAST analysis, dependency vulnerability scanning, OWASP Top 10 compliance, container security scanning, and automated security hardening |
| `unit-testing` | testing | 2 | 1 | 0 | Unit and integration test automation for Python and JavaScript with debugging support |
| `code-refactoring` | utilities | 2 | 3 | 0 | Code cleanup, refactoring automation, and technical debt management with context restoration |
| `dependency-management` | utilities | 1 | 1 | 0 | Dependency auditing, version management, and security vulnerability scanning |
| `error-debugging` | utilities | 2 | 3 | 0 | Error analysis, trace debugging, and multi-agent problem diagnosis |
| `team-collaboration` | utilities | 1 | 2 | 0 | Team workflows, issue management, standup automation, and developer experience optimization |
| `full-stack-orchestration` | workflows | 4 | 1 | 0 | End-to-end feature orchestration with testing, security, performance, and deployment |
| `git-pr-workflows` | workflows | 1 | 3 | 0 | Git workflow automation, pull request enhancement, and team onboarding processes |
| `tdd-workflows` | workflows | 2 | 4 | 0 | Test-driven development methodology with red-green-refactor cycles and code review |

</details>

Across all 87 plugins: 168 agents, 90 commands, 81 skills, and 3 hooks. Some wshobson/agents agents appear in more than one plugin, so the agent count includes those copies.

---

## Migrating from 1.x

In 1.x this marketplace was named `claude-code-workflows`, the same name that [wshobson/agents](https://github.com/wshobson/agents) uses. Claude Code keeps one marketplace per name, so only one of the two could be added: adding the second from GitHub fails with "its network source differs from the one declared for it". v2.0.0 renames this one to `claude-code-game-development`, so both can be installed side by side.

1. Check which repo `claude-code-workflows` points to:

   ```
   /plugin marketplace list
   ```

   or `claude plugin marketplace list` in a terminal. Read the `Source:` line under `claude-code-workflows`.

2. **Only if** it says `GitHub (HermeticOrmus/claude-code-game-development)` (or a local checkout of this repo), remove it from a terminal:

   ```bash
   claude plugin marketplace remove claude-code-workflows
   ```

   This also uninstalls the plugins you installed from it. If it says `GitHub (wshobson/agents)`, leave it alone: that is Seth Hobson's marketplace, and removing it would remove his plugins.

3. Add this repo under its new name and reinstall what you use:

   ```
   /plugin marketplace add HermeticOrmus/claude-code-game-development
   /plugin install <plugin>@claude-code-game-development
   ```

The 66 plugins that came from wshobson/agents keep their names and versions here, so the ones you used before are still available.

---

## Repository Structure

This repository is organized for progressive learning and easy reference:

### `/plugins` and `/.claude-plugin` - Claude Code Plugins

`.claude-plugin/marketplace.json` makes the repo the `claude-code-game-development` plugin marketplace. `plugins/` holds the 87 plugins it lists: the 21 game plugins from LibreGameDev and the 66 plugins from wshobson/agents. See [Game Plugins](#game-plugins). `setup.sh` installs them from a checkout.

### `/docs` - Comprehensive Documentation (180,000+ words)

Thirteen major sections covering every aspect of game development with Claude Code:

#### 01. Getting Started (17,000+ words)
Your introduction to Claude Code for game development. Covers installation, setup, fundamental concepts, prompt engineering basics, and troubleshooting. Perfect starting point for beginners.

**Key Files:**
- `installation-setup.md` - Platform-specific setup guides
- `first-game-in-10-minutes.md` - Complete tutorial building Pong
- `claude-code-fundamentals.md` - Core concepts and workflow
- `prompt-engineering-for-games.md` - Game-specific prompting strategies
- `troubleshooting-common-issues.md` - Solutions to frequent problems

#### 02. Core Game Concepts (28,000+ words)
Essential game development knowledge with Claude Code implementations. Master game loops, state management, input handling, collision detection, physics, animation, and camera systems.

**Key Files:**
- `game-loops-and-timing.md` - Frame-rate independence and timing
- `state-management.md` - Managing game state effectively
- `collision-detection.md` - Various collision algorithms with examples
- `physics-integration.md` - 2D/3D physics systems
- `animation-systems.md` - Sprite, skeletal, and procedural animation

#### 03. Graphics and Rendering (21,000+ words)
Deep dive into 2D and 3D rendering. Learn Canvas 2D, WebGL, shader programming, particle systems, sprite management, lighting, and post-processing effects.

**Key Files:**
- `canvas-2d-rendering.md` - HTML5 Canvas techniques
- `webgl-basics.md` - 3D rendering fundamentals
- `shader-programming.md` - GLSL with AI assistance
- `particle-systems.md` - Visual effects and optimization
- `lighting-shadows.md` - Lighting systems for games

#### 04. Game AI (25,000+ words)
Implement intelligent game behaviors. Covers pathfinding, behavior trees, finite state machines, procedural generation, NPC behaviors, and adaptive difficulty.

**Key Files:**
- `pathfinding-algorithms.md` - A*, Dijkstra, nav meshes
- `behavior-trees.md` - AI decision making
- `procedural-generation.md` - Generating levels and content
- `npc-behaviors.md` - Realistic character AI

#### 05. Audio Systems (12,000+ words)
Complete audio implementation guide. Web Audio API, spatial audio, dynamic music systems, sound effect management, and performance optimization.

#### 06. Networking and Multiplayer (12,000+ words)
Build real-time multiplayer games. WebSocket implementation, client-server architecture, state synchronization, lag compensation, matchmaking, and anti-cheat strategies.

**Key Files:**
- `websocket-implementation.md` - Real-time networking
- `state-synchronization.md` - Network state management
- `lag-compensation.md` - Client prediction and reconciliation

#### 07. UI/UX (5,000+ words)
Create polished game interfaces. Menu systems, HUD design, dialogue systems, inventory interfaces, and accessibility considerations.

#### 08. Game Engines (15,000+ words)
Integrate Claude Code with popular game engines. Phaser, Babylon.js, Three.js, PixiJS workflows, and custom engine development.

#### 09. Advanced Patterns (13,000+ words)
Production-quality architectures. Entity Component Systems, dependency injection, event-driven architecture, object pooling, spatial partitioning, and save/load systems.

#### 10. Performance Optimization (6,000+ words)
Make your games run fast. Profiling, rendering optimization, memory management, asset loading strategies, Web Worker parallelism, and mobile optimization.

#### 11. Testing and QA (11,000+ words)
Ensure game quality. Unit testing game logic, integration testing, automated playtesting, and CI/CD pipelines.

#### 12. Deployment and Distribution (10,000+ words)
Ship your games. Web hosting, mobile packaging (PWA, Cordova, Capacitor), desktop deployment (Electron, Tauri), monetization strategies, and analytics.

#### 13. Case Studies (1,000+ words)
Real-world development stories. The section README outlines four case studies (platformer, puzzle, multiplayer shooter, procedural RPG) from concept to deployment; the full write-ups are not in the repository yet.

### Described here, not in the repository yet

The README has described the directories below since the first release, but they have not been added: there is no `examples/`, `templates/`, `prompts/`, `resources/`, or `community/` directory, and `tools/` holds the meta-prompting framework rather than the JavaScript utilities listed. They stay here as the plan, and each is a good first contribution (see [Contributing](#contributing)). What ships today is `plugins/`, `docs/`, and `tools/meta-prompting-framework/`.

### `/examples` - 10+ Complete Working Games (not added yet)

#### Simple Games (`01-simple-games/`)
Six complete games perfect for learning fundamentals:
- **Pong**: AI opponent, physics, scoring
- **Snake**: Grid-based movement, collision, growth mechanics
- **Breakout**: Brick destruction, power-ups, level progression
- **Tetris**: Piece rotation, line clearing, scoring
- **Flappy Bird**: Infinite scrolling, procedural obstacles
- **Asteroids**: Vector graphics, space physics, shooting

Each includes:
- Complete, working source code (300-500 lines)
- Detailed README with architecture explanation
- PROMPTS.md with exact Claude Code prompts used
- Line-by-line code comments
- Playable in browser

#### Intermediate Games (`02-intermediate-games/`)
Five more complex games demonstrating advanced concepts:
- **Platformer Adventure**: Multi-level, enemies, power-ups, save system
- **Tower Defense**: Pathfinding, wave management, upgrade systems
- **Puzzle Match-3**: Grid matching, combos, special pieces
- **Endless Runner**: Procedural generation, increasing difficulty
- **Roguelike Dungeon**: Procedural levels, permadeath, item systems

Each includes:
- Modular architecture (500-1500 lines across multiple files)
- Complete documentation
- Development workflow logs
- Asset management examples

#### Advanced Games (`03-advanced-games/`)
Production-quality examples:
- **Multiplayer Shooter**: Complete client-server architecture, real-time networking, lag compensation
- **Procedural RPG**: World generation, quest systems, character progression
- **Real-Time Strategy**: Unit management, fog of war, resource gathering
- **Physics Sandbox**: Advanced physics, user creation tools

Each includes:
- Professional architecture patterns
- Comprehensive documentation (5000+ words)
- Deployment guides
- Performance optimization examples

#### Game Components (`04-game-components/`)
Reusable systems you can integrate into your games:
- Animation system
- Dialogue engine
- Inventory manager
- Quest system
- Crafting system
- Skill tree system

### `/templates` - Project Templates (not added yet)

Five ready-to-use templates:
- **basic-game-template**: Minimal structure for quick prototypes
- **phaser-starter**: Phaser 3 project configured for Claude Code
- **babylon-starter**: Babylon.js 3D game template
- **three-js-starter**: Three.js custom engine template
- **multiplayer-starter**: Client-server multiplayer foundation

Each template includes:
- Complete project structure
- Build configuration (webpack/Vite)
- README with Claude Code usage guide
- Example game demonstrating the template

### `/prompts` - Prompt Engineering Library (not added yet)

**100+ tested prompts** organized by category:

- **game-initialization-prompts.md**: Project setup and configuration (30+ prompts)
- **feature-development-prompts.md**: Building game systems (40+ prompts)
- **debugging-prompts.md**: Finding and fixing bugs (15+ prompts)
- **optimization-prompts.md**: Performance improvements (15+ prompts)
- **refactoring-prompts.md**: Code improvement patterns (10+ prompts)
- **prompt-templates/**: Reusable prompt patterns for common tasks

Each prompt includes:
- The exact prompt text
- Expected output and quality assessment
- Common issues and refinements
- Variations for different scenarios
- Results analysis

### `/tools` - Development Utilities

What is in `tools/` today: the [meta-prompting framework](tools/README.md) (`tools/meta-prompting-framework/`), a recursive prompt improvement system that calls the Claude API. It comes from [manutej/meta-prompting-framework](https://github.com/manutej/meta-prompting-framework) and carries its own MIT license.

Planned helper tools for game development with Claude Code (not added yet):
- **game-project-analyzer.js**: Analyze your game's structure and complexity
- **asset-optimizer.js**: Optimize images, audio, and other assets
- **performance-monitor.js**: Real-time performance overlay
- **debug-overlay.js**: Visual debugging tools
- **build-scripts/**: Automated build and deployment scripts

### `/resources` - Reference Materials (not added yet)

- **cheat-sheets/**: Quick reference for Claude Code commands and patterns
- **reference/**: Math, physics, algorithms for game development
- **learning-paths/**: Structured 30/60/90-day curricula

### `/community` - Community Resources (not added yet)

- **showcase/**: Template for sharing your projects
- **discussions/**: Common questions and answers
- **contributions/**: Guide for contributing to this repository

---

## Example Games

Explore 10+ complete, working games ranging from simple classics to complex multiplayer experiences:

> **Not in the repository yet.** The games below are specs: each one lists what to build and which techniques it teaches, and the `Try It` paths show where each game will live once it is added. You can build any of them today with Claude Code, the docs, and the game plugins. Pong is the exception: [`docs/01-getting-started/first-game-in-10-minutes.md`](docs/01-getting-started/first-game-in-10-minutes.md) builds it step by step.

### Simple Games - Perfect for Learning

#### Pong
**Complexity**: Beginner | **Time to Build**: 15-30 min with Claude Code | **Lines of Code**: ~350

Classic arcade game demonstrating core concepts:
- Game loop and timing
- Collision detection
- AI opponent with adjustable difficulty
- Score tracking and game states
- Canvas 2D rendering

**What You'll Learn**: Basic game structure, physics, AI fundamentals

**Try It**: `examples/01-simple-games/pong/index.html`

**Claude Code Highlights**:
- Generated complete game with one initial prompt
- Refined AI difficulty with follow-up prompt
- Added particle effects in 30 seconds

---

#### Snake
**Complexity**: Beginner | **Time to Build**: 20-40 min | **Lines of Code**: ~400

Grid-based classic teaching:
- Grid movement and collision
- Array-based snake body management
- Food spawning and growth mechanics
- Score and high-score persistence
- Responsive keyboard controls

**What You'll Learn**: Grid-based games, data structures, local storage

**Try It**: `examples/01-simple-games/snake/index.html`

---

#### Breakout
**Complexity**: Beginner+ | **Time to Build**: 30-60 min | **Lines of Code**: ~500

Brick-breaker game demonstrating:
- Paddle and ball physics
- Brick destruction with grid layout
- Power-ups (multi-ball, paddle size, etc.)
- Level progression
- Particle effects

**What You'll Learn**: Physics refinement, grid systems, power-up architecture

**Try It**: `examples/01-simple-games/breakout/index.html`

---

#### Tetris
**Complexity**: Intermediate | **Time to Build**: 1-2 hours | **Lines of Code**: ~600

Puzzle classic teaching:
- Piece rotation and collision
- Grid-based placement
- Line clearing algorithm
- Score calculation and levels
- Next piece preview

**What You'll Learn**: Complex state management, algorithms, game feel

**Try It**: `examples/01-simple-games/tetris/index.html`

---

### Intermediate Games - Advanced Concepts

#### Platformer Adventure
**Complexity**: Intermediate | **Time to Build**: 4-8 hours | **Lines of Code**: ~1500

Complete platformer with:
- Physics-based player movement (jump, double-jump, wall-slide)
- Multiple enemy types with AI
- Collectibles and power-ups
- Multi-level progression
- Save/load system
- Boss fights

**What You'll Learn**: Advanced physics, enemy AI, level design, game progression

**Architecture Highlights**:
- Modular ECS-inspired architecture
- Tilemap system for levels
- State machine for player states
- Event system for game events

**Try It**: `examples/02-intermediate-games/platformer-adventure/index.html`

---

#### Tower Defense
**Complexity**: Intermediate | **Time to Build**: 6-10 hours | **Lines of Code**: ~2000

Strategic game featuring:
- A* pathfinding for enemies
- Tower placement and upgrades
- Wave management system
- Resource economy
- Multiple tower and enemy types
- Visual effects and animations

**What You'll Learn**: Pathfinding algorithms, strategic AI, economy systems

**Try It**: `examples/02-intermediate-games/tower-defense/index.html`

---

### Advanced Games - Production Quality

#### Multiplayer Shooter
**Complexity**: Advanced | **Time to Build**: 20-40 hours | **Lines of Code**: ~5000+

Complete multiplayer game with:
- Real-time WebSocket networking
- Authoritative server architecture
- Client prediction and reconciliation
- Lag compensation techniques
- Matchmaking system
- Anti-cheat measures
- Spectator mode
- Voice chat integration (optional)

**What You'll Learn**: Network programming, client-server architecture, multiplayer optimization

**Architecture**:
- Separate client and server codebases
- Shared code for validation
- Message protocol design
- State synchronization strategies

**Deployment**: Includes complete deployment guide for Digital Ocean, AWS, or Heroku

**Try It**: `examples/03-advanced-games/multiplayer-shooter/` (requires server setup)

**Read More**: See `docs/13-case-studies/multiplayer-shooter-analysis.md` for complete development story

---

## Documentation

The documentation is organized into 13 comprehensive sections with 180,000+ words across 80 files, covering every aspect of game development with Claude Code. Each document includes:

- Theoretical background explaining why concepts matter
- Claude Code-specific guidance and prompts
- Multiple working code examples
- Common pitfalls and solutions
- Advanced considerations
- Related topics and next steps

**Recommended Reading Order for Beginners**:
1. `docs/01-getting-started/claude-code-fundamentals.md`
2. `docs/01-getting-started/first-game-in-10-minutes.md`
3. `docs/01-getting-started/prompt-engineering-for-games.md`
4. `docs/02-core-game-concepts/game-loops-and-timing.md`
5. `docs/02-core-game-concepts/state-management.md`
6. Then explore topics as needed for your projects

**For Experienced Developers**:
Jump directly to:
- `docs/09-advanced-patterns/` for architecture patterns
- `docs/10-performance-optimization/` for optimization techniques
- `docs/06-networking-multiplayer/` for multiplayer implementation
- `docs/13-case-studies/` for real-world examples

---

## Learning Paths

Choose your path based on your goals and timeline:

### Beginner Path - 4 Weeks (2-3 hours/day)

**Goal**: Build your first complete game and understand game development fundamentals

**Week 1: Foundations**
- Day 1-2: Install Claude Code, complete Quick Start tutorial
- Day 3-4: Build Pong and Snake following examples
- Day 5-6: Read `docs/02-core-game-concepts/game-loops-and-timing.md`
- Day 7: Experiment with prompt variations, build a Pong variant

**Week 2: Core Mechanics**
- Day 8-9: Build Breakout, focus on physics
- Day 10-11: Study collision detection documentation
- Day 12-13: Build Asteroids, implement rotation and shooting
- Day 14: Create your own simple game combining learned mechanics

**Week 3: Complexity**
- Day 15-16: Build Tetris, master grid-based games
- Day 17-18: Study state management patterns
- Day 19-20: Build Flappy Bird, understand procedural generation basics
- Day 21: Start planning your first original game

**Week 4: Your First Original Game**
- Day 22-25: Build your original game using learned concepts
- Day 26-27: Polish, add sound effects and visuals
- Day 28: Deploy to web, share with community

**Outcome**: You can build complete 2D games independently and use Claude Code effectively for game development.

---

### Intermediate Path - 8 Weeks (2-3 hours/day)

**Goal**: Build multiple game genres and master advanced patterns

**Weeks 1-4**: Complete Beginner Path

**Week 5: Advanced Mechanics**
- Build Platformer Adventure
- Study physics systems in depth
- Implement enemy AI behaviors
- Master level design with tilemaps

**Week 6: Strategic Games**
- Build Tower Defense game
- Master A* pathfinding
- Implement economy systems
- Study UI/UX patterns

**Week 7: Performance and Polish**
- Study `docs/10-performance-optimization/`
- Optimize your previous games
- Implement particle systems
- Add audio systems to all games

**Week 8: Advanced Topics**
- Study Entity Component System architecture
- Explore procedural generation
- Build Roguelike Dungeon game
- Implement save/load systems

**Outcome**: You can build professional-quality 2D games in multiple genres, optimize performance, and architect scalable game systems.

---

### Advanced Path - 12 Weeks (3-4 hours/day)

**Goal**: Build production-ready games including multiplayer

**Weeks 1-8**: Complete Intermediate Path

**Week 9-10: 3D Game Development**
- Study WebGL and Three.js documentation
- Build 3D game using Babylon.js or Three.js
- Implement 3D physics
- Master shader programming basics

**Week 11: Multiplayer Networking**
- Study complete networking documentation
- Build multiplayer shooter (client and server)
- Implement lag compensation
- Deploy to production server

**Week 12: Complete Production Project**
- Build a complete game ready for release
- Implement analytics and telemetry
- Set up monetization (if applicable)
- Deploy across multiple platforms (web, mobile, desktop)
- Prepare marketing materials

**Outcome**: You can build and ship production-ready games across platforms, including complex multiplayer experiences. You're ready for professional game development or indie game creation.

---

## Technology Stack

This repository focuses on web-based game development using modern JavaScript/TypeScript:

### Core Technologies

**Languages**:
- JavaScript (ES6+) - Primary language for all examples
- TypeScript - Used in advanced examples and templates
- HTML5 - Markup for game containers
- CSS3 - Styling and responsive layouts
- GLSL - Shader programming for visual effects

**Rendering**:
- HTML5 Canvas 2D - 2D games and simple graphics
- WebGL / WebGL2 - 3D graphics and advanced 2D rendering
- Three.js - 3D game development
- Babylon.js - Complete 3D game engine
- PixiJS - High-performance 2D rendering

**Game Engines/Frameworks**:
- Phaser 3 - Comprehensive 2D game framework
- Babylon.js - Professional 3D engine
- Three.js - 3D graphics library
- PixiJS - 2D WebGL renderer
- Custom engines - Built from scratch for learning

**Networking**:
- WebSockets (ws library) - Real-time multiplayer
- Socket.io - Abstracted WebSocket library
- WebRTC - Peer-to-peer networking and voice chat

**Audio**:
- Web Audio API - All audio implementation
- Howler.js - Audio library abstraction (optional)

**Physics**:
- Matter.js - 2D physics engine
- Cannon.js - 3D physics engine
- Custom physics - For learning and simple games

### Development Tools

**Build Tools**:
- Vite - Modern, fast build tool (recommended)
- webpack - Feature-rich bundler
- Parcel - Zero-config bundler
- esbuild - Extremely fast bundler

**Testing**:
- Jest - Unit testing
- Playwright - End-to-end testing
- Cypress - Integration testing
- Testing Library - UI component testing

**Code Quality**:
- ESLint - Code linting
- Prettier - Code formatting
- TypeScript - Type checking

**Version Control**:
- Git - Version control
- GitHub - Repository hosting and CI/CD

### Deployment Platforms

**Web Hosting**:
- GitHub Pages - Free static hosting
- Netlify - Continuous deployment
- Vercel - Optimized web hosting
- AWS S3/CloudFront - Scalable hosting

**Mobile**:
- Progressive Web Apps (PWA) - Web-based mobile apps
- Capacitor - Native mobile apps from web code
- Cordova - Mobile app framework

**Desktop**:
- Electron - Cross-platform desktop apps
- Tauri - Lightweight desktop apps

**Game Distribution**:
- Itch.io - Indie game platform
- Steam - Desktop game distribution
- App Stores - iOS and Android

### Why These Technologies?

**Accessibility**: Web technologies run everywhere without installation
**Learning Curve**: JavaScript is widely known and beginner-friendly
**Iteration Speed**: Hot reloading and instant preview accelerate development
**Claude Code Compatibility**: AI excels at web technologies
**Cross-Platform**: Write once, deploy everywhere
**Community**: Massive ecosystem of libraries and resources
**Cost**: Free tools and many free hosting options

---

## Feedback

Starred this? Tell us what worked and what is missing: [open a feedback issue](https://github.com/HermeticOrmus/claude-code-game-development/issues/new?template=feedback.yml). Every piece of feedback gets an answer, and changes that come from it are credited in the release notes.

---

## Contribute

- Pick up work from the [Menu](pantry/MENU.md): every item has a Done-when anyone can check. Open items carry the [`menu` label](https://github.com/HermeticOrmus/claude-code-game-development/issues?q=is%3Aopen+label%3Amenu), and [good first issues](https://github.com/HermeticOrmus/claude-code-game-development/contribute) are on the contribute page.
- Claude picked the wrong agent or skill? File a [routing miss](https://github.com/HermeticOrmus/claude-code-game-development/issues/new?template=routing-miss.yml).
- Want a new plugin, agent, skill or command? File a [plugin proposal](https://github.com/HermeticOrmus/claude-code-game-development/issues/new?template=plugin-proposal.yml), or tell us in a [feedback issue](https://github.com/HermeticOrmus/claude-code-game-development/issues/new?template=feedback.yml).
- Show what you built in [Discussions](https://github.com/HermeticOrmus/claude-code-game-development/discussions).
- Layout and the local test loop: [Ways to contribute](CONTRIBUTING.md#ways-to-contribute).

---

## Contributing

This repository thrives on community contributions! Whether you're adding a new game example, improving documentation, or fixing bugs, your contributions are welcome.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-contribution`
3. **Make your changes** following our style guidelines
4. **Test thoroughly** - all code examples must work
5. **Commit** with clear messages: `git commit -m "Add: Snake variant with power-ups"`
6. **Push** to your fork: `git push origin feature/amazing-contribution`
7. **Open a Pull Request** with detailed description

### Contribution Ideas

**New Game Examples**:
- Variants of existing games (e.g., multiplayer Tetris)
- New game genres (racing, fighting, rhythm games)
- Mobile-specific game examples
- VR/AR game examples

**Documentation Improvements**:
- Additional code examples
- Better explanations of complex topics
- Translations to other languages
- Video tutorial scripts

**Prompts and Templates**:
- New prompt patterns you've discovered
- Additional project templates
- Optimization prompts that worked well

**Tools and Utilities**:
- Development helper tools
- Asset generation scripts
- Testing utilities
- Deployment automation

### Code Quality Standards

All contributions must meet these standards:

**Code Must**:
- Work completely without errors
- Follow ESLint rules (config included)
- Include comprehensive comments
- Handle errors gracefully
- Be performant (no obvious bottlenecks)
- Follow security best practices

**Documentation Must**:
- Be technically accurate
- Include working code examples
- Use clear, beginner-friendly language
- Link to related resources
- Be free of typos and grammatical errors

**Game Examples Must**:
- Be playable and fun
- Include README with architecture explanation
- Include PROMPTS.md with Claude Code workflow
- Have source code with detailed comments
- Run at 60 FPS on modern hardware
- Be accessible (keyboard controls minimum)

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## Community

Join the growing community of developers building games with Claude Code:

### Get Help

- **Feedback**: [Open a feedback issue](https://github.com/HermeticOrmus/claude-code-game-development/issues/new?template=feedback.yml) to ask questions, share projects, or say what is missing
- **Issues**: Report bugs or request features
- **Discord**: Real-time chat with other developers (link coming soon)

### Share Your Work

Built something cool with this resource? We'd love to see it!

1. [Open a feedback issue](https://github.com/HermeticOrmus/claude-code-game-development/issues/new?template=feedback.yml) about your project
2. Include screenshots, description, and link
3. Or submit a pull request that adds it to this README
4. Get featured in our community highlights!

### Community Guidelines

We're committed to providing a welcoming, inclusive environment for all developers. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

**Expected Behavior**:
- Be respectful and considerate
- Welcome beginners and help them learn
- Give constructive feedback
- Respect different perspectives and approaches
- Focus on building great games together

---

## FAQ

### About Claude Code

**Q: Do I need a paid Claude Code subscription?**
A: Claude Code offers both free and paid tiers. The free tier is sufficient for learning and building the example games. Paid tiers offer faster responses and higher usage limits.

**Q: Can Claude Code really build an entire game?**
A: Yes! With proper prompts, Claude Code can generate complete, working games. However, you'll likely iterate and refine the AI-generated code for best results. This repository teaches you how to do this effectively.

**Q: Will Claude Code replace game developers?**
A: No. Claude Code is a tool that augments developer capabilities. You still need to design the game, direct development, make creative decisions, and refine the implementation. Think of it as a highly skilled assistant, not a replacement.

### About This Repository

**Q: Do I need to follow the learning paths in order?**
A: The learning paths are recommendations. Feel free to jump to topics that interest you, but beginners should start with the fundamentals.

**Q: Can I use code from this repository in my commercial games?**
A: Yes! This repository is MIT licensed, meaning you can use the code for any purpose, including commercial projects. Attribution is appreciated but not required.

**Q: Are the game examples production-ready?**
A: The simple and intermediate examples are great learning tools but would need polish for commercial release. The advanced examples demonstrate production-quality patterns and could be used as foundations for commercial games with additional development.

**Q: What if I get stuck?**
A: Check the troubleshooting guides in each section, search the issues for similar problems, or open a feedback issue. The community is here to help!

### About Game Development

**Q: Can I make 3D games with these techniques?**
A: Yes! The repository includes 3D game development with Three.js and Babylon.js. See `docs/08-game-engines/` for details.

**Q: Can I build multiplayer games?**
A: Absolutely! See `docs/06-networking-multiplayer/` for WebSocket games, and the `multiplayer-networking` plugin for rollback, lockstep, client prediction, and lag compensation in Godot and Unity.

**Q: What about mobile games?**
A: All games can be deployed to mobile via PWA, Capacitor, or Cordova. See `docs/12-deployment-distribution/mobile-packaging.md`.

**Q: Can I monetize games built with Claude Code?**
A: Yes! See `docs/12-deployment-distribution/monetization-strategies.md` for implementation details on ads, in-app purchases, and premium models.

### Technical Questions

**Q: What browser is recommended?**
A: Chrome, Edge, or Firefox (latest versions) work great. Safari works but may have some WebGL limitations.

**Q: Do I need a powerful computer?**
A: No. Any modern computer from the last 5 years should work fine for development. The example games are optimized to run on modest hardware.

**Q: Can I use a different programming language?**
A: This repository focuses on JavaScript/TypeScript for web games, but the concepts and prompt engineering techniques apply to any language. Claude Code supports many languages.

**Q: What about game assets (graphics, sounds)?**
A: Simple games use programmatic graphics (shapes, particles). For production games, you'll need to create or license assets. The repository includes guidance on asset integration.

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details. The 66 plugins derived from wshobson/agents are Copyright (c) 2024 Seth Hobson, also under the MIT License; [NOTICE.md](NOTICE.md) lists them with the upstream notice.

**What this means**:
- Use this code for any purpose (personal, educational, commercial)
- Modify and distribute freely
- No warranty is provided
- Include the license and copyright notice in distributions

---

## Acknowledgments

This repository was created to empower game developers and advance the field of AI-assisted development.

**Special Thanks To**:
- **[Seth Hobson](https://github.com/wshobson)** for [wshobson/agents](https://github.com/wshobson/agents), the MIT-licensed collection that 66 of the plugins here come from (see [NOTICE.md](NOTICE.md))
- **[manutej](https://github.com/manutej)** for the [meta-prompting framework](https://github.com/manutej/meta-prompting-framework) in `tools/`
- **Anthropic** for creating Claude Code and pushing the boundaries of AI-assisted development
- **The Game Development Community** for decades of knowledge sharing and open-source contributions
- **All Contributors** who help improve this resource
- **You** for choosing to learn game development with AI assistance

---

## What's Next?

Ready to start building games with Claude Code?

1. **Complete the Quick Start** above
2. **Choose your learning path** based on your experience level
3. **Install the game plugins** that fit your engine and systems
4. **Build the example games** from their specs to learn concepts hands-on
5. **Create your own game** using the docs and prompts
6. **Share your creation** with the community
7. **Contribute back** to help other developers

**The future of game development is here. Let's build it together.**

---

**Happy Game Development!**

*"The best way to predict the future is to build it."*

---

**Repository Statistics:**
- 87 Claude Code plugins (22 for games): 168 agents, 90 commands, 81 skills, 3 hooks
- 180,000+ words of documentation across 80 files
- A meta-prompting framework in `tools/`
- Comprehensive learning paths
- Production-ready patterns

**Last Updated**: 2025
**Maintained By**: Community Contributors
**Status**: Active Development

---

[⬆ Back to Top](#claude-code-game-development)

---

## Part of the Libre Open-Source Stack for Claude Code

This repository is part of a growing family of open-source toolkits for Claude Code.

### Libre suite — comprehensive plugin bundles

- [LibreUIUX-Claude-Code](https://github.com/HermeticOrmus/LibreUIUX-Claude-Code) — UI/UX development (152 agents, 70 plugins, 76 commands, 74 skills)
- [LibreArch-Claude-Code](https://github.com/HermeticOrmus/LibreArch-Claude-Code) — Software architecture and system design
- [LibreCopy-Claude-Code](https://github.com/HermeticOrmus/LibreCopy-Claude-Code) — Technical writing and documentation engineering
- [LibreDevOps-Claude-Code](https://github.com/HermeticOrmus/LibreDevOps-Claude-Code) — DevOps engineering and infrastructure automation
- [LibreEmbed-Claude-Code](https://github.com/HermeticOrmus/LibreEmbed-Claude-Code) — Embedded systems, firmware, and IoT development
- [LibreFinTech-Claude-Code](https://github.com/HermeticOrmus/LibreFinTech-Claude-Code) — Financial technology development
- [LibreGEO-Claude-Code](https://github.com/HermeticOrmus/LibreGEO-Claude-Code) — AI-search optimization (ChatGPT, Perplexity, Gemini, Google AI Overviews)
- [LibreGameDev-Claude-Code](https://github.com/HermeticOrmus/LibreGameDev-Claude-Code) — Game development across Godot, Unity, Unreal (its plugins now ship here)
- [LibreMLOps-Claude-Code](https://github.com/HermeticOrmus/LibreMLOps-Claude-Code) — ML engineering and AI operations
- [LibreMobileDev-Claude-Code](https://github.com/HermeticOrmus/LibreMobileDev-Claude-Code) — Mobile app development (Flutter, React Native, native iOS, native Android)
- [LibreSecOps-Claude-Code](https://github.com/HermeticOrmus/LibreSecOps-Claude-Code) — Security operations

### Skills mini-repos — single CLAUDE.md drop-ins

- [vibe-engineer-skills](https://github.com/HermeticOrmus/vibe-engineer-skills) — Direct AI codegen well (hypothesis → scope → validate → reject working-but-wrong)
- [markdown-discipline-skills](https://github.com/HermeticOrmus/markdown-discipline-skills) — Strip AI-slop from markdown (no em dashes, no marketing fluff)
- [shell-safety-skills](https://github.com/HermeticOrmus/shell-safety-skills) — `set -euo pipefail` discipline + 15 failure-mode examples
- [commit-standard-skills](https://github.com/HermeticOrmus/commit-standard-skills) — Ormus Commit Standard v1.0 + commit-msg hook + commitlint
- [unwoke-skills](https://github.com/HermeticOrmus/unwoke-skills) — Strip AI theater (ten sins to eliminate, symmetric engagement)
- [python-conventions-skills](https://github.com/HermeticOrmus/python-conventions-skills) — Modern Python 3.11+ (types, pathlib, async, ruff, mypy, uv)
- [typescript-conventions-skills](https://github.com/HermeticOrmus/typescript-conventions-skills) — TypeScript strict mode, discriminated unions, Result types
- [hermetic-laws-skills](https://github.com/HermeticOrmus/hermetic-laws-skills) — Seven Hermetic Principles applied to engineering
- [riper-workflow-skills](https://github.com/HermeticOrmus/riper-workflow-skills) — Research / Innovate / Plan / Execute / Review systematic dev
- [six-day-cycle-skills](https://github.com/HermeticOrmus/six-day-cycle-skills) — Sustainable shipping cadence with mandatory rest
- [token-optimization-skills](https://github.com/HermeticOrmus/token-optimization-skills) — Claude Code token + context optimization
- [osint-skills](https://github.com/HermeticOrmus/osint-skills) — OSINT research methodology (multi-wave investigative spiral)
- [calcinate-skills](https://github.com/HermeticOrmus/calcinate-skills) — Stage 1 of the Magnum Opus (burn project bloat)
- [claude-md-overhaul-skills](https://github.com/HermeticOrmus/claude-md-overhaul-skills) — Audit CLAUDE.md and MEMORY.md against caps
- [session-handoff-skills](https://github.com/HermeticOrmus/session-handoff-skills) — Session handoff + pickup discipline
- [naming-skills](https://github.com/HermeticOrmus/naming-skills) — Product naming methodology (mine the brand's vocabulary)
- [magnum-opus-skills](https://github.com/HermeticOrmus/magnum-opus-skills) — Seven-stage alchemy applied to project transformation

### Template source

- [andrej-karpathy-skills](https://github.com/HermeticOrmus/andrej-karpathy-skills) — the canonical single-file CLAUDE.md pattern (fork of jiayuan_jy's original)

Star the family, not just one — that's how the suite stays coherent.
