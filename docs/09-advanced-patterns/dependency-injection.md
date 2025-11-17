# Dependency Injection for Games

Dependency Injection (DI) is a design pattern that implements Inversion of Control (IoC) for resolving dependencies. It makes code more modular, testable, and maintainable.

## Table of Contents
- [DI Fundamentals](#di-fundamentals)
- [Service Container Implementation](#service-container-implementation)
- [Game Service Examples](#game-service-examples)
- [DI Implementations](#di-implementations)
- [Testing Benefits](#testing-benefits)
- [Claude Code Prompts](#claude-code-prompts)

## DI Fundamentals

### Without DI (Tight Coupling)

```typescript
// Bad: Hard-coded dependencies
class Player {
  private audioManager: AudioManager;
  private inputManager: InputManager;
  private scoreService: ScoreService;

  constructor() {
    // Creating dependencies inside the class
    this.audioManager = new AudioManager();
    this.inputManager = new InputManager();
    this.scoreService = new ScoreService();
  }

  // Problems:
  // 1. Cannot test in isolation
  // 2. Cannot swap implementations
  // 3. Hard to mock dependencies
  // 4. Violates Single Responsibility Principle
}
```

### With DI (Loose Coupling)

```typescript
// Good: Dependencies injected
class Player {
  constructor(
    private audioManager: IAudioManager,
    private inputManager: IInputManager,
    private scoreService: IScoreService
  ) {
    // Dependencies provided from outside
  }

  // Benefits:
  // 1. Easy to test with mocks
  // 2. Can swap implementations
  // 3. Clear dependencies
  // 4. Follows SOLID principles
}

// Usage with real services
const player = new Player(
  audioManager,
  inputManager,
  scoreService
);

// Usage in tests with mocks
const player = new Player(
  mockAudioManager,
  mockInputManager,
  mockScoreService
);
```

## Service Container Implementation

### Simple DI Container

```typescript
// src/di/Container.ts
type ServiceFactory<T> = (container: Container) => T;
type ServiceInstance = any;

export class Container {
  private services: Map<string, ServiceFactory<any>> = new Map();
  private singletons: Map<string, ServiceInstance> = new Map();
  private instances: Map<string, ServiceInstance> = new Map();

  // Register a singleton (created once)
  registerSingleton<T>(
    name: string,
    factory: ServiceFactory<T>
  ): void {
    this.services.set(name, factory);
    this.singletons.set(name, null);
  }

  // Register a transient (created each time)
  registerTransient<T>(
    name: string,
    factory: ServiceFactory<T>
  ): void {
    this.services.set(name, factory);
  }

  // Register an existing instance
  registerInstance<T>(name: string, instance: T): void {
    this.instances.set(name, instance);
  }

  // Resolve a service
  resolve<T>(name: string): T {
    // Check for registered instance
    if (this.instances.has(name)) {
      return this.instances.get(name) as T;
    }

    // Check for singleton
    if (this.singletons.has(name)) {
      let instance = this.singletons.get(name);

      if (!instance) {
        const factory = this.services.get(name);
        if (!factory) {
          throw new Error(`Service ${name} not registered`);
        }

        instance = factory(this);
        this.singletons.set(name, instance);
      }

      return instance as T;
    }

    // Create transient
    const factory = this.services.get(name);
    if (!factory) {
      throw new Error(`Service ${name} not registered`);
    }

    return factory(this) as T;
  }

  // Check if service is registered
  has(name: string): boolean {
    return this.services.has(name) || this.instances.has(name);
  }

  // Clear all services
  clear(): void {
    this.services.clear();
    this.singletons.clear();
    this.instances.clear();
  }

  // Create a child container
  createChild(): Container {
    const child = new Container();

    // Copy parent registrations
    this.services.forEach((factory, name) => {
      if (this.singletons.has(name)) {
        child.registerSingleton(name, factory);
      } else {
        child.registerTransient(name, factory);
      }
    });

    this.instances.forEach((instance, name) => {
      child.registerInstance(name, instance);
    });

    return child;
  }
}
```

### Advanced DI Container with Decorators

```typescript
// src/di/decorators.ts
const INJECTABLE_METADATA_KEY = Symbol('injectable');
const INJECT_METADATA_KEY = Symbol('inject');

export function Injectable() {
  return function (target: any) {
    Reflect.defineMetadata(INJECTABLE_METADATA_KEY, true, target);
  };
}

export function Inject(serviceName: string) {
  return function (target: any, propertyKey: string, parameterIndex: number) {
    const existingInjections = Reflect.getMetadata(INJECT_METADATA_KEY, target) || [];
    existingInjections.push({ index: parameterIndex, serviceName });
    Reflect.defineMetadata(INJECT_METADATA_KEY, existingInjections, target);
  };
}

// Advanced container with auto-wiring
export class AdvancedContainer extends Container {
  resolveWithDecorators<T>(constructor: new (...args: any[]) => T): T {
    const isInjectable = Reflect.getMetadata(INJECTABLE_METADATA_KEY, constructor);
    if (!isInjectable) {
      throw new Error(`${constructor.name} is not injectable`);
    }

    const injections: Array<{ index: number; serviceName: string }> =
      Reflect.getMetadata(INJECT_METADATA_KEY, constructor) || [];

    const paramTypes = Reflect.getMetadata('design:paramtypes', constructor) || [];
    const args = paramTypes.map((type: any, index: number) => {
      const injection = injections.find(inj => inj.index === index);
      if (injection) {
        return this.resolve(injection.serviceName);
      }
      return undefined;
    });

    return new constructor(...args);
  }
}
```

## Game Service Examples

### Audio Service

```typescript
// src/services/IAudioService.ts
export interface IAudioService {
  playSound(soundName: string, volume?: number): void;
  playMusic(musicName: string, loop?: boolean): void;
  stopMusic(): void;
  setMasterVolume(volume: number): void;
  mute(): void;
  unmute(): void;
}

// src/services/AudioService.ts
export class AudioService implements IAudioService {
  private sounds: Map<string, HTMLAudioElement> = new Map();
  private music?: HTMLAudioElement;
  private masterVolume: number = 1.0;
  private isMuted: boolean = false;

  constructor(
    private assetLoader: IAssetLoader
  ) {
    // Dependency: AssetLoader
  }

  async preloadSound(soundName: string, path: string): Promise<void> {
    const audio = await this.assetLoader.loadAudio(path);
    this.sounds.set(soundName, audio);
  }

  playSound(soundName: string, volume: number = 1.0): void {
    if (this.isMuted) return;

    const sound = this.sounds.get(soundName);
    if (!sound) {
      console.warn(`Sound ${soundName} not loaded`);
      return;
    }

    const instance = sound.cloneNode() as HTMLAudioElement;
    instance.volume = volume * this.masterVolume;
    instance.play().catch(e => console.error('Failed to play sound:', e));
  }

  playMusic(musicName: string, loop: boolean = true): void {
    this.stopMusic();

    const music = this.sounds.get(musicName);
    if (!music) {
      console.warn(`Music ${musicName} not loaded`);
      return;
    }

    this.music = music;
    this.music.loop = loop;
    this.music.volume = this.masterVolume;

    if (!this.isMuted) {
      this.music.play().catch(e => console.error('Failed to play music:', e));
    }
  }

  stopMusic(): void {
    if (this.music) {
      this.music.pause();
      this.music.currentTime = 0;
    }
  }

  setMasterVolume(volume: number): void {
    this.masterVolume = Math.max(0, Math.min(1, volume));
    if (this.music) {
      this.music.volume = this.masterVolume;
    }
  }

  mute(): void {
    this.isMuted = true;
    if (this.music) {
      this.music.pause();
    }
  }

  unmute(): void {
    this.isMuted = false;
    if (this.music) {
      this.music.play().catch(e => console.error('Failed to resume music:', e));
    }
  }
}

// Mock for testing
export class MockAudioService implements IAudioService {
  public soundsPlayed: string[] = [];
  public musicPlayed: string[] = [];

  playSound(soundName: string, volume?: number): void {
    this.soundsPlayed.push(soundName);
  }

  playMusic(musicName: string, loop?: boolean): void {
    this.musicPlayed.push(musicName);
  }

  stopMusic(): void {}
  setMasterVolume(volume: number): void {}
  mute(): void {}
  unmute(): void {}
}
```

### Input Service

```typescript
// src/services/IInputService.ts
export interface IInputService {
  isKeyDown(key: string): boolean;
  isKeyPressed(key: string): boolean;
  getMousePosition(): { x: number; y: number };
  isMouseButtonDown(button: number): boolean;
  update(): void;
}

// src/services/InputService.ts
export class InputService implements IInputService {
  private keys: Map<string, boolean> = new Map();
  private keysPressed: Map<string, boolean> = new Map();
  private mousePosition: { x: number; y: number } = { x: 0, y: 0 };
  private mouseButtons: Map<number, boolean> = new Map();

  constructor(canvas: HTMLCanvasElement) {
    this.setupEventListeners(canvas);
  }

  private setupEventListeners(canvas: HTMLCanvasElement): void {
    window.addEventListener('keydown', (e) => {
      if (!this.keys.get(e.code)) {
        this.keysPressed.set(e.code, true);
      }
      this.keys.set(e.code, true);
    });

    window.addEventListener('keyup', (e) => {
      this.keys.set(e.code, false);
    });

    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      this.mousePosition.x = e.clientX - rect.left;
      this.mousePosition.y = e.clientY - rect.top;
    });

    canvas.addEventListener('mousedown', (e) => {
      this.mouseButtons.set(e.button, true);
    });

    canvas.addEventListener('mouseup', (e) => {
      this.mouseButtons.set(e.button, false);
    });
  }

  isKeyDown(key: string): boolean {
    return this.keys.get(key) || false;
  }

  isKeyPressed(key: string): boolean {
    return this.keysPressed.get(key) || false;
  }

  getMousePosition(): { x: number; y: number } {
    return { ...this.mousePosition };
  }

  isMouseButtonDown(button: number): boolean {
    return this.mouseButtons.get(button) || false;
  }

  update(): void {
    this.keysPressed.clear();
  }
}
```

### State Management Service

```typescript
// src/services/IStateService.ts
export interface IStateService {
  setState(key: string, value: any): void;
  getState<T>(key: string): T | undefined;
  subscribe(key: string, callback: (value: any) => void): () => void;
  clearState(): void;
}

// src/services/StateService.ts
export class StateService implements IStateService {
  private state: Map<string, any> = new Map();
  private subscribers: Map<string, Set<(value: any) => void>> = new Map();

  setState(key: string, value: any): void {
    const oldValue = this.state.get(key);
    if (oldValue === value) return;

    this.state.set(key, value);
    this.notifySubscribers(key, value);
  }

  getState<T>(key: string): T | undefined {
    return this.state.get(key) as T | undefined;
  }

  subscribe(key: string, callback: (value: any) => void): () => void {
    if (!this.subscribers.has(key)) {
      this.subscribers.set(key, new Set());
    }

    this.subscribers.get(key)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.subscribers.get(key)?.delete(callback);
    };
  }

  private notifySubscribers(key: string, value: any): void {
    const subscribers = this.subscribers.get(key);
    if (subscribers) {
      subscribers.forEach(callback => callback(value));
    }
  }

  clearState(): void {
    this.state.clear();
  }
}
```

### Score Service

```typescript
// src/services/IScoreService.ts
export interface IScoreService {
  addPoints(points: number): void;
  getScore(): number;
  getHighScore(): number;
  resetScore(): void;
  saveHighScore(): Promise<void>;
}

// src/services/ScoreService.ts
export class ScoreService implements IScoreService {
  private score: number = 0;
  private highScore: number = 0;

  constructor(
    private storageService: IStorageService,
    private eventBus: IEventBus
  ) {
    this.loadHighScore();
  }

  addPoints(points: number): void {
    this.score += points;
    this.eventBus.emit('score-changed', { score: this.score });

    if (this.score > this.highScore) {
      this.highScore = this.score;
      this.eventBus.emit('new-high-score', { score: this.highScore });
    }
  }

  getScore(): number {
    return this.score;
  }

  getHighScore(): number {
    return this.highScore;
  }

  resetScore(): void {
    this.score = 0;
    this.eventBus.emit('score-reset', {});
  }

  async saveHighScore(): Promise<void> {
    await this.storageService.save('highScore', this.highScore);
  }

  private async loadHighScore(): Promise<void> {
    const saved = await this.storageService.load<number>('highScore');
    this.highScore = saved || 0;
  }
}
```

## DI Implementations

### Constructor Injection (Recommended)

```typescript
class GameManager {
  constructor(
    private audioService: IAudioService,
    private inputService: IInputService,
    private scoreService: IScoreService
  ) {
    // All dependencies provided via constructor
  }
}

// Setup
const container = new Container();

container.registerSingleton('audioService', (c) => new AudioService(
  c.resolve('assetLoader')
));

container.registerSingleton('inputService', (c) => new InputService(canvas));

container.registerSingleton('scoreService', (c) => new ScoreService(
  c.resolve('storageService'),
  c.resolve('eventBus')
));

container.registerSingleton('gameManager', (c) => new GameManager(
  c.resolve('audioService'),
  c.resolve('inputService'),
  c.resolve('scoreService')
));

// Usage
const gameManager = container.resolve<GameManager>('gameManager');
```

### Property Injection

```typescript
class GameManager {
  public audioService!: IAudioService;
  public inputService!: IInputService;
  public scoreService!: IScoreService;

  constructor() {
    // Dependencies set after construction
  }
}

// Setup with property injection
const container = new Container();
const gameManager = new GameManager();
gameManager.audioService = container.resolve('audioService');
gameManager.inputService = container.resolve('inputService');
gameManager.scoreService = container.resolve('scoreService');
```

### Method Injection

```typescript
class GameManager {
  private audioService?: IAudioService;

  setAudioService(audioService: IAudioService): void {
    this.audioService = audioService;
  }

  playSound(soundName: string): void {
    this.audioService?.playSound(soundName);
  }
}
```

## Testing Benefits

### Unit Testing with Mocks

```typescript
// GameManager.test.ts
import { describe, it, expect, beforeEach } from 'vitest';

describe('GameManager', () => {
  let gameManager: GameManager;
  let mockAudio: MockAudioService;
  let mockInput: MockInputService;
  let mockScore: MockScoreService;

  beforeEach(() => {
    mockAudio = new MockAudioService();
    mockInput = new MockInputService();
    mockScore = new MockScoreService();

    gameManager = new GameManager(mockAudio, mockInput, mockScore);
  });

  it('should play sound when enemy dies', () => {
    gameManager.onEnemyDied();

    expect(mockAudio.soundsPlayed).toContain('enemy-death');
  });

  it('should add score when enemy dies', () => {
    gameManager.onEnemyDied();

    expect(mockScore.getScore()).toBe(100);
  });

  it('should handle input correctly', () => {
    mockInput.setKeyDown('Space', true);

    gameManager.update(0.016);

    expect(mockAudio.soundsPlayed).toContain('shoot');
  });
});
```

### Integration Testing

```typescript
// GameIntegration.test.ts
describe('Game Integration', () => {
  let container: Container;

  beforeEach(() => {
    container = new Container();

    // Register real services
    container.registerSingleton('audioService', () => new AudioService());
    container.registerSingleton('inputService', () => new InputService(canvas));
    container.registerSingleton('scoreService', (c) => new ScoreService(
      c.resolve('storageService'),
      c.resolve('eventBus')
    ));
  });

  it('should create game with all dependencies', () => {
    const gameManager = container.resolve<GameManager>('gameManager');

    expect(gameManager).toBeDefined();
  });
});
```

## Claude Code Prompts

```
Create a dependency injection container for my game with service registration
```

```
Implement game services with dependency injection pattern
```

```
Add mock services for unit testing my game classes
```

```
Create a service locator pattern as alternative to DI
```

```
Refactor my game to use constructor injection for better testability
```

## Best Practices

1. **Prefer Constructor Injection**: Makes dependencies explicit and immutable
2. **Use Interfaces**: Program to interfaces, not implementations
3. **Singleton vs Transient**: Choose lifetime appropriately
4. **Avoid Service Locator**: Use DI container at composition root only
5. **Keep Container Configuration Separate**: Don't scatter `container.resolve()` calls
6. **Test with Mocks**: DI makes unit testing trivial

## Common Pitfalls

1. **Over-Abstraction**: Not everything needs an interface
2. **Circular Dependencies**: Design flaw, refactor to eliminate
3. **Service Locator Anti-Pattern**: Hides dependencies
4. **Container Everywhere**: Pass dependencies, not the container
5. **New Keyword in Business Logic**: Create objects in composition root

## Next Steps

- Explore [Event-Driven Architecture](./event-driven-architecture.md)
- Learn [Entity-Component-System](./entity-component-system.md)
- Review [Testing & QA](../11-testing-qa/README.md)
