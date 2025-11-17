# Unit Testing Games

Unit testing is the foundation of a robust testing strategy. For games, unit tests validate the core logic that drives gameplay: state management, physics calculations, collision detection, AI behaviors, and game rules. This guide shows you how to write comprehensive unit tests for game code.

## Why Test Game Logic?

**Games are complex state machines**. A seemingly simple game like Pong has states for ball position, paddle positions, velocities, scores, game phase (menu, playing, paused, game over), and more. As games grow, untested code becomes a minefield of bugs.

**Benefits of unit testing games**:

1. **Catch bugs immediately** - Tests fail the moment you break something
2. **Safe refactoring** - Improve code structure without fear
3. **Documentation** - Tests show how systems are supposed to work
4. **Faster debugging** - Failing tests pinpoint exact problems
5. **Confident updates** - Add features knowing old ones still work
6. **Performance benchmarks** - Track performance regressions

**Common myth**: "Games are too visual to test." **Reality**: 80% of game code is pure logic that's perfectly testable. Separate rendering from logic, and testing becomes straightforward.

## Jest Setup for Game Development

Jest is the most popular JavaScript testing framework. Here's how to set it up for games:

### Installation

```bash
npm install --save-dev jest @types/jest
```

### Basic Configuration

Create `jest.config.js`:

```javascript
export default {
  testEnvironment: 'jsdom', // Simulates browser environment
  moduleFileExtensions: ['js', 'json'],
  transform: {
    '^.+\\.js$': 'babel-jest',
  },
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',
    '!src/index.js',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
};
```

### Setup File for Canvas Mocking

Create `jest.setup.js`:

```javascript
// Mock canvas context for tests
HTMLCanvasElement.prototype.getContext = function(contextType) {
  if (contextType === '2d') {
    return {
      fillStyle: '',
      strokeStyle: '',
      lineWidth: 1,
      fillRect: jest.fn(),
      clearRect: jest.fn(),
      strokeRect: jest.fn(),
      beginPath: jest.fn(),
      moveTo: jest.fn(),
      lineTo: jest.fn(),
      arc: jest.fn(),
      fill: jest.fn(),
      stroke: jest.fn(),
      save: jest.fn(),
      restore: jest.fn(),
      translate: jest.fn(),
      rotate: jest.fn(),
      scale: jest.fn(),
      drawImage: jest.fn(),
      measureText: jest.fn(() => ({ width: 0 })),
      fillText: jest.fn(),
      strokeText: jest.fn(),
    };
  }
  return null;
};

// Mock requestAnimationFrame
global.requestAnimationFrame = (cb) => {
  return setTimeout(cb, 0);
};

global.cancelAnimationFrame = (id) => {
  clearTimeout(id);
};
```

### Package.json Scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:verbose": "jest --verbose"
  }
}
```

## Testing Game State Management

Game state is the heart of any game. Let's test a comprehensive game state manager:

### Game State Manager

```javascript
// gameState.js
export class GameState {
  constructor() {
    this.phase = 'menu'; // menu, playing, paused, gameOver
    this.score = 0;
    this.level = 1;
    this.lives = 3;
    this.entities = [];
    this.listeners = [];
  }

  start() {
    if (this.phase !== 'menu') return false;
    this.phase = 'playing';
    this.score = 0;
    this.level = 1;
    this.lives = 3;
    this.entities = [];
    this.emit('started');
    return true;
  }

  pause() {
    if (this.phase !== 'playing') return false;
    this.phase = 'paused';
    this.emit('paused');
    return true;
  }

  resume() {
    if (this.phase !== 'paused') return false;
    this.phase = 'playing';
    this.emit('resumed');
    return true;
  }

  gameOver() {
    this.phase = 'gameOver';
    this.emit('gameOver', { score: this.score, level: this.level });
  }

  addScore(points) {
    if (this.phase !== 'playing') return;
    this.score += points;
    this.emit('scoreChanged', this.score);
  }

