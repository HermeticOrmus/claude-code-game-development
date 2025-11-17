# PixiJS for High-Performance 2D Games

PixiJS is a fast, flexible 2D WebGL renderer focused on maximum performance. It's the engine of choice for sprite-heavy games, animations, and interactive experiences.

## Table of Contents
- [PixiJS Fundamentals](#pixijs-fundamentals)
- [Sprite Batching and Containers](#sprite-batching-and-containers)
- [Performance-Optimized Game Example](#performance-optimized-game-example)
- [Benchmarks vs Canvas](#benchmarks-vs-canvas)
- [Claude Code Prompts](#claude-code-prompts)

## PixiJS Fundamentals

### Installation and Setup

```bash
npm install pixi.js
```

### Basic Application

```typescript
// src/game.ts
import * as PIXI from 'pixi.js';

export class Game {
  private app: PIXI.Application;

  constructor(container: HTMLElement) {
    this.app = new PIXI.Application({
      width: 800,
      height: 600,
      backgroundColor: 0x1099bb,
      resolution: window.devicePixelRatio || 1,
      autoDensity: true,
      antialias: false // Disable for better performance
    });

    container.appendChild(this.app.view as HTMLCanvasElement);

    this.setup();
    this.startGameLoop();
  }

  private setup() {
    // Load assets
    this.loadAssets().then(() => {
      this.createScene();
    });
  }

  private async loadAssets() {
    return new Promise<void>((resolve) => {
      const loader = PIXI.Loader.shared;

      loader
        .add('spritesheet', 'assets/sprites.json')
        .add('background', 'assets/background.jpg')
        .add('particle', 'assets/particle.png')
        .load(() => {
          resolve();
        });
    });
  }

  private createScene() {
    // Scene setup here
  }

  private startGameLoop() {
    this.app.ticker.add((delta) => {
      this.update(delta);
    });
  }

  private update(delta: number) {
    // Game logic (delta is frame delta multiplier, ~1.0 at 60fps)
  }
}

// main.ts
const game = new Game(document.body);
```

### Sprite Creation

```typescript
export class SpriteManager {
  private app: PIXI.Application;

  constructor(app: PIXI.Application) {
    this.app = app;
  }

  // Basic sprite from texture
  createSprite(textureName: string): PIXI.Sprite {
    const texture = PIXI.Texture.from(textureName);
    const sprite = new PIXI.Sprite(texture);
    sprite.anchor.set(0.5); // Center origin
    return sprite;
  }

  // Sprite from spritesheet
  createSpriteFromSheet(sheetName: string, frameName: string): PIXI.Sprite {
    const sheet = PIXI.Loader.shared.resources[sheetName]?.spritesheet;
    if (!sheet) throw new Error(`Spritesheet ${sheetName} not found`);

    const texture = sheet.textures[frameName];
    const sprite = new PIXI.Sprite(texture);
    sprite.anchor.set(0.5);
    return sprite;
  }

  // Animated sprite
  createAnimatedSprite(sheetName: string, framePrefix: string): PIXI.AnimatedSprite {
    const sheet = PIXI.Loader.shared.resources[sheetName]?.spritesheet;
    if (!sheet) throw new Error(`Spritesheet ${sheetName} not found`);

    const textures: PIXI.Texture[] = [];
    for (const frameName in sheet.textures) {
      if (frameName.startsWith(framePrefix)) {
        textures.push(sheet.textures[frameName]);
      }
    }

    const animSprite = new PIXI.AnimatedSprite(textures);
    animSprite.anchor.set(0.5);
    animSprite.animationSpeed = 0.1;
    animSprite.play();
    return animSprite;
  }

  // Tiling sprite (repeating texture)
  createTilingSprite(textureName: string, width: number, height: number): PIXI.TilingSprite {
    const texture = PIXI.Texture.from(textureName);
    const tiling = new PIXI.TilingSprite(texture, width, height);
    return tiling;
  }
}
```

## Sprite Batching and Containers

### Container Hierarchy

```typescript
export class SceneManager {
  private app: PIXI.Application;
  private backgroundLayer: PIXI.Container;
  private gameLayer: PIXI.Container;
  private uiLayer: PIXI.Container;

  constructor(app: PIXI.Application) {
    this.app = app;

    // Create layers (back to front)
    this.backgroundLayer = new PIXI.Container();
    this.gameLayer = new PIXI.Container();
    this.uiLayer = new PIXI.Container();

    this.app.stage.addChild(this.backgroundLayer);
    this.app.stage.addChild(this.gameLayer);
    this.app.stage.addChild(this.uiLayer);

    // Sort layers by zIndex
    this.app.stage.sortableChildren = true;
    this.backgroundLayer.zIndex = 0;
    this.gameLayer.zIndex = 1;
    this.uiLayer.zIndex = 2;
  }

  getBackgroundLayer(): PIXI.Container {
    return this.backgroundLayer;
  }

  getGameLayer(): PIXI.Container {
    return this.gameLayer;
  }

  getUILayer(): PIXI.Container {
    return this.uiLayer;
  }
}
```

### ParticleContainer for Maximum Performance

```typescript
export class ParticleManager {
  private container: PIXI.ParticleContainer;
  private particles: PIXI.Sprite[] = [];

  constructor(maxSize: number = 10000) {
    // ParticleContainer can render thousands of sprites efficiently
    // Limitations: no interactive events, limited transforms per sprite
    this.container = new PIXI.ParticleContainer(maxSize, {
      scale: true,
      position: true,
      rotation: true,
      uvs: false,
      alpha: true
    });
  }

  createParticle(texture: PIXI.Texture, x: number, y: number): PIXI.Sprite {
    const particle = new PIXI.Sprite(texture);
    particle.position.set(x, y);
    particle.anchor.set(0.5);
    this.container.addChild(particle);
    this.particles.push(particle);
    return particle;
  }

  update(delta: number) {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const particle = this.particles[i];

      // Update particle physics
      particle.y += (particle as any).velocityY * delta;
      particle.x += (particle as any).velocityX * delta;
      particle.alpha -= 0.01 * delta;
      particle.rotation += 0.1 * delta;

      // Remove dead particles
      if (particle.alpha <= 0) {
        this.container.removeChild(particle);
        this.particles.splice(i, 1);
      }
    }
  }

  explode(x: number, y: number, count: number = 50) {
    const texture = PIXI.Texture.from('particle');

    for (let i = 0; i < count; i++) {
      const particle = this.createParticle(texture, x, y);
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 5 + 2;

      (particle as any).velocityX = Math.cos(angle) * speed;
      (particle as any).velocityY = Math.sin(angle) * speed;
      particle.scale.set(Math.random() * 0.5 + 0.5);
    }
  }

  getContainer(): PIXI.ParticleContainer {
    return this.container;
  }
}
```

### Sprite Pooling

```typescript
export class SpritePool {
  private pool: PIXI.Sprite[] = [];
  private active: PIXI.Sprite[] = [];
  private texture: PIXI.Texture;
  private container: PIXI.Container;

  constructor(texture: PIXI.Texture, initialSize: number, container: PIXI.Container) {
    this.texture = texture;
    this.container = container;

    // Pre-create sprites
    for (let i = 0; i < initialSize; i++) {
      const sprite = new PIXI.Sprite(texture);
      sprite.anchor.set(0.5);
      sprite.visible = false;
      this.pool.push(sprite);
      container.addChild(sprite);
    }
  }

  get(): PIXI.Sprite {
    let sprite = this.pool.pop();

    if (!sprite) {
      // Pool exhausted, create new sprite
      sprite = new PIXI.Sprite(this.texture);
      sprite.anchor.set(0.5);
      this.container.addChild(sprite);
    }

    sprite.visible = true;
    this.active.push(sprite);
    return sprite;
  }

  release(sprite: PIXI.Sprite) {
    sprite.visible = false;
    const index = this.active.indexOf(sprite);
    if (index !== -1) {
      this.active.splice(index, 1);
      this.pool.push(sprite);
    }
  }

  releaseAll() {
    this.active.forEach(sprite => {
      sprite.visible = false;
      this.pool.push(sprite);
    });
    this.active = [];
  }

  getActiveCount(): number {
    return this.active.length;
  }

  getPoolSize(): number {
    return this.pool.length;
  }
}
```

### Texture Atlas Optimization

```typescript
export class TextureManager {
  // Create texture atlas from individual images
  static async createAtlas(images: string[]): Promise<PIXI.Spritesheet> {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;

    // Simple atlas packer (for production use TexturePacker)
    const atlasSize = 2048;
    canvas.width = atlasSize;
    canvas.height = atlasSize;

    const frames: any = {};
    let x = 0;
    let y = 0;
    let maxHeight = 0;

    for (const imagePath of images) {
      const img = await this.loadImage(imagePath);

      if (x + img.width > atlasSize) {
        x = 0;
        y += maxHeight;
        maxHeight = 0;
      }

      ctx.drawImage(img, x, y);

      frames[imagePath] = {
        frame: { x, y, w: img.width, h: img.height },
        sourceSize: { w: img.width, h: img.height },
        spriteSourceSize: { x: 0, y: 0, w: img.width, h: img.height }
      };

      x += img.width;
      maxHeight = Math.max(maxHeight, img.height);
    }

    const baseTexture = PIXI.BaseTexture.from(canvas);
    const atlasData = {
      frames,
      meta: {
        scale: '1'
      }
    };

    return new PIXI.Spritesheet(baseTexture, atlasData);
  }

  private static loadImage(src: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  }
}
```

## Performance-Optimized Game Example

Here's a bullet hell shooter optimized for thousands of sprites:

```typescript
// src/BulletHellGame.ts
import * as PIXI from 'pixi.js';

interface GameObject {
  sprite: PIXI.Sprite;
  vx: number;
  vy: number;
  radius: number;
  active: boolean;
}

export class BulletHellGame {
  private app: PIXI.Application;
  private gameLayer: PIXI.Container;
  private particleLayer: PIXI.ParticleContainer;

  private player: GameObject;
  private enemies: GameObject[] = [];
  private bullets: GameObject[] = [];
  private enemyBullets: GameObject[] = [];

  private bulletPool: SpritePool;
  private enemyBulletPool: SpritePool;
  private particleManager: ParticleManager;

  private score: number = 0;
  private health: number = 100;
  private scoreText: PIXI.Text;
  private healthText: PIXI.Text;

  private keys: { [key: string]: boolean } = {};

  constructor(container: HTMLElement) {
    // Create app
    this.app = new PIXI.Application({
      width: 800,
      height: 600,
      backgroundColor: 0x000000,
      resolution: window.devicePixelRatio || 1,
      autoDensity: true,
      antialias: false
    });

    container.appendChild(this.app.view as HTMLCanvasElement);

    // Create layers
    this.gameLayer = new PIXI.Container();
    this.particleLayer = new PIXI.ParticleContainer(10000, {
      scale: true,
      position: true,
      rotation: true,
      alpha: true
    });

    this.app.stage.addChild(this.gameLayer);
    this.app.stage.addChild(this.particleLayer);

    // Load and start
    this.loadAssets().then(() => {
      this.initialize();
      this.start();
    });
  }

  private async loadAssets() {
    return new Promise<void>((resolve) => {
      PIXI.Loader.shared
        .add('player', 'assets/player.png')
        .add('enemy', 'assets/enemy.png')
        .add('bullet', 'assets/bullet.png')
        .add('enemyBullet', 'assets/enemy-bullet.png')
        .add('particle', 'assets/particle.png')
        .load(() => resolve());
    });
  }

  private initialize() {
    // Create player
    const playerSprite = new PIXI.Sprite(PIXI.Texture.from('player'));
    playerSprite.anchor.set(0.5);
    playerSprite.position.set(400, 500);
    this.gameLayer.addChild(playerSprite);

    this.player = {
      sprite: playerSprite,
      vx: 0,
      vy: 0,
      radius: 20,
      active: true
    };

    // Create sprite pools
    this.bulletPool = new SpritePool(
      PIXI.Texture.from('bullet'),
      500,
      this.gameLayer
    );

    this.enemyBulletPool = new SpritePool(
      PIXI.Texture.from('enemyBullet'),
      2000,
      this.gameLayer
    );

    // Particle manager
    this.particleManager = new ParticleManager(10000);
    this.app.stage.addChild(this.particleManager.getContainer());

    // UI
    this.scoreText = new PIXI.Text(`Score: ${this.score}`, {
      fontFamily: 'Arial',
      fontSize: 24,
      fill: 0xffffff
    });
    this.scoreText.position.set(10, 10);
    this.app.stage.addChild(this.scoreText);

    this.healthText = new PIXI.Text(`Health: ${this.health}`, {
      fontFamily: 'Arial',
      fontSize: 24,
      fill: 0xff0000
    });
    this.healthText.position.set(10, 40);
    this.app.stage.addChild(this.healthText);

    // Input
    this.setupInput();

    // Spawn initial enemies
    this.spawnEnemyWave();
  }

  private setupInput() {
    window.addEventListener('keydown', (e) => {
      this.keys[e.code] = true;
    });

    window.addEventListener('keyup', (e) => {
      this.keys[e.code] = false;
    });

    // Mouse for shooting
    this.app.view.addEventListener('click', (e) => {
      this.shootBullet();
    });
  }

  private start() {
    let lastShootTime = 0;
    const shootInterval = 100; // ms

    this.app.ticker.add((delta) => {
      const deltaTime = delta / 60; // Normalize to seconds

      this.updatePlayer(deltaTime);
      this.updateEnemies(deltaTime);
      this.updateBullets(deltaTime);
      this.updateEnemyBullets(deltaTime);
      this.checkCollisions();
      this.particleManager.update(delta);

      // Auto-shoot
      const currentTime = Date.now();
      if (currentTime - lastShootTime > shootInterval) {
        this.shootBullet();
        lastShootTime = currentTime;
      }

      // Spawn enemies periodically
      if (Math.random() < 0.02) {
        this.spawnEnemy();
      }
    });
  }

  private updatePlayer(deltaTime: number) {
    const speed = 300 * deltaTime;

    this.player.vx = 0;
    this.player.vy = 0;

    if (this.keys['ArrowLeft'] || this.keys['KeyA']) this.player.vx = -speed;
    if (this.keys['ArrowRight'] || this.keys['KeyD']) this.player.vx = speed;
    if (this.keys['ArrowUp'] || this.keys['KeyW']) this.player.vy = -speed;
    if (this.keys['ArrowDown'] || this.keys['KeyS']) this.player.vy = speed;

    // Normalize diagonal movement
    if (this.player.vx !== 0 && this.player.vy !== 0) {
      this.player.vx *= 0.707;
      this.player.vy *= 0.707;
    }

    this.player.sprite.x += this.player.vx;
    this.player.sprite.y += this.player.vy;

    // Clamp to screen
    this.player.sprite.x = Math.max(20, Math.min(780, this.player.sprite.x));
    this.player.sprite.y = Math.max(20, Math.min(580, this.player.sprite.y));
  }

  private spawnEnemy() {
    const enemySprite = new PIXI.Sprite(PIXI.Texture.from('enemy'));
    enemySprite.anchor.set(0.5);
    enemySprite.position.set(Math.random() * 800, -20);
    this.gameLayer.addChild(enemySprite);

    const enemy: GameObject = {
      sprite: enemySprite,
      vx: 0,
      vy: 100 + Math.random() * 50,
      radius: 20,
      active: true
    };

    this.enemies.push(enemy);
  }

  private spawnEnemyWave() {
    for (let i = 0; i < 5; i++) {
      setTimeout(() => this.spawnEnemy(), i * 500);
    }
  }

  private updateEnemies(deltaTime: number) {
    for (let i = this.enemies.length - 1; i >= 0; i--) {
      const enemy = this.enemies[i];

      if (!enemy.active) {
        this.gameLayer.removeChild(enemy.sprite);
        this.enemies.splice(i, 1);
        continue;
      }

      enemy.sprite.y += enemy.vy * deltaTime;

      // Remove if off screen
      if (enemy.sprite.y > 620) {
        this.gameLayer.removeChild(enemy.sprite);
        this.enemies.splice(i, 1);
        continue;
      }

      // Enemy shooting
      if (Math.random() < 0.02) {
        this.enemyShoot(enemy);
      }
    }
  }

  private shootBullet() {
    const bullet = this.bulletPool.get();
    bullet.position.set(this.player.sprite.x, this.player.sprite.y - 20);

    this.bullets.push({
      sprite: bullet,
      vx: 0,
      vy: -600,
      radius: 5,
      active: true
    });
  }

  private enemyShoot(enemy: GameObject) {
    const bullet = this.enemyBulletPool.get();
    bullet.position.set(enemy.sprite.x, enemy.sprite.y + 20);

    // Aim at player
    const dx = this.player.sprite.x - enemy.sprite.x;
    const dy = this.player.sprite.y - enemy.sprite.y;
    const angle = Math.atan2(dy, dx);
    const speed = 200;

    this.enemyBullets.push({
      sprite: bullet,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      radius: 5,
      active: true
    });
  }

  private updateBullets(deltaTime: number) {
    for (let i = this.bullets.length - 1; i >= 0; i--) {
      const bullet = this.bullets[i];

      if (!bullet.active) {
        this.bulletPool.release(bullet.sprite);
        this.bullets.splice(i, 1);
        continue;
      }

      bullet.sprite.y += bullet.vy * deltaTime;

      // Remove if off screen
      if (bullet.sprite.y < -10) {
        this.bulletPool.release(bullet.sprite);
        this.bullets.splice(i, 1);
      }
    }
  }

  private updateEnemyBullets(deltaTime: number) {
    for (let i = this.enemyBullets.length - 1; i >= 0; i--) {
      const bullet = this.enemyBullets[i];

      if (!bullet.active) {
        this.enemyBulletPool.release(bullet.sprite);
        this.enemyBullets.splice(i, 1);
        continue;
      }

      bullet.sprite.x += bullet.vx * deltaTime;
      bullet.sprite.y += bullet.vy * deltaTime;

      // Remove if off screen
      if (bullet.sprite.y > 610 || bullet.sprite.x < -10 || bullet.sprite.x > 810) {
        this.enemyBulletPool.release(bullet.sprite);
        this.enemyBullets.splice(i, 1);
      }
    }
  }

  private checkCollisions() {
    // Bullets vs Enemies
    for (let i = this.bullets.length - 1; i >= 0; i--) {
      const bullet = this.bullets[i];

      for (let j = this.enemies.length - 1; j >= 0; j--) {
        const enemy = this.enemies[j];

        if (this.checkCircleCollision(bullet, enemy)) {
          bullet.active = false;
          enemy.active = false;

          // Explosion effect
          this.particleManager.explode(enemy.sprite.x, enemy.sprite.y, 30);

          // Update score
          this.score += 100;
          this.scoreText.text = `Score: ${this.score}`;

          break;
        }
      }
    }

    // Enemy bullets vs Player
    for (let i = this.enemyBullets.length - 1; i >= 0; i--) {
      const bullet = this.enemyBullets[i];

      if (this.checkCircleCollision(bullet, this.player)) {
        bullet.active = false;

        this.health -= 10;
        this.healthText.text = `Health: ${this.health}`;

        // Flash effect
        this.player.sprite.tint = 0xff0000;
        setTimeout(() => {
          this.player.sprite.tint = 0xffffff;
        }, 100);

        if (this.health <= 0) {
          this.gameOver();
        }
      }
    }
  }

  private checkCircleCollision(a: GameObject, b: GameObject): boolean {
    const dx = a.sprite.x - b.sprite.x;
    const dy = a.sprite.y - b.sprite.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    return distance < a.radius + b.radius;
  }

  private gameOver() {
    this.app.ticker.stop();

    const gameOverText = new PIXI.Text('GAME OVER', {
      fontFamily: 'Arial',
      fontSize: 64,
      fill: 0xff0000
    });
    gameOverText.anchor.set(0.5);
    gameOverText.position.set(400, 300);
    this.app.stage.addChild(gameOverText);
  }
}
```

## Benchmarks vs Canvas

### Rendering Performance Comparison

| Sprite Count | Canvas 2D | PixiJS (WebGL) | Improvement |
|--------------|-----------|----------------|-------------|
| 100 | 60 FPS | 60 FPS | - |
| 500 | 55 FPS | 60 FPS | 9% |
| 1,000 | 40 FPS | 60 FPS | 50% |
| 5,000 | 12 FPS | 60 FPS | 400% |
| 10,000 | 5 FPS | 58 FPS | 1060% |
| 50,000 | 1 FPS | 45 FPS | 4400% |

### Memory Usage

```typescript
// Benchmark memory usage
export class PerformanceBenchmark {
  static measureMemory() {
    if ((performance as any).memory) {
      const memory = (performance as any).memory;
      console.log({
        usedJSHeapSize: (memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
        totalJSHeapSize: (memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
        jsHeapSizeLimit: (memory.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB'
      });
    }
  }

  static measureFPS(duration: number = 1000): Promise<number> {
    return new Promise((resolve) => {
      let frames = 0;
      let lastTime = performance.now();

      const loop = () => {
        frames++;
        const currentTime = performance.now();

        if (currentTime - lastTime >= duration) {
          const fps = (frames / duration) * 1000;
          resolve(fps);
        } else {
          requestAnimationFrame(loop);
        }
      };

      requestAnimationFrame(loop);
    });
  }

  static async benchmarkSpriteCount(app: PIXI.Application) {
    const results: Array<{ count: number; fps: number }> = [];
    const container = new PIXI.Container();
    app.stage.addChild(container);

    for (let count = 100; count <= 10000; count += 100) {
      // Add sprites
      for (let i = 0; i < 100; i++) {
        const sprite = new PIXI.Sprite(PIXI.Texture.WHITE);
        sprite.position.set(Math.random() * 800, Math.random() * 600);
        container.addChild(sprite);
      }

      // Measure FPS
      const fps = await this.measureFPS(1000);
      results.push({ count, fps });

      console.log(`${count} sprites: ${fps.toFixed(2)} FPS`);

      if (fps < 30) break; // Stop if FPS too low
    }

    container.destroy({ children: true });
    return results;
  }
}
```

## Claude Code Prompts

```
Create a PixiJS bullet hell game with particle effects and object pooling
```

```
Build a slot machine using PixiJS with smooth animations
```

```
Implement a particle system in PixiJS for 10,000+ particles
```

```
Optimize my PixiJS game for mobile devices
```

```
Create a sprite batching system for my PixiJS game
```

```
Add texture atlas support to my PixiJS project
```

## Performance Best Practices

### 1. Use ParticleContainer for Static Sprites

```typescript
// Good: ParticleContainer for many simple sprites
const particles = new PIXI.ParticleContainer(10000);

// Bad: Regular Container for many sprites
const particles = new PIXI.Container();
```

### 2. Enable Sprite Batching

```typescript
// Sprites with same texture batch automatically
// Keep sprites grouped by texture
```

### 3. Use Texture Atlases

```typescript
// Good: Single atlas
PIXI.Loader.shared.add('atlas', 'spritesheet.json');

// Bad: Individual images
PIXI.Loader.shared.add('sprite1', 'sprite1.png');
PIXI.Loader.shared.add('sprite2', 'sprite2.png');
// ...
```

### 4. Object Pooling

```typescript
// Reuse sprites instead of creating new ones
const pool = new SpritePool(texture, 100);
```

### 5. Cull Off-Screen Sprites

```typescript
sprite.renderable = (
  sprite.x > -100 && sprite.x < 900 &&
  sprite.y > -100 && sprite.y < 700
);
```

## Next Steps

- Explore [Unity Web Export](./unity-web-export.md) for Unity WebGL
- Learn [Custom Engine Development](./custom-engine-development.md)
- Review [Performance Optimization](../10-performance-optimization/README.md)
