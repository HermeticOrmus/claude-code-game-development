---
name: procgen-patterns
description: "Procedural generation code: FastNoiseLite terrain, a BSP dungeon generator, a cellular automata cave generator, a seeded room populator, and a solvability validator. Use when implementing or debugging procedural levels."
---

# Procgen Patterns

## FastNoiseLite Terrain Generation

```gdscript
# Layered noise terrain heightmap - Godot 4
class_name TerrainGenerator extends Node
@export var width: int = 128
@export var height: int = 128
@export var seed: int = 0

@export var base_frequency: float = 0.01
@export var octaves: int = 5
@export var lacunarity: float = 2.0  # Frequency multiplier per octave
@export var gain: float = 0.5        # Amplitude multiplier per octave

func generate_heightmap() -> Image:
    var noise := FastNoiseLite.new()
    noise.noise_type = FastNoiseLite.TYPE_SIMPLEX
    noise.fractal_type = FastNoiseLite.FRACTAL_FBM
    noise.seed = seed
    noise.frequency = base_frequency
    noise.fractal_octaves = octaves
    noise.fractal_lacunarity = lacunarity
    noise.fractal_gain = gain

    var img := Image.create(width, height, false, Image.FORMAT_R8)
    for y in height:
        for x in width:
            var value := (noise.get_noise_2d(x, y) + 1.0) * 0.5  # Normalize to [0,1]
            img.set_pixel(x, y, Color(value, 0, 0))
    return img

func sample_height(world_pos: Vector2) -> float:
    # Used at runtime for placing objects at correct heights
    var noise := FastNoiseLite.new()
    noise.seed = seed
    noise.frequency = base_frequency
    return (noise.get_noise_2d(world_pos.x, world_pos.y) + 1.0) * 0.5
```

## BSP Dungeon Generator

```gdscript
# Binary Space Partitioning dungeon - produces structured room layouts
class_name BSPDungeon extends RefCounted

class BSPNode:
    var rect: Rect2i
    var left: BSPNode
    var right: BSPNode
    var room: Rect2i  # Only set on leaf nodes

    func _init(r: Rect2i) -> void:
        rect = r

const MIN_LEAF_SIZE := 10
const MIN_ROOM_SIZE := 4

var _rng: RandomNumberGenerator
var _rooms: Array[Rect2i] = []
var _corridors: Array[Array] = []  # Array of [Vector2i, Vector2i] pairs

func generate(bounds: Rect2i, seed: int) -> void:
    _rng = RandomNumberGenerator.new()
    _rng.seed = seed
    _rooms.clear()
    _corridors.clear()

    var root := BSPNode.new(bounds)
    _split(root, 0)
    _create_rooms(root)
    _connect_rooms(root)

func _split(node: BSPNode, depth: int) -> void:
    if depth > 5:
        return
    var split_horizontal := _rng.randi() % 2 == 0
    var min_size := MIN_LEAF_SIZE * 2
    if node.rect.size.x < min_size and node.rect.size.y < min_size:
        return  # Too small to split

    if node.rect.size.x > node.rect.size.y:
        split_horizontal = false  # Force vertical split for wide nodes

    var split_pos: int
    if split_horizontal:
        split_pos = _rng.randi_range(MIN_LEAF_SIZE, node.rect.size.y - MIN_LEAF_SIZE)
        node.left = BSPNode.new(Rect2i(node.rect.position, Vector2i(node.rect.size.x, split_pos)))
        node.right = BSPNode.new(Rect2i(
            node.rect.position + Vector2i(0, split_pos),
            Vector2i(node.rect.size.x, node.rect.size.y - split_pos)
        ))
    else:
        split_pos = _rng.randi_range(MIN_LEAF_SIZE, node.rect.size.x - MIN_LEAF_SIZE)
        node.left = BSPNode.new(Rect2i(node.rect.position, Vector2i(split_pos, node.rect.size.y)))
        node.right = BSPNode.new(Rect2i(
            node.rect.position + Vector2i(split_pos, 0),
            Vector2i(node.rect.size.x - split_pos, node.rect.size.y)
        ))

    _split(node.left, depth + 1)
    _split(node.right, depth + 1)

func _create_rooms(node: BSPNode) -> void:
    if node.left == null and node.right == null:
        # Leaf: create a room with padding
        var padding := 1
        var max_w := node.rect.size.x - padding * 2
        var max_h := node.rect.size.y - padding * 2
        if max_w < MIN_ROOM_SIZE or max_h < MIN_ROOM_SIZE:
            return
        var w := _rng.randi_range(MIN_ROOM_SIZE, max_w)
        var h := _rng.randi_range(MIN_ROOM_SIZE, max_h)
        var x := node.rect.position.x + padding + _rng.randi_range(0, max_w - w)
        var y := node.rect.position.y + padding + _rng.randi_range(0, max_h - h)
        node.room = Rect2i(x, y, w, h)
        _rooms.append(node.room)
        return
    if node.left:
        _create_rooms(node.left)
    if node.right:
        _create_rooms(node.right)

func _connect_rooms(node: BSPNode) -> void:
    if node.left == null or node.right == null:
        return
    var left_room := _get_room(node.left)
    var right_room := _get_room(node.right)
    if left_room != Rect2i() and right_room != Rect2i():
        var start := left_room.get_center()
        var end := right_room.get_center()
        _corridors.append([start, end])  # L-shaped corridor between centers
    _connect_rooms(node.left)
    _connect_rooms(node.right)

func _get_room(node: BSPNode) -> Rect2i:
    if node.room != Rect2i():
        return node.room
    var left_room := Rect2i()
    var right_room := Rect2i()
    if node.left:
        left_room = _get_room(node.left)
    if node.right:
        right_room = _get_room(node.right)
    if left_room == Rect2i():
        return right_room
    return left_room

func get_rooms() -> Array[Rect2i]:
    return _rooms
```

