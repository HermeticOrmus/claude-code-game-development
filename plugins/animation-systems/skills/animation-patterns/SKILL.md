---
name: animation-patterns
description: "Animation code patterns: Godot BlendSpace2D locomotion, AnimationNodeStateMachine transitions, root motion integration, IK foot planting, call-method animation events, and a Unity 2D freeform blend tree. Use when implementing character locomotion, animation state logic, or IK in a game."
---

# Animation Patterns

## Godot AnimationTree BlendSpace2D Locomotion

```gdscript
# Locomotion blend tree setup - driven by velocity
class_name PlayerAnimator extends Node
@onready var animation_tree: AnimationTree = $AnimationTree
@onready var body: CharacterBody3D = get_parent()

const BLEND_PATH := "parameters/LocomotionBlend/blend_position"
const SPEED_PATH := "parameters/SpeedBlend/blend_amount"

func _physics_process(_delta: float) -> void:
    var velocity := body.velocity
    var speed := velocity.length()

    # 2D blend space: X=strafe (-1 left, 1 right), Y=forward (0 idle, 1 run)
    # Normalize by max speed so blend space uses [0,1] range
    var horizontal := body.global_transform.basis.x.dot(velocity) / 6.0
    var forward := -body.global_transform.basis.z.dot(velocity) / 6.0

    animation_tree.set(BLEND_PATH, Vector2(horizontal, forward))
    animation_tree.set(SPEED_PATH, speed / 6.0)  # 6.0 = max run speed

# AnimationTree configuration (in Godot editor):
# Root: AnimationNodeStateMachine
#   State "Locomotion": AnimationNodeBlendSpace2D
#     Points:
#       (0, 0) = "idle" clip
#       (0, 1) = "run_forward" clip
#       (1, 0) = "strafe_right" clip
#       (-1, 0) = "strafe_left" clip
#       (0, -1) = "walk_backward" clip
#     Blend mode: Interpolation (linear)
#   State "Jump": AnimationNodeAnimation ("jump" clip, no loop)
#   State "Land": AnimationNodeAnimation ("land" clip, no loop)
#   Transitions:
#     Locomotion -> Jump: condition "is_jumping" (bool param)
#     Jump -> Land: advance condition "animation_finished"
#     Land -> Locomotion: advance condition "animation_finished"
```

## AnimationNodeStateMachine Transitions (GDScript)

```gdscript
# Trigger state transitions through AnimationTree parameters
func jump() -> void:
    animation_tree.set("parameters/conditions/is_jumping", true)
    # Reset after one frame so it acts as a trigger
    await get_tree().process_frame
    animation_tree.set("parameters/conditions/is_jumping", false)

func land() -> void:
    animation_tree.set("parameters/conditions/is_landing", true)
    await get_tree().process_frame
    animation_tree.set("parameters/conditions/is_landing", false)

# Reading current state name for logic decisions
func get_current_animation() -> StringName:
    var playback: AnimationNodeStateMachinePlayback = animation_tree.get(
        "parameters/playback"
    )
    return playback.get_current_node()

func is_in_state(state_name: StringName) -> bool:
    return get_current_animation() == state_name
```

## Root Motion Integration

```gdscript
# Apply AnimationTree root motion to CharacterBody3D
class_name RootMotionCharacter extends CharacterBody3D
@onready var animation_tree: AnimationTree = $AnimationTree

func _physics_process(delta: float) -> void:
    # Get root motion delta from animation (in local space)
    var root_motion: Vector3 = animation_tree.get_root_motion_position()

    # Transform from local animation space to world space
    var world_motion: Vector3 = global_transform.basis * root_motion

    # Apply gravity separately (root motion only handles horizontal locomotion)
    if not is_on_floor():
        velocity.y -= 9.8 * delta
    else:
        velocity.y = 0.0

    # Override XZ velocity with root motion
    velocity.x = world_motion.x / delta
    velocity.z = world_motion.z / delta

    move_and_slide()
```

## Inverse Kinematics - Foot Planting

