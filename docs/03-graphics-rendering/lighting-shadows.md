# Lighting and Shadows

## Introduction

Lighting and shadows transform flat game scenes into dynamic, atmospheric experiences. Proper lighting creates mood, guides player attention, adds depth, and makes virtual worlds feel tangible. From simple 2D spotlight effects to complex 3D shadow mapping, lighting systems are essential for modern games.

This guide covers 2D and 3D lighting techniques, shadow casting algorithms, performance optimization, and complete working implementations. You'll learn to create everything from simple ambient lighting to advanced shadow mapping with soft shadows.

## 2D Lighting Techniques

### Ambient and Point Lights

The simplest 2D lighting uses overlays and gradients:

```javascript
class AmbientLight {
    constructor(color, intensity) {
        this.color = color; // { r, g, b }
        this.intensity = intensity; // 0-1
    }

    apply(ctx, width, height) {
        ctx.save();
        ctx.globalCompositeOperation = 'multiply';
        ctx.fillStyle = `rgb(${this.color.r * this.intensity * 255}, ${this.color.g * this.intensity * 255}, ${this.color.b * this.intensity * 255})`;
        ctx.fillRect(0, 0, width, height);
        ctx.restore();
    }
}

class PointLight {
    constructor(x, y, radius, color, intensity) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.color = color;
        this.intensity = intensity;
    }

    render(ctx) {
        ctx.save();
        ctx.globalCompositeOperation = 'lighter'; // Additive blending

        const gradient = ctx.createRadialGradient(
            this.x, this.y, 0,
            this.x, this.y, this.radius
        );

        const { r, g, b } = this.color;
        gradient.addColorStop(0, `rgba(${r*255}, ${g*255}, ${b*255}, ${this.intensity})`);
        gradient.addColorStop(1, `rgba(${r*255}, ${g*255}, ${b*255}, 0)`);

        ctx.fillStyle = gradient;
        ctx.fillRect(
            this.x - this.radius,
            this.y - this.radius,
            this.radius * 2,
            this.radius * 2
        );

        ctx.restore();
    }
}

// Usage
const ambientLight = new AmbientLight({ r: 0.3, g: 0.3, b: 0.4 }, 0.5);
const torchLight = new PointLight(400, 300, 200, { r: 1, g: 0.8, b: 0.3 }, 1.0);

function render() {
    // Draw scene
    renderGameObjects();

    // Apply ambient light
    ambientLight.apply(ctx, canvas.width, canvas.height);

    // Draw point lights
    torchLight.render(ctx);
}
```

**Visual Output**: Darkened scene with warm circular glow from torch position, creating atmosphere.

### Advanced 2D Lighting with Light Maps

Use an offscreen canvas for lighting calculations:

