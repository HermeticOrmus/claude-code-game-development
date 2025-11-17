# Shader Programming

## Introduction

Shaders are the secret weapon of modern game graphics, enabling visual effects that would be impossible with traditional rendering APIs. Written in GLSL (OpenGL Shading Language), shaders are small programs that run massively parallel on your GPU, processing thousands of vertices and millions of pixels per frame. From simple color tinting to complex procedural effects like water simulation, fire, and post-processing, shaders transform basic 3D geometry into stunning visuals.

This guide teaches GLSL from fundamentals to advanced effects, with complete working examples for every technique. We'll cover vertex shaders that transform geometry, fragment shaders that compute pixel colors, and the mathematical concepts that make effects work. By the end, you'll be creating custom visual effects for your games with confidence.

## GLSL Fundamentals

### Language Basics

GLSL is a C-like language designed for graphics operations:

```glsl
// Data types
float a = 1.0;          // Single float
vec2 b = vec2(1.0, 2.0); // 2D vector
vec3 c = vec3(1.0, 2.0, 3.0); // 3D vector
vec4 d = vec4(1.0, 2.0, 3.0, 4.0); // 4D vector (often RGBA or homogeneous coords)

mat2 m2;  // 2x2 matrix
mat3 m3;  // 3x3 matrix
mat4 m4;  // 4x4 matrix (transformations)

sampler2D tex; // 2D texture sampler
samplerCube cubemap; // Cubemap sampler

// Vector swizzling (very powerful!)
vec4 color = vec4(1.0, 0.5, 0.2, 1.0);
vec3 rgb = color.rgb;     // Extract RGB
vec2 rg = color.rg;       // Extract RG
float r = color.r;        // Extract red channel

// Swizzle reordering
vec4 bgra = color.bgra;   // Reorder channels
vec3 rrr = color.rrr;     // Replicate red

// Vector operations
vec3 pos = vec3(1.0, 2.0, 3.0);
vec3 dir = vec3(0.0, 1.0, 0.0);
float d = dot(pos, dir);        // Dot product
vec3 cross = cross(pos, dir);   // Cross product
float len = length(pos);        // Vector length
vec3 norm = normalize(pos);     // Normalized vector

// Built-in functions
float x = sin(1.0);
float y = cos(1.0);
float z = pow(2.0, 3.0);  // 2^3 = 8
float w = clamp(value, 0.0, 1.0); // Clamp to range
float mixed = mix(a, b, 0.5); // Linear interpolation
```

### Shader Types and Communication

**Vertex Shader** processes each vertex:
- **Input**: Attributes (per-vertex data from buffers)
- **Output**: `gl_Position` (transformed position) and varyings
- **Purpose**: Transform vertices, prepare data for fragment shader

**Fragment Shader** processes each pixel:
- **Input**: Varyings (interpolated from vertex shader)
- **Output**: `gl_FragColor` (pixel color)
- **Purpose**: Compute final pixel color

**Uniforms**: Data shared across all vertices/fragments (time, textures, matrices)

**Varyings**: Data passed from vertex to fragment shader (interpolated)

```glsl
// Vertex Shader
attribute vec3 aPosition;    // INPUT: From JavaScript
attribute vec2 aTexCoord;    // INPUT: From JavaScript

uniform mat4 uModelMatrix;   // UNIFORM: Shared across all vertices
uniform mat4 uViewMatrix;
uniform mat4 uProjectionMatrix;

varying vec2 vTexCoord;      // OUTPUT: To fragment shader

void main() {
    gl_Position = uProjectionMatrix * uViewMatrix * uModelMatrix * vec4(aPosition, 1.0);
    vTexCoord = aTexCoord;   // Pass to fragment shader
}
```

```glsl
// Fragment Shader
precision mediump float;     // REQUIRED: Precision qualifier

varying vec2 vTexCoord;      // INPUT: From vertex shader

uniform sampler2D uTexture;  // UNIFORM: Texture
uniform float uTime;         // UNIFORM: Animation time

void main() {
    vec4 texColor = texture2D(uTexture, vTexCoord);
    gl_FragColor = texColor; // OUTPUT: Final pixel color
}
```

## Vertex Shader Examples

Vertex shaders transform 3D positions and prepare data for fragment shaders.

### Example 1: Basic Transform with Color Pass-through

