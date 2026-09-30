---
description: "Design, implement, migrate, or debug a game save system"
argument-hint: "[design|implement|migrate|debug] <save data or problem>"
---

# /save-system

Save file architecture, serialization, versioning, migration, and platform cloud saves for Godot games.

## Trigger

`/save-system [action] [target]`

## Actions

### `design`
Architect a save system for a specific game type.

```
/save-system design "RPG with 3 save slots, manual saves, and autosave at checkpoints"
/save-system design "roguelike: single save file, delete on death, save on exit"
/save-system design "open world: frequent autosave + manual slots + Steam Cloud"
```

**Output**: Save data schema, slot design rationale, autosave trigger points, file format recommendation.

### `implement`
Generate save/load code.

```
/save-system implement "player position, health, inventory array, and quest flags"
/save-system implement "settings file separate from game save"
/save-system implement "save slot metadata for UI (level name, playtime, date)"
```

**Output**: Typed GDScript with `to_dict()` / `from_dict()`, atomic write with tmp+rename, version field.

### `migrate`
Add versioning or migration to an existing save system.

```
/save-system migrate "added new 'stamina' stat in v2 that didn't exist in v1"
/save-system migrate "renamed 'hp' to 'health' and added 'max_health' field"
/save-system migrate "moved audio settings from game save into separate settings file"
```

**Output**: Migration function chain, version bump, backward compatibility handler, test procedure.

### `debug`
Diagnose save system problems.

```
/save-system debug "save file sometimes empty on game crash"
/save-system debug "loading old save throws error after adding new inventory system"
/save-system debug "settings reset whenever player starts new game"
```

**Output**: Root cause, fix code, prevention strategy.

## Examples

**Implementing a complete save system:**
```
/save-system implement "2D platformer save: player position, health, collected items (Array), level, playtime"
```
Produces: `PlayerSaveData` with `to_dict()`/`from_dict()`, `SaveManager` with atomic write, version=1, slot 0-2 support.

**Migrating from v1 to v2:**
```
/save-system migrate "v1 had 'max_hp: 100', v2 renames to 'max_health' and adds 'stamina: 100'"
```
Produces: `_migrate_v1_to_v2()` function that renames key, adds missing key with default, bumps version.

**Diagnosing corrupt save on crash:**
```
/save-system debug "save file is empty or truncated when game crashes during save"
```
Root cause: writing directly to save path; crash during write truncates file. Fix: write to `.tmp`, rename to final path (atomic).

## Save Format Decision Table

| Game Type | Format | Slots | Autosave |
|-----------|--------|-------|---------|
| Indie story game | JSON | 3 manual | Checkpoints |
| Roguelike | JSON | 1 (run = slot) | Exit only |
| Open world | JSON | 3 + autosave | Every 3 min + transitions |
| Mobile game | JSON + cloud | 1 (cloud sync) | Constant |
| High-performance PC | Binary | 3 | Frequent |

## Versioning Rule

Every save file ships with version=1. Every schema change increments the version. Migration functions handle every version transition. This is non-negotiable - without it, the first schema change corrupts all existing saves.
