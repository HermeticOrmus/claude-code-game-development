---
name: shader-patterns
description: "Godot shader code: dissolve, 2D outline, fresnel hologram, scrolling water, a pixelate post-process on a SubViewport, and setting shader parameters from GDScript. Use when building visual effects in Godot's shading language."
---

# Shader Patterns

## Dissolve Effect (Godot Spatial)

```glsl
shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back;

uniform sampler2D albedo_texture : source_color;
uniform sampler2D noise_texture;
uniform float dissolve_amount : hint_range(0.0, 1.0) = 0.0;
uniform vec4 edge_color : source_color = vec4(1.0, 0.4, 0.0, 1.0);
uniform float edge_width : hint_range(0.0, 0.2) = 0.05;

void fragment() {
    vec4 albedo = texture(albedo_texture, UV);
    float noise = texture(noise_texture, UV).r;

    // Discard fragments below dissolve threshold
    if (noise < dissolve_amount) {
        discard;
    }

    // Glow at dissolve edge
    float edge = smoothstep(dissolve_amount, dissolve_amount + edge_width, noise);
    vec3 emission = mix(edge_color.rgb, vec3(0.0), edge);

    ALBEDO = albedo.rgb;
    EMISSION = emission;
    ALPHA = albedo.a;
}
```

## Outline Shader (Godot CanvasItem / 2D)

```glsl
shader_type canvas_item;

uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float outline_width : hint_range(0.0, 10.0) = 2.0;

void fragment() {
    vec2 uv = UV;
    vec2 texel_size = outline_width / vec2(textureSize(TEXTURE, 0));

    float alpha = texture(TEXTURE, uv).a;

    // Sample 8 neighbors
    float neighbor_alpha = 0.0;
    neighbor_alpha += texture(TEXTURE, uv + vec2(texel_size.x, 0.0)).a;
    neighbor_alpha += texture(TEXTURE, uv + vec2(-texel_size.x, 0.0)).a;
    neighbor_alpha += texture(TEXTURE, uv + vec2(0.0, texel_size.y)).a;
    neighbor_alpha += texture(TEXTURE, uv + vec2(0.0, -texel_size.y)).a;
    neighbor_alpha += texture(TEXTURE, uv + vec2(texel_size.x, texel_size.y)).a;
    neighbor_alpha += texture(TEXTURE, uv + vec2(-texel_size.x, texel_size.y)).a;
    neighbor_alpha += texture(TEXTURE, uv + vec2(texel_size.x, -texel_size.y)).a;
    neighbor_alpha += texture(TEXTURE, uv + vec2(-texel_size.x, -texel_size.y)).a;

    // If any neighbor has alpha but this pixel doesn't: draw outline
    if (alpha < 0.1 && neighbor_alpha > 0.1) {
        COLOR = outline_color;
    } else {
        COLOR = texture(TEXTURE, uv);
    }
}
```

## Fresnel / Hologram Effect (Godot Spatial)

```glsl
shader_type spatial;
render_mode blend_add, depth_draw_never, cull_disabled, unshaded;

uniform vec4 hologram_color : source_color = vec4(0.0, 1.0, 0.8, 1.0);
uniform float fresnel_power : hint_range(0.5, 8.0) = 3.0;
uniform float scan_line_density : hint_range(10.0, 200.0) = 60.0;
uniform float flicker_speed : hint_range(0.0, 20.0) = 8.0;
uniform float alpha_intensity : hint_range(0.0, 2.0) = 1.0;

void fragment() {
    // Fresnel: bright at glancing angles
    float fresnel = pow(1.0 - abs(dot(NORMAL, VIEW)), fresnel_power);

    // Scan lines via screen-space Y coordinate
    float scan = step(0.5, fract(FRAGCOORD.y / scan_line_density));

    // Flicker
    float flicker = 0.8 + 0.2 * sin(TIME * flicker_speed + FRAGCOORD.y * 0.1);

    float alpha = fresnel * scan * flicker * alpha_intensity;
    ALBEDO = hologram_color.rgb;
    EMISSION = hologram_color.rgb * fresnel;
    ALPHA = clamp(alpha, 0.0, 1.0);
}
```

