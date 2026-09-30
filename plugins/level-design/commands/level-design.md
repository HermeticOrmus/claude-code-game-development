---
description: "Greybox a level, set up tiles, bake navigation, or prepare a level for export"
argument-hint: "[greybox|tile|nav|export] <level or area>"
---

# /level-design

Level construction: greyboxing, TileMap configuration, NavMesh baking, zone streaming, and environmental design.

## Trigger

`/level-design [action] [target]`

## Actions

### `greybox`
Plan or review greybox phase for a level space.

```
/level-design greybox "dungeon level: entry chamber, 3 side rooms, boss room"
/level-design greybox "platformer level: introduction, mid-challenge, climax zone"
/level-design greybox "review this greybox for navigability and pacing"
```

**Output**: Spatial intent description, CSG node structure, playtest checklist.

### `tile`
Configure TileMap/TileSet or troubleshoot tile issues.

```
/level-design tile "2D platformer TileMap with autotile terrain and physics"
/level-design tile "isometric TileMap with Z-sorting and collision"
/level-design tile "tile physics seam causing player to catch"
```

**Output**: TileSet configuration steps, terrain set setup, physics layer assignment, GDScript tile painting code.

### `nav`
Configure and validate navigation mesh for AI agents.

```
/level-design nav "humanoid enemy navigation for indoor dungeon"
/level-design nav "flying enemy pathfinding separate from ground nav"
/level-design nav "NavMesh not reaching corners of room"
```

**Output**: NavigationRegion3D bake parameters, diagnostic steps for nav issues, NavigationLink3D for special traversal.

### `export`
Set up level streaming and zone transition.

```
/level-design export "open world with 6 streaming zones and seamless transitions"
/level-design export "scene-per-level loading with loading screen"
/level-design export "additive loading for dungeon floors"
```

**Output**: LevelStreamer GDScript, ZoneTrigger placement guide, preload distance calculation.

## Examples

**Dungeon layout design:**
```
/level-design greybox "roguelite dungeon: procedural rooms connected by corridors, locked doors, boss room"
```
Produces: Room size standards, corridor dimensions, CSG template scenes, playtest checklist.

**TileMap autotile terrain:**
```
/level-design tile "grass/dirt/water terrain with smooth autotile transitions"
```
Produces: TileSet terrain set configuration, `set_cells_terrain_connect()` usage, fallback tile for missing terrain combos.

**NavMesh debugging:**
```
/level-design nav "enemies get stuck at doorway corners"
```
Root cause: agent_radius larger than corner clearance. Fix: reduce agent_radius in NavigationMesh, or widen doorways by 2*agent_radius.

## Level Pacing Reference

| Zone Type | Spatial Character | Purpose |
|-----------|-----------------|---------|
| Introduction | Open, safe, visible exits | Establish rules, low pressure |
| Challenge | Constrained, hazards visible | Apply learned rules |
| Relief | Wider, resource-rich | Recovery before next challenge |
| Climax | Dramatic, high stakes | Peak challenge application |
| Reward | Open, visually distinct | Payoff, exploration opportunity |
