---
description: "Set up, blend, add IK to, or wire events into a game animation system"
argument-hint: "[setup|blend|ik|events] <character or animation>"
---

# /animate

Animation system design, implementation, and debugging for Godot, Unity, and Unreal.

## Trigger

`/animate [action] [target]`

## Actions

### `setup`
Configure AnimationTree or Animator controller from scratch.

```
/animate setup "Godot third-person locomotion with 8-directional blend space"
/animate setup "Unity humanoid animator with combat layer"
/animate setup "Godot 2D character with 4-direction sprite sheet"
```

**Output**: AnimationTree node structure diagram, GDScript parameter driver, export variable list.

### `blend`
Design or fix blend tree configuration for smooth animation transitions.

```
/animate blend "speed blend between idle, walk, run - fix foot sliding"
/animate blend "aim offset for 8-directional upper body aiming"
/animate blend "additive layer for breathing over locomotion"
```

**Output**: Blend space configuration, parameter normalization code, transition timing.

### `ik`
Implement inverse kinematics for foot planting, hand placement, or look-at.

```
/animate ik "foot planting on uneven terrain with Godot SkeletonIK3D"
/animate ik "look-at IK for character eye/head tracking"
/animate ik "two-bone IK for hand placement on climbing surfaces"
```

**Output**: IK node setup, raycast-based target positioning, IK weight blending code.

### `events`
Set up animation-driven events for footsteps, hit boxes, or audio triggers.

```
/animate events "footstep sounds triggered by animation"
/animate events "attack hit box enable/disable via animation"
/animate events "particle burst at impact frame"
```

**Output**: Call Method Track setup guide, receiver script with typed signal definitions.

## Examples

**Eight-directional locomotion blend space:**
```
/animate setup "Godot 8-directional locomotion with idle, walk, run per direction"
```
Produces: BlendSpace2D with 9 points (center=idle, cardinal=walk, diagonal=run), GDScript that transforms world velocity into blend space coordinates.

**Fixing foot sliding:**
```
/animate blend "character slides feet during walk animation"
```
Root cause: blend space Y-axis driven by input magnitude (0-1) but animation was authored at 3.5 m/s. Fix: set blend position Y = `velocity.length() / 3.5`.

**Foot planting on stairs:**
```
/animate ik "feet clip through stair edges"
```
Produces: SkeletonIK3D configuration per foot, downward raycast from ankle bone position, pelvis height compensation when one leg extends beyond threshold.

## Blend Space Reference

| Blend Type | Use Case | Godot Node |
|------------|----------|------------|
| 1D | Speed (idle/walk/run) | BlendSpace1D |
| 2D Interpolated | Directional locomotion | BlendSpace2D (Linear) |
| 2D Freeform Directional | Aim offset, strafing | BlendSpace2D (Discrete/Freeform) |
| Additive | Breathing, damage reaction | AnimationNodeAdd2 |
| Transition | State changes | AnimationNodeTransition |

## Root Motion vs In-Place Decision

Use root motion when:
- Animation has authored curves (walk cycle with actual forward movement)
- Physical accuracy matters (character shouldn't slide during attacks)
- Animation speed must match visual character motion precisely

Use in-place when:
- You need code to drive speed (acceleration curves, physics-based movement)
- Multiple speed variants from a single animation (slow/fast walk from same clip)
- Networked characters (easier to sync velocity than root motion delta)
