---
name: godot-development
description: "Godot 4 reference patterns: signal-vs-call and physics-body decision tables, resource sharing traps, input handling, a common mistakes catalog, a GDScript to C# rosetta, typed class structure, pooling, autoloads, GUT tests, and collision layer constants. Use when designing, writing, or reviewing Godot 4 code."
---

# Godot development pattern library

Reference patterns for Godot 4 development. Use as lookup when designing or reviewing Godot code.

## Signal vs. direct call decision

| Case | Choose |
|---|---|
| Emitter doesn't know listeners (achievement system, sound manager) | Signal |
| Emitter knows exactly one listener and the relationship is tight | Direct call |
| Multiple listeners with shared interest | Signal |
| Receiver needs to return a value to caller | Direct call |
| Order of execution matters | Direct call (signals are deferred by default) |
| Crossing scene boundaries | Signal (or autoload) |

Convention: signal names are past-tense verbs (`died`, `damaged`, `level_completed`).

## Resource sharing

The trap: `@export var config: ConfigResource` gives every instance the SAME resource. Modifying it affects all instances.

Safe patterns:

```gdscript
# Pattern A: Always duplicate
@onready var my_config: ConfigResource = config.duplicate()

# Pattern B: Make Unique in Inspector
# Right-click resource → Make Unique. Per-scene instance.

# Pattern C: Treat as immutable
# Document + discipline. Never write to config from runtime code.
```

## Input handling matrix

| Source | Use for |
|---|---|
| `Input.is_action_pressed("name")` in `_process` | Continuous input (movement) — but adds 1 frame latency |
| `Input.is_action_just_pressed("name")` in `_process` | One-shot input — same latency caveat |
| `_unhandled_input(event)` with `event.is_action_pressed("name")` | One-shot input with no latency |
| `_input(event)` with `event.is_action_pressed("name")` | Input that should ignore GUI focus |
| `_gui_input(event)` | UI input only (on Control nodes) |

## Physics body decision

| Body | Use when |
|---|---|
| `CharacterBody2D` / `CharacterBody3D` | Player or NPC under direct control |
| `RigidBody2D` / `RigidBody3D` | Object responds to physics forces |
| `RigidBody*` with `freeze_mode = KINEMATIC` | Want physics events but control velocity directly |
| `StaticBody*` | Immovable collider (wall, floor) |
| `AnimatableBody*` | Moving platform — animates but pushes RigidBody correctly |
| `Area2D` / `Area3D` | Trigger volume, no collision response |

## Common mistakes catalog

### "Physics is jittery"

Almost always `_process` instead of `_physics_process`. Variable timestep + physics = drift.

### "Input feels laggy"

`Input.is_action_pressed` in `_process` is one frame behind. For responsive actions, use `_unhandled_input`.

### "Modifying one enemy's HP changes all enemies"

Resource sharing. The HP value is in an `@export`ed `EnemyConfig` resource. Either `.duplicate()` it on `_ready()` or store HP in the Enemy node, not in the resource.

### "Signal fires too late / wrong order"

Signals are deferred (call_deferred semantics) when emitted from physics process. For immediate ordering, direct calls. For correct ordering across signals, use `await`:

```gdscript
emit_signal("event")
await get_tree().process_frame
# Now all listeners have processed
```

### "Camera2D doesn't follow player"

Camera2D needs `enabled = true` and to be a child of the moving body. Or use `set_make_current()` if multiple cameras exist.

### "Autoload script crashes on `get_node`"

Autoloads load before scenes. Getting nodes from a scene that doesn't exist yet fails. Either:
- Use signals for autoload → scene communication
- Defer the `get_node` until after `_ready()`

### "Scene I instantiated has wrong values"

You instantiated from a PackedScene resource. Edits to one instance don't affect the PackedScene. Conversely, edits to the PackedScene affect all future instances but not existing ones.

### "C# script doesn't see GDScript class"

GDScript classes are not visible to C# (and vice versa) until you use `class_name` for GDScript and the class is exported. Cross-language work requires explicit interfaces.

## Animation pattern card

| System | Use for |
|---|---|
| `AnimationPlayer` | Cutscenes, simple state transitions, UI animations |
| `AnimationTree` + `AnimationNodeStateMachine` | Character gameplay state (idle/walk/run/jump) |
| `AnimationTree` + `AnimationNodeBlendTree` | Blended animations (walk-aim with separate body parts) |
| `AnimationTree` + `AnimationNodeBlendSpace2D` | Directional blends (8-way walking) |
| `Tween` | UI transitions only (not characters) |

## GDScript ↔ C# rosetta

