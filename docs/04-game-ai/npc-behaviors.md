# NPC Behaviors

## Introduction

The difference between lifeless game characters and believable NPCs lies in the details of their behavior. A guard that robotically walks back and forth feels artificial; one that occasionally stops to look around, adjusts their pace, and reacts to environmental cues feels alive. This guide covers techniques for creating NPCs that move naturally, perceive their environment, remember events, and exhibit distinct personalities.

Realistic NPC behavior combines multiple systems: steering behaviors for smooth movement, perception systems for environmental awareness, memory for coherent reactions, and personality traits for individual variation. When layered together, these create NPCs that players believe are thinking, feeling entities rather than simple scripts.

This documentation provides complete implementations of steering behaviors, flocking and swarming, vision and perception systems, NPC memory and knowledge, personality-driven behavior, and techniques for making AI feel intelligent and alive.

## Steering Behaviors: Realistic Movement

Steering behaviors create smooth, natural-looking movement by applying forces to entities rather than setting positions directly. Developed by Craig Reynolds, these behaviors form the foundation of modern character movement.

### Basic Steering Behavior Framework

```javascript
class SteeringEntity {
    constructor(x, y) {
        this.position = {x, y};
        this.velocity = {x: 0, y: 0};
        this.acceleration = {x: 0, y: 0};

        this.maxSpeed = 3;
        this.maxForce = 0.2;
        this.mass = 1;

        this.radius = 10;
    }

    applyForce(force) {
        // F = ma, so a = F/m
        this.acceleration.x += force.x / this.mass;
        this.acceleration.y += force.y / this.mass;
    }

    update(deltaTime) {
        // Update velocity
        this.velocity.x += this.acceleration.x;
        this.velocity.y += this.acceleration.y;

        // Limit speed
        const speed = Math.sqrt(
            this.velocity.x * this.velocity.x +
            this.velocity.y * this.velocity.y
        );

        if (speed > this.maxSpeed) {
            this.velocity.x = (this.velocity.x / speed) * this.maxSpeed;
            this.velocity.y = (this.velocity.y / speed) * this.maxSpeed;
        }

        // Update position
        this.position.x += this.velocity.x;
        this.position.y += this.velocity.y;

        // Reset acceleration
        this.acceleration = {x: 0, y: 0};
    }

    // Vector utility functions
    static subtract(a, b) {
        return {x: a.x - b.x, y: a.y - b.y};
    }

    static add(a, b) {
        return {x: a.x + b.x, y: a.y + b.y};
    }

    static magnitude(v) {
        return Math.sqrt(v.x * v.x + v.y * v.y);
    }

    static normalize(v) {
        const mag = SteeringEntity.magnitude(v);
        if (mag === 0) return {x: 0, y: 0};
        return {x: v.x / mag, y: v.y / mag};
    }

    static multiply(v, scalar) {
        return {x: v.x * scalar, y: v.y * scalar};
    }

    static limit(v, max) {
        const mag = SteeringEntity.magnitude(v);
        if (mag > max) {
            return SteeringEntity.multiply(SteeringEntity.normalize(v), max);
        }
        return v;
    }
}
```

### Seek and Flee Behaviors

