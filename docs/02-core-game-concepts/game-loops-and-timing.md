# Game Loops and Timing

The game loop is the heartbeat of every game ever made. It's the fundamental structure that drives all game logic, rendering, and interaction. Understanding game loops and timing is essential for creating smooth, responsive games that run consistently across different devices and frame rates.

## Table of Contents

1. [What is a Game Loop?](#what-is-a-game-loop)
2. [Why Game Loops Matter](#why-game-loops-matter)
3. [The Basic Game Loop Pattern](#the-basic-game-loop-pattern)
4. [requestAnimationFrame vs setInterval](#requestanimationframe-vs-setinterval)
5. [Variable Timestep Implementation](#variable-timestep-implementation)
6. [Fixed Timestep Implementation](#fixed-timestep-implementation)
7. [Semi-Fixed Timestep (Hybrid Approach)](#semi-fixed-timestep-hybrid-approach)
8. [Delta Time Calculations](#delta-time-calculations)
9. [Frame-Rate Independence](#frame-rate-independence)
10. [Performance Implications](#performance-implications)
11. [Common Timing Bugs](#common-timing-bugs)
12. [Integration with Game State](#integration-with-game-state)
13. [Complete Working Examples](#complete-working-examples)

## What is a Game Loop?

A game loop is a continuous cycle that runs throughout your game's lifetime. Each iteration of the loop performs three essential tasks:

1. **Process Input**: Check for and handle player input (keyboard, mouse, touch, gamepad)
2. **Update Game State**: Update positions, velocities, AI, animations, and all game logic
3. **Render**: Draw the current state of the game to the screen

This loop runs continuously, typically 30-60+ times per second, creating the illusion of smooth motion and responsive interaction. The speed at which this loop executes is called the frame rate, measured in frames per second (FPS).

### The Game Loop Cycle

```
┌─────────────────────────────────────┐
│   Start Game Loop                   │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   1. Calculate Delta Time           │
│      (time since last frame)        │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   2. Process Input                  │
│      - Keyboard events              │
│      - Mouse/touch events           │
│      - Gamepad input                │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   3. Update Game Logic              │
│      - Move objects                 │
│      - Check collisions             │
│      - Update AI                    │
│      - Update animations            │
│      - Update physics               │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   4. Render Frame                   │
│      - Clear screen                 │
│      - Draw background              │
│      - Draw game objects            │
│      - Draw UI                      │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   Request Next Frame                │
│   (loop back to start)              │
└─────────────────────────────────────┘
```

## Why Game Loops Matter

### Consistency Across Hardware

Different computers run at different speeds. A game loop ensures that gameplay remains consistent whether running on a high-end gaming PC or a modest laptop. Without proper timing, your game might run in fast-forward on powerful machines and in slow-motion on weaker ones.

### Smooth Animation and Movement

By updating the game state many times per second and re-rendering, we create smooth animation. The faster the loop runs (higher FPS), the smoother the experience, up to the limits of display refresh rates.

### Responsive Input

A fast game loop means minimal delay between player input and on-screen response. This is critical for games requiring precision, like platformers, fighting games, or first-person shooters.

### Predictable Simulation

Physics simulations, AI behaviors, and game logic all depend on consistent timing. A well-implemented game loop ensures that objects fall at the same speed, bullets travel the same distance, and AI makes decisions at regular intervals.

## The Basic Game Loop Pattern

At its simplest, a game loop is just a function that calls itself repeatedly:

```javascript
function gameLoop() {
    // Update game state
    update();

    // Render current state
    render();

    // Schedule next frame
    requestAnimationFrame(gameLoop);
}

// Start the loop
gameLoop();
```

However, this basic pattern has a critical flaw: it doesn't account for timing. The update and render functions don't know how much time has passed, making frame-rate independence impossible.

## requestAnimationFrame vs setInterval

JavaScript provides several ways to implement game loops. Understanding their differences is crucial for making the right choice.

### requestAnimationFrame (Recommended)

```javascript
function gameLoop(timestamp) {
    // Game logic here

    requestAnimationFrame(gameLoop);
}

requestAnimationFrame(gameLoop);
```

**Advantages:**
- Automatically syncs with browser refresh rate (usually 60 FPS)
- Pauses when tab is not visible (saves battery/CPU)
- Optimized by browser for smooth rendering
- Provides high-resolution timestamp
- Prevents visual tearing

**Disadvantages:**
- Variable timing (not guaranteed to be exact)
- Tied to display refresh rate
- Requires polyfill for older browsers

### setInterval

```javascript
const FPS = 60;
const frameTime = 1000 / FPS;

setInterval(() => {
    update();
    render();
}, frameTime);
```

**Advantages:**
- Simple to understand
- Predictable timing (in theory)
- Works in older browsers

**Disadvantages:**
- Doesn't sync with display refresh
- Runs even when tab is hidden (wastes resources)
- Can cause timing drift and jitter
- Not optimized for animation
- Can cause visual tearing

### setTimeout (Recursive)

```javascript
const FPS = 60;
const frameTime = 1000 / FPS;

function gameLoop() {
    update();
    render();

    setTimeout(gameLoop, frameTime);
}

gameLoop();
```

**Advantages:**
- More precise than setInterval
- Can adjust timing dynamically

**Disadvantages:**
- Same issues as setInterval regarding display sync
- More complex than requestAnimationFrame

**Verdict**: Use `requestAnimationFrame` for browser games. It's the industry standard for a reason.

## Variable Timestep Implementation

Variable timestep means the game loop adapts to the actual time that has passed between frames. This is the most common approach for browser games.

### Claude Code Prompt

```
Prompt: "Create a complete game loop using requestAnimationFrame with variable
timestep. Include delta time calculation in seconds, FPS counter that updates
every second, and pause/resume functionality. Add a simple moving square demo
that moves at 200 pixels per second to demonstrate frame-rate independence."
```

### Complete Implementation

```javascript
class GameLoopVariable {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Timing
        this.lastTime = 0;
        this.deltaTime = 0;
        this.fps = 0;
        this.frameCount = 0;
        this.fpsUpdateTime = 0;

        // Game state
        this.running = false;
        this.squareX = 0;
        this.squareY = canvas.height / 2 - 25;
        this.squareSpeed = 200; // pixels per second

        // Bind methods
        this.loop = this.loop.bind(this);
    }

    start() {
        if (!this.running) {
            this.running = true;
            this.lastTime = performance.now();
            requestAnimationFrame(this.loop);
        }
    }

    pause() {
        this.running = false;
    }

    resume() {
        if (!this.running) {
            this.running = true;
            this.lastTime = performance.now();
            requestAnimationFrame(this.loop);
        }
    }

    loop(currentTime) {
        if (!this.running) return;

        // Calculate delta time in seconds
        this.deltaTime = (currentTime - this.lastTime) / 1000;
        this.lastTime = currentTime;

        // Cap delta time to prevent spiral of death
        if (this.deltaTime > 0.1) {
            this.deltaTime = 0.1;
        }

        // Update FPS counter
        this.frameCount++;
        if (currentTime - this.fpsUpdateTime >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.fpsUpdateTime = currentTime;
        }

        // Update and render
        this.update(this.deltaTime);
        this.render();

        // Schedule next frame
        requestAnimationFrame(this.loop);
    }

    update(dt) {
        // Move square with frame-rate independence
        this.squareX += this.squareSpeed * dt;

        // Wrap around screen
        if (this.squareX > this.canvas.width) {
            this.squareX = -50;
        }
    }

    render() {
        // Clear screen
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw square
        this.ctx.fillStyle = '#00ff00';
        this.ctx.fillRect(this.squareX, this.squareY, 50, 50);

        // Draw FPS counter
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '20px monospace';
        this.ctx.fillText(`FPS: ${this.fps}`, 10, 30);
        this.ctx.fillText(`Delta: ${(this.deltaTime * 1000).toFixed(2)}ms`, 10, 55);
    }
}

// Usage
const canvas = document.getElementById('gameCanvas');
const game = new GameLoopVariable(canvas);
game.start();

// Pause/resume example
document.addEventListener('keydown', (e) => {
    if (e.key === ' ') {
        if (game.running) {
            game.pause();
        } else {
            game.resume();
        }
    }
});
```

### Key Concepts

**Delta Time**: The time elapsed since the last frame, usually in seconds. This is used to scale movement and updates to be independent of frame rate.

**Delta Time Capping**: We cap delta time at 0.1 seconds (100ms) to prevent the "spiral of death" where a lag spike causes huge delta times, which cause the next frame to lag, creating a death spiral.

**FPS Counter**: Counts frames over one second to display current frame rate. Useful for debugging performance.

**Frame-Rate Independence**: The square moves at 200 pixels per second regardless of whether the game runs at 30 FPS or 144 FPS because we multiply speed by delta time.

## Fixed Timestep Implementation

Fixed timestep runs the update logic at a fixed rate (e.g., exactly 60 times per second) while allowing rendering to happen as fast as possible. This is preferred for deterministic physics and multiplayer games.

### Claude Code Prompt

```
Prompt: "Implement a game loop with fixed timestep at 60 updates per second.
Use an accumulator pattern to ensure consistent physics updates regardless of
frame rate. Include interpolation between physics states for smooth rendering.
Add a physics demo with gravity and bouncing ball to show deterministic behavior."
```

### Complete Implementation

```javascript
class GameLoopFixed {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Fixed timestep settings
        this.fixedTimeStep = 1 / 60; // 60 updates per second
        this.maxFrameTime = 0.25; // Max 250ms to avoid spiral of death

        // Timing
        this.lastTime = 0;
        this.accumulator = 0;
        this.fps = 0;
        this.frameCount = 0;
        this.fpsUpdateTime = 0;

        // Game state
        this.running = false;

        // Ball physics (current and previous states for interpolation)
        this.ball = {
            x: canvas.width / 2,
            y: 50,
            vx: 150,
            vy: 0,
            radius: 20,
            gravity: 980, // pixels per second squared
            bounce: 0.8
        };

        this.prevBall = { ...this.ball };

        this.loop = this.loop.bind(this);
    }

    start() {
        if (!this.running) {
            this.running = true;
            this.lastTime = performance.now() / 1000;
            requestAnimationFrame(this.loop);
        }
    }

    loop(timestamp) {
        if (!this.running) return;

        const currentTime = timestamp / 1000; // Convert to seconds
        let frameTime = currentTime - this.lastTime;

        // Cap frame time to prevent spiral of death
        if (frameTime > this.maxFrameTime) {
            frameTime = this.maxFrameTime;
        }

        this.lastTime = currentTime;
        this.accumulator += frameTime;

        // Update FPS counter
        this.frameCount++;
        if (timestamp - this.fpsUpdateTime >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.fpsUpdateTime = timestamp;
        }

        // Fixed timestep updates
        while (this.accumulator >= this.fixedTimeStep) {
            // Save previous state for interpolation
            this.prevBall = { ...this.ball };

            // Fixed update
            this.fixedUpdate(this.fixedTimeStep);

            this.accumulator -= this.fixedTimeStep;
        }

        // Calculate interpolation factor
        const alpha = this.accumulator / this.fixedTimeStep;

        // Render with interpolation
        this.render(alpha);

        requestAnimationFrame(this.loop);
    }

    fixedUpdate(dt) {
        // Apply gravity
        this.ball.vy += this.ball.gravity * dt;

        // Update position
        this.ball.x += this.ball.vx * dt;
        this.ball.y += this.ball.vy * dt;

        // Floor collision
        if (this.ball.y + this.ball.radius > this.canvas.height) {
            this.ball.y = this.canvas.height - this.ball.radius;
            this.ball.vy = -this.ball.vy * this.ball.bounce;

            // Stop bouncing if velocity is too low
            if (Math.abs(this.ball.vy) < 50) {
                this.ball.vy = 0;
            }
        }

        // Wall collisions
        if (this.ball.x - this.ball.radius < 0) {
            this.ball.x = this.ball.radius;
            this.ball.vx = -this.ball.vx * this.ball.bounce;
        } else if (this.ball.x + this.ball.radius > this.canvas.width) {
            this.ball.x = this.canvas.width - this.ball.radius;
            this.ball.vx = -this.ball.vx * this.ball.bounce;
        }

        // Ceiling collision
        if (this.ball.y - this.ball.radius < 0) {
            this.ball.y = this.ball.radius;
            this.ball.vy = -this.ball.vy * this.ball.bounce;
        }
    }

    render(alpha) {
        // Clear screen
        this.ctx.fillStyle = '#001133';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Interpolate ball position for smooth rendering
        const renderX = this.prevBall.x + (this.ball.x - this.prevBall.x) * alpha;
        const renderY = this.prevBall.y + (this.ball.y - this.prevBall.y) * alpha;

        // Draw ball
        this.ctx.fillStyle = '#ff6600';
        this.ctx.beginPath();
        this.ctx.arc(renderX, renderY, this.ball.radius, 0, Math.PI * 2);
        this.ctx.fill();

        // Draw shadow
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        this.ctx.beginPath();
        this.ctx.ellipse(
            renderX,
            this.canvas.height - 5,
            this.ball.radius * 0.8,
            this.ball.radius * 0.3,
            0, 0, Math.PI * 2
        );
        this.ctx.fill();

        // Draw info
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '16px monospace';
        this.ctx.fillText(`FPS: ${this.fps}`, 10, 25);
        this.ctx.fillText(`Fixed timestep: ${this.fixedTimeStep.toFixed(4)}s`, 10, 45);
        this.ctx.fillText(`Accumulator: ${this.accumulator.toFixed(4)}s`, 10, 65);
        this.ctx.fillText(`Interpolation: ${alpha.toFixed(4)}`, 10, 85);

        // Draw floor line
        this.ctx.strokeStyle = '#ffffff44';
        this.ctx.beginPath();
        this.ctx.moveTo(0, this.canvas.height - 1);
        this.ctx.lineTo(this.canvas.width, this.canvas.height - 1);
        this.ctx.stroke();
    }
}

// Usage
const canvas = document.getElementById('gameCanvas');
const game = new GameLoopFixed(canvas);
game.start();
```

### Key Concepts

**Accumulator**: Stores leftover time that hasn't been simulated yet. When enough time accumulates, we run a fixed update.

**Fixed Timestep**: Physics updates always happen with exactly the same time step (1/60 second), ensuring deterministic behavior.

**Interpolation**: We interpolate between the previous and current physics state when rendering to create smooth visuals even if rendering happens at different rates than physics updates.

**Determinism**: With fixed timestep, the same inputs always produce the same outputs, critical for networked games and replays.

## Semi-Fixed Timestep (Hybrid Approach)

This approach combines the best of both worlds: fixed updates for physics with variable timestep flexibility.

### Claude Code Prompt

```
Prompt: "Create a semi-fixed timestep game loop that runs physics at a fixed
rate but allows rendering at variable rates. Include performance monitoring
that shows both update rate and render rate separately. Add multiple physics
objects to demonstrate consistent simulation."
```

### Complete Implementation

```javascript
class GameLoopSemiFixed {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Timestep configuration
        this.physicsTimeStep = 1 / 60; // 60 physics updates per second
        this.maxPhysicsSteps = 5; // Prevent spiral of death

        // Timing
        this.lastTime = 0;
        this.accumulator = 0;
        this.renderFPS = 0;
        this.updateFPS = 0;
        this.renderFrameCount = 0;
        this.updateFrameCount = 0;
        this.fpsUpdateTime = 0;

        // Game state
        this.running = false;
        this.particles = this.createParticles(20);

        this.loop = this.loop.bind(this);
    }

    createParticles(count) {
        const particles = [];
        for (let i = 0; i < count; i++) {
            particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * 100,
                vx: (Math.random() - 0.5) * 200,
                vy: Math.random() * 100,
                radius: 5 + Math.random() * 10,
                color: `hsl(${Math.random() * 360}, 70%, 60%)`,
                gravity: 500,
                bounce: 0.7 + Math.random() * 0.2
            });
        }
        return particles;
    }

    start() {
        if (!this.running) {
            this.running = true;
            this.lastTime = performance.now() / 1000;
            requestAnimationFrame(this.loop);
        }
    }

    loop(timestamp) {
        if (!this.running) return;

        const currentTime = timestamp / 1000;
        let frameTime = currentTime - this.lastTime;
        this.lastTime = currentTime;

        // Update FPS counters
        this.renderFrameCount++;
        if (timestamp - this.fpsUpdateTime >= 1000) {
            this.renderFPS = this.renderFrameCount;
            this.updateFPS = this.updateFrameCount;
            this.renderFrameCount = 0;
            this.updateFrameCount = 0;
            this.fpsUpdateTime = timestamp;
        }

        // Add frame time to accumulator
        this.accumulator += frameTime;

        // Limit number of physics steps to prevent spiral of death
        let steps = 0;
        while (this.accumulator >= this.physicsTimeStep && steps < this.maxPhysicsSteps) {
            this.update(this.physicsTimeStep);
            this.accumulator -= this.physicsTimeStep;
            this.updateFrameCount++;
            steps++;
        }

        // If we hit max steps, discard remaining time
        if (steps >= this.maxPhysicsSteps) {
            this.accumulator = 0;
        }

        // Always render (variable rate)
        this.render();

        requestAnimationFrame(this.loop);
    }

    update(dt) {
        this.particles.forEach(particle => {
            // Apply gravity
            particle.vy += particle.gravity * dt;

            // Update position
            particle.x += particle.vx * dt;
            particle.y += particle.vy * dt;

            // Floor collision
            if (particle.y + particle.radius > this.canvas.height) {
                particle.y = this.canvas.height - particle.radius;
                particle.vy = -particle.vy * particle.bounce;
            }

            // Wall collisions
            if (particle.x - particle.radius < 0) {
                particle.x = particle.radius;
                particle.vx = -particle.vx * particle.bounce;
            } else if (particle.x + particle.radius > this.canvas.width) {
                particle.x = this.canvas.width - particle.radius;
                particle.vx = -particle.vx * particle.bounce;
            }

            // Ceiling collision
            if (particle.y - particle.radius < 0) {
                particle.y = particle.radius;
                particle.vy = -particle.vy * particle.bounce;
            }

            // Apply friction when on ground
            if (Math.abs(particle.y + particle.radius - this.canvas.height) < 1) {
                particle.vx *= 0.98;
            }
        });
    }

    render() {
        // Clear with trail effect
        this.ctx.fillStyle = 'rgba(10, 10, 30, 0.2)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw particles
        this.particles.forEach(particle => {
            this.ctx.fillStyle = particle.color;
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            this.ctx.fill();
        });

        // Draw info panel
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(5, 5, 250, 90);

        this.ctx.fillStyle = '#0f0';
        this.ctx.font = '14px monospace';
        this.ctx.fillText(`Render FPS: ${this.renderFPS}`, 10, 25);
        this.ctx.fillText(`Update FPS: ${this.updateFPS}`, 10, 45);
        this.ctx.fillText(`Physics step: ${(this.physicsTimeStep * 1000).toFixed(2)}ms`, 10, 65);
        this.ctx.fillText(`Particles: ${this.particles.length}`, 10, 85);
    }
}

// Usage
const canvas = document.getElementById('gameCanvas');
const game = new GameLoopSemiFixed(canvas);
game.start();

// Add particles on click
canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const particle = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        vx: (Math.random() - 0.5) * 400,
        vy: -200 - Math.random() * 200,
        radius: 8 + Math.random() * 12,
        color: `hsl(${Math.random() * 360}, 80%, 60%)`,
        gravity: 500,
        bounce: 0.7
    };
    game.particles.push(particle);
});
```

## Delta Time Calculations

Delta time is the cornerstone of frame-rate independence. Here's everything you need to know:

### Accurate Delta Time

```javascript
// High precision timing
let lastTime = performance.now();

function gameLoop(currentTime) {
    // Delta time in milliseconds
    const deltaTimeMs = currentTime - lastTime;

    // Delta time in seconds (preferred for physics)
    const deltaTimeSec = deltaTimeMs / 1000;

    lastTime = currentTime;

    // Use delta time for updates
    update(deltaTimeSec);
    render();

    requestAnimationFrame(gameLoop);
}
```

### Delta Time Smoothing

Sometimes delta time can spike, causing jerky movement. Smoothing helps:

```javascript
class DeltaTimeSmoothing {
    constructor(sampleSize = 10) {
        this.samples = [];
        this.sampleSize = sampleSize;
        this.lastTime = performance.now();
    }

    getDeltaTime(currentTime) {
        const rawDelta = (currentTime - this.lastTime) / 1000;
        this.lastTime = currentTime;

        // Add to samples
        this.samples.push(rawDelta);
        if (this.samples.length > this.sampleSize) {
            this.samples.shift();
        }

        // Return average
        return this.samples.reduce((a, b) => a + b) / this.samples.length;
    }
}

// Usage
const deltaTimer = new DeltaTimeSmoothing(10);

function gameLoop(timestamp) {
    const dt = deltaTimer.getDeltaTime(timestamp);
    update(dt);
    render();
    requestAnimationFrame(gameLoop);
}
```

## Frame-Rate Independence

The golden rule: **Never assume a specific frame rate.**

### Wrong: Frame-Rate Dependent

```javascript
// BAD: Assumes 60 FPS
function update() {
    player.x += 5; // Moves 5 pixels per frame
    // At 60 FPS: 300 pixels/second
    // At 30 FPS: 150 pixels/second (half speed!)
    // At 120 FPS: 600 pixels/second (double speed!)
}
```

### Right: Frame-Rate Independent

```javascript
// GOOD: Uses delta time
function update(dt) {
    const speed = 300; // pixels per second
    player.x += speed * dt; // Consistent across all frame rates
    // At any FPS: 300 pixels/second
}
```

### Complex Example

```javascript
class Player {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = 0;
        this.vy = 0;
        this.speed = 200; // pixels per second
        this.jumpForce = 400;
        this.gravity = 980;
        this.onGround = false;
    }

    update(dt, input) {
        // Horizontal movement (frame-rate independent)
        if (input.left) this.vx = -this.speed;
        else if (input.right) this.vx = this.speed;
        else this.vx = 0;

        // Jumping
        if (input.jump && this.onGround) {
            this.vy = -this.jumpForce;
            this.onGround = false;
        }

        // Apply gravity (frame-rate independent)
        if (!this.onGround) {
            this.vy += this.gravity * dt;
        }

        // Update position (frame-rate independent)
        this.x += this.vx * dt;
        this.y += this.vy * dt;
    }
}
```

## Performance Implications

### Benchmarking Different Approaches

```javascript
class GameLoopBenchmark {
    constructor() {
        this.results = {
            variable: [],
            fixed: [],
            semFixed: []
        };
    }

    benchmark(loopType, iterations = 1000) {
        const startTime = performance.now();
        let frames = 0;
        let lastTime = startTime;

        const loop = () => {
            const currentTime = performance.now();
            const deltaTime = (currentTime - lastTime) / 1000;
            lastTime = currentTime;

            // Simulate work
            this.simulateWork(loopType, deltaTime);

            frames++;
            if (frames < iterations) {
                requestAnimationFrame(loop);
            } else {
                const endTime = performance.now();
                const totalTime = endTime - startTime;
                const avgFrameTime = totalTime / iterations;
                const avgFPS = 1000 / avgFrameTime;

                console.log(`${loopType} Results:`);
                console.log(`  Total time: ${totalTime.toFixed(2)}ms`);
                console.log(`  Avg frame time: ${avgFrameTime.toFixed(2)}ms`);
                console.log(`  Avg FPS: ${avgFPS.toFixed(2)}`);

                this.results[loopType] = {
                    totalTime,
                    avgFrameTime,
                    avgFPS
                };
            }
        };

        requestAnimationFrame(loop);
    }

    simulateWork(loopType, deltaTime) {
        // Simulate different amounts of work
        const workLoad = loopType === 'fixed' ? 100 :
                        loopType === 'variable' ? 80 : 90;

        let sum = 0;
        for (let i = 0; i < workLoad * 1000; i++) {
            sum += Math.sqrt(i) * Math.sin(i);
        }
        return sum;
    }
}

// Run benchmarks
const benchmark = new GameLoopBenchmark();
benchmark.benchmark('variable');
// Wait, then:
// benchmark.benchmark('fixed');
// benchmark.benchmark('semFixed');
```

### Performance Tips

1. **Separate Update and Render**: Don't mix game logic with rendering
2. **Batch Operations**: Group similar operations together
3. **Early Exit**: Skip updates for off-screen objects
4. **Object Pooling**: Reuse objects instead of creating/destroying
5. **Limit Fixed Steps**: Prevent spiral of death with max iterations

## Common Timing Bugs

### Bug 1: Spiral of Death

**Problem**: A lag spike causes huge delta time, which causes more lag, creating a death spiral.

**Solution**: Cap delta time and max physics steps.

```javascript
// Cap delta time
if (deltaTime > 0.1) deltaTime = 0.1;

// Limit physics steps
let steps = 0;
while (accumulator >= timeStep && steps < 5) {
    fixedUpdate(timeStep);
    accumulator -= timeStep;
    steps++;
}
```

### Bug 2: Inconsistent Movement Speeds

**Problem**: Objects move at different speeds on different machines.

**Solution**: Always use delta time.

```javascript
// Wrong
position += speed;

// Right
position += speed * deltaTime;
```

### Bug 3: Physics Tunneling

**Problem**: Fast-moving objects pass through walls at low frame rates.

**Solution**: Use fixed timestep with smaller steps or continuous collision detection.

```javascript
// Continuous collision detection
function checkCollisionPath(from, to, obstacle) {
    // Check multiple points along the path
    const steps = 10;
    for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        const x = from.x + (to.x - from.x) * t;
        const y = from.y + (to.y - from.y) * t;

        if (collidesWith({x, y}, obstacle)) {
            return true;
        }
    }
    return false;
}
```

### Bug 4: Pause/Resume Timing Issues

**Problem**: Huge delta time when resuming from pause causes objects to jump.

**Solution**: Reset timing when resuming.

```javascript
resume() {
    this.running = true;
    this.lastTime = performance.now(); // Reset timing!
    requestAnimationFrame(this.loop);
}
```

## Integration with Game State

A complete example showing how the game loop integrates with state management:

```javascript
class Game {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Game state
        this.state = 'menu'; // menu, playing, paused, gameover
        this.score = 0;
        this.level = 1;

        // Timing
        this.running = false;
        this.lastTime = 0;
        this.deltaTime = 0;

        // Game objects
        this.player = null;
        this.enemies = [];
        this.projectiles = [];

        this.loop = this.loop.bind(this);
    }

    start() {
        this.running = true;
        this.lastTime = performance.now();
        requestAnimationFrame(this.loop);
    }

    loop(timestamp) {
        if (!this.running) return;

        this.deltaTime = (timestamp - this.lastTime) / 1000;
        this.lastTime = timestamp;

        // Cap delta time
        if (this.deltaTime > 0.1) this.deltaTime = 0.1;

        // Update based on state
        switch (this.state) {
            case 'menu':
                this.updateMenu(this.deltaTime);
                this.renderMenu();
                break;
            case 'playing':
                this.updateGame(this.deltaTime);
                this.renderGame();
                break;
            case 'paused':
                this.renderGame(); // Still render, but don't update
                this.renderPauseOverlay();
                break;
            case 'gameover':
                this.updateGameOver(this.deltaTime);
                this.renderGameOver();
                break;
        }

        requestAnimationFrame(this.loop);
    }

    updateMenu(dt) {
        // Menu animations
    }

    updateGame(dt) {
        // Update player
        if (this.player) {
            this.player.update(dt);
        }

        // Update enemies
        this.enemies.forEach(enemy => enemy.update(dt));

        // Update projectiles
        this.projectiles.forEach(proj => proj.update(dt));

        // Check collisions, etc.
    }

    updateGameOver(dt) {
        // Game over animations
    }

    renderMenu() {
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.fillStyle = '#fff';
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('GAME MENU', this.canvas.width / 2, this.canvas.height / 2);
    }

    renderGame() {
        // Clear
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Render all game objects
        if (this.player) this.player.render(this.ctx);
        this.enemies.forEach(e => e.render(this.ctx));
        this.projectiles.forEach(p => p.render(this.ctx));

        // Render UI
        this.renderUI();
    }

    renderUI() {
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '20px Arial';
        this.ctx.textAlign = 'left';
        this.ctx.fillText(`Score: ${this.score}`, 10, 30);
        this.ctx.fillText(`Level: ${this.level}`, 10, 55);
    }

    renderPauseOverlay() {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.fillStyle = '#fff';
        this.ctx.font = '36px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('PAUSED', this.canvas.width / 2, this.canvas.height / 2);
    }

    renderGameOver() {
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.fillStyle = '#f00';
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('GAME OVER', this.canvas.width / 2, this.canvas.height / 2);
        this.ctx.fillText(`Final Score: ${this.score}`, this.canvas.width / 2, this.canvas.height / 2 + 60);
    }

    setState(newState) {
        console.log(`State change: ${this.state} -> ${newState}`);
        this.state = newState;

        // Reset timing when entering playing state
        if (newState === 'playing') {
            this.lastTime = performance.now();
        }
    }
}
```

## Conclusion

Game loops are the foundation of all games. Understanding timing, delta time, and frame-rate independence will serve you throughout your game development career. The three main approaches each have their place:

- **Variable Timestep**: Simple, works for most games, good for beginners
- **Fixed Timestep**: Best for deterministic physics, multiplayer, and replays
- **Semi-Fixed**: Combines benefits of both, good for complex simulations

Use the Claude Code prompts in this guide to generate these implementations, study them, modify them, and make them your own. The key is understanding not just what the code does, but why it's structured that way.

## Next Steps

- Explore [State Management](./state-management.md) to organize your game logic
- Learn [Input Handling](./input-handling.md) to make your game loop respond to players
- Study [Physics Integration](./physics-integration.md) to see how timing affects physics

---

**Related Documentation:**
- [State Management](./state-management.md)
- [Performance Optimization](../10-performance-optimization/)
- [Testing QA](../11-testing-qa/)
