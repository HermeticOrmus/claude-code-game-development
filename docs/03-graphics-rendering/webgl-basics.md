# WebGL Basics

## Introduction

WebGL (Web Graphics Library) is a JavaScript API that provides hardware-accelerated 2D and 3D graphics rendering directly in web browsers without requiring plugins. Built on OpenGL ES 2.0/3.0, WebGL leverages your GPU to render complex scenes with millions of triangles, sophisticated lighting, and advanced visual effects—all at 60+ FPS. While more complex than Canvas 2D, WebGL unlocks rendering capabilities impossible with traditional APIs.

This guide demystifies WebGL, starting with fundamental concepts and building toward practical game rendering systems. We'll cover the rendering pipeline, shaders, buffers, textures, and optimization techniques, with complete working examples you can use as foundations for your games.

## Why WebGL for Games?

**Performance**: WebGL runs on the GPU, processing thousands of vertices and pixels in parallel. A mid-range GPU can render 100,000+ triangles per frame at 60 FPS, while Canvas 2D struggles with 1,000+ complex sprites.

**3D Rendering**: True 3D with perspective projection, depth testing, and 3D transformations. Essential for first-person shooters, racing games, flight simulators, and any game requiring camera movement through 3D space.

**Advanced Effects**: Custom shaders enable effects impossible in Canvas: realistic lighting, shadows, reflections, post-processing, procedural textures, and more.

**2D Acceleration**: WebGL excels at 2D rendering too, using batching and instancing to render thousands of sprites faster than Canvas.

**Cross-Platform**: WebGL runs on desktop, mobile, and tablets with consistent performance characteristics.

## WebGL vs Canvas 2D Performance

| Scenario | Canvas 2D FPS | WebGL FPS | Winner |
|----------|---------------|-----------|--------|
| 100 sprites | 60 | 60 | Tie |
| 1,000 sprites | 45 | 60 | WebGL |
| 10,000 sprites | 5 | 60 | WebGL |
| 3D scene (1000 triangles) | N/A | 60 | WebGL |
| Complex particle system | 30 | 60 | WebGL |
| Post-processing effects | 20 | 60 | WebGL |

WebGL shines when you need many draw calls, 3D rendering, or advanced visual effects.

## WebGL Fundamentals

### The Graphics Pipeline

WebGL follows a fixed pipeline that transforms 3D coordinates into 2D pixels:

1. **Vertex Shader**: Processes each vertex, transforming 3D positions to screen space
2. **Primitive Assembly**: Connects vertices into triangles
3. **Rasterization**: Determines which pixels each triangle covers
4. **Fragment Shader**: Computes color for each pixel
5. **Output**: Writes final colors to framebuffer (screen)

Understanding this pipeline is key to WebGL mastery.

### Setup and Context Creation

```javascript
const canvas = document.getElementById('glCanvas');
const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');

if (!gl) {
    console.error('WebGL not supported');
    // Fallback to Canvas 2D
}

// Set canvas size
canvas.width = 800;
canvas.height = 600;

// Set viewport
gl.viewport(0, 0, canvas.width, canvas.height);

// Set clear color (background)
gl.clearColor(0.0, 0.0, 0.0, 1.0); // Black

// Enable depth testing (for 3D)
gl.enable(gl.DEPTH_TEST);

// Clear the canvas
gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
```

WebGL 2.0 offers significant improvements over 1.0 (more features, better performance). Always try to get `webgl2` context first.

### Handling Context Loss

WebGL contexts can be lost (GPU crash, system sleep, etc.). Robust games handle this:

```javascript
canvas.addEventListener('webglcontextlost', (event) => {
    event.preventDefault();
    console.log('WebGL context lost');
    cancelAnimationFrame(animationId);
}, false);

canvas.addEventListener('webglcontextrestored', () => {
    console.log('WebGL context restored');
    initWebGL(); // Recreate all resources
    startRenderLoop();
}, false);
```

## Shaders: The Heart of WebGL

Shaders are programs that run on the GPU, written in GLSL (OpenGL Shading Language). Every WebGL program needs at least two shaders:

### Vertex Shader

Processes each vertex, transforming positions:

```glsl
// Vertex shader
attribute vec3 aPosition;
attribute vec2 aTexCoord;

uniform mat4 uModelViewMatrix;
uniform mat4 uProjectionMatrix;

varying vec2 vTexCoord;

void main() {
    gl_Position = uProjectionMatrix * uModelViewMatrix * vec4(aPosition, 1.0);
    vTexCoord = aTexCoord;
}
```