```javascript
class SteeringBehaviors {
    static seek(entity, target) {
        // Desired velocity: direction to target at max speed
        const desired = SteeringEntity.subtract(target, entity.position);
        const distance = SteeringEntity.magnitude(desired);

        if (distance > 0) {
            const normalized = SteeringEntity.normalize(desired);
            const desiredVelocity = SteeringEntity.multiply(normalized, entity.maxSpeed);

            // Steering force: desired - current
            const steer = SteeringEntity.subtract(desiredVelocity, entity.velocity);
            return SteeringEntity.limit(steer, entity.maxForce);
        }

        return {x: 0, y: 0};
    }

    static flee(entity, target) {
        // Flee is seek in opposite direction
        const desired = SteeringEntity.subtract(entity.position, target);
        const distance = SteeringEntity.magnitude(desired);

        if (distance > 0) {
            const normalized = SteeringEntity.normalize(desired);
            const desiredVelocity = SteeringEntity.multiply(normalized, entity.maxSpeed);

            const steer = SteeringEntity.subtract(desiredVelocity, entity.velocity);
            return SteeringEntity.limit(steer, entity.maxForce);
        }

        return {x: 0, y: 0};
    }

    static arrive(entity, target, slowingRadius = 100) {
        // Seek but slow down as we approach
        const desired = SteeringEntity.subtract(target, entity.position);
        const distance = SteeringEntity.magnitude(desired);

        if (distance > 0) {
            const normalized = SteeringEntity.normalize(desired);

            // Calculate desired speed based on distance
            let speed = entity.maxSpeed;
            if (distance < slowingRadius) {
                speed = entity.maxSpeed * (distance / slowingRadius);
            }

            const desiredVelocity = SteeringEntity.multiply(normalized, speed);
            const steer = SteeringEntity.subtract(desiredVelocity, entity.velocity);

            return SteeringEntity.limit(steer, entity.maxForce);
        }

        return {x: 0, y: 0};
    }

    static pursue(entity, target, targetVelocity) {
        // Predict where target will be
        const distance = SteeringEntity.magnitude(
            SteeringEntity.subtract(target, entity.position)
        );

        const lookAhead = distance / entity.maxSpeed;

        const predictedPosition = SteeringEntity.add(
            target,
            SteeringEntity.multiply(targetVelocity, lookAhead)
        );

        return this.seek(entity, predictedPosition);
    }

    static evade(entity, target, targetVelocity) {
        // Predict and flee
        const distance = SteeringEntity.magnitude(
            SteeringEntity.subtract(target, entity.position)
        );

        const lookAhead = distance / entity.maxSpeed;

        const predictedPosition = SteeringEntity.add(
            target,
            SteeringEntity.multiply(targetVelocity, lookAhead)
        );

        return this.flee(entity, predictedPosition);
    }

    static wander(entity, wanderRadius = 50, wanderDistance = 80, wanderAngle = 0) {
        // Create circle in front of entity
        const circleCenter = SteeringEntity.normalize(entity.velocity);
        const circlePos = SteeringEntity.multiply(circleCenter, wanderDistance);

        // Calculate displacement force
        const displacement = {
            x: Math.cos(wanderAngle) * wanderRadius,
            y: Math.sin(wanderAngle) * wanderRadius
        };

        // Wander force
        const wanderForce = SteeringEntity.add(circlePos, displacement);

        // Update wander angle for next frame (stored externally)
        entity.wanderAngle = (entity.wanderAngle || 0) + (Math.random() - 0.5) * 0.5;

        return SteeringEntity.limit(wanderForce, entity.maxForce);
    }

    static avoid(entity, obstacles, safeDistance = 50) {
        // Find closest obstacle in path
        let closestObstacle = null;
        let closestDistance = Infinity;

        const ahead = SteeringEntity.add(
            entity.position,
            SteeringEntity.multiply(
                SteeringEntity.normalize(entity.velocity),
                safeDistance
            )
        );

        for (const obstacle of obstacles) {
            const dist = SteeringEntity.magnitude(
                SteeringEntity.subtract(obstacle.position, ahead)
            );

            if (dist < obstacle.radius + entity.radius && dist < closestDistance) {
                closestObstacle = obstacle;
                closestDistance = dist;
            }
        }

        // Steer away from closest obstacle
        if (closestObstacle) {
            const avoidanceForce = SteeringEntity.subtract(
                ahead,
                closestObstacle.position
            );
            return SteeringEntity.limit(
                SteeringEntity.multiply(
                    SteeringEntity.normalize(avoidanceForce),
                    entity.maxForce * 2
                ),
                entity.maxForce
            );
        }

        return {x: 0, y: 0};
    }
}

// Example: NPC that seeks player but avoids obstacles
class SeekingNPC extends SteeringEntity {
    constructor(x, y) {
        super(x, y);
    }

    update(deltaTime, player, obstacles) {
        // Combine behaviors
        const seekForce = SteeringBehaviors.seek(this, player.position);
        const avoidForce = SteeringBehaviors.avoid(this, obstacles, 60);

        // Weight the forces
        this.applyForce(SteeringEntity.multiply(seekForce, 1.0));
        this.applyForce(SteeringEntity.multiply(avoidForce, 2.0)); // Avoid has priority

        super.update(deltaTime);
    }

    draw(ctx) {
        ctx.fillStyle = 'orange';
        ctx.beginPath();
        ctx.arc(this.position.x, this.position.y, this.radius, 0, Math.PI * 2);
        ctx.fill();

        // Draw velocity vector
        ctx.strokeStyle = 'red';
        ctx.beginPath();
        ctx.moveTo(this.position.x, this.position.y);
        ctx.lineTo(
            this.position.x + this.velocity.x * 5,
            this.position.y + this.velocity.y * 5
        );
        ctx.stroke();
    }
}
```

