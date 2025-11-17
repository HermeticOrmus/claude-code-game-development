# Integration Testing for Games

While unit tests validate individual components, integration tests ensure that multiple systems work together correctly. In games, this means testing how input handling, game state, physics, rendering, and audio coordinate to create the gameplay experience.

## Why Integration Testing Matters

Games are complex systems where components interact in subtle ways:

- **Input system** → **Game state** → **Physics engine** → **Renderer**
- **Collision detection** → **Audio system** → **Score manager**
- **AI controller** → **Pathfinding** → **Animation system**

Bugs often hide at the boundaries between systems. Integration tests catch these issues before they reach players.

## Integration vs Unit Tests

| Unit Tests | Integration Tests |
|------------|-------------------|
| Test single functions/classes | Test multiple systems together |
| Fast (milliseconds) | Slower (seconds) |
| No external dependencies | May use DOM, canvas, etc. |
| Mock everything external | Minimal mocking |
| 70% of test suite | 20% of test suite |

## Testing Multiple Systems Together

### Example: Input → State → Rendering Flow

Let's test how player input flows through a complete game:

```javascript
// game.js
import { InputHandler } from './input';
import { GameState } from './gameState';
import { Renderer } from './renderer';

export class Game {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.state = new GameState();
    this.input = new InputHandler();
    this.renderer = new Renderer(this.ctx);
    this.running = false;
  }

  start() {
    this.state.start();
    this.running = true;
    this.input.enable();
    this.gameLoop();
  }

  stop() {
    this.running = false;
    this.input.disable();
  }

  gameLoop() {
    if (!this.running) return;

    // Process input
    if (this.input.isPressed('ArrowLeft')) {
      this.state.player.moveLeft();
    }
    if (this.input.isPressed('ArrowRight')) {
      this.state.player.moveRight();
    }
    if (this.input.isPressed(' ')) {
      this.state.player.jump();
    }

    // Update game state
    this.state.update();

    // Render
    this.renderer.clear();
    this.renderer.render(this.state);

    requestAnimationFrame(() => this.gameLoop());
  }
}

// input.js
export class InputHandler {
  constructor() {
    this.keys = new Set();
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.handleKeyUp = this.handleKeyUp.bind(this);
  }

  enable() {
    window.addEventListener('keydown', this.handleKeyDown);
    window.addEventListener('keyup', this.handleKeyUp);
  }

  disable() {
    window.removeEventListener('keydown', this.handleKeyDown);
    window.removeEventListener('keyup', this.handleKeyUp);
  }

  handleKeyDown(e) {
    this.keys.add(e.key);
  }

  handleKeyUp(e) {
    this.keys.delete(e.key);
  }

  isPressed(key) {
    return this.keys.has(key);
  }
}

// gameState.js
export class GameState {
  constructor() {
    this.phase = 'menu';
    this.player = {
      x: 100,
      y: 100,
      vx: 0,
      vy: 0,
      speed: 5,
      jumpPower: 10,
      onGround: true,
      moveLeft: () => { this.player.vx = -this.player.speed; },
      moveRight: () => { this.player.vx = this.player.speed; },
      jump: () => {
        if (this.player.onGround) {
          this.player.vy = -this.player.jumpPower;
          this.player.onGround = false;
        }
      },
    };
  }

  start() {
    this.phase = 'playing';
  }

  update() {
    if (this.phase !== 'playing') return;

    // Apply gravity
    this.player.vy += 0.5;

    // Update position
    this.player.x += this.player.vx;
    this.player.y += this.player.vy;

    // Ground collision
    if (this.player.y >= 400) {
      this.player.y = 400;
      this.player.vy = 0;
      this.player.onGround = true;
    }

    // Friction
    this.player.vx *= 0.8;
  }
}
```

### Integration Test Suite

