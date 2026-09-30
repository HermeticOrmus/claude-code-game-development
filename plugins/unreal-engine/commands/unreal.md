---
description: "Create actors, set up the Gameplay Framework, build abilities, or debug an Unreal Engine 5 project"
argument-hint: "[actor|framework|ability|debug] <feature>"
---

# /unreal

Unreal Engine 5 development: Gameplay Framework, Blueprint/C++, GAS, replication, materials, and Lumen/Nanite.

## Trigger

`/unreal [action] [target]`

## Actions

### `actor`
Create Actor/Character/Pawn classes with proper UE5 structure.

```
/unreal actor "ACharacter subclass with Enhanced Input, movement, jump, replicated health"
/unreal actor "AI enemy: patrol waypoints, detect player via sight, chase and attack"
/unreal actor "interactive door: Blueprint interface, opens with RPC, replicated open state"
```

**Output**: C++ header + source with UPROPERTY/UFUNCTION macros, BeginPlay, replication setup, Blueprint-callable interface.

### `framework`
Design Gameplay Framework class responsibilities.

```
/unreal framework "multiplayer FPS: where does kill tracking, score, team assignment go?"
/unreal framework "RPG with stats, abilities, inventory - GameMode vs PlayerState vs Character"
/unreal framework "metagame session flow: lobby, game, post-game using GameInstance"
```

**Output**: Class responsibility diagram, which class owns which data, replication boundaries.

### `ability`
Implement with Gameplay Ability System.

```
/unreal ability "projectile fire ability with mana cost, cooldown, and GAS tags"
/unreal ability "stun status effect: GameplayEffect with duration, blocks movement ability"
/unreal ability "attribute set for health, mana, stamina with damage calculation"
```

**Output**: GAS component setup, UGameplayAbility subclass, UGameplayEffect data asset spec, UAttributeSet C++.

### `debug`
Diagnose Unreal-specific problems.

```
/unreal debug "Replicated property not updating on clients"
/unreal debug "Server RPC not being called - client fires but server never receives"
/unreal debug "Blueprint cast fails at runtime after C++ refactor"
/unreal debug "Nanite mesh not rendering correctly with translucent material"
```

**Output**: Root cause (replication, authority, cast validity), fix code, prevention.

## Examples

**Setting up a multiplayer character:**
```
/unreal actor "ACharacter with Enhanced Input, replicated health and death, server attack RPC"
```
Produces: Complete `.h` and `.cpp` with `DOREPLIFETIME`, server RPC with `_Validate` + `_Implementation`, multicast for cosmetic effects, `GetLifetimeReplicatedProps`.

**Designing Gameplay Framework for a game type:**
```
/unreal framework "4-player co-op dungeon game: shared health pool, wave enemies, loot on boss kill"
```
Produces: Class responsibility table, shared health in GameState (replicated), wave spawning in GameMode (server only), loot distribution RPC chain, PlayerState for per-player score.

## Gameplay Framework Quick Reference

| Question | Class | Exists On |
|----------|-------|----------|
| What are the rules? | GameMode | Server only |
| What's the current game state? | GameState | Server + clients |
| What input is this player giving? | PlayerController | Server + owning client |
| What's this player's public data? | PlayerState | Server + all clients |
| What's the physical player? | Pawn/Character | Server + all clients |
| What persists across levels? | GameInstance | Local only |

## Blueprint Communication Guide

| Scenario | Use |
|----------|-----|
| Same actor, function call | Direct call |
| Child actor knows parent type | Cast (cache the result) |
| Unknown actor type, shared behavior | Blueprint Interface |
| Broadcast to any listener | Event Dispatcher |
| Global cross-system event | GAS Gameplay Tag event |
