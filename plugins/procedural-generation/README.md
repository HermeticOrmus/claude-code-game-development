# procedural-generation

Procedural generation plugin for LibreGameDev. Covers noise functions (Simplex, Perlin, Voronoi, fBm), dungeon algorithms (BSP, cellular automata, drunk walk), Wave Function Collapse, seeded randomness, content population, and solvability validation.

## Algorithm Quick Reference

| Algorithm | Output | Godot Tool | When to Use |
|-----------|--------|-----------|-------------|
| Simplex fBm | Smooth terrain | FastNoiseLite | Heightmaps, biomes, organic textures |
| BSP | Room-based dungeon | Custom | Structured dungeon layouts |
| Cellular automata | Cave/organic shapes | Custom | Underground caves, eroded terrain |
| Drunk walk | Winding corridors | Custom | Tunnels, rivers |
| WFC | Tile-constrained maps | Custom | When tile adjacency rules matter |
| Voronoi | Cell patterns | FastNoiseLite TYPE_CELLULAR | Cracked rock, territory maps |

## Components

- **procgen-engineer**: Agent with expertise in noise mathematics, dungeon algorithms, WFC, seeded randomness, authored intent vs procedural balance
- **procgen**: Command for generating terrain, dungeons, caves, populating content, and validating solvability
- **procgen-patterns**: Skill library with FastNoiseLite terrain, BSP dungeon generator, cellular automata cave, seeded room populator with weighted loot, BFS solvability validator

## Quick Start

Generate a dungeon:
```
/procgen dungeon "BSP dungeon 80x50, 10 rooms, seeded, validate path exists"
```

Generate terrain heightmap:
```
/procgen terrain "simplex fBm heightmap with 5 octaves for 2D world"
```

Add content population:
```
/procgen populate "enemies per room scaled to difficulty, guaranteed key item"
```

## Seeding Rule

Every procedural system must accept an integer seed and produce identical output for the same seed. Save the seed; save the world. Use `RandomNumberGenerator` with explicit seed, never global `randf()`.

## Solvability Guarantee

Always run a BFS flood fill from spawn to exit before exposing a generated level to the player. If unsolvable, increment seed and regenerate. Never ship a generator that can produce unwinnable levels.
