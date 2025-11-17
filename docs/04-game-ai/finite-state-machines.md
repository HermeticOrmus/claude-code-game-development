# Finite State Machines

## Introduction

Finite State Machines (FSMs) are the simplest and most intuitive approach to AI decision-making. An FSM defines a set of states (idle, patrol, chase, attack) and rules for transitioning between them. Despite their simplicity, FSMs power AI in countless games, from classic Pac-Man ghosts to modern indie titles. When you need clear, predictable AI behavior with a limited number of states, FSMs are the perfect tool.

The key strength of FSMs is their clarity. Looking at an FSM diagram immediately reveals how AI will behave and what triggers each behavior change. This makes FSMs excellent for prototyping, simple enemies, character animation controllers, and game state management. While they become unwieldy with many states (10+), for typical enemy AI with 3-7 states, FSMs strike the perfect balance between simplicity and capability.

This guide covers FSM fundamentals, complete implementations, practical character AI examples, hierarchical state machines for complex behaviors, comparison with behavior trees, and debugging techniques.

## FSM Fundamentals

A Finite State Machine consists of:

**States**: Discrete modes of behavior. An enemy might have states like IDLE, PATROL, CHASE, ATTACK, FLEE.

**Transitions**: Rules that move from one state to another. "If player detected, transition from PATROL to CHASE."

**Actions**: What happens in each state. In CHASE state, move toward player.

**Entry/Exit Hooks**: Code that runs when entering or leaving a state. Play animation on entry, stop animation on exit.

At any given time, the FSM is in exactly one state. Each frame, the current state:
1. Executes its update logic
2. Checks transition conditions
3. Transitions to a new state if conditions are met

### FSM Architecture

```
┌─────────┐  player detected   ┌─────────┐  in range   ┌─────────┐
│  PATROL │ ─────────────────> │  CHASE  │ ──────────> │  ATTACK │
└─────────┘                     └─────────┘             └─────────┘
     ^                               │                       │
     │                               │                       │
     │      player lost              │        low health     │
     └───────────────────────────────┴───────────────────────┘
                                     │
                                     v
                              ┌─────────┐
                              │  FLEE   │
                              └─────────┘
```

## Simple State Machine Implementation

Let's start with a basic FSM framework:

```javascript
class State {
    constructor(name) {
        this.name = name;
    }

    enter(actor, fsm) {
        // Called when entering this state
    }

    execute(actor, fsm, deltaTime) {
        // Called every frame while in this state
        // Should return the next state name or null to stay
        return null;
    }

    exit(actor, fsm) {
        // Called when leaving this state
    }
}

class FiniteStateMachine {
    constructor(initialState) {
        this.states = new Map();
        this.currentState = null;
        this.initialState = initialState;
    }

    addState(state) {
        this.states.set(state.name, state);
    }

    setState(stateName) {
        const newState = this.states.get(stateName);

        if (!newState) {
            console.error(`State ${stateName} not found`);
            return;
        }

        // Exit current state
        if (this.currentState) {
            this.currentState.exit(this.actor, this);
        }

        // Enter new state
        this.currentState = newState;
        this.currentState.enter(this.actor, this);
    }

    update(actor, deltaTime) {
        this.actor = actor;

        // Initialize if no current state
        if (!this.currentState) {
            this.setState(this.initialState);
            return;
        }

        // Execute current state
        const nextState = this.currentState.execute(actor, this, deltaTime);

        // Transition if requested
        if (nextState && nextState !== this.currentState.name) {
            this.setState(nextState);
        }
    }

    getCurrentStateName() {
        return this.currentState ? this.currentState.name : null;
    }
}
```

## Character AI States: Complete Enemy Example

Let's build a complete enemy AI with idle, patrol, chase, attack, and flee states.

