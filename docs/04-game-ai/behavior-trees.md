# Behavior Trees

## Introduction

Behavior Trees are the modern standard for game AI decision-making. From AAA titles like Halo and Uncharted to indie games, behavior trees have become the go-to architecture for creating complex, maintainable AI behaviors. They provide a hierarchical, modular structure that's both powerful enough for sophisticated AI and intuitive enough to be edited by designers without programming experience.

Unlike Finite State Machines that become unwieldy with many states, behavior trees scale gracefully. They separate decision logic from execution, making behaviors composable and reusable. A "take cover" behavior can be used by soldiers, civilians, and robots without duplication. A "find health" behavior works for any entity that needs healing.

This guide covers behavior tree fundamentals, complete implementation, practical examples for enemies and NPCs, integration with game systems, and debugging techniques to make your AI understandable and maintainable.

## Behavior Tree Fundamentals

A behavior tree is a directed tree structure where:

- **Root**: The starting point, ticked every frame
- **Nodes**: Individual units that return Success, Failure, or Running status
- **Leaves**: Action and Condition nodes that do actual work
- **Composites**: Control flow nodes that manage child execution

### Node Types

**Composite Nodes** control flow through their children:

- **Sequence**: Executes children left-to-right until one fails. Returns Success only if all children succeed. Like AND logic.
- **Selector**: Executes children left-to-right until one succeeds. Returns Failure only if all children fail. Like OR logic.
- **Parallel**: Executes all children simultaneously. Policies determine when it succeeds/fails.

**Decorator Nodes** modify behavior of their single child:

- **Inverter**: Flips Success to Failure and vice versa
- **Repeater**: Repeats child N times or until it fails
- **Succeeder**: Always returns Success regardless of child result
- **UntilFail**: Repeats child until it fails, then returns Success

**Leaf Nodes** perform actual work:

- **Action**: Performs game action (move, attack, play animation)
- **Condition**: Checks game state (is player visible? health below 50%?)

### Status Values

Every node returns one of three statuses:

- **Success**: Node completed successfully
- **Failure**: Node failed to complete
- **Running**: Node is still executing (will continue next tick)

## Complete Behavior Tree Implementation