```javascript
// game.integration.test.js
import { Game } from './game';
import { JSDOM } from 'jsdom';

describe('Game Integration Tests', () => {
  let game, canvas, document;

  beforeEach(() => {
    // Setup DOM environment
    const dom = new JSDOM('<!DOCTYPE html><canvas id="game"></canvas>');
    document = dom.window.document;
    global.window = dom.window;
    global.document = document;
    global.requestAnimationFrame = (cb) => setTimeout(cb, 16);
    global.cancelAnimationFrame = clearTimeout;

    canvas = document.getElementById('game');
    canvas.width = 800;
    canvas.height = 600;

    game = new Game(canvas);
  });

  afterEach(() => {
    game.stop();
  });

  describe('Input → State Integration', () => {
    test('arrow keys move player', () => {
      game.start();

      const initialX = game.state.player.x;

      // Simulate key press
      const event = new window.KeyboardEvent('keydown', { key: 'ArrowRight' });
      window.dispatchEvent(event);

      // Run one game loop iteration
      game.gameLoop();

      expect(game.state.player.vx).toBeGreaterThan(0);
    });

    test('spacebar makes player jump when on ground', () => {
      game.start();
      game.state.player.onGround = true;

      const event = new window.KeyboardEvent('keydown', { key: ' ' });
      window.dispatchEvent(event);

      game.gameLoop();

      expect(game.state.player.vy).toBeLessThan(0);
      expect(game.state.player.onGround).toBe(false);
    });

    test('cannot jump while in air', () => {
      game.start();
      game.state.player.onGround = false;

      const event = new window.KeyboardEvent('keydown', { key: ' ' });
      window.dispatchEvent(event);

      const vyBefore = game.state.player.vy;
      game.gameLoop();

      expect(game.state.player.vy).toBe(vyBefore);
    });

    test('key release stops movement input', () => {
      game.start();

      const keydown = new window.KeyboardEvent('keydown', { key: 'ArrowRight' });
      window.dispatchEvent(keydown);
      game.gameLoop();

      const keyup = new window.KeyboardEvent('keyup', { key: 'ArrowRight' });
      window.dispatchEvent(keyup);

      // Velocity should decay due to friction, not continue from input
      const vxAfterRelease = game.state.player.vx;
      game.state.update();
      expect(game.state.player.vx).toBeLessThan(vxAfterRelease);
    });
  });

  describe('State → Physics Integration', () => {
    test('gravity affects player', () => {
      game.start();
      game.state.player.y = 100;
      game.state.player.onGround = false;

      const initialY = game.state.player.y;
      game.state.update();

      expect(game.state.player.y).toBeGreaterThan(initialY);
    });

    test('player lands on ground', () => {
      game.start();
      game.state.player.y = 395;
      game.state.player.vy = 10;

      game.state.update();

      expect(game.state.player.y).toBe(400);
      expect(game.state.player.vy).toBe(0);
      expect(game.state.player.onGround).toBe(true);
    });

    test('friction slows horizontal movement', () => {
      game.start();
      game.state.player.vx = 10;

      const iterations = 5;
      for (let i = 0; i < iterations; i++) {
        game.state.update();
      }

      expect(game.state.player.vx).toBeLessThan(10);
      expect(game.state.player.vx).toBeGreaterThan(0);
    });
  });

  describe('Full Game Loop Integration', () => {
    test('complete input-to-state flow', (done) => {
      game.start();

      const initialX = game.state.player.x;

      // Press right arrow
      const keydown = new window.KeyboardEvent('keydown', { key: 'ArrowRight' });
      window.dispatchEvent(keydown);

      // Let a few frames pass
      setTimeout(() => {
        expect(game.state.player.x).toBeGreaterThan(initialX);
        expect(game.running).toBe(true);
        done();
      }, 50);
    });

    test('stop halts game loop', () => {
      game.start();
      expect(game.running).toBe(true);

      game.stop();
      expect(game.running).toBe(false);
    });
  });
});
```

## Browser Automation with Playwright

Playwright enables testing real games in actual browsers. It's perfect for visual regression testing and complex user interactions.

### Setup

```bash
npm install --save-dev @playwright/test
npx playwright install
```