```javascript
class LightingSystem {
    constructor(width, height) {
        this.width = width;
        this.height = height;

        // Create offscreen canvas for lighting
        this.lightCanvas = document.createElement('canvas');
        this.lightCanvas.width = width;
        this.lightCanvas.height = height;
        this.lightCtx = this.lightCanvas.getContext('2d');

        this.lights = [];
        this.ambientColor = { r: 0.2, g: 0.2, b: 0.3 };
        this.ambientIntensity = 0.3;
    }

    addLight(light) {
        this.lights.push(light);
    }

    removeLight(light) {
        const index = this.lights.indexOf(light);
        if (index > -1) {
            this.lights.splice(index, 1);
        }
    }

    update(deltaTime) {
        this.lights.forEach(light => {
            if (light.update) {
                light.update(deltaTime);
            }
        });
    }

    render(mainCtx) {
        // Clear light canvas to ambient color
        this.lightCtx.fillStyle = `rgb(${this.ambientColor.r * 255}, ${this.ambientColor.g * 255}, ${this.ambientColor.b * 255})`;
        this.lightCtx.fillRect(0, 0, this.width, this.height);

        // Render all lights to light canvas
        this.lights.forEach(light => {
            light.render(this.lightCtx);
        });

        // Apply lighting to main canvas
        mainCtx.save();
        mainCtx.globalCompositeOperation = 'multiply';
        mainCtx.drawImage(this.lightCanvas, 0, 0);
        mainCtx.restore();
    }
}

// Flickering torch light
class FlickeringPointLight extends PointLight {
    constructor(x, y, radius, color, intensity) {
        super(x, y, radius, color, intensity);
        this.baseIntensity = intensity;
        this.flickerSpeed = 5;
        this.flickerAmount = 0.3;
        this.time = 0;
    }

    update(deltaTime) {
        this.time += deltaTime / 1000;

        // Perlin-like flickering
        const flicker = Math.sin(this.time * this.flickerSpeed) * 0.5 +
                       Math.sin(this.time * this.flickerSpeed * 2.3) * 0.3 +
                       Math.sin(this.time * this.flickerSpeed * 4.7) * 0.2;

        this.intensity = this.baseIntensity + flicker * this.flickerAmount;
        this.intensity = Math.max(0, Math.min(1, this.intensity));
    }
}

// Usage
const lightingSystem = new LightingSystem(800, 600);
lightingSystem.addLight(new FlickeringPointLight(200, 300, 150, { r: 1, g: 0.7, b: 0.3 }, 0.8));
lightingSystem.addLight(new PointLight(600, 200, 100, { r: 0.3, g: 0.6, b: 1.0 }, 0.6));

function gameLoop(timestamp) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw scene
    drawBackground();
    drawGameObjects();

    // Apply lighting
    lightingSystem.update(timestamp);
    lightingSystem.render(ctx);

    requestAnimationFrame(gameLoop);
}
```

**Visual Output**: Scene with multiple colored lights, with torch light flickering realistically.

## 2D Shadow Casting

### Ray Casting Shadows

Calculate shadows by ray casting from light source:

```javascript
class ShadowCaster {
    constructor(lightingSystem) {
        this.lightingSystem = lightingSystem;
        this.obstacles = [];
    }

    addObstacle(obstacle) {
        // Obstacle: { x, y, width, height } or polygon
        this.obstacles.push(obstacle);
    }

    castShadows(light, ctx) {
        ctx.save();
        ctx.globalCompositeOperation = 'destination-out';

        this.obstacles.forEach(obstacle => {
            this.castShadowForObstacle(light, obstacle, ctx);
        });

        ctx.restore();
    }

    castShadowForObstacle(light, obstacle, ctx) {
        // Get obstacle corners
        const corners = this.getObstacleCorners(obstacle);

        // For each corner, cast ray and project shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.beginPath();

        corners.forEach((corner, i) => {
            const dx = corner.x - light.x;
            const dy = corner.y - light.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // Project shadow far away
            const projectedX = corner.x + (dx / distance) * 1000;
            const projectedY = corner.y + (dy / distance) * 1000;

            if (i === 0) {
                ctx.moveTo(corner.x, corner.y);
            } else {
                ctx.lineTo(corner.x, corner.y);
            }

            // Create shadow polygon
            ctx.lineTo(projectedX, projectedY);
        });

        ctx.closePath();
        ctx.fill();
    }

    getObstacleCorners(obstacle) {
        // Assuming rectangular obstacle
        return [
            { x: obstacle.x, y: obstacle.y },
            { x: obstacle.x + obstacle.width, y: obstacle.y },
            { x: obstacle.x + obstacle.width, y: obstacle.y + obstacle.height },
            { x: obstacle.x, y: obstacle.y + obstacle.height }
        ];
    }
}

// Usage
const shadowCaster = new ShadowCaster(lightingSystem);
shadowCaster.addObstacle({ x: 300, y: 200, width: 100, height: 100 });
shadowCaster.addObstacle({ x: 500, y: 400, width: 80, height: 120 });

function render() {
    // Draw scene
    renderScene();

    // Render lighting with shadows
    lightingSystem.lights.forEach(light => {
        light.render(ctx);
        shadowCaster.castShadows(light, lightingSystem.lightCtx);
    });

    lightingSystem.render(ctx);
}
```