```javascript
// Base node class
class BehaviorNode {
    constructor(name = 'Unnamed') {
        this.name = name;
        this.status = 'ready';
    }

    tick(actor, context) {
        // Override in subclasses
        return 'failure';
    }

    reset() {
        this.status = 'ready';
    }
}

// Composite Nodes

class Sequence extends BehaviorNode {
    constructor(name, children = []) {
        super(name);
        this.children = children;
        this.currentChildIndex = 0;
    }

    tick(actor, context) {
        while (this.currentChildIndex < this.children.length) {
            const child = this.children[this.currentChildIndex];
            const status = child.tick(actor, context);

            if (status === 'running') {
                return 'running';
            }

            if (status === 'failure') {
                this.reset();
                return 'failure';
            }

            // Child succeeded, move to next
            this.currentChildIndex++;
        }

        // All children succeeded
        this.reset();
        return 'success';
    }

    reset() {
        this.currentChildIndex = 0;
        for (const child of this.children) {
            child.reset();
        }
    }
}

class Selector extends BehaviorNode {
    constructor(name, children = []) {
        super(name);
        this.children = children;
        this.currentChildIndex = 0;
    }

    tick(actor, context) {
        while (this.currentChildIndex < this.children.length) {
            const child = this.children[this.currentChildIndex];
            const status = child.tick(actor, context);

            if (status === 'running') {
                return 'running';
            }

            if (status === 'success') {
                this.reset();
                return 'success';
            }

            // Child failed, try next
            this.currentChildIndex++;
        }

        // All children failed
        this.reset();
        return 'failure';
    }

    reset() {
        this.currentChildIndex = 0;
        for (const child of this.children) {
            child.reset();
        }
    }
}

class Parallel extends BehaviorNode {
    constructor(name, children = [], successPolicy = 'requireAll', failurePolicy = 'requireOne') {
        super(name);
        this.children = children;
        this.successPolicy = successPolicy; // 'requireAll' or 'requireOne'
        this.failurePolicy = failurePolicy; // 'requireAll' or 'requireOne'
    }

    tick(actor, context) {
        let successCount = 0;
        let failureCount = 0;
        let runningCount = 0;

        for (const child of this.children) {
            const status = child.tick(actor, context);

            if (status === 'success') successCount++;
            else if (status === 'failure') failureCount++;
            else if (status === 'running') runningCount++;
        }

        // Check failure policy
        if (this.failurePolicy === 'requireOne' && failureCount > 0) {
            this.reset();
            return 'failure';
        }

        if (this.failurePolicy === 'requireAll' && failureCount === this.children.length) {
            this.reset();
            return 'failure';
        }

        // Check success policy
        if (this.successPolicy === 'requireAll' && successCount === this.children.length) {
            this.reset();
            return 'success';
        }

        if (this.successPolicy === 'requireOne' && successCount > 0) {
            this.reset();
            return 'success';
        }

        return 'running';
    }

    reset() {
        for (const child of this.children) {
            child.reset();
        }
    }
}

// Decorator Nodes

class Inverter extends BehaviorNode {
    constructor(name, child) {
        super(name);
        this.child = child;
    }

    tick(actor, context) {
        const status = this.child.tick(actor, context);

        if (status === 'success') return 'failure';
        if (status === 'failure') return 'success';
        return 'running';
    }

    reset() {
        this.child.reset();
    }
}

class Repeater extends BehaviorNode {
    constructor(name, child, count = Infinity) {
        super(name);
        this.child = child;
        this.count = count;
        this.currentCount = 0;
    }

    tick(actor, context) {
        if (this.currentCount >= this.count) {
            this.reset();
            return 'success';
        }

        const status = this.child.tick(actor, context);

        if (status === 'success' || status === 'failure') {
            this.currentCount++;
            this.child.reset();

            if (this.currentCount >= this.count) {
                this.reset();
                return 'success';
            }
        }

        return 'running';
    }

    reset() {
        this.currentCount = 0;
        this.child.reset();
    }
}

class Succeeder extends BehaviorNode {
    constructor(name, child) {
        super(name);
        this.child = child;
    }

    tick(actor, context) {
        this.child.tick(actor, context);
        return 'success';
    }

    reset() {
        this.child.reset();
    }
}

class UntilFail extends BehaviorNode {
    constructor(name, child) {
        super(name);
        this.child = child;
    }

    tick(actor, context) {
        const status = this.child.tick(actor, context);

        if (status === 'failure') {
            this.reset();
            return 'success';
        }

        if (status === 'success') {
            this.child.reset();
        }

        return 'running';
    }

    reset() {
        this.child.reset();
    }
}

// Leaf Nodes - Actions and Conditions

class Action extends BehaviorNode {
    constructor(name, actionFunction) {
        super(name);
        this.actionFunction = actionFunction;
        this.isRunning = false;
    }

    tick(actor, context) {
        if (!this.isRunning) {
            this.isRunning = true;
        }

        const result = this.actionFunction(actor, context);

        if (result === 'running') {
            return 'running';
        }

        this.reset();
        return result;
    }

    reset() {
        this.isRunning = false;
    }
}

class Condition extends BehaviorNode {
    constructor(name, conditionFunction) {
        super(name);
        this.conditionFunction = conditionFunction;
    }

    tick(actor, context) {
        const result = this.conditionFunction(actor, context);
        return result ? 'success' : 'failure';
    }
}

// Behavior Tree Manager

class BehaviorTree {
    constructor(rootNode) {
        this.root = rootNode;
    }

    tick(actor, context = {}) {
        return this.root.tick(actor, context);
    }

    reset() {
        this.root.reset();
    }

    // Visual representation for debugging
    toString(node = this.root, indent = 0) {
        const spaces = '  '.repeat(indent);
        let result = `${spaces}${node.constructor.name}: ${node.name}\n`;

        if (node.children) {
            for (const child of node.children) {
                result += this.toString(child, indent + 1);
            }
        } else if (node.child) {
            result += this.toString(node.child, indent + 1);
        }

        return result;
    }
}
```

## Enemy AI Example: Patrol, Chase, Attack, Retreat

Let's build a complete enemy AI that patrols, chases the player when detected, attacks when in range, and retreats when health is low.