```glsl
attribute vec3 aPosition;
attribute vec3 aColor;

uniform mat4 uMVP;  // Model-View-Projection matrix

varying vec3 vColor;

void main() {
    gl_Position = uMVP * vec4(aPosition, 1.0);
    vColor = aColor;
}
```

**Purpose**: Standard vertex transformation with color data forwarded to fragment shader.

### Example 2: Wave Animation

```glsl
attribute vec3 aPosition;
attribute vec2 aTexCoord;

uniform mat4 uMVP;
uniform float uTime;
uniform float uWaveAmplitude;
uniform float uWaveFrequency;

varying vec2 vTexCoord;

void main() {
    vec3 pos = aPosition;

    // Create wave effect based on X position and time
    float wave = sin(pos.x * uWaveFrequency + uTime) * uWaveAmplitude;
    pos.y += wave;

    gl_Position = uMVP * vec4(pos, 1.0);
    vTexCoord = aTexCoord;
}
```

**Visual Effect**: Vertices oscillate vertically creating a wave motion, perfect for water surfaces or cloth simulation.

### Example 3: Vertex Displacement (Terrain)

```glsl
attribute vec3 aPosition;
attribute vec2 aTexCoord;

uniform mat4 uMVP;
uniform sampler2D uHeightMap;
uniform float uHeightScale;

varying vec2 vTexCoord;
varying float vHeight;

void main() {
    vec3 pos = aPosition;

    // Sample height from texture
    float height = texture2D(uHeightMap, aTexCoord).r;
    pos.y += height * uHeightScale;

    vHeight = height;  // Pass height to fragment shader for coloring

    gl_Position = uMVP * vec4(pos, 1.0);
    vTexCoord = aTexCoord;
}
```

**Visual Effect**: Transforms a flat plane into 3D terrain by displacing vertices based on a height map texture.

### Example 4: Billboard Sprites (Always Face Camera)

```glsl
attribute vec3 aPosition;    // Sprite center
attribute vec2 aOffset;      // Corner offset in screen space
attribute vec2 aTexCoord;

uniform mat4 uView;
uniform mat4 uProjection;

varying vec2 vTexCoord;

void main() {
    // Transform center to view space
    vec4 viewPos = uView * vec4(aPosition, 1.0);

    // Add offset in view space (stays facing camera)
    viewPos.xy += aOffset;

    gl_Position = uProjection * viewPos;
    vTexCoord = aTexCoord;
}
```

**Visual Effect**: Sprites always face the camera, ideal for particles, trees in 3D games, or 2D sprites in 3D space.

### Example 5: Skeletal Animation

```glsl
attribute vec3 aPosition;
attribute vec3 aNormal;
attribute vec4 aBoneIndices;   // Which bones affect this vertex
attribute vec4 aBoneWeights;   // How much each bone affects

uniform mat4 uMVP;
uniform mat4 uBoneMatrices[50]; // Bone transformation matrices

varying vec3 vNormal;

void main() {
    // Blend bone transformations
    mat4 boneTransform =
        uBoneMatrices[int(aBoneIndices.x)] * aBoneWeights.x +
        uBoneMatrices[int(aBoneIndices.y)] * aBoneWeights.y +
        uBoneMatrices[int(aBoneIndices.z)] * aBoneWeights.z +
        uBoneMatrices[int(aBoneIndices.w)] * aBoneWeights.w;

    vec4 skinnedPos = boneTransform * vec4(aPosition, 1.0);
    vec4 skinnedNormal = boneTransform * vec4(aNormal, 0.0);

    gl_Position = uMVP * skinnedPos;
    vNormal = skinnedNormal.xyz;
}
```

**Visual Effect**: Enables character animation by deforming mesh based on skeletal rig.

## Fragment Shader Examples

Fragment shaders compute the final color of each pixel.

### Example 1: Simple Texture with Tint

```glsl
precision mediump float;

varying vec2 vTexCoord;

uniform sampler2D uTexture;
uniform vec4 uTintColor;

void main() {
    vec4 texColor = texture2D(uTexture, vTexCoord);
    gl_FragColor = texColor * uTintColor;
}
```

**Visual Effect**: Multiplies texture color by tint color, useful for damage flashes, powerups, or team colors.

### Example 2: Animated Gradient

```glsl
precision mediump float;

varying vec2 vTexCoord;

uniform float uTime;

void main() {
    // Animated color based on position and time
    float r = sin(vTexCoord.x * 10.0 + uTime) * 0.5 + 0.5;
    float g = sin(vTexCoord.y * 10.0 + uTime * 1.3) * 0.5 + 0.5;
    float b = sin((vTexCoord.x + vTexCoord.y) * 5.0 + uTime * 0.7) * 0.5 + 0.5;

    gl_FragColor = vec4(r, g, b, 1.0);
}
```