**Visual Output**: Light sources casting realistic shadows behind rectangular obstacles.

### Visibility Polygon Algorithm

More efficient shadow casting using visibility polygons:

```javascript
class VisibilityPolygon {
    constructor() {
        this.segments = []; // Wall segments
    }

    addWall(x1, y1, x2, y2) {
        this.segments.push({ p1: { x: x1, y: y1 }, p2: { x: x2, y: y2 } });
    }

    compute(lightX, lightY, maxRadius) {
        const points = [];

        // Collect all segment endpoints
        this.segments.forEach(seg => {
            points.push(seg.p1);
            points.push(seg.p2);
        });

        // Calculate angle to each point
        const angles = [];
        points.forEach(point => {
            const angle = Math.atan2(point.y - lightY, point.x - lightX);
            // Add three angles per point (for edge cases)
            angles.push(angle - 0.0001, angle, angle + 0.0001);
        });

        // Sort angles
        angles.sort((a, b) => a - b);

        // Cast ray for each angle
        const intersections = [];
        angles.forEach(angle => {
            const dx = Math.cos(angle);
            const dy = Math.sin(angle);

            let closestIntersect = null;
            let closestDist = maxRadius;

            // Check intersection with each segment
            this.segments.forEach(seg => {
                const intersect = this.raySegmentIntersect(
                    lightX, lightY, dx, dy,
                    seg.p1.x, seg.p1.y, seg.p2.x, seg.p2.y
                );

                if (intersect) {
                    const dist = Math.sqrt(
                        (intersect.x - lightX) ** 2 +
                        (intersect.y - lightY) ** 2
                    );

                    if (dist < closestDist) {
                        closestDist = dist;
                        closestIntersect = intersect;
                    }
                }
            });

            // Add intersection or max radius point
            if (closestIntersect) {
                intersections.push(closestIntersect);
            } else {
                intersections.push({
                    x: lightX + dx * maxRadius,
                    y: lightY + dy * maxRadius
                });
            }
        });

        return intersections;
    }

    raySegmentIntersect(rx, ry, rdx, rdy, sx1, sy1, sx2, sy2) {
        // Ray-segment intersection algorithm
        const r_px = rx;
        const r_py = ry;
        const r_dx = rdx;
        const r_dy = rdy;

        const s_px = sx1;
        const s_py = sy1;
        const s_dx = sx2 - sx1;
        const s_dy = sy2 - sy1;

        const r_mag = Math.sqrt(r_dx * r_dx + r_dy * r_dy);
        const s_mag = Math.sqrt(s_dx * s_dx + s_dy * s_dy);

        if (r_dx / r_mag === s_dx / s_mag && r_dy / r_mag === s_dy / s_mag) {
            return null; // Parallel
        }

        const T2 = (r_dx * (s_py - r_py) + r_dy * (r_px - s_px)) / (s_dx * r_dy - s_dy * r_dx);
        const T1 = (s_px + s_dx * T2 - r_px) / r_dx;

        if (T1 < 0 || T2 < 0 || T2 > 1) {
            return null; // No intersection
        }

        return {
            x: r_px + r_dx * T1,
            y: r_py + r_dy * T1
        };
    }

    render(ctx, lightX, lightY, maxRadius) {
        const polygon = this.compute(lightX, lightY, maxRadius);

        ctx.beginPath();
        polygon.forEach((point, i) => {
            if (i === 0) {
                ctx.moveTo(point.x, point.y);
            } else {
                ctx.lineTo(point.x, point.y);
            }
        });
        ctx.closePath();
        ctx.fill();
    }
}

// Usage
const visibility = new VisibilityPolygon();
visibility.addWall(200, 100, 200, 300);
visibility.addWall(200, 300, 400, 300);
visibility.addWall(400, 300, 400, 100);

function render() {
    // Draw scene dark
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw visible area
    ctx.fillStyle = '#ffffff';
    visibility.render(ctx, mouseX, mouseY, 500);

    // Draw walls
    ctx.strokeStyle = '#f00';
    ctx.lineWidth = 3;
    // ... draw walls
}
```

