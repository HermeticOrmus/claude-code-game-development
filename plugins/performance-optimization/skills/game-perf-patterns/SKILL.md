---
name: game-perf-patterns
description: "Game performance patterns: MultiMeshInstance3D batching, a custom performance monitor, a generic object pool, LOD visibility ranges, GDScript hot path optimization, and deferred processing for expensive work. Use when optimizing frame time or memory in a game."
---

# Game Performance Patterns

## MultiMeshInstance3D for Batch Rendering

```gdscript
# Render thousands of identical objects with a single draw call
class_name FoliageRenderer extends Node3D
@export var mesh: Mesh
@export var count: int = 1000
@export var spread_radius: float = 50.0

@onready var multimesh_instance: MultiMeshInstance3D = $MultiMeshInstance3D

func _ready() -> void:
    var multimesh := MultiMesh.new()
    multimesh.mesh = mesh
    multimesh.transform_format = MultiMesh.TRANSFORM_3D
    multimesh.instance_count = count

    for i in count:
        var angle := randf() * TAU
        var radius := randf() * spread_radius
        var pos := Vector3(cos(angle) * radius, 0.0, sin(angle) * radius)
        # Raycast to ground for terrain alignment
        pos.y = _get_ground_height(pos)
        var random_rotation := Basis.from_euler(Vector3(0, randf() * TAU, 0))
        var random_scale := randf_range(0.8, 1.2)
        multimesh.set_instance_transform(i, Transform3D(
            random_rotation.scaled(Vector3.ONE * random_scale),
            pos
        ))

    multimesh_instance.multimesh = multimesh

func _get_ground_height(pos: Vector3) -> float:
    var space := get_world_3d().direct_space_state
    var query := PhysicsRayQueryParameters3D.create(
        pos + Vector3.UP * 100.0,
        pos + Vector3.DOWN * 10.0,
        0b0001  # ground layer
    )
    var result := space.intersect_ray(query)
    return result.position.y if result else 0.0
```

## Custom Performance Monitor

```gdscript
# Add game-specific metrics to Godot's built-in profiler
class_name GameMetrics extends Node
var _enemy_count: int = 0
var _projectile_count: int = 0
var _active_particles: int = 0

func _ready() -> void:
    # Register custom monitors (visible in Godot Profiler > Monitors)
    Performance.add_custom_monitor(
        "game/active_enemies",
        func(): return _enemy_count
    )
    Performance.add_custom_monitor(
        "game/active_projectiles",
        func(): return _projectile_count
    )
    Performance.add_custom_monitor(
        "game/draw_calls",
        func(): return Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
    )
    Performance.add_custom_monitor(
        "game/physics_contacts",
        func(): return Performance.get_monitor(Performance.PHYSICS_3D_COLLISION_PAIRS)
    )

func update_counts(enemies: int, projectiles: int) -> void:
    _enemy_count = enemies
    _projectile_count = projectiles
```

## Object Pool (Generic)

```gdscript
class_name GenericPool extends Node
signal pool_exhausted(requested_type: String)

@export var prefab: PackedScene
@export var initial_size: int = 32
@export var max_size: int = 128
@export var pool_name: String = "unnamed"

var _available: Array[Node] = []
var _active: Array[Node] = []

func _ready() -> void:
    _grow(initial_size)

func acquire() -> Node:
    if _available.is_empty():
        if _active.size() >= max_size:
            pool_exhausted.emit(pool_name)
            return null  # Caller handles null
        _grow(mini(initial_size, max_size - _active.size()))

    var obj := _available.pop_back()
    _active.append(obj)
    obj.show()
    if obj.has_method(&"on_acquired"):
        obj.on_acquired()
    return obj

func release(obj: Node) -> void:
    var idx := _active.find(obj)
    if idx == -1:
        push_warning("Releasing object not in active pool: %s" % obj.name)
        return
    _active.remove_at(idx)
    _available.append(obj)
    obj.hide()
    if obj.has_method(&"on_released"):
        obj.on_released()

func _grow(amount: int) -> void:
    for i in amount:
        var obj := prefab.instantiate()
        add_child(obj)
        obj.hide()
        _available.append(obj)
```

## LOD Visibility Range Configuration

```gdscript
# Configure LOD transitions for a 3D object
@tool
class_name LODSetup extends Node

@export var lod0_end: float = 10.0   # LOD0 visible from 0 to 10m
@export var lod1_end: float = 30.0   # LOD1 visible from 10 to 30m
@export var lod2_end: float = 80.0   # LOD2 visible from 30 to 80m
@export var fade_margin: float = 2.0  # Crossfade distance

func _ready() -> void:
    if Engine.is_editor_hint():
        return
    _configure_lods()

func _configure_lods() -> void:
    var children := get_children().filter(func(c): return c is GeometryInstance3D)
    # Expects children named LOD0, LOD1, LOD2
    for child in children:
        var instance := child as GeometryInstance3D
        match child.name:
            "LOD0":
                instance.visibility_range_begin = 0.0
                instance.visibility_range_end = lod0_end
                instance.visibility_range_end_margin = fade_margin
                instance.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
            "LOD1":
                instance.visibility_range_begin = lod0_end - fade_margin
                instance.visibility_range_end = lod1_end
                instance.visibility_range_end_margin = fade_margin
                instance.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
            "LOD2":
                instance.visibility_range_begin = lod1_end - fade_margin
                instance.visibility_range_end = lod2_end
                instance.visibility_range_end_margin = fade_margin
                instance.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
```

## GDScript Hot Path Optimization

```gdscript
# Before optimization (slow)
func _physics_process(_delta: float) -> void:
    for i in get_child_count():
        var child = get_child(i)  # Variant - dynamic dispatch
        if child.has_method("update_ai"):
            child.call("update_ai", _delta)  # Reflection - slow

# After optimization (fast)
var _ai_agents: Array[AIAgent] = []  # Typed array, populated in _ready()

func _ready() -> void:
    for child in get_children():
        if child is AIAgent:
            _ai_agents.append(child)

func _physics_process(delta: float) -> void:
    for agent in _ai_agents:  # Typed - direct dispatch
        agent.update_ai(delta)  # Direct method call - fast

# Further optimization: skip inactive agents
func _physics_process(delta: float) -> void:
    for agent in _ai_agents:
        if agent.is_active:  # Property check before method call
            agent.update_ai(delta)
```

## Deferred Processing for Expensive Operations

```gdscript
# Spread expensive work across multiple frames
class_name FrameBudgetScheduler extends Node
const BUDGET_MS: float = 2.0  # Spend max 2ms per frame on deferred work

var _work_queue: Array[Callable] = []

func schedule(work: Callable) -> void:
    _work_queue.append(work)

func _process(_delta: float) -> void:
    var start := Time.get_ticks_usec()
    var budget_usec := int(BUDGET_MS * 1000)

    while not _work_queue.is_empty():
        if Time.get_ticks_usec() - start > budget_usec:
            break  # Out of budget, continue next frame
        var work := _work_queue.pop_front()
        work.call()
```

## Anti-Patterns

- **Optimizing without profiling**: "This looks slow" is not a measurement. Profile, then target the measured bottleneck.
- **Instantiate + queue_free every projectile**: Creates GC spikes. Use object pools for anything spawned frequently.
- **Untyped variables in _physics_process**: `var node = get_child(0)` creates Variant lookups each call. Typed arrays + cached references.
- **get_node() in hot loops**: `get_node("../Player")` traverses scene tree every call. Cache in `_ready()` with `@onready`.
- **Draw call per foliage instance**: 1000 grass blades = 1000 draw calls. Use MultiMeshInstance3D = 1 draw call.