```javascript
// Idle State - enemy waits and looks around
class IdleState extends State {
    constructor() {
        super('IDLE');
        this.waitTime = 0;
        this.waitDuration = 2000; // 2 seconds
    }

    enter(actor, fsm) {
        this.waitTime = 0;
        actor.velocity = {x: 0, y: 0};
        console.log(`${actor.name} is idle`);
    }

    execute(actor, fsm, deltaTime) {
        this.waitTime += deltaTime;

        // Check if player is detected
        if (this.canSeePlayer(actor, fsm.context)) {
            return 'CHASE';
        }

        // After waiting, start patrolling
        if (this.waitTime >= this.waitDuration) {
            return 'PATROL';
        }

        return null;
    }

    canSeePlayer(actor, context) {
        if (!context || !context.player) return false;

        const dx = context.player.x - actor.x;
        const dy = context.player.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        return distance <= actor.detectionRange;
    }

    exit(actor, fsm) {
        // Nothing to clean up
    }
}

// Patrol State - enemy moves between waypoints
class PatrolState extends State {
    constructor() {
        super('PATROL');
    }

    enter(actor, fsm) {
        console.log(`${actor.name} is patrolling`);
        // Ensure we have a patrol target
        if (!actor.currentPatrolIndex) {
            actor.currentPatrolIndex = 0;
        }
    }

    execute(actor, fsm, deltaTime) {
        // Check if player is detected
        if (this.canSeePlayer(actor, fsm.context)) {
            return 'CHASE';
        }

        // Move to current patrol point
        const target = actor.patrolPoints[actor.currentPatrolIndex];

        const dx = target.x - actor.x;
        const dy = target.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 5) {
            // Reached patrol point, move to next
            actor.currentPatrolIndex = (actor.currentPatrolIndex + 1) % actor.patrolPoints.length;
        } else {
            // Move toward patrol point
            const speed = actor.speed * (deltaTime / 1000);
            actor.x += (dx / distance) * speed;
            actor.y += (dy / distance) * speed;
        }

        return null;
    }

    canSeePlayer(actor, context) {
        if (!context || !context.player) return false;

        const dx = context.player.x - actor.x;
        const dy = context.player.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        return distance <= actor.detectionRange;
    }

    exit(actor, fsm) {
        // Remember where we were in patrol
    }
}

// Chase State - enemy pursues the player
class ChaseState extends State {
    constructor() {
        super('CHASE');
        this.lostTargetTime = 0;
        this.maxLostTime = 3000; // Give up after 3 seconds
    }

    enter(actor, fsm) {
        console.log(`${actor.name} is chasing!`);
        this.lostTargetTime = 0;
    }

    execute(actor, fsm, deltaTime) {
        const context = fsm.context;

        if (!context || !context.player) {
            return 'IDLE';
        }

        // Check if health is low
        if (actor.health < actor.fleeThreshold) {
            return 'FLEE';
        }

        const dx = context.player.x - actor.x;
        const dy = context.player.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Check if in attack range
        if (distance <= actor.attackRange) {
            return 'ATTACK';
        }

        // Check if player is still visible
        if (distance > actor.detectionRange) {
            this.lostTargetTime += deltaTime;

            if (this.lostTargetTime >= this.maxLostTime) {
                console.log(`${actor.name} lost the player`);
                return 'PATROL';
            }
        } else {
            this.lostTargetTime = 0;
        }

        // Move toward player
        const speed = actor.speed * 1.5 * (deltaTime / 1000); // Chase faster
        actor.x += (dx / distance) * speed;
        actor.y += (dy / distance) * speed;

        return null;
    }

    exit(actor, fsm) {
        this.lostTargetTime = 0;
    }
}

// Attack State - enemy attacks the player
class AttackState extends State {
    constructor() {
        super('ATTACK');
        this.attackCooldown = 0;
        this.attackDelay = 1000; // Attack every 1 second
    }

    enter(actor, fsm) {
        console.log(`${actor.name} is attacking!`);
        actor.velocity = {x: 0, y: 0};
        this.attackCooldown = 0;
    }

    execute(actor, fsm, deltaTime) {
        const context = fsm.context;

        if (!context || !context.player) {
            return 'IDLE';
        }

        // Check if health is low
        if (actor.health < actor.fleeThreshold) {
            return 'FLEE';
        }

        const dx = context.player.x - actor.x;
        const dy = context.player.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Player moved out of range
        if (distance > actor.attackRange * 1.2) {
            return 'CHASE';
        }

        // Attack cooldown
        this.attackCooldown += deltaTime;

        if (this.attackCooldown >= this.attackDelay) {
            this.performAttack(actor, context);
            this.attackCooldown = 0;
        }

        return null;
    }

    performAttack(actor, context) {
        console.log(`${actor.name} attacks for ${actor.attackDamage} damage!`);

        // Deal damage to player
        if (context.player && context.player.health !== undefined) {
            context.player.health -= actor.attackDamage;
        }

        // Trigger attack animation/effects
        if (actor.onAttack) {
            actor.onAttack();
        }
    }

    exit(actor, fsm) {
        this.attackCooldown = 0;
    }
}

// Flee State - enemy runs away when low on health
class FleeState extends State {
    constructor() {
        super('FLEE');
        this.fleeDuration = 0;
        this.maxFleeDuration = 5000; // Flee for 5 seconds
    }

    enter(actor, fsm) {
        console.log(`${actor.name} is fleeing!`);
        this.fleeDuration = 0;
    }

    execute(actor, fsm, deltaTime) {
        const context = fsm.context;

        this.fleeDuration += deltaTime;

        // If health recovered, stop fleeing
        if (actor.health >= actor.fleeThreshold + 20) {
            return 'IDLE';
        }

        // If fled long enough and far from player, stop
        if (this.fleeDuration >= this.maxFleeDuration) {
            return 'IDLE';
        }

        // Run away from player
        if (context && context.player) {
            const dx = actor.x - context.player.x;
            const dy = actor.y - context.player.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance > 0) {
                const speed = actor.speed * 2 * (deltaTime / 1000); // Flee fast!
                actor.x += (dx / distance) * speed;
                actor.y += (dy / distance) * speed;
            }
        }

        return null;
    }

    exit(actor, fsm) {
        this.fleeDuration = 0;
    }
}

// Complete Enemy class using FSM
class FSMEnemy {
    constructor(x, y, name = 'Enemy') {
        this.x = x;
        this.y = y;
        this.name = name;

        this.health = 100;
        this.maxHealth = 100;
        this.speed = 60; // pixels per second
        this.detectionRange = 150;
        this.attackRange = 50;
        this.attackDamage = 10;
        this.fleeThreshold = 30;

        this.patrolPoints = [
            {x: x, y: y},
            {x: x + 100, y: y},
            {x: x + 100, y: y + 100},
            {x: x, y: y + 100}
        ];
        this.currentPatrolIndex = 0;

        this.velocity = {x: 0, y: 0};

        // Create state machine
        this.fsm = new FiniteStateMachine('IDLE');
        this.fsm.addState(new IdleState());
        this.fsm.addState(new PatrolState());
        this.fsm.addState(new ChaseState());
        this.fsm.addState(new AttackState());
        this.fsm.addState(new FleeState());
    }

    update(deltaTime, context) {
        this.fsm.context = context;
        this.fsm.update(this, deltaTime);
    }

    draw(ctx) {
        // Draw enemy with color based on state
        const stateColors = {
            'IDLE': 'gray',
            'PATROL': 'blue',
            'CHASE': 'orange',
            'ATTACK': 'red',
            'FLEE': 'yellow'
        };

        const state = this.fsm.getCurrentStateName();
        ctx.fillStyle = stateColors[state] || 'purple';

        ctx.beginPath();
        ctx.arc(this.x, this.y, 12, 0, Math.PI * 2);
        ctx.fill();

        // Draw health bar
        ctx.fillStyle = 'black';
        ctx.fillRect(this.x - 15, this.y - 20, 30, 4);
        ctx.fillStyle = 'green';
        ctx.fillRect(this.x - 15, this.y - 20, 30 * (this.health / this.maxHealth), 4);

        // Draw state name
        ctx.fillStyle = 'white';
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(state, this.x, this.y - 25);

        // Draw detection range (debug)
        ctx.strokeStyle = 'rgba(255, 255, 0, 0.2)';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.detectionRange, 0, Math.PI * 2);
        ctx.stroke();

        // Draw attack range (debug)
        ctx.strokeStyle = 'rgba(255, 0, 0, 0.3)';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.attackRange, 0, Math.PI * 2);
        ctx.stroke();
    }
}
```