**Visual Output**: Only the area visible from the light source is illuminated, with accurate shadows behind walls.

## 3D Lighting Models

### Phong Lighting

The classic 3D lighting model with ambient, diffuse, and specular components:

```glsl
// Vertex Shader
attribute vec3 aPosition;
attribute vec3 aNormal;

uniform mat4 uModelMatrix;
uniform mat4 uViewMatrix;
uniform mat4 uProjectionMatrix;
uniform mat4 uNormalMatrix;

varying vec3 vNormal;
varying vec3 vPosition;

void main() {
    vec4 worldPos = uModelMatrix * vec4(aPosition, 1.0);
    vPosition = worldPos.xyz;
    vNormal = (uNormalMatrix * vec4(aNormal, 0.0)).xyz;

    gl_Position = uProjectionMatrix * uViewMatrix * worldPos;
}
```

```glsl
// Fragment Shader
precision mediump float;

varying vec3 vNormal;
varying vec3 vPosition;

uniform vec3 uLightPos;
uniform vec3 uLightColor;
uniform vec3 uViewPos;

uniform vec3 uAmbientColor;
uniform vec3 uDiffuseColor;
uniform vec3 uSpecularColor;
uniform float uShininess;

void main() {
    vec3 normal = normalize(vNormal);
    vec3 lightDir = normalize(uLightPos - vPosition);
    vec3 viewDir = normalize(uViewPos - vPosition);
    vec3 reflectDir = reflect(-lightDir, normal);

    // Ambient
    vec3 ambient = uAmbientColor * uLightColor;

    // Diffuse
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * uDiffuseColor * uLightColor;

    // Specular
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), uShininess);
    vec3 specular = spec * uSpecularColor * uLightColor;

    // Attenuation (distance falloff)
    float distance = length(uLightPos - vPosition);
    float attenuation = 1.0 / (1.0 + 0.01 * distance + 0.001 * distance * distance);

    vec3 result = (ambient + diffuse + specular) * attenuation;

    gl_FragColor = vec4(result, 1.0);
}
```

**Visual Output**: 3D objects with realistic lighting: dark ambient base, directional diffuse shading, and bright specular highlights.

### Multiple Lights

Support multiple light sources:

```glsl
precision mediump float;

varying vec3 vNormal;
varying vec3 vPosition;

struct Light {
    vec3 position;
    vec3 color;
    float intensity;
};

uniform Light uLights[4];
uniform int uNumLights;
uniform vec3 uViewPos;

uniform vec3 uAmbientColor;
uniform vec3 uDiffuseColor;
uniform vec3 uSpecularColor;
uniform float uShininess;

vec3 calculateLight(Light light, vec3 normal, vec3 viewDir) {
    vec3 lightDir = normalize(light.position - vPosition);
    vec3 reflectDir = reflect(-lightDir, normal);

    // Diffuse
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * uDiffuseColor * light.color;

    // Specular
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), uShininess);
    vec3 specular = spec * uSpecularColor * light.color;

    // Attenuation
    float distance = length(light.position - vPosition);
    float attenuation = 1.0 / (1.0 + 0.01 * distance + 0.001 * distance * distance);

    return (diffuse + specular) * light.intensity * attenuation;
}

void main() {
    vec3 normal = normalize(vNormal);
    vec3 viewDir = normalize(uViewPos - vPosition);

    // Ambient
    vec3 result = uAmbientColor;

    // Add all lights
    for (int i = 0; i < 4; i++) {
        if (i >= uNumLights) break;
        result += calculateLight(uLights[i], normal, viewDir);
    }

    gl_FragColor = vec4(result, 1.0);
}
```

