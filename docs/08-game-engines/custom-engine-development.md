# Custom Engine Development

Building a custom game engine provides deep understanding of game architecture and complete control over your game's technology stack. This guide covers when and how to build your own engine.

## Table of Contents
- [When to Build a Custom Engine](#when-to-build-a-custom-engine)
- [Core Systems Architecture](#core-systems-architecture)
- [Minimal Engine Example](#minimal-engine-example)
- [Claude Code Prompts](#claude-code-prompts)

## When to Build a Custom Engine

### Good Reasons

1. **Learning**: Best way to deeply understand game engine architecture
2. **Specific Requirements**: Unique gameplay mechanics not supported by existing engines
3. **File Size**: Need minimal bundle size (< 50 KB possible)
4. **Performance**: Maximum optimization for specific use case
5. **Control**: Complete control over every aspect
6. **Innovation**: Experimental rendering or gameplay systems

### Bad Reasons

1. **"Not Invented Here" Syndrome**: Existing engines usually better
2. **General-Purpose Games**: Use proven engines like Phaser, Babylon.js
3. **Time Constraints**: Building engines is time-consuming
4. **Team Unfamiliarity**: Established engines have better documentation
5. **Complex 3D**: Modern 3D engines are very sophisticated

### Decision Matrix

| Your Need | Custom Engine | Existing Engine |
|-----------|---------------|-----------------|
| Simple 2D game | Maybe | Recommended |
| Complex 3D game | No | Recommended |
| Unique mechanic | Maybe | Try first |
| Learning project | Yes | Optional |
| Production game | Rarely | Recommended |
| Minimal size | Yes | No |
| Rapid prototype | No | Recommended |

## Core Systems Architecture

A minimal game engine needs these core systems:

```typescript
// src/engine/Engine.ts
export class GameEngine {
  // Core systems
  private renderer: Renderer;
  private inputManager: InputManager;
  private sceneManager: SceneManager;
  private audioManager: AudioManager;
  private assetLoader: AssetLoader;

  // Game loop
  private isRunning: boolean = false;
  private lastTime: number = 0;
  private accumulator: number = 0;
  private readonly fixedDeltaTime: number = 1 / 60;

  constructor(canvas: HTMLCanvasElement) {
    this.renderer = new Renderer(canvas);
    this.inputManager = new InputManager(canvas);
    this.sceneManager = new SceneManager();
    this.audioManager = new AudioManager();
    this.assetLoader = new AssetLoader();
  }

  async initialize() {
    await this.assetLoader.loadAll();
    this.sceneManager.setActiveScene('game');
  }

  start() {
    this.isRunning = true;
    this.lastTime = performance.now();
    this.gameLoop();
  }

  stop() {
    this.isRunning = false;
  }

  private gameLoop = () => {
    if (!this.isRunning) return;

    requestAnimationFrame(this.gameLoop);

    const currentTime = performance.now();
    const deltaTime = (currentTime - this.lastTime) / 1000;
    this.lastTime = currentTime;

    this.accumulator += deltaTime;

    // Fixed timestep for physics
    while (this.accumulator >= this.fixedDeltaTime) {
      this.fixedUpdate(this.fixedDeltaTime);
      this.accumulator -= this.fixedDeltaTime;
    }

    // Variable timestep for rendering
    this.update(deltaTime);
    this.render();
  };

  private fixedUpdate(deltaTime: number) {
    const scene = this.sceneManager.getActiveScene();
    scene?.fixedUpdate(deltaTime);
  }

  private update(deltaTime: number) {
    this.inputManager.update();
    const scene = this.sceneManager.getActiveScene();
    scene?.update(deltaTime);
  }

  private render() {
    this.renderer.clear();
    const scene = this.sceneManager.getActiveScene();
    scene?.render(this.renderer);
  }
}
```

### Renderer System

```typescript
// src/engine/Renderer.ts
export class Renderer {
  private ctx: CanvasRenderingContext2D;
  private canvas: HTMLCanvasElement;
  private camera: Camera;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.camera = new Camera(0, 0, canvas.width, canvas.height);
  }

  clear() {
    this.ctx.fillStyle = '#000';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawSprite(sprite: Sprite) {
    const screenPos = this.camera.worldToScreen(sprite.position);

    this.ctx.save();
    this.ctx.translate(screenPos.x, screenPos.y);
    this.ctx.rotate(sprite.rotation);
    this.ctx.scale(sprite.scale.x, sprite.scale.y);

    if (sprite.image) {
      this.ctx.drawImage(
        sprite.image,
        -sprite.width / 2,
        -sprite.height / 2,
        sprite.width,
        sprite.height
      );
    } else {
      this.ctx.fillStyle = sprite.color;
      this.ctx.fillRect(
        -sprite.width / 2,
        -sprite.height / 2,
        sprite.width,
        sprite.height
      );
    }

    this.ctx.restore();
  }

  drawRect(x: number, y: number, width: number, height: number, color: string) {
    const screenPos = this.camera.worldToScreen({ x, y });
    this.ctx.fillStyle = color;
    this.ctx.fillRect(screenPos.x, screenPos.y, width, height);
  }

  drawCircle(x: number, y: number, radius: number, color: string) {
    const screenPos = this.camera.worldToScreen({ x, y });
    this.ctx.fillStyle = color;
    this.ctx.beginPath();
    this.ctx.arc(screenPos.x, screenPos.y, radius, 0, Math.PI * 2);
    this.ctx.fill();
  }

  drawText(text: string, x: number, y: number, font: string, color: string) {
    const screenPos = this.camera.worldToScreen({ x, y });
    this.ctx.font = font;
    this.ctx.fillStyle = color;
    this.ctx.fillText(text, screenPos.x, screenPos.y);
  }

  getCamera(): Camera {
    return this.camera;
  }
}

export class Camera {
  constructor(
    public x: number,
    public y: number,
    public width: number,
    public height: number
  ) {}

  worldToScreen(worldPos: { x: number; y: number }): { x: number; y: number } {
    return {
      x: worldPos.x - this.x + this.width / 2,
      y: worldPos.y - this.y + this.height / 2
    };
  }

  screenToWorld(screenPos: { x: number; y: number }): { x: number; y: number } {
    return {
      x: screenPos.x + this.x - this.width / 2,
      y: screenPos.y + this.y - this.height / 2
    };
  }

  follow(target: { x: number; y: number }, lerp: number = 0.1) {
    this.x += (target.x - this.x) * lerp;
    this.y += (target.y - this.y) * lerp;
  }
}
```

### Input System

```typescript
// src/engine/InputManager.ts
export class InputManager {
  private keys: Map<string, boolean> = new Map();
  private keysPressed: Map<string, boolean> = new Map();
  private keysReleased: Map<string, boolean> = new Map();

  private mousePos: { x: number; y: number } = { x: 0, y: 0 };
  private mouseButtons: Map<number, boolean> = new Map();
  private mouseClicked: Map<number, boolean> = new Map();

  constructor(canvas: HTMLCanvasElement) {
    this.setupEventListeners(canvas);
  }

  private setupEventListeners(canvas: HTMLCanvasElement) {
    // Keyboard
    window.addEventListener('keydown', (e) => {
      if (!this.keys.get(e.code)) {
        this.keysPressed.set(e.code, true);
      }
      this.keys.set(e.code, true);
    });

    window.addEventListener('keyup', (e) => {
      this.keys.set(e.code, false);
      this.keysReleased.set(e.code, true);
    });

    // Mouse
    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      this.mousePos.x = e.clientX - rect.left;
      this.mousePos.y = e.clientY - rect.top;
    });

    canvas.addEventListener('mousedown', (e) => {
      this.mouseButtons.set(e.button, true);
      this.mouseClicked.set(e.button, true);
    });

    canvas.addEventListener('mouseup', (e) => {
      this.mouseButtons.set(e.button, false);
    });

    // Touch (mobile)
    canvas.addEventListener('touchstart', (e) => {
      const touch = e.touches[0];
      const rect = canvas.getBoundingClientRect();
      this.mousePos.x = touch.clientX - rect.left;
      this.mousePos.y = touch.clientY - rect.top;
      this.mouseButtons.set(0, true);
      this.mouseClicked.set(0, true);
    });

    canvas.addEventListener('touchend', () => {
      this.mouseButtons.set(0, false);
    });

    canvas.addEventListener('touchmove', (e) => {
      const touch = e.touches[0];
      const rect = canvas.getBoundingClientRect();
      this.mousePos.x = touch.clientX - rect.left;
      this.mousePos.y = touch.clientY - rect.top;
    });
  }

  update() {
    // Clear one-frame states
    this.keysPressed.clear();
    this.keysReleased.clear();
    this.mouseClicked.clear();
  }

  isKeyDown(key: string): boolean {
    return this.keys.get(key) || false;
  }

  isKeyPressed(key: string): boolean {
    return this.keysPressed.get(key) || false;
  }

  isKeyReleased(key: string): boolean {
    return this.keysReleased.get(key) || false;
  }

  isMouseDown(button: number = 0): boolean {
    return this.mouseButtons.get(button) || false;
  }

  isMouseClicked(button: number = 0): boolean {
    return this.mouseClicked.get(button) || false;
  }

  getMousePosition(): { x: number; y: number } {
    return { ...this.mousePos };
  }
}
```

### Entity System

```typescript
// src/engine/Entity.ts
export class Entity {
  public position: { x: number; y: number } = { x: 0, y: 0 };
  public velocity: { x: number; y: number } = { x: 0, y: 0 };
  public rotation: number = 0;
  public scale: { x: number; y: number } = { x: 1, y: 1 };
  public active: boolean = true;

  public components: Map<string, Component> = new Map();

  update(deltaTime: number) {
    if (!this.active) return;

    this.components.forEach(component => {
      if (component.enabled) {
        component.update(deltaTime);
      }
    });
  }

  fixedUpdate(deltaTime: number) {
    if (!this.active) return;

    this.components.forEach(component => {
      if (component.enabled) {
        component.fixedUpdate(deltaTime);
      }
    });
  }

  render(renderer: Renderer) {
    if (!this.active) return;

    this.components.forEach(component => {
      if (component.enabled) {
        component.render(renderer);
      }
    });
  }

  addComponent<T extends Component>(component: T): T {
    component.entity = this;
    this.components.set(component.constructor.name, component);
    component.start();
    return component;
  }

  getComponent<T extends Component>(type: new () => T): T | undefined {
    return this.components.get(type.name) as T;
  }

  destroy() {
    this.active = false;
    this.components.forEach(component => component.destroy());
    this.components.clear();
  }
}

export abstract class Component {
  public entity!: Entity;
  public enabled: boolean = true;

  start() {}
  update(deltaTime: number) {}
  fixedUpdate(deltaTime: number) {}
  render(renderer: Renderer) {}
  destroy() {}
}
```

### Scene System

```typescript
// src/engine/Scene.ts
export class Scene {
  protected entities: Entity[] = [];
  protected name: string;

  constructor(name: string) {
    this.name = name;
  }

  addEntity(entity: Entity) {
    this.entities.push(entity);
  }

  removeEntity(entity: Entity) {
    const index = this.entities.indexOf(entity);
    if (index !== -1) {
      this.entities.splice(index, 1);
    }
  }

  update(deltaTime: number) {
    this.entities.forEach(entity => entity.update(deltaTime));
    this.entities = this.entities.filter(e => e.active);
  }

  fixedUpdate(deltaTime: number) {
    this.entities.forEach(entity => entity.fixedUpdate(deltaTime));
  }

  render(renderer: Renderer) {
    this.entities.forEach(entity => entity.render(renderer));
  }

  onEnter() {}
  onExit() {}
}

export class SceneManager {
  private scenes: Map<string, Scene> = new Map();
  private activeScene: Scene | null = null;

  addScene(name: string, scene: Scene) {
    this.scenes.set(name, scene);
  }

  setActiveScene(name: string) {
    const newScene = this.scenes.get(name);
    if (!newScene) {
      console.error(`Scene ${name} not found`);
      return;
    }

    if (this.activeScene) {
      this.activeScene.onExit();
    }

    this.activeScene = newScene;
    this.activeScene.onEnter();
  }

  getActiveScene(): Scene | null {
    return this.activeScene;
  }
}
```

## Minimal Engine Example

Here's a complete minimal game using the custom engine:

```typescript
// src/game/GameScene.ts
import { Scene, Entity, Component, Renderer } from '../engine';

// Player component
class PlayerController extends Component {
  private speed = 200;

  update(deltaTime: number) {
    const input = (this.entity as any).input;
    const vel = this.entity.velocity;

    vel.x = 0;
    vel.y = 0;

    if (input.isKeyDown('ArrowLeft')) vel.x = -this.speed;
    if (input.isKeyDown('ArrowRight')) vel.x = this.speed;
    if (input.isKeyDown('ArrowUp')) vel.y = -this.speed;
    if (input.isKeyDown('ArrowDown')) vel.y = this.speed;
  }

  fixedUpdate(deltaTime: number) {
    this.entity.position.x += this.entity.velocity.x * deltaTime;
    this.entity.position.y += this.entity.velocity.y * deltaTime;
  }
}

// Sprite renderer component
class SpriteRenderer extends Component {
  constructor(
    public width: number,
    public height: number,
    public color: string
  ) {
    super();
  }

  render(renderer: Renderer) {
    renderer.drawRect(
      this.entity.position.x - this.width / 2,
      this.entity.position.y - this.height / 2,
      this.width,
      this.height,
      this.color
    );
  }
}

// Enemy AI component
class EnemyAI extends Component {
  private speed = 100;
  private target: Entity;

  constructor(target: Entity) {
    super();
    this.target = target;
  }

  update(deltaTime: number) {
    const dx = this.target.position.x - this.entity.position.x;
    const dy = this.target.position.y - this.entity.position.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance > 0) {
      this.entity.velocity.x = (dx / distance) * this.speed;
      this.entity.velocity.y = (dy / distance) * this.speed;
    }
  }

  fixedUpdate(deltaTime: number) {
    this.entity.position.x += this.entity.velocity.x * deltaTime;
    this.entity.position.y += this.entity.velocity.y * deltaTime;
  }
}

// Collision component
class BoxCollider extends Component {
  constructor(
    public width: number,
    public height: number
  ) {
    super();
  }

  intersects(other: BoxCollider): boolean {
    return (
      Math.abs(this.entity.position.x - other.entity.position.x) < (this.width + other.width) / 2 &&
      Math.abs(this.entity.position.y - other.entity.position.y) < (this.height + other.height) / 2
    );
  }
}

// Game scene
export class GameScene extends Scene {
  private player: Entity;
  private enemies: Entity[] = [];
  private score: number = 0;
  private input: any;

  constructor(input: any) {
    super('game');
    this.input = input;
    this.player = this.createPlayer();
    this.spawnEnemies();
  }

  private createPlayer(): Entity {
    const player = new Entity();
    player.position = { x: 400, y: 300 };
    (player as any).input = this.input;

    player.addComponent(new PlayerController());
    player.addComponent(new SpriteRenderer(30, 30, '#00ff00'));
    player.addComponent(new BoxCollider(30, 30));

    this.addEntity(player);
    return player;
  }

  private spawnEnemies() {
    for (let i = 0; i < 5; i++) {
      const enemy = new Entity();
      enemy.position = {
        x: Math.random() * 800,
        y: Math.random() * 600
      };

      enemy.addComponent(new EnemyAI(this.player));
      enemy.addComponent(new SpriteRenderer(20, 20, '#ff0000'));
      enemy.addComponent(new BoxCollider(20, 20));

      this.addEntity(enemy);
      this.enemies.push(enemy);
    }
  }

  update(deltaTime: number) {
    super.update(deltaTime);

    // Check collisions
    const playerCollider = this.player.getComponent(BoxCollider);
    if (!playerCollider) return;

    this.enemies.forEach(enemy => {
      const enemyCollider = enemy.getComponent(BoxCollider);
      if (enemyCollider && playerCollider.intersects(enemyCollider)) {
        enemy.destroy();
        this.score += 100;
        this.spawnEnemy();
      }
    });

    this.enemies = this.enemies.filter(e => e.active);
  }

  private spawnEnemy() {
    const enemy = new Entity();
    enemy.position = {
      x: Math.random() * 800,
      y: Math.random() * 600
    };

    enemy.addComponent(new EnemyAI(this.player));
    enemy.addComponent(new SpriteRenderer(20, 20, '#ff0000'));
    enemy.addComponent(new BoxCollider(20, 20));

    this.addEntity(enemy);
    this.enemies.push(enemy);
  }

  render(renderer: Renderer) {
    super.render(renderer);

    // Draw score
    renderer.drawText(
      `Score: ${this.score}`,
      20,
      20,
      '24px Arial',
      '#ffffff'
    );

    // Camera follows player
    renderer.getCamera().follow(this.player.position, 0.1);
  }
}

// main.ts
import { GameEngine } from './engine/Engine';
import { GameScene } from './game/GameScene';

const canvas = document.getElementById('game-canvas') as HTMLCanvasElement;
const engine = new GameEngine(canvas);

// Add game scene
const gameScene = new GameScene(engine.getInputManager());
engine.getSceneManager().addScene('game', gameScene);

// Initialize and start
engine.initialize().then(() => {
  engine.start();
});
```

### Performance Optimizations

```typescript
// Spatial partitioning for collision detection
export class QuadTree {
  private maxObjects: number = 10;
  private maxLevels: number = 5;
  private level: number;
  private bounds: Rectangle;
  private objects: Entity[] = [];
  private nodes: QuadTree[] = [];

  constructor(level: number, bounds: Rectangle) {
    this.level = level;
    this.bounds = bounds;
  }

  clear() {
    this.objects = [];
    this.nodes.forEach(node => node.clear());
    this.nodes = [];
  }

  split() {
    const subWidth = this.bounds.width / 2;
    const subHeight = this.bounds.height / 2;
    const x = this.bounds.x;
    const y = this.bounds.y;

    this.nodes[0] = new QuadTree(this.level + 1, {
      x: x + subWidth,
      y: y,
      width: subWidth,
      height: subHeight
    });

    this.nodes[1] = new QuadTree(this.level + 1, {
      x: x,
      y: y,
      width: subWidth,
      height: subHeight
    });

    this.nodes[2] = new QuadTree(this.level + 1, {
      x: x,
      y: y + subHeight,
      width: subWidth,
      height: subHeight
    });

    this.nodes[3] = new QuadTree(this.level + 1, {
      x: x + subWidth,
      y: y + subHeight,
      width: subWidth,
      height: subHeight
    });
  }

  insert(entity: Entity) {
    if (this.nodes.length > 0) {
      const index = this.getIndex(entity);
      if (index !== -1) {
        this.nodes[index].insert(entity);
        return;
      }
    }

    this.objects.push(entity);

    if (this.objects.length > this.maxObjects && this.level < this.maxLevels) {
      if (this.nodes.length === 0) {
        this.split();
      }

      let i = 0;
      while (i < this.objects.length) {
        const index = this.getIndex(this.objects[i]);
        if (index !== -1) {
          this.nodes[index].insert(this.objects.splice(i, 1)[0]);
        } else {
          i++;
        }
      }
    }
  }

  retrieve(entity: Entity): Entity[] {
    const index = this.getIndex(entity);
    let returnObjects = this.objects;

    if (this.nodes.length > 0) {
      if (index !== -1) {
        returnObjects = returnObjects.concat(this.nodes[index].retrieve(entity));
      } else {
        this.nodes.forEach(node => {
          returnObjects = returnObjects.concat(node.retrieve(entity));
        });
      }
    }

    return returnObjects;
  }

  private getIndex(entity: Entity): number {
    const collider = entity.getComponent(BoxCollider);
    if (!collider) return -1;

    const verticalMidpoint = this.bounds.x + this.bounds.width / 2;
    const horizontalMidpoint = this.bounds.y + this.bounds.height / 2;

    const topQuadrant = entity.position.y < horizontalMidpoint &&
      entity.position.y + collider.height < horizontalMidpoint;

    const bottomQuadrant = entity.position.y > horizontalMidpoint;

    if (entity.position.x < verticalMidpoint &&
        entity.position.x + collider.width < verticalMidpoint) {
      if (topQuadrant) return 1;
      else if (bottomQuadrant) return 2;
    } else if (entity.position.x > verticalMidpoint) {
      if (topQuadrant) return 0;
      else if (bottomQuadrant) return 3;
    }

    return -1;
  }
}

interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}
```

## Claude Code Prompts

```
Create a minimal 2D game engine with entity-component system
```

```
Build a custom game engine with physics and collision detection
```

```
Implement a scene management system for my game engine
```

```
Add particle system to my custom game engine
```

```
Create an asset loading system for my game engine
```

```
Optimize collision detection in my game engine using spatial partitioning
```

## Engine Size Comparison

| Engine Type | Minified Size | Gzipped Size |
|-------------|---------------|--------------|
| Phaser 3 | ~1.2 MB | ~350 KB |
| PixiJS | ~400 KB | ~120 KB |
| Custom (Minimal) | ~10 KB | ~3 KB |
| Custom (Full-Featured) | ~50 KB | ~15 KB |

## Next Steps

- Review [Advanced Patterns](../09-advanced-patterns/README.md) for scalable architecture
- Learn [Performance Optimization](../10-performance-optimization/README.md) techniques
- Explore [Testing & QA](../11-testing-qa/README.md) for engine testing

Building a custom engine is a learning journey. Start small, iterate, and gradually add features as needed!