## Hierarchical State Machines

For complex behaviors, nest state machines within states (Hierarchical FSM or HFSM).

```javascript
// Animation State Machine (nested within character states)
class AnimationFSM {
    constructor() {
        this.currentAnimation = 'idle';
        this.states = new Map();
    }

    playAnimation(name, loop = true) {
        if (this.currentAnimation !== name) {
            console.log(`Playing animation: ${name}`);
            this.currentAnimation = name;
            // Trigger actual animation system
        }
    }

    update(deltaTime) {
        // Update current animation
    }
}

// Combat State (contains sub-states for different attack types)
class CombatState extends State {
    constructor() {
        super('COMBAT');

        // Create sub-FSM for combat behaviors
        this.combatFSM = new FiniteStateMachine('MELEE_ATTACK');
        this.combatFSM.addState(new MeleeAttackState());
        this.combatFSM.addState(new RangedAttackState());
        this.combatFSM.addState(new BlockState());
        this.combatFSM.addState(new DodgeState());
    }

    enter(actor, fsm) {
        console.log('Entering combat mode');
        actor.inCombat = true;
    }

    execute(actor, fsm, deltaTime) {
        // Check if should exit combat
        if (!this.isPlayerNearby(actor, fsm.context)) {
            return 'PATROL';
        }

        // Update combat sub-states
        this.combatFSM.update(actor, deltaTime);

        return null;
    }

    isPlayerNearby(actor, context) {
        if (!context || !context.player) return false;

        const dx = context.player.x - actor.x;
        const dy = context.player.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        return distance <= actor.detectionRange;
    }

    exit(actor, fsm) {
        actor.inCombat = false;
    }
}

// Sub-states for combat
class MeleeAttackState extends State {
    constructor() {
        super('MELEE_ATTACK');
        this.attackTime = 0;
        this.attackDuration = 500;
    }

    enter(actor, fsm) {
        this.attackTime = 0;
        console.log('Melee attack!');
    }

    execute(actor, fsm, deltaTime) {
        this.attackTime += deltaTime;

        if (this.attackTime >= this.attackDuration) {
            // Attack complete, decide next action
            if (this.shouldBlock(actor, fsm.context)) {
                return 'BLOCK';
            }
            return 'MELEE_ATTACK'; // Attack again
        }

        return null;
    }

    shouldBlock(actor, context) {
        // Simplified: block randomly
        return Math.random() < 0.3;
    }
}

class RangedAttackState extends State {
    constructor() {
        super('RANGED_ATTACK');
        this.shotsFired = 0;
        this.maxShots = 3;
        this.shotInterval = 300;
        this.timeSinceLastShot = 0;
    }

    enter(actor, fsm) {
        this.shotsFired = 0;
        this.timeSinceLastShot = 0;
        console.log('Ranged attack!');
    }

    execute(actor, fsm, deltaTime) {
        this.timeSinceLastShot += deltaTime;

        if (this.timeSinceLastShot >= this.shotInterval) {
            this.fireProjectile(actor, fsm.context);
            this.shotsFired++;
            this.timeSinceLastShot = 0;
        }

        if (this.shotsFired >= this.maxShots) {
            return 'MELEE_ATTACK';
        }

        return null;
    }

    fireProjectile(actor, context) {
        console.log('Firing projectile!');
        // Create projectile entity
    }
}

class BlockState extends State {
    constructor() {
        super('BLOCK');
        this.blockDuration = 0;
        this.blockTime = 1000;
    }

    enter(actor, fsm) {
        this.blockDuration = 0;
        actor.isBlocking = true;
        console.log('Blocking!');
    }

    execute(actor, fsm, deltaTime) {
        this.blockDuration += deltaTime;

        if (this.blockDuration >= this.blockTime) {
            return 'DODGE';
        }

        return null;
    }

    exit(actor, fsm) {
        actor.isBlocking = false;
    }
}

class DodgeState extends State {
    constructor() {
        super('DODGE');
        this.dodgeTime = 0;
        this.dodgeDuration = 400;
    }

    enter(actor, fsm) {
        this.dodgeTime = 0;
        console.log('Dodging!');

        // Quick movement in random direction
        const angle = Math.random() * Math.PI * 2;
        actor.velocity = {
            x: Math.cos(angle) * 200,
            y: Math.sin(angle) * 200
        };
    }

    execute(actor, fsm, deltaTime) {
        this.dodgeTime += deltaTime;

        // Apply dodge velocity
        actor.x += actor.velocity.x * (deltaTime / 1000);
        actor.y += actor.velocity.y * (deltaTime / 1000);

        if (this.dodgeTime >= this.dodgeDuration) {
            actor.velocity = {x: 0, y: 0};
            return 'MELEE_ATTACK';
        }

        return null;
    }

    exit(actor, fsm) {
        actor.velocity = {x: 0, y: 0};
    }
}
```