  loseLife() {
    if (this.phase !== 'playing') return false;
    this.lives--;
    this.emit('lifeChanged', this.lives);

    if (this.lives <= 0) {
      this.gameOver();
      return true;
    }
    return false;
  }

  levelUp() {
    if (this.phase !== 'playing') return;
    this.level++;
    this.emit('levelChanged', this.level);
  }

  addEntity(entity) {
    this.entities.push(entity);
    return entity;
  }

  removeEntity(entity) {
    const index = this.entities.indexOf(entity);
    if (index > -1) {
      this.entities.splice(index, 1);
      return true;
    }
    return false;
  }

  on(event, callback) {
    this.listeners.push({ event, callback });
  }

  emit(event, data) {
    this.listeners
      .filter(l => l.event === event)
      .forEach(l => l.callback(data));
  }

  reset() {
    this.phase = 'menu';
    this.score = 0;
    this.level = 1;
    this.lives = 3;
    this.entities = [];
    this.listeners = [];
  }
}
```

### Comprehensive Test Suite

```javascript
// gameState.test.js
import { GameState } from './gameState';

describe('GameState', () => {
  let state;

  beforeEach(() => {
    state = new GameState();
  });

  describe('initialization', () => {
    test('starts in menu phase', () => {
      expect(state.phase).toBe('menu');
    });

    test('initializes with default values', () => {
      expect(state.score).toBe(0);
      expect(state.level).toBe(1);
      expect(state.lives).toBe(3);
      expect(state.entities).toEqual([]);
    });
  });

  describe('state transitions', () => {
    test('can start game from menu', () => {
      const result = state.start();
      expect(result).toBe(true);
      expect(state.phase).toBe('playing');
    });

    test('cannot start game from non-menu phase', () => {
      state.start();
      const result = state.start();
      expect(result).toBe(false);
      expect(state.phase).toBe('playing');
    });

    test('can pause during gameplay', () => {
      state.start();
      const result = state.pause();
      expect(result).toBe(true);
      expect(state.phase).toBe('paused');
    });

    test('cannot pause when not playing', () => {
      const result = state.pause();
      expect(result).toBe(false);
      expect(state.phase).toBe('menu');
    });

    test('can resume from paused', () => {
      state.start();
      state.pause();
      const result = state.resume();
      expect(result).toBe(true);
      expect(state.phase).toBe('playing');
    });

    test('cannot resume when not paused', () => {
      state.start();
      const result = state.resume();
      expect(result).toBe(false);
    });

    test('transitions to game over', () => {
      state.start();
      state.gameOver();
      expect(state.phase).toBe('gameOver');
    });
  });

  describe('scoring system', () => {
    beforeEach(() => {
      state.start();
    });

    test('adds score during gameplay', () => {
      state.addScore(100);
      expect(state.score).toBe(100);
    });

    test('accumulates score', () => {
      state.addScore(100);
      state.addScore(50);
      expect(state.score).toBe(150);
    });

    test('does not add score when not playing', () => {
      state.pause();
      state.addScore(100);
      expect(state.score).toBe(0);
    });

    test('emits scoreChanged event', () => {
      const callback = jest.fn();
      state.on('scoreChanged', callback);
      state.addScore(100);
      expect(callback).toHaveBeenCalledWith(100);
    });
  });

  describe('lives system', () => {
    beforeEach(() => {
      state.start();
    });

    test('loses a life', () => {
      state.loseLife();
      expect(state.lives).toBe(2);
    });

    test('returns false when lives remaining', () => {
      const result = state.loseLife();
      expect(result).toBe(false);
      expect(state.phase).toBe('playing');
    });

    test('triggers game over when no lives left', () => {
      state.loseLife();
      state.loseLife();
      const result = state.loseLife();
      expect(result).toBe(true);
      expect(state.phase).toBe('gameOver');
    });

    test('does not lose life when not playing', () => {
      state.pause();
      state.loseLife();
      expect(state.lives).toBe(3);
    });

    test('emits lifeChanged event', () => {
      const callback = jest.fn();
      state.on('lifeChanged', callback);
      state.loseLife();
      expect(callback).toHaveBeenCalledWith(2);
    });
  });

  describe('level system', () => {
    beforeEach(() => {
      state.start();
    });

    test('advances to next level', () => {
      state.levelUp();
      expect(state.level).toBe(2);
    });

    test('emits levelChanged event', () => {
      const callback = jest.fn();
      state.on('levelChanged', callback);
      state.levelUp();
      expect(callback).toHaveBeenCalledWith(2);
    });
  });

  describe('entity management', () => {
    test('adds entities', () => {
      const entity = { id: 1, type: 'enemy' };
      state.addEntity(entity);
      expect(state.entities).toContain(entity);
      expect(state.entities.length).toBe(1);
    });

    test('removes entities', () => {
      const entity = { id: 1, type: 'enemy' };
      state.addEntity(entity);
      const result = state.removeEntity(entity);
      expect(result).toBe(true);
      expect(state.entities).not.toContain(entity);
      expect(state.entities.length).toBe(0);
    });

    test('returns false when removing non-existent entity', () => {
      const entity = { id: 1, type: 'enemy' };
      const result = state.removeEntity(entity);
      expect(result).toBe(false);
    });
  });

  describe('event system', () => {
    test('emits started event', () => {
      const callback = jest.fn();
      state.on('started', callback);
      state.start();
      expect(callback).toHaveBeenCalled();
    });

    test('emits gameOver event with data', () => {
      const callback = jest.fn();
      state.on('gameOver', callback);
      state.start();
      state.addScore(500);
      state.gameOver();
      expect(callback).toHaveBeenCalledWith({ score: 500, level: 1 });
    });

    test('supports multiple listeners', () => {
      const callback1 = jest.fn();
      const callback2 = jest.fn();
      state.on('started', callback1);
      state.on('started', callback2);
      state.start();
      expect(callback1).toHaveBeenCalled();
      expect(callback2).toHaveBeenCalled();
    });
  });

  describe('reset', () => {
    test('resets to initial state', () => {
      state.start();
      state.addScore(1000);
      state.levelUp();
      state.loseLife();
      state.reset();

      expect(state.phase).toBe('menu');
      expect(state.score).toBe(0);
      expect(state.level).toBe(1);
      expect(state.lives).toBe(3);
      expect(state.entities).toEqual([]);
    });
  });
});
```

## Testing Physics Calculations

Physics is critical for game feel. Let's test a physics engine:

```javascript
// physics.js
export class PhysicsBody {
  constructor(x, y, width, height) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.vx = 0;
    this.vy = 0;
    this.ax = 0;
    this.ay = 0;
    this.mass = 1;
    this.restitution = 0.8; // Bounciness
    this.friction = 0.1;
  }

  applyForce(fx, fy) {
    this.ax += fx / this.mass;
    this.ay += fy / this.mass;
  }

  update(dt) {
    // Update velocity
    this.vx += this.ax * dt;
    this.vy += this.ay * dt;

    // Apply friction
    this.vx *= (1 - this.friction);
    this.vy *= (1 - this.friction);

    // Update position
    this.x += this.vx * dt;
    this.y += this.vy * dt;

    // Reset acceleration
    this.ax = 0;
    this.ay = 0;
  }

  collidesWith(other) {
    return (
      this.x < other.x + other.width &&
      this.x + this.width > other.x &&
      this.y < other.y + other.height &&
      this.y + this.height > other.y
    );
  }

  resolveCollision(other) {
    // Simple AABB collision response
    const overlapX = Math.min(
      this.x + this.width - other.x,
      other.x + other.width - this.x
    );
    const overlapY = Math.min(
      this.y + this.height - other.y,
      other.y + other.height - this.y
    );

    if (overlapX < overlapY) {
      // Resolve horizontally
      if (this.x < other.x) {
        this.x -= overlapX;
        this.vx = -this.vx * this.restitution;
      } else {
        this.x += overlapX;
        this.vx = -this.vx * this.restitution;
      }
    } else {
      // Resolve vertically
      if (this.y < other.y) {
        this.y -= overlapY;
        this.vy = -this.vy * this.restitution;
      } else {
        this.y += overlapY;
        this.vy = -this.vy * this.restitution;
      }
    }
  }
}

