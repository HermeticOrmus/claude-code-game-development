# Godot Development

> Godot 4 expertise — GDScript + C#, Node tree, scene composition, signals, resources, physics, animation, project structure. The patterns that make Godot productive instead of fighting you.

## Overview

Godot has gone from "the indie engine some people use" to a genuine alternative to Unity in 4.x. But Godot's idioms are different — Nodes vs. GameObjects, Signals vs. UnityEvents, Resources vs. ScriptableObjects, scene inheritance vs. prefab variants. This plugin encodes Godot-specific patterns so the agent thinks in Godot rather than translating from Unity.

## Contents

### Agents

- **godot-engineer** -- Godot 4 specialist. Designs Node trees with proper composition, names the signal vs. direct-call decision per case, handles resource sharing + duplication correctly, knows the GDScript ↔ C# trade-offs. Defaults to GDScript for gameplay logic, C# for compute-heavy work.

### Commands

- **/godot** -- Node tree design + script authoring + Godot-idiomatic refactoring. Hand it a feature and it returns a Node structure + script with proper Godot patterns.

### Skills

- **godot-development** -- Reference library: signal vs. polling decision tree, resource sharing pitfalls, common-mistakes catalog, GDScript ↔ C# rosetta.

## Key Capabilities

- **Node tree design** for game features — properly composed scenes, scripts attached at the right level, signal connections that aren't a maze
- **GDScript + C# bilingual** — knows when GDScript's lighter syntax wins (gameplay) and when C# wins (heavy compute, IL2CPP if you ever need Unity portability)
- **Scene composition + inheritance** — when to use inherited scenes vs. instantiated scenes vs. PackedScene references
- **Signal architecture** — decoupled event flow that doesn't become a spaghetti web
- **Resource management** — knows the shared-by-default trap, when to duplicate, when to use UniqueResource, when to use a Resource as a script-level configuration
- **Physics setup** — RigidBody2D vs. CharacterBody2D vs. Area2D vs. StaticBody2D decision, collision layers, one-way collisions, kinematic patterns
- **Animation systems** — AnimationPlayer vs. AnimationTree, blend trees, state machines, root motion
- **Input handling** — Input.is_action_pressed vs. _unhandled_input vs. _input vs. _gui_input — when each is correct

## When to use this plugin

- Starting a new Godot 4 project — get the architecture right early
- Migrating from Godot 3 (significant API changes; the agent knows them)
- Coming from Unity and learning Godot — avoid the "translate Unity to Godot" trap
- Debugging a "this should work" Godot-specific scenario
- Refactoring a Godot project that has become tangled

## Compatibility

- **Godot version**: 4.2+ (4.0 + 4.1 patterns covered, but some APIs changed)
- **Languages**: GDScript (deep), C# (deep), C++ via GDExtension (light)
- **Renderer**: Forward+, Mobile, Compatibility — agent knows which choice fits which target
- **Export targets**: Linux, Windows, macOS, Web (HTML5), Android, iOS

## Limitations the agent will tell you about

- Godot 3.x is deprecated; agent will recommend porting rather than supporting both
- Custom GDExtension patterns are covered at a high level; deep GDExtension C++ work would benefit from official Godot docs
- VR / XR in Godot is supported but agent depth there is lighter than core 2D + 3D
