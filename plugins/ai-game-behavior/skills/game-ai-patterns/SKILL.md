---
name: game-ai-patterns
description: "Game AI code patterns: behavior tree node types, FSM transition tables, utility AI consideration curves, GOAP action definitions, Godot NavMesh agent setup, and field-of-view sensing. Use when writing or reviewing NPC decision-making, pathfinding, or perception code."
---

# Game AI Patterns

## Behavior Tree Node Types

### Composite Nodes
```gdscript
# Sequence: all children must succeed (AND)
# Returns FAILURE on first child failure, SUCCESS if all succeed
class_name BTSequence extends BTComposite
func _tick(delta: float) -> Status:
    for child in children:
        var status := child.tick(delta)
        if status != Status.SUCCESS:
            return status  # FAILURE or RUNNING propagates up
    return Status.SUCCESS

# Selector: first child to succeed wins (OR)
# Returns SUCCESS on first child success, FAILURE if all fail
class_name BTSelector extends BTComposite
func _tick(delta: float) -> Status:
    for child in children:
        var status := child.tick(delta)
        if status != Status.FAILURE:
            return status  # SUCCESS or RUNNING propagates up
    return Status.FAILURE

# Parallel: runs all children simultaneously
# succeeds when N children succeed (default: all)
class_name BTParallel extends BTComposite
@export var success_threshold: int = -1  # -1 = all children
func _tick(delta: float) -> Status:
    var success_count := 0
    var threshold := success_threshold if success_threshold > 0 else children.size()
    for child in children:
        var status := child.tick(delta)
        if status == Status.SUCCESS:
            success_count += 1
    return Status.SUCCESS if success_count >= threshold else Status.RUNNING
```

### Decorator Nodes
```gdscript
# Inverter: flips SUCCESS <-> FAILURE
class_name BTInverter extends BTDecorator
func _tick(delta: float) -> Status:
    match child.tick(delta):
        Status.SUCCESS: return Status.FAILURE
        Status.FAILURE: return Status.SUCCESS
        _: return Status.RUNNING

# Cooldown: prevents child from running more than once per interval
class_name BTCooldown extends BTDecorator
@export var cooldown_time: float = 2.0
var _last_success_time: float = -INF
func _tick(delta: float) -> Status:
    if Time.get_ticks_msec() / 1000.0 - _last_success_time < cooldown_time:
        return Status.FAILURE
    var status := child.tick(delta)
    if status == Status.SUCCESS:
        _last_success_time = Time.get_ticks_msec() / 1000.0
    return status
```

### Blackboard Pattern
```gdscript
# Typed blackboard - define schema explicitly
class_name AIBlackboard extends Resource
@export var target: Node3D
@export var last_known_position: Vector3
@export var health_ratio: float
@export var alert_level: float  # 0=unaware, 1=fully alerted
@export var cover_node: Node3D
@export var can_see_player: bool
@export var time_since_last_seen: float

# Blackboard condition decorator
class_name BTCheckBlackboard extends BTDecorator
@export var key: StringName
@export var operator: StringName = &"greater_than"
@export var value: float
func _tick(delta: float) -> Status:
    var bb_value: float = blackboard.get(key)
    var passes := match_condition(bb_value, operator, value)
    return child.tick(delta) if passes else Status.FAILURE
```

## FSM Transition Table Design

```gdscript
# Data-driven FSM using transition table
class_name StateMachine extends Node
enum State { IDLE, PATROL, INVESTIGATE, ALERT, ATTACK, FLEE, DEAD }
enum Event { SAW_PLAYER, LOST_PLAYER, HEARD_NOISE, TOOK_DAMAGE, LOW_HEALTH, ENEMY_DEAD, TIMEOUT }

# Transition table: [current_state][event] = [action_func, next_state]
const TRANSITIONS: Dictionary = {
    State.PATROL: {
        Event.SAW_PLAYER:   [&"_on_enter_alert",   State.ALERT],
        Event.HEARD_NOISE:  [&"_on_enter_investigate", State.INVESTIGATE],
        Event.TOOK_DAMAGE:  [&"_on_enter_alert",   State.ALERT],
    },
    State.ALERT: {
        Event.SAW_PLAYER:   [&"_on_enter_attack",  State.ATTACK],
        Event.LOST_PLAYER:  [&"_on_enter_investigate", State.INVESTIGATE],
        Event.TIMEOUT:      [&"_on_enter_patrol",  State.PATROL],
    },
    State.ATTACK: {
        Event.LOST_PLAYER:  [&"_on_enter_alert",   State.ALERT],
        Event.LOW_HEALTH:   [&"_on_enter_flee",    State.FLEE],
        Event.TOOK_DAMAGE:  [null,                 State.ATTACK],  # stay, no action
    },
}

var current_state: State = State.PATROL

func send_event(event: Event) -> void:
    if current_state not in TRANSITIONS:
        return
    if event not in TRANSITIONS[current_state]:
        return
    var transition: Array = TRANSITIONS[current_state][event]
    var action: StringName = transition[0]
    var next_state: State = transition[1]
    if action:
        call(action)
    current_state = next_state
```

## Utility AI Consideration Curves

