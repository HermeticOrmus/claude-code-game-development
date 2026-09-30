# game-architecture

Game architecture plugin for LibreGameDev. Covers game loop patterns, ECS composition, event systems, Resource/ScriptableObject data architecture, service locator, and scene management.

## Core References

- "Game Programming Patterns" - Robert Nystrom (free at gameprogrammingpatterns.com)
- "Fix Your Timestep!" - Glenn Fiedler (gafferongames.com)
- Unity DOTS ECS documentation
- EnTT ECS library documentation

## Pattern Selection Guide

| Symptom | Pattern to Apply |
|---------|-----------------|
| Scripts depend on node paths | Signal wiring or Service Locator |
| Same data in multiple scripts | Resource/ScriptableObject |
| Cross-scene communication breaks | EventBus autoload |
| Physics behavior framerate-dependent | Fixed Timestep (use _physics_process) |
| 500+ objects updating per frame | ECS / batch systems |
| Singleton dependency web | Service Locator with registration |
| Scene transition state lost | Game State Stack |
| God script >300 lines | Component decomposition |

## Components

- **game-architect**: Agent with expertise in game loop patterns, ECS, event systems, and Nystrom's pattern catalog
- **game-arch**: Command for designing, refactoring, testing, and profiling game systems
- **game-arch-patterns**: Skill library with fixed timestep loop, EventBus, ECS composition, Resource data, Service Locator, and Game State Stack

## Quick Start

Design a new system:
```
/game-arch design "inventory with items, equipment, and crafting"
```

Refactor a god script:
```
/game-arch refactor "Player.gd is 400 lines handling everything"
```

Write testable code:
```
/game-arch test "health and damage system with GUT"
```