```gdscript
# Foot IK using SkeletonIK3D nodes
class_name FootIK extends Node
@export var skeleton: Skeleton3D
@export var left_ik: SkeletonIK3D
@export var right_ik: SkeletonIK3D
@export var raycast_distance: float = 1.5
@export var ik_blend_speed: float = 10.0

var _left_ik_weight: float = 0.0
var _right_ik_weight: float = 0.0

func _physics_process(delta: float) -> void:
    _update_foot_ik(left_ik, "LeftFoot", delta, _left_ik_weight)
    _update_foot_ik(right_ik, "RightFoot", delta, _right_ik_weight)

func _update_foot_ik(ik: SkeletonIK3D, bone_name: String, delta: float, weight: float) -> void:
    var bone_idx := skeleton.find_bone(bone_name)
    var bone_global_pos := skeleton.get_bone_global_pose(bone_idx).origin
    bone_global_pos = skeleton.global_transform * bone_global_pos

    var space_state := get_world_3d().direct_space_state
    var query := PhysicsRayQueryParameters3D.create(
        bone_global_pos + Vector3.UP * 0.5,
        bone_global_pos + Vector3.DOWN * raycast_distance,
        0b0001  # ground layer only
    )
    var result := space_state.intersect_ray(query)

    if result:
        # Align IK target to ground surface
        var target_xform := Transform3D(
            Basis(result.normal),  # orient to slope
            result.position
        )
        ik.target = target_xform
        _left_ik_weight = move_toward(_left_ik_weight, 1.0, delta * ik_blend_speed)
    else:
        _left_ik_weight = move_toward(_left_ik_weight, 0.0, delta * ik_blend_speed)

    ik.interpolation = _left_ik_weight
```

## Animation Events via Call Method Track

```gdscript
# Receiver script on character (animation calls these via Method Track)
class_name CharacterAnimationReceiver extends Node
signal footstep_left
signal footstep_right
signal attack_hit_start
signal attack_hit_end

# Called by AnimationPlayer Method Track at frame of left foot contact
func on_footstep_left() -> void:
    footstep_left.emit()
    # Determine surface material for correct footstep sound
    _play_footstep_sound(-1.0)  # -1 = left

func on_footstep_right() -> void:
    footstep_right.emit()
    _play_footstep_sound(1.0)

func on_attack_active() -> void:
    attack_hit_start.emit()

func on_attack_inactive() -> void:
    attack_hit_end.emit()

func _play_footstep_sound(side: float) -> void:
    # Raycast down to detect surface material
    # Surface material -> audio bus send to correct footstep pool
    pass
```

## Unity Animator Blend Tree - 2D Freeform Directional (C#)

```csharp
// Drive Animator blend tree from CharacterController velocity
public class PlayerAnimatorController : MonoBehaviour
{
    private Animator _animator;
    private CharacterController _controller;

    // Animator parameter hashes - cache to avoid string lookup cost
    private static readonly int SpeedX = Animator.StringToHash("SpeedX");
    private static readonly int SpeedZ = Animator.StringToHash("SpeedZ");
    private static readonly int IsGrounded = Animator.StringToHash("IsGrounded");
    private static readonly int JumpTrigger = Animator.StringToHash("Jump");

    private const float AnimDampTime = 0.1f;  // Smooth parameter changes

    private void Awake()
    {
        _animator = GetComponent<Animator>();
        _controller = GetComponent<CharacterController>();
    }

    private void Update()
    {
        // Project world velocity into local character space
        Vector3 localVelocity = transform.InverseTransformDirection(_controller.velocity);
        float normalizedX = localVelocity.x / 6f;
        float normalizedZ = localVelocity.z / 6f;

        // Damped parameter update prevents blend tree pops
        _animator.SetFloat(SpeedX, normalizedX, AnimDampTime, Time.deltaTime);
        _animator.SetFloat(SpeedZ, normalizedZ, AnimDampTime, Time.deltaTime);
        _animator.SetBool(IsGrounded, _controller.isGrounded);
    }

    public void TriggerJump() => _animator.SetTrigger(JumpTrigger);
}
```

## Anti-Patterns

- **Driving blend positions with Input.get_vector()**: Use actual velocity, not input. Input doesn't account for acceleration, sliding, or external forces.
- **String parameter lookups in Update**: Use `Animator.StringToHash()` or Godot's StringName cache. String allocation per frame is measurable overhead.
- **IK every frame on background characters**: Gate IK evaluation on distance from camera. Disable SkeletonIK3D when character is >15m from camera.
- **Animation events for collision detection**: Don't enable hit boxes via animation events alone. Events can miss frames. Use a dedicated AttackComponent that checks animation state.
- **Single monolithic blend tree**: Split locomotion, combat, and interaction into separate Animator layers (Unity) or nested AnimationNodeStateMachines (Godot).