### Configuration

```javascript
// playwright.config.js
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: true,
  },
});
```

### Playwright Test Examples

```javascript
// tests/e2e/platformer.spec.js
import { test, expect } from '@playwright/test';

test.describe('Platformer Game', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('canvas');
  });

  test('game loads and displays canvas', async ({ page }) => {
    const canvas = await page.locator('canvas');
    await expect(canvas).toBeVisible();

    const boundingBox = await canvas.boundingBox();
    expect(boundingBox.width).toBeGreaterThan(0);
    expect(boundingBox.height).toBeGreaterThan(0);
  });

  test('start button begins game', async ({ page }) => {
    await page.click('button:has-text("Start Game")');

    // Check that game state changed
    const score = await page.locator('#score').textContent();
    expect(score).toBe('0');

    const lives = await page.locator('#lives').textContent();
    expect(lives).toBe('3');
  });

  test('arrow keys control player movement', async ({ page }) => {
    await page.click('button:has-text("Start Game")');

    // Get initial player position via exposed game state
    const initialX = await page.evaluate(() => window.game.state.player.x);

    // Press right arrow
    await page.keyboard.down('ArrowRight');
    await page.waitForTimeout(500);
    await page.keyboard.up('ArrowRight');

    // Check player moved
    const finalX = await page.evaluate(() => window.game.state.player.x);
    expect(finalX).toBeGreaterThan(initialX);
  });

  test('player can jump', async ({ page }) => {
    await page.click('button:has-text("Start Game")');

    const initialY = await page.evaluate(() => window.game.state.player.y);

    // Jump
    await page.keyboard.press('Space');
    await page.waitForTimeout(100);

    const jumpY = await page.evaluate(() => window.game.state.player.y);
    expect(jumpY).toBeLessThan(initialY);
  });

  test('collecting coin increases score', async ({ page }) => {
    await page.click('button:has-text("Start Game")');

    // Expose game state
    await page.evaluate(() => {
      window.game.state.spawnCoin(150, 400);
    });

    // Move to coin
    await page.keyboard.down('ArrowRight');
    await page.waitForTimeout(1000);
    await page.keyboard.up('ArrowRight');

    const score = await page.locator('#score').textContent();
    expect(parseInt(score)).toBeGreaterThan(0);
  });

  test('hitting enemy loses life', async ({ page }) => {
    await page.click('button:has-text("Start Game")');

    const initialLives = await page.evaluate(() => window.game.state.lives);

    // Spawn enemy at player position
    await page.evaluate(() => {
      const px = window.game.state.player.x;
      const py = window.game.state.player.y;
      window.game.state.spawnEnemy(px + 50, py);
    });

    // Move into enemy
    await page.keyboard.down('ArrowRight');
    await page.waitForTimeout(1000);
    await page.keyboard.up('ArrowRight');

    const finalLives = await page.evaluate(() => window.game.state.lives);
    expect(finalLives).toBeLessThan(initialLives);
  });

  test('game over shows when lives depleted', async ({ page }) => {
    await page.click('button:has-text("Start Game")');

    // Force game over
    await page.evaluate(() => {
      window.game.state.lives = 0;
      window.game.state.checkGameOver();
    });

    await page.waitForSelector('text=Game Over');
    const gameOverText = await page.locator('text=Game Over');
    await expect(gameOverText).toBeVisible();
  });

  test('pause works correctly', async ({ page }) => {
    await page.click('button:has-text("Start Game")');

    await page.keyboard.press('Escape');

    const phase = await page.evaluate(() => window.game.state.phase);
    expect(phase).toBe('paused');

    const pausedText = await page.locator('text=Paused');
    await expect(pausedText).toBeVisible();
  });

  test('visual regression - game screen', async ({ page }) => {
    await page.click('button:has-text("Start Game")');
    await page.waitForTimeout(1000);

    // Take screenshot and compare
    await expect(page).toHaveScreenshot('game-screen.png', {
      maxDiffPixels: 100,
    });
  });
});
```

