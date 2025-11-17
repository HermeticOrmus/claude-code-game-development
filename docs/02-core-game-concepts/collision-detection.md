# Collision Detection

Collision detection is the process of determining when game objects intersect or touch each other. It's fundamental to almost every game genre, from platformers to shooters to puzzle games. This guide covers multiple collision detection algorithms, optimization techniques, and practical implementations.

## Table of Contents

1. [Why Collision Detection Matters](#why-collision-detection-matters)
2. [Axis-Aligned Bounding Box (AABB)](#axis-aligned-bounding-box-aabb)
3. [Circle Collision Detection](#circle-collision-detection)
4. [Oriented Bounding Box (OBB)](#oriented-bounding-box-obb)
5. [Separating Axis Theorem (SAT)](#separating-axis-theorem-sat)
6. [Pixel-Perfect Collision](#pixel-perfect-collision)
7. [Continuous Collision Detection](#continuous-collision-detection)
8. [Spatial Partitioning](#spatial-partitioning)
9. [Performance Comparisons](#performance-comparisons)
10. [When to Use Which Technique](#when-to-use-which-technique)

## Why Collision Detection Matters

### Gameplay Foundation

Collision detection enables core gameplay mechanics:
- Player colliding with platforms in platformers
- Bullets hitting enemies in shooters
- Collecting power-ups and coins
- Detecting game overs (player hitting obstacles)
- Trigger zones for events and cutscenes

### Performance Critical

Collision detection can be one of the most expensive operations in a game. With hundreds or thousands of objects, naive collision detection (checking every object against every other object) becomes prohibitively expensive. Understanding efficient algorithms is essential.

### Accuracy vs Performance

Different games need different levels of accuracy. A bullet hell shooter might need pixel-perfect collision for the player but simple circle collision for bullets. A platformer might use AABB collision for most objects but need more precise detection for specific mechanics.

## Axis-Aligned Bounding Box (AABB)

AABB is the simplest and fastest collision detection algorithm. It checks if two axis-aligned rectangles overlap.

### Claude Code Prompt

```
Prompt: "Create a comprehensive AABB collision detection system with collision
response (pushing objects apart), edge detection (which side collided), and
a complete demo with multiple moving rectangles. Include debug visualization
showing bounding boxes and collision normals."
```

### Implementation

```javascript
class AABBCollision {
    // Basic AABB collision check
    static checkCollision(rect1, rect2) {
        return rect1.x < rect2.x + rect2.width &&
               rect1.x + rect1.width > rect2.x &&
               rect1.y < rect2.y + rect2.height &&
               rect1.y + rect1.height > rect2.y;
    }

    // AABB collision with detailed info (overlap amount, collision normal)
    static getCollisionInfo(rect1, rect2) {
        if (!this.checkCollision(rect1, rect2)) {
            return null;
        }

        // Calculate overlap on each axis
        const overlapX = Math.min(
            rect1.x + rect1.width - rect2.x,
            rect2.x + rect2.width - rect1.x
        );

        const overlapY = Math.min(
            rect1.y + rect1.height - rect2.y,
            rect2.y + rect2.height - rect1.y
        );

        // Determine collision side (minimum overlap axis)
        let normal = { x: 0, y: 0 };
        let penetration = 0;

        if (overlapX < overlapY) {
            // Collision on X axis
            penetration = overlapX;
            normal.x = (rect1.x + rect1.width / 2) < (rect2.x + rect2.width / 2) ? -1 : 1;
        } else {
            // Collision on Y axis
            penetration = overlapY;
            normal.y = (rect1.y + rect1.height / 2) < (rect2.y + rect2.height / 2) ? -1 : 1;
        }

        return {
            colliding: true,
            normal,
            penetration,
            overlapX,
            overlapY
        };
    }

    // Resolve collision by pushing objects apart
    static resolveCollision(dynamic, static, info) {
        if (!info) return;

        // Push dynamic object out of static object
        dynamic.x += info.normal.x * info.penetration;
        dynamic.y += info.normal.y * info.penetration;
    }

    // Sweep test - predict collision during movement
    static sweepAABB(moving, static, velocityX, velocityY) {
        // Minkowski difference
        const broadphase = {
            x: static.x - moving.width,
            y: static.y - moving.height,
            width: static.width + moving.width,
            height: static.height + moving.height
        };

        // Ray from moving object's position in direction of velocity
        const ray = {
            x: moving.x + moving.width / 2,
            y: moving.y + moving.height / 2,
            dx: velocityX,
            dy: velocityY
        };

        // Check if ray intersects broadphase box
        const hit = this.raycastAABB(ray, broadphase);

        if (hit && hit.time >= 0 && hit.time <= 1) {
            return {
                colliding: true,
                time: hit.time,
                normal: hit.normal,
                position: {
                    x: moving.x + velocityX * hit.time,
                    y: moving.y + velocityY * hit.time
                }
            };
        }

        return null;
    }

    // Raycast against AABB
    static raycastAABB(ray, box) {
        const dx = ray.dx;
        const dy = ray.dy;

        // Calculate intersection distances
        let tmin = (box.x - ray.x) / dx;
        let tmax = (box.x + box.width - ray.x) / dx;

        if (tmin > tmax) [tmin, tmax] = [tmax, tmin];

        let tymin = (box.y - ray.y) / dy;
        let tymax = (box.y + box.height - ray.y) / dy;

        if (tymin > tymax) [tymin, tymax] = [tymax, tymin];

        if (tmin > tymax || tymin > tmax) {
            return null;
        }

        const tenter = Math.max(tmin, tymin);
        const texit = Math.min(tmax, tymax);

        if (texit < 0) {
            return null;
        }

        // Determine collision normal
        let normal = { x: 0, y: 0 };
        if (tmin > tymin) {
            normal.x = dx > 0 ? -1 : 1;
        } else {
            normal.y = dy > 0 ? -1 : 1;
        }

        return {
            time: tenter,
            normal
        };
    }
}

// Demo: AABB Collision System
class AABBDemo {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Create some objects
        this.player = {
            x: 100,
            y: 100,
            width: 40,
            height: 40,
            vx: 0,
            vy: 0,
            speed: 200,
            color: '#00ff00'
        };

        this.obstacles = [
            { x: 200, y: 150, width: 100, height: 20, color: '#ff0000' },
            { x: 350, y: 250, width: 80, height: 80, color: '#ff0000' },
            { x: 100, y: 300, width: 200, height: 30, color: '#ff0000' },
            { x: 500, y: 100, width: 50, height: 200, color: '#ff0000' }
        ];

        this.collisionInfo = [];
    }

    update(dt, input) {
        // Get input
        this.player.vx = 0;
        this.player.vy = 0;

        if (input.isActionDown('up')) this.player.vy = -this.player.speed;
        if (input.isActionDown('down')) this.player.vy = this.player.speed;
        if (input.isActionDown('left')) this.player.vx = -this.player.speed;
        if (input.isActionDown('right')) this.player.vx = this.player.speed;

        // Move player
        this.player.x += this.player.vx * dt;
        this.player.y += this.player.vy * dt;

        // Check collisions and resolve
        this.collisionInfo = [];

        for (const obstacle of this.obstacles) {
            const info = AABBCollision.getCollisionInfo(this.player, obstacle);

            if (info) {
                this.collisionInfo.push({
                    obstacle,
                    info
                });

                AABBCollision.resolveCollision(this.player, obstacle, info);
            }
        }

        // Keep player in bounds
        this.player.x = Math.max(0, Math.min(this.canvas.width - this.player.width, this.player.x));
        this.player.y = Math.max(0, Math.min(this.canvas.height - this.player.height, this.player.y));
    }

    render() {
        // Clear
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw obstacles
        for (const obstacle of this.obstacles) {
            this.ctx.fillStyle = obstacle.color;
            this.ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);

            // Bounding box
            this.ctx.strokeStyle = '#ffffff44';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
        }

        // Draw player
        this.ctx.fillStyle = this.player.color;
        this.ctx.fillRect(this.player.x, this.player.y, this.player.width, this.player.height);

        // Draw collision normals
        for (const { obstacle, info } of this.collisionInfo) {
            const centerX = this.player.x + this.player.width / 2;
            const centerY = this.player.y + this.player.height / 2;

            this.ctx.strokeStyle = '#ffff00';
            this.ctx.lineWidth = 3;
            this.ctx.beginPath();
            this.ctx.moveTo(centerX, centerY);
            this.ctx.lineTo(
                centerX + info.normal.x * 50,
                centerY + info.normal.y * 50
            );
            this.ctx.stroke();
        }

        // Info
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '16px monospace';
        this.ctx.fillText(`Collisions: ${this.collisionInfo.length}`, 10, 20);
        this.ctx.fillText('WASD to move', 10, 40);
    }
}
```

### AABB Performance

**Time Complexity**: O(1) per collision check
**Best For**: Rectangles, tiles, simple shapes
**Limitations**: Cannot handle rotation

## Circle Collision Detection

Circle collision is nearly as fast as AABB and works well for round objects.

### Claude Code Prompt

```
Prompt: "Create a circle collision detection system with elastic collision
response (objects bounce off each other realistically). Include multiple
moving circles with different sizes and masses, momentum conservation, and
visual debug showing collision circles and velocity vectors."
```

### Implementation

```javascript
class CircleCollision {
    // Check if two circles collide
    static checkCollision(circle1, circle2) {
        const dx = circle2.x - circle1.x;
        const dy = circle2.y - circle1.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const minDistance = circle1.radius + circle2.radius;

        return distance < minDistance;
    }

    // Get collision info
    static getCollisionInfo(circle1, circle2) {
        const dx = circle2.x - circle1.x;
        const dy = circle2.y - circle1.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const minDistance = circle1.radius + circle2.radius;

        if (distance >= minDistance) {
            return null;
        }

        const penetration = minDistance - distance;
        const normal = {
            x: dx / distance,
            y: dy / distance
        };

        return {
            colliding: true,
            penetration,
            normal,
            distance
        };
    }

    // Resolve collision with elastic response
    static resolveElasticCollision(circle1, circle2, info, restitution = 0.8) {
        if (!info) return;

        // Separate circles
        const totalMass = circle1.mass + circle2.mass;
        const ratio1 = circle2.mass / totalMass;
        const ratio2 = circle1.mass / totalMass;

        circle1.x -= info.normal.x * info.penetration * ratio1;
        circle1.y -= info.normal.y * info.penetration * ratio1;
        circle2.x += info.normal.x * info.penetration * ratio2;
        circle2.y += info.normal.y * info.penetration * ratio2;

        // Calculate relative velocity
        const relativeVelocity = {
            x: circle2.vx - circle1.vx,
            y: circle2.vy - circle1.vy
        };

        // Velocity along collision normal
        const velocityAlongNormal =
            relativeVelocity.x * info.normal.x +
            relativeVelocity.y * info.normal.y;

        // Don't resolve if circles are separating
        if (velocityAlongNormal > 0) return;

        // Calculate impulse
        const impulse = -(1 + restitution) * velocityAlongNormal / totalMass;

        // Apply impulse
        circle1.vx -= impulse * circle2.mass * info.normal.x;
        circle1.vy -= impulse * circle2.mass * info.normal.y;
        circle2.vx += impulse * circle1.mass * info.normal.x;
        circle2.vy += impulse * circle1.mass * info.normal.y;
    }

    // Continuous collision detection for circles
    static sweepCircle(moving, static, dt) {
        // Relative velocity
        const vx = moving.vx - (static.vx || 0);
        const vy = moving.vy - (static.vy || 0);

        // Relative position
        const dx = static.x - moving.x;
        const dy = static.y - moving.y;

        // Quadratic equation coefficients
        const a = vx * vx + vy * vy;
        const b = -2 * (dx * vx + dy * vy);
        const c = dx * dx + dy * dy - Math.pow(moving.radius + static.radius, 2);

        // Solve quadratic
        const discriminant = b * b - 4 * a * c;

        if (discriminant < 0) {
            return null; // No collision
        }

        const t1 = (-b - Math.sqrt(discriminant)) / (2 * a);
        const t2 = (-b + Math.sqrt(discriminant)) / (2 * a);

        // Get first collision time within this timestep
        const t = Math.min(t1, t2);

        if (t >= 0 && t <= dt) {
            // Calculate collision point
            const collisionX = moving.x + moving.vx * t;
            const collisionY = moving.y + moving.vy * t;

            // Calculate normal
            const nx = (collisionX - static.x);
            const ny = (collisionY - static.y);
            const length = Math.sqrt(nx * nx + ny * ny);

            return {
                time: t,
                position: { x: collisionX, y: collisionY },
                normal: { x: nx / length, y: ny / length }
            };
        }

        return null;
    }
}

// Demo: Circle Collision System
class CircleDemo {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Create circles
        this.circles = [];

        for (let i = 0; i < 15; i++) {
            this.circles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 200,
                vy: (Math.random() - 0.5) * 200,
                radius: 15 + Math.random() * 25,
                mass: 1,
                color: `hsl(${Math.random() * 360}, 70%, 60%)`
            });
        }

        // Set mass based on radius
        this.circles.forEach(circle => {
            circle.mass = Math.PI * circle.radius * circle.radius;
        });
    }

    update(dt) {
        // Update positions
        this.circles.forEach(circle => {
            circle.x += circle.vx * dt;
            circle.y += circle.vy * dt;

            // Bounce off walls
            if (circle.x - circle.radius < 0) {
                circle.x = circle.radius;
                circle.vx = Math.abs(circle.vx) * 0.8;
            } else if (circle.x + circle.radius > this.canvas.width) {
                circle.x = this.canvas.width - circle.radius;
                circle.vx = -Math.abs(circle.vx) * 0.8;
            }

            if (circle.y - circle.radius < 0) {
                circle.y = circle.radius;
                circle.vy = Math.abs(circle.vy) * 0.8;
            } else if (circle.y + circle.radius > this.canvas.height) {
                circle.y = this.canvas.height - circle.radius;
                circle.vy = -Math.abs(circle.vy) * 0.8;
            }

            // Apply friction
            circle.vx *= 0.995;
            circle.vy *= 0.995;
        });

        // Check collisions between circles
        for (let i = 0; i < this.circles.length; i++) {
            for (let j = i + 1; j < this.circles.length; j++) {
                const info = CircleCollision.getCollisionInfo(
                    this.circles[i],
                    this.circles[j]
                );

                if (info) {
                    CircleCollision.resolveElasticCollision(
                        this.circles[i],
                        this.circles[j],
                        info,
                        0.9
                    );
                }
            }
        }
    }

    render() {
        // Clear
        this.ctx.fillStyle = 'rgba(10, 10, 30, 0.3)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw circles
        this.circles.forEach(circle => {
            this.ctx.fillStyle = circle.color;
            this.ctx.beginPath();
            this.ctx.arc(circle.x, circle.y, circle.radius, 0, Math.PI * 2);
            this.ctx.fill();

            // Debug: velocity vector
            this.ctx.strokeStyle = '#ffffff88';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.moveTo(circle.x, circle.y);
            this.ctx.lineTo(
                circle.x + circle.vx * 0.1,
                circle.y + circle.vy * 0.1
            );
            this.ctx.stroke();
        });

        // Info
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '14px monospace';
        this.ctx.fillText(`Circles: ${this.circles.length}`, 10, 20);
    }
}
```

### Circle Collision Performance

**Time Complexity**: O(1) per collision check
**Best For**: Balls, circular objects, approximate collision for many shapes
**Advantages**: Very fast, works from any angle

## Oriented Bounding Box (OBB)

OBB extends AABB to handle rotated rectangles.

### Claude Code Prompt

```
Prompt: "Create an OBB collision detection system using the Separating Axis
Theorem. Include rotating rectangles, collision response with rotation,
and debug visualization showing all axes and projections."
```

### Implementation

```javascript
class OBBCollision {
    // Create OBB from rectangle with rotation
    static createOBB(x, y, width, height, rotation) {
        const halfWidth = width / 2;
        const halfHeight = height / 2;
        const cos = Math.cos(rotation);
        const sin = Math.sin(rotation);

        return {
            center: { x: x + halfWidth, y: y + halfHeight },
            halfExtents: { x: halfWidth, y: halfHeight },
            rotation,
            axes: [
                { x: cos, y: sin },
                { x: -sin, y: cos }
            ],
            vertices: [
                {
                    x: x + halfWidth + (-halfWidth * cos - -halfHeight * sin),
                    y: y + halfHeight + (-halfWidth * sin + -halfHeight * cos)
                },
                {
                    x: x + halfWidth + (halfWidth * cos - -halfHeight * sin),
                    y: y + halfHeight + (halfWidth * sin + -halfHeight * cos)
                },
                {
                    x: x + halfWidth + (halfWidth * cos - halfHeight * sin),
                    y: y + halfHeight + (halfWidth * sin + halfHeight * cos)
                },
                {
                    x: x + halfWidth + (-halfWidth * cos - halfHeight * sin),
                    y: y + halfHeight + (-halfWidth * sin + halfHeight * cos)
                }
            ]
        };
    }

    // Project OBB onto axis
    static projectOBB(obb, axis) {
        let min = Infinity;
        let max = -Infinity;

        for (const vertex of obb.vertices) {
            const projection = vertex.x * axis.x + vertex.y * axis.y;
            min = Math.min(min, projection);
            max = Math.max(max, projection);
        }

        return { min, max };
    }

    // Check if projections overlap
    static projectionsOverlap(proj1, proj2) {
        return !(proj1.max < proj2.min || proj2.max < proj1.min);
    }

    // Get overlap amount
    static getOverlap(proj1, proj2) {
        return Math.min(proj1.max, proj2.max) - Math.max(proj1.min, proj2.min);
    }

    // SAT collision detection for OBB
    static checkCollision(obb1, obb2) {
        const axes = [...obb1.axes, ...obb2.axes];
        let minOverlap = Infinity;
        let minAxis = null;

        for (const axis of axes) {
            const proj1 = this.projectOBB(obb1, axis);
            const proj2 = this.projectOBB(obb2, axis);

            if (!this.projectionsOverlap(proj1, proj2)) {
                return null; // Separating axis found
            }

            const overlap = this.getOverlap(proj1, proj2);
            if (overlap < minOverlap) {
                minOverlap = overlap;
                minAxis = axis;
            }
        }

        // Ensure normal points from obb1 to obb2
        const dx = obb2.center.x - obb1.center.x;
        const dy = obb2.center.y - obb1.center.y;
        const dot = dx * minAxis.x + dy * minAxis.y;

        if (dot < 0) {
            minAxis = { x: -minAxis.x, y: -minAxis.y };
        }

        return {
            colliding: true,
            normal: minAxis,
            penetration: minOverlap
        };
    }
}
```

## Separating Axis Theorem (SAT)

SAT is a general-purpose algorithm for detecting collisions between convex polygons.

### Claude Code Prompt

```
Prompt: "Implement the Separating Axis Theorem for arbitrary convex polygons.
Create a demo with triangles, pentagons, and hexagons colliding. Include
visualization of all separating axes, projections, and MTV (Minimum Translation
Vector) for collision resolution."
```

### Implementation

```javascript
class SATCollision {
    // Get axes (normals) for a polygon
    static getAxes(vertices) {
        const axes = [];

        for (let i = 0; i < vertices.length; i++) {
            const v1 = vertices[i];
            const v2 = vertices[(i + 1) % vertices.length];

            const edge = {
                x: v2.x - v1.x,
                y: v2.y - v1.y
            };

            // Get perpendicular (normal)
            const length = Math.sqrt(edge.x * edge.x + edge.y * edge.y);
            axes.push({
                x: -edge.y / length,
                y: edge.x / length
            });
        }

        return axes;
    }

    // Project polygon onto axis
    static projectPolygon(vertices, axis) {
        let min = Infinity;
        let max = -Infinity;

        for (const vertex of vertices) {
            const projection = vertex.x * axis.x + vertex.y * axis.y;
            min = Math.min(min, projection);
            max = Math.max(max, projection);
        }

        return { min, max };
    }

    // SAT collision detection
    static checkCollision(vertices1, vertices2) {
        const axes1 = this.getAxes(vertices1);
        const axes2 = this.getAxes(vertices2);
        const allAxes = [...axes1, ...axes2];

        let minOverlap = Infinity;
        let minAxis = null;

        for (const axis of allAxes) {
            const proj1 = this.projectPolygon(vertices1, axis);
            const proj2 = this.projectPolygon(vertices2, axis);

            // Check for separation
            if (proj1.max < proj2.min || proj2.max < proj1.min) {
                return null; // Separating axis found - no collision
            }

            // Calculate overlap
            const overlap = Math.min(proj1.max, proj2.max) -
                          Math.max(proj1.min, proj2.min);

            if (overlap < minOverlap) {
                minOverlap = overlap;
                minAxis = axis;
            }
        }

        // Calculate polygon centers
        const center1 = this.getCenter(vertices1);
        const center2 = this.getCenter(vertices2);

        // Ensure normal points from poly1 to poly2
        const dx = center2.x - center1.x;
        const dy = center2.y - center1.y;
        const dot = dx * minAxis.x + dy * minAxis.y;

        if (dot < 0) {
            minAxis = { x: -minAxis.x, y: -minAxis.y };
        }

        return {
            colliding: true,
            normal: minAxis,
            penetration: minOverlap
        };
    }

    static getCenter(vertices) {
        let x = 0, y = 0;
        for (const v of vertices) {
            x += v.x;
            y += v.y;
        }
        return {
            x: x / vertices.length,
            y: y / vertices.length
        };
    }

    // Create regular polygon vertices
    static createPolygon(x, y, sides, radius, rotation = 0) {
        const vertices = [];
        for (let i = 0; i < sides; i++) {
            const angle = (i / sides) * Math.PI * 2 + rotation;
            vertices.push({
                x: x + Math.cos(angle) * radius,
                y: y + Math.sin(angle) * radius
            });
        }
        return vertices;
    }
}
```

## Pixel-Perfect Collision

Pixel-perfect collision checks actual pixel data for the most accurate collision detection.

### Claude Code Prompt

```
Prompt: "Create a pixel-perfect collision detection system using canvas pixel
data. Include sprite masking, alpha threshold detection, and optimization with
bounding box pre-checks. Add a demo with complex sprite shapes."
```

### Implementation

```javascript
class PixelPerfectCollision {
    constructor() {
        this.maskCache = new Map();
    }

    // Create collision mask from image
    createMask(image, alphaThreshold = 128) {
        const canvas = document.createElement('canvas');
        canvas.width = image.width;
        canvas.height = image.height;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(image, 0, 0);

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const mask = [];

        for (let y = 0; y < canvas.height; y++) {
            mask[y] = [];
            for (let x = 0; x < canvas.width; x++) {
                const index = (y * canvas.width + x) * 4;
                const alpha = imageData.data[index + 3];
                mask[y][x] = alpha >= alphaThreshold ? 1 : 0;
            }
        }

        return mask;
    }

    // Check pixel-perfect collision
    checkCollision(sprite1, sprite2, alphaThreshold = 128) {
        // First, do AABB check (fast rejection)
        if (!AABBCollision.checkCollision(
            { x: sprite1.x, y: sprite1.y, width: sprite1.width, height: sprite1.height },
            { x: sprite2.x, y: sprite2.y, width: sprite2.width, height: sprite2.height }
        )) {
            return false;
        }

        // Get or create masks
        let mask1 = this.maskCache.get(sprite1.image);
        if (!mask1) {
            mask1 = this.createMask(sprite1.image, alphaThreshold);
            this.maskCache.set(sprite1.image, mask1);
        }

        let mask2 = this.maskCache.get(sprite2.image);
        if (!mask2) {
            mask2 = this.createMask(sprite2.image, alphaThreshold);
            this.maskCache.set(sprite2.image, mask2);
        }

        // Calculate overlap region
        const overlapX1 = Math.max(sprite1.x, sprite2.x);
        const overlapY1 = Math.max(sprite1.y, sprite2.y);
        const overlapX2 = Math.min(sprite1.x + sprite1.width, sprite2.x + sprite2.width);
        const overlapY2 = Math.min(sprite1.y + sprite1.height, sprite2.y + sprite2.height);

        // Check pixels in overlap region
        for (let y = overlapY1; y < overlapY2; y++) {
            for (let x = overlapX1; x < overlapX2; x++) {
                // Convert to sprite-local coordinates
                const x1 = Math.floor(x - sprite1.x);
                const y1 = Math.floor(y - sprite1.y);
                const x2 = Math.floor(x - sprite2.x);
                const y2 = Math.floor(y - sprite2.y);

                // Check if both sprites have solid pixels at this position
                if (mask1[y1] && mask1[y1][x1] &&
                    mask2[y2] && mask2[y2][x2]) {
                    return true;
                }
            }
        }

        return false;
    }
}
```

## Continuous Collision Detection

Continuous collision detection prevents fast-moving objects from passing through obstacles (tunneling).

### Implementation

```javascript
class ContinuousCollision {
    // Sweep AABB against static AABB
    static sweepAABB(moving, static, vx, vy) {
        // Entry and exit times
        let xInvEntry, yInvEntry;
        let xInvExit, yInvExit;

        // Calculate distances
        if (vx > 0) {
            xInvEntry = static.x - (moving.x + moving.width);
            xInvExit = (static.x + static.width) - moving.x;
        } else {
            xInvEntry = (static.x + static.width) - moving.x;
            xInvExit = static.x - (moving.x + moving.width);
        }

        if (vy > 0) {
            yInvEntry = static.y - (moving.y + moving.height);
            yInvExit = (static.y + static.height) - moving.y;
        } else {
            yInvEntry = (static.y + static.height) - moving.y;
            yInvExit = static.y - (moving.y + moving.height);
        }

        // Find time of collision
        let xEntry, yEntry;
        let xExit, yExit;

        if (vx === 0) {
            xEntry = -Infinity;
            xExit = Infinity;
        } else {
            xEntry = xInvEntry / vx;
            xExit = xInvExit / vx;
        }

        if (vy === 0) {
            yEntry = -Infinity;
            yExit = Infinity;
        } else {
            yEntry = yInvEntry / vy;
            yExit = yInvExit / vy;
        }

        const entryTime = Math.max(xEntry, yEntry);
        const exitTime = Math.min(xExit, yExit);

        // No collision
        if (entryTime > exitTime ||
            (xEntry < 0 && yEntry < 0) ||
            xEntry > 1 || yEntry > 1) {
            return null;
        }

        // Calculate collision normal
        let normalX = 0, normalY = 0;

        if (xEntry > yEntry) {
            normalX = xInvEntry < 0 ? 1 : -1;
        } else {
            normalY = yInvEntry < 0 ? 1 : -1;
        }

        return {
            time: entryTime,
            normal: { x: normalX, y: normalY },
            position: {
                x: moving.x + vx * entryTime,
                y: moving.y + vy * entryTime
            }
        };
    }
}
```

## Spatial Partitioning

Spatial partitioning reduces the number of collision checks needed by dividing space into regions.

### Claude Code Prompt

```
Prompt: "Create a spatial hash grid for broad-phase collision detection.
Include automatic grid sizing, dynamic object insertion/removal, and
visualization showing grid cells and which objects are in which cells.
Compare performance with and without spatial partitioning."
```

### Implementation

```javascript
class SpatialGrid {
    constructor(cellSize = 100) {
        this.cellSize = cellSize;
        this.grid = new Map();
    }

    // Get cell key for position
    getCellKey(x, y) {
        const cellX = Math.floor(x / this.cellSize);
        const cellY = Math.floor(y / this.cellSize);
        return `${cellX},${cellY}`;
    }

    // Get all cells that object overlaps
    getCellsForObject(obj) {
        const cells = new Set();

        const minCellX = Math.floor(obj.x / this.cellSize);
        const minCellY = Math.floor(obj.y / this.cellSize);
        const maxCellX = Math.floor((obj.x + obj.width) / this.cellSize);
        const maxCellY = Math.floor((obj.y + obj.height) / this.cellSize);

        for (let cy = minCellY; cy <= maxCellY; cy++) {
            for (let cx = minCellX; cx <= maxCellX; cx++) {
                cells.add(`${cx},${cy}`);
            }
        }

        return cells;
    }

    // Insert object into grid
    insert(obj) {
        const cells = this.getCellsForObject(obj);

        for (const cellKey of cells) {
            if (!this.grid.has(cellKey)) {
                this.grid.set(cellKey, new Set());
            }
            this.grid.get(cellKey).add(obj);
        }

        obj._gridCells = cells;
    }

    // Remove object from grid
    remove(obj) {
        if (!obj._gridCells) return;

        for (const cellKey of obj._gridCells) {
            const cell = this.grid.get(cellKey);
            if (cell) {
                cell.delete(obj);
                if (cell.size === 0) {
                    this.grid.delete(cellKey);
                }
            }
        }

        delete obj._gridCells;
    }

    // Update object position in grid
    update(obj) {
        this.remove(obj);
        this.insert(obj);
    }

    // Get nearby objects
    getNearby(obj) {
        const nearby = new Set();
        const cells = this.getCellsForObject(obj);

        for (const cellKey of cells) {
            const cell = this.grid.get(cellKey);
            if (cell) {
                for (const other of cell) {
                    if (other !== obj) {
                        nearby.add(other);
                    }
                }
            }
        }

        return Array.from(nearby);
    }

    // Clear grid
    clear() {
        this.grid.clear();
    }

    // Render debug visualization
    renderDebug(ctx, width, height) {
        ctx.strokeStyle = 'rgba(0, 255, 0, 0.2)';
        ctx.lineWidth = 1;

        // Draw grid lines
        for (let x = 0; x < width; x += this.cellSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }

        for (let y = 0; y < height; y += this.cellSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }

        // Highlight occupied cells
        ctx.fillStyle = 'rgba(0, 255, 0, 0.1)';
        for (const [cellKey, objects] of this.grid) {
            if (objects.size > 0) {
                const [cx, cy] = cellKey.split(',').map(Number);
                ctx.fillRect(
                    cx * this.cellSize,
                    cy * this.cellSize,
                    this.cellSize,
                    this.cellSize
                );
            }
        }
    }
}
```

## Performance Comparisons

### Benchmark Implementation

```javascript
class CollisionBenchmark {
    static benchmark(name, collisionFn, objectCount, iterations = 1000) {
        const objects = [];

        // Create test objects
        for (let i = 0; i < objectCount; i++) {
            objects.push({
                x: Math.random() * 800,
                y: Math.random() * 600,
                width: 20 + Math.random() * 30,
                height: 20 + Math.random() * 30,
                radius: 25
            });
        }

        // Benchmark
        const startTime = performance.now();

        for (let iter = 0; iter < iterations; iter++) {
            let collisions = 0;

            for (let i = 0; i < objects.length; i++) {
                for (let j = i + 1; j < objects.length; j++) {
                    if (collisionFn(objects[i], objects[j])) {
                        collisions++;
                    }
                }
            }
        }

        const endTime = performance.now();
        const totalTime = endTime - startTime;
        const avgTime = totalTime / iterations;

        console.log(`${name}:`);
        console.log(`  Objects: ${objectCount}`);
        console.log(`  Total checks: ${objectCount * (objectCount - 1) / 2}`);
        console.log(`  Total time: ${totalTime.toFixed(2)}ms`);
        console.log(`  Avg time: ${avgTime.toFixed(4)}ms`);
        console.log(`  Checks/ms: ${((objectCount * (objectCount - 1) / 2) / avgTime).toFixed(0)}`);
    }

    static runAllBenchmarks() {
        const objectCounts = [50, 100, 200];

        for (const count of objectCounts) {
            console.log(`\n=== ${count} Objects ===`);

            this.benchmark('AABB', (a, b) => {
                return AABBCollision.checkCollision(a, b);
            }, count, 100);

            this.benchmark('Circle', (a, b) => {
                return CircleCollision.checkCollision(a, b);
            }, count, 100);
        }
    }
}

// Run benchmarks
// CollisionBenchmark.runAllBenchmarks();
```

## When to Use Which Technique

### Decision Tree

1. **Simple rectangular objects, no rotation** → AABB
   - Fastest option
   - Perfect for tiles, platforms, simple UI elements

2. **Circular or round objects** → Circle Collision
   - Nearly as fast as AABB
   - Great for balls, bullets, approximate collision

3. **Rotated rectangles** → OBB or SAT
   - More expensive but handles rotation
   - Good for vehicles, rotated platforms

4. **Arbitrary convex polygons** → SAT
   - Most general solution
   - Slower but very flexible

5. **Complex, non-convex shapes** → Pixel-Perfect
   - Most accurate but slowest
   - Use only when necessary (player hit detection in bullet hell)

6. **Fast-moving objects** → Continuous Collision Detection
   - Prevents tunneling
   - Essential for bullets, fast projectiles

7. **Many objects (100+)** → Spatial Partitioning
   - Reduces collision checks dramatically
   - Necessary for good performance with many objects

### Combination Strategies

Most games use multiple techniques:
- **Broad Phase**: Spatial partitioning to find potential collisions
- **Narrow Phase**: AABB, Circle, or SAT for exact collision
- **Special Cases**: Pixel-perfect for player in bullet hell, continuous for fast projectiles

## Conclusion

Collision detection is a balancing act between accuracy and performance. Start with simple techniques like AABB and Circle collision, then add more sophisticated methods only where needed. Always use spatial partitioning for games with many objects, and consider continuous collision detection for fast-moving objects.

---

**Related Documentation:**
- [Physics Integration](./physics-integration.md)
- [Game Loops and Timing](./game-loops-and-timing.md)
- [Performance Optimization](../10-performance-optimization/)