## Flocking and Swarming

Create coordinated group movement like birds, fish, or enemy swarms using three simple rules:

```javascript
class Boid extends SteeringEntity {
    constructor(x, y) {
        super(x, y);
        this.perceptionRadius = 50;
    }

    flock(boids) {
        const separation = this.separate(boids);
        const alignment = this.align(boids);
        const cohesion = this.cohesion(boids);

        // Weight the forces
        this.applyForce(SteeringEntity.multiply(separation, 1.5));
        this.applyForce(SteeringEntity.multiply(alignment, 1.0));
        this.applyForce(SteeringEntity.multiply(cohesion, 1.0));
    }

    separate(boids) {
        const desiredSeparation = this.radius * 4;
        let steer = {x: 0, y: 0};
        let count = 0;

        for (const other of boids) {
            if (other === this) continue;

            const diff = SteeringEntity.subtract(this.position, other.position);
            const distance = SteeringEntity.magnitude(diff);

            if (distance > 0 && distance < desiredSeparation) {
                // Weight by distance (closer = stronger force)
                const normalized = SteeringEntity.normalize(diff);
                const weighted = SteeringEntity.multiply(normalized, 1 / distance);

                steer = SteeringEntity.add(steer, weighted);
                count++;
            }
        }

        if (count > 0) {
            steer = SteeringEntity.multiply(steer, 1 / count);

            // Steer = desired - velocity
            if (SteeringEntity.magnitude(steer) > 0) {
                const normalized = SteeringEntity.normalize(steer);
                const desired = SteeringEntity.multiply(normalized, this.maxSpeed);
                steer = SteeringEntity.subtract(desired, this.velocity);
                steer = SteeringEntity.limit(steer, this.maxForce);
            }
        }

        return steer;
    }

    align(boids) {
        const neighborDist = this.perceptionRadius;
        let sum = {x: 0, y: 0};
        let count = 0;

        for (const other of boids) {
            if (other === this) continue;

            const distance = SteeringEntity.magnitude(
                SteeringEntity.subtract(this.position, other.position)
            );

            if (distance > 0 && distance < neighborDist) {
                sum = SteeringEntity.add(sum, other.velocity);
                count++;
            }
        }

        if (count > 0) {
            sum = SteeringEntity.multiply(sum, 1 / count);
            const normalized = SteeringEntity.normalize(sum);
            const desired = SteeringEntity.multiply(normalized, this.maxSpeed);

            const steer = SteeringEntity.subtract(desired, this.velocity);
            return SteeringEntity.limit(steer, this.maxForce);
        }

        return {x: 0, y: 0};
    }

    cohesion(boids) {
        const neighborDist = this.perceptionRadius;
        let sum = {x: 0, y: 0};
        let count = 0;

        for (const other of boids) {
            if (other === this) continue;

            const distance = SteeringEntity.magnitude(
                SteeringEntity.subtract(this.position, other.position)
            );

            if (distance > 0 && distance < neighborDist) {
                sum = SteeringEntity.add(sum, other.position);
                count++;
            }
        }

        if (count > 0) {
            sum = SteeringEntity.multiply(sum, 1 / count);
            return SteeringBehaviors.seek(this, sum);
        }

        return {x: 0, y: 0};
    }

    update(deltaTime, boids, boundaries) {
        this.flock(boids);

        // Keep within boundaries
        const margin = 50;
        if (this.position.x < margin) {
            this.applyForce({x: this.maxForce, y: 0});
        } else if (this.position.x > boundaries.width - margin) {
            this.applyForce({x: -this.maxForce, y: 0});
        }

        if (this.position.y < margin) {
            this.applyForce({x: 0, y: this.maxForce});
        } else if (this.position.y > boundaries.height - margin) {
            this.applyForce({x: 0, y: -this.maxForce});
        }

        super.update(deltaTime);
    }

    draw(ctx) {
        // Draw as triangle pointing in velocity direction
        const angle = Math.atan2(this.velocity.y, this.velocity.x);

        ctx.save();
        ctx.translate(this.position.x, this.position.y);
        ctx.rotate(angle);

        ctx.fillStyle = 'blue';
        ctx.beginPath();
        ctx.moveTo(this.radius, 0);
        ctx.lineTo(-this.radius, this.radius / 2);
        ctx.lineTo(-this.radius, -this.radius / 2);
        ctx.closePath();
        ctx.fill();

        ctx.restore();

        // Draw perception radius (debug)
        ctx.strokeStyle = 'rgba(0, 100, 255, 0.2)';
        ctx.beginPath();
        ctx.arc(this.position.x, this.position.y, this.perceptionRadius, 0, Math.PI * 2);
        ctx.stroke();
    }
}

// Create a flock
class FlockSimulation {
    constructor(canvas, numBoids = 50) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.boids = [];

        for (let i = 0; i < numBoids; i++) {
            const boid = new Boid(
                Math.random() * canvas.width,
                Math.random() * canvas.height
            );

            // Random initial velocity
            boid.velocity = {
                x: (Math.random() - 0.5) * 2,
                y: (Math.random() - 0.5) * 2
            };

            this.boids.push(boid);
        }
    }

    update() {
        for (const boid of this.boids) {
            boid.update(1, this.boids, {
                width: this.canvas.width,
                height: this.canvas.height
            });
        }
    }

    draw() {
        this.ctx.fillStyle = 'rgba(20, 20, 20, 0.1)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        for (const boid of this.boids) {
            boid.draw(this.ctx);
        }
    }

    run() {
        const animate = () => {
            this.update();
            this.draw();
            requestAnimationFrame(animate);
        };
        animate();
    }
}
```

