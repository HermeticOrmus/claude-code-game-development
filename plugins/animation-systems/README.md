# animation-systems

Animation plugin for LibreGameDev. Covers skeletal animation, blend trees, state machines, inverse kinematics, root motion, and animation events across Godot, Unity, and Unreal.

## Scope

Runtime animation logic: how animations are blended, transitioned, and driven by gameplay code. Does not cover DCC tooling (Blender rigging, Maya skinning) or asset compression pipelines (covered by asset-pipelines plugin).

## Engine Coverage

| Feature | Godot 4 | Unity | Unreal 5 |
|---------|---------|-------|----------|
| State machine | AnimationNodeStateMachine | Animator Controller | AnimGraph State Machine |
| 1D blend | BlendSpace1D | Blend Tree 1D | Blend Space 1D |
| 2D blend | BlendSpace2D | Blend Tree 2D | Blend Space |
| Additive layer | AnimationNodeAdd2 | Animator Layer (Additive) | Additive Animation Layer |
| IK | SkeletonIK3D, FABRIK | Animation Rigging | Control Rig, IK Retargeter |
| Root motion | get_root_motion_position() | Apply Root Motion (Animator) | Root Motion |

## Components

- **animation-engineer**: Agent with expertise in skeletal animation, blend trees, IK, and root motion
- **animate**: Command for setting up, blending, adding IK, and wiring animation events
- **animation-patterns**: Skill library with GDScript/C# for blend space locomotion, root motion, foot planting IK, and animation events

## Quick Start

Set up locomotion blend tree:
```
/animate setup "Godot 3D character with 8-directional locomotion blend space"
```

Fix foot sliding:
```
/animate blend "locomotion blend space foot sliding at high speed"
```

Add foot IK on terrain:
```
/animate ik "foot planting on uneven terrain"
```