## Cellular Automata Cave Generator

```gdscript
# Cave generation using cellular automata smoothing
class_name CaveGenerator extends RefCounted
# true = wall, false = floor

@export var width: int = 80
@export var height: int = 50
@export var fill_probability: float = 0.45  # Initial wall density
@export var smoothing_iterations: int = 5
@export var birth_limit: int = 5   # Neighbors to become wall
@export var death_limit: int = 4   # Neighbors to stay wall

func generate(seed: int) -> Array:
    var rng := RandomNumberGenerator.new()
    rng.seed = seed

    # Initialize with random walls
    var grid: Array = []
    for y in height:
        var row: Array = []
        for x in width:
            # Border is always wall
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                row.append(true)
            else:
                row.append(rng.randf() < fill_probability)
        grid.append(row)

    # Smooth with CA rules
    for _i in smoothing_iterations:
        grid = _smooth_pass(grid)

    return grid

func _smooth_pass(grid: Array) -> Array:
    var new_grid: Array = []
    for y in height:
        var row: Array = []
        for x in width:
            var neighbors := _count_wall_neighbors(grid, x, y)
            if grid[y][x]:  # Currently a wall
                row.append(neighbors >= death_limit)
            else:  # Currently floor
                row.append(neighbors > birth_limit)
        new_grid.append(row)
    return new_grid

func _count_wall_neighbors(grid: Array, cx: int, cy: int) -> int:
    var count := 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            var nx := cx + dx
            var ny := cy + dy
            if nx < 0 or ny < 0 or nx >= width or ny >= height:
                count += 1  # Out of bounds = wall
            elif grid[ny][nx]:
                count += 1
    return count
```

## Seeded Room Populator

```gdscript
# Deterministic content placement using derived seeds
class_name RoomPopulator extends RefCounted

func populate_room(room: Rect2i, world_seed: int, room_index: int, difficulty: float) -> Dictionary:
    # Derive a unique seed for this specific room - same world + room always = same content
    var room_seed: int = hash("%d_%d" % [world_seed, room_index])
    var rng := RandomNumberGenerator.new()
    rng.seed = room_seed

    var enemies: Array[Vector2i] = []
    var items: Array[Dictionary] = []

    # Scale enemy count with difficulty (0.0 = easy, 1.0 = hard)
    var enemy_count := roundi(lerp(1.0, 5.0, difficulty))
    for _i in enemy_count:
        enemies.append(_random_floor_pos(room, rng))

    # Items: always at least one if room is large enough
    if room.size.x * room.size.y > 25:
        items.append({
            "type": _pick_weighted(["health", "ammo", "key"], [0.5, 0.4, 0.1], rng),
            "position": _random_floor_pos(room, rng),
        })

    return {"enemies": enemies, "items": items}

func _random_floor_pos(room: Rect2i, rng: RandomNumberGenerator) -> Vector2i:
    return Vector2i(
        rng.randi_range(room.position.x + 1, room.position.x + room.size.x - 2),
        rng.randi_range(room.position.y + 1, room.position.y + room.size.y - 2)
    )

func _pick_weighted(options: Array, weights: Array[float], rng: RandomNumberGenerator) -> String:
    var total := weights.reduce(func(acc, w): return acc + w, 0.0)
    var roll := rng.randf() * total
    var cumulative := 0.0
    for i in options.size():
        cumulative += weights[i]
        if roll <= cumulative:
            return options[i]
    return options[-1]
```

## Solvability Validator

```gdscript
# BFS flood fill to confirm dungeon has path from start to exit
class_name DungeonValidator extends RefCounted

func is_solvable(grid: Array, start: Vector2i, exit: Vector2i) -> bool:
    var visited: Dictionary = {}
    var queue: Array[Vector2i] = [start]
    visited[start] = true

    while not queue.is_empty():
        var current := queue.pop_front() as Vector2i
        if current == exit:
            return true
        for neighbor in _get_neighbors(current, grid):
            if neighbor not in visited:
                visited[neighbor] = true
                queue.append(neighbor)
    return false

func _get_neighbors(pos: Vector2i, grid: Array) -> Array[Vector2i]:
    var neighbors: Array[Vector2i] = []
    for dir in [Vector2i(1,0), Vector2i(-1,0), Vector2i(0,1), Vector2i(0,-1)]:
        var n := pos + dir
        if n.y >= 0 and n.y < grid.size() and n.x >= 0 and n.x < grid[0].size():
            if not grid[n.y][n.x]:  # Not a wall
                neighbors.append(n)
    return neighbors
```

## Anti-Patterns

- **Global randf() in procgen**: Non-seeded calls break reproducibility. Any call to `randf()`, `randi()`, `randf_range()` without an explicit `RandomNumberGenerator` makes levels non-deterministic.
- **No solvability check**: Always run flood fill from start to exit before exposing generated level to player. Return a new seed and retry if unsolvable.
- **Generating on main thread**: BSP with deep recursion or CA with many iterations can spike frame time. Use `Thread` or `WorkerThreadPool.add_task()`.
- **Magic number tile IDs**: `if tile == 3` is unmaintainable. Define an enum or const: `const FLOOR := 0; const WALL := 1`.
- **WFC without backtracking**: WFC can reach contradictions. Without backtracking or restart, the algorithm produces broken output silently. Detect contradiction (empty option set) and restart with different seed.