## Vision Cones and Perception Systems

NPCs should only react to what they can see:

```javascript
class PerceptionSystem {
    constructor(entity) {
        this.entity = entity;
        this.visionRange = 150;
        this.visionAngle = Math.PI / 3; // 60 degrees
        this.hearingRange = 200;
        this.visibleEntities = [];
        this.heardEntities = [];
    }

    update(entities) {
        this.visibleEntities = [];
        this.heardEntities = [];

        for (const other of entities) {
            if (other === this.entity) continue;

            // Check if in hearing range
            const distance = this.getDistance(this.entity.position, other.position);

            if (distance <= this.hearingRange) {
                this.heardEntities.push(other);
            }

            // Check if in vision range and cone
            if (distance <= this.visionRange && this.isInVisionCone(other.position)) {
                this.visibleEntities.push(other);
            }
        }
    }

    isInVisionCone(targetPosition) {
        // Get direction entity is facing
        const facingAngle = this.getFacingAngle();

        // Get angle to target
        const dx = targetPosition.x - this.entity.position.x;
        const dy = targetPosition.y - this.entity.position.y;
        const angleToTarget = Math.atan2(dy, dx);

        // Calculate angle difference
        let angleDiff = angleToTarget - facingAngle;

        // Normalize to -PI to PI
        while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
        while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;

        // Check if within vision cone
        return Math.abs(angleDiff) <= this.visionAngle / 2;
    }

    getFacingAngle() {
        // Assume entity faces direction of velocity
        if (this.entity.velocity) {
            return Math.atan2(this.entity.velocity.y, this.entity.velocity.x);
        }
        return 0; // Default facing right
    }

    getDistance(pos1, pos2) {
        const dx = pos2.x - pos1.x;
        const dy = pos2.y - pos1.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    canSee(targetPosition) {
        const distance = this.getDistance(this.entity.position, targetPosition);
        return distance <= this.visionRange && this.isInVisionCone(targetPosition);
    }

    canHear(targetPosition) {
        const distance = this.getDistance(this.entity.position, targetPosition);
        return distance <= this.hearingRange;
    }

    visualize(ctx) {
        const facingAngle = this.getFacingAngle();

        // Draw vision cone
        ctx.fillStyle = 'rgba(255, 255, 0, 0.2)';
        ctx.beginPath();
        ctx.moveTo(this.entity.position.x, this.entity.position.y);

        const startAngle = facingAngle - this.visionAngle / 2;
        const endAngle = facingAngle + this.visionAngle / 2;

        ctx.arc(
            this.entity.position.x,
            this.entity.position.y,
            this.visionRange,
            startAngle,
            endAngle
        );

        ctx.closePath();
        ctx.fill();

        // Draw hearing range
        ctx.strokeStyle = 'rgba(100, 100, 255, 0.3)';
        ctx.beginPath();
        ctx.arc(
            this.entity.position.x,
            this.entity.position.y,
            this.hearingRange,
            0,
            Math.PI * 2
        );
        ctx.stroke();

        // Highlight visible entities
        ctx.fillStyle = 'red';
        for (const entity of this.visibleEntities) {
            ctx.beginPath();
            ctx.arc(entity.position.x, entity.position.y, 5, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}

// NPC with perception
class PerceptiveNPC extends SteeringEntity {
    constructor(x, y) {
        super(x, y);
        this.perception = new PerceptionSystem(this);
        this.state = 'IDLE';
    }

    update(deltaTime, entities) {
        this.perception.update(entities);

        // React to visible threats
        if (this.perception.visibleEntities.length > 0) {
            const threat = this.perception.visibleEntities[0];
            const fleeForce = SteeringBehaviors.flee(this, threat.position);
            this.applyForce(fleeForce);
            this.state = 'FLEEING';
        } else if (this.perception.heardEntities.length > 0) {
            // Investigate sounds
            const sound = this.perception.heardEntities[0];
            const seekForce = SteeringBehaviors.seek(this, sound.position);
            this.applyForce(SteeringEntity.multiply(seekForce, 0.5));
            this.state = 'INVESTIGATING';
        } else {
            // Wander
            const wanderForce = SteeringBehaviors.wander(this);
            this.applyForce(wanderForce);
            this.state = 'WANDERING';
        }

        super.update(deltaTime);
    }

    draw(ctx) {
        this.perception.visualize(ctx);

        // Draw NPC
        ctx.fillStyle = 'green';
        ctx.beginPath();
        ctx.arc(this.position.x, this.position.y, this.radius, 0, Math.PI * 2);
        ctx.fill();

        // Draw state
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(this.state, this.position.x, this.position.y - 20);
    }
}
```