**Attributes**: Per-vertex data (position, color, texture coordinates)
**Uniforms**: Data shared across all vertices (matrices, time, colors)
**Varyings**: Data passed to fragment shader (interpolated across triangle)

### Fragment Shader

Computes color for each pixel:

```glsl
// Fragment shader
precision mediump float;

varying vec2 vTexCoord;
uniform sampler2D uTexture;

void main() {
    gl_FragColor = texture2D(uTexture, vTexCoord);
}
```

**precision**: Defines float precision (lowp, mediump, highp)
**sampler2D**: Texture sampler
**gl_FragColor**: Output color for this pixel

### Shader Compilation and Linking

```javascript
function createShader(gl, type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);

    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
    }

    return shader;
}

function createProgram(gl, vertexShaderSource, fragmentShaderSource) {
    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

    const program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error('Program linking error:', gl.getProgramInfoLog(program));
        gl.deleteProgram(program);
        return null;
    }

    return program;
}

// Usage
const vertSource = `
    attribute vec3 aPosition;
    void main() {
        gl_Position = vec4(aPosition, 1.0);
    }
`;

const fragSource = `
    precision mediump float;
    void main() {
        gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); // Red
    }
`;

const program = createProgram(gl, vertSource, fragSource);
gl.useProgram(program);
```

## Drawing Your First Triangle

The "Hello World" of WebGL:

```javascript
// Complete triangle example
const canvas = document.getElementById('glCanvas');
const gl = canvas.getContext('webgl2');

// Vertex shader
const vertexShaderSource = `
    attribute vec3 aPosition;
    attribute vec3 aColor;
    varying vec3 vColor;

    void main() {
        gl_Position = vec4(aPosition, 1.0);
        vColor = aColor;
    }
`;

// Fragment shader
const fragmentShaderSource = `
    precision mediump float;
    varying vec3 vColor;

    void main() {
        gl_FragColor = vec4(vColor, 1.0);
    }
`;

// Create program
const program = createProgram(gl, vertexShaderSource, fragmentShaderSource);

// Triangle vertices (x, y, z, r, g, b)
const vertices = new Float32Array([
    // Position        Color
     0.0,  0.5, 0.0,  1.0, 0.0, 0.0,  // Top (red)
    -0.5, -0.5, 0.0,  0.0, 1.0, 0.0,  // Bottom-left (green)
     0.5, -0.5, 0.0,  0.0, 0.0, 1.0   // Bottom-right (blue)
]);

// Create and bind buffer
const buffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

// Get attribute locations
const positionLocation = gl.getAttribLocation(program, 'aPosition');
const colorLocation = gl.getAttribLocation(program, 'aColor');

// Configure position attribute
gl.enableVertexAttribArray(positionLocation);
gl.vertexAttribPointer(
    positionLocation,
    3,           // 3 components (x, y, z)
    gl.FLOAT,    // Data type
    false,       // Don't normalize
    24,          // Stride: 6 floats * 4 bytes
    0            // Offset: start of each vertex
);

// Configure color attribute
gl.enableVertexAttribArray(colorLocation);
gl.vertexAttribPointer(
    colorLocation,
    3,           // 3 components (r, g, b)
    gl.FLOAT,
    false,
    24,          // Stride
    12           // Offset: 3 floats * 4 bytes
);

// Clear and draw
gl.clearColor(0.0, 0.0, 0.0, 1.0);
gl.clear(gl.COLOR_BUFFER_BIT);
gl.useProgram(program);
gl.drawArrays(gl.TRIANGLES, 0, 3);
```

**Visual Output**: A triangle with vertices colored red (top), green (bottom-left), and blue (bottom-right). The GPU interpolates colors across the triangle's surface, creating a smooth gradient.

### Understanding Vertex Buffers

Vertex buffers store vertex data in GPU memory:

```javascript
class VertexBuffer {
    constructor(gl, data, usage = gl.STATIC_DRAW) {
        this.gl = gl;
        this.buffer = gl.createBuffer();
        this.bind();
        gl.bufferData(gl.ARRAY_BUFFER, data, usage);
    }

    bind() {
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.buffer);
    }

    delete() {
        this.gl.deleteBuffer(this.buffer);
    }
}

// Index buffer for indexed drawing
class IndexBuffer {
    constructor(gl, indices) {
        this.gl = gl;
        this.buffer = gl.createBuffer();
        this.count = indices.length;
        this.bind();
        gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);
    }

    bind() {
        this.gl.bindBuffer(this.gl.ELEMENT_ARRAY_BUFFER, this.buffer);
    }

    delete() {
        this.gl.deleteBuffer(this.buffer);
    }
}
```

