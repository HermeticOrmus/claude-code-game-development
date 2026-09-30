---
description: "Configure, simulate, debug, or optimize game physics"
argument-hint: "[configure|simulate|debug|optimize] <body or interaction>"
---

# /physics

Physics configuration, simulation, debugging, and optimization for Godot PhysicsServer3D.

## Trigger

`/physics [action] [target]`

## Actions

### `configure`
Set up physics bodies, collision layers, and materials.

```
/physics configure "collision layer table for player, enemy, projectile, trigger"
/physics configure "character controller with floor snap and slope handling"
/physics configure "rigidbody crate with physics material for bounce and friction"
```

**Output**: CollisionLayer constants, body type selection rationale, PhysicsMaterial configuration.

### `simulate`
Implement physics-driven gameplay mechanics.

```
/physics simulate "destructible prop that breaks into debris on high impact"
/physics simulate "hinged door that opens with physics impulse"
/physics simulate "conveyor belt that pushes rigidbodies"
/physics simulate "rope simulation with chain of rigid bodies and joints"
```

**Output**: Typed GDScript with physics body configuration, force application, joint setup.

### `debug`
Diagnose physics problems.

```
/physics debug "character falls through floor at high speed"
/physics debug "rigidbody objects jitter when stacked"
/physics debug "player getting stuck on stairs"
/physics debug "collision layers not working, enemies pass through player"
```

**Output**: Root cause analysis, fix code, layer/mask table audit.

### `optimize`
Reduce physics performance overhead.

```
/physics optimize "200 physics bodies causing frame drops"
/physics optimize "too many contact events per frame"
/physics optimize "NavMesh + physics causing double work for AI"
```

**Output**: Body reduction strategy, sleep threshold tuning, collision mask optimization.

## Examples

**Designing collision layer table:**
```
/physics configure "collision layers for: player, enemy, projectile, pickup, trigger, vehicle"
```
Produces: Layer constants table, body assignment table (who is what, who sees what), rationale for each mask choice.

**Character falls through floor:**
```
/physics debug "CharacterBody3D occasionally falls through floor when moving fast"
```
Root cause: velocity too high for collision step; character moves further than floor thickness in one frame. Fixes:
1. Enable CCD for fast-moving scenarios
2. Increase physics tick rate (Project Settings > physics_fps to 120)
3. Add floor sweep margin: `floor_snap_length = 0.3`

**Physics objects jitter when stacked:**
```
/physics debug "crates jitter when stacked 3 high"
```
Root cause: physics solver instability. Fixes: increase `physics/3d/solver_iterations` in ProjectSettings, reduce crate mass variance, add slight friction to crate material.

## Physics Body Selection Guide

| Scenario | Body Type | Key Property |
|---------|----------|-------------|
| Terrain, walls, ground | StaticBody3D | Never moves |
| Player character | CharacterBody3D | move_and_slide() |
| NPC character | CharacterBody3D | NavigationAgent3D |
| Physics prop | RigidBody3D | mass, linear_damp |
| Moving platform | AnimatableBody3D | Kinematic, affects rigid |
| Zone trigger | Area3D | body_entered signal |
| Pickup item | Area3D or StaticBody3D | Depends on pickup type |