// physics.test.js
import { PhysicsBody } from './physics';

describe('PhysicsBody', () => {
  let body;

  beforeEach(() => {
    body = new PhysicsBody(0, 0, 10, 10);
  });

  describe('initialization', () => {
    test('sets position and size', () => {
      expect(body.x).toBe(0);
      expect(body.y).toBe(0);
      expect(body.width).toBe(10);
      expect(body.height).toBe(10);
    });

    test('initializes with zero velocity', () => {
      expect(body.vx).toBe(0);
      expect(body.vy).toBe(0);
    });

    test('has default physical properties', () => {
      expect(body.mass).toBe(1);
      expect(body.restitution).toBe(0.8);
      expect(body.friction).toBe(0.1);
    });
  });

  describe('force application', () => {
    test('applies force to acceleration', () => {
      body.applyForce(10, 0);
      expect(body.ax).toBe(10);
    });

    test('considers mass when applying force', () => {
      body.mass = 2;
      body.applyForce(10, 0);
      expect(body.ax).toBe(5);
    });

    test('accumulates forces', () => {
      body.applyForce(10, 0);
      body.applyForce(5, 0);
      expect(body.ax).toBe(15);
    });
  });

  describe('physics update', () => {
    test('updates velocity from acceleration', () => {
      body.applyForce(100, 0);
      body.update(1);
      expect(body.vx).toBe(100);
    });

    test('updates position from velocity', () => {
      body.vx = 50;
      body.update(1);
      expect(body.x).toBe(50);
    });

    test('applies friction to velocity', () => {
      body.vx = 100;
      body.friction = 0.1;
      body.update(1);
      expect(body.vx).toBe(90);
    });

    test('resets acceleration after update', () => {
      body.applyForce(100, 0);
      body.update(1);
      expect(body.ax).toBe(0);
    });

    test('respects delta time', () => {
      body.applyForce(100, 0);
      body.update(0.5);
      expect(body.vx).toBe(50);
      expect(body.x).toBe(25);
    });
  });

  describe('collision detection', () => {
    test('detects collision', () => {
      const other = new PhysicsBody(5, 5, 10, 10);
      expect(body.collidesWith(other)).toBe(true);
    });

    test('detects no collision when separated', () => {
      const other = new PhysicsBody(20, 0, 10, 10);
      expect(body.collidesWith(other)).toBe(false);
    });

    test('detects edge collision', () => {
      const other = new PhysicsBody(10, 0, 10, 10);
      expect(body.collidesWith(other)).toBe(false);
    });

    test('detects collision with different sizes', () => {
      const other = new PhysicsBody(5, 5, 20, 20);
      expect(body.collidesWith(other)).toBe(true);
    });
  });

  describe('collision resolution', () => {
    test('resolves horizontal collision', () => {
      const other = new PhysicsBody(5, 0, 10, 10);
      body.vx = 10;
      body.resolveCollision(other);
      expect(body.vx).toBeLessThan(0);
    });

    test('applies restitution to bounce', () => {
      const other = new PhysicsBody(5, 0, 10, 10);
      body.vx = 10;
      body.restitution = 0.8;
      body.resolveCollision(other);
      expect(body.vx).toBe(-8);
    });

    test('separates bodies after collision', () => {
      const other = new PhysicsBody(5, 0, 10, 10);
      body.resolveCollision(other);
      expect(body.collidesWith(other)).toBe(false);
    });
  });
});
```

## Testing AI Behaviors

AI logic is complex and prone to bugs. Let's test an enemy AI:

```javascript
// enemyAI.js
export class EnemyAI {
  constructor(enemy, target) {
    this.enemy = enemy;
    this.target = target;
    this.state = 'idle';
    this.detectionRange = 100;
    this.attackRange = 20;
    this.lastAttackTime = 0;
    this.attackCooldown = 1000;
  }

