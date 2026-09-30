---
description: "Write, debug, optimize, or extend a Godot shader"
argument-hint: "[write|debug|optimize|extend] <effect>"
---

# /shader

Write, debug, and optimize shaders for Godot's spatial, canvas_item, and particles pipelines.

## Trigger

`/shader [action] [target]`

## Actions

### `write`
Create a new shader for a specific visual effect.

```
/shader write "character dissolves away with orange glowing edge when killed"
/shader write "2D sprite outline that pulses when selected"
/shader write "water surface with normal map scrolling, fresnel, and wave vertices"
/shader write "hologram effect: scan lines, fresnel edges, flicker"
/shader write "pixelate post-process for retro camera transition"
```

**Output**: Complete `.gdshader` file with uniforms, vertex/fragment functions, render mode selection, and GDScript snippet for setting parameters.

### `debug`
Diagnose shader problems.

```
/shader debug "shader renders black on mobile but works in editor"
/shader debug "transparent shader z-sorting artifacts when overlapping"
/shader debug "SCREEN_TEXTURE uniform not sampling correctly"
/shader debug "outline only shows on some sides of sprite"
```

**Output**: Root cause analysis, fix code, explanation of why the issue occurs.

### `optimize`
Reduce shader GPU cost.

```
/shader optimize "fragment shader has 8 texture samples and 3 if-branches"
/shader optimize "post-process effect drops FPS from 60 to 45 on mobile"
```

**Output**: Profiling approach, specific optimizations (pack textures, replace if with mix/step, reduce precision), before/after comparison.

### `extend`
Modify an existing shader to add a feature.

```
/shader extend "add hit flash to existing character shader - turn white briefly when taking damage"
/shader extend "add rain drip normal map distortion to existing water shader"
```

**Output**: Modified shader code with diff annotations showing what changed and why.

## Examples

**Creating a dissolve effect:**
```
/shader write "mesh dissolves into particles when dying - noise-based discard with glowing orange edge"
```
Produces: Spatial shader with noise texture uniform, `dissolve_amount` 0-1 uniform, `discard` at threshold, `EMISSION` at edge. Includes GDScript Tween to animate `dissolve_amount` over time.

**Debugging black output on mobile:**
```
/shader debug "spatial shader works in editor (Forward+) but renders black on Android"
```
Root cause: `SCREEN_TEXTURE` not available in Compatibility renderer without explicit hint. Fix: add `hint_screen_texture` to uniform declaration; check renderer compatibility.

## Shader Type Reference

| Type | Engine Pipeline | When to Use |
|------|----------------|-------------|
| `spatial` | 3D Forward+ / Mobile | 3D meshes, PBR surfaces, 3D effects |
| `canvas_item` | 2D renderer | Sprites, UI, 2D post-process |
| `particles` | GPU particle system | Particle color/size/movement |
| `sky` | Sky shader | Procedural sky, skybox replacement |
| `fog` | Volumetric fog | Height fog, colored atmosphere |

## Render Mode Quick Reference

| Goal | Render Mode |
|------|------------|
| Emissive/unlit | `unshaded` |
| Transparent object | `blend_mix, depth_draw_never` |
| Additive (fire, sparks) | `blend_add, depth_draw_never, cull_disabled` |
| Two-sided geometry | `cull_disabled` |
| Binary alpha mask | `alpha_to_coverage` or `ALPHA_SCISSOR_THRESHOLD` |
