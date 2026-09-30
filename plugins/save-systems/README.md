# save-systems

Save system plugin for LibreGameDev. Covers JSON/binary serialization, save schema versioning and migration, atomic write patterns (tmp+rename), save slot design, slot metadata for UI, settings persistence, and platform cloud saves.

## Core Principles

1. **Version every save file** - `"version": 1` from day one. Every schema change = version increment + migration function.
2. **Atomic writes** - Write to `.tmp`, rename to final. A crash during write leaves the original intact.
3. **Keep backup** - Copy previous save to `.bak` before overwriting. Offer restore on corruption.
4. **Separate settings from saves** - Resetting settings must not lose game progress.
5. **Never save node references** - Save data values (health: 80), not node pointers.

## Components

- **save-system-engineer**: Agent with expertise in serialization tradeoffs, versioning/migration strategy, atomic writes, slot design by genre, and platform cloud save APIs
- **save-system**: Command for designing save architecture, generating serialization code, adding migration chains, and debugging corruption
- **save-system-patterns**: Skill library with SaveManager (atomic write, migration chain, backup restore), PlayerSaveData (to_dict/from_dict), SaveSlotMeta (lightweight UI metadata), and GameSettings (ConfigFile-based)

## Quick Start

Design a save system for your game type:
```
/save-system design "2D action RPG: 3 save slots, autosave at doors, player position + inventory + quest flags"
```

Implement save data model:
```
/save-system implement "player health, position, inventory as string array, and collected_flags dictionary"
```

Add migration for a schema change:
```
/save-system migrate "added 'stamina' field in v2 that old saves don't have"
```

## File Layout

```
user://
  save_0.json      <- Slot 0 (current)
  save_0.json.bak  <- Slot 0 backup (previous save)
  save_0.json.tmp  <- Slot 0 in-progress write (deleted on success)
  save_1.json
  save_2.json
  settings.cfg     <- Separate from game saves
```