## Scrolling Water (Godot Spatial)

```glsl
shader_type spatial;
render_mode blend_mix, depth_draw_opaque;

uniform sampler2D normal_map_a : hint_normal;
uniform sampler2D normal_map_b : hint_normal;
uniform vec4 shallow_color : source_color = vec4(0.1, 0.6, 0.8, 0.9);
uniform vec4 deep_color : source_color = vec4(0.0, 0.15, 0.4, 1.0);
uniform float tiling : hint_range(1.0, 20.0) = 5.0;
uniform float scroll_speed : hint_range(0.0, 2.0) = 0.3;
uniform float wave_height : hint_range(0.0, 1.0) = 0.1;
uniform float fresnel_power : hint_range(0.5, 8.0) = 4.0;

void vertex() {
    // Sine wave vertex displacement
    float wave = sin(VERTEX.x * 2.0 + TIME * scroll_speed * 3.0)
               * cos(VERTEX.z * 2.5 + TIME * scroll_speed * 2.0);
    VERTEX.y += wave * wave_height;
}

void fragment() {
    vec2 uv1 = UV * tiling + vec2(TIME * scroll_speed, TIME * scroll_speed * 0.7);
    vec2 uv2 = UV * tiling * 0.7 + vec2(-TIME * scroll_speed * 0.8, TIME * scroll_speed * 0.5);

    vec3 n1 = texture(normal_map_a, uv1).rgb;
    vec3 n2 = texture(normal_map_b, uv2).rgb;
    NORMAL_MAP = normalize(n1 + n2);  // Blend two normal maps

    float fresnel = pow(1.0 - dot(NORMAL, VIEW), fresnel_power);
    ALBEDO = mix(deep_color.rgb, shallow_color.rgb, fresnel);
    ROUGHNESS = 0.05;
    METALLIC = 0.0;
    ALPHA = mix(deep_color.a, shallow_color.a, fresnel);
}
```

## Pixelate Post-Process (CanvasItem on SubViewport)

```glsl
shader_type canvas_item;

uniform float pixel_size : hint_range(1.0, 64.0) = 4.0;

void fragment() {
    // Snap UV to pixel grid
    vec2 uv = UV;
    vec2 screen_size = vec2(textureSize(TEXTURE, 0));
    vec2 pixels = screen_size / pixel_size;
    uv = floor(uv * pixels) / pixels;
    COLOR = texture(TEXTURE, uv);
}
```

## Setting Shader Parameters from GDScript

```gdscript
# Set uniform parameters on a ShaderMaterial at runtime
class_name DissolveController extends Node3D
@export var mesh_instance: MeshInstance3D
@export var dissolve_duration: float = 1.5

var _dissolve_tween: Tween

func start_dissolve() -> void:
    var mat := mesh_instance.get_active_material(0) as ShaderMaterial
    if not mat:
        push_error("DissolveController: no ShaderMaterial on mesh")
        return

    _dissolve_tween = create_tween()
    _dissolve_tween.tween_method(
        func(v: float): mat.set_shader_parameter("dissolve_amount", v),
        0.0,
        1.0,
        dissolve_duration
    )
    _dissolve_tween.tween_callback(func(): mesh_instance.visible = false)
```

## Anti-Patterns

- **Branching in fragment shader**: `if (condition)` on GPU executes both branches. Use `mix(a, b, step(0.5, condition))` instead.
- **Texture samples in vertex shader for per-fragment detail**: Vertex shader has limited texture precision (depends on mesh density). Sample detail textures in fragment.
- **SCREEN_TEXTURE without hint**: `uniform sampler2D screen_texture` requires `hint_screen_texture` annotation in Godot 4, otherwise it binds incorrectly.
- **Complex post-process as canvas_item on every sprite**: One expensive shader on a full-screen quad costs the same as on a tiny sprite but covers far fewer pixels. Post-process goes on screen-covering quad.
- **`discard` for alpha blending**: `discard` prevents early-z optimization. For gradual transparency, use `ALPHA` with `blend_mix`. Reserve `discard` for binary alpha (foliage, windows) where the expense is worth the sorting simplicity.