| GDScript | C# |
|---|---|
| `extends Node2D` | `: Node2D` (class declaration) |
| `@export var hp := 100` | `[Export] public int Hp = 100;` |
| `signal died` | `[Signal] public delegate void DiedEventHandler();` |
| `@onready var sprite = $Sprite2D` | Get in `_Ready()`: `_sprite = GetNode<Sprite2D>("Sprite2D");` |
| `func _ready():` | `public override void _Ready()` |
| `func _physics_process(delta):` | `public override void _PhysicsProcess(double delta)` |
| `await get_tree().process_frame` | `await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);` |

## Project structure conventions

```
res://
├── scenes/        # PackedScene files (.tscn)
├── scripts/       # GDScript and C# files
├── resources/     # Custom Resources (configs, themes)
├── assets/        # Art, audio, fonts
│   ├── sprites/
│   ├── audio/
│   ├── fonts/
│   └── shaders/
├── autoloads/     # Singleton scripts (Project Settings → Autoload)
└── addons/        # Editor plugins
```

## Performance reference card

| Issue | Cost | Fix |
|---|---|---|
| Many `_process` scripts | Each is a method call per frame | Consolidate or use signal-driven updates |
| Many `_physics_process` scripts | Each is a method call per physics tick | Same as above |
| Drawing many sprites | Each is a draw call | MultiMeshInstance2D for repeated identical sprites |
| Many small Area2D | Each does a physics query | Combine queries; use raycast for one-shot |
| GDScript heavy loop | GDScript is interpreted | Move hot loop to C# or use bulk operations |
| String concatenation in loop | Allocates new String each time | StringBuilder pattern with PackedStringArray + join |

## Typed GDScript Class Structure

```gdscript
class_name PlayerCharacter extends CharacterBody3D
## Player character controller with movement and combat.
## Requires: CollisionShape3D child, AnimationTree child

signal died
signal health_changed(old_health: float, new_health: float)

const SPEED: float = 6.0
const JUMP_VELOCITY: float = 5.5
const GRAVITY: float = 9.8

@export var max_health: float = 100.0
@export var weapon_data: WeaponData  # Resource reference

@onready var animation_tree: AnimationTree = $AnimationTree
@onready var weapon_pivot: Node3D = $WeaponPivot
@onready var health_bar: ProgressBar = %HealthBar  # % = unique name shortcut

var _current_health: float
var _is_dead: bool = false

func _ready() -> void:
    _current_health = max_health
    animation_tree.active = true

func _physics_process(delta: float) -> void:
    if _is_dead:
        return
    _handle_gravity(delta)
    _handle_movement()
    move_and_slide()

func take_damage(amount: float) -> void:
    if _is_dead:
        return
    var old_health := _current_health
    _current_health = maxf(0.0, _current_health - amount)
    health_changed.emit(old_health, _current_health)
    if _current_health <= 0.0:
        _die()

func _die() -> void:
    _is_dead = true
    set_physics_process(false)  # Stop physics checks, cheaper than bool guard
    died.emit()

func _handle_gravity(delta: float) -> void:
    if not is_on_floor():
        velocity.y -= GRAVITY * delta

func _handle_movement() -> void:
    var input_dir := Input.get_vector(
        &"move_left", &"move_right", &"move_forward", &"move_back"
    )
    var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    if direction:
        velocity.x = direction.x * SPEED
        velocity.z = direction.z * SPEED
    else:
        velocity.x = move_toward(velocity.x, 0, SPEED)
        velocity.z = move_toward(velocity.z, 0, SPEED)
```

## Scene Inheritance Pattern

```gdscript
# Base scene: Enemy.tscn with Enemy.gd
class_name Enemy extends CharacterBody3D
@export var move_speed: float = 3.0
@export var health: float = 50.0

func _ready() -> void:
    _setup()

func _setup() -> void:
    pass  # Override in subclasses

func attack(target: Node3D) -> void:
    pass  # Override in subclasses

# Inherited scene: GoblinEnemy.tscn extends Enemy.tscn
class_name GoblinEnemy extends Enemy

func _setup() -> void:
    move_speed = 4.0  # Goblins are faster
    health = 30.0

func attack(target: Node3D) -> void:
    # Goblin-specific attack logic
    pass
```

## Autoload Singleton (correct usage)

```gdscript
# res://autoloads/GameManager.gd
# Added in Project Settings > Autoloads as "GameManager"
class_name GameManager extends Node
# Correct uses for Autoloads:
# - Global event bus
# - Save system
# - Audio manager
# - Input rebinding
# WRONG uses: player state, enemy state, level data (use scene nodes instead)

signal scene_changed(scene_name: StringName)

var current_scene: StringName = &""
var _score: int = 0

func change_scene(scene_path: String) -> void:
    current_scene = scene_path.get_file().get_basename() as StringName
    get_tree().change_scene_to_file(scene_path)
    scene_changed.emit(current_scene)

func add_score(points: int) -> void:
    _score += points
```

