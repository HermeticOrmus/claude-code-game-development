---
name: game-arch-patterns
description: "Game architecture code patterns: a fixed timestep loop with accumulator, an EventBus, ECS-style composition in Godot, Resource-based game data, an autoload service locator, and a game state stack. Use when laying out the core structure of a game or untangling one that has grown messy."
---

# Game Architecture Patterns

## Fixed Timestep Game Loop with Accumulator

```gdscript
# Fixed physics timestep decoupled from variable render rate
# Based on Glenn Fiedler's "Fix Your Timestep!" (2004)
class_name GameLoop extends Node
const PHYSICS_DELTA: float = 1.0 / 60.0  # Fixed 60Hz physics
const MAX_DELTA: float = 0.25            # Spiral-of-death prevention

var _accumulator: float = 0.0
var _previous_time: float = 0.0
var _alpha: float = 0.0  # Interpolation factor for rendering

func _ready() -> void:
    _previous_time = Time.get_ticks_msec() / 1000.0

func _process(_delta: float) -> void:
    var current_time := Time.get_ticks_msec() / 1000.0
    var frame_time := min(current_time - _previous_time, MAX_DELTA)
    _previous_time = current_time
    _accumulator += frame_time

    # Fixed timestep physics integration
    while _accumulator >= PHYSICS_DELTA:
        _physics_step(PHYSICS_DELTA)
        _accumulator -= PHYSICS_DELTA

    # Render interpolation between previous and current state
    _alpha = _accumulator / PHYSICS_DELTA
    _render(_alpha)

func _physics_step(delta: float) -> void:
    # Deterministic physics: same delta every time
    pass

func _render(alpha: float) -> void:
    # Interpolate render positions between previous_state and current_state
    # position = lerp(previous_position, current_position, alpha)
    pass
# Note: Godot's built-in _physics_process IS a fixed timestep loop.
# Use _physics_process for physics, _process for visual interpolation.
```

## EventBus (Decoupled Signal System)

```gdscript
# Global EventBus autoload - replaces Singleton coupling
# Add as autoload: EventBus -> res://systems/event_bus.gd
class_name EventBus extends Node

# Typed event signals - define all game events here
signal player_died(player_id: int)
signal enemy_spawned(enemy: Node, position: Vector3)
signal item_collected(item_id: StringName, player_id: int)
signal level_completed(level_id: int, score: int)
signal health_changed(entity_id: int, old_health: float, new_health: float)
signal game_state_changed(old_state: int, new_state: int)

# Usage from any script (no direct reference needed):
# EventBus.player_died.emit(player.id)
# EventBus.player_died.connect(_on_player_died)
```

```gdscript
# Resource-as-event-channel pattern (decentralized, typed)
class_name GameEvent extends Resource
signal triggered(data: Dictionary)

func trigger(data: Dictionary = {}) -> void:
    triggered.emit(data)

# Usage: create GameEvent Resources in editor, reference by @export
# Emitter:  player_died_event.trigger({"player_id": id})
# Receiver: player_died_event.triggered.connect(_on_player_died)
```

## ECS Approximation in Godot (Composition Pattern)

```gdscript
# Godot uses scene tree composition, not true ECS.
# Approximate ECS with component nodes.

# "Entity" = CharacterBody3D with component children
# Node: Player (CharacterBody3D)
#   ChildNode: HealthComponent
#   ChildNode: MovementComponent
#   ChildNode: WeaponComponent
#   ChildNode: InputComponent

class_name HealthComponent extends Node
signal died(entity: Node)
signal health_changed(old_val: float, new_val: float)

@export var max_health: float = 100.0
var current_health: float:
    get: return _current_health
    set(value):
        var old := _current_health
        _current_health = clamp(value, 0.0, max_health)
        health_changed.emit(old, _current_health)
        if _current_health <= 0.0:
            died.emit(get_parent())

var _current_health: float

func _ready() -> void:
    _current_health = max_health

func take_damage(amount: float) -> void:
    current_health -= amount

func heal(amount: float) -> void:
    current_health += amount
```

## Resource-Based Game Data (ScriptableObject Equivalent)

```gdscript
# Data container as Resource - store in .tres files
class_name WeaponData extends Resource
@export var weapon_name: String
@export var damage: float = 10.0
@export var fire_rate: float = 0.5         # shots per second
@export var projectile_speed: float = 30.0
@export var ammo_capacity: int = 30
@export var reload_time: float = 1.5
@export var projectile_scene: PackedScene
@export var fire_sound: AudioStream
@export var weapon_icon: Texture2D

# Use in weapon script:
# @export var weapon_data: WeaponData
# var damage := weapon_data.damage
```

## Service Locator (Autoload Pattern)

```gdscript
# Services autoload - controlled global access
# Avoids direct cross-singleton coupling
class_name Services extends Node
var _registry: Dictionary = {}

func register(service_name: StringName, service: Object) -> void:
    _registry[service_name] = service

func get_service(service_name: StringName) -> Object:
    if service_name in _registry:
        return _registry[service_name]
    push_error("Service not registered: %s" % service_name)
    return null

# Null service pattern: register no-op service at startup
func register_null_service(service_name: StringName, null_service: Object) -> void:
    if service_name not in _registry:
        _registry[service_name] = null_service

# Usage:
# Services.register(&"AudioManager", $AudioManager)
# var audio: AudioManager = Services.get_service(&"AudioManager")
```

## Game State Stack

```gdscript
class_name GameStateStack extends Node
enum GameState { GAMEPLAY, PAUSE, INVENTORY, DIALOGUE, GAME_OVER, MAIN_MENU }

var _state_stack: Array[GameState] = []
signal state_changed(new_state: GameState, old_state: GameState)

func push_state(state: GameState) -> void:
    var old := current_state()
    _state_stack.push_back(state)
    _on_state_enter(state)
    state_changed.emit(state, old)

func pop_state() -> void:
    if _state_stack.is_empty():
        return
    var old := _state_stack.pop_back()
    _on_state_exit(old)
    if not _state_stack.is_empty():
        state_changed.emit(current_state(), old)

func current_state() -> GameState:
    return _state_stack.back() if not _state_stack.is_empty() else GameState.MAIN_MENU

func _on_state_enter(state: GameState) -> void:
    match state:
        GameState.PAUSE:
            get_tree().paused = true
            EventBus.game_state_changed.emit(GameState.GAMEPLAY, GameState.PAUSE)
        GameState.GAMEPLAY:
            get_tree().paused = false

func _on_state_exit(state: GameState) -> void:
    match state:
        GameState.PAUSE:
            get_tree().paused = false
```

## Anti-Patterns

- **God object / God scene**: Single 2000-line script managing everything. Decompose into component nodes with single responsibilities.
- **Everything as Autoload**: Autoloads (singletons) create hidden global state. Use them only for truly global systems (AudioManager, SaveSystem, EventBus). Not for gameplay objects.
- **Signals with too many parameters**: If a signal needs 6+ parameters, the event carries too much data. Use a typed data class/dictionary payload instead.
- **Direct scene path strings**: `get_node("/root/Game/Player/Health")` breaks if scene structure changes. Use @onready, signals, or the Service Locator.
- **Variable timestep physics**: Never use `_process(delta)` for physics simulation. Non-deterministic, framerate-dependent behavior. Use `_physics_process(delta)`.
