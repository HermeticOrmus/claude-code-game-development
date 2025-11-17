# Camera Systems

The camera is the player's window into your game world. A good camera system feels invisible, keeping the action in frame while providing the right amount of smoothness and anticipation. This guide covers 2D camera fundamentals, following behaviors, effects, and optimization.

## Table of Contents

1. [Camera Fundamentals](#camera-fundamentals)
2. [Basic Camera (Translation and Zoom)](#basic-camera-translation-and-zoom)
3. [Camera Following Player](#camera-following-player)
4. [Camera Bounds and Constraints](#camera-bounds-and-constraints)
5. [Camera Effects](#camera-effects)
6. [Parallax Scrolling](#parallax-scrolling)
7. [3D Camera Basics](#3d-camera-basics)
8. [Integration Examples](#integration-examples)

## Camera Fundamentals

A 2D camera controls what portion of the game world is visible on screen. Key concepts:

- **Position**: Where the camera is in world space (usually center point)
- **Viewport**: The screen dimensions
- **Zoom**: Scale factor (1.0 = normal, 2.0 = zoomed in 2x)
- **Bounds**: Limits on where the camera can move
- **Transformation**: Converting world coordinates to screen coordinates

### World to Screen Coordinates

```javascript
function worldToScreen(worldX, worldY, camera) {
    const screenX = (worldX - camera.x) * camera.zoom + camera.viewportWidth / 2;
    const screenY = (worldY - camera.y) * camera.zoom + camera.viewportHeight / 2;
    return { x: screenX, y: screenY };
}

function screenToWorld(screenX, screenY, camera) {
    const worldX = (screenX - camera.viewportWidth / 2) / camera.zoom + camera.x;
    const worldY = (screenY - camera.viewportHeight / 2) / camera.zoom + camera.y;
    return { x: worldX, y: worldY };
}
```

## Basic Camera (Translation and Zoom)

### Claude Code Prompt

```
Prompt: "Create a basic 2D camera class with position, zoom, rotation support,
coordinate transformation methods, and rendering integration with canvas context.
Include manual camera controls (WASD to move, scroll to zoom) and debug
visualization showing camera bounds and center point."
```

### Implementation

```javascript
class Camera {
    constructor(x, y, viewportWidth, viewportHeight) {
        this.x = x; // Camera center in world coordinates
        this.y = y;
        this.viewportWidth = viewportWidth;
        this.viewportHeight = viewportHeight;

        this.zoom = 1.0;
        this.rotation = 0; // radians
        this.minZoom = 0.5;
        this.maxZoom = 3.0;

        // Bounds (optional - limits camera movement)
        this.bounds = null;
    }

    // Set world bounds
    setBounds(x, y, width, height) {
        this.bounds = { x, y, width, height };
    }

    // Move camera
    move(dx, dy) {
        this.x += dx;
        this.y += dy;
        this.applyBounds();
    }

    // Set camera position
    setPosition(x, y) {
        this.x = x;
        this.y = y;
        this.applyBounds();
    }

    // Zoom camera
    setZoom(zoom) {
        this.zoom = Math.max(this.minZoom, Math.min(this.maxZoom, zoom));
    }

    // Apply bounds constraints
    applyBounds() {
        if (!this.bounds) return;

        // Calculate visible world area
        const halfWidth = this.viewportWidth / (2 * this.zoom);
        const halfHeight = this.viewportHeight / (2 * this.zoom);

        // Clamp camera position
        this.x = Math.max(
            this.bounds.x + halfWidth,
            Math.min(this.bounds.x + this.bounds.width - halfWidth, this.x)
        );

        this.y = Math.max(
            this.bounds.y + halfHeight,
            Math.min(this.bounds.y + this.bounds.height - halfHeight, this.y)
        );
    }

    // Convert world coordinates to screen coordinates
    worldToScreen(worldX, worldY) {
        // Translate to camera space
        let x = worldX - this.x;
        let y = worldY - this.y;

        // Apply rotation
        if (this.rotation !== 0) {
            const cos = Math.cos(-this.rotation);
            const sin = Math.sin(-this.rotation);
            const rotatedX = x * cos - y * sin;
            const rotatedY = x * sin + y * cos;
            x = rotatedX;
            y = rotatedY;
        }

        // Apply zoom and translate to screen center
        x = x * this.zoom + this.viewportWidth / 2;
        y = y * this.zoom + this.viewportHeight / 2;

        return { x, y };
    }

    // Convert screen coordinates to world coordinates
    screenToWorld(screenX, screenY) {
        // Translate from screen center
        let x = (screenX - this.viewportWidth / 2) / this.zoom;
        let y = (screenY - this.viewportHeight / 2) / this.zoom;

        // Apply inverse rotation
        if (this.rotation !== 0) {
            const cos = Math.cos(this.rotation);
            const sin = Math.sin(this.rotation);
            const rotatedX = x * cos - y * sin;
            const rotatedY = x * sin + y * cos;
            x = rotatedX;
            y = rotatedY;
        }

        // Translate to world space
        x += this.x;
        y += this.y;

        return { x, y };
    }

    // Apply camera transformation to canvas context
    applyTransform(ctx) {
        ctx.save();

        // Translate to center
        ctx.translate(this.viewportWidth / 2, this.viewportHeight / 2);

        // Apply zoom
        ctx.scale(this.zoom, this.zoom);

        // Apply rotation
        ctx.rotate(this.rotation);

        // Translate to camera position
        ctx.translate(-this.x, -this.y);
    }

    // Restore canvas context
    restoreTransform(ctx) {
        ctx.restore();
    }

    // Get visible world bounds
    getVisibleBounds() {
        const topLeft = this.screenToWorld(0, 0);
        const bottomRight = this.screenToWorld(this.viewportWidth, this.viewportHeight);

        return {
            x: topLeft.x,
            y: topLeft.y,
            width: bottomRight.x - topLeft.x,
            height: bottomRight.y - topLeft.y
        };
    }

    // Check if point is visible
    isVisible(x, y, margin = 0) {
        const bounds = this.getVisibleBounds();
        return x >= bounds.x - margin &&
               x <= bounds.x + bounds.width + margin &&
               y >= bounds.y - margin &&
               y <= bounds.y + bounds.height + margin;
    }

    // Render debug info
    renderDebug(ctx) {
        // Render in screen space (not transformed)
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(10, 10, 250, 100);

        ctx.fillStyle = '#0f0';
        ctx.font = '14px monospace';
        ctx.fillText(`Cam: (${this.x.toFixed(0)}, ${this.y.toFixed(0)})`, 20, 30);
        ctx.fillText(`Zoom: ${this.zoom.toFixed(2)}x`, 20, 50);
        ctx.fillText(`Rotation: ${(this.rotation * 180 / Math.PI).toFixed(1)}°`, 20, 70);

        // Show camera center (in world space)
        this.applyTransform(ctx);

        ctx.strokeStyle = '#ff00ff';
        ctx.lineWidth = 2 / this.zoom;
        ctx.beginPath();
        ctx.moveTo(this.x - 20, this.y);
        ctx.lineTo(this.x + 20, this.y);
        ctx.moveTo(this.x, this.y - 20);
        ctx.lineTo(this.x, this.y + 20);
        ctx.stroke();

        this.restoreTransform(ctx);
    }
}
```

## Camera Following Player

### Claude Code Prompt

```
Prompt: "Create camera following behaviors: snap (immediate), smooth (lerp),
and platformer-style (with deadzone). Include look-ahead (camera moves ahead
of player direction), and vertical/horizontal-only following. Add visualization
showing deadzone and target position."
```

### Implementation

```javascript
class FollowCamera extends Camera {
    constructor(x, y, viewportWidth, viewportHeight) {
        super(x, y, viewportWidth, viewportHeight);

        // Follow settings
        this.followMode = 'smooth'; // 'snap', 'smooth', 'deadzone'
        this.smoothness = 0.1; // Lower = smoother (0.05 - 0.2)
        this.deadzone = {
            x: 100,
            y: 60
        };

        // Look-ahead
        this.lookAhead = true;
        this.lookAheadDistance = 50;
        this.lookAheadSmooth = 0.05;
        this.currentLookAhead = { x: 0, y: 0 };

        // Target
        this.target = null;
        this.targetVelocity = { x: 0, y: 0 };
    }

    setTarget(target) {
        this.target = target;
    }

    update(dt) {
        if (!this.target) return;

        // Store target velocity for look-ahead
        this.targetVelocity.x = this.target.vx || 0;
        this.targetVelocity.y = this.target.vy || 0;

        switch (this.followMode) {
            case 'snap':
                this.snapFollow();
                break;
            case 'smooth':
                this.smoothFollow(dt);
                break;
            case 'deadzone':
                this.deadzoneFollow(dt);
                break;
        }

        this.applyBounds();
    }

    snapFollow() {
        // Immediately center on target
        this.x = this.target.x;
        this.y = this.target.y;
    }

    smoothFollow(dt) {
        // Smooth lerp to target
        const targetX = this.target.x + this.getLookAheadX();
        const targetY = this.target.y + this.getLookAheadY();

        this.x += (targetX - this.x) * this.smoothness;
        this.y += (targetY - this.y) * this.smoothness;
    }

    deadzoneFollow(dt) {
        // Only move camera when target leaves deadzone
        const targetX = this.target.x + this.getLookAheadX();
        const targetY = this.target.y + this.getLookAheadY();

        // Check horizontal deadzone
        const dx = targetX - this.x;
        if (Math.abs(dx) > this.deadzone.x) {
            const sign = dx > 0 ? 1 : -1;
            this.x += (Math.abs(dx) - this.deadzone.x) * sign * this.smoothness;
        }

        // Check vertical deadzone
        const dy = targetY - this.y;
        if (Math.abs(dy) > this.deadzone.y) {
            const sign = dy > 0 ? 1 : -1;
            this.y += (Math.abs(dy) - this.deadzone.y) * sign * this.smoothness;
        }
    }

    getLookAheadX() {
        if (!this.lookAhead) return 0;

        const targetLookAhead = this.targetVelocity.x !== 0
            ? Math.sign(this.targetVelocity.x) * this.lookAheadDistance
            : 0;

        this.currentLookAhead.x += (targetLookAhead - this.currentLookAhead.x) * this.lookAheadSmooth;
        return this.currentLookAhead.x;
    }

    getLookAheadY() {
        if (!this.lookAhead) return 0;

        const targetLookAhead = this.targetVelocity.y > 0
            ? this.lookAheadDistance * 0.5 // Less look-ahead when falling
            : 0;

        this.currentLookAhead.y += (targetLookAhead - this.currentLookAhead.y) * this.lookAheadSmooth;
        return this.currentLookAhead.y;
    }

    renderDebug(ctx) {
        super.renderDebug(ctx);

        if (this.followMode === 'deadzone') {
            this.applyTransform(ctx);

            // Draw deadzone
            ctx.strokeStyle = 'rgba(255, 255, 0, 0.5)';
            ctx.lineWidth = 2 / this.zoom;
            ctx.strokeRect(
                this.x - this.deadzone.x,
                this.y - this.deadzone.y,
                this.deadzone.x * 2,
                this.deadzone.y * 2
            );

            this.restoreTransform(ctx);
        }

        // Show follow mode
        ctx.fillStyle = '#0f0';
        ctx.font = '14px monospace';
        ctx.fillText(`Mode: ${this.followMode}`, 20, 90);
    }
}
```

## Camera Bounds and Constraints

Camera bounds prevent the camera from showing areas outside the game world.

### Implementation (Already in Camera class)

The `setBounds()` and `applyBounds()` methods in the Camera class handle this. When bounds are set, the camera is constrained to stay within the world.

## Camera Effects

### Screen Shake

### Claude Code Prompt

```
Prompt: "Create a screen shake effect system with different shake patterns
(random, sine wave), intensity control, and automatic decay. Include trauma-
based shake where multiple events stack up shake intensity."
```

### Implementation

```javascript
class CameraEffects {
    constructor(camera) {
        this.camera = camera;

        // Screen shake
        this.shakeTrauma = 0; // 0 to 1
        this.shakeDecay = 2.0; // Trauma decay per second
        this.shakeMaxOffset = 20; // Maximum pixel offset
        this.shakeMaxRotation = 0.1; // Maximum rotation in radians

        this.shakeOffset = { x: 0, y: 0 };
        this.shakeRotation = 0;

        // Flash effect
        this.flashAlpha = 0;
        this.flashColor = '#ffffff';
        this.flashDecay = 3.0;
    }

    // Add trauma (0 to 1)
    addShake(amount) {
        this.shakeTrauma = Math.min(1, this.shakeTrauma + amount);
    }

    // Add flash
    addFlash(color = '#ffffff', intensity = 1.0) {
        this.flashColor = color;
        this.flashAlpha = intensity;
    }

    update(dt) {
        // Decay trauma
        this.shakeTrauma = Math.max(0, this.shakeTrauma - this.shakeDecay * dt);

        // Calculate shake based on trauma squared (feel more punchy)
        const shake = this.shakeTrauma * this.shakeTrauma;

        if (shake > 0) {
            // Random offset
            this.shakeOffset.x = (Math.random() * 2 - 1) * this.shakeMaxOffset * shake;
            this.shakeOffset.y = (Math.random() * 2 - 1) * this.shakeMaxOffset * shake;

            // Random rotation
            this.shakeRotation = (Math.random() * 2 - 1) * this.shakeMaxRotation * shake;
        } else {
            this.shakeOffset.x = 0;
            this.shakeOffset.y = 0;
            this.shakeRotation = 0;
        }

        // Decay flash
        this.flashAlpha = Math.max(0, this.flashAlpha - this.flashDecay * dt);
    }

    applyShake() {
        // Apply shake offset to camera
        this.camera.x += this.shakeOffset.x / this.camera.zoom;
        this.camera.y += this.shakeOffset.y / this.camera.zoom;
        this.camera.rotation += this.shakeRotation;
    }

    removeShake() {
        // Remove shake offset from camera
        this.camera.x -= this.shakeOffset.x / this.camera.zoom;
        this.camera.y -= this.shakeOffset.y / this.camera.zoom;
        this.camera.rotation -= this.shakeRotation;
    }

    renderFlash(ctx) {
        if (this.flashAlpha > 0) {
            ctx.fillStyle = this.flashColor;
            ctx.globalAlpha = this.flashAlpha;
            ctx.fillRect(0, 0, this.camera.viewportWidth, this.camera.viewportHeight);
            ctx.globalAlpha = 1;
        }
    }
}

// Usage in game loop
/*
const camera = new Camera(0, 0, 800, 600);
const effects = new CameraEffects(camera);

function update(dt) {
    effects.update(dt);

    // Apply shake before rendering
    effects.applyShake();

    // ... render game world ...

    // Remove shake after rendering
    effects.removeShake();

    // Render flash on top
    effects.renderFlash(ctx);
}

// Trigger effects
function onExplosion() {
    effects.addShake(0.5); // Add trauma
    effects.addFlash('#ff8800', 0.5);
}
*/
```

### Zoom Effects

```javascript
class ZoomEffect {
    constructor(camera) {
        this.camera = camera;
        this.targetZoom = camera.zoom;
        this.zoomSpeed = 2.0;
    }

    zoomTo(targetZoom, duration = 1.0) {
        this.targetZoom = targetZoom;
        this.zoomSpeed = Math.abs(targetZoom - this.camera.zoom) / duration;
    }

    update(dt) {
        const diff = this.targetZoom - this.camera.zoom;

        if (Math.abs(diff) > 0.01) {
            const step = Math.sign(diff) * this.zoomSpeed * dt;

            if (Math.abs(step) > Math.abs(diff)) {
                this.camera.zoom = this.targetZoom;
            } else {
                this.camera.zoom += step;
            }
        }
    }
}
```

## Parallax Scrolling

Parallax creates depth by moving background layers at different speeds.

### Claude Code Prompt

```
Prompt: "Create a parallax scrolling system with multiple layers at different
depths. Include automatic tiling for seamless infinite scrolling, and support
for both horizontal and vertical parallax. Add debug visualization showing
layer speeds and positions."
```

### Implementation

```javascript
class ParallaxLayer {
    constructor(image, scrollSpeed, y = 0) {
        this.image = image;
        this.scrollSpeed = scrollSpeed; // 0 = fixed, 1 = matches camera
        this.y = y; // Vertical offset
        this.offsetX = 0;
    }

    update(cameraX, cameraWidth) {
        // Calculate scroll offset based on camera position
        this.offsetX = -cameraX * this.scrollSpeed;

        // Wrap offset for seamless tiling
        if (this.image) {
            this.offsetX = this.offsetX % this.image.width;
        }
    }

    render(ctx, viewportWidth, viewportHeight) {
        if (!this.image) return;

        // Draw tiled images
        const startX = Math.floor(this.offsetX / this.image.width) * this.image.width;

        for (let x = startX; x < viewportWidth; x += this.image.width) {
            ctx.drawImage(this.image, x + this.offsetX, this.y);
        }
    }
}

class ParallaxBackground {
    constructor() {
        this.layers = [];
    }

    addLayer(image, scrollSpeed, y = 0) {
        this.layers.push(new ParallaxLayer(image, scrollSpeed, y));

        // Sort by scroll speed (furthest to nearest)
        this.layers.sort((a, b) => a.scrollSpeed - b.scrollSpeed);
    }

    update(camera) {
        for (const layer of this.layers) {
            layer.update(camera.x, camera.viewportWidth);
        }
    }

    render(ctx, camera) {
        ctx.save();

        // Render layers from back to front
        for (const layer of this.layers) {
            layer.render(ctx, camera.viewportWidth, camera.viewportHeight);
        }

        ctx.restore();
    }
}

// Usage example
/*
const parallax = new ParallaxBackground();

// Load background images
const skyImage = new Image();
skyImage.src = 'sky.png';

const mountainsImage = new Image();
mountainsImage.src = 'mountains.png';

const hillsImage = new Image();
hillsImage.src = 'hills.png';

// Add layers (furthest to nearest)
parallax.addLayer(skyImage, 0.0); // Fixed background
parallax.addLayer(mountainsImage, 0.2); // Slow parallax
parallax.addLayer(hillsImage, 0.6); // Faster parallax

// In game loop
function render() {
    // Render parallax background (no camera transform)
    parallax.update(camera);
    parallax.render(ctx, camera);

    // Then render game world with camera transform
    camera.applyTransform(ctx);
    // ... render game objects ...
    camera.restoreTransform(ctx);
}
*/
```

## 3D Camera Basics

While this guide focuses on 2D, here's a basic 3D camera for reference.

### Simple 3D Camera

```javascript
class Camera3D {
    constructor() {
        this.position = { x: 0, y: 0, z: -5 };
        this.rotation = { x: 0, y: 0, z: 0 };
        this.fov = 60; // Field of view in degrees
        this.near = 0.1;
        this.far = 1000;
    }

    // Project 3D point to 2D screen
    project(x, y, z, viewportWidth, viewportHeight) {
        // Transform to camera space
        const cx = x - this.position.x;
        const cy = y - this.position.y;
        const cz = z - this.position.z;

        // Simple perspective projection
        if (cz === 0) return null; // Avoid division by zero

        const scale = (viewportWidth / 2) / Math.tan((this.fov * Math.PI / 180) / 2);
        const screenX = (cx / cz) * scale + viewportWidth / 2;
        const screenY = (cy / cz) * scale + viewportHeight / 2;

        return {
            x: screenX,
            y: screenY,
            scale: scale / Math.abs(cz) // For scaling objects based on distance
        };
    }
}
```

## Integration Examples

### Complete Camera Integration

```javascript
class Game {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Create camera
        this.camera = new FollowCamera(0, 0, canvas.width, canvas.height);
        this.camera.setBounds(0, 0, 2000, 1500); // World bounds
        this.camera.followMode = 'deadzone';

        // Camera effects
        this.cameraEffects = new CameraEffects(this.camera);

        // Parallax background
        this.parallax = new ParallaxBackground();

        // Player (camera target)
        this.player = {
            x: 400,
            y: 300,
            vx: 0,
            vy: 0
        };

        this.camera.setTarget(this.player);
    }

    update(dt) {
        // Update player
        this.player.x += this.player.vx * dt;
        this.player.y += this.player.vy * dt;

        // Update camera
        this.camera.update(dt);
        this.cameraEffects.update(dt);
        this.parallax.update(this.camera);
    }

    render() {
        // Clear
        this.ctx.fillStyle = '#87ceeb';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Render parallax (before camera transform)
        this.parallax.render(this.ctx, this.camera);

        // Apply shake
        this.cameraEffects.applyShake();

        // Apply camera transform
        this.camera.applyTransform(this.ctx);

        // Render world
        this.renderWorld();

        // Restore transform
        this.camera.restoreTransform(this.ctx);

        // Remove shake
        this.cameraEffects.removeShake();

        // Render flash
        this.cameraEffects.renderFlash(this.ctx);

        // Debug
        this.camera.renderDebug(this.ctx);
    }

    renderWorld() {
        // Draw player
        this.ctx.fillStyle = '#0f0';
        this.ctx.fillRect(this.player.x - 20, this.player.y - 20, 40, 40);

        // Draw world objects...
    }
}
```

## Conclusion

Camera systems are crucial for creating polished games. Start with a basic camera, add smooth following for action games, use deadzones for platformers, and enhance with effects like screen shake and parallax. Always test camera feel extensively, as it significantly impacts how your game feels to play.

---

**Related Documentation:**
- [Game Loops and Timing](./game-loops-and-timing.md)
- [Graphics Rendering](../03-graphics-rendering/)
- [UI/UX](../07-ui-ux/)