```javascript
class Enemy {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.health = 100;
        this.maxHealth = 100;
        this.speed = 2;
        this.detectionRange = 150;
        this.attackRange = 50;
        this.retreatThreshold = 30;

        this.patrolPoints = [
            {x: 100, y: 100},
            {x: 300, y: 100},
            {x: 300, y: 300},
            {x: 100, y: 300}
        ];
        this.currentPatrolIndex = 0;

        this.target = null;
        this.lastAttackTime = 0;
        this.attackCooldown = 1000; // ms

        // Create behavior tree
        this.behaviorTree = this.createBehaviorTree();
    }

    createBehaviorTree() {
        // Root selector: try behaviors in priority order
        const root = new Selector('Root', [
            // Priority 1: Retreat if health is low
            new Sequence('Retreat Sequence', [
                new Condition('Health Low?', (actor) => actor.health < actor.retreatThreshold),
                new Action('Retreat', (actor, context) => {
                    return this.retreat(actor, context);
                })
            ]),

            // Priority 2: Combat if player is detected
            new Sequence('Combat Sequence', [
                new Condition('Player Detected?', (actor, context) => {
                    return this.detectPlayer(actor, context);
                }),

                // Try to attack, fall back to chase if not in range
                new Selector('Combat Actions', [
                    // Try to attack first
                    new Sequence('Attack Sequence', [
                        new Condition('In Attack Range?', (actor, context) => {
                            return this.inAttackRange(actor, context);
                        }),
                        new Condition('Attack Ready?', (actor) => {
                            return Date.now() - actor.lastAttackTime > actor.attackCooldown;
                        }),
                        new Action('Attack', (actor, context) => {
                            return this.attack(actor, context);
                        })
                    ]),

                    // If can't attack, chase
                    new Action('Chase Player', (actor, context) => {
                        return this.chasePlayer(actor, context);
                    })
                ])
            ]),

            // Priority 3: Patrol if nothing else to do
            new Action('Patrol', (actor, context) => {
                return this.patrol(actor, context);
            })
        ]);

        return new BehaviorTree(root);
    }

    // Behavior implementations

    detectPlayer(actor, context) {
        if (!context.player) return false;

        const dx = context.player.x - actor.x;
        const dy = context.player.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance <= actor.detectionRange) {
            actor.target = context.player;
            return true;
        }

        return false;
    }

    inAttackRange(actor, context) {
        if (!actor.target) return false;

        const dx = actor.target.x - actor.x;
        const dy = actor.target.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        return distance <= actor.attackRange;
    }

    attack(actor, context) {
        if (!actor.target) return 'failure';

        // Perform attack
        console.log('Enemy attacks!');
        actor.lastAttackTime = Date.now();

        // Deal damage to player
        if (context.player && context.player.health) {
            context.player.health -= 10;
        }

        return 'success';
    }

    chasePlayer(actor, context) {
        if (!actor.target) return 'failure';

        const dx = actor.target.x - actor.x;
        const dy = actor.target.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 0) {
            actor.x += (dx / distance) * actor.speed;
            actor.y += (dy / distance) * actor.speed;
        }

        return 'running';
    }

    retreat(actor, context) {
        if (!actor.target && !context.player) return 'failure';

        const threat = actor.target || context.player;

        // Move away from threat
        const dx = actor.x - threat.x;
        const dy = actor.y - threat.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 0) {
            actor.x += (dx / distance) * actor.speed * 1.5; // Retreat faster
            actor.y += (dy / distance) * actor.speed * 1.5;
        }

        // Keep retreating
        return 'running';
    }

    patrol(actor, context) {
        const target = actor.patrolPoints[actor.currentPatrolIndex];

        const dx = target.x - actor.x;
        const dy = target.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 5) {
            // Reached patrol point, move to next
            actor.currentPatrolIndex = (actor.currentPatrolIndex + 1) % actor.patrolPoints.length;
            return 'success';
        }

        // Move toward patrol point
        actor.x += (dx / distance) * actor.speed;
        actor.y += (dy / distance) * actor.speed;

        return 'running';
    }

    update(context) {
        this.behaviorTree.tick(this, context);
    }

    draw(ctx) {
        // Draw enemy
        ctx.fillStyle = this.health < this.retreatThreshold ? 'orange' : 'red';
        ctx.beginPath();
        ctx.arc(this.x, this.y, 10, 0, Math.PI * 2);
        ctx.fill();

        // Draw health bar
        ctx.fillStyle = 'black';
        ctx.fillRect(this.x - 15, this.y - 20, 30, 4);
        ctx.fillStyle = 'green';
        ctx.fillRect(this.x - 15, this.y - 20, 30 * (this.health / this.maxHealth), 4);

        // Draw detection range (debug)
        ctx.strokeStyle = 'rgba(255, 0, 0, 0.2)';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.detectionRange, 0, Math.PI * 2);
        ctx.stroke();
    }
}
```

