# shader-programming

Shader programming plugin for LibreGameDev. Covers Godot's shading language (GLSL-based), spatial/canvas_item/particles pipelines, vertex and fragment stage techniques, common visual effects (dissolve, outline, fresnel, water, hologram, pixelate), post-processing, render modes, and GPU performance optimization.

## Effect Quick Reference

| Effect | Shader Type | Key Technique |
|--------|-------------|---------------|
| Dissolve with glowing edge | spatial | Noise `discard` + edge `EMISSION` |
| 2D outline | canvas_item | 8-neighbor alpha sample |
| Hologram | spatial | Fresnel + scan lines + `blend_add` |
| Water surface | spatial | Normal map scroll + vertex wave |
| Pixelate | canvas_item | Floor UV to grid |
| Hit flash | spatial | Mix albedo with white via uniform |
| Cel shading | spatial | `step()` on light dot product |
| Heat distortion | canvas_item | SCREEN_UV offset by noise |

## Components

- **shader-programmer**: Agent with expertise in Godot shading language, vertex/fragment stages, render modes, effect techniques, post-processing, and GPU performance
- **shader**: Command for writing new shaders, debugging render issues, optimizing GPU cost, and extending existing shaders
- **shader-patterns**: Skill library with dissolve (spatial), outline (canvas_item), fresnel/hologram, scrolling water with vertex waves, pixelate post-process, and GDScript parameter control via ShaderMaterial

## Quick Start

Create an effect shader:
```
/shader write "enemy flashes red when taking damage, returns to normal after 0.2 seconds"
```

Debug rendering issues:
```
/shader debug "shader looks correct in editor but black on mobile build"
```

Optimize a heavy shader:
```
/shader optimize "fragment shader doing 6 texture samples and conditional branching"
```

## Godot Render Pipelines

- **Forward+**: Desktop; full feature set including SDFGI, SSR, SSAO, volumetric fog
- **Mobile**: Reduced feature set; no SDFGI; targets mobile GPU constraints
- **Compatibility**: OpenGL ES 3.0; broadest compatibility; no compute shaders

Shaders written for Forward+ may not work on Compatibility. Test on target renderer.