**Visual Effect**: Flowing, animated rainbow gradient perfect for power-up effects or backgrounds.

### Example 3: Dissolve Effect

```glsl
precision mediump float;

varying vec2 vTexCoord;

uniform sampler2D uTexture;
uniform sampler2D uNoiseTexture;
uniform float uDissolveAmount; // 0.0 to 1.0

void main() {
    vec4 texColor = texture2D(uTexture, vTexCoord);
    float noise = texture2D(uNoiseTexture, vTexCoord).r;

    // Discard pixels below threshold
    if (noise < uDissolveAmount) {
        discard;
    }

    // Add glow at dissolve edge
    float edge = smoothstep(uDissolveAmount, uDissolveAmount + 0.1, noise);
    vec3 edgeColor = vec3(1.0, 0.5, 0.0); // Orange glow

    vec3 finalColor = mix(edgeColor, texColor.rgb, edge);

    gl_FragColor = vec4(finalColor, texColor.a);
}
```

**Visual Effect**: Object dissolves away with glowing orange edges, perfect for death animations or teleport effects.

### Example 4: Pixelation Effect

```glsl
precision mediump float;

varying vec2 vTexCoord;

uniform sampler2D uTexture;
uniform vec2 uResolution;
uniform float uPixelSize;

void main() {
    // Snap coordinates to pixel grid
    vec2 pixelCoord = floor(vTexCoord * uResolution / uPixelSize) * uPixelSize;
    pixelCoord /= uResolution;

    gl_FragColor = texture2D(uTexture, pixelCoord);
}
```

**Visual Effect**: Creates pixelated/mosaic look, useful for retro aesthetics or damage effects.

### Example 5: Outline Shader

```glsl
precision mediump float;

varying vec2 vTexCoord;

uniform sampler2D uTexture;
uniform vec2 uTexelSize;
uniform vec4 uOutlineColor;

void main() {
    vec4 center = texture2D(uTexture, vTexCoord);

    // Sample neighboring pixels
    float left = texture2D(uTexture, vTexCoord + vec2(-uTexelSize.x, 0.0)).a;
    float right = texture2D(uTexture, vTexCoord + vec2(uTexelSize.x, 0.0)).a;
    float top = texture2D(uTexture, vTexCoord + vec2(0.0, -uTexelSize.y)).a;
    float bottom = texture2D(uTexture, vTexCoord + vec2(0.0, uTexelSize.y)).a;

    // Detect edge
    float edge = (left + right + top + bottom) - (4.0 * center.a);

    if (abs(edge) > 0.1 && center.a < 0.5) {
        gl_FragColor = uOutlineColor;
    } else {
        gl_FragColor = center;
    }
}
```

**Visual Effect**: Adds colored outline around sprites, common in cartoon-style games.

## Advanced Visual Effects

### Water Shader

Complete water effect with waves, reflections, and transparency:

```glsl
// Vertex Shader
attribute vec3 aPosition;
attribute vec2 aTexCoord;

uniform mat4 uMVP;
uniform float uTime;

varying vec2 vTexCoord;
varying vec3 vWorldPos;

void main() {
    vec3 pos = aPosition;

    // Multi-frequency waves
    float wave1 = sin(pos.x * 2.0 + uTime * 2.0) * 0.1;
    float wave2 = sin(pos.z * 3.0 + uTime * 1.5) * 0.05;
    float wave3 = sin((pos.x + pos.z) * 4.0 + uTime * 3.0) * 0.03;

    pos.y += wave1 + wave2 + wave3;

    vWorldPos = pos;
    gl_Position = uMVP * vec4(pos, 1.0);
    vTexCoord = aTexCoord;
}
```

