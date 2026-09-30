# level-design

Level design plugin for LibreGameDev. Covers greyboxing workflow, Godot TileMap/TileSet, NavMesh baking, zone streaming, modular kit design, and environmental storytelling.

## Design Principle

Greybox before art. Test before polish. Every level starts as boxes and gets art only after the space works as gameplay.

## Components

- **level-designer**: Agent with expertise in greyboxing, TileMap, NavMesh, streaming, and environmental storytelling
- **level-design**: Command for greybox planning, tile configuration, nav setup, and zone export
- **level-design-patterns**: Skill library with TileMap code, NavigationRegion3D configuration, level streaming, zone triggers, and CSG greybox workflow

## Quick Start

Plan a dungeon layout:
```
/level-design greybox "dungeon: 5 rooms, 3 corridors, boss chamber at end"
```

Configure TileMap terrain:
```
/level-design tile "2D platformer with grass/dirt/water autotile terrain"
```

Set up NavMesh for AI:
```
/level-design nav "configure NavMesh for humanoid enemies in indoor level"
```
