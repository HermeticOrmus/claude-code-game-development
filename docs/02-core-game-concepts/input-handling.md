# Input Handling

Input handling is how your game communicates with the player. Whether it's jumping, shooting, navigating menus, or performing complex combos, responsive and robust input systems are essential for creating games that feel good to play. This guide covers keyboard, mouse, touch, and gamepad input with complete working examples.

## Table of Contents

1. [Why Input Handling Matters](#why-input-handling-matters)
2. [Keyboard Input](#keyboard-input)
3. [Mouse Input](#mouse-input)
4. [Touch Input for Mobile](#touch-input-for-mobile)
5. [Gamepad/Controller Support](#gamepadcontroller-support)
6. [Input Buffering and Queueing](#input-buffering-and-queueing)
7. [Multiple Input Methods](#multiple-input-methods-simultaneously)
8. [Cross-Platform Considerations](#cross-platform-input-considerations)
9. [Accessibility Considerations](#accessibility-considerations)

## Why Input Handling Matters

### Responsiveness Defines Feel

The difference between a game that feels "tight" and one that feels "sluggish" often comes down to input handling. Players expect instant feedback when they press a button. Even a delay of 100ms can make a game feel unresponsive.

### Input Buffering Prevents Frustration

Fighting games and platformers use input buffering to allow players to press buttons slightly before they're valid. This makes the game feel more responsive and forgiving.

### Supporting Multiple Input Methods

Modern games need to support keyboard+mouse, gamepad, and often touch input. A good input system handles all of these seamlessly and allows players to switch between them on the fly.

### Preventing Input Errors

Edge cases like simultaneous key presses, rapid button mashing, or held keys during state changes need to be handled gracefully.

## Keyboard Input

Keyboard input is the foundation of PC gaming. There are two main approaches: event-based and state-based.

### Claude Code Prompt

```
Prompt: "Create a comprehensive keyboard input handler that tracks key states
(pressed, held, released), handles WASD movement with diagonal support,
prevents key repeat from browser, and includes debug visualization showing
which keys are currently pressed. Add support for key combinations."
```

### Complete Implementation

```javascript
class KeyboardInput {
    constructor() {
        // Track key states
        this.keys = {};
        this.keysPressed = {}; // Triggered once when key first pressed
        this.keysReleased = {}; // Triggered once when key released

        // Key bindings (customizable)
        this.bindings = {
            up: ['ArrowUp', 'KeyW'],
            down: ['ArrowDown', 'KeyS'],
            left: ['ArrowLeft', 'KeyA'],
            right: ['ArrowRight', 'KeyD'],
            jump: ['Space', 'KeyZ'],
            attack: ['KeyX'],
            special: ['KeyC'],
            interact: ['KeyE'],
            pause: ['Escape', 'KeyP']
        };

        // Debug info
        this.debugEnabled = false;

        // Setup event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        window.addEventListener('keydown', (e) => this.handleKeyDown(e));
        window.addEventListener('keyup', (e) => this.handleKeyUp(e));

        // Prevent default behavior for game keys
        window.addEventListener('keydown', (e) => {
            if (this.isGameKey(e.code)) {
                e.preventDefault();
            }
        });
    }

    handleKeyDown(e) {
        const code = e.code;

        // Only trigger pressed state once (prevents key repeat)
        if (!this.keys[code]) {
            this.keysPressed[code] = true;
        }

        this.keys[code] = true;
    }

    handleKeyUp(e) {
        const code = e.code;
        this.keys[code] = false;
        this.keysReleased[code] = true;
    }

    isGameKey(code) {
        // Check if this key is bound to any game action
        for (const action in this.bindings) {
            if (this.bindings[action].includes(code)) {
                return true;
            }
        }
        return false;
    }

    // Check if key is currently held down
    isKeyDown(code) {
        return this.keys[code] || false;
    }

    // Check if key was just pressed this frame
    isKeyPressed(code) {
        return this.keysPressed[code] || false;
    }

    // Check if key was just released this frame
    isKeyReleased(code) {
        return this.keysReleased[code] || false;
    }

    // Check if action is active (checks all bound keys)
    isActionDown(action) {
        const codes = this.bindings[action];
        if (!codes) return false;
        return codes.some(code => this.isKeyDown(code));
    }

    isActionPressed(action) {
        const codes = this.bindings[action];
        if (!codes) return false;
        return codes.some(code => this.isKeyPressed(code));
    }

    isActionReleased(action) {
        const codes = this.bindings[action];
        if (!codes) return false;
        return codes.some(code => this.isKeyReleased(code));
    }

    // Get movement vector from input
    getMovementVector() {
        const x = (this.isActionDown('right') ? 1 : 0) -
                  (this.isActionDown('left') ? 1 : 0);
        const y = (this.isActionDown('down') ? 1 : 0) -
                  (this.isActionDown('up') ? 1 : 0);

        // Normalize diagonal movement
        if (x !== 0 && y !== 0) {
            const length = Math.sqrt(x * x + y * y);
            return { x: x / length, y: y / length };
        }

        return { x, y };
    }

    // Call this at the end of each frame to reset pressed/released states
    update() {
        this.keysPressed = {};
        this.keysReleased = {};
    }

    // Rebind a key to an action
    rebindKey(action, newCode) {
        if (!this.bindings[action]) {
            this.bindings[action] = [];
        }
        this.bindings[action].push(newCode);
    }

    // Clear all keys for an action and set new one
    setBinding(action, codes) {
        this.bindings[action] = Array.isArray(codes) ? codes : [codes];
    }

    // Reset all key states (useful when window loses focus)
    reset() {
        this.keys = {};
        this.keysPressed = {};
        this.keysReleased = {};
    }

    // Debug visualization
    renderDebug(ctx, x, y) {
        if (!this.debugEnabled) return;

        ctx.save();
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(x, y, 300, 200);

        ctx.fillStyle = '#0f0';
        ctx.font = '14px monospace';
        ctx.fillText('Keyboard Input Debug', x + 10, y + 20);

        let offsetY = 40;
        for (const action in this.bindings) {
            const active = this.isActionDown(action);
            ctx.fillStyle = active ? '#0f0' : '#666';
            ctx.fillText(`${action}: ${active ? 'ON' : 'OFF'}`, x + 10, y + offsetY);
            offsetY += 20;
        }

        ctx.restore();
    }
}

// Usage Example
const keyboard = new KeyboardInput();
keyboard.debugEnabled = true;

// In game loop
function gameLoop(timestamp) {
    // Check input
    if (keyboard.isActionPressed('jump')) {
        console.log('Jump!');
    }

    if (keyboard.isActionDown('attack')) {
        console.log('Attacking...');
    }

    // Get movement
    const movement = keyboard.getMovementVector();
    player.x += movement.x * speed * deltaTime;
    player.y += movement.y * speed * deltaTime;

    // Update keyboard (clear pressed/released states)
    keyboard.update();

    requestAnimationFrame(gameLoop);
}

// Handle window losing focus
window.addEventListener('blur', () => {
    keyboard.reset();
});
```

### Key Features

1. **State Tracking**: Distinguishes between held, pressed (once), and released
2. **No Key Repeat**: Browser key repeat is ignored
3. **Action Bindings**: Multiple keys can trigger the same action
4. **Diagonal Normalization**: Diagonal movement doesn't make you faster
5. **Customizable Bindings**: Players can rebind keys
6. **Debug Visualization**: See which keys are active in real-time

## Mouse Input

Mouse input includes clicking, movement, and dragging. Essential for point-and-click games, strategy games, and menu navigation.

### Claude Code Prompt

```
Prompt: "Create a mouse input handler that tracks button states, mouse position
in both screen and world coordinates, click events, drag events with start/end
positions, and hover states. Include support for mouse wheel scrolling and
right-click prevention. Add visual feedback for mouse position and debug info."
```

### Implementation

```javascript
class MouseInput {
    constructor(canvas) {
        this.canvas = canvas;

        // Button states (0 = left, 1 = middle, 2 = right)
        this.buttons = [false, false, false];
        this.buttonsPressed = [false, false, false];
        this.buttonsReleased = [false, false, false];

        // Position
        this.x = 0;
        this.y = 0;
        this.prevX = 0;
        this.prevY = 0;

        // World position (accounting for camera)
        this.worldX = 0;
        this.worldY = 0;

        // Drag state
        this.dragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.dragButton = -1;

        // Wheel
        this.wheelDelta = 0;

        // Hover
        this.hoverTarget = null;

        // Camera offset for world coordinates
        this.cameraX = 0;
        this.cameraY = 0;

        this.setupEventListeners();
    }

    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('wheel', (e) => this.handleWheel(e));
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());

        // Handle mouse leaving canvas
        this.canvas.addEventListener('mouseleave', () => this.reset());
    }

    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.x = e.clientX - rect.left;
        this.y = e.clientY - rect.top;

        this.updateWorldPosition();

        if (!this.buttons[e.button]) {
            this.buttonsPressed[e.button] = true;

            // Start drag
            if (e.button === 0) { // Left click
                this.dragging = true;
                this.dragStartX = this.x;
                this.dragStartY = this.y;
                this.dragButton = e.button;
            }
        }

        this.buttons[e.button] = true;
    }

    handleMouseUp(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.x = e.clientX - rect.left;
        this.y = e.clientY - rect.top;

        this.updateWorldPosition();

        this.buttons[e.button] = false;
        this.buttonsReleased[e.button] = true;

        // End drag
        if (this.dragging && e.button === this.dragButton) {
            this.dragging = false;
            this.onDragEnd(this.dragStartX, this.dragStartY, this.x, this.y);
        }
    }

    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();

        this.prevX = this.x;
        this.prevY = this.y;

        this.x = e.clientX - rect.left;
        this.y = e.clientY - rect.top;

        this.updateWorldPosition();
    }

    handleWheel(e) {
        e.preventDefault();
        this.wheelDelta = e.deltaY;
    }

    updateWorldPosition() {
        this.worldX = this.x + this.cameraX;
        this.worldY = this.y + this.cameraY;
    }

    // Set camera position for world coordinate calculation
    setCamera(x, y) {
        this.cameraX = x;
        this.cameraY = y;
        this.updateWorldPosition();
    }

    // Check if button is held
    isButtonDown(button = 0) {
        return this.buttons[button];
    }

    // Check if button was just pressed
    isButtonPressed(button = 0) {
        return this.buttonsPressed[button];
    }

    // Check if button was just released
    isButtonReleased(button = 0) {
        return this.buttonsReleased[button];
    }

    // Get mouse movement delta
    getDelta() {
        return {
            x: this.x - this.prevX,
            y: this.y - this.prevY
        };
    }

    // Check if mouse is in a rectangular area
    isInRect(x, y, width, height) {
        return this.x >= x && this.x <= x + width &&
               this.y >= y && this.y <= y + height;
    }

    // Check if mouse is in a circle
    isInCircle(centerX, centerY, radius) {
        const dx = this.x - centerX;
        const dy = this.y - centerY;
        return Math.sqrt(dx * dx + dy * dy) <= radius;
    }

    // Get drag info
    getDragInfo() {
        if (!this.dragging) return null;

        return {
            startX: this.dragStartX,
            startY: this.dragStartY,
            currentX: this.x,
            currentY: this.y,
            deltaX: this.x - this.dragStartX,
            deltaY: this.y - this.dragStartY
        };
    }

    // Override this to handle drag end
    onDragEnd(startX, startY, endX, endY) {
        // Custom logic here
        console.log(`Dragged from (${startX}, ${startY}) to (${endX}, ${endY})`);
    }

    update() {
        // Clear pressed/released states
        this.buttonsPressed = [false, false, false];
        this.buttonsReleased = [false, false, false];
        this.wheelDelta = 0;
    }

    reset() {
        this.buttons = [false, false, false];
        this.buttonsPressed = [false, false, false];
        this.buttonsReleased = [false, false, false];
        this.dragging = false;
        this.wheelDelta = 0;
    }

    renderDebug(ctx) {
        ctx.save();

        // Crosshair at mouse position
        ctx.strokeStyle = '#ff00ff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(this.x - 10, this.y);
        ctx.lineTo(this.x + 10, this.y);
        ctx.moveTo(this.x, this.y - 10);
        ctx.lineTo(this.x, this.y + 10);
        ctx.stroke();

        // Drag visualization
        if (this.dragging) {
            ctx.strokeStyle = '#00ffff';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(this.dragStartX, this.dragStartY);
            ctx.lineTo(this.x, this.y);
            ctx.stroke();

            // Start point
            ctx.fillStyle = '#00ffff';
            ctx.beginPath();
            ctx.arc(this.dragStartX, this.dragStartY, 5, 0, Math.PI * 2);
            ctx.fill();
        }

        // Info panel
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(10, 10, 250, 120);

        ctx.fillStyle = '#0f0';
        ctx.font = '14px monospace';
        ctx.fillText('Mouse Input Debug', 20, 30);
        ctx.fillText(`Screen: (${Math.floor(this.x)}, ${Math.floor(this.y)})`, 20, 50);
        ctx.fillText(`World: (${Math.floor(this.worldX)}, ${Math.floor(this.worldY)})`, 20, 70);
        ctx.fillText(`Left: ${this.buttons[0] ? 'DOWN' : 'UP'}`, 20, 90);
        ctx.fillText(`Dragging: ${this.dragging ? 'YES' : 'NO'}`, 20, 110);

        ctx.restore();
    }
}

// Usage
const canvas = document.getElementById('gameCanvas');
const mouse = new MouseInput(canvas);

// Game loop
function gameLoop() {
    // Check for clicks
    if (mouse.isButtonPressed(0)) {
        console.log(`Clicked at (${mouse.x}, ${mouse.y})`);
    }

    // Check hover over button
    if (mouse.isInRect(100, 100, 200, 50)) {
        // Show hover effect
        if (mouse.isButtonPressed(0)) {
            console.log('Button clicked!');
        }
    }

    // Handle drag
    const dragInfo = mouse.getDragInfo();
    if (dragInfo) {
        // Update preview or selection box
        console.log(`Dragging: ${dragInfo.deltaX}, ${dragInfo.deltaY}`);
    }

    // Handle zoom with wheel
    if (mouse.wheelDelta !== 0) {
        const zoomFactor = mouse.wheelDelta > 0 ? 0.9 : 1.1;
        camera.zoom *= zoomFactor;
    }

    mouse.renderDebug(ctx);
    mouse.update();

    requestAnimationFrame(gameLoop);
}
```

## Touch Input for Mobile

Touch input is essential for mobile games. It's more complex than mouse input because it supports multiple simultaneous touches.

### Claude Code Prompt

```
Prompt: "Create a comprehensive touch input handler that supports multi-touch,
gesture detection (tap, double-tap, swipe, pinch-to-zoom), and virtual joystick
controls. Include visual feedback for touches and support for both touch events
and pointer events as fallback."
```

### Implementation

```javascript
class TouchInput {
    constructor(canvas) {
        this.canvas = canvas;

        // Active touches
        this.touches = new Map(); // Map of touch ID to touch data

        // Gestures
        this.tap = null;
        this.doubleTap = null;
        this.swipe = null;
        this.pinch = null;

        // Last tap time for double-tap detection
        this.lastTapTime = 0;
        this.doubleTapThreshold = 300; // ms

        // Virtual joystick
        this.joystick = {
            active: false,
            startX: 0,
            startY: 0,
            currentX: 0,
            currentY: 0,
            radius: 50,
            deadzone: 0.2
        };

        // Swipe detection
        this.swipeThreshold = 50; // pixels
        this.swipeTimeout = 300; // ms

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Touch events
        this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: false });
        this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: false });
        this.canvas.addEventListener('touchend', (e) => this.handleTouchEnd(e), { passive: false });
        this.canvas.addEventListener('touchcancel', (e) => this.handleTouchEnd(e), { passive: false });

        // Prevent default touch behaviors
        this.canvas.addEventListener('touchstart', (e) => e.preventDefault());
    }

    handleTouchStart(e) {
        const rect = this.canvas.getBoundingClientRect();

        for (let i = 0; i < e.changedTouches.length; i++) {
            const touch = e.changedTouches[i];
            const x = touch.clientX - rect.left;
            const y = touch.clientY - rect.top;

            const touchData = {
                id: touch.identifier,
                startX: x,
                startY: y,
                currentX: x,
                currentY: y,
                prevX: x,
                prevY: y,
                startTime: performance.now()
            };

            this.touches.set(touch.identifier, touchData);

            // Activate virtual joystick if touch is on left side
            if (x < this.canvas.width / 2 && !this.joystick.active) {
                this.joystick.active = true;
                this.joystick.startX = x;
                this.joystick.startY = y;
                this.joystick.currentX = x;
                this.joystick.currentY = y;
                this.joystick.touchId = touch.identifier;
            }
        }

        // Detect pinch start
        if (this.touches.size === 2) {
            this.startPinch();
        }
    }

    handleTouchMove(e) {
        const rect = this.canvas.getBoundingClientRect();

        for (let i = 0; i < e.changedTouches.length; i++) {
            const touch = e.changedTouches[i];
            const touchData = this.touches.get(touch.identifier);

            if (touchData) {
                touchData.prevX = touchData.currentX;
                touchData.prevY = touchData.currentY;
                touchData.currentX = touch.clientX - rect.left;
                touchData.currentY = touch.clientY - rect.top;

                // Update joystick
                if (this.joystick.active && this.joystick.touchId === touch.identifier) {
                    this.joystick.currentX = touchData.currentX;
                    this.joystick.currentY = touchData.currentY;
                }
            }
        }

        // Update pinch
        if (this.touches.size === 2) {
            this.updatePinch();
        }
    }

    handleTouchEnd(e) {
        for (let i = 0; i < e.changedTouches.length; i++) {
            const touch = e.changedTouches[i];
            const touchData = this.touches.get(touch.identifier);

            if (touchData) {
                const duration = performance.now() - touchData.startTime;
                const dx = touchData.currentX - touchData.startX;
                const dy = touchData.currentY - touchData.startY;
                const distance = Math.sqrt(dx * dx + dy * dy);

                // Detect tap
                if (distance < 10 && duration < 300) {
                    this.detectTap(touchData);
                }

                // Detect swipe
                if (distance > this.swipeThreshold && duration < this.swipeTimeout) {
                    this.detectSwipe(touchData, dx, dy);
                }

                this.touches.delete(touch.identifier);

                // Deactivate joystick
                if (this.joystick.active && this.joystick.touchId === touch.identifier) {
                    this.joystick.active = false;
                }
            }
        }

        // End pinch
        if (this.touches.size < 2) {
            this.pinch = null;
        }
    }

    detectTap(touchData) {
        const now = performance.now();

        this.tap = {
            x: touchData.currentX,
            y: touchData.currentY,
            timestamp: now
        };

        // Check for double tap
        if (now - this.lastTapTime < this.doubleTapThreshold) {
            this.doubleTap = {
                x: touchData.currentX,
                y: touchData.currentY,
                timestamp: now
            };
        }

        this.lastTapTime = now;
    }

    detectSwipe(touchData, dx, dy) {
        const absDx = Math.abs(dx);
        const absDy = Math.abs(dy);

        let direction;
        if (absDx > absDy) {
            direction = dx > 0 ? 'right' : 'left';
        } else {
            direction = dy > 0 ? 'down' : 'up';
        }

        this.swipe = {
            direction,
            distance: Math.sqrt(dx * dx + dy * dy),
            dx,
            dy,
            startX: touchData.startX,
            startY: touchData.startY,
            endX: touchData.currentX,
            endY: touchData.currentY
        };
    }

    startPinch() {
        const touches = Array.from(this.touches.values());
        if (touches.length === 2) {
            const dx = touches[1].currentX - touches[0].currentX;
            const dy = touches[1].currentY - touches[0].currentY;
            const distance = Math.sqrt(dx * dx + dy * dy);

            this.pinch = {
                startDistance: distance,
                currentDistance: distance,
                scale: 1.0
            };
        }
    }

    updatePinch() {
        const touches = Array.from(this.touches.values());
        if (touches.length === 2 && this.pinch) {
            const dx = touches[1].currentX - touches[0].currentX;
            const dy = touches[1].currentY - touches[0].currentY;
            const distance = Math.sqrt(dx * dx + dy * dy);

            this.pinch.currentDistance = distance;
            this.pinch.scale = distance / this.pinch.startDistance;
        }
    }

    // Get virtual joystick direction vector
    getJoystickVector() {
        if (!this.joystick.active) {
            return { x: 0, y: 0 };
        }

        const dx = this.joystick.currentX - this.joystick.startX;
        const dy = this.joystick.currentY - this.joystick.startY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Apply deadzone
        if (distance < this.joystick.radius * this.joystick.deadzone) {
            return { x: 0, y: 0 };
        }

        // Clamp to joystick radius
        const clampedDistance = Math.min(distance, this.joystick.radius);
        const normalizedDistance = clampedDistance / this.joystick.radius;

        const angle = Math.atan2(dy, dx);
        return {
            x: Math.cos(angle) * normalizedDistance,
            y: Math.sin(angle) * normalizedDistance
        };
    }

    // Check if position is being touched
    isTouchedAt(x, y, radius = 20) {
        for (const touch of this.touches.values()) {
            const dx = touch.currentX - x;
            const dy = touch.currentY - y;
            if (Math.sqrt(dx * dx + dy * dy) <= radius) {
                return true;
            }
        }
        return false;
    }

    update() {
        // Clear one-time gestures
        this.tap = null;
        this.doubleTap = null;
        this.swipe = null;
    }

    renderDebug(ctx) {
        ctx.save();

        // Draw all active touches
        for (const touch of this.touches.values()) {
            // Touch point
            ctx.fillStyle = 'rgba(255, 0, 255, 0.5)';
            ctx.beginPath();
            ctx.arc(touch.currentX, touch.currentY, 30, 0, Math.PI * 2);
            ctx.fill();

            // Touch trail
            ctx.strokeStyle = 'rgba(255, 0, 255, 0.3)';
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.moveTo(touch.startX, touch.startY);
            ctx.lineTo(touch.currentX, touch.currentY);
            ctx.stroke();
        }

        // Draw virtual joystick
        if (this.joystick.active) {
            // Base
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(this.joystick.startX, this.joystick.startY,
                   this.joystick.radius, 0, Math.PI * 2);
            ctx.stroke();

            // Deadzone
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.beginPath();
            ctx.arc(this.joystick.startX, this.joystick.startY,
                   this.joystick.radius * this.joystick.deadzone, 0, Math.PI * 2);
            ctx.stroke();

            // Stick
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.beginPath();
            ctx.arc(this.joystick.currentX, this.joystick.currentY, 20, 0, Math.PI * 2);
            ctx.fill();
        }

        // Show gesture info
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(10, 10, 300, 150);

        ctx.fillStyle = '#0f0';
        ctx.font = '14px monospace';
        ctx.fillText('Touch Input Debug', 20, 30);
        ctx.fillText(`Active touches: ${this.touches.size}`, 20, 50);

        if (this.tap) {
            ctx.fillText(`Tap at (${Math.floor(this.tap.x)}, ${Math.floor(this.tap.y)})`, 20, 70);
        }

        if (this.swipe) {
            ctx.fillText(`Swipe: ${this.swipe.direction}`, 20, 90);
        }

        if (this.pinch) {
            ctx.fillText(`Pinch scale: ${this.pinch.scale.toFixed(2)}`, 20, 110);
        }

        const joystickVec = this.getJoystickVector();
        ctx.fillText(`Joystick: (${joystickVec.x.toFixed(2)}, ${joystickVec.y.toFixed(2)})`, 20, 130);

        ctx.restore();
    }
}

// Usage
const canvas = document.getElementById('gameCanvas');
const touch = new TouchInput(canvas);

function gameLoop() {
    // Check for tap
    if (touch.tap) {
        console.log(`Tapped at (${touch.tap.x}, ${touch.tap.y})`);
    }

    // Check for swipe
    if (touch.swipe) {
        console.log(`Swiped ${touch.swipe.direction}`);
    }

    // Use joystick for movement
    const joystick = touch.getJoystickVector();
    player.x += joystick.x * speed * deltaTime;
    player.y += joystick.y * speed * deltaTime;

    // Handle pinch zoom
    if (touch.pinch) {
        camera.zoom = baseZoom * touch.pinch.scale;
    }

    touch.renderDebug(ctx);
    touch.update();

    requestAnimationFrame(gameLoop);
}
```

## Gamepad/Controller Support

Modern browsers support the Gamepad API for console controllers and other game controllers.

### Claude Code Prompt

```
Prompt: "Create a gamepad input handler that supports Xbox and PlayStation
controllers with button mapping, analog stick input with deadzone, trigger
support, and vibration/rumble. Include automatic gamepad detection and
connection/disconnection handling. Add visual debug display showing all
button and stick states."
```

### Implementation

```javascript
class GamepadInput {
    constructor() {
        this.gamepads = {};
        this.buttonStates = {};
        this.previousButtonStates = {};

        // Deadzone for analog sticks (0.0 to 1.0)
        this.deadzone = 0.15;

        // Button mapping for standard gamepad
        this.buttonNames = [
            'A', 'B', 'X', 'Y',           // 0-3
            'LB', 'RB',                    // 4-5
            'LT', 'RT',                    // 6-7
            'Select', 'Start',             // 8-9
            'LS', 'RS',                    // 10-11 (stick buttons)
            'DPad-Up', 'DPad-Down',       // 12-13
            'DPad-Left', 'DPad-Right'     // 14-15
        ];

        this.setupEventListeners();
    }

    setupEventListeners() {
        window.addEventListener('gamepadconnected', (e) => {
            console.log(`Gamepad connected: ${e.gamepad.id}`);
            this.gamepads[e.gamepad.index] = e.gamepad;
        });

        window.addEventListener('gamepaddisconnected', (e) => {
            console.log(`Gamepad disconnected: ${e.gamepad.id}`);
            delete this.gamepads[e.gamepad.index];
        });
    }

    update() {
        // Update gamepad states (required for some browsers)
        const gamepads = navigator.getGamepads();

        for (let i = 0; i < gamepads.length; i++) {
            if (gamepads[i]) {
                this.gamepads[i] = gamepads[i];
            }
        }

        // Store previous button states for pressed/released detection
        this.previousButtonStates = { ...this.buttonStates };
        this.buttonStates = {};

        // Update button states
        for (const index in this.gamepads) {
            const gamepad = this.gamepads[index];
            if (!gamepad) continue;

            for (let i = 0; i < gamepad.buttons.length; i++) {
                const key = `${index}_${i}`;
                this.buttonStates[key] = gamepad.buttons[i].pressed;
            }
        }
    }

    // Get first connected gamepad
    getGamepad(index = 0) {
        return this.gamepads[index] || null;
    }

    // Check if button is currently pressed
    isButtonDown(gamepadIndex, buttonIndex) {
        const key = `${gamepadIndex}_${buttonIndex}`;
        return this.buttonStates[key] || false;
    }

    // Check if button was just pressed this frame
    isButtonPressed(gamepadIndex, buttonIndex) {
        const key = `${gamepadIndex}_${buttonIndex}`;
        return this.buttonStates[key] && !this.previousButtonStates[key];
    }

    // Check if button was just released this frame
    isButtonReleased(gamepadIndex, buttonIndex) {
        const key = `${gamepadIndex}_${buttonIndex}`;
        return !this.buttonStates[key] && this.previousButtonStates[key];
    }

    // Get button pressure (0.0 to 1.0) for analog buttons
    getButtonValue(gamepadIndex, buttonIndex) {
        const gamepad = this.gamepads[gamepadIndex];
        if (!gamepad || !gamepad.buttons[buttonIndex]) return 0;

        return gamepad.buttons[buttonIndex].value;
    }

    // Get left stick position with deadzone
    getLeftStick(gamepadIndex = 0) {
        const gamepad = this.gamepads[gamepadIndex];
        if (!gamepad) return { x: 0, y: 0 };

        let x = gamepad.axes[0] || 0;
        let y = gamepad.axes[1] || 0;

        // Apply deadzone
        const magnitude = Math.sqrt(x * x + y * y);
        if (magnitude < this.deadzone) {
            return { x: 0, y: 0 };
        }

        // Normalize and scale
        const scale = (magnitude - this.deadzone) / (1 - this.deadzone);
        const angle = Math.atan2(y, x);

        return {
            x: Math.cos(angle) * scale,
            y: Math.sin(angle) * scale
        };
    }

    // Get right stick position with deadzone
    getRightStick(gamepadIndex = 0) {
        const gamepad = this.gamepads[gamepadIndex];
        if (!gamepad) return { x: 0, y: 0 };

        let x = gamepad.axes[2] || 0;
        let y = gamepad.axes[3] || 0;

        // Apply deadzone (same as left stick)
        const magnitude = Math.sqrt(x * x + y * y);
        if (magnitude < this.deadzone) {
            return { x: 0, y: 0 };
        }

        const scale = (magnitude - this.deadzone) / (1 - this.deadzone);
        const angle = Math.atan2(y, x);

        return {
            x: Math.cos(angle) * scale,
            y: Math.sin(angle) * scale
        };
    }

    // Vibrate controller (if supported)
    vibrate(gamepadIndex = 0, duration = 200, weakMagnitude = 0.5, strongMagnitude = 0.5) {
        const gamepad = this.gamepads[gamepadIndex];
        if (!gamepad || !gamepad.vibrationActuator) {
            console.log('Vibration not supported on this gamepad');
            return;
        }

        gamepad.vibrationActuator.playEffect('dual-rumble', {
            duration,
            weakMagnitude,
            strongMagnitude
        });
    }

    // Get number of connected gamepads
    getConnectedCount() {
        return Object.keys(this.gamepads).length;
    }

    renderDebug(ctx, x, y) {
        const gamepad = this.getGamepad(0);

        if (!gamepad) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
            ctx.fillRect(x, y, 400, 50);
            ctx.fillStyle = '#f00';
            ctx.font = '16px monospace';
            ctx.fillText('No gamepad connected', x + 10, y + 30);
            return;
        }

        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(x, y, 400, 350);

        ctx.fillStyle = '#0f0';
        ctx.font = '14px monospace';
        ctx.fillText(`Gamepad: ${gamepad.id}`, x + 10, y + 20);

        // Draw buttons
        let offsetY = 45;
        ctx.fillText('Buttons:', x + 10, y + offsetY);
        offsetY += 20;

        for (let i = 0; i < Math.min(gamepad.buttons.length, 16); i++) {
            const button = gamepad.buttons[i];
            const pressed = button.pressed;
            const value = button.value.toFixed(2);

            ctx.fillStyle = pressed ? '#0f0' : '#666';
            const buttonName = this.buttonNames[i] || `Button ${i}`;
            ctx.fillText(`${buttonName}: ${pressed ? 'ON' : 'OFF'} (${value})`,
                        x + 10, y + offsetY);
            offsetY += 18;

            if ((i + 1) % 8 === 0) offsetY += 5;
        }

        // Draw sticks
        offsetY += 10;
        const leftStick = this.getLeftStick(0);
        const rightStick = this.getRightStick(0);

        ctx.fillStyle = '#fff';
        ctx.fillText(`Left Stick: (${leftStick.x.toFixed(2)}, ${leftStick.y.toFixed(2)})`,
                    x + 10, y + offsetY);
        offsetY += 20;
        ctx.fillText(`Right Stick: (${rightStick.x.toFixed(2)}, ${rightStick.y.toFixed(2)})`,
                    x + 10, y + offsetY);

        // Visual representation of sticks
        this.drawStick(ctx, x + 320, y + 280, leftStick);
        this.drawStick(ctx, x + 360, y + 280, rightStick);
    }

    drawStick(ctx, centerX, centerY, stick) {
        const radius = 25;

        // Deadzone circle
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius * this.deadzone, 0, Math.PI * 2);
        ctx.stroke();

        // Outer circle
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.stroke();

        // Stick position
        const stickX = centerX + stick.x * radius;
        const stickY = centerY + stick.y * radius;

        ctx.fillStyle = '#0f0';
        ctx.beginPath();
        ctx.arc(stickX, stickY, 5, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Usage
const gamepad = new GamepadInput();

function gameLoop() {
    gamepad.update();

    // Check buttons
    if (gamepad.isButtonPressed(0, 0)) { // A button
        player.jump();
        gamepad.vibrate(0, 100, 0.3, 0.3); // Light vibration
    }

    // Use left stick for movement
    const leftStick = gamepad.getLeftStick(0);
    player.x += leftStick.x * speed * deltaTime;
    player.y += leftStick.y * speed * deltaTime;

    // Use right stick for aiming
    const rightStick = gamepad.getRightStick(0);
    if (rightStick.x !== 0 || rightStick.y !== 0) {
        player.aimAngle = Math.atan2(rightStick.y, rightStick.x);
    }

    // Triggers for shooting
    const rightTrigger = gamepad.getButtonValue(0, 7);
    if (rightTrigger > 0.5) {
        player.shoot();
    }

    gamepad.renderDebug(ctx, 10, 10);

    requestAnimationFrame(gameLoop);
}
```

## Input Buffering and Queueing

Input buffering allows players to press buttons slightly before they're valid, improving responsiveness.

### Claude Code Prompt

```
Prompt: "Create an input buffer system that stores recent inputs and allows
checking if an input was pressed within a time window. Include combo detection
for fighting game style input sequences, and a visual debug display showing
the input buffer contents and detected combos."
```

### Implementation

```javascript
class InputBuffer {
    constructor(bufferTime = 0.15) {
        this.bufferTime = bufferTime; // seconds
        this.inputs = [];
        this.combos = new Map();

        // Define combos (example fighting game style)
        this.defineCombos();
    }

    defineCombos() {
        // Define combo sequences
        this.combos.set('hadouken', {
            sequence: ['down', 'down-right', 'right', 'attack'],
            window: 0.5, // Must complete within 0.5 seconds
            callback: () => console.log('Hadouken!')
        });

        this.combos.set('shoryuken', {
            sequence: ['right', 'down', 'down-right', 'attack'],
            window: 0.4,
            callback: () => console.log('Shoryuken!')
        });

        this.combos.set('double-jump', {
            sequence: ['jump', 'jump'],
            window: 0.3,
            callback: () => console.log('Double jump!')
        });
    }

    // Add input to buffer
    addInput(action, timestamp = performance.now()) {
        this.inputs.push({
            action,
            timestamp
        });

        // Check for combos
        this.checkCombos();
    }

    // Check if action was pressed within buffer time
    wasPressed(action, currentTime = performance.now()) {
        for (let i = this.inputs.length - 1; i >= 0; i--) {
            const input = this.inputs[i];
            const age = (currentTime - input.timestamp) / 1000;

            if (age > this.bufferTime) {
                break; // Too old
            }

            if (input.action === action && !input.consumed) {
                input.consumed = true; // Mark as consumed
                return true;
            }
        }

        return false;
    }

    // Check for combo sequences
    checkCombos() {
        const now = performance.now();

        for (const [name, combo] of this.combos) {
            if (this.matchesCombo(combo.sequence, combo.window, now)) {
                combo.callback();

                // Consume the inputs used in the combo
                let matched = 0;
                for (let i = this.inputs.length - 1; i >= 0 && matched < combo.sequence.length; i--) {
                    this.inputs[i].consumed = true;
                    matched++;
                }

                return name;
            }
        }

        return null;
    }

    matchesCombo(sequence, window, currentTime) {
        if (this.inputs.length < sequence.length) {
            return false;
        }

        // Check last N inputs match the sequence
        let matchIndex = sequence.length - 1;
        for (let i = this.inputs.length - 1; i >= 0 && matchIndex >= 0; i--) {
            const input = this.inputs[i];
            const age = (currentTime - input.timestamp) / 1000;

            if (age > window) {
                return false; // Too old
            }

            if (input.action === sequence[matchIndex]) {
                matchIndex--;
            }
        }

        return matchIndex < 0; // All sequence elements matched
    }

    // Clean up old inputs
    update(currentTime = performance.now()) {
        const maxAge = this.bufferTime * 1000;

        this.inputs = this.inputs.filter(input => {
            return (currentTime - input.timestamp) < maxAge * 2;
        });
    }

    // Debug visualization
    renderDebug(ctx, x, y) {
        ctx.save();

        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(x, y, 350, 200);

        ctx.fillStyle = '#0f0';
        ctx.font = '14px monospace';
        ctx.fillText('Input Buffer Debug', x + 10, y + 20);

        // Show buffered inputs
        const now = performance.now();
        let offsetY = 40;

        ctx.fillText('Recent Inputs:', x + 10, y + offsetY);
        offsetY += 20;

        for (let i = Math.max(0, this.inputs.length - 10); i < this.inputs.length; i++) {
            const input = this.inputs[i];
            const age = ((now - input.timestamp) / 1000).toFixed(3);
            const alpha = 1 - Math.min(age / this.bufferTime, 1);

            ctx.fillStyle = input.consumed
                ? `rgba(100, 100, 100, ${alpha})`
                : `rgba(0, 255, 0, ${alpha})`;

            ctx.fillText(`${input.action} (${age}s)`, x + 15, y + offsetY);
            offsetY += 18;
        }

        // Show combo list
        offsetY = 180;
        ctx.fillStyle = '#fff';
        ctx.font = '12px monospace';
        ctx.fillText('Available Combos:', x + 10, y + offsetY);

        ctx.restore();
    }
}

// Usage with keyboard input
const keyboard = new KeyboardInput();
const inputBuffer = new InputBuffer(0.15);

function gameLoop(timestamp) {
    const now = performance.now();

    // Add inputs to buffer
    if (keyboard.isActionPressed('jump')) {
        inputBuffer.addInput('jump', now);
    }

    if (keyboard.isActionPressed('attack')) {
        inputBuffer.addInput('attack', now);
    }

    // Check directional inputs for combos
    const movement = keyboard.getMovementVector();
    if (movement.y > 0) {
        if (movement.x > 0) inputBuffer.addInput('down-right', now);
        else if (movement.x < 0) inputBuffer.addInput('down-left', now);
        else inputBuffer.addInput('down', now);
    } else if (movement.x > 0) {
        inputBuffer.addInput('right', now);
    } else if (movement.x < 0) {
        inputBuffer.addInput('left', now);
    }

    // Check buffered jump (allows pressing jump before landing)
    if (player.onGround && inputBuffer.wasPressed('jump', now)) {
        player.jump();
    }

    inputBuffer.update(now);
    inputBuffer.renderDebug(ctx, 10, 300);

    keyboard.update();
    requestAnimationFrame(gameLoop);
}
```

## Multiple Input Methods Simultaneously

Modern games often need to support keyboard, mouse, gamepad, and touch all at once.

### Implementation

```javascript
class UnifiedInputManager {
    constructor(canvas) {
        this.canvas = canvas;

        // Initialize all input handlers
        this.keyboard = new KeyboardInput();
        this.mouse = new MouseInput(canvas);
        this.touch = new TouchInput(canvas);
        this.gamepad = new GamepadInput();

        // Detect primary input method
        this.primaryInput = 'keyboard'; // keyboard, gamepad, touch
        this.lastInputTime = {
            keyboard: 0,
            mouse: 0,
            touch: 0,
            gamepad: 0
        };
    }

    update() {
        this.keyboard.update();
        this.mouse.update();
        this.touch.update();
        this.gamepad.update();

        // Auto-detect primary input method
        this.detectPrimaryInput();
    }

    detectPrimaryInput() {
        const now = performance.now();

        // Check recent keyboard input
        if (Object.values(this.keyboard.keys).some(k => k)) {
            this.lastInputTime.keyboard = now;
            this.primaryInput = 'keyboard';
        }

        // Check gamepad input
        if (this.gamepad.getConnectedCount() > 0) {
            const leftStick = this.gamepad.getLeftStick(0);
            if (Math.abs(leftStick.x) > 0.1 || Math.abs(leftStick.y) > 0.1) {
                this.lastInputTime.gamepad = now;
                this.primaryInput = 'gamepad';
            }
        }

        // Check touch input
        if (this.touch.touches.size > 0) {
            this.lastInputTime.touch = now;
            this.primaryInput = 'touch';
        }
    }

    // Unified movement input
    getMovementVector() {
        switch (this.primaryInput) {
            case 'keyboard':
                return this.keyboard.getMovementVector();

            case 'gamepad':
                return this.gamepad.getLeftStick(0);

            case 'touch':
                return this.touch.getJoystickVector();

            default:
                return { x: 0, y: 0 };
        }
    }

    // Unified jump action
    isJumpPressed() {
        return this.keyboard.isActionPressed('jump') ||
               this.gamepad.isButtonPressed(0, 0) ||
               (this.touch.tap && this.touch.tap.x > this.canvas.width / 2);
    }

    // Unified attack action
    isAttackPressed() {
        return this.keyboard.isActionPressed('attack') ||
               this.gamepad.isButtonPressed(0, 2) ||
               this.mouse.isButtonPressed(0);
    }

    // Get aim direction (mouse, right stick, or touch)
    getAimVector() {
        // Mouse aiming (if mouse moved recently)
        if (performance.now() - this.lastInputTime.mouse < 100) {
            const dx = this.mouse.x - this.canvas.width / 2;
            const dy = this.mouse.y - this.canvas.height / 2;
            const length = Math.sqrt(dx * dx + dy * dy);
            return length > 0 ? { x: dx / length, y: dy / length } : { x: 1, y: 0 };
        }

        // Gamepad right stick
        const rightStick = this.gamepad.getRightStick(0);
        if (Math.abs(rightStick.x) > 0.1 || Math.abs(rightStick.y) > 0.1) {
            return rightStick;
        }

        // Default to movement direction
        return this.getMovementVector();
    }

    renderDebug(ctx) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(10, 10, 200, 80);

        ctx.fillStyle = '#0f0';
        ctx.font = '14px monospace';
        ctx.fillText('Unified Input', 20, 30);
        ctx.fillText(`Primary: ${this.primaryInput}`, 20, 50);

        const movement = this.getMovementVector();
        ctx.fillText(`Move: (${movement.x.toFixed(2)}, ${movement.y.toFixed(2)})`, 20, 70);
    }
}

// Usage
const canvas = document.getElementById('gameCanvas');
const input = new UnifiedInputManager(canvas);

function gameLoop() {
    input.update();

    // Use unified input
    const movement = input.getMovementVector();
    player.x += movement.x * speed * deltaTime;
    player.y += movement.y * speed * deltaTime;

    if (input.isJumpPressed()) {
        player.jump();
    }

    if (input.isAttackPressed()) {
        const aim = input.getAimVector();
        player.attack(aim);
    }

    input.renderDebug(ctx);

    requestAnimationFrame(gameLoop);
}
```

## Cross-Platform Input Considerations

Different platforms have different input characteristics and requirements.

### Best Practices

1. **Mobile-First Design**: Design UI elements large enough for touch (minimum 44x44 pixels)
2. **Gamepad Support**: Always test with controllers, not just keyboard
3. **Keyboard Shortcuts**: Provide keyboard shortcuts for all actions
4. **Mouse Precision**: Use mouse for precise aiming and selection
5. **Touch Gestures**: Support common gestures (pinch, swipe, tap)
6. **Input Remapping**: Allow players to customize controls
7. **Visual Feedback**: Show which input method is active

## Accessibility Considerations

Making your game accessible to all players is important.

### Implementation Tips

```javascript
// Example: Accessibility features in input handling
class AccessibleInputManager extends UnifiedInputManager {
    constructor(canvas) {
        super(canvas);

        this.settings = {
            holdToPress: false, // Convert holds to toggles
            autoRun: false, // Don't require holding movement
            inputAssist: true, // Generous input windows
            reducedPrecision: false, // Larger hitboxes for clicks
            remappableKeys: true // Allow full key remapping
        };
    }

    // Hold-to-toggle for actions
    isJumpPressed() {
        if (this.settings.holdToPress) {
            // Convert to toggle
            if (super.isJumpPressed()) {
                this.jumpToggled = !this.jumpToggled;
            }
            return this.jumpToggled;
        }

        return super.isJumpPressed();
    }

    // Auto-run feature
    getMovementVector() {
        const movement = super.getMovementVector();

        if (this.settings.autoRun && (movement.x !== 0 || movement.y !== 0)) {
            // Remember last movement direction
            this.lastMovement = movement;
        }

        return this.settings.autoRun && this.lastMovement ? this.lastMovement : movement;
    }
}
```

## Conclusion

Robust input handling is crucial for creating responsive, accessible games. Use the implementations in this guide as starting points and customize them for your specific game's needs. Always test with multiple input methods and consider accessibility from the start.

---

**Related Documentation:**
- [Game Loops and Timing](./game-loops-and-timing.md)
- [State Management](./state-management.md)
- [UI/UX](../07-ui-ux/)
