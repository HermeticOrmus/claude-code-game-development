# Game Engines for Web Development

This section provides comprehensive guides for integrating popular game engines and frameworks into your web game development workflow, along with guidance on building custom engines.

## Overview

Game engines provide essential infrastructure for game development, handling rendering, physics, audio, input, and more. For web games, you have several options ranging from full-featured engines to lightweight frameworks and custom solutions.

## When to Use Different Engines

### Phaser 3 (2D Games)
**Best for:** Mobile-friendly 2D games, prototypes, arcade games, platformers

**Advantages:**
- Comprehensive 2D feature set out of the box
- Excellent documentation and community
- Built-in physics (Arcade, Matter.js)
- Scene management and asset loading
- Mobile-optimized

**Use when:** You want to ship 2D games quickly with minimal setup, need proven mobile performance, or are building classic game genres (platformers, shooters, puzzle games).

### Babylon.js (3D Games)
**Best for:** Complex 3D games, simulations, VR/AR experiences

**Advantages:**
- Production-ready 3D engine with complete toolchain
- Excellent performance optimization
- WebXR support built-in
- Node-based material editor
- Physics integration (Cannon.js, Ammo.js, Havok)
- Active development and Microsoft backing

**Use when:** Building sophisticated 3D experiences, need VR/AR support, want visual development tools, or require enterprise-level support.

### Three.js (3D Visualization and Games)
**Best for:** Custom 3D experiences, data visualization, artistic projects

**Advantages:**
- Lightweight and flexible
- Massive community and examples
- Great for custom rendering pipelines
- Excellent WebGL abstraction
- Many third-party plugins

**Use when:** You need maximum flexibility, are building custom 3D visualizations, want fine-grained control, or have specific rendering requirements.

### PixiJS (High-Performance 2D)
**Best for:** Sprite-heavy games, slot machines, animated interfaces

**Advantages:**
- Extremely fast 2D rendering
- WebGL-based sprite batching
- Minimal API surface
- Great for UI-heavy games

**Use when:** Maximum 2D rendering performance is critical, building games with thousands of sprites, or creating animated casino/slot games.

### Unity WebGL
**Best for:** Porting existing Unity games, complex 3D projects, teams familiar with Unity

**Advantages:**
- Full Unity Editor features
- Existing Unity asset ecosystem
- Cross-platform development
- Visual development environment

**Use when:** You have existing Unity games to port, your team knows Unity, or you need the complete Unity ecosystem.

### Custom Engine
**Best for:** Learning, specific requirements, maximum control, minimal file size

**Advantages:**
- Complete control over every aspect
- No unnecessary code or features
- Deep understanding of engine architecture
- Optimal for specific use cases

**Use when:** You have unique requirements, need minimal file size, want educational value, or existing engines don't fit your needs.

## Performance Comparison

| Engine | File Size (min) | 2D Performance | 3D Performance | Learning Curve | Mobile Support |
|--------|----------------|----------------|----------------|----------------|----------------|
| Phaser 3 | ~1.2 MB | Excellent | N/A | Low | Excellent |
| Babylon.js | ~2 MB | Good | Excellent | Medium | Very Good |
| Three.js | ~600 KB | Good | Very Good | Medium | Good |
| PixiJS | ~400 KB | Excellent | N/A | Low | Excellent |
| Unity WebGL | 5+ MB | Good | Excellent | High | Fair |
| Custom | Varies | Varies | Varies | High | Depends |

## Architecture Patterns

### Scene-Based Architecture (Phaser, Babylon.js)
Games organized into discrete scenes (menus, levels, game over screens). Each scene has its own lifecycle methods (create, update, destroy).

### Component-Based Architecture (Custom, Three.js)
Game objects composed of reusable components. More flexible but requires more setup.

### Entity-Component-System (Advanced)
Maximum performance and flexibility through data-oriented design. See Advanced Patterns section.

## Integration with Modern Web Stack

All engines integrate well with modern JavaScript tooling:

```javascript
// ES6 modules
import Phaser from 'phaser';
import * as THREE from 'three';
import * as BABYLON from '@babylonjs/core';
import * as PIXI from 'pixi.js';

// TypeScript support (all engines have type definitions)
// Bundlers: Webpack, Vite, Rollup, esbuild
// Frameworks: React, Vue, Svelte (see individual guides)
```

## Claude Code Integration

Each engine guide includes specific Claude Code prompts optimized for that engine. Common patterns:

```
Create a Phaser 3 game with [features] using [physics engine]
```

```
Build a Babylon.js scene with [lighting] and [meshes]
```

```
Implement [game mechanic] using Three.js
```

```
Optimize PixiJS rendering for [number] sprites
```

## Section Navigation

1. **[Phaser Integration](./phaser-integration.md)** - Complete guide to building 2D games with Phaser 3
2. **[Babylon.js Workflows](./babylon-js-workflows.md)** - 3D game development with Babylon.js
3. **[Three.js Games](./three-js-games.md)** - Custom 3D games with Three.js
4. **[PixiJS Performance](./pixi-js-performance.md)** - High-performance 2D rendering
5. **[Unity Web Export](./unity-web-export.md)** - WebGL export and optimization
6. **[Custom Engine Development](./custom-engine-development.md)** - Building your own engine

## Choosing Your Engine: Decision Tree

1. **Is your game 2D or 3D?**
   - 2D → Go to step 2
   - 3D → Go to step 4

2. **2D: Do you need maximum performance (thousands of sprites)?**
   - Yes → PixiJS
   - No → Go to step 3

3. **2D: Do you want comprehensive features out of the box?**
   - Yes → Phaser 3
   - No → Custom Engine or PixiJS

4. **3D: Are you porting an existing Unity game?**
   - Yes → Unity WebGL
   - No → Go to step 5

5. **3D: Do you need VR/AR or a complete 3D toolchain?**
   - Yes → Babylon.js
   - No → Go to step 6

6. **3D: Do you need maximum flexibility and custom rendering?**
   - Yes → Three.js
   - No → Babylon.js (best general-purpose 3D)

## Getting Started

Each engine guide includes:
- Setup and configuration
- Core concepts and architecture
- Complete game examples
- Best practices and patterns
- Claude Code prompts for rapid development
- Performance optimization techniques
- Common pitfalls and solutions

Choose an engine from the navigation above to begin!