  update(currentTime) {
    const distance = this.distanceToTarget();

    if (distance > this.detectionRange) {
      this.state = 'idle';
      return 'idle';
    }

    if (distance <= this.attackRange) {
      if (currentTime - this.lastAttackTime >= this.attackCooldown) {
        this.state = 'attacking';
        this.lastAttackTime = currentTime;
        return 'attack';
      }
      this.state = 'waiting';
      return 'wait';
    }

    this.state = 'chasing';
    return 'chase';
  }

  distanceToTarget() {
    const dx = this.target.x - this.enemy.x;
    const dy = this.target.y - this.enemy.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  getChaseDirection() {
    const dx = this.target.x - this.enemy.x;
    const dy = this.target.y - this.enemy.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    return {
      x: dx / distance,
      y: dy / distance,
    };
  }
}

// enemyAI.test.js
import { EnemyAI } from './enemyAI';

describe('EnemyAI', () => {
  let ai, enemy, target;

  beforeEach(() => {
    enemy = { x: 0, y: 0 };
    target = { x: 0, y: 0 };
    ai = new EnemyAI(enemy, target);
  });

  describe('state transitions', () => {
    test('idles when target is far away', () => {
      target.x = 200;
      const action = ai.update(0);
      expect(action).toBe('idle');
      expect(ai.state).toBe('idle');
    });

    test('chases when target is in detection range', () => {
      target.x = 50;
      const action = ai.update(0);
      expect(action).toBe('chase');
      expect(ai.state).toBe('chasing');
    });

    test('attacks when target is in attack range', () => {
      target.x = 15;
      const action = ai.update(0);
      expect(action).toBe('attack');
      expect(ai.state).toBe('attacking');
    });

    test('waits during attack cooldown', () => {
      target.x = 15;
      ai.update(0);
      const action = ai.update(500);
      expect(action).toBe('wait');
      expect(ai.state).toBe('waiting');
    });

    test('attacks again after cooldown', () => {
      target.x = 15;
      ai.update(0);
      ai.update(500);
      const action = ai.update(1000);
      expect(action).toBe('attack');
    });
  });

  describe('distance calculation', () => {
    test('calculates distance correctly', () => {
      target.x = 3;
      target.y = 4;
      expect(ai.distanceToTarget()).toBe(5);
    });

    test('handles same position', () => {
      expect(ai.distanceToTarget()).toBe(0);
    });
  });

  describe('chase behavior', () => {
    test('returns normalized direction vector', () => {
      target.x = 10;
      target.y = 0;
      const direction = ai.getChaseDirection();
      expect(direction.x).toBe(1);
      expect(direction.y).toBe(0);
    });

    test('handles diagonal movement', () => {
      target.x = 10;
      target.y = 10;
      const direction = ai.getChaseDirection();
      expect(direction.x).toBeCloseTo(0.707, 2);
      expect(direction.y).toBeCloseTo(0.707, 2);
    });
  });
});
```

## Complete Pong Test Suite (90%+ Coverage)

Here's a real-world example: testing a complete Pong game:

```javascript
// pong.js
export class PongGame {
  constructor(width = 800, height = 600) {
    this.width = width;
    this.height = height;
    this.reset();
  }