## State Transition Diagrams

Visual diagrams help design and communicate FSM logic:

```javascript
class FSMDiagram {
    constructor(fsm) {
        this.fsm = fsm;
        this.transitions = [];
    }

    addTransition(fromState, toState, condition) {
        this.transitions.push({from: fromState, to: toState, condition});
    }

    visualize(ctx, x, y, width, height) {
        // Draw FSM diagram
        const stateNames = Array.from(this.fsm.states.keys());
        const stateCount = stateNames.length;
        const angleStep = (Math.PI * 2) / stateCount;
        const radius = Math.min(width, height) / 3;
        const centerX = x + width / 2;
        const centerY = y + height / 2;

        // Calculate state positions
        const statePositions = new Map();
        stateNames.forEach((name, index) => {
            const angle = index * angleStep - Math.PI / 2;
            statePositions.set(name, {
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius
            });
        });

        // Draw transitions (arrows)
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.lineWidth = 2;

        for (const trans of this.transitions) {
            const fromPos = statePositions.get(trans.from);
            const toPos = statePositions.get(trans.to);

            if (fromPos && toPos) {
                ctx.beginPath();
                ctx.moveTo(fromPos.x, fromPos.y);
                ctx.lineTo(toPos.x, toPos.y);
                ctx.stroke();

                // Draw arrow head
                const dx = toPos.x - fromPos.x;
                const dy = toPos.y - fromPos.y;
                const angle = Math.atan2(dy, dx);

                ctx.save();
                ctx.translate(toPos.x, toPos.y);
                ctx.rotate(angle);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(-10, -5);
                ctx.lineTo(-10, 5);
                ctx.closePath();
                ctx.fill();
                ctx.restore();
            }
        }

        // Draw states (circles)
        for (const [name, pos] of statePositions) {
            const isActive = this.fsm.getCurrentStateName() === name;

            ctx.fillStyle = isActive ? 'yellow' : 'rgba(100, 100, 255, 0.8)';
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, 30, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = isActive ? 'red' : 'white';
            ctx.lineWidth = isActive ? 3 : 1;
            ctx.stroke();

            // Draw state name
            ctx.fillStyle = 'black';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(name, pos.x, pos.y);
        }
    }

    exportDiagram() {
        // Export as text diagram
        let diagram = 'State Machine Diagram:\n\n';

        for (const trans of this.transitions) {
            diagram += `${trans.from} --> ${trans.to} [${trans.condition}]\n`;
        }

        return diagram;
    }
}
```