## Memory and Knowledge Systems

NPCs that remember create more believable interactions:

```javascript
class NPCMemory {
    constructor(capacity = 20) {
        this.capacity = capacity;
        this.memories = [];
        this.knowledge = new Map(); // Long-term facts
    }

    remember(event) {
        const memory = {
            event: event,
            timestamp: Date.now(),
            importance: event.importance || 1
        };

        this.memories.push(memory);

        // Forget old memories if capacity exceeded
        if (this.memories.length > this.capacity) {
            // Remove least important old memory
            this.memories.sort((a, b) => {
                const ageA = Date.now() - a.timestamp;
                const ageB = Date.now() - b.timestamp;
                return (ageA * (1 / a.importance)) - (ageB * (1 / b.importance));
            });

            this.memories.shift();
        }
    }

    recall(type, maxAge = Infinity) {
        const now = Date.now();
        return this.memories.filter(m =>
            m.event.type === type &&
            (now - m.timestamp) <= maxAge
        );
    }

    hasSeenBefore(entityId) {
        return this.memories.some(m =>
            m.event.type === 'SIGHTING' &&
            m.event.entityId === entityId
        );
    }

    learn(fact, value) {
        this.knowledge.set(fact, value);
    }

    knows(fact) {
        return this.knowledge.has(fact);
    }

    forget(fact) {
        this.knowledge.delete(fact);
    }

    getKnowledge(fact) {
        return this.knowledge.get(fact);
    }

    // Get most recent memory of a type
    getMostRecent(type) {
        const relevant = this.recall(type);
        if (relevant.length === 0) return null;

        return relevant.reduce((latest, current) =>
            current.timestamp > latest.timestamp ? current : latest
        );
    }
}

// NPC with memory
class MemoryNPC extends PerceptiveNPC {
    constructor(x, y, name) {
        super(x, y);
        this.name = name;
        this.memory = new NPCMemory(30);
        this.relationships = new Map(); // entityId -> relationship value (-1 to 1)
    }

    update(deltaTime, entities) {
        this.perception.update(entities);

        // Record sightings
        for (const entity of this.perception.visibleEntities) {
            if (entity.id) {
                this.memory.remember({
                    type: 'SIGHTING',
                    entityId: entity.id,
                    position: {...entity.position},
                    importance: 2
                });

                // Update relationship based on entity type
                if (entity.isPlayer) {
                    const hasSeenBefore = this.memory.hasSeenBefore(entity.id);

                    if (!hasSeenBefore) {
                        console.log(`${this.name}: First time seeing player!`);
                        this.relationships.set(entity.id, 0); // Neutral
                    } else {
                        // Gradually warm up to player
                        const current = this.relationships.get(entity.id) || 0;
                        this.relationships.set(entity.id, Math.min(1, current + 0.01));
                    }
                }
            }
        }

        // Behavior based on memory and relationships
        if (this.perception.visibleEntities.length > 0) {
            const entity = this.perception.visibleEntities[0];
            const relationship = this.relationships.get(entity.id) || 0;

            if (relationship < -0.3) {
                // Hostile
                const fleeForce = SteeringBehaviors.flee(this, entity.position);
                this.applyForce(fleeForce);
                this.state = 'FLEEING';
            } else if (relationship > 0.3) {
                // Friendly - approach
                const seekForce = SteeringBehaviors.seek(this, entity.position);
                this.applyForce(SteeringEntity.multiply(seekForce, 0.5));
                this.state = 'APPROACHING';
            } else {
                // Neutral - observe
                this.velocity = {x: 0, y: 0};
                this.state = 'OBSERVING';
            }
        } else {
            // Check if we remember seeing someone recently
            const recentSighting = this.memory.getMostRecent('SIGHTING');

            if (recentSighting && (Date.now() - recentSighting.timestamp) < 5000) {
                // Investigate last known position
                const seekForce = SteeringBehaviors.seek(this, recentSighting.event.position);
                this.applyForce(SteeringEntity.multiply(seekForce, 0.3));
                this.state = 'INVESTIGATING';
            } else {
                // Wander
                const wanderForce = SteeringBehaviors.wander(this);
                this.applyForce(wanderForce);
                this.state = 'WANDERING';
            }
        }

        super.update(deltaTime, entities);
    }

    draw(ctx) {
        super.draw(ctx);

        // Draw relationship status
        if (this.relationships.size > 0) {
            const relationships = Array.from(this.relationships.values());
            const avgRelationship = relationships.reduce((a, b) => a + b, 0) / relationships.length;

            let color = 'gray';
            if (avgRelationship > 0.3) color = 'green';
            else if (avgRelationship < -0.3) color = 'red';

            ctx.strokeStyle = color;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(this.position.x, this.position.y, this.radius + 3, 0, Math.PI * 2);
            ctx.stroke();
            ctx.lineWidth = 1;
        }

        // Draw name
        ctx.fillStyle = 'white';
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(this.name, this.position.x, this.position.y + 25);
    }
}
```

