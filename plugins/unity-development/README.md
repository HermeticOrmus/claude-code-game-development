# Unity Development

> Unity 6 expertise — C# scripting, MonoBehaviour vs. ECS/DOTS decision, Addressables, Render Pipelines (URP / HDRP), Cinemachine, Timeline. The patterns that separate "Unity that ships" from "Unity that gets stuck."

## Overview

Unity has the most surface area of any commercial game engine. MonoBehaviour vs. ECS, Built-in vs. URP vs. HDRP, Resources vs. Addressables vs. AssetBundles — each fork is a real architectural decision with downstream consequences. This plugin encodes Unity-specific expertise so the agent makes those decisions correctly rather than picking the path of least resistance.

## Contents

### Agents

- **unity-engineer** -- Unity 6 specialist. Designs MonoBehaviour vs. ECS architecture deliberately, knows the Render Pipeline trade-offs cold, picks Addressables vs. Resources for the case, and writes idiomatic C# that respects Unity's update loop semantics.

### Commands

- **/unity** -- Architecture design + C# implementation + Unity-specific refactoring. Hand it a Unity project + a feature and it returns the right architectural fork plus implementation.

### Skills

- **unity-development** -- Reference library: MonoBehaviour vs. ECS decision tree, Render Pipeline migration patterns, Addressables vs. Resources, common-mistakes catalog.

## Key Capabilities

- **MonoBehaviour vs. ECS/DOTS decision** — knows when classic OO Unity wins (most gameplay) and when DOTS pays off (massive entity counts, deterministic sim)
- **Render Pipeline choice + migration** — Built-in vs. URP vs. HDRP, switching costs, shader compatibility
- **Asset management** — Addressables (preferred), Resources (legacy), AssetBundles (advanced), Streaming Assets, Pre-load patterns
- **Cinemachine** — virtual cameras, blending, dolly tracks, impulse + noise patterns
- **Timeline** — cinematic sequencing, signals between tracks, runtime control vs. authoring
- **Input System** (new) — Action Maps, Player Input component, control schemes, runtime rebinding
- **DOTS** — Entities, Components, Systems; when the complexity overhead is worth it
- **Networking** — Netcode for GameObjects (current Unity-recommended), Mirror (community alternative), FishNet (newer)

## When to use this plugin

- Starting a new Unity 6 project — get the architecture forks right early
- Migrating from Built-in Render Pipeline to URP / HDRP
- Migrating from Resources to Addressables
- Adopting Unity's new Input System
- Considering DOTS for a high-entity-count gameplay scenario
- Debugging Unity-specific scenarios (domain reload, script execution order, prefab variant gotchas)

## Compatibility

- **Unity version**: 6.0+ (most current; 2022 LTS patterns covered)
- **Languages**: C# (deep)
- **Render Pipelines**: URP (most projects), HDRP (high-end), Built-in (legacy)
- **Platforms**: PC, Mac, Linux, consoles (general patterns within NDA), iOS, Android, WebGL, VR/XR
- **Target use**: 2D + 3D, single + multiplayer, mobile + console + PC

## Limitations the agent will tell you about

- Console-specific code (Switch, PlayStation, Xbox) is supported only at the general pattern level; platform-specific docs live behind NDAs the agent respects
- Legacy Unity (5.x, 2017, 2018) patterns are deprecated; agent will recommend upgrading
- Bolt / Visual Scripting (Unity's node-graph alternative to C#) is covered lightly; deep visual scripting is its own discipline