## Boss AI Example: Complex Multi-Phase Behavior

Boss enemies need sophisticated AI with multiple phases and attack patterns.

```javascript
class BossEnemy {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.health = 500;
        this.maxHealth = 500;
        this.speed = 1.5;

        this.phase = 1;
        this.isVulnerable = false;
        this.attackPattern = 0;
        this.lastSpecialAttackTime = 0;
        this.summonedMinions = [];

        this.behaviorTree = this.createBehaviorTree();
    }

    createBehaviorTree() {
        const root = new Selector('Boss Root', [
            // Phase 3: Enraged (below 25% health)
            new Sequence('Phase 3', [
                new Condition('Health Below 25%', (actor) => actor.health / actor.maxHealth < 0.25),
                new Action('Set Phase 3', (actor) => {
                    if (actor.phase !== 3) {
                        actor.phase = 3;
                        console.log('Boss enters Phase 3: Enraged!');
                    }
                    return 'success';
                }),

                new Selector('Phase 3 Actions', [
                    // Berserker mode: rapid attacks
                    new Sequence('Berserker Attack', [
                        new Condition('Player Nearby', (actor, context) => {
                            return this.playerDistance(actor, context) < 100;
                        }),
                        new Action('Rapid Attack', (actor, context) => {
                            return this.rapidAttack(actor, context);
                        })
                    ]),

                    // Summon minions for help
                    new Sequence('Desperate Summon', [
                        new Condition('Few Minions', (actor) => actor.summonedMinions.length < 3),
                        new Action('Summon Minions', (actor, context) => {
                            return this.summonMinions(actor, context);
                        })
                    ]),

                    // Default: aggressive chase
                    new Action('Aggressive Chase', (actor, context) => {
                        return this.aggressiveChase(actor, context);
                    })
                ])
            ]),

            // Phase 2: Tactical (25-60% health)
            new Sequence('Phase 2', [
                new Condition('Health Below 60%', (actor) => actor.health / actor.maxHealth < 0.6),
                new Action('Set Phase 2', (actor) => {
                    if (actor.phase !== 2) {
                        actor.phase = 2;
                        console.log('Boss enters Phase 2: Tactical!');
                    }
                    return 'success';
                }),

                new Selector('Phase 2 Actions', [
                    // Special attack pattern
                    new Sequence('Special Attack Pattern', [
                        new Condition('Special Attack Ready', (actor) => {
                            return Date.now() - actor.lastSpecialAttackTime > 5000;
                        }),
                        new Action('Area Attack', (actor, context) => {
                            return this.areaAttack(actor, context);
                        })
                    ]),

                    // Teleport away if player too close
                    new Sequence('Tactical Teleport', [
                        new Condition('Player Too Close', (actor, context) => {
                            return this.playerDistance(actor, context) < 50;
                        }),
                        new Action('Teleport', (actor, context) => {
                            return this.teleport(actor, context);
                        })
                    ]),

                    // Projectile attacks
                    new Action('Shoot Projectiles', (actor, context) => {
                        return this.shootProjectiles(actor, context);
                    })
                ])
            ]),

            // Phase 1: Standard (60-100% health)
            new Sequence('Phase 1', [
                new Action('Set Phase 1', (actor) => {
                    if (actor.phase !== 1) {
                        actor.phase = 1;
                    }
                    return 'success';
                }),

                new Selector('Phase 1 Actions', [
                    // Charge attack when far
                    new Sequence('Charge Attack', [
                        new Condition('Player Far', (actor, context) => {
                            return this.playerDistance(actor, context) > 150;
                        }),
                        new Action('Charge', (actor, context) => {
                            return this.chargeAttack(actor, context);
                        })
                    ]),

                    // Melee attack when close
                    new Sequence('Melee Attack', [
                        new Condition('Player Close', (actor, context) => {
                            return this.playerDistance(actor, context) < 60;
                        }),
                        new Action('Melee', (actor, context) => {
                            return this.meleeAttack(actor, context);
                        })
                    ]),

                    // Default: circle player
                    new Action('Circle Player', (actor, context) => {
                        return this.circlePlayer(actor, context);
                    })
                ])
            ])
        ]);

        return new BehaviorTree(root);
    }

    // Helper functions

    playerDistance(actor, context) {
        if (!context.player) return Infinity;
        const dx = context.player.x - actor.x;
        const dy = context.player.y - actor.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    // Attack implementations

    rapidAttack(actor, context) {
        console.log('Boss: Rapid Attack!');
        // Implementation: fast succession of attacks
        return 'success';
    }

    summonMinions(actor, context) {
        console.log('Boss: Summoning minions!');
        // Create minion entities
        for (let i = 0; i < 3; i++) {
            const angle = (Math.PI * 2 / 3) * i;
            const minion = {
                x: actor.x + Math.cos(angle) * 50,
                y: actor.y + Math.sin(angle) * 50
            };
            actor.summonedMinions.push(minion);
        }
        return 'success';
    }

    aggressiveChase(actor, context) {
        if (!context.player) return 'failure';

        const dx = context.player.x - actor.x;
        const dy = context.player.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 0) {
            actor.x += (dx / distance) * actor.speed * 2; // Double speed in phase 3
            actor.y += (dy / distance) * actor.speed * 2;
        }

        return 'running';
    }

    areaAttack(actor, context) {
        console.log('Boss: Area Attack!');
        actor.lastSpecialAttackTime = Date.now();
        // Implementation: damage in radius around boss
        return 'success';
    }

    teleport(actor, context) {
        // Teleport to random location
        actor.x = Math.random() * 600 + 100;
        actor.y = Math.random() * 400 + 100;
        console.log('Boss: Teleport!');
        return 'success';
    }

    shootProjectiles(actor, context) {
        console.log('Boss: Shooting projectiles!');
        // Implementation: create projectile entities
        return 'success';
    }

    chargeAttack(actor, context) {
        if (!context.player) return 'failure';

        // Charge toward player at high speed
        const dx = context.player.x - actor.x;
        const dy = context.player.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 0) {
            actor.x += (dx / distance) * actor.speed * 3;
            actor.y += (dy / distance) * actor.speed * 3;
        }

        return 'running';
    }

    meleeAttack(actor, context) {
        console.log('Boss: Melee Attack!');
        // Implementation: damage player if in range
        return 'success';
    }

    circlePlayer(actor, context) {
        if (!context.player) return 'failure';

        // Circle around player at constant distance
        const dx = context.player.x - actor.x;
        const dy = context.player.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        const targetDistance = 120;
        const angleIncrement = 0.02;

        // Move tangent to circle
        const tangentX = -dy / distance;
        const tangentY = dx / distance;

        actor.x += tangentX * actor.speed;
        actor.y += tangentY * actor.speed;

        // Maintain distance
        if (distance < targetDistance - 10) {
            actor.x -= (dx / distance) * actor.speed;
            actor.y -= (dy / distance) * actor.speed;
        } else if (distance > targetDistance + 10) {
            actor.x += (dx / distance) * actor.speed;
            actor.y += (dy / distance) * actor.speed;
        }

        return 'running';
    }

    update(context) {
        this.behaviorTree.tick(this, context);
    }

    draw(ctx) {
        // Draw boss with phase-specific color
        const colors = ['blue', 'yellow', 'red'];
        ctx.fillStyle = colors[this.phase - 1];
        ctx.beginPath();
        ctx.arc(this.x, this.y, 20, 0, Math.PI * 2);
        ctx.fill();

        // Draw health bar
        ctx.fillStyle = 'black';
        ctx.fillRect(this.x - 30, this.y - 35, 60, 6);
        ctx.fillStyle = 'green';
        ctx.fillRect(this.x - 30, this.y - 35, 60 * (this.health / this.maxHealth), 6);

        // Draw phase indicator
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`Phase ${this.phase}`, this.x, this.y - 40);
    }
}
```

