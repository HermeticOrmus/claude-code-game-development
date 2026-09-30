---
name: physics-patterns
description: "Game physics code patterns: collision layer configuration, a full CharacterBody3D controller, RigidBody3D interaction, raycasting, Area3D triggers, and a hinge door joint. Use when writing movement, collision, or physics interaction code."
---

# Physics Patterns

## Collision Layer Configuration

```gdscript
# Define collision layers as constants - never magic numbers
class_name PhysicsLayers
# Layer values: collision_layer and collision_mask use bitmasks
const WORLD: int        = 1 << 0  # Layer 1: Static geometry (terrain, walls)
const PLAYER: int       = 1 << 1  # Layer 2: Player character
const ENEMY: int        = 1 << 2  # Layer 3: Enemy characters
const PROJECTILE: int   = 1 << 3  # Layer 4: Bullets, arrows, spells
const PICKUP: int       = 1 << 4  # Layer 5: Collectible items
const TRIGGER: int      = 1 << 5  # Layer 6: Area3D triggers (checkpoints)
const VEHICLE: int      = 1 << 6  # Layer 7: Driveable objects

# Layer assignment table:
# Body Type          | collision_layer    | collision_mask
# Player             | PLAYER             | WORLD | ENEMY | PICKUP | TRIGGER
# Enemy              | ENEMY              | WORLD | PLAYER | PROJECTILE
# Projectile         | PROJECTILE         | WORLD | ENEMY (not PLAYER if friendly fire off)
# Pickup (Area3D)    | PICKUP             | PLAYER (only player can collect)
# Terrain (Static)   | WORLD              | 0 (statics don't need to detect anything)

# Usage:
# player_body.collision_layer = PhysicsLayers.PLAYER
# player_body.collision_mask = PhysicsLayers.WORLD | PhysicsLayers.ENEMY | PhysicsLayers.PICKUP
```

## CharacterBody3D Controller (Full Featured)

```gdscript
class_name PlatformerCharacter extends CharacterBody3D
const SPEED: float = 6.0
const JUMP_VELOCITY: float = 6.0
const GRAVITY: float = 20.0
const FALL_GRAVITY_MULTIPLIER: float = 2.0  # Fast fall on descent
const MAX_FALL_SPEED: float = -30.0

@export var floor_snap_length: float = 0.3  # Prevents bouncing on slopes

func _ready() -> void:
    # Floor snap prevents character bouncing when descending slopes
    motion_mode = CharacterBody3D.MOTION_MODE_GROUNDED
    floor_snap_length = 0.3
    floor_stop_on_slope = true
    floor_max_angle = deg_to_rad(46)  # Max walkable slope

func _physics_process(delta: float) -> void:
    _apply_gravity(delta)
    _handle_movement()
    move_and_slide()
    # move_and_slide() updates velocity for you after collisions

func _apply_gravity(delta: float) -> void:
    if is_on_floor():
        # Keep small downward velocity for slope snapping
        velocity.y = -0.1
    else:
        var grav := GRAVITY * delta
        if velocity.y < 0:
            grav *= FALL_GRAVITY_MULTIPLIER  # Faster fall = better game feel
        velocity.y = maxf(velocity.y - grav, MAX_FALL_SPEED)

func _handle_movement() -> void:
    var input := Input.get_axis(&"move_left", &"move_right")
    velocity.x = input * SPEED

func jump() -> void:
    if is_on_floor():
        velocity.y = JUMP_VELOCITY
```

## RigidBody3D Physics Interaction

```gdscript
# Physics-based destructible prop
class_name DestructibleProp extends RigidBody3D
@export var health: float = 30.0
@export var break_force_threshold: float = 10.0  # Newtons to break
@export var debris_scene: PackedScene
@export var break_sound: AudioStream

signal destroyed(position: Vector3)

func _ready() -> void:
    contact_monitor = true
    max_contacts_reported = 4

func _on_body_shape_entered(body_rid: RID, body: Node, body_shape_index: int, local_shape_index: int) -> void:
    var contact_velocity := linear_velocity.length()
    var impact_force := contact_velocity * mass
    if impact_force > break_force_threshold:
        _break(global_position)

func take_damage(amount: float) -> void:
    health -= amount
    if health <= 0.0:
        _break(global_position)

func _break(position: Vector3) -> void:
    destroyed.emit(position)
    if debris_scene:
        for i in 3:
            var debris := debris_scene.instantiate() as RigidBody3D
            get_parent().add_child(debris)
            debris.global_position = position + Vector3(randf_range(-0.3, 0.3), 0.2, randf_range(-0.3, 0.3))
            debris.apply_central_impulse(Vector3(randf_range(-2, 2), randf_range(1, 3), randf_range(-2, 2)))
    queue_free()
```

