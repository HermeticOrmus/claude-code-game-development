# Event-Driven Architecture

Event-driven architecture enables loose coupling between game systems through asynchronous message passing. Systems communicate by publishing and subscribing to events without direct references to each other.

## Table of Contents
- [Event Bus Implementation](#event-bus-implementation)
- [Observer Pattern](#observer-pattern)
- [Message Passing Systems](#message-passing-systems)
- [Event System Implementations](#event-system-implementations)
- [Debugging Events](#debugging-events)
- [Claude Code Prompts](#claude-code-prompts)

## Event Bus Implementation

### Simple Event Bus

```typescript
// src/events/EventBus.ts
type EventHandler<T = any> = (data: T) => void;

export class EventBus {
  private events: Map<string, Set<EventHandler>> = new Map();

  on<T = any>(eventName: string, handler: EventHandler<T>): () => void {
    if (!this.events.has(eventName)) {
      this.events.set(eventName, new Set());
    }

    this.events.get(eventName)!.add(handler);

    // Return unsubscribe function
    return () => this.off(eventName, handler);
  }

  once<T = any>(eventName: string, handler: EventHandler<T>): void {
    const wrappedHandler = (data: T) => {
      handler(data);
      this.off(eventName, wrappedHandler);
    };

    this.on(eventName, wrappedHandler);
  }

  off<T = any>(eventName: string, handler: EventHandler<T>): void {
    const handlers = this.events.get(eventName);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.events.delete(eventName);
      }
    }
  }

  emit<T = any>(eventName: string, data?: T): void {
    const handlers = this.events.get(eventName);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${eventName}:`, error);
        }
      });
    }
  }

  clear(eventName?: string): void {
    if (eventName) {
      this.events.delete(eventName);
    } else {
      this.events.clear();
    }
  }

  getListenerCount(eventName: string): number {
    return this.events.get(eventName)?.size || 0;
  }

  hasListeners(eventName: string): boolean {
    return this.getListenerCount(eventName) > 0;
  }
}
```

### Typed Event Bus

```typescript
// src/events/TypedEventBus.ts
interface GameEvents {
  'player-died': { playerId: number; cause: string };
  'enemy-spawned': { enemyId: number; position: { x: number; y: number } };
  'score-changed': { newScore: number; delta: number };
  'level-completed': { level: number; time: number };
  'achievement-unlocked': { achievementId: string; name: string };
}

export class TypedEventBus {
  private events: Map<string, Set<(data: any) => void>> = new Map();

  on<K extends keyof GameEvents>(
    eventName: K,
    handler: (data: GameEvents[K]) => void
  ): () => void {
    if (!this.events.has(eventName)) {
      this.events.set(eventName, new Set());
    }

    this.events.get(eventName)!.add(handler);

    return () => this.off(eventName, handler);
  }

  emit<K extends keyof GameEvents>(
    eventName: K,
    data: GameEvents[K]
  ): void {
    const handlers = this.events.get(eventName);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  off<K extends keyof GameEvents>(
    eventName: K,
    handler: (data: GameEvents[K]) => void
  ): void {
    const handlers = this.events.get(eventName);
    if (handlers) {
      handlers.delete(handler);
    }
  }
}

// Usage with type safety
const eventBus = new TypedEventBus();

eventBus.on('player-died', (data) => {
  // data is typed as { playerId: number; cause: string }
  console.log(`Player ${data.playerId} died from ${data.cause}`);
});

eventBus.emit('player-died', { playerId: 1, cause: 'fall-damage' });
```

### Priority Event Bus

```typescript
// src/events/PriorityEventBus.ts
interface PriorityHandler<T = any> {
  handler: EventHandler<T>;
  priority: number;
}

export class PriorityEventBus {
  private events: Map<string, PriorityHandler[]> = new Map();

  on<T = any>(
    eventName: string,
    handler: EventHandler<T>,
    priority: number = 0
  ): () => void {
    if (!this.events.has(eventName)) {
      this.events.set(eventName, []);
    }

    const handlers = this.events.get(eventName)!;
    handlers.push({ handler, priority });

    // Sort by priority (higher priority first)
    handlers.sort((a, b) => b.priority - a.priority);

    return () => this.off(eventName, handler);
  }

  emit<T = any>(eventName: string, data?: T): void {
    const handlers = this.events.get(eventName);
    if (handlers) {
      for (const { handler } of handlers) {
        handler(data);
      }
    }
  }