## NPC AI Example: Realistic Civilian Behavior

NPCs need to feel alive with daily routines and reactions to events.

```javascript
class CivilianNPC {
    constructor(x, y, name) {
        this.x = x;
        this.y = y;
        this.name = name;
        this.speed = 1;

        this.home = {x: x, y: y};
        this.workplace = {x: x + 200, y: y - 100};
        this.hunger = 0;
        this.energy = 100;
        this.fearLevel = 0;

        this.currentActivity = 'idle';

        this.behaviorTree = this.createBehaviorTree();
    }

    createBehaviorTree() {
        const root = new Selector('NPC Root', [
            // Priority 1: Safety - flee from danger
            new Sequence('Flee from Danger', [
                new Condition('Danger Detected?', (actor, context) => {
                    return actor.fearLevel > 50 || this.detectDanger(actor, context);
                }),
                new Action('Flee', (actor, context) => {
                    return this.flee(actor, context);
                })
            ]),

            // Priority 2: Basic needs
            new Selector('Basic Needs', [
                // Sleep if very tired
                new Sequence('Sleep', [
                    new Condition('Very Tired?', (actor) => actor.energy < 20),
                    new Action('Go to Bed', (actor, context) => {
                        return this.sleep(actor, context);
                    })
                ]),

                // Eat if very hungry
                new Sequence('Eat', [
                    new Condition('Very Hungry?', (actor) => actor.hunger > 80),
                    new Action('Find Food', (actor, context) => {
                        return this.eat(actor, context);
                    })
                ])
            ]),

            // Priority 3: Daily routine based on time
            new Selector('Daily Routine', [
                // Work during work hours
                new Sequence('Work', [
                    new Condition('Work Hours?', (actor, context) => {
                        const hour = context.gameTime ? context.gameTime.hour : 9;
                        return hour >= 9 && hour < 17;
                    }),
                    new Action('Go to Work', (actor, context) => {
                        return this.work(actor, context);
                    })
                ]),

                // Evening activities
                new Sequence('Evening', [
                    new Condition('Evening?', (actor, context) => {
                        const hour = context.gameTime ? context.gameTime.hour : 18;
                        return hour >= 17 && hour < 22;
                    }),
                    new Selector('Evening Activities', [
                        new Action('Socialize', (actor, context) => {
                            return this.socialize(actor, context);
                        }),
                        new Action('Recreation', (actor, context) => {
                            return this.recreation(actor, context);
                        })
                    ])
                ]),

                // Night - go home and rest
                new Sequence('Night', [
                    new Condition('Night?', (actor, context) => {
                        const hour = context.gameTime ? context.gameTime.hour : 22;
                        return hour >= 22 || hour < 6;
                    }),
                    new Action('Go Home', (actor, context) => {
                        return this.goHome(actor, context);
                    })
                ])
            ]),

            // Default: idle behavior
            new Action('Idle', (actor, context) => {
                return this.idle(actor, context);
            })
        ]);

        return new BehaviorTree(root);
    }

    // Behavior implementations

    detectDanger(actor, context) {
        // Check for nearby threats
        if (context.threats) {
            for (const threat of context.threats) {
                const dx = threat.x - actor.x;
                const dy = threat.y - actor.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 100) {
                    actor.fearLevel = 100;
                    return true;
                }
            }
        }

        actor.fearLevel = Math.max(0, actor.fearLevel - 1);
        return false;
    }

    flee(actor, context) {
        actor.currentActivity = 'fleeing';

        // Find nearest safe location (home or away from threats)
        const safeSpot = actor.home;

        const dx = safeSpot.x - actor.x;
        const dy = safeSpot.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 10) {
            actor.fearLevel = 0;
            return 'success';
        }

        // Run toward safety
        actor.x += (dx / distance) * actor.speed * 2;
        actor.y += (dy / distance) * actor.speed * 2;

        return 'running';
    }

    sleep(actor, context) {
        actor.currentActivity = 'sleeping';

        // Move to bed
        const dx = actor.home.x - actor.x;
        const dy = actor.home.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 5) {
            actor.x += (dx / distance) * actor.speed;
            actor.y += (dy / distance) * actor.speed;
            return 'running';
        }

        // Restore energy
        actor.energy = Math.min(100, actor.energy + 2);

        if (actor.energy >= 100) {
            return 'success';
        }

        return 'running';
    }

    eat(actor, context) {
        actor.currentActivity = 'eating';

        // Reduce hunger
        actor.hunger = Math.max(0, actor.hunger - 5);

        if (actor.hunger <= 20) {
            return 'success';
        }

        return 'running';
    }

    work(actor, context) {
        actor.currentActivity = 'working';

        // Move to workplace
        const dx = actor.workplace.x - actor.x;
        const dy = actor.workplace.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 5) {
            actor.x += (dx / distance) * actor.speed;
            actor.y += (dy / distance) * actor.speed;
            return 'running';
        }

        // Work consumes energy and increases hunger
        actor.energy = Math.max(0, actor.energy - 0.1);
        actor.hunger = Math.min(100, actor.hunger + 0.2);

        return 'running';
    }

    socialize(actor, context) {
        actor.currentActivity = 'socializing';
        // Find other NPCs and move toward them
        return Math.random() > 0.01 ? 'running' : 'success';
    }

    recreation(actor, context) {
        actor.currentActivity = 'recreation';
        // Wander around for fun
        return Math.random() > 0.01 ? 'running' : 'success';
    }

    goHome(actor, context) {
        actor.currentActivity = 'going home';

        const dx = actor.home.x - actor.x;
        const dy = actor.home.y - actor.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 5) {
            return 'success';
        }

        actor.x += (dx / distance) * actor.speed;
        actor.y += (dy / distance) * actor.speed;

        return 'running';
    }

    idle(actor, context) {
        actor.currentActivity = 'idle';
        // Slowly increase hunger and decrease energy
        actor.hunger = Math.min(100, actor.hunger + 0.05);
        actor.energy = Math.max(0, actor.energy - 0.05);
        return 'running';
    }

    update(context) {
        this.behaviorTree.tick(this, context);
    }

    draw(ctx) {
        ctx.fillStyle = 'green';
        ctx.beginPath();
        ctx.arc(this.x, this.y, 8, 0, Math.PI * 2);
        ctx.fill();

        // Draw activity label
        ctx.fillStyle = 'black';
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(this.currentActivity, this.x, this.y - 15);

        // Draw status bars
        // Energy (blue)
        ctx.fillStyle = 'rgba(0, 100, 255, 0.5)';
        ctx.fillRect(this.x - 10, this.y + 10, 20 * (this.energy / 100), 2);

        // Hunger (orange)
        ctx.fillStyle = 'rgba(255, 150, 0, 0.5)';
        ctx.fillRect(this.x - 10, this.y + 13, 20 * (this.hunger / 100), 2);
    }
}
```

