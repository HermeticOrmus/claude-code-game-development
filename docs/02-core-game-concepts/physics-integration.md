# Physics Integration

Physics simulation brings realism and weight to game movement. Whether you're building a platformer with tight jumping mechanics or a physics puzzle game with realistic object interactions, understanding physics integration is essential. This guide covers both custom physics implementations and integration of physics libraries.

## Table of Contents

1. [Physics Fundamentals](#physics-fundamentals)
2. [Basic Physics: Velocity, Acceleration, Friction](#basic-physics-velocity-acceleration-friction)
3. [Gravity and Jumping Mechanics](#gravity-and-jumping-mechanics)
4. [Integrating Physics Libraries](#integrating-physics-libraries)
5. [Custom Physics vs Library Physics](#custom-physics-vs-library-physics)
6. [Physics Timestep and Stability](#physics-timestep-and-stability)
7. [Platformer Physics Example](#platformer-physics-example)
8. [Top-Down Physics Example](#top-down-physics-example)
9. [Common Physics Bugs](#common-physics-bugs)

## Physics Fundamentals

### The Core Equation

All physics simulation starts with Newton's second law:
```
Force = Mass × Acceleration
```

From this, we derive:
```
Acceleration = Force / Mass
Velocity = Velocity + Acceleration × Time
Position = Position + Velocity × Time
```

These simple equations power everything from simple platformer movement to complex ragdoll physics.

### Units and Scale

In game physics, you need to decide on units:
- **Position**: pixels
- **Velocity**: pixels per second
- **Acceleration**: pixels per second per second
- **Mass**: arbitrary units (often just 1.0)

Consistent units are crucial. If your velocity is in pixels per second but you multiply by delta time in milliseconds, you'll get incorrect results.

## Basic Physics: Velocity, Acceleration, Friction

### Claude Code Prompt

```
Prompt: "Create a basic physics system with velocity, acceleration, and
friction. Include multiple objects with different masses, air resistance,
and ground friction. Add visualization showing velocity and acceleration
vectors, and allow toggling friction on/off to see the difference."
```

### Implementation

```javascript
class PhysicsObject {
    constructor(x, y, mass = 1) {
        // Position
        this.x = x;
        this.y = y;

        // Velocity (pixels per second)
        this.vx = 0;
        this.vy = 0;

        // Acceleration (pixels per second squared)
        this.ax = 0;
        this.ay = 0;

        // Physical properties
        this.mass = mass;
        this.friction = 0.9; // 0 = no friction, 1 = no movement
        this.airResistance = 0.99; // Applied every frame
        this.restitution = 0.7; // Bounciness (0 = no bounce, 1 = perfect bounce)

        // Visual properties
        this.radius = 20;
        this.color = '#00ff00';

        // Grounded state
        this.onGround = false;
    }

    // Apply force (F = ma, so a = F/m)
    applyForce(fx, fy) {
        this.ax += fx / this.mass;
        this.ay += fy / this.mass;
    }

    // Apply impulse (instant velocity change)
    applyImpulse(ix, iy) {
        this.vx += ix / this.mass;
        this.vy += iy / this.mass;
    }

    update(dt) {
        // Update velocity from acceleration
        this.vx += this.ax * dt;
        this.vy += this.ay * dt;

        // Apply air resistance
        this.vx *= this.airResistance;
        this.vy *= this.airResistance;

        // Apply ground friction if on ground
        if (this.onGround) {
            this.vx *= this.friction;
        }

        // Update position from velocity
        this.x += this.vx * dt;
        this.y += this.vy * dt;

        // Reset acceleration (forces are applied each frame)
        this.ax = 0;
        this.ay = 0;
    }

    render(ctx) {
        // Draw object
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fill();

        // Draw velocity vector
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x + this.vx * 0.1, this.y + this.vy * 0.1);
        ctx.stroke();

        // Draw acceleration vector
        ctx.strokeStyle = '#ffff00';
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x + this.ax * 0.5, this.y + this.ay * 0.5);
        ctx.stroke();
    }
}

class BasicPhysicsSystem {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        this.objects = [];
        this.gravity = 980; // pixels per second squared
        this.enableFriction = true;

        // Create some objects
        for (let i = 0; i < 5; i++) {
            const obj = new PhysicsObject(
                100 + i * 100,
                100,
                1 + Math.random() * 3
            );
            obj.color = `hsl(${i * 60}, 70%, 60%)`;
            obj.radius = 10 + obj.mass * 5;
            this.objects.push(obj);
        }
    }

    update(dt) {
        for (const obj of this.objects) {
            // Apply gravity
            obj.applyForce(0, obj.mass * this.gravity);

            // Update physics
            obj.update(dt);

            // Floor collision
            if (obj.y + obj.radius > this.canvas.height) {
                obj.y = this.canvas.height - obj.radius;
                obj.vy = -obj.vy * obj.restitution;
                obj.onGround = Math.abs(obj.vy) < 50;

                // Stop bouncing if velocity is too low
                if (Math.abs(obj.vy) < 10) {
                    obj.vy = 0;
                    obj.onGround = true;
                }
            } else {
                obj.onGround = false;
            }

            // Wall collisions
            if (obj.x - obj.radius < 0) {
                obj.x = obj.radius;
                obj.vx = -obj.vx * obj.restitution;
            } else if (obj.x + obj.radius > this.canvas.width) {
                obj.x = this.canvas.width - obj.radius;
                obj.vx = -obj.vx * obj.restitution;
            }

            // Apply or disable friction
            obj.friction = this.enableFriction ? 0.8 : 1.0;
        }
    }

    render() {
        // Clear
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw floor
        this.ctx.strokeStyle = '#ffffff44';
        this.ctx.beginPath();
        this.ctx.moveTo(0, this.canvas.height);
        this.ctx.lineTo(this.canvas.width, this.canvas.height);
        this.ctx.stroke();

        // Draw objects
        for (const obj of this.objects) {
            obj.render(this.ctx);
        }

        // Info
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '16px monospace';
        this.ctx.fillText(`Friction: ${this.enableFriction ? 'ON' : 'OFF'}`, 10, 20);
        this.ctx.fillText('Press F to toggle friction', 10, 40);
        this.ctx.fillText('Click to apply force', 10, 60);
    }

    handleClick(x, y) {
        // Apply upward force to nearest object
        let nearest = null;
        let nearestDist = Infinity;

        for (const obj of this.objects) {
            const dx = obj.x - x;
            const dy = obj.y - y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < nearestDist) {
                nearestDist = dist;
                nearest = obj;
            }
        }

        if (nearest) {
            nearest.applyImpulse(0, -300 * nearest.mass);
        }
    }
}
```

## Gravity and Jumping Mechanics

Jumping is deceptively complex. Good jumping mechanics make or break a platformer.

### Claude Code Prompt

```
Prompt: "Create a platformer character with variable jump height (hold jump
for higher jumps), coyote time (grace period after walking off platform),
jump buffering (pressing jump before landing), double jump, and wall jump.
Include visual debug showing jump state and available jumps."
```

### Implementation

```javascript
class PlatformerCharacter {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = 32;
        this.height = 48;

        // Physics
        this.vx = 0;
        this.vy = 0;
        this.speed = 250;
        this.jumpForce = 500;
        this.gravity = 1400;
        this.maxFallSpeed = 600;

        // Jump mechanics
        this.onGround = false;
        this.jumpPressed = false;
        this.jumpHeld = false;
        this.canJump = false;
        this.doubleJumpAvailable = true;

        // Coyote time (grace period after leaving ground)
        this.coyoteTime = 0.15; // seconds
        this.coyoteTimer = 0;

        // Jump buffering (press jump before landing)
        this.jumpBufferTime = 0.1; // seconds
        this.jumpBufferTimer = 0;

        // Variable jump height
        this.jumpReleaseGravityMultiplier = 3;

        // Wall jump
        this.onWall = false;
        this.wallDirection = 0; // -1 left, 1 right
        this.wallSlideSpeed = 100;
        this.wallJumpForce = { x: 300, y: 450 };
    }

    update(dt, input, platforms) {
        // Horizontal movement
        this.vx = 0;
        if (input.isActionDown('left')) this.vx = -this.speed;
        if (input.isActionDown('right')) this.vx = this.speed;

        // Check if on ground
        this.checkGroundCollision(platforms);

        // Coyote time (can jump shortly after leaving platform)
        if (this.onGround) {
            this.coyoteTimer = this.coyoteTime;
            this.doubleJumpAvailable = true;
        } else {
            this.coyoteTimer -= dt;
        }

        // Jump buffering
        if (input.isActionPressed('jump')) {
            this.jumpBufferTimer = this.jumpBufferTime;
        } else {
            this.jumpBufferTimer -= dt;
        }

        // Jump logic
        this.canJump = this.onGround || this.coyoteTimer > 0;

        if (this.jumpBufferTimer > 0 && this.canJump && !this.jumpPressed) {
            // Normal jump
            this.vy = -this.jumpForce;
            this.jumpPressed = true;
            this.jumpHeld = true;
            this.jumpBufferTimer = 0;
            this.coyoteTimer = 0;
        } else if (input.isActionPressed('jump') && this.doubleJumpAvailable && !this.onGround && this.coyoteTimer <= 0) {
            // Double jump
            this.vy = -this.jumpForce * 0.9;
            this.doubleJumpAvailable = false;
        } else if (this.onWall && input.isActionPressed('jump')) {
            // Wall jump
            this.vy = -this.wallJumpForce.y;
            this.vx = this.wallDirection * this.wallJumpForce.x;
            this.wallJumpTimer = 0.2; // Brief period where horizontal input is reduced
        }

        // Variable jump height (release jump early for shorter jump)
        if (!input.isActionDown('jump') && this.jumpHeld && this.vy < 0) {
            this.vy *= 0.5; // Cut upward velocity
            this.jumpHeld = false;
        }

        // Reset jump pressed state when jump button released
        if (!input.isActionDown('jump')) {
            this.jumpPressed = false;
        }

        // Apply gravity
        let gravityMultiplier = 1;

        // Fall faster if not holding jump (better feeling)
        if (this.vy > 0 && !this.jumpHeld) {
            gravityMultiplier = this.jumpReleaseGravityMultiplier;
        }

        this.vy += this.gravity * gravityMultiplier * dt;

        // Wall slide
        if (this.onWall && !this.onGround && this.vy > 0) {
            this.vy = Math.min(this.vy, this.wallSlideSpeed);
        }

        // Max fall speed
        this.vy = Math.min(this.vy, this.maxFallSpeed);

        // Update position
        this.x += this.vx * dt;
        this.y += this.vy * dt;

        // Collision resolution
        this.resolveCollisions(platforms);
    }

    checkGroundCollision(platforms) {
        this.onGround = false;
        this.onWall = false;

        for (const platform of platforms) {
            // Ground check (below player)
            if (this.vx >= 0 && // Moving down or stationary
                this.y + this.height >= platform.y &&
                this.y + this.height <= platform.y + 10 && // Small threshold
                this.x + this.width > platform.x &&
                this.x < platform.x + platform.width) {
                this.onGround = true;
                break;
            }
        }
    }

    resolveCollisions(platforms) {
        for (const platform of platforms) {
            if (this.x < platform.x + platform.width &&
                this.x + this.width > platform.x &&
                this.y < platform.y + platform.height &&
                this.y + this.height > platform.y) {

                // Calculate overlap on each axis
                const overlapX = Math.min(
                    this.x + this.width - platform.x,
                    platform.x + platform.width - this.x
                );
                const overlapY = Math.min(
                    this.y + this.height - platform.y,
                    platform.y + platform.height - this.y
                );

                // Resolve on minimum overlap axis
                if (overlapX < overlapY) {
                    // Horizontal collision (wall)
                    if (this.x < platform.x) {
                        this.x = platform.x - this.width;
                        this.wallDirection = 1;
                        this.onWall = true;
                    } else {
                        this.x = platform.x + platform.width;
                        this.wallDirection = -1;
                        this.onWall = true;
                    }
                    this.vx = 0;
                } else {
                    // Vertical collision
                    if (this.y < platform.y) {
                        // Landing on top
                        this.y = platform.y - this.height;
                        this.vy = 0;
                        this.onGround = true;
                        this.jumpHeld = false;
                    } else {
                        // Hitting head
                        this.y = platform.y + platform.height;
                        this.vy = 0;
                    }
                }
            }
        }
    }

    render(ctx) {
        // Draw character
        ctx.fillStyle = this.onGround ? '#00ff00' : '#ffaa00';
        ctx.fillRect(this.x, this.y, this.width, this.height);

        // Debug info
        ctx.fillStyle = '#fff';
        ctx.font = '10px monospace';
        ctx.fillText(`Grounded: ${this.onGround}`, this.x, this.y - 30);
        ctx.fillText(`Coyote: ${this.coyoteTimer.toFixed(2)}`, this.x, this.y - 20);
        ctx.fillText(`DoubleJump: ${this.doubleJumpAvailable}`, this.x, this.y - 10);

        // Wall indicator
        if (this.onWall) {
            ctx.fillStyle = '#ff00ff';
            if (this.wallDirection < 0) {
                ctx.fillRect(this.x - 5, this.y, 5, this.height);
            } else {
                ctx.fillRect(this.x + this.width, this.y, 5, this.height);
            }
        }
    }
}
```

## Integrating Physics Libraries

For complex physics simulations, using a library like Matter.js can save significant development time.

### Claude Code Prompt

```
Prompt: "Create a demo integrating Matter.js physics engine. Include rigid
bodies with different shapes, joints connecting bodies, mouse interaction
for dragging objects, and a chain/rope simulation. Show how to sync Matter.js
physics with canvas rendering."
```

### Implementation

```javascript
// Note: Requires Matter.js library
// <script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.19.0/matter.min.js"></script>

class MatterJSDemo {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Create Matter.js engine
        this.engine = Matter.Engine.create();
        this.world = this.engine.world;

        // Adjust gravity
        this.engine.gravity.y = 1;

        // Create ground
        const ground = Matter.Bodies.rectangle(
            canvas.width / 2,
            canvas.height - 25,
            canvas.width,
            50,
            { isStatic: true }
        );

        // Create walls
        const leftWall = Matter.Bodies.rectangle(
            25,
            canvas.height / 2,
            50,
            canvas.height,
            { isStatic: true }
        );

        const rightWall = Matter.Bodies.rectangle(
            canvas.width - 25,
            canvas.height / 2,
            50,
            canvas.height,
            { isStatic: true }
        );

        // Add static bodies
        Matter.World.add(this.world, [ground, leftWall, rightWall]);

        // Create dynamic bodies
        this.createShapes();

        // Create rope/chain
        this.createRope(200, 50, 15);

        // Mouse control
        this.mouse = Matter.Mouse.create(canvas);
        this.mouseConstraint = Matter.MouseConstraint.create(this.engine, {
            mouse: this.mouse,
            constraint: {
                stiffness: 0.2,
                render: { visible: true }
            }
        });

        Matter.World.add(this.world, this.mouseConstraint);
    }

    createShapes() {
        // Boxes
        for (let i = 0; i < 5; i++) {
            const box = Matter.Bodies.rectangle(
                100 + i * 80,
                100,
                40,
                40,
                {
                    restitution: 0.6,
                    friction: 0.1
                }
            );
            Matter.World.add(this.world, box);
        }

        // Circles
        for (let i = 0; i < 5; i++) {
            const circle = Matter.Bodies.circle(
                150 + i * 80,
                200,
                20,
                {
                    restitution: 0.8,
                    friction: 0.05
                }
            );
            Matter.World.add(this.world, circle);
        }

        // Triangle
        const triangle = Matter.Bodies.polygon(
            400,
            100,
            3,
            30,
            { restitution: 0.5 }
        );
        Matter.World.add(this.world, triangle);

        // Hexagon
        const hexagon = Matter.Bodies.polygon(
            500,
            100,
            6,
            25,
            { restitution: 0.7 }
        );
        Matter.World.add(this.world, hexagon);
    }

    createRope(x, y, segments) {
        const segmentWidth = 5;
        const segmentHeight = 20;
        const rope = Matter.Composites.stack(
            x,
            y,
            1,
            segments,
            0,
            0,
            (sx, sy) => {
                return Matter.Bodies.rectangle(
                    sx,
                    sy,
                    segmentWidth,
                    segmentHeight,
                    { friction: 0.5 }
                );
            }
        );

        // Connect segments with constraints
        Matter.Composites.chain(rope, 0, 0, 0, 0, {
            stiffness: 0.9,
            length: 0
        });

        // Pin first segment
        Matter.Composite.add(
            rope,
            Matter.Constraint.create({
                bodyB: rope.bodies[0],
                pointB: { x: 0, y: -segmentHeight / 2 },
                pointA: { x: x, y: y },
                stiffness: 1,
                length: 0
            })
        );

        // Add ball at end
        const ball = Matter.Bodies.circle(
            x,
            y + segments * segmentHeight,
            15,
            { density: 0.1 }
        );

        Matter.Composite.add(rope, ball);

        Matter.Composite.add(
            rope,
            Matter.Constraint.create({
                bodyA: rope.bodies[rope.bodies.length - 2],
                bodyB: ball,
                length: 0,
                stiffness: 0.9
            })
        );

        Matter.World.add(this.world, rope);
    }

    update(dt) {
        // Update Matter.js physics
        // Matter.js uses fixed timestep internally
        Matter.Engine.update(this.engine, dt * 1000);
    }

    render() {
        const ctx = this.ctx;

        // Clear
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Render all bodies
        const bodies = Matter.Composite.allBodies(this.world);

        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;

        bodies.forEach(body => {
            const vertices = body.vertices;

            // Determine color based on properties
            if (body.isStatic) {
                ctx.fillStyle = '#333';
            } else {
                ctx.fillStyle = '#0f6';
            }

            ctx.beginPath();
            ctx.moveTo(vertices[0].x, vertices[0].y);

            for (let i = 1; i < vertices.length; i++) {
                ctx.lineTo(vertices[i].x, vertices[i].y);
            }

            ctx.closePath();
            ctx.fill();
            ctx.stroke();
        });

        // Render constraints (ropes, chains)
        const constraints = Matter.Composite.allConstraints(this.world);

        ctx.strokeStyle = '#ff6b6b';
        ctx.lineWidth = 2;

        constraints.forEach(constraint => {
            if (!constraint.pointA || !constraint.pointB) return;

            const posA = constraint.bodyA
                ? Matter.Vector.add(constraint.bodyA.position, constraint.pointA)
                : constraint.pointA;

            const posB = constraint.bodyB
                ? Matter.Vector.add(constraint.bodyB.position, constraint.pointB)
                : constraint.pointB;

            ctx.beginPath();
            ctx.moveTo(posA.x, posA.y);
            ctx.lineTo(posB.x, posB.y);
            ctx.stroke();
        });

        // Info
        ctx.fillStyle = '#fff';
        ctx.font = '14px monospace';
        ctx.fillText(`Bodies: ${bodies.length}`, 10, 20);
        ctx.fillText('Click and drag objects', 10, 40);
    }
}
```

## Custom Physics vs Library Physics

### When to Use Custom Physics

**Pros:**
- Full control over behavior
- Lighter weight (no library overhead)
- Easier to tweak for specific game feel
- Better for simple 2D games

**Cons:**
- More development time
- Need to implement everything yourself
- May have bugs or edge cases
- Limited to what you implement

**Best For:**
- Platformers with specific jump feel
- Top-down games with simple physics
- Games where "feel" is more important than realism

### When to Use Physics Libraries

**Pros:**
- Battle-tested, robust implementations
- Complex features (joints, constraints, etc.)
- Handles edge cases you might miss
- Great documentation and examples

**Cons:**
- Learning curve
- Additional dependency
- May be overkill for simple games
- Harder to customize behavior

**Best For:**
- Physics puzzle games
- Games requiring realistic physics
- Games with complex interactions (ragdolls, destruction)
- Prototyping complex mechanics

## Physics Timestep and Stability

Physics simulation stability depends heavily on timestep.

### Fixed Timestep for Physics

```javascript
class StablePhysicsLoop {
    constructor() {
        this.physicsTimeStep = 1 / 60; // 60 physics updates per second
        this.accumulator = 0;
        this.maxPhysicsSteps = 5;
    }

    update(dt, physicsSystem) {
        this.accumulator += dt;

        let steps = 0;
        while (this.accumulator >= this.physicsTimeStep && steps < this.maxPhysicsSteps) {
            physicsSystem.fixedUpdate(this.physicsTimeStep);
            this.accumulator -= this.physicsTimeStep;
            steps++;
        }

        // Discard excess time to prevent spiral of death
        if (steps >= this.maxPhysicsSteps) {
            this.accumulator = 0;
        }
    }
}
```

## Platformer Physics Example

Complete platformer physics implementation is shown in the "Gravity and Jumping Mechanics" section above.

## Top-Down Physics Example

### Claude Code Prompt

```
Prompt: "Create a top-down physics system for a racing or space game. Include
acceleration, steering, drifting, and momentum. Add obstacles that objects
bounce off, and visual indicators for velocity and heading."
```

### Implementation

```javascript
class TopDownVehicle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.width = 40;
        this.height = 60;

        // Physics
        this.vx = 0;
        this.vy = 0;
        this.angle = 0; // radians
        this.angularVelocity = 0;

        // Movement properties
        this.acceleration = 400;
        this.maxSpeed = 300;
        this.turnSpeed = 3; // radians per second
        this.drag = 0.95;
        this.driftFactor = 0.9;
    }

    update(dt, input) {
        // Acceleration/braking
        let thrust = 0;
        if (input.isActionDown('up')) thrust = this.acceleration;
        if (input.isActionDown('down')) thrust = -this.acceleration * 0.5;

        // Turning
        let turn = 0;
        if (input.isActionDown('left')) turn = -this.turnSpeed;
        if (input.isActionDown('right')) turn = this.turnSpeed;

        // Apply turning (more effective at higher speeds)
        const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
        const turnEffectiveness = Math.min(speed / this.maxSpeed, 1);
        this.angle += turn * turnEffectiveness * dt;

        // Calculate forward direction
        const forwardX = Math.cos(this.angle);
        const forwardY = Math.sin(this.angle);

        // Apply thrust
        if (thrust !== 0) {
            this.vx += forwardX * thrust * dt;
            this.vy += forwardY * thrust * dt;
        }

        // Apply drag
        this.vx *= this.drag;
        this.vy *= this.drag;

        // Drift (reduce perpendicular velocity for arcade feel)
        const dot = this.vx * forwardX + this.vy * forwardY;
        const projX = forwardX * dot;
        const projY = forwardY * dot;
        const perpX = this.vx - projX;
        const perpY = this.vy - projY;

        this.vx = projX + perpX * this.driftFactor;
        this.vy = projY + perpY * this.driftFactor;

        // Cap speed
        const currentSpeed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
        if (currentSpeed > this.maxSpeed) {
            this.vx = (this.vx / currentSpeed) * this.maxSpeed;
            this.vy = (this.vy / currentSpeed) * this.maxSpeed;
        }

        // Update position
        this.x += this.vx * dt;
        this.y += this.vy * dt;
    }

    render(ctx) {
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.rotate(this.angle);

        // Draw vehicle
        ctx.fillStyle = '#00ff00';
        ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);

        // Draw direction indicator
        ctx.fillStyle = '#ff0000';
        ctx.fillRect(this.width / 2 - 10, -5, 15, 10);

        ctx.restore();

        // Draw velocity vector
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.lineTo(this.x + this.vx * 0.2, this.y + this.vy * 0.2);
        ctx.stroke();
    }
}
```

## Common Physics Bugs

### Bug 1: Tunneling (Fast objects pass through walls)

**Problem**: Objects move so fast they skip over obstacles.

**Solution**: Use continuous collision detection or limit max velocities.

### Bug 2: Jittering at Rest

**Problem**: Objects vibrate when they should be still.

**Solution**: Use sleep states or velocity thresholds.

```javascript
if (Math.abs(this.vx) < 0.1 && this.onGround) {
    this.vx = 0;
}
```

### Bug 3: Floating Point Accumulation

**Problem**: Small errors accumulate over time.

**Solution**: Reset values that should be exact (like setting vy = 0 when on ground).

### Bug 4: Inconsistent Behavior at Different Frame Rates

**Problem**: Physics behaves differently at 30 FPS vs 60 FPS.

**Solution**: Use delta time correctly and consider fixed timestep.

### Bug 5: Energy Gain from Collision Response

**Problem**: Objects gain speed when colliding.

**Solution**: Ensure collision response applies damping or uses restitution < 1.

## Conclusion

Physics integration can range from simple velocity and gravity to complex simulations with joints and constraints. Start simple with custom physics for basic games, and consider libraries like Matter.js when you need more complex interactions. Always use delta time for frame-rate independence and consider fixed timestep for stability.

---

**Related Documentation:**
- [Collision Detection](./collision-detection.md)
- [Game Loops and Timing](./game-loops-and-timing.md)
- [Advanced Patterns](../09-advanced-patterns/)