```glsl
// Fragment Shader
precision mediump float;

varying vec2 vTexCoord;
varying vec3 vWorldPos;

uniform sampler2D uWaterTexture;
uniform sampler2D uReflectionTexture;
uniform float uTime;
uniform vec3 uCameraPos;

void main() {
    // Animated water texture coordinates
    vec2 uv1 = vTexCoord + vec2(uTime * 0.03, uTime * 0.02);
    vec2 uv2 = vTexCoord + vec2(-uTime * 0.02, uTime * 0.04);

    // Sample water normal map twice for detail
    vec3 normal1 = texture2D(uWaterTexture, uv1).rgb * 2.0 - 1.0;
    vec3 normal2 = texture2D(uWaterTexture, uv2).rgb * 2.0 - 1.0;
    vec3 normal = normalize(normal1 + normal2);

    // Reflection with distortion
    vec2 reflectionUV = vTexCoord + normal.xy * 0.05;
    vec4 reflection = texture2D(uReflectionTexture, reflectionUV);

    // Fresnel effect (more reflective at grazing angles)
    vec3 viewDir = normalize(uCameraPos - vWorldPos);
    float fresnel = pow(1.0 - dot(viewDir, normal), 3.0);

    // Water color
    vec4 waterColor = vec4(0.1, 0.3, 0.5, 0.7);

    // Combine
    vec4 finalColor = mix(waterColor, reflection, fresnel * 0.6);

    gl_FragColor = finalColor;
}
```

**Visual Effect**: Realistic animated water with waves, reflections that distort with the surface, and Fresnel effect making edges more reflective.

### Fire Shader

Procedural fire effect:

```glsl
precision mediump float;

varying vec2 vTexCoord;

uniform float uTime;

// Noise function (Perlin-like)
float noise(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

float smoothNoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);

    float a = noise(i);
    float b = noise(i + vec2(1.0, 0.0));
    float c = noise(i + vec2(0.0, 1.0));
    float d = noise(i + vec2(1.0, 1.0));

    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fractalNoise(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;

    for (int i = 0; i < 5; i++) {
        value += amplitude * smoothNoise(p);
        p *= 2.0;
        amplitude *= 0.5;
    }

    return value;
}

void main() {
    vec2 uv = vTexCoord;

    // Create upward-flowing noise
    vec2 p = vec2(uv.x * 4.0, uv.y * 6.0 - uTime * 2.0);
    float n = fractalNoise(p);

    // Shape fire (narrow at top, wide at bottom)
    float fireShape = smoothstep(0.0, 0.3, uv.y) * smoothstep(1.0, 0.5, uv.y);
    fireShape *= smoothstep(0.0, 0.1, 0.5 - abs(uv.x - 0.5));

    // Combine noise with shape
    float fire = n * fireShape;

    // Fire colors (yellow -> orange -> red -> black)
    vec3 color = vec3(0.0);
    color = mix(color, vec3(1.0, 0.1, 0.0), smoothstep(0.0, 0.3, fire)); // Red
    color = mix(color, vec3(1.0, 0.5, 0.0), smoothstep(0.3, 0.5, fire)); // Orange
    color = mix(color, vec3(1.0, 1.0, 0.0), smoothstep(0.5, 0.8, fire)); // Yellow

    gl_FragColor = vec4(color, fire);
}
```

**Visual Effect**: Animated procedural fire with realistic color gradient and flowing motion.

### Cel Shading (Toon Shader)

```glsl
// Vertex Shader
attribute vec3 aPosition;
attribute vec3 aNormal;

uniform mat4 uModelMatrix;
uniform mat4 uViewMatrix;
uniform mat4 uProjectionMatrix;
uniform mat4 uNormalMatrix;

varying vec3 vNormal;
varying vec3 vViewDir;

void main() {
    vec4 worldPos = uModelMatrix * vec4(aPosition, 1.0);
    vec4 viewPos = uViewMatrix * worldPos;

    gl_Position = uProjectionMatrix * viewPos;

    vNormal = normalize((uNormalMatrix * vec4(aNormal, 0.0)).xyz);
    vViewDir = normalize(-viewPos.xyz);
}
```

```glsl
// Fragment Shader
precision mediump float;

varying vec3 vNormal;
varying vec3 vViewDir;

uniform vec3 uLightDir;
uniform vec3 uObjectColor;
uniform vec3 uOutlineColor;

void main() {
    vec3 normal = normalize(vNormal);

    // Diffuse lighting
    float diffuse = max(dot(normal, uLightDir), 0.0);

    // Quantize to discrete levels (cel shading)
    float intensity = 0.0;
    if (diffuse > 0.95) intensity = 1.0;
    else if (diffuse > 0.5) intensity = 0.6;
    else if (diffuse > 0.25) intensity = 0.4;
    else intensity = 0.2;

    vec3 color = uObjectColor * intensity;

    // Rim lighting for outline effect
    float rim = 1.0 - max(dot(vViewDir, normal), 0.0);
    rim = smoothstep(0.6, 1.0, rim);

    color = mix(color, uOutlineColor, rim);

    gl_FragColor = vec4(color, 1.0);
}
```