## FSM Debugging and Visualization

Debug tools make FSM behavior visible:

```javascript
class FSMDebugger {
    constructor(fsm, actor) {
        this.fsm = fsm;
        this.actor = actor;
        this.history = [];
        this.maxHistory = 50;
    }

    update(deltaTime) {
        const currentState = this.fsm.getCurrentStateName();
        const timestamp = Date.now();

        // Record state changes
        if (this.history.length === 0 ||
            this.history[this.history.length - 1].state !== currentState) {

            this.history.push({
                state: currentState,
                timestamp: timestamp,
                actorData: {
                    x: this.actor.x,
                    y: this.actor.y,
                    health: this.actor.health
                }
            });

            // Limit history size
            if (this.history.length > this.maxHistory) {
                this.history.shift();
            }

            console.log(`[FSM] ${this.actor.name} transitioned to ${currentState}`);
        }
    }

    visualize(ctx, x, y, width, height) {
        // Draw debug panel
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(x, y, width, height);

        ctx.fillStyle = 'white';
        ctx.font = '14px monospace';
        ctx.textAlign = 'left';

        // Current state
        const currentState = this.fsm.getCurrentStateName();
        ctx.fillText(`Current State: ${currentState}`, x + 10, y + 20);

        // State history
        ctx.font = '12px monospace';
        ctx.fillText('State History:', x + 10, y + 45);

        let yPos = y + 60;
        const recentHistory = this.history.slice(-10);

        for (let i = recentHistory.length - 1; i >= 0; i--) {
            const entry = recentHistory[i];
            const duration = i < recentHistory.length - 1 ?
                recentHistory[i + 1].timestamp - entry.timestamp :
                Date.now() - entry.timestamp;

            ctx.fillStyle = i === recentHistory.length - 1 ? 'yellow' : 'white';
            ctx.fillText(
                `${entry.state} (${(duration / 1000).toFixed(1)}s)`,
                x + 15,
                yPos
            );

            yPos += 15;
            if (yPos > y + height - 10) break;
        }
    }

    printHistory() {
        console.log('FSM State History:');

        for (let i = 0; i < this.history.length; i++) {
            const entry = this.history[i];
            const duration = i < this.history.length - 1 ?
                this.history[i + 1].timestamp - entry.timestamp :
                'ongoing';

            console.log(`${entry.state}: ${duration}ms at (${entry.actorData.x}, ${entry.actorData.y})`);
        }
    }

    getStateDurations() {
        const durations = new Map();

        for (let i = 0; i < this.history.length - 1; i++) {
            const entry = this.history[i];
            const duration = this.history[i + 1].timestamp - entry.timestamp;

            if (!durations.has(entry.state)) {
                durations.set(entry.state, {total: 0, count: 0});
            }

            const data = durations.get(entry.state);
            data.total += duration;
            data.count++;
        }

        // Calculate averages
        const result = new Map();
        for (const [state, data] of durations) {
            result.set(state, {
                average: data.total / data.count,
                total: data.total,
                count: data.count
            });
        }

        return result;
    }
}
```