  off<T = any>(eventName: string, handler: EventHandler<T>): void {
    const handlers = this.events.get(eventName);
    if (handlers) {
      const index = handlers.findIndex(h => h.handler === handler);
      if (index !== -1) {
        handlers.splice(index, 1);
      }
    }
  }
}

// Usage
const eventBus = new PriorityEventBus();

// High priority handler (runs first)
eventBus.on('game-over', () => {
  console.log('Save high score');
}, 100);

// Low priority handler (runs last)
eventBus.on('game-over', () => {
  console.log('Show game over screen');
}, 10);
```

## Observer Pattern

### Subject-Observer Implementation

```typescript
// src/patterns/Observer.ts
export interface Observer<T = any> {
  update(data: T): void;
}

export class Subject<T = any> {
  private observers: Set<Observer<T>> = new Set();

  attach(observer: Observer<T>): void {
    this.observers.add(observer);
  }

  detach(observer: Observer<T>): void {
    this.observers.delete(observer);
  }

  notify(data: T): void {
    this.observers.forEach(observer => observer.update(data));
  }

  getObserverCount(): number {
    return this.observers.size;
  }
}

// Example: Health system with observers
class Health extends Subject<{ current: number; max: number }> {
  constructor(
    private current: number,
    private max: number
  ) {
    super();
  }

  takeDamage(amount: number): void {
    this.current = Math.max(0, this.current - amount);
    this.notify({ current: this.current, max: this.max });
  }

  heal(amount: number): void {
    this.current = Math.min(this.max, this.current + amount);
    this.notify({ current: this.current, max: this.max });
  }

  getCurrent(): number {
    return this.current;
  }

  getMax(): number {
    return this.max;
  }
}

// UI Observer
class HealthBarUI implements Observer<{ current: number; max: number }> {
  constructor(private element: HTMLElement) {}

  update(data: { current: number; max: number }): void {
    const percentage = (data.current / data.max) * 100;
    this.element.style.width = `${percentage}%`;
    this.element.textContent = `${data.current} / ${data.max}`;
  }
}

// Audio Observer
class HealthAudio implements Observer<{ current: number; max: number }> {
  private lastHealth: number = 0;

  update(data: { current: number; max: number }): void {
    if (data.current < this.lastHealth) {
      this.playDamageSound();
    } else if (data.current > this.lastHealth) {
      this.playHealSound();
    }
    this.lastHealth = data.current;
  }

  private playDamageSound(): void {
    // Play damage sound
  }

  private playHealSound(): void {
    // Play heal sound
  }
}

// Usage
const playerHealth = new Health(100, 100);
const healthBar = new HealthBarUI(document.getElementById('health-bar')!);
const healthAudio = new HealthAudio();

playerHealth.attach(healthBar);
playerHealth.attach(healthAudio);

playerHealth.takeDamage(20); // Both observers notified
```

## Message Passing Systems

### Command Pattern with Events

```typescript
// src/commands/Command.ts
export interface Command {
  execute(): void;
  undo?(): void;
}

export class CommandHistory {
  private history: Command[] = [];
  private currentIndex: number = -1;

  execute(command: Command): void {
    command.execute();

    // Clear redo history
    this.history = this.history.slice(0, this.currentIndex + 1);

    this.history.push(command);
    this.currentIndex++;
  }

  undo(): void {
    if (this.canUndo()) {
      const command = this.history[this.currentIndex];
      if (command.undo) {
        command.undo();
        this.currentIndex--;
      }
    }
  }

  redo(): void {
    if (this.canRedo()) {
      this.currentIndex++;
      const command = this.history[this.currentIndex];
      command.execute();
    }
  }

  canUndo(): boolean {
    return this.currentIndex >= 0;
  }

  canRedo(): boolean {
    return this.currentIndex < this.history.length - 1;
  }

  clear(): void {
    this.history = [];
    this.currentIndex = -1;
  }
}

// Example commands
class MoveCommand implements Command {
  private previousPosition: { x: number; y: number };

  constructor(
    private entity: { x: number; y: number },
    private newPosition: { x: number; y: number }
  ) {
    this.previousPosition = { x: entity.x, y: entity.y };
  }

  execute(): void {
    this.entity.x = this.newPosition.x;
    this.entity.y = this.newPosition.y;
  }

  undo(): void {
    this.entity.x = this.previousPosition.x;
    this.entity.y = this.previousPosition.y;
  }
}

class SpawnEnemyCommand implements Command {
  private spawnedEntity?: number;

  constructor(
    private gameWorld: GameWorld,
    private position: { x: number; y: number }
  ) {}

  execute(): void {
    this.spawnedEntity = this.gameWorld.spawnEnemy(this.position);
  }

