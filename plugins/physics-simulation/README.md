# physics-simulation

Physics plugin for LibreGameDev. Covers Godot PhysicsServer3D, collision layers, body type selection, CharacterBody3D controller, RigidBody3D dynamics, Area3D triggers, joint constraints, and physics optimization.

## Body Type Quick Reference

| Type | Moves? | Physics? | Use For |
|------|--------|---------|---------|
| StaticBody3D | No | Receives only | Terrain, walls, platforms |
| CharacterBody3D | Code-driven | Kinematic | Player, NPC |
| RigidBody3D | Physics-driven | Full simulation | Props, debris, vehicles |
| AnimatableBody3D | Code-driven | Affects RigidBody | Moving platforms |
| Area3D | Optional | Overlap only | Triggers, sensors, zones |

## Components

- **physics-engineer**: Agent with expertise in Godot physics bodies, collision layers, CCD, joints, and PhysicsServer3D direct API
- **physics**: Command for configuring, simulating, debugging, and optimizing physics
- **physics-patterns**: Skill library with collision layer constants, CharacterBody3D controller, RigidBody3D destruction, raycasting patterns, Area3D triggers, and HingeJoint3D

## Quick Start

Configure collision layers:
```
/physics configure "collision layers for 3D action game: player, enemy, projectile, trigger"
```

Debug falling through floor:
```
/physics debug "character falls through floor at high movement speed"
```

Implement destructible object:
```
/physics simulate "crate that breaks into debris when hit with enough force"
```