## Debugging Behavior Trees

Visual debugging is essential for understanding AI behavior:

```javascript
class BehaviorTreeDebugger {
    constructor(behaviorTree, actor) {
        this.tree = behaviorTree;
        this.actor = actor;
        this.executionHistory = [];
        this.maxHistoryLength = 100;
    }

    tickWithDebug(context) {
        const tickData = {
            timestamp: Date.now(),
            nodes: []
        };

        // Wrap tick to record execution
        const originalTick = this.tree.root.tick.bind(this.tree.root);
        this.tree.root.tick = (actor, ctx) => {
            const result = this.recordNodeExecution(this.tree.root, actor, ctx, tickData);
            return result;
        };

        const result = this.tree.tick(this.actor, context);

        // Restore original
        this.tree.root.tick = originalTick;

        // Store in history
        this.executionHistory.push(tickData);
        if (this.executionHistory.length > this.maxHistoryLength) {
            this.executionHistory.shift();
        }

        return result;
    }

    recordNodeExecution(node, actor, context, tickData, depth = 0) {
        const nodeData = {
            name: node.name,
            type: node.constructor.name,
            depth: depth
        };

        const result = node.tick(actor, context);
        nodeData.result = result;

        tickData.nodes.push(nodeData);

        return result;
    }

    visualize(ctx, x, y, width, height) {
        // Draw behavior tree structure
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(x, y, width, height);

        ctx.fillStyle = 'white';
        ctx.font = '12px monospace';
        ctx.textAlign = 'left';

        let yPos = y + 20;

        if (this.executionHistory.length > 0) {
            const latest = this.executionHistory[this.executionHistory.length - 1];

            ctx.fillText('Behavior Tree Execution:', x + 10, yPos);
            yPos += 20;

            for (const nodeData of latest.nodes) {
                const indent = '  '.repeat(nodeData.depth);
                const color = this.getStatusColor(nodeData.result);

                ctx.fillStyle = color;
                const text = `${indent}${nodeData.name} [${nodeData.result}]`;
                ctx.fillText(text, x + 10, yPos);
                yPos += 15;

                if (yPos > y + height - 10) break;
            }
        }
    }

    getStatusColor(status) {
        switch (status) {
            case 'success': return '#00ff00';
            case 'failure': return '#ff0000';
            case 'running': return '#ffff00';
            default: return '#ffffff';
        }
    }

    printTree() {
        console.log('Behavior Tree Structure:');
        console.log(this.tree.toString());
    }

    printExecutionHistory(count = 5) {
        console.log(`Last ${count} executions:`);

        const history = this.executionHistory.slice(-count);

        for (let i = 0; i < history.length; i++) {
            console.log(`\nTick ${i + 1}:`);
            for (const node of history[i].nodes) {
                const indent = '  '.repeat(node.depth);
                console.log(`${indent}${node.name} -> ${node.result}`);
            }
        }
    }
}
```