  undo(): void {
    if (this.spawnedEntity !== undefined) {
      this.gameWorld.removeEntity(this.spawnedEntity);
    }
  }
}
```

### Message Queue System

```typescript
// src/messaging/MessageQueue.ts
export interface Message<T = any> {
  type: string;
  data: T;
  timestamp: number;
  priority?: number;
}

export class MessageQueue {
  private queue: Message[] = [];
  private handlers: Map<string, Set<(data: any) => void>> = new Map();

  enqueue<T>(type: string, data: T, priority: number = 0): void {
    const message: Message<T> = {
      type,
      data,
      timestamp: Date.now(),
      priority
    };

    this.queue.push(message);

    // Sort by priority
    this.queue.sort((a, b) => (b.priority || 0) - (a.priority || 0));
  }

  process(maxMessages: number = Infinity): number {
    let processed = 0;

    while (this.queue.length > 0 && processed < maxMessages) {
      const message = this.queue.shift()!;
      const handlers = this.handlers.get(message.type);

      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message.data);
          } catch (error) {
            console.error(`Error processing message ${message.type}:`, error);
          }
        });
      }

      processed++;
    }

    return processed;
  }

  registerHandler(type: string, handler: (data: any) => void): void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);
  }

  unregisterHandler(type: string, handler: (data: any) => void): void {
    this.handlers.get(type)?.delete(handler);
  }

  clear(): void {
    this.queue = [];
  }

  size(): number {
    return this.queue.length;
  }
}

// Usage in game loop
const messageQueue = new MessageQueue();

// Register handlers
messageQueue.registerHandler('damage', (data) => {
  console.log(`Entity ${data.entityId} took ${data.amount} damage`);
});

messageQueue.registerHandler('pickup', (data) => {
  console.log(`Player picked up ${data.item}`);
});

// Game loop
function gameLoop() {
  // Process up to 10 messages per frame
  messageQueue.process(10);

  requestAnimationFrame(gameLoop);
}

// Enqueue messages
messageQueue.enqueue('damage', { entityId: 1, amount: 20 }, 10);
messageQueue.enqueue('pickup', { item: 'health-potion' }, 5);
```

## Event System Implementations

### Achievement System

```typescript
// src/systems/AchievementSystem.ts
interface Achievement {
  id: string;
  name: string;
  description: string;
  unlocked: boolean;
  progress: number;
  maxProgress: number;
}

export class AchievementSystem {
  private achievements: Map<string, Achievement> = new Map();
  private eventBus: EventBus;

  constructor(eventBus: EventBus) {
    this.eventBus = eventBus;
    this.setupAchievements();
    this.registerEventHandlers();
  }

  private setupAchievements(): void {
    this.achievements.set('first-kill', {
      id: 'first-kill',
      name: 'First Blood',
      description: 'Defeat your first enemy',
      unlocked: false,
      progress: 0,
      maxProgress: 1
    });

    this.achievements.set('kill-100', {
      id: 'kill-100',
      name: 'Century',
      description: 'Defeat 100 enemies',
      unlocked: false,
      progress: 0,
      maxProgress: 100
    });

    this.achievements.set('no-damage', {
      id: 'no-damage',
      name: 'Untouchable',
      description: 'Complete a level without taking damage',
      unlocked: false,
      progress: 0,
      maxProgress: 1
    });
  }

  private registerEventHandlers(): void {
    this.eventBus.on('enemy-killed', () => {
      this.updateProgress('first-kill', 1);
      this.updateProgress('kill-100', 1);
    });

    this.eventBus.on('player-damaged', () => {
      const achievement = this.achievements.get('no-damage');
      if (achievement) {
        achievement.progress = 0; // Reset progress
      }
    });

    this.eventBus.on('level-completed', () => {
      const achievement = this.achievements.get('no-damage');
      if (achievement && achievement.progress === achievement.maxProgress) {
        this.unlock('no-damage');
      }
    });
  }

  private updateProgress(achievementId: string, amount: number): void {
    const achievement = this.achievements.get(achievementId);
    if (!achievement || achievement.unlocked) return;

    achievement.progress = Math.min(
      achievement.progress + amount,
      achievement.maxProgress
    );

    if (achievement.progress >= achievement.maxProgress) {
      this.unlock(achievementId);
    }

    this.eventBus.emit('achievement-progress', {
      achievementId,
      progress: achievement.progress,
      maxProgress: achievement.maxProgress
    });
  }

  private unlock(achievementId: string): void {
    const achievement = this.achievements.get(achievementId);
    if (!achievement || achievement.unlocked) return;

    achievement.unlocked = true;

    this.eventBus.emit('achievement-unlocked', {
      achievementId,
      name: achievement.name,
      description: achievement.description
    });
  }