## Personality Traits Affecting Behavior

Give each NPC unique personality:

```javascript
class PersonalityTraits {
    constructor() {
        // All traits from 0 to 1
        this.courage = 0.5;        // 0 = cowardly, 1 = brave
        this.aggression = 0.5;     // 0 = passive, 1 = aggressive
        this.curiosity = 0.5;      // 0 = cautious, 1 = curious
        this.sociability = 0.5;    // 0 = antisocial, 1 = social
        this.energy = 0.5;         // 0 = lazy, 1 = energetic
    }

    static random() {
        const traits = new PersonalityTraits();
        traits.courage = Math.random();
        traits.aggression = Math.random();
        traits.curiosity = Math.random();
        traits.sociability = Math.random();
        traits.energy = Math.random();
        return traits;
    }

    static fromArchetype(type) {
        const traits = new PersonalityTraits();

        switch (type) {
            case 'GUARD':
                traits.courage = 0.8;
                traits.aggression = 0.6;
                traits.curiosity = 0.3;
                traits.sociability = 0.4;
                traits.energy = 0.7;
                break;

            case 'VILLAGER':
                traits.courage = 0.3;
                traits.aggression = 0.2;
                traits.curiosity = 0.6;
                traits.sociability = 0.8;
                traits.energy = 0.5;
                break;

            case 'SCHOLAR':
                traits.courage = 0.4;
                traits.aggression = 0.1;
                traits.curiosity = 0.9;
                traits.sociability = 0.5;
                traits.energy = 0.4;
                break;

            case 'MERCHANT':
                traits.courage = 0.5;
                traits.aggression = 0.3;
                traits.curiosity = 0.7;
                traits.sociability = 0.9;
                traits.energy = 0.8;
                break;
        }

        return traits;
    }
}

class PersonalityDrivenNPC extends MemoryNPC {
    constructor(x, y, name, personalityType = null) {
        super(x, y, name);

        this.personality = personalityType ?
            PersonalityTraits.fromArchetype(personalityType) :
            PersonalityTraits.random();

        // Adjust parameters based on personality
        this.maxSpeed = 2 + this.personality.energy;
        this.detectionRange = 100 + this.personality.curiosity * 100;
    }

    update(deltaTime, entities) {
        this.perception.update(entities);

        // Record sightings
        for (const entity of this.perception.visibleEntities) {
            if (entity.id) {
                this.memory.remember({
                    type: 'SIGHTING',
                    entityId: entity.id,
                    position: {...entity.position},
                    importance: 2
                });
            }
        }

        // Behavior influenced by personality
        if (this.perception.visibleEntities.length > 0) {
            const entity = this.perception.visibleEntities[0];
            const relationship = this.relationships.get(entity.id) || 0;

            // Courage affects flee threshold
            const fleeThreshold = -0.3 + (1 - this.personality.courage) * 0.5;

            if (relationship < fleeThreshold) {
                const fleeForce = SteeringBehaviors.flee(this, entity.position);
                this.applyForce(fleeForce);
                this.state = 'FLEEING';
            } else if (this.personality.aggression > 0.6 && relationship < 0) {
                // Aggressive NPCs approach threats
                const seekForce = SteeringBehaviors.seek(this, entity.position);
                this.applyForce(seekForce);
                this.state = 'CONFRONTING';
            } else if (this.personality.sociability > 0.6 && relationship > 0) {
                // Social NPCs approach friends
                const arriveForce = SteeringBehaviors.arrive(this, entity.position, 100);
                this.applyForce(arriveForce);
                this.state = 'SOCIALIZING';
            } else {
                this.velocity = {x: 0, y: 0};
                this.state = 'OBSERVING';
            }
        } else {
            // Curiosity affects investigation
            const recentSighting = this.memory.getMostRecent('SIGHTING');

            if (recentSighting &&
                (Date.now() - recentSighting.timestamp) < 5000 &&
                this.personality.curiosity > 0.5) {

                const seekForce = SteeringBehaviors.seek(this, recentSighting.event.position);
                this.applyForce(SteeringEntity.multiply(seekForce, this.personality.curiosity));
                this.state = 'INVESTIGATING';
            } else {
                // Energy affects wander speed
                const wanderForce = SteeringBehaviors.wander(this);
                this.applyForce(SteeringEntity.multiply(wanderForce, this.personality.energy));
                this.state = 'WANDERING';
            }
        }

        SteeringEntity.prototype.update.call(this, deltaTime);
    }

    draw(ctx) {
        super.draw(ctx);

        // Draw personality indicator
        const x = this.position.x + 20;
        const y = this.position.y - 20;

        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(x, y, 60, 50);

        ctx.fillStyle = 'white';
        ctx.font = '8px monospace';
        ctx.textAlign = 'left';

        ctx.fillText(`C:${this.personality.courage.toFixed(1)}`, x + 2, y + 10);
        ctx.fillText(`A:${this.personality.aggression.toFixed(1)}`, x + 2, y + 20);
        ctx.fillText(`U:${this.personality.curiosity.toFixed(1)}`, x + 2, y + 30);
        ctx.fillText(`S:${this.personality.sociability.toFixed(1)}`, x + 2, y + 40);
    }
}
```