```gdscript
# Response curve types for normalizing raw inputs to [0,1]
class_name UtilityResponseCurve
enum CurveType { LINEAR, EXPONENTIAL, LOGISTIC, INVERSE_LOGISTIC }

static func evaluate(x: float, type: CurveType, m: float = 1.0, k: float = 1.0, b: float = 0.0, c: float = 0.0) -> float:
    # m=slope/shape, k=exponent, b=y-shift, c=x-shift
    match type:
        CurveType.LINEAR:
            return clamp(m * x + b, 0.0, 1.0)
        CurveType.EXPONENTIAL:
            return clamp(m * pow(x - c, k) + b, 0.0, 1.0)
        CurveType.LOGISTIC:
            # S-curve: slow at extremes, fast in middle
            return 1.0 / (1.0 + exp(-k * (x - 0.5)))
        CurveType.INVERSE_LOGISTIC:
            return 1.0 - (1.0 / (1.0 + exp(-k * (x - 0.5))))
    return 0.0

# Action scorer using geometric mean (avoids zero-kill from one bad consideration)
class_name UtilityAction extends Resource
@export var action_name: StringName
@export var considerations: Array[UtilityConsideration]

func score(context: AIContext) -> float:
    if considerations.is_empty():
        return 0.0
    var product := 1.0
    for consideration in considerations:
        var raw := consideration.evaluate(context)
        var normalized := consideration.curve.evaluate(raw)
        product *= normalized
    # Compensation factor: geometric mean instead of raw product
    var compensation := 1.0 - (1.0 / considerations.size())
    var modified := 1.0 - product
    return product + (modified * compensation * product)
```

## GOAP Action Definition

```gdscript
# GOAP world state as typed dictionary
class_name GOAPWorldState
var state: Dictionary = {
    &"target_dead": false,
    &"has_weapon": true,
    &"weapon_loaded": true,
    &"in_cover": false,
    &"near_target": false,
    &"low_health": false,
}

# GOAP action with preconditions, effects, cost
class_name GOAPAction extends Resource
@export var action_name: StringName
@export var cost: float = 1.0
var preconditions: Dictionary  # required world state
var effects: Dictionary        # changes after action completes

class MoveToTargetAction extends GOAPAction:
    func _init() -> void:
        action_name = &"MoveToTarget"
        cost = 2.0
        preconditions = {}
        effects = { &"near_target": true }

class AttackTargetAction extends GOAPAction:
    func _init() -> void:
        action_name = &"AttackTarget"
        cost = 1.0
        preconditions = { &"near_target": true, &"weapon_loaded": true, &"has_weapon": true }
        effects = { &"target_dead": true }

class ReloadAction extends GOAPAction:
    func _init() -> void:
        action_name = &"Reload"
        cost = 1.5
        preconditions = { &"has_weapon": true }
        effects = { &"weapon_loaded": true }
```

## NavMesh Agent Configuration (Godot)

```gdscript
# NavigationAgent3D setup for NPC
class_name NPCMovement extends Node
@onready var nav_agent: NavigationAgent3D = $NavigationAgent3D
@onready var character: CharacterBody3D = get_parent()

func _ready() -> void:
    nav_agent.path_desired_distance = 0.5      # close enough to waypoint
    nav_agent.target_desired_distance = 1.0    # close enough to destination
    nav_agent.path_max_distance = 3.0          # recalculate if deviated this far
    nav_agent.avoidance_enabled = true
    nav_agent.radius = 0.5
    nav_agent.max_speed = 4.0
    nav_agent.velocity_computed.connect(_on_velocity_computed)

func move_to(target_position: Vector3) -> void:
    nav_agent.target_position = target_position

func _physics_process(delta: float) -> void:
    if nav_agent.is_navigation_finished():
        return
    var next_pos := nav_agent.get_next_path_position()
    var direction := character.global_position.direction_to(next_pos)
    nav_agent.velocity = direction * nav_agent.max_speed

func _on_velocity_computed(safe_velocity: Vector3) -> void:
    # RVO2 avoidance modifies velocity, apply to character
    character.velocity = safe_velocity
    character.move_and_slide()
```

## Field of View Sensing

```gdscript
class_name VisionSensor extends Node3D
@export var fov_angle_degrees: float = 90.0
@export var max_range: float = 20.0
@export var detection_layers: int = 0b0011  # physics layers for raycast

var _cos_half_fov: float

func _ready() -> void:
    _cos_half_fov = cos(deg_to_rad(fov_angle_degrees * 0.5))

func can_see(target: Node3D) -> bool:
    var to_target := target.global_position - global_position
    var distance := to_target.length()
    if distance > max_range:
        return false
    # Angle check using dot product
    var direction := to_target.normalized()
    var dot := global_transform.basis.z.dot(-direction)  # -Z is forward in Godot
    if dot < _cos_half_fov:
        return false
    # Occlusion raycast
    var space_state := get_world_3d().direct_space_state
    var query := PhysicsRayQueryParameters3D.create(
        global_position, target.global_position, detection_layers
    )
    query.exclude = [get_parent()]
    var result := space_state.intersect_ray(query)
    return result.is_empty() or result.collider == target
```

## Anti-Patterns

- **God FSM**: >15 states in a flat FSM. Refactor into HFSM or switch to behavior tree.
- **Polling perception every frame**: Use Area3D enter/exit signals + periodic raycast confirm instead.
- **Hardcoded transition logic**: State classes that directly call `set_state(ATTACK)`. Use event dispatch through the transition table.
- **GOAP without planner cache**: Replanning from scratch every frame. Cache plan, only replan on world state change or action failure.
- **Utility AI with additive scoring**: Product of considerations handles "all must be somewhat valid"; additive scoring allows a single extreme consideration to override everything.
