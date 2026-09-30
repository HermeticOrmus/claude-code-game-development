---
description: "Generate terrain, dungeons, or content placement procedurally, or validate generated output"
argument-hint: "[terrain|dungeon|populate|validate] <what to generate>"
---

# /procgen

Procedural content generation: terrain, dungeons, caves, tile maps, and content placement.

## Trigger

`/procgen [action] [target]`

## Actions

### `terrain`
Generate noise-based terrain or heightmaps.

```
/procgen terrain "2D sidescroller background with rolling hills"
/procgen terrain "top-down world map with biomes: forest, desert, water"
/procgen terrain "3D heightmap with mountain peaks and valleys, 256x256"
```

**Output**: FastNoiseLite configuration, heightmap sampling function, biome thresholds.

### `dungeon`
Generate room-based dungeon or cave layouts.

```
/procgen dungeon "BSP dungeon 80x50 grid, 8-15 rooms, connect all rooms"
/procgen dungeon "cellular automata cave system, 60x40, 5 smoothing passes"
/procgen dungeon "drunk walk corridors for underground tunnels"
```

**Output**: Typed GDScript generator class with seed parameter, room list, corridor list, TileMap fill method.

### `populate`
Place enemies, items, and events in generated spaces.

```
/procgen populate "enemies in dungeon rooms scaled by difficulty 0-1"
/procgen populate "loot tables for 3 room types: treasure, combat, rest"
/procgen populate "guaranteed key item in first room, exit in last room"
```

**Output**: RoomPopulator with derived seeds, weighted random placement, quota enforcement.

### `validate`
Add solvability and quality checks to a generator.

```
/procgen validate "check dungeon has path from spawn to exit"
/procgen validate "verify enemy count within 3-8 range per level"
/procgen validate "stress test: generate 100 levels and report failures"
```

**Output**: BFS flood fill validator, stat assertions, batch generation test loop.

## Examples

**Generating a seeded dungeon with validation:**
```
/procgen dungeon "BSP dungeon for roguelike, 100x60, must have guaranteed spawn-to-exit path"
```
Produces: `BSPDungeon.generate(bounds, seed)` with rooms + corridors, plus `DungeonValidator.is_solvable()` check; if unsolvable, increments seed and retries.

**Terrain with biomes:**
```
/procgen terrain "top-down world with ocean (< 0.3), beach (0.3-0.4), grass (0.4-0.7), mountain (> 0.7)"
```
Produces: `FastNoiseLite` config, `get_biome(x, y) -> StringName` function using noise thresholds, TileMap tile assignment.

## Algorithm Selection Guide

| Goal | Algorithm | Notes |
|------|-----------|-------|
| Structured dungeon rooms | BSP | Controllable room count, clean corridors |
| Organic caves | Cellular automata | Tune birth/death limits for cave density |
| Winding tunnels | Drunk walk | Adjust step count for corridor length |
| Tile-constrained variety | Wave Function Collapse | Requires adjacency rule definition |
| Terrain heightmap | Simplex fBm | Tune octaves + lacunarity for detail level |
| Scattered objects | White noise | Objects, trees, debris - not terrain |
| Cracked rock / alien ground | Voronoi noise | Cell-based patterns |

## Seeding Protocol

All generators must accept an `int seed` parameter:
```gdscript
# Correct: explicit RNG
var rng := RandomNumberGenerator.new()
rng.seed = level_seed

# Wrong: global rng breaks reproducibility
var x = randi()  # Different every run
```