  getAchievements(): Achievement[] {
    return Array.from(this.achievements.values());
  }
}
```

### Combat System with Events

```typescript
// src/systems/CombatSystem.ts
export class CombatSystem {
  constructor(private eventBus: EventBus) {
    this.registerEventHandlers();
  }

  private registerEventHandlers(): void {
    this.eventBus.on('attack', (data: { attackerId: number; targetId: number; damage: number }) => {
      this.processAttack(data.attackerId, data.targetId, data.damage);
    });
  }

  attack(attackerId: number, targetId: number, baseDamage: number): void {
    this.eventBus.emit('attack', { attackerId, targetId, damage: baseDamage });
  }

  private processAttack(attackerId: number, targetId: number, damage: number): void {
    // Calculate final damage (could be modified by armor, buffs, etc.)
    let finalDamage = damage;

    // Emit damage calculation event (other systems can modify damage)
    this.eventBus.emit('calculate-damage', {
      attackerId,
      targetId,
      baseDamage: damage,
      modifyDamage: (newDamage: number) => { finalDamage = newDamage; }
    });

    // Apply damage
    this.eventBus.emit('take-damage', {
      entityId: targetId,
      damage: finalDamage,
      source: attackerId
    });

    // Check for death
    this.eventBus.emit('check-death', { entityId: targetId });
  }
}

// Buff system that modifies damage
export class BuffSystem {
  private damageBuffs: Map<number, number> = new Map();

  constructor(private eventBus: EventBus) {
    this.eventBus.on('calculate-damage', (data) => {
      const buff = this.damageBuffs.get(data.attackerId);
      if (buff) {
        data.modifyDamage(data.baseDamage * buff);
      }
    });
  }

  applyDamageBuff(entityId: number, multiplier: number, duration: number): void {
    this.damageBuffs.set(entityId, multiplier);

    setTimeout(() => {
      this.damageBuffs.delete(entityId);
      this.eventBus.emit('buff-expired', { entityId, buffType: 'damage' });
    }, duration);

    this.eventBus.emit('buff-applied', {
      entityId,
      buffType: 'damage',
      multiplier,
      duration
    });
  }
}
```

## Debugging Events

### Event Logger

```typescript
// src/debugging/EventLogger.ts
export class EventLogger {
  private logs: Array<{
    timestamp: number;
    eventName: string;
    data: any;
  }> = [];

  private maxLogs: number = 1000;

  constructor(private eventBus: EventBus) {
    this.setupLogging();
  }

  private setupLogging(): void {
    // Intercept all events
    const originalEmit = this.eventBus.emit.bind(this.eventBus);

    this.eventBus.emit = <T = any>(eventName: string, data?: T): void => {
      this.log(eventName, data);
      originalEmit(eventName, data);
    };
  }

  private log(eventName: string, data: any): void {
    this.logs.push({
      timestamp: Date.now(),
      eventName,
      data
    });

    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }
  }

  getLogs(filter?: string): typeof this.logs {
    if (filter) {
      return this.logs.filter(log => log.eventName.includes(filter));
    }
    return [...this.logs];
  }

  getEventCount(eventName?: string): number {
    if (eventName) {
      return this.logs.filter(log => log.eventName === eventName).length;
    }
    return this.logs.length;
  }

  clear(): void {
    this.logs = [];
  }

  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }
}

// Usage
const eventLogger = new EventLogger(eventBus);

// Later...
console.log(eventLogger.getLogs('player')); // Get all player-related events
console.log(eventLogger.getEventCount('enemy-killed')); // Count specific event
```

## Claude Code Prompts

```
Create an event bus system for my game with type safety
```

```
Implement an achievement system using event-driven architecture
```

```
Add event logging and debugging tools to my game
```

```
Create a message queue system for handling game events
```

```
Implement the observer pattern for my game's UI updates
```

```
Build a command pattern system with undo/redo support
```

## Best Practices

1. **Use Typed Events**: TypeScript interfaces prevent errors
2. **Avoid Event Chains**: Don't emit events from event handlers (can cause infinite loops)
3. **Namespace Events**: Use prefixes like `player:died` instead of `died`
4. **Clean Up**: Always unsubscribe when objects are destroyed
5. **Error Handling**: Wrap handlers in try-catch to prevent one error breaking all handlers
6. **Document Events**: Maintain a list of all events and their data structures
7. **Avoid Over-Use**: Not everything needs events; sometimes a direct call is clearer

## Next Steps

- Explore [Object Pooling](./object-pooling.md) for performance
- Learn [Spatial Partitioning](./spatial-partitioning.md)
- Review [Entity-Component-System](./entity-component-system.md)