## PackedScene Pooling

```gdscript
# Object pool for frequently spawned scenes (bullets, particles, enemies)
class_name ScenePool extends Node
@export var scene: PackedScene
@export var initial_size: int = 20

var _pool: Array[Node] = []

func _ready() -> void:
    for i in initial_size:
        _create_instance()

func _create_instance() -> Node:
    var instance := scene.instantiate()
    add_child(instance)
    instance.hide()
    _pool.append(instance)
    return instance

func acquire() -> Node:
    for instance in _pool:
        if not instance.visible:
            instance.show()
            return instance
    # Pool exhausted: grow it
    var new_instance := _create_instance()
    new_instance.show()
    return new_instance

func release(instance: Node) -> void:
    instance.hide()
    # Reset state - position, velocity, etc.
    if instance.has_method(&"reset"):
        instance.reset()
```

## Signal-Based Component Communication

```gdscript
# Loose coupling: HealthComponent emits, HUDComponent receives
# No direct reference between gameplay and UI

# In HealthComponent:
class_name HealthComponent extends Node
signal health_changed(ratio: float)  # 0.0 to 1.0
signal died

@export var max_health: float = 100.0
var _hp: float

func _ready() -> void:
    _hp = max_health

func damage(amount: float) -> void:
    _hp = maxf(0.0, _hp - amount)
    health_changed.emit(_hp / max_health)
    if _hp <= 0.0:
        died.emit()

# In scene setup (via editor or code):
# $HealthComponent.health_changed.connect($HUD/HealthBar.set_value)
# $HealthComponent.died.connect(_on_player_died)
```

## GUT Unit Test Structure

```gdscript
# test/test_health_component.gd
extends GutTest

var _health: HealthComponent
var _signals_watched: bool = false

func before_each() -> void:
    _health = HealthComponent.new()
    _health.max_health = 100.0
    add_child_autofree(_health)
    watch_signals(_health)

func test_starts_at_full_health() -> void:
    assert_eq(_health._hp, 100.0, "Health should start at max")

func test_damage_reduces_health() -> void:
    _health.damage(30.0)
    assert_eq(_health._hp, 70.0, "Health should be 70 after 30 damage")

func test_damage_emits_health_changed() -> void:
    _health.damage(50.0)
    assert_signal_emitted(_health, "health_changed")

func test_lethal_damage_emits_died() -> void:
    _health.damage(200.0)
    assert_signal_emitted(_health, "died")
    assert_eq(_health._hp, 0.0, "Health should not go below 0")

func test_overkill_does_not_underflow() -> void:
    _health.damage(999.0)
    assert_gte(_health._hp, 0.0, "Health should never be negative")
```

## Collision Layer Constants

```gdscript
# Define collision layers as constants to avoid magic numbers
# Project Settings > Layer Names defines names, but constants help in code
class_name CollisionLayers
const WORLD: int      = 1 << 0  # Layer 1: static terrain, walls
const PLAYER: int     = 1 << 1  # Layer 2: player character
const ENEMY: int      = 1 << 2  # Layer 3: enemy characters
const PROJECTILE: int = 1 << 3  # Layer 4: bullets, arrows
const TRIGGER: int    = 1 << 4  # Layer 5: Area3D triggers (checkpoints, pickups)
const INTERACTABLE: int = 1 << 5  # Layer 6: doors, levers, NPCs

# Usage:
# raycast.collision_mask = CollisionLayers.WORLD | CollisionLayers.ENEMY
# area3d.collision_layer = CollisionLayers.TRIGGER
# area3d.collision_mask = CollisionLayers.PLAYER
```

## Anti-Patterns

- **Untyped variables in hot paths**: `var node = $Child` is Variant. Use `var node: Enemy = $Child`. Variant dispatch is 2-3x slower.
- **`get_node()` with absolute paths**: `/root/Main/World/Player` breaks when scene structure changes. Use @onready, signals, or Service Locator.
- **Autoload for everything**: Autoloads are global singletons. Only use for truly global systems. Don't put Player into an Autoload.
- **`queue_free()` then access**: After `queue_free()`, node is still alive until end of frame. Check `is_instance_valid(node)` before accessing.
- **`_ready()` ordering assumption**: Child `_ready()` runs before parent. Never assume parent is ready in child's `_ready()`. Use signals.

## Cross-references

- See `docs/02-core-game-concepts/` for game loop fundamentals
- See `docs/03-graphics-rendering/` for shader and particle patterns
- See `docs/06-networking-multiplayer/` for Godot's high-level multiplayer API
- See `docs/10-performance-optimization/` for profiling and frame-budget patterns