  reset() {
    this.ball = {
      x: this.width / 2,
      y: this.height / 2,
      vx: 5,
      vy: 3,
      radius: 10,
    };

    this.paddle1 = {
      x: 20,
      y: this.height / 2 - 50,
      width: 10,
      height: 100,
      vy: 0,
      speed: 8,
    };

    this.paddle2 = {
      x: this.width - 30,
      y: this.height / 2 - 50,
      width: 10,
      height: 100,
      vy: 0,
      speed: 8,
    };

    this.score = { player1: 0, player2: 0 };
  }

  update() {
    // Update ball position
    this.ball.x += this.ball.vx;
    this.ball.y += this.ball.vy;

    // Ball collision with top/bottom walls
    if (this.ball.y - this.ball.radius <= 0 ||
        this.ball.y + this.ball.radius >= this.height) {
      this.ball.vy = -this.ball.vy;
    }

    // Ball out of bounds (scoring)
    if (this.ball.x - this.ball.radius <= 0) {
      this.score.player2++;
      this.resetBall();
      return 'player2_scored';
    }

    if (this.ball.x + this.ball.radius >= this.width) {
      this.score.player1++;
      this.resetBall();
      return 'player1_scored';
    }

    // Paddle collisions
    if (this.checkPaddleCollision(this.paddle1) ||
        this.checkPaddleCollision(this.paddle2)) {
      this.ball.vx = -this.ball.vx;
    }

    // Update paddles
    this.paddle1.y += this.paddle1.vy;
    this.paddle2.y += this.paddle2.vy;

    // Clamp paddles to screen
    this.paddle1.y = Math.max(0, Math.min(this.height - this.paddle1.height, this.paddle1.y));
    this.paddle2.y = Math.max(0, Math.min(this.height - this.paddle2.height, this.paddle2.y));

    return null;
  }