**Visual Effect**: Cartoon-style shading with distinct color bands and rim lighting, popular in cel-shaded games.

### Chromatic Aberration

```glsl
precision mediump float;

varying vec2 vTexCoord;

uniform sampler2D uTexture;
uniform float uAberrationAmount;

void main() {
    // Offset each color channel
    vec2 offset = (vTexCoord - 0.5) * uAberrationAmount;

    float r = texture2D(uTexture, vTexCoord + offset).r;
    float g = texture2D(uTexture, vTexCoord).g;
    float b = texture2D(uTexture, vTexCoord - offset).b;

    gl_FragColor = vec4(r, g, b, 1.0);
}
```

**Visual Effect**: Color fringing effect like old cameras, adds retro or damaged look.

### Blur Effect

```glsl
precision mediump float;

varying vec2 vTexCoord;

uniform sampler2D uTexture;
uniform vec2 uTexelSize;
uniform float uBlurAmount;

void main() {
    vec4 color = vec4(0.0);

    // 9-tap gaussian blur
    float weights[9];
    weights[0] = 0.05; weights[1] = 0.09; weights[2] = 0.05;
    weights[3] = 0.09; weights[4] = 0.20; weights[5] = 0.09;
    weights[6] = 0.05; weights[7] = 0.09; weights[8] = 0.05;

    int index = 0;
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 offset = vec2(float(x), float(y)) * uTexelSize * uBlurAmount;
            color += texture2D(uTexture, vTexCoord + offset) * weights[index];
            index++;
        }
    }

    gl_FragColor = color;
}
```

**Visual Effect**: Gaussian blur, useful for depth of field or motion blur effects.

### Bloom Effect

```glsl
precision mediump float;

varying vec2 vTexCoord;

uniform sampler2D uTexture;
uniform sampler2D uBlurredTexture;
uniform float uBloomIntensity;
uniform float uBloomThreshold;

void main() {
    vec4 original = texture2D(uTexture, vTexCoord);
    vec4 blurred = texture2D(uBlurredTexture, vTexCoord);

    // Extract bright areas
    float brightness = dot(original.rgb, vec3(0.2126, 0.7152, 0.0722));
    float bloomFactor = smoothstep(uBloomThreshold, uBloomThreshold + 0.5, brightness);

    // Combine
    vec3 bloom = blurred.rgb * bloomFactor * uBloomIntensity;
    vec3 result = original.rgb + bloom;

    gl_FragColor = vec4(result, original.a);
}
```

**Visual Effect**: Bright areas glow and bleed into surrounding pixels, creating ethereal lighting.

## Debugging Shader Code with AI

Shader debugging is notoriously difficult. Here's how Claude Code helps:

**Visualization Debugging:**
```
My shader isn't working correctly. Here's the code: [paste shader]
The expected output is [description], but I'm seeing [actual output].
Help me debug by adding visualization code to check intermediate values.
```

Claude Code will add visualization shaders that output intermediate calculations as colors, making it easy to see where things go wrong.

**Performance Debugging:**
```
This shader runs slowly on mobile devices: [paste shader]
Identify performance issues and suggest optimizations.
```

**Common Issues Claude Code Catches:**
- Division by zero creating NaN/Inf
- Precision issues with mediump/lowp
- Expensive operations in loops
- Missing normalization
- Incorrect matrix multiplication order
- Texture sampling outside [0,1] range

## Complete Shader Integration Example

Here's how to integrate custom shaders into a game:

```javascript
class ShaderMaterial {
    constructor(gl, vertexSource, fragmentSource) {
        this.gl = gl;
        this.program = this.createProgram(vertexSource, fragmentSource);
        this.uniforms = {};
        this.attributes = {};

        this.extractUniforms();
        this.extractAttributes();
    }

    createProgram(vertSource, fragSource) {
        const vertShader = this.compileShader(this.gl.VERTEX_SHADER, vertSource);
        const fragShader = this.compileShader(this.gl.FRAGMENT_SHADER, fragSource);

        const program = this.gl.createProgram();
        this.gl.attachShader(program, vertShader);
        this.gl.attachShader(program, fragShader);
        this.gl.linkProgram(program);

        if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS)) {
            throw new Error('Program link failed: ' + this.gl.getProgramInfoLog(program));
        }

        return program;
    }

    compileShader(type, source) {
        const shader = this.gl.createShader(type);
        this.gl.shaderSource(shader, source);
        this.gl.compileShader(shader);

        if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
            const error = this.gl.getShaderInfoLog(shader);
            this.gl.deleteShader(shader);
            throw new Error('Shader compilation failed: ' + error);
        }

        return shader;
    }

    extractUniforms() {
        const count = this.gl.getProgramParameter(this.program, this.gl.ACTIVE_UNIFORMS);
        for (let i = 0; i < count; i++) {
            const info = this.gl.getActiveUniform(this.program, i);
            this.uniforms[info.name] = this.gl.getUniformLocation(this.program, info.name);
        }
    }

    extractAttributes() {
        const count = this.gl.getProgramParameter(this.program, this.gl.ACTIVE_ATTRIBUTES);
        for (let i = 0; i < count; i++) {
            const info = this.gl.getActiveAttrib(this.program, i);
            this.attributes[info.name] = this.gl.getAttribLocation(this.program, info.name);
        }
    }

    use() {
        this.gl.useProgram(this.program);
    }

    setUniform(name, value) {
        const location = this.uniforms[name];
        if (location === undefined) return;

        if (typeof value === 'number') {
            this.gl.uniform1f(location, value);
        } else if (value instanceof Float32Array) {
            if (value.length === 16) {
                this.gl.uniformMatrix4fv(location, false, value);
            } else if (value.length === 9) {
                this.gl.uniformMatrix3fv(location, false, value);
            } else if (value.length === 4) {
                this.gl.uniform4fv(location, value);
            } else if (value.length === 3) {
                this.gl.uniform3fv(location, value);
            } else if (value.length === 2) {
                this.gl.uniform2fv(location, value);
            }
        } else if (value.isTexture) {
            // Handle texture binding
            this.gl.activeTexture(this.gl.TEXTURE0 + value.unit);
            this.gl.bindTexture(this.gl.TEXTURE_2D, value.texture);
            this.gl.uniform1i(location, value.unit);
        }
    }

    setUniforms(uniforms) {
        Object.keys(uniforms).forEach(name => {
            this.setUniform(name, uniforms[name]);
        });
    }
}

// Usage in game
const waterShader = new ShaderMaterial(gl, waterVertexShader, waterFragmentShader);

function renderWater(time) {
    waterShader.use();
    waterShader.setUniforms({
        uMVP: mvpMatrix,
        uTime: time,
        uCameraPos: new Float32Array([camera.x, camera.y, camera.z]),
        uWaterTexture: { texture: waterNormalTexture, unit: 0, isTexture: true },
        uReflectionTexture: { texture: reflectionTexture, unit: 1, isTexture: true }
    });

    // Bind geometry and draw
    waterMesh.draw();
}
```

## Claude Code Prompts for Shader Development

**Creating Effects:**
```
Create a GLSL shader that produces a holographic effect with scan lines,
color shifting, and flickering. Include both vertex and fragment shaders.
```

**Optimization:**
```
Optimize this shader for mobile devices. It currently runs at 30 FPS
on mid-range phones: [paste shader code]
```

**Debugging:**
```
This shader produces black output instead of the expected glow effect.
Debug it and explain what's wrong: [paste shader]
```

**Learning:**
```
Explain how this water shader works line by line, including the math
behind the Fresnel effect: [paste shader]
```

**Variations:**
```
I have this fire shader. Create 3 variations: ice, electric, and poison effects
by modifying colors and animation: [paste shader]
```

## Performance Considerations

**Mobile Optimization:**
- Use `mediump` precision instead of `highp`
- Minimize texture samples (expensive on mobile)
- Avoid loops when possible
- Use built-in functions (faster than custom)
- Reduce fragment shader complexity (runs per-pixel!)

**Desktop Optimization:**
- Batch objects using same shader
- Minimize uniform updates
- Use texture atlases to reduce texture switches
- Consider compute shaders for complex calculations (WebGL 2)

## Next Steps

Master shader programming, and you unlock unlimited visual possibilities:

- **[Particle Systems](./particle-systems.md)**: Use shaders for GPU particle effects
- **[Lighting and Shadows](./lighting-shadows.md)**: Advanced lighting shaders
- **[Post-Processing Effects](./post-processing-effects.md)**: Screen-space shader effects

Shaders are where art meets code. With Claude Code as your guide, you'll create stunning visual effects that bring your games to life!