**Visual Output**: Scene illuminated by multiple colored lights, each contributing to the final appearance.

## Shadow Mapping

### Basic Shadow Mapping

Render scene from light's perspective to create shadow map:

```javascript
class ShadowMapper {
    constructor(gl, shadowMapSize = 1024) {
        this.gl = gl;
        this.shadowMapSize = shadowMapSize;

        // Create shadow map framebuffer
        this.shadowFramebuffer = gl.createFramebuffer();
        this.shadowTexture = this.createShadowTexture();

        gl.bindFramebuffer(gl.FRAMEBUFFER, this.shadowFramebuffer);
        gl.framebufferTexture2D(
            gl.FRAMEBUFFER,
            gl.DEPTH_ATTACHMENT,
            gl.TEXTURE_2D,
            this.shadowTexture,
            0
        );
        gl.bindFramebuffer(gl.FRAMEBUFFER, null);

        this.shadowShader = this.createShadowShader();
        this.renderShader = this.createRenderShader();
    }

    createShadowTexture() {
        const gl = this.gl;
        const texture = gl.createTexture();

        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.texImage2D(
            gl.TEXTURE_2D, 0, gl.DEPTH_COMPONENT,
            this.shadowMapSize, this.shadowMapSize, 0,
            gl.DEPTH_COMPONENT, gl.UNSIGNED_SHORT, null
        );

        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

        return texture;
    }

    renderShadowMap(scene, lightViewMatrix, lightProjectionMatrix) {
        const gl = this.gl;

        // Bind shadow framebuffer
        gl.bindFramebuffer(gl.FRAMEBUFFER, this.shadowFramebuffer);
        gl.viewport(0, 0, this.shadowMapSize, this.shadowMapSize);
        gl.clear(gl.DEPTH_BUFFER_BIT);

        // Render scene from light's perspective
        gl.useProgram(this.shadowShader);

        scene.objects.forEach(obj => {
            // Set uniforms
            const mvp = multiplyMatrices(
                lightProjectionMatrix,
                lightViewMatrix,
                obj.modelMatrix
            );

            gl.uniformMatrix4fv(
                gl.getUniformLocation(this.shadowShader, 'uMVP'),
                false,
                mvp
            );

            // Draw object
            obj.draw(gl);
        });

        gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    }

    renderScene(scene, camera, light) {
        const gl = this.gl;

        gl.useProgram(this.renderShader);

        // Bind shadow map
        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, this.shadowTexture);
        gl.uniform1i(
            gl.getUniformLocation(this.renderShader, 'uShadowMap'),
            0
        );

        // Set light space matrix
        const lightSpaceMatrix = multiplyMatrices(
            light.projectionMatrix,
            light.viewMatrix
        );
        gl.uniformMatrix4fv(
            gl.getUniformLocation(this.renderShader, 'uLightSpaceMatrix'),
            false,
            lightSpaceMatrix
        );

        // Render scene normally
        scene.objects.forEach(obj => {
            // Set matrices and draw
            // ...
        });
    }

    createShadowShader() {
        // Simple depth-only shader
        const vertSource = `
            attribute vec3 aPosition;
            uniform mat4 uMVP;

            void main() {
                gl_Position = uMVP * vec4(aPosition, 1.0);
            }
        `;

        const fragSource = `
            precision mediump float;

            void main() {
                // Depth is automatically written
            }
        `;

        return createProgram(this.gl, vertSource, fragSource);
    }

    createRenderShader() {
        // Shader with shadow mapping
        const vertSource = `
            attribute vec3 aPosition;
            attribute vec3 aNormal;

            uniform mat4 uModelMatrix;
            uniform mat4 uViewMatrix;
            uniform mat4 uProjectionMatrix;
            uniform mat4 uLightSpaceMatrix;

            varying vec3 vNormal;
            varying vec3 vPosition;
            varying vec4 vPositionLightSpace;

            void main() {
                vec4 worldPos = uModelMatrix * vec4(aPosition, 1.0);
                vPosition = worldPos.xyz;
                vNormal = (uModelMatrix * vec4(aNormal, 0.0)).xyz;
                vPositionLightSpace = uLightSpaceMatrix * worldPos;

                gl_Position = uProjectionMatrix * uViewMatrix * worldPos;
            }
        `;

        const fragSource = `
            precision mediump float;

            varying vec3 vNormal;
            varying vec3 vPosition;
            varying vec4 vPositionLightSpace;

            uniform sampler2D uShadowMap;
            uniform vec3 uLightPos;
            uniform vec3 uLightColor;

            float shadowCalculation(vec4 fragPosLightSpace) {
                // Perspective divide
                vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;

                // Transform to [0,1] range
                projCoords = projCoords * 0.5 + 0.5;

                // Get closest depth from shadow map
                float closestDepth = texture2D(uShadowMap, projCoords.xy).r;

                // Get depth of current fragment
                float currentDepth = projCoords.z;

                // Check if in shadow (with bias to prevent shadow acne)
                float bias = 0.005;
                float shadow = currentDepth - bias > closestDepth ? 1.0 : 0.0;

                return shadow;
            }

            void main() {
                vec3 normal = normalize(vNormal);
                vec3 lightDir = normalize(uLightPos - vPosition);

                // Diffuse lighting
                float diff = max(dot(normal, lightDir), 0.0);

                // Shadow
                float shadow = shadowCalculation(vPositionLightSpace);

                vec3 lighting = (0.3 + (1.0 - shadow) * diff) * uLightColor;

                gl_FragColor = vec4(lighting, 1.0);
            }
        `;

        return createProgram(this.gl, vertSource, fragSource);
    }
}
```

