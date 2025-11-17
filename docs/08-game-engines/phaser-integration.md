# Phaser 3 Integration Guide

Phaser 3 is the leading open-source HTML5 game framework for creating 2D games. This guide covers complete integration, from basic setup to production-ready games.

## Table of Contents
- [Setup and Configuration](#setup-and-configuration)
- [Scene Architecture](#scene-architecture)
- [Physics Systems](#physics-systems)
- [Sprites and Animation](#sprites-and-animation)
- [Tilemaps](#tilemaps)
- [Complete Game Example](#complete-game-example)
- [Claude Code Prompts](#claude-code-prompts)
- [Best Practices](#best-practices)

## Setup and Configuration

### Installation

```bash
npm install phaser
# or
yarn add phaser
```

### Basic Configuration

```javascript
// src/config.js
import Phaser from 'phaser';

export const gameConfig = {
  type: Phaser.AUTO, // Use WebGL if available, fallback to Canvas
  width: 800,
  height: 600,
  parent: 'game-container',
  backgroundColor: '#2d2d2d',
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH
  },
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { y: 300 },
      debug: false
    }
  },
  scene: [] // Add scenes here
};
```

### Vite Integration

```javascript
// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          phaser: ['phaser']
        }
      }
    }
  }
});
```

### TypeScript Configuration

```typescript
// src/config.ts
import Phaser from 'phaser';
import { BootScene } from './scenes/BootScene';
import { GameScene } from './scenes/GameScene';

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 800,
  height: 600,
  parent: 'game-container',
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { y: 300 },
      debug: process.env.NODE_ENV === 'development'
    }
  },
  scene: [BootScene, GameScene]
};

export default config;
```

## Scene Architecture

Phaser games are organized into Scenes. Each scene represents a distinct state of your game (menu, gameplay, game over, etc.).

### Scene Lifecycle

```typescript
// src/scenes/GameScene.ts
import Phaser from 'phaser';

export class GameScene extends Phaser.Scene {
  private player?: Phaser.Physics.Arcade.Sprite;
  private cursors?: Phaser.Types.Input.Keyboard.CursorKeys;
  private score: number = 0;
  private scoreText?: Phaser.GameObjects.Text;

  constructor() {
    super({ key: 'GameScene' });
  }

  // Called once when scene is created
  init(data: any) {
    console.log('Scene initialized with data:', data);
    this.score = 0;
  }

  // Load assets
  preload() {
    this.load.setPath('assets');

    // Load sprite sheets
    this.load.spritesheet('player', 'sprites/player.png', {
      frameWidth: 32,
      frameHeight: 48
    });

    // Load images
    this.load.image('ground', 'sprites/platform.png');
    this.load.image('star', 'sprites/star.png');

    // Load audio
    this.load.audio('jump', 'audio/jump.mp3');
    this.load.audio('collect', 'audio/collect.mp3');
  }

  // Create game objects
  create() {
    // Create platforms
    const platforms = this.physics.add.staticGroup();
    platforms.create(400, 568, 'ground').setScale(2).refreshBody();
    platforms.create(600, 400, 'ground');
    platforms.create(50, 250, 'ground');
    platforms.create(750, 220, 'ground');

    // Create player
    this.player = this.physics.add.sprite(100, 450, 'player');
    this.player.setBounce(0.2);
    this.player.setCollideWorldBounds(true);

    // Create animations
    this.anims.create({
      key: 'left',
      frames: this.anims.generateFrameNumbers('player', { start: 0, end: 3 }),
      frameRate: 10,
      repeat: -1
    });

    this.anims.create({
      key: 'turn',
      frames: [{ key: 'player', frame: 4 }],
      frameRate: 20
    });

    this.anims.create({
      key: 'right',
      frames: this.anims.generateFrameNumbers('player', { start: 5, end: 8 }),
      frameRate: 10,
      repeat: -1
    });

    // Collisions
    this.physics.add.collider(this.player, platforms);

    // Input
    this.cursors = this.input.keyboard?.createCursorKeys();

    // UI
    this.scoreText = this.add.text(16, 16, 'Score: 0', {
      fontSize: '32px',
      color: '#fff'
    });
  }

  // Called every frame
  update(time: number, delta: number) {
    if (!this.player || !this.cursors) return;

    // Player movement
    if (this.cursors.left.isDown) {
      this.player.setVelocityX(-160);
      this.player.anims.play('left', true);
    } else if (this.cursors.right.isDown) {
      this.player.setVelocityX(160);
      this.player.anims.play('right', true);
    } else {
      this.player.setVelocityX(0);
      this.player.anims.play('turn');
    }

    // Jump
    if (this.cursors.up.isDown && this.player.body?.touching.down) {
      this.player.setVelocityY(-330);
      this.sound.play('jump');
    }
  }

  // Helper methods
  private updateScore(points: number) {
    this.score += points;
    this.scoreText?.setText('Score: ' + this.score);
  }

  // Clean up when scene is shut down
  shutdown() {
    this.player?.destroy();
    this.scoreText?.destroy();
  }
}
```

### Scene Management

```typescript
// src/scenes/MenuScene.ts
export class MenuScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MenuScene' });
  }

  create() {
    const title = this.add.text(400, 200, 'My Game', {
      fontSize: '64px',
      color: '#fff'
    }).setOrigin(0.5);

    const playButton = this.add.text(400, 400, 'Play', {
      fontSize: '32px',
      color: '#0f0'
    })
    .setOrigin(0.5)
    .setInteractive({ useHandCursor: true });

    playButton.on('pointerdown', () => {
      // Transition to game scene
      this.scene.start('GameScene', { difficulty: 'normal' });
    });

    playButton.on('pointerover', () => {
      playButton.setStyle({ color: '#00ff00' });
    });

    playButton.on('pointerout', () => {
      playButton.setStyle({ color: '#0f0' });
    });
  }
}
```

## Physics Systems

Phaser 3 includes two physics engines: Arcade Physics (simple, fast) and Matter.js (complex, realistic).

### Arcade Physics

```typescript
export class ArcadePhysicsExample extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite;
  private enemies!: Phaser.Physics.Arcade.Group;

  create() {
    // Static physics group (platforms)
    const platforms = this.physics.add.staticGroup();
    platforms.create(400, 568, 'ground').setScale(2).refreshBody();

    // Dynamic sprite
    this.player = this.physics.add.sprite(100, 450, 'player');
    this.player.setBounce(0.2);
    this.player.setCollideWorldBounds(true);
    this.player.setDrag(100, 0);

    // Physics group (enemies)
    this.enemies = this.physics.add.group({
      key: 'enemy',
      repeat: 5,
      setXY: { x: 100, y: 0, stepX: 100 }
    });

    this.enemies.children.iterate((child) => {
      const enemy = child as Phaser.Physics.Arcade.Sprite;
      enemy.setBounceY(Phaser.Math.FloatBetween(0.4, 0.8));
      return true;
    });

    // Colliders
    this.physics.add.collider(this.player, platforms);
    this.physics.add.collider(this.enemies, platforms);

    // Overlap detection
    this.physics.add.overlap(
      this.player,
      this.enemies,
      this.hitEnemy,
      undefined,
      this
    );
  }

  private hitEnemy(
    player: Phaser.GameObjects.GameObject,
    enemy: Phaser.GameObjects.GameObject
  ) {
    const enemySprite = enemy as Phaser.Physics.Arcade.Sprite;
    enemySprite.disableBody(true, true);

    // Add particle effect
    const particles = this.add.particles('particle');
    const emitter = particles.createEmitter({
      speed: 100,
      scale: { start: 1, end: 0 },
      blendMode: 'ADD'
    });
    emitter.explode(16, enemySprite.x, enemySprite.y);
  }
}
```

### Matter.js Physics

```typescript
export class MatterPhysicsExample extends Phaser.Scene {
  constructor() {
    super({
      key: 'MatterPhysicsExample',
      physics: {
        default: 'matter',
        matter: {
          gravity: { y: 1 },
          debug: true
        }
      }
    });
  }

  create() {
    // Create compound bodies
    const player = this.matter.add.sprite(100, 100, 'player');

    // Set physics properties
    player.setFriction(0.05);
    player.setBounce(0.2);
    player.setMass(5);

    // Create sensors (collision detection without physics response)
    const sensor = this.matter.add.rectangle(400, 300, 100, 100, {
      isSensor: true,
      isStatic: true
    });

    // Collision events
    this.matter.world.on('collisionstart', (event: any) => {
      event.pairs.forEach((pair: any) => {
        const { bodyA, bodyB } = pair;
        console.log('Collision between:', bodyA.label, bodyB.label);
      });
    });

    // Create constraints (joints, springs)
    const anchor = this.matter.add.rectangle(400, 100, 20, 20, {
      isStatic: true
    });

    const ball = this.matter.add.sprite(400, 200, 'ball');

    this.matter.add.constraint(anchor, ball, 100, 0.5, {
      pointA: { x: 0, y: 0 },
      pointB: { x: 0, y: 0 }
    });
  }
}
```

## Sprites and Animation

```typescript
export class SpriteAnimationExample extends Phaser.Scene {
  preload() {
    // Load sprite sheet
    this.load.spritesheet('hero', 'assets/hero.png', {
      frameWidth: 64,
      frameHeight: 64
    });

    // Load texture atlas (more efficient)
    this.load.atlas(
      'characters',
      'assets/characters.png',
      'assets/characters.json'
    );
  }

  create() {
    // Create animations from sprite sheet
    this.anims.create({
      key: 'walk',
      frames: this.anims.generateFrameNumbers('hero', {
        start: 0,
        end: 7
      }),
      frameRate: 10,
      repeat: -1
    });

    this.anims.create({
      key: 'attack',
      frames: this.anims.generateFrameNumbers('hero', {
        start: 8,
        end: 15
      }),
      frameRate: 15,
      repeat: 0
    });

    // Create animations from atlas
    this.anims.create({
      key: 'mage-idle',
      frames: this.anims.generateFrameNames('characters', {
        prefix: 'mage-idle-',
        start: 0,
        end: 3,
        zeroPad: 2
      }),
      frameRate: 8,
      repeat: -1
    });

    // Create sprite
    const player = this.add.sprite(400, 300, 'hero');
    player.play('walk');

    // Animation events
    player.on('animationcomplete-attack', () => {
      player.play('walk');
    });

    // Control animations
    this.input.keyboard?.on('keydown-SPACE', () => {
      player.play('attack');
    });
  }

  // Advanced: Dynamic animation speed
  updateAnimationSpeed(sprite: Phaser.GameObjects.Sprite, speed: number) {
    const currentAnim = sprite.anims.currentAnim;
    if (currentAnim) {
      sprite.anims.pause();
      sprite.anims.setTimeScale(speed);
      sprite.anims.resume();
    }
  }
}
```

## Tilemaps

```typescript
export class TilemapExample extends Phaser.Scene {
  private player?: Phaser.Physics.Arcade.Sprite;
  private map?: Phaser.Tilemaps.Tilemap;

  preload() {
    // Load tilemap (created with Tiled editor)
    this.load.image('tiles', 'assets/tilesets/dungeon.png');
    this.load.tilemapTiledJSON('level1', 'assets/tilemaps/level1.json');

    this.load.spritesheet('player', 'assets/player.png', {
      frameWidth: 32,
      frameHeight: 48
    });
  }

  create() {
    // Create the map
    this.map = this.make.tilemap({ key: 'level1' });

    // Add tileset image
    const tileset = this.map.addTilesetImage('dungeon', 'tiles');

    // Create layers
    const backgroundLayer = this.map.createLayer('Background', tileset!, 0, 0);
    const platformLayer = this.map.createLayer('Platforms', tileset!, 0, 0);
    const obstacleLayer = this.map.createLayer('Obstacles', tileset!, 0, 0);

    // Set collision
    platformLayer?.setCollisionByProperty({ collides: true });
    obstacleLayer?.setCollisionByProperty({ collides: true });

    // Alternative: set collision by tile index
    // platformLayer?.setCollisionBetween(1, 100);

    // Create player
    this.player = this.physics.add.sprite(100, 100, 'player');

    // Collide player with layers
    if (platformLayer) {
      this.physics.add.collider(this.player, platformLayer);
    }
    if (obstacleLayer) {
      this.physics.add.collider(this.player, obstacleLayer);
    }

    // Camera follows player
    this.cameras.main.startFollow(this.player);
    this.cameras.main.setBounds(0, 0, this.map.widthInPixels, this.map.heightInPixels);

    // Parse object layers
    const spawnPoint = this.map.findObject('Objects', obj => obj.name === 'Spawn');
    if (spawnPoint) {
      this.player.setPosition(spawnPoint.x!, spawnPoint.y!);
    }

    // Get all objects of a type
    const enemies = this.map.createFromObjects('Objects', {
      name: 'enemy',
      key: 'enemy'
    });

    // Enable physics on objects
    this.physics.world.enable(enemies);
  }

  // Get tile at world coordinates
  getTileAtWorldXY(worldX: number, worldY: number) {
    const platformLayer = this.map?.getLayer('Platforms');
    if (platformLayer) {
      return this.map?.getTileAtWorldXY(worldX, worldY, false, undefined, platformLayer);
    }
    return null;
  }
}
```

## Complete Game Example

Here's a complete platformer game combining all concepts:

```typescript
// src/scenes/PlatformerGame.ts
import Phaser from 'phaser';

interface PlayerData {
  lives: number;
  score: number;
}

export class PlatformerGame extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite;
  private platforms!: Phaser.Physics.Arcade.StaticGroup;
  private stars!: Phaser.Physics.Arcade.Group;
  private bombs!: Phaser.Physics.Arcade.Group;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;

  private score: number = 0;
  private lives: number = 3;
  private level: number = 1;

  private scoreText!: Phaser.GameObjects.Text;
  private livesText!: Phaser.GameObjects.Text;
  private levelText!: Phaser.GameObjects.Text;

  private gameOver: boolean = false;

  constructor() {
    super({ key: 'PlatformerGame' });
  }

  preload() {
    this.load.setPath('assets');

    this.load.image('sky', 'backgrounds/sky.png');
    this.load.image('ground', 'sprites/platform.png');
    this.load.image('star', 'sprites/star.png');
    this.load.image('bomb', 'sprites/bomb.png');

    this.load.spritesheet('dude', 'sprites/dude.png', {
      frameWidth: 32,
      frameHeight: 48
    });

    this.load.audio('jump', 'audio/jump.mp3');
    this.load.audio('collect', 'audio/collect.mp3');
    this.load.audio('explosion', 'audio/explosion.mp3');
    this.load.audio('bgm', 'audio/background-music.mp3');
  }

  create() {
    // Background
    this.add.image(400, 300, 'sky');

    // Platforms
    this.platforms = this.physics.add.staticGroup();
    this.platforms.create(400, 568, 'ground').setScale(2).refreshBody();
    this.platforms.create(600, 400, 'ground');
    this.platforms.create(50, 250, 'ground');
    this.platforms.create(750, 220, 'ground');

    // Player
    this.player = this.physics.add.sprite(100, 450, 'dude');
    this.player.setBounce(0.2);
    this.player.setCollideWorldBounds(true);

    // Animations
    this.createAnimations();

    // Stars
    this.stars = this.physics.add.group({
      key: 'star',
      repeat: 11,
      setXY: { x: 12, y: 0, stepX: 70 }
    });

    this.stars.children.iterate((child) => {
      const star = child as Phaser.Physics.Arcade.Image;
      star.setBounceY(Phaser.Math.FloatBetween(0.4, 0.8));
      return true;
    });

    // Bombs
    this.bombs = this.physics.add.group();

    // Collisions
    this.physics.add.collider(this.player, this.platforms);
    this.physics.add.collider(this.stars, this.platforms);
    this.physics.add.collider(this.bombs, this.platforms);

    // Overlaps
    this.physics.add.overlap(
      this.player,
      this.stars,
      this.collectStar,
      undefined,
      this
    );

    this.physics.add.collider(
      this.player,
      this.bombs,
      this.hitBomb,
      undefined,
      this
    );

    // Input
    this.cursors = this.input.keyboard!.createCursorKeys();

    // UI
    this.scoreText = this.add.text(16, 16, 'Score: 0', {
      fontSize: '32px',
      color: '#fff'
    });

    this.livesText = this.add.text(16, 50, 'Lives: 3', {
      fontSize: '32px',
      color: '#fff'
    });

    this.levelText = this.add.text(700, 16, 'Level: 1', {
      fontSize: '32px',
      color: '#fff'
    });

    // Background music
    const music = this.sound.add('bgm', { loop: true, volume: 0.5 });
    music.play();
  }

  update() {
    if (this.gameOver) return;

    // Player movement
    if (this.cursors.left.isDown) {
      this.player.setVelocityX(-160);
      this.player.anims.play('left', true);
    } else if (this.cursors.right.isDown) {
      this.player.setVelocityX(160);
      this.player.anims.play('right', true);
    } else {
      this.player.setVelocityX(0);
      this.player.anims.play('turn');
    }

    // Jump
    if (this.cursors.up.isDown && this.player.body!.touching.down) {
      this.player.setVelocityY(-330);
      this.sound.play('jump');
    }
  }

  private createAnimations() {
    this.anims.create({
      key: 'left',
      frames: this.anims.generateFrameNumbers('dude', { start: 0, end: 3 }),
      frameRate: 10,
      repeat: -1
    });

    this.anims.create({
      key: 'turn',
      frames: [{ key: 'dude', frame: 4 }],
      frameRate: 20
    });

    this.anims.create({
      key: 'right',
      frames: this.anims.generateFrameNumbers('dude', { start: 5, end: 8 }),
      frameRate: 10,
      repeat: -1
    });
  }

  private collectStar(
    player: Phaser.GameObjects.GameObject,
    star: Phaser.GameObjects.GameObject
  ) {
    const starSprite = star as Phaser.Physics.Arcade.Image;
    starSprite.disableBody(true, true);

    // Update score
    this.score += 10;
    this.scoreText.setText('Score: ' + this.score);

    this.sound.play('collect');

    // Check if all stars collected
    if (this.stars.countActive(true) === 0) {
      this.nextLevel();
    }
  }

  private hitBomb(
    player: Phaser.GameObjects.GameObject,
    bomb: Phaser.GameObjects.GameObject
  ) {
    const bombSprite = bomb as Phaser.Physics.Arcade.Image;
    bombSprite.disableBody(true, true);

    this.sound.play('explosion');

    // Camera shake
    this.cameras.main.shake(200, 0.01);

    // Flash
    this.cameras.main.flash(200);

    // Lose a life
    this.lives--;
    this.livesText.setText('Lives: ' + this.lives);

    if (this.lives <= 0) {
      this.endGame();
    } else {
      // Respawn player
      this.player.setPosition(100, 450);
      this.player.setVelocity(0, 0);
    }
  }

  private nextLevel() {
    this.level++;
    this.levelText.setText('Level: ' + this.level);

    // Re-enable stars
    this.stars.children.iterate((child) => {
      const star = child as Phaser.Physics.Arcade.Image;
      star.enableBody(true, star.x, 0, true, true);
      return true;
    });

    // Add more bombs
    const x = Phaser.Math.Between(0, 800);
    const bomb = this.bombs.create(x, 16, 'bomb');
    bomb.setBounce(1);
    bomb.setCollideWorldBounds(true);
    bomb.setVelocity(Phaser.Math.Between(-200, 200), 20);
  }

  private endGame() {
    this.gameOver = true;
    this.physics.pause();
    this.player.setTint(0xff0000);
    this.player.anims.play('turn');

    // Game over text
    const gameOverText = this.add.text(400, 300, 'GAME OVER', {
      fontSize: '64px',
      color: '#ff0000'
    }).setOrigin(0.5);

    // Restart button
    const restartButton = this.add.text(400, 400, 'Restart', {
      fontSize: '32px',
      color: '#fff'
    })
    .setOrigin(0.5)
    .setInteractive({ useHandCursor: true });

    restartButton.on('pointerdown', () => {
      this.scene.restart();
    });
  }
}
```

## Claude Code Prompts

### Game Creation Prompts

```
Create a Phaser 3 platformer game with player movement, jumping, collectibles, and enemies
```

```
Build a top-down shooter in Phaser 3 with bullet pooling, enemy spawning, and power-ups
```

```
Implement a match-3 puzzle game using Phaser 3 with animations and scoring
```

### Feature Implementation Prompts

```
Add tilemap support to my Phaser game using Tiled JSON format
```

```
Implement particle effects for explosions and collectibles in Phaser 3
```

```
Create a scene management system with transitions for my Phaser game
```

```
Add touch controls for mobile support in my Phaser platformer
```

### Optimization Prompts

```
Optimize my Phaser game for mobile devices with texture atlases and object pooling
```

```
Implement a loading screen with progress bar for my Phaser game
```

```
Add WebGL shader effects to my Phaser 3 game
```

## Best Practices

### Performance Optimization

1. **Use Texture Atlases**: Combine multiple images into atlases to reduce draw calls
2. **Object Pooling**: Reuse game objects instead of creating/destroying
3. **Disable Physics When Not Needed**: Turn off physics for static objects
4. **Limit Particle Effects**: Use conservative particle counts
5. **Use Groups**: Physics groups are more efficient than individual objects

### Code Organization

```typescript
// Organize by feature
src/
  ├── scenes/
  │   ├── BootScene.ts
  │   ├── MenuScene.ts
  │   ├── GameScene.ts
  │   └── GameOverScene.ts
  ├── entities/
  │   ├── Player.ts
  │   ├── Enemy.ts
  │   └── Collectible.ts
  ├── systems/
  │   ├── InputSystem.ts
  │   ├── ScoreSystem.ts
  │   └── AudioSystem.ts
  ├── config/
  │   ├── gameConfig.ts
  │   └── constants.ts
  └── main.ts
```

### Asset Management

```typescript
export class AssetLoader {
  static preloadAll(scene: Phaser.Scene) {
    // Images
    const images = [
      { key: 'player', path: 'sprites/player.png' },
      { key: 'enemy', path: 'sprites/enemy.png' }
    ];

    images.forEach(({ key, path }) => {
      scene.load.image(key, path);
    });

    // Audio
    const audio = [
      { key: 'bgm', path: 'audio/music.mp3' },
      { key: 'jump', path: 'audio/jump.mp3' }
    ];

    audio.forEach(({ key, path }) => {
      scene.load.audio(key, path);
    });
  }
}
```

### Mobile Considerations

```typescript
const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    width: isMobile ? 375 : 800,
    height: isMobile ? 667 : 600
  },
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { y: isMobile ? 200 : 300 }
    }
  }
};

// Touch controls
if (isMobile) {
  const leftButton = this.add.image(50, 550, 'button-left')
    .setInteractive()
    .on('pointerdown', () => this.moveLeft = true)
    .on('pointerup', () => this.moveLeft = false);
}
```

### Common Pitfalls

1. **Not Cleaning Up**: Always destroy sprites and remove event listeners in scene shutdown
2. **Ignoring RefreshBody()**: Call refreshBody() after scaling static physics objects
3. **Excessive Create() Logic**: Move heavy initialization to preload() or init()
4. **Missing Texture Keys**: Verify asset keys match loaded assets
5. **Physics Body Sizing**: Set custom physics body sizes when sprite frames vary

## Next Steps

- Explore [Babylon.js Workflows](./babylon-js-workflows.md) for 3D games
- Learn [Advanced Patterns](../09-advanced-patterns/README.md) for scalable architecture
- Review [Performance Optimization](../10-performance-optimization/README.md) techniques

## Additional Resources

- [Official Phaser 3 Documentation](https://photonstorm.github.io/phaser3-docs/)
- [Phaser 3 Examples](https://phaser.io/examples)
- [Phaser Discord Community](https://discord.gg/phaser)