## End-to-End Testing with Cypress

Cypress offers an interactive testing experience with time-travel debugging.

### Setup

```bash
npm install --save-dev cypress
npx cypress open
```

### Cypress Test Examples

```javascript
// cypress/e2e/pong.cy.js
describe('Pong Game', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('loads game successfully', () => {
    cy.get('canvas').should('exist');
    cy.get('#score-player1').should('contain', '0');
    cy.get('#score-player2').should('contain', '0');
  });

  it('starts game on button click', () => {
    cy.get('button').contains('Start').click();

    cy.window().then((win) => {
      expect(win.game.state.phase).to.equal('playing');
    });
  });

  it('controls paddle with keyboard', () => {
    cy.get('button').contains('Start').click();

    cy.window().then((win) => {
      const initialY = win.game.state.paddle1.y;

      cy.get('body').type('{w}');
      cy.wait(100);

      cy.window().then((win) => {
        expect(win.game.state.paddle1.y).to.be.lessThan(initialY);
      });
    });
  });

  it('ball bounces off paddles', () => {
    cy.get('button').contains('Start').click();

    cy.window().then((win) => {
      // Position ball near paddle
      win.game.state.ball.x = 35;
      win.game.state.ball.y = win.game.state.paddle1.y + 50;
      win.game.state.ball.vx = -5;

      const initialVx = win.game.state.ball.vx;

      // Wait for collision
      cy.wait(50);

      cy.window().then((win) => {
        expect(win.game.state.ball.vx).to.not.equal(initialVx);
      });
    });
  });

  it('scores point when ball goes out', () => {
    cy.get('button').contains('Start').click();

    cy.window().then((win) => {
      // Force ball out of bounds
      win.game.state.ball.x = -20;
    });

    cy.wait(100);

    cy.get('#score-player2').should('contain', '1');
  });

  it('full game simulation', () => {
    cy.get('button').contains('Start').click();

    // Play for 10 seconds
    cy.wait(10000);

    // Check that score changed (someone scored)
    cy.window().then((win) => {
      const totalScore = win.game.state.score.player1 + win.game.state.score.player2;
      expect(totalScore).to.be.greaterThan(0);
    });
  });

  it('reset clears score', () => {
    cy.get('button').contains('Start').click();

    cy.window().then((win) => {
      win.game.state.score.player1 = 5;
      win.game.state.score.player2 = 3;
    });

    cy.get('button').contains('Reset').click();

    cy.get('#score-player1').should('contain', '0');
    cy.get('#score-player2').should('contain', '0');
  });
});
```

## Automated Gameplay Testing

Test complete gameplay scenarios by simulating player behavior:

```javascript
// tests/gameplay/scenarios.test.js
import { Game } from '../../src/game';

describe('Gameplay Scenarios', () => {
  let game;

  beforeEach(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 800;
    canvas.height = 600;
    game = new Game(canvas);
  });

  test('complete level playthrough', async () => {
    game.start();

    // Simulate player reaching end of level
    const moves = [
      { key: 'ArrowRight', duration: 2000 },
      { key: ' ', duration: 100 }, // Jump
      { key: 'ArrowRight', duration: 1000 },
      { key: ' ', duration: 100 }, // Jump
      { key: 'ArrowRight', duration: 3000 },
    ];

    for (const move of moves) {
      game.input.keys.add(move.key);
      await sleep(move.duration);
      game.input.keys.delete(move.key);
    }

    expect(game.state.phase).toBe('levelComplete');
  });

  test('player death and respawn', async () => {
    game.start();

    const initialLives = game.state.lives;

    // Force player into hazard
    game.state.player.y = 1000; // Fall off map
    game.state.update();

    expect(game.state.lives).toBe(initialLives - 1);
    expect(game.state.player.y).toBe(100); // Respawn position
  });

  test('combo system awards bonus points', () => {
    game.start();

    // Defeat enemies in quick succession
    const comboTime = 2000;
    const startTime = Date.now();

    for (let i = 0; i < 3; i++) {
      game.state.defeatEnemy();
    }

    const endTime = Date.now();
    const duration = endTime - startTime;

    if (duration < comboTime) {
      expect(game.state.comboMultiplier).toBeGreaterThan(1);
    }
  });

  test('power-up effects expire correctly', async () => {
    game.start();

    game.state.applyPowerUp('invincibility', 1000);
    expect(game.state.player.invincible).toBe(true);

    await sleep(1100);

    expect(game.state.player.invincible).toBe(false);
  });
});

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

## Performance Integration Testing

Test that systems work together efficiently:

```javascript
// tests/performance/integration.test.js
import { Game } from '../../src/game';