## Raycasting Patterns

```gdscript
# Multiple raycast patterns for different use cases
class_name PhysicsQueries extends Node

# Single raycast - weapon hit detection
func raycast_hit(from: Vector3, to: Vector3, mask: int = 0b0111) -> Dictionary:
    var space := get_world_3d().direct_space_state
    var params := PhysicsRayQueryParameters3D.create(from, to, mask)
    params.hit_back_faces = false
    return space.intersect_ray(params)

# Sphere cast - area of effect check
func sphere_overlap(center: Vector3, radius: float, mask: int) -> Array[Dictionary]:
    var space := get_world_3d().direct_space_state
    var shape := SphereShape3D.new()
    shape.radius = radius
    var params := PhysicsShapeQueryParameters3D.new()
    params.shape = shape
    params.transform = Transform3D(Basis(), center)
    params.collision_mask = mask
    return space.intersect_shape(params)

# Ground check raycast
func is_grounded(body_position: Vector3, check_distance: float = 0.1) -> bool:
    var result := raycast_hit(
        body_position + Vector3.UP * 0.05,
        body_position + Vector3.DOWN * check_distance,
        PhysicsLayers.WORLD
    )
    return not result.is_empty()

# Line of sight check
func has_line_of_sight(from: Vector3, to: Vector3) -> bool:
    var result := raycast_hit(from, to, PhysicsLayers.WORLD)
    return result.is_empty()  # No hit = clear line of sight
```

## Area3D Trigger Setup

```gdscript
# Flexible trigger volume for game events
class_name TriggerVolume extends Area3D
signal player_entered
signal player_exited

@export var trigger_once: bool = false
var _triggered: bool = false

func _ready() -> void:
    collision_layer = PhysicsLayers.TRIGGER
    collision_mask = PhysicsLayers.PLAYER
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body: Node3D) -> void:
    if _triggered and trigger_once:
        return
    if body.is_in_group(&"player"):
        _triggered = true
        player_entered.emit()
        if trigger_once:
            set_deferred(&"monitoring", false)

func _on_body_exited(body: Node3D) -> void:
    if body.is_in_group(&"player"):
        player_exited.emit()
```

## Physics Joint (Hinge Door)

```gdscript
# Hinged door using HingeJoint3D
class_name HingeDoor extends Node3D
@onready var door_body: RigidBody3D = $DoorBody
@onready var hinge: HingeJoint3D = $HingeJoint3D

@export var max_angle_degrees: float = 90.0
@export var damping: float = 0.5

func _ready() -> void:
    # HingeJoint3D connects door_body to a StaticBody3D frame
    hinge.set_flag(HingeJoint3D.FLAG_USE_LIMIT, true)
    hinge.set_param(HingeJoint3D.PARAM_LIMIT_LOWER, deg_to_rad(-max_angle_degrees))
    hinge.set_param(HingeJoint3D.PARAM_LIMIT_UPPER, deg_to_rad(max_angle_degrees))
    hinge.set_param(HingeJoint3D.PARAM_MOTOR_TARGET_VELOCITY, 0.0)
    hinge.set_param(HingeJoint3D.PARAM_MOTOR_MAX_IMPULSE, damping)

func open(direction: float = 1.0) -> void:
    door_body.apply_torque(door_body.global_transform.basis.y * direction * 100.0)
```

## Anti-Patterns

- **Mesh collider on moving objects**: Trimesh (ConcavePolygonShape3D) is expensive and doesn't work correctly on moving bodies. Use compound of primitives for characters and props.
- **RigidBody3D for player character**: Physics engine fights player input; momentum makes control feel wrong. Use CharacterBody3D.
- **Raycast every frame for ground check**: Expensive. Use `is_on_floor()` on CharacterBody3D; it's provided for free by `move_and_slide()`.
- **Area3D monitoring with collision_mask = 0**: Area3D with mask 0 monitors nothing. Set mask to the layers you want to detect.
- **High `max_contacts_reported` on all RigidBodies**: Contact generation is expensive. Set `contact_monitor = false` on bodies that don't need contact events.
