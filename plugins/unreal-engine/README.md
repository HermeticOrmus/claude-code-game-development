# unreal-engine

Unreal Engine 5 plugin for LibreGameDev. Covers Gameplay Framework (GameMode/GameState/PlayerController/Pawn/GameInstance), Blueprint vs C++ architecture, UObject/AActor lifecycle, Gameplay Ability System (GAS), Enhanced Input System, network replication (RPCs, DOREPLIFETIME), Lumen/Nanite rendering, and the Material system.

## Gameplay Framework

| Class | Server/Client | Owns |
|-------|--------------|------|
| GameMode | Server only | Game rules, spawning, win/lose |
| GameState | Server + clients | Replicated game state (score, round) |
| PlayerController | Server + owning client | Input, camera, HUD |
| PlayerState | Server + all clients | Per-player public data (score, team) |
| Character/Pawn | Server + all clients | Physical representation, movement |
| GameInstance | Local only | Session, settings, cross-level data |

## Components

- **unreal-developer**: Agent with expertise in Gameplay Framework, Blueprint/C++ hybrid patterns, GAS, Enhanced Input, replication, Lumen/Nanite, and Material system
- **unreal**: Command for creating Actor/Character classes, designing Gameplay Framework responsibilities, implementing GAS abilities, and debugging replication/Blueprint issues
- **unreal-patterns**: Skill library with ACharacter + Enhanced Input (C++), Blueprint Interface pattern, server RPC with validation + multicast, Gameplay Tag usage, and anti-patterns catalog

## Quick Start

Create a character:
```
/unreal actor "ACharacter with Enhanced Input: move, look, jump, replicated health"
```

Design system ownership:
```
/unreal framework "multiplayer shooter: where does score, kills, respawn logic live?"
```

Implement an ability:
```
/unreal ability "dash ability: short dash with iframe, 1.5 second cooldown, GAS implementation"
```

## Blueprint vs C++

Use C++ for: base classes, GAS, replication setup, performance-critical systems.
Use Blueprint for: prototyping, designer-owned logic, UI, level scripting, ability visual effects.
Hybrid: C++ base with `BlueprintCallable`/`BlueprintImplementableEvent` so Blueprint can extend and override.