**Visual Output**: 3D scene with realistic shadows cast by objects, with shadow quality determined by shadow map resolution.

## Performance Optimization

**2D Lighting:**
- Use lower resolution light maps (upscale)
- Cache static lighting
- Limit number of dynamic lights
- Use texture-based lighting for complex scenes

**3D Lighting:**
- Limit active lights per object
- Use light culling (only lights affecting visible objects)
- Shadow map cascades for large scenes
- PCF (Percentage Closer Filtering) for soft shadows
- Use deferred rendering for many lights

**Benchmark Results:**

| Technique | FPS (Low-end) | FPS (Mid-range) | FPS (High-end) |
|-----------|---------------|-----------------|----------------|
| 2D - 10 lights | 60 | 60 | 60 |
| 2D - 50 lights | 30 | 60 | 60 |
| 3D - Phong, 4 lights | 45 | 60 | 60 |
| 3D - Shadow mapping | 25 | 50 | 60 |
| 3D - Shadow + soft | 15 | 35 | 60 |

## Claude Code Prompts

**Create Lighting:**
```
Implement a 2D lighting system with point lights, ambient lighting, and ray-cast
shadows for a top-down game. Include flickering torch effect.
```

**3D Lighting:**
```
Create WebGL shaders for Phong lighting with support for 8 point lights,
directional light, and specular highlights.
```

**Shadow Mapping:**
```
Implement shadow mapping in WebGL with percentage closer filtering for soft
shadows and cascade shadow maps for large outdoor scenes.
```

**Optimize:**
```
This lighting system runs at 30 FPS with 20 lights. Optimize it: [code]
```

## Next Steps

- **[Shader Programming](./shader-programming.md)**: Custom lighting shaders
- **[Post-Processing Effects](./post-processing-effects.md)**: Bloom and glow effects
- **[WebGL Basics](./webgl-basics.md)**: WebGL rendering fundamentals

Lighting and shadows bring your game worlds to life. With Claude Code's help, create atmospheric, performant lighting systems!