## Making AI Feel Intelligent

Techniques to create the illusion of intelligence:

```javascript
class IntelligentNPC extends PersonalityDrivenNPC {
    constructor(x, y, name, personalityType) {
        super(x, y, name, personalityType);

        this.reactionDelay = 200 + Math.random() * 300; // Human-like delay
        this.pendingReaction = null;
        this.lastReactionTime = 0;

        this.debugMessages = [];
    }

    update(deltaTime, entities) {
        // Process delayed reactions
        if (this.pendingReaction && Date.now() - this.lastReactionTime >= this.reactionDelay) {
            this.pendingReaction();
            this.pendingReaction = null;
        }

        // Add randomness to perception (simulate distraction)
        if (Math.random() < 0.05) {
            // Temporarily don't update perception (distracted)
            return;
        }

        this.perception.update(entities);

        // React with delay
        if (this.perception.visibleEntities.length > 0 && !this.pendingReaction) {
            this.lastReactionTime = Date.now();

            const entity = this.perception.visibleEntities[0];

            this.pendingReaction = () => {
                // Show "thought process"
                this.addDebugMessage(`I see someone!`);

                const relationship = this.relationships.get(entity.id) || 0;

                if (relationship < -0.3) {
                    this.addDebugMessage(`That's a threat! Running away.`);
                } else if (relationship > 0.3) {
                    this.addDebugMessage(`A friend! Going to say hi.`);
                } else {
                    this.addDebugMessage(`Who is that? Watching carefully.`);
                }

                // Continue with normal behavior
                super.update(deltaTime, entities);
            };
        } else if (!this.pendingReaction) {
            super.update(deltaTime, entities);
        }

        // Clear old debug messages
        if (this.debugMessages.length > 0) {
            const now = Date.now();
            this.debugMessages = this.debugMessages.filter(m => now - m.time < 3000);
        }
    }

    addDebugMessage(message) {
        this.debugMessages.push({
            text: message,
            time: Date.now()
        });
    }

    draw(ctx) {
        super.draw(ctx);

        // Draw thought bubble
        if (this.debugMessages.length > 0) {
            const msg = this.debugMessages[this.debugMessages.length - 1];

            ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            ctx.strokeStyle = 'black';
            ctx.lineWidth = 2;

            const bubbleX = this.position.x;
            const bubbleY = this.position.y - 50;
            const bubbleWidth = msg.text.length * 6 + 10;
            const bubbleHeight = 20;

            // Bubble
            ctx.beginPath();
            ctx.roundRect(bubbleX - bubbleWidth / 2, bubbleY, bubbleWidth, bubbleHeight, 5);
            ctx.fill();
            ctx.stroke();

            // Tail
            ctx.beginPath();
            ctx.moveTo(bubbleX, bubbleY + bubbleHeight);
            ctx.lineTo(bubbleX - 5, bubbleY + bubbleHeight + 8);
            ctx.lineTo(bubbleX + 5, bubbleY + bubbleHeight + 5);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // Text
            ctx.fillStyle = 'black';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(msg.text, bubbleX, bubbleY + 14);
        }
    }
}
```

## Complete NPC Simulation

Bringing it all together:

```javascript
class NPCWorld {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        this.npcs = [];
        this.player = {
            position: {x: 400, y: 300},
            id: 'player',
            isPlayer: true
        };