## Advanced FSM Patterns

### State Stack (Pushdown Automaton)

Allow states to be pushed and popped, useful for interruptions:

```javascript
class StateStack {
    constructor() {
        this.stack = [];
    }

    push(state, actor) {
        // Pause current state
        if (this.stack.length > 0) {
            const current = this.stack[this.stack.length - 1];
            if (current.pause) {
                current.pause(actor);
            }
        }

        // Enter new state
        this.stack.push(state);
        state.enter(actor, this);
    }

    pop(actor) {
        if (this.stack.length === 0) return;

        // Exit current state
        const current = this.stack.pop();
        current.exit(actor, this);

        // Resume previous state
        if (this.stack.length > 0) {
            const previous = this.stack[this.stack.length - 1];
            if (previous.resume) {
                previous.resume(actor, this);
            }
        }
    }

    update(actor, deltaTime) {
        if (this.stack.length === 0) return;

        const current = this.stack[this.stack.length - 1];
        const shouldPop = current.execute(actor, this, deltaTime);

        if (shouldPop) {
            this.pop(actor);
        }
    }

    getCurrent() {
        return this.stack[this.stack.length - 1];
    }
}

// Example: Interruptible states
class InterruptiblePatrolState extends State {
    constructor() {
        super('PATROL');
        this.savedPosition = null;
    }

    pause(actor) {
        // Save position for resuming later
        this.savedPosition = {x: actor.x, y: actor.y};
        console.log('Patrol paused');
    }

    resume(actor, stack) {
        console.log('Patrol resumed');
        // Could restore position or continue from current location
    }

    execute(actor, stack, deltaTime) {
        // Patrol logic...

        // If hear a noise, investigate (push investigation state)
        if (this.heardNoise(actor, stack.context)) {
            const investigateState = new InvestigateState();
            stack.push(investigateState, actor);
            return false; // Don't pop, just push new state
        }

        return false; // null means stay in this state
    }

    heardNoise(actor, context) {
        // Simplified noise detection
        return Math.random() < 0.01;
    }
}

class InvestigateState extends State {
    constructor() {
        super('INVESTIGATE');
        this.investigateTime = 0;
        this.maxInvestigateTime = 3000;
    }

    enter(actor, stack) {
        console.log('Investigating noise...');
        this.investigateTime = 0;
    }

    execute(actor, stack, deltaTime) {
        this.investigateTime += deltaTime;

        // Look around, move to noise source, etc.

        // After investigating, return to previous state (pop)
        if (this.investigateTime >= this.maxInvestigateTime) {
            console.log('Investigation complete');
            return true; // Pop this state
        }

        return false;
    }
}
```

## Complete Game Example

Let's tie it all together:

```javascript
class FSMGame {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        this.player = {
            x: 400,
            y: 300,
            health: 100
        };

        this.enemies = [
            new FSMEnemy(100, 100, 'Guard 1'),
            new FSMEnemy(600, 400, 'Guard 2'),
            new FSMEnemy(350, 150, 'Guard 3')
        ];

        // Create debuggers
        this.debuggers = this.enemies.map(enemy =>
            new FSMDebugger(enemy.fsm, enemy)
        );

        this.lastTime = Date.now();
    }

    update() {
        const now = Date.now();
        const deltaTime = now - this.lastTime;
        this.lastTime = now;

        const context = {
            player: this.player
        };

        // Update enemies
        for (let i = 0; i < this.enemies.length; i++) {
            this.enemies[i].update(deltaTime, context);
            this.debuggers[i].update(deltaTime);
        }
    }

    draw() {
        // Clear screen
        this.ctx.fillStyle = '#1a1a1a';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw player
        this.ctx.fillStyle = 'cyan';
        this.ctx.beginPath();
        this.ctx.arc(this.player.x, this.player.y, 15, 0, Math.PI * 2);
        this.ctx.fill();

        // Draw enemies
        for (const enemy of this.enemies) {
            enemy.draw(this.ctx);
        }

        // Draw debug info
        this.debuggers[0].visualize(this.ctx, 10, 10, 300, 200);
    }

    run() {
        const gameLoop = () => {
            this.update();
            this.draw();
            requestAnimationFrame(gameLoop);
        };

        requestAnimationFrame(gameLoop);
    }

    handleMouseMove(event) {
        const rect = this.canvas.getBoundingClientRect();
        this.player.x = event.clientX - rect.left;
        this.player.y = event.clientY - rect.top;
    }
}

// Initialize game
const canvas = document.getElementById('gameCanvas');
const game = new FSMGame(canvas);

canvas.addEventListener('mousemove', (e) => game.handleMouseMove(e));

game.run();
```

## Claude Code Prompts for FSMs

**Basic Enemy AI:**
```
"Create a finite state machine for an enemy with idle, patrol, chase, and attack states with smooth transitions"
```

**Hierarchical FSM:**
```
"Implement a hierarchical FSM where the combat state contains sub-states for melee attack, ranged attack, and blocking"
```

**State Visualization:**
```
"Add visual debugging to this FSM that shows the current state and recent state history on screen"
```

**Complex Transitions:**
```
"Add state transitions that consider multiple conditions like player distance, health percentage, and time of day"
```

**Animation Integration:**
```
"Connect this character FSM to an animation system so each state plays appropriate animations"
```

## FSM vs Behavior Trees Comparison

| Aspect | FSMs | Behavior Trees |
|--------|------|----------------|
| Complexity | Best for 3-7 states | Scales to 20+ behaviors |
| Readability | Very clear for simple AI | Better for complex AI |
| Modularity | States can be reused | Highly modular subtrees |
| Design | One state at a time | Hierarchical priorities |
| Performance | Slightly faster | Minimal overhead |
| Debugging | Clear current state | Shows execution path |
| Designer-friendly | With tools, yes | More accessible |
| Transitions | Explicit n-to-n | Implicit via priority |

**Use FSMs when:**
- AI is simple (few states)
- Transitions are well-defined
- Current state is important (animations)
- You need maximum clarity

**Use Behavior Trees when:**
- AI is complex (many actions)
- Priority-based decisions
- High modularity needed
- Designer authoring required

## Performance Considerations

FSMs are naturally efficient:
- **O(1) state updates** - just execute current state
- **No memory allocation** - states can be pre-created
- **Minimal overhead** - simple state machine logic

Optimizations:
- Cache frequently-accessed context data
- Use state pooling for dynamic state creation
- Avoid expensive calculations in transition checks
- Update distant FSMs less frequently (LOD)

## Related Documentation

- [Behavior Trees](./behavior-trees.md) - More flexible alternative for complex AI
- [Pathfinding Algorithms](./pathfinding-algorithms.md) - Movement for chase/patrol states
- [NPC Behaviors](./npc-behaviors.md) - Steering behaviors within states
- [Animation Systems](../02-core-game-concepts/animation-systems.md) - Integrating FSMs with animations

Finite State Machines are the foundation of game AI. They're simple, clear, and powerful enough for most enemy behaviors. Master FSMs, and you'll have the tools to create compelling AI for the majority of game scenarios!