## Integration with Game Systems

Behavior trees connect to the rest of your game:

```javascript
class GameWorld {
    constructor() {
        this.entities = [];
        this.player = {x: 400, y: 300, health: 100};
        this.gameTime = {hour: 9, minute: 0};

        // Create some enemies with behavior trees
        this.entities.push(new Enemy(100, 100));
        this.entities.push(new Enemy(600, 400));
        this.entities.push(new BossEnemy(400, 100));

        // Create NPCs
        this.entities.push(new CivilianNPC(200, 300, 'Alice'));
        this.entities.push(new CivilianNPC(500, 300, 'Bob'));
    }

    update(deltaTime) {
        // Advance game time
        this.gameTime.minute += 1;
        if (this.gameTime.minute >= 60) {
            this.gameTime.minute = 0;
            this.gameTime.hour = (this.gameTime.hour + 1) % 24;
        }

        // Create context for AI
        const context = {
            player: this.player,
            gameTime: this.gameTime,
            threats: this.entities.filter(e => e instanceof Enemy),
            deltaTime: deltaTime
        };

        // Update all entities
        for (const entity of this.entities) {
            if (entity.update) {
                entity.update(context);
            }
        }
    }

    draw(ctx) {
        // Clear screen
        ctx.fillStyle = '#2a2a2a';
        ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);

        // Draw player
        ctx.fillStyle = 'cyan';
        ctx.beginPath();
        ctx.arc(this.player.x, this.player.y, 12, 0, Math.PI * 2);
        ctx.fill();

        // Draw entities
        for (const entity of this.entities) {
            if (entity.draw) {
                entity.draw(ctx);
            }
        }

        // Draw UI
        ctx.fillStyle = 'white';
        ctx.font = '14px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(`Time: ${String(this.gameTime.hour).padStart(2, '0')}:${String(this.gameTime.minute).padStart(2, '0')}`, 10, 20);
        ctx.fillText(`Player Health: ${this.player.health}`, 10, 40);
    }
}
```