## Drawing a Textured Quad

Textures add visual richness. Here's a complete textured quad example:

```javascript
// Textured quad vertex shader
const texVertSource = `
    attribute vec3 aPosition;
    attribute vec2 aTexCoord;
    varying vec2 vTexCoord;

    void main() {
        gl_Position = vec4(aPosition, 1.0);
        vTexCoord = aTexCoord;
    }
`;

// Textured quad fragment shader
const texFragSource = `
    precision mediump float;
    varying vec2 vTexCoord;
    uniform sampler2D uTexture;

    void main() {
        gl_FragColor = texture2D(uTexture, vTexCoord);
    }
`;

// Quad vertices (position + texture coordinates)
const quadVertices = new Float32Array([
    // x,    y,    z,    u,   v
    -0.5,  0.5, 0.0,  0.0, 0.0,  // Top-left
    -0.5, -0.5, 0.0,  0.0, 1.0,  // Bottom-left
     0.5,  0.5, 0.0,  1.0, 0.0,  // Top-right
     0.5, -0.5, 0.0,  1.0, 1.0   // Bottom-right
]);

// Indices for two triangles (quad)
const quadIndices = new Uint16Array([
    0, 1, 2,  // First triangle
    1, 3, 2   // Second triangle
]);

// Create buffers
const vbo = new VertexBuffer(gl, quadVertices);
const ibo = new IndexBuffer(gl, quadIndices);

// Create and load texture
function createTexture(gl, imagePath) {
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);

    // Temporary 1x1 pixel while image loads
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE,
                  new Uint8Array([255, 0, 255, 255])); // Magenta

    const image = new Image();
    image.onload = () => {
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);

        // Generate mipmaps or set filtering for non-power-of-2 textures
        if (isPowerOf2(image.width) && isPowerOf2(image.height)) {
            gl.generateMipmap(gl.TEXTURE_2D);
        } else {
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        }
    };
    image.src = imagePath;

    return texture;
}

function isPowerOf2(value) {
    return (value & (value - 1)) === 0;
}

// Load texture
const texture = createTexture(gl, 'sprite.png');

// Render function
function render() {
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    gl.useProgram(texProgram);

    // Bind texture
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.uniform1i(gl.getUniformLocation(texProgram, 'uTexture'), 0);

    // Bind buffers and set attributes
    vbo.bind();
    ibo.bind();

    const posLoc = gl.getAttribLocation(texProgram, 'aPosition');
    const texLoc = gl.getAttribLocation(texProgram, 'aTexCoord');

    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 3, gl.FLOAT, false, 20, 0);

    gl.enableVertexAttribArray(texLoc);
    gl.vertexAttribPointer(texLoc, 2, gl.FLOAT, false, 20, 12);

    // Draw indexed
    gl.drawElements(gl.TRIANGLES, ibo.count, gl.UNSIGNED_SHORT, 0);
}

render();
```

**Visual Output**: A quad (square) displaying the loaded texture image. If the image hasn't loaded yet, you see a magenta square.

## 3D Rendering with Matrices

To render 3D, we need projection and view matrices:

```javascript
// Simple matrix library (or use gl-matrix.js)
class Mat4 {
    static perspective(fov, aspect, near, far) {
        const f = 1.0 / Math.tan(fov / 2);
        const nf = 1 / (near - far);

        return new Float32Array([
            f / aspect, 0, 0, 0,
            0, f, 0, 0,
            0, 0, (far + near) * nf, -1,
            0, 0, 2 * far * near * nf, 0
        ]);
    }

    static translate(x, y, z) {
        return new Float32Array([
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            x, y, z, 1
        ]);
    }

    static rotateY(angle) {
        const c = Math.cos(angle);
        const s = Math.sin(angle);
        return new Float32Array([
            c, 0, s, 0,
            0, 1, 0, 0,
            -s, 0, c, 0,
            0, 0, 0, 1
        ]);
    }

    static multiply(a, b) {
        const result = new Float32Array(16);
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                result[i * 4 + j] =
                    a[i * 4 + 0] * b[0 * 4 + j] +
                    a[i * 4 + 1] * b[1 * 4 + j] +
                    a[i * 4 + 2] * b[2 * 4 + j] +
                    a[i * 4 + 3] * b[3 * 4 + j];
            }
        }
        return result;
    }
}

// 3D cube example
const cubeVertices = new Float32Array([
    // Front face
    -1, -1,  1,  0, 0, 1,
     1, -1,  1,  0, 0, 1,
     1,  1,  1,  0, 0, 1,
    -1,  1,  1,  0, 0, 1,
    // Back face
    -1, -1, -1,  0, 0, -1,
    -1,  1, -1,  0, 0, -1,
     1,  1, -1,  0, 0, -1,
     1, -1, -1,  0, 0, -1,
    // Top face
    -1,  1, -1,  0, 1, 0,
    -1,  1,  1,  0, 1, 0,
     1,  1,  1,  0, 1, 0,
     1,  1, -1,  0, 1, 0,
    // Bottom face
    -1, -1, -1,  0, -1, 0,
     1, -1, -1,  0, -1, 0,
     1, -1,  1,  0, -1, 0,
    -1, -1,  1,  0, -1, 0,
    // Right face
     1, -1, -1,  1, 0, 0,
     1,  1, -1,  1, 0, 0,
     1,  1,  1,  1, 0, 0,
     1, -1,  1,  1, 0, 0,
    // Left face
    -1, -1, -1, -1, 0, 0,
    -1, -1,  1, -1, 0, 0,
    -1,  1,  1, -1, 0, 0,
    -1,  1, -1, -1, 0, 0
]);

const cubeIndices = new Uint16Array([
    0,  1,  2,   0,  2,  3,   // front
    4,  5,  6,   4,  6,  7,   // back
    8,  9, 10,   8, 10, 11,   // top
    12, 13, 14,  12, 14, 15,  // bottom
    16, 17, 18,  16, 18, 19,  // right
    20, 21, 22,  20, 22, 23   // left
]);

// Vertex shader with matrices
const cube3DVertShader = `
    attribute vec3 aPosition;
    attribute vec3 aNormal;

    uniform mat4 uModelMatrix;
    uniform mat4 uViewMatrix;
    uniform mat4 uProjectionMatrix;

    varying vec3 vNormal;

    void main() {
        gl_Position = uProjectionMatrix * uViewMatrix * uModelMatrix * vec4(aPosition, 1.0);
        vNormal = aNormal;
    }
`;

// Fragment shader with simple lighting
const cube3DFragShader = `
    precision mediump float;
    varying vec3 vNormal;

    void main() {
        vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
        float diff = max(dot(normalize(vNormal), lightDir), 0.0);
        vec3 color = vec3(0.3, 0.6, 0.9) * (0.3 + 0.7 * diff);
        gl_FragColor = vec4(color, 1.0);
    }
`;

// Render loop
let rotation = 0;
function renderCube() {
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.useProgram(cubeProgram);

    // Update rotation
    rotation += 0.01;

    // Compute matrices
    const projectionMatrix = Mat4.perspective(
        Math.PI / 4,          // 45 degree FOV
        canvas.width / canvas.height,
        0.1,                  // Near plane
        100.0                 // Far plane
    );

    const viewMatrix = Mat4.translate(0, 0, -6); // Move camera back

    const modelMatrix = Mat4.multiply(
        Mat4.rotateY(rotation),
        Mat4.translate(0, 0, 0)
    );

    // Set uniforms
    const projLoc = gl.getUniformLocation(cubeProgram, 'uProjectionMatrix');
    const viewLoc = gl.getUniformLocation(cubeProgram, 'uViewMatrix');
    const modelLoc = gl.getUniformLocation(cubeProgram, 'uModelMatrix');

    gl.uniformMatrix4fv(projLoc, false, projectionMatrix);
    gl.uniformMatrix4fv(viewLoc, false, viewMatrix);
    gl.uniformMatrix4fv(modelLoc, false, modelMatrix);

    // Draw cube
    cubeVBO.bind();
    cubeIBO.bind();

    const posLoc = gl.getAttribLocation(cubeProgram, 'aPosition');
    const normLoc = gl.getAttribLocation(cubeProgram, 'aNormal');

    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 3, gl.FLOAT, false, 24, 0);

    gl.enableVertexAttribArray(normLoc);
    gl.vertexAttribPointer(normLoc, 3, gl.FLOAT, false, 24, 12);

    gl.drawElements(gl.TRIANGLES, 36, gl.UNSIGNED_SHORT, 0);

    requestAnimationFrame(renderCube);
}

requestAnimationFrame(renderCube);
```

**Visual Output**: A spinning 3D blue cube with simple lighting. The cube appears to have depth, with faces getting darker as they face away from the light source.