        // Create diverse NPCs
        this.npcs.push(new IntelligentNPC(100, 100, 'Guard Alice', 'GUARD'));
        this.npcs.push(new IntelligentNPC(600, 400, 'Merchant Bob', 'MERCHANT'));
        this.npcs.push(new IntelligentNPC(300, 200, 'Scholar Carol', 'SCHOLAR'));
        this.npcs.push(new IntelligentNPC(500, 300, 'Villager Dave', 'VILLAGER'));
    }

    update() {
        const allEntities = [...this.npcs, this.player];

        for (const npc of this.npcs) {
            npc.update(1, allEntities);
        }
    }

    draw() {
        this.ctx.fillStyle = '#2d2d2d';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw player
        this.ctx.fillStyle = 'cyan';
        this.ctx.beginPath();
        this.ctx.arc(this.player.position.x, this.player.position.y, 15, 0, Math.PI * 2);
        this.ctx.fill();

        // Draw NPCs
        for (const npc of this.npcs) {
            npc.draw(this.ctx);
        }
    }

    run() {
        const loop = () => {
            this.update();
            this.draw();
            requestAnimationFrame(loop);
        };
        loop();
    }

    handleMouseMove(event) {
        const rect = this.canvas.getBoundingClientRect();
        this.player.position.x = event.clientX - rect.left;
        this.player.position.y = event.clientY - rect.top;
    }
}
```

## Claude Code Prompts for NPC Behaviors

**Steering Behaviors:**
```
"Implement a seek and avoid steering behavior system where NPCs navigate toward a target while avoiding obstacles"
```

**Flocking:**
```
"Create a flocking simulation with separation, alignment, and cohesion for 50 boids with smooth, realistic movement"
```

**Perception:**
```
"Add a vision cone system to this NPC that only reacts to entities within a 60-degree cone in front of them"
```

**Memory:**
```
"Implement an NPC memory system that remembers the last 20 significant events and influences decision-making"
```

**Personality:**
```
"Create personality traits (courage, aggression, curiosity) that affect how NPCs react to the player and make each feel unique"
```

## Related Documentation

- [Behavior Trees](./behavior-trees.md) - Decision-making for NPC actions
- [Finite State Machines](./finite-state-machines.md) - State management for NPC behaviors
- [Pathfinding Algorithms](./pathfinding-algorithms.md) - Long-range navigation
- [Collision Detection](../02-core-game-concepts/collision-detection.md) - Obstacle avoidance

Believable NPC behavior is the key to immersive game worlds. Combine steering behaviors for natural movement, perception for environmental awareness, memory for consistency, and personality for uniqueness. The result: NPCs that feel alive!