describe('Performance Integration', () => {
  let game;

  beforeEach(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 1920;
    canvas.height = 1080;
    game = new Game(canvas);
    game.start();
  });

  test('handles many entities without dropping frames', () => {
    // Spawn 1000 entities
    for (let i = 0; i < 1000; i++) {
      game.state.spawnEnemy(Math.random() * 1920, Math.random() * 1080);
    }

    const frameTimings = [];
    const frames = 60;

    for (let i = 0; i < frames; i++) {
      const start = performance.now();
      game.state.update();
      const end = performance.now();
      frameTimings.push(end - start);
    }

    const avgFrameTime = frameTimings.reduce((a, b) => a + b) / frames;
    const maxFrameTime = Math.max(...frameTimings);

    // Should average under 16ms (60fps)
    expect(avgFrameTime).toBeLessThan(16);
    // No frame should exceed 32ms (30fps minimum)
    expect(maxFrameTime).toBeLessThan(32);
  });

  test('particle system does not degrade performance', () => {
    const start = performance.now();

    // Spawn particles
    for (let i = 0; i < 100; i++) {
      game.particleSystem.emit(400, 300, 50);
    }

    // Run updates
    for (let i = 0; i < 60; i++) {
      game.particleSystem.update();
    }

    const end = performance.now();
    const duration = end - start;

    // Should complete in under 100ms
    expect(duration).toBeLessThan(100);
  });
});
```

## Claude Code Prompts for Integration Testing

**Generate integration test scenarios**:
```
Create Playwright integration tests for this game:
[describe game mechanics]

Test scenarios:
- User starts game
- Player controls work
- Scoring system functions
- Game over condition
- Restart functionality

Include visual regression tests.
```

**Generate E2E test suite**:
```
Create a comprehensive Cypress E2E test suite for this platformer game.

Test:
- Movement (left, right, jump)
- Collision with enemies
- Collision with coins
- Level completion
- Game over scenarios
- Pause/resume
- Settings persistence

Use realistic player behavior patterns.
```

**Convert manual test plan to automated tests**:
```
Convert this manual QA test plan into automated Playwright tests:
[paste test plan]

Generate:
- Test setup/teardown
- Page objects for reusability
- Assertions for each test case
- Screenshot capture on failure
```

## Best Practices

1. **Test user journeys, not implementation** - Focus on player experience
2. **Use page objects** - Encapsulate UI interactions for reusability
3. **Run in CI/CD** - Automate testing on every commit
4. **Test across browsers** - Playwright makes this easy
5. **Capture videos/screenshots** - Debug failures easily
6. **Expose game state** - Make testing easier without changing game code
7. **Balance coverage and speed** - Don't over-test
8. **Test realistic scenarios** - Simulate actual player behavior

## Debugging Integration Tests

**Playwright debug mode**:
```bash
PWDEBUG=1 npx playwright test
```

**Cypress time-travel**:
```javascript
cy.pause(); // Pause test execution
cy.debug(); // Debugger breakpoint
```

**View test videos**:
```bash
npx playwright show-report
```

## Next Steps

Integration tests validate that your game's systems work together. Next, explore [Playtesting Automation](./playtesting-automation.md) to learn advanced techniques for simulating realistic player behavior and discovering edge cases automatically.