## Batch Rendering for 2D Sprites

WebGL excels at rendering thousands of 2D sprites using batching:

```javascript
class SpriteBatch {
    constructor(gl, maxSprites = 10000) {
        this.gl = gl;
        this.maxSprites = maxSprites;
        this.sprites = [];

        // Each sprite = 4 vertices = 24 floats (pos=3, tex=2, color=4)
        this.vertexData = new Float32Array(maxSprites * 4 * 9);
        this.indices = new Uint16Array(maxSprites * 6);

        // Generate indices (two triangles per sprite)
        for (let i = 0; i < maxSprites; i++) {
            const offset = i * 6;
            const vertexOffset = i * 4;

            this.indices[offset + 0] = vertexOffset + 0;
            this.indices[offset + 1] = vertexOffset + 1;
            this.indices[offset + 2] = vertexOffset + 2;
            this.indices[offset + 3] = vertexOffset + 0;
            this.indices[offset + 4] = vertexOffset + 2;
            this.indices[offset + 5] = vertexOffset + 3;
        }

        this.vbo = new VertexBuffer(gl, this.vertexData, gl.DYNAMIC_DRAW);
        this.ibo = new IndexBuffer(gl, this.indices);

        // Create shader program
        this.program = createProgram(gl, this.vertexShader, this.fragmentShader);
        this.setupAttributes();
    }

    get vertexShader() {
        return `
            attribute vec3 aPosition;
            attribute vec2 aTexCoord;
            attribute vec4 aColor;

            uniform mat4 uProjection;

            varying vec2 vTexCoord;
            varying vec4 vColor;

            void main() {
                gl_Position = uProjection * vec4(aPosition, 1.0);
                vTexCoord = aTexCoord;
                vColor = aColor;
            }
        `;
    }

    get fragmentShader() {
        return `
            precision mediump float;
            varying vec2 vTexCoord;
            varying vec4 vColor;
            uniform sampler2D uTexture;

            void main() {
                gl_FragColor = texture2D(uTexture, vTexCoord) * vColor;
            }
        `;
    }

    setupAttributes() {
        this.vbo.bind();

        const posLoc = this.gl.getAttribLocation(this.program, 'aPosition');
        const texLoc = this.gl.getAttribLocation(this.program, 'aTexCoord');
        const colorLoc = this.gl.getAttribLocation(this.program, 'aColor');

        this.gl.enableVertexAttribArray(posLoc);
        this.gl.vertexAttribPointer(posLoc, 3, this.gl.FLOAT, false, 36, 0);

        this.gl.enableVertexAttribArray(texLoc);
        this.gl.vertexAttribPointer(texLoc, 2, this.gl.FLOAT, false, 36, 12);

        this.gl.enableVertexAttribArray(colorLoc);
        this.gl.vertexAttribPointer(colorLoc, 4, this.gl.FLOAT, false, 36, 20);
    }

    addSprite(x, y, width, height, texX, texY, texW, texH, r=1, g=1, b=1, a=1) {
        if (this.sprites.length >= this.maxSprites) {
            this.flush();
        }

        const index = this.sprites.length * 4 * 9;

        // Top-left
        this.vertexData[index + 0] = x;
        this.vertexData[index + 1] = y;
        this.vertexData[index + 2] = 0;
        this.vertexData[index + 3] = texX;
        this.vertexData[index + 4] = texY;
        this.vertexData[index + 5] = r;
        this.vertexData[index + 6] = g;
        this.vertexData[index + 7] = b;
        this.vertexData[index + 8] = a;

        // Top-right
        this.vertexData[index + 9] = x + width;
        this.vertexData[index + 10] = y;
        this.vertexData[index + 11] = 0;
        this.vertexData[index + 12] = texX + texW;
        this.vertexData[index + 13] = texY;
        this.vertexData[index + 14] = r;
        this.vertexData[index + 15] = g;
        this.vertexData[index + 16] = b;
        this.vertexData[index + 17] = a;

        // Bottom-right
        this.vertexData[index + 18] = x + width;
        this.vertexData[index + 19] = y + height;
        this.vertexData[index + 20] = 0;
        this.vertexData[index + 21] = texX + texW;
        this.vertexData[index + 22] = texY + texH;
        this.vertexData[index + 23] = r;
        this.vertexData[index + 24] = g;
        this.vertexData[index + 25] = b;
        this.vertexData[index + 26] = a;

        // Bottom-left
        this.vertexData[index + 27] = x;
        this.vertexData[index + 28] = y + height;
        this.vertexData[index + 29] = 0;
        this.vertexData[index + 30] = texX;
        this.vertexData[index + 31] = texY + texH;
        this.vertexData[index + 32] = r;
        this.vertexData[index + 33] = g;
        this.vertexData[index + 34] = b;
        this.vertexData[index + 35] = a;

        this.sprites.push(true);
    }

    flush() {
        if (this.sprites.length === 0) return;

        this.gl.useProgram(this.program);

        // Update vertex buffer
        this.vbo.bind();
        this.gl.bufferSubData(this.gl.ARRAY_BUFFER, 0, this.vertexData);

        // Set projection matrix
        const projMatrix = this.createOrthoMatrix(0, canvas.width, canvas.height, 0, -1, 1);
        const projLoc = this.gl.getUniformLocation(this.program, 'uProjection');
        this.gl.uniformMatrix4fv(projLoc, false, projMatrix);

        // Draw
        this.ibo.bind();
        this.gl.drawElements(this.gl.TRIANGLES, this.sprites.length * 6, this.gl.UNSIGNED_SHORT, 0);

        this.sprites = [];
    }

    createOrthoMatrix(left, right, bottom, top, near, far) {
        const lr = 1 / (left - right);
        const bt = 1 / (bottom - top);
        const nf = 1 / (near - far);

        return new Float32Array([
            -2 * lr, 0, 0, 0,
            0, -2 * bt, 0, 0,
            0, 0, 2 * nf, 0,
            (left + right) * lr, (top + bottom) * bt, (far + near) * nf, 1
        ]);
    }
}

// Usage
const batch = new SpriteBatch(gl, 10000);

function render() {
    gl.clear(gl.COLOR_BUFFER_BIT);

    // Add 1000 sprites
    for (let i = 0; i < 1000; i++) {
        const x = Math.random() * 800;
        const y = Math.random() * 600;
        batch.addSprite(x, y, 32, 32, 0, 0, 1, 1);
    }

    batch.flush();

    requestAnimationFrame(render);
}
```