## Claude Code Prompts for Behavior Trees

**Basic Enemy AI:**
```
"Create a behavior tree for an enemy that patrols, chases the player when detected, attacks when in range, and flees when health is low"
```

**Complex Boss:**
```
"Implement a multi-phase boss behavior tree with different attack patterns in each phase, using Selector and Sequence nodes"
```

**NPC Daily Routine:**
```
"Build a behavior tree for an NPC with a daily schedule: work during the day, socialize in the evening, sleep at night"
```

**Adding New Behaviors:**
```
"Add a 'take cover' behavior to this enemy AI that activates when being shot at, finding the nearest cover point"
```

**Debugging:**
```
"Create a visual debugger for this behavior tree that shows which nodes are executing and their status each frame"
```

## FSM vs Behavior Trees Comparison

When should you use Behavior Trees instead of Finite State Machines?

**Use Behavior Trees when:**
- AI has many possible actions (10+ states becomes unwieldy in FSM)
- Behaviors should be prioritized (selectors naturally express priority)
- You need modular, reusable behaviors
- Designers need to author AI without programming
- Debugging needs to show decision hierarchy

**Use FSMs when:**
- AI is simple with few states (3-5 states)
- State transitions are well-defined and limited
- Performance is critical (FSMs are slightly faster)
- State persistence is important (FSMs track current state clearly)

**Hybrid Approach:**
Use both! Behavior trees for high-level decisions, FSMs within action nodes for animation states or sub-behaviors.

## Performance Considerations

Behavior trees are efficient but can be optimized:

- **Lazy Evaluation**: Conditions should be cheap; expensive checks should have guard conditions
- **Caching**: Cache expensive calculations in context, update once per frame
- **Update Frequency**: Not all AI needs 60 FPS updates; stagger updates or use LOD
- **Node Pooling**: Reuse node instances rather than creating dynamically
- **Early Exits**: Use Selectors to avoid evaluating low-priority branches

## Related Documentation

- [Finite State Machines](./finite-state-machines.md) - Simpler alternative for basic AI
- [Pathfinding Algorithms](./pathfinding-algorithms.md) - Movement behaviors for behavior tree actions
- [NPC Behaviors](./npc-behaviors.md) - Steering and perception for realistic movement

Behavior trees are the industry standard for good reason - they're powerful, maintainable, and scalable. Master them, and you can create AI of any complexity!