  checkPaddleCollision(paddle) {
    return (
      this.ball.x - this.ball.radius <= paddle.x + paddle.width &&
      this.ball.x + this.ball.radius >= paddle.x &&
      this.ball.y + this.ball.radius >= paddle.y &&
      this.ball.y - this.ball.radius <= paddle.y + paddle.height
    );
  }

  resetBall() {
    this.ball.x = this.width / 2;
    this.ball.y = this.height / 2;
    this.ball.vx = -this.ball.vx;
  }

  movePaddle1(direction) {
    this.paddle1.vy = direction * this.paddle1.speed;
  }

  movePaddle2(direction) {
    this.paddle2.vy = direction * this.paddle2.speed;
  }
}

// pong.test.js
import { PongGame } from './pong';

describe('PongGame', () => {
  let game;

  beforeEach(() => {
    game = new PongGame(800, 600);
  });

  describe('initialization', () => {
    test('creates game with correct dimensions', () => {
      expect(game.width).toBe(800);
      expect(game.height).toBe(600);
    });

    test('initializes ball at center', () => {
      expect(game.ball.x).toBe(400);
      expect(game.ball.y).toBe(300);
    });

    test('initializes scores at zero', () => {
      expect(game.score.player1).toBe(0);
      expect(game.score.player2).toBe(0);
    });
  });

  describe('ball physics', () => {
    test('ball moves according to velocity', () => {
      const initialX = game.ball.x;
      const initialY = game.ball.y;
      game.update();
      expect(game.ball.x).toBe(initialX + game.ball.vx);
      expect(game.ball.y).toBe(initialY + game.ball.vy);
    });

    test('ball bounces off top wall', () => {
      game.ball.y = 5;
      game.ball.vy = -5;
      game.update();
      expect(game.ball.vy).toBe(5);
    });

    test('ball bounces off bottom wall', () => {
      game.ball.y = 595;
      game.ball.vy = 5;
      game.update();
      expect(game.ball.vy).toBe(-5);
    });
  });

  describe('scoring', () => {
    test('player 2 scores when ball goes left', () => {
      game.ball.x = 5;
      game.ball.vx = -5;
      const result = game.update();
      expect(result).toBe('player2_scored');
      expect(game.score.player2).toBe(1);
    });

    test('player 1 scores when ball goes right', () => {
      game.ball.x = 795;
      game.ball.vx = 5;
      const result = game.update();
      expect(result).toBe('player1_scored');
      expect(game.score.player1).toBe(1);
    });

    test('ball resets after scoring', () => {
      game.ball.x = 5;
      game.update();
      expect(game.ball.x).toBe(400);
      expect(game.ball.y).toBe(300);
    });
  });

  describe('paddle control', () => {
    test('moves paddle 1 up', () => {
      const initialY = game.paddle1.y;
      game.movePaddle1(-1);
      game.update();
      expect(game.paddle1.y).toBe(initialY - game.paddle1.speed);
    });

    test('moves paddle 1 down', () => {
      const initialY = game.paddle1.y;
      game.movePaddle1(1);
      game.update();
      expect(game.paddle1.y).toBe(initialY + game.paddle1.speed);
    });

    test('clamps paddle 1 to top edge', () => {
      game.paddle1.y = 0;
      game.movePaddle1(-1);
      game.update();
      expect(game.paddle1.y).toBe(0);
    });

    test('clamps paddle 1 to bottom edge', () => {
      game.paddle1.y = 500;
      game.movePaddle1(1);
      game.update();
      expect(game.paddle1.y).toBe(500);
    });
  });

  describe('paddle collisions', () => {
    test('ball bounces off paddle 1', () => {
      game.ball.x = 35;
      game.ball.y = game.paddle1.y + 50;
      game.ball.vx = -5;
      game.update();
      expect(game.ball.vx).toBe(5);
    });

    test('ball bounces off paddle 2', () => {
      game.ball.x = 765;
      game.ball.y = game.paddle2.y + 50;
      game.ball.vx = 5;
      game.update();
      expect(game.ball.vx).toBe(-5);
    });
  });
});
```

## TDD Workflow for Games

Test-Driven Development (TDD) works great for games:

1. **Write a failing test**
2. **Write minimal code to pass**
3. **Refactor**
4. **Repeat**

**Example TDD session**:

```javascript
// Step 1: Write failing test
test('power-up increases paddle size', () => {
  const game = new PongGame();
  const originalHeight = game.paddle1.height;
  game.applyPowerUp('grow');
  expect(game.paddle1.height).toBeGreaterThan(originalHeight);
});

// Step 2: Implement feature
applyPowerUp(type) {
  if (type === 'grow') {
    this.paddle1.height *= 1.5;
  }
}

// Step 3: Test passes! Now refactor if needed
```

## Claude Code Prompts for Test Generation

**Generate comprehensive test suite**:
```
Create a complete Jest test suite for this game class:
[paste code]

Include tests for:
- Initialization
- State transitions
- Edge cases
- Boundary conditions
- Error handling

Aim for 90%+ code coverage.
```

**Generate specific test scenarios**:
```
Generate test cases for this collision detection function:
[paste function]

Include:
- Basic collision cases
- Edge cases (touching but not overlapping)
- Different sizes and positions
- Performance edge cases
```

**Generate mocks**:
```
Create Jest mocks for this game's external dependencies:
- Canvas 2D context
- Audio API
- localStorage
- requestAnimationFrame

Include all methods used by the game.
```

**Convert existing code to testable architecture**:
```
Refactor this game code to be more testable:
[paste code]

Separate:
- Pure logic from rendering
- State management from side effects
- Business rules from framework code

Maintain the same behavior but make it unit-testable.
```

## Best Practices

1. **Test behavior, not implementation** - Tests should validate what the code does, not how
2. **Keep tests fast** - Unit tests should run in milliseconds
3. **Use descriptive names** - `test('ball bounces off top wall')` not `test('case 1')`
4. **One assertion per concept** - Test one thing at a time
5. **Arrange-Act-Assert** - Structure tests clearly
6. **Don't test private methods** - Test public interface
7. **Mock external dependencies** - Don't test canvas rendering, test logic
8. **Use beforeEach for setup** - Keep tests DRY
9. **Aim for 80%+ coverage** - But don't obsess over 100%
10. **Test edge cases** - Zero, negative, maximum values

## Common Pitfalls

**Testing rendering logic**: Don't test what pixels are drawn. Test the state that determines what should be drawn.

**Over-mocking**: Mock external APIs, but don't mock your own code.

**Brittle tests**: Tests that break with minor refactoring are testing implementation, not behavior.

**Slow tests**: If unit tests take seconds, you're probably doing integration testing.

## Next Steps

Now that you understand unit testing, move on to [Integration Testing](./integration-testing.md) to test how systems work together, or explore [Playtesting Automation](./playtesting-automation.md) for advanced testing strategies.

**Remember**: Tests are code too. Write them well, refactor them, and let Claude Code help you maintain them.