**Performance**: This renders 10,000+ sprites at 60 FPS by batching all draws into a single call.

## Claude Code Prompts for WebGL

**Basic Setup:**
```
Create a WebGL 2.0 initialization system with context loss handling,
high-DPI support, and automatic canvas resizing.
```

**3D Rendering:**
```
Implement a WebGL 3D renderer with perspective camera, basic lighting,
and support for rendering multiple meshes with different textures.
```

**Optimization:**
```
Create a WebGL sprite batch renderer that can handle 10,000+ textured quads
with color tinting and efficient vertex buffer updates.
```

**Shader Effects:**
```
Write WebGL shaders that create a water reflection effect with wave animation
and fresnel edge highlighting.
```

## Common WebGL Pitfalls

**Pitfall 1: Not checking shader compilation**
Always check `gl.getShaderParameter(shader, gl.COMPILE_STATUS)` and log errors with `gl.getShaderInfoLog()`.

**Pitfall 2: Forgetting to enable vertex attributes**
Must call `gl.enableVertexAttribArray()` for each attribute before drawing.

**Pitfall 3: Texture non-power-of-2 issues**
Non-POT textures can't use mipmaps. Set `TEXTURE_WRAP` to `CLAMP_TO_EDGE` and `MIN_FILTER` to `LINEAR`.

**Pitfall 4: Not clearing depth buffer**
For 3D, clear both: `gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)`

**Pitfall 5: Incorrect matrix multiplication order**
Matrix multiplication order matters: `projection * view * model`, not reversed.

## Performance Optimization

1. **Minimize state changes**: Batch draws with same shader/texture
2. **Use vertex buffer objects**: Store data in GPU memory
3. **Use indexed drawing**: Reuse vertices with `drawElements`
4. **Texture atlases**: Combine textures to reduce texture swaps
5. **Instanced rendering**: Draw many copies of same mesh efficiently (WebGL 2)
6. **Frustum culling**: Don't submit invisible objects to GPU

## Next Steps

You now understand WebGL fundamentals. Continue to:

- **[Shader Programming](./shader-programming.md)**: Create custom visual effects with GLSL
- **[Lighting and Shadows](./lighting-shadows.md)**: Implement realistic lighting models
- **[Post-Processing Effects](./post-processing-effects.md)**: Add bloom, blur, and other effects

WebGL unlocks incredible rendering power. With Claude Code's help, you can create stunning 3D games and highly optimized 2D rendering systems!
