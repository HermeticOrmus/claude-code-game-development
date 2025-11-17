# Playtesting Automation

Automated playtesting goes beyond traditional testing by simulating realistic player behavior to discover bugs, balance issues, and edge cases that manual testing might miss. This guide shows you how to build sophisticated automated playtest systems.

## Why Automate Playtesting?

**Human playtesters are expensive and inconsistent**. They get tired, biased, and miss edge cases. Automated playtesters:

- Run 24/7 without fatigue
- Execute millions of gameplay variations
- Find rare edge cases and exploits
- Regression test gameplay balance
- Validate difficulty curves
- Test accessibility features
- Generate heatmaps and analytics

**Real-world example**: A tower defense game had a subtle bug where specific tower combinations caused a memory leak. Manual testing missed it for months. Automated playtesting found it in 2 hours by systematically testing every tower combination.

## Core Concepts

### 1. Player Behavior Simulation

Model how real players interact with your game:

```javascript
// playerBehavior.js
export class PlayerSimulator {
  constructor(game) {
    this.game = game;
    this.personality = this.generatePersonality();
    this.reactionTime = 100 + Math.random() * 400; // 100-500ms
    this.accuracy = 0.7 + Math.random() * 0.3; // 70-100%
    this.aggression = Math.random(); // 0 = defensive, 1 = aggressive
    this.patience = Math.random(); // How long they'll try before giving up
  }

  generatePersonality() {
    const types = ['aggressive', 'defensive', 'explorer', 'speedrunner', 'completionist'];
    return types[Math.floor(Math.random() * types.length)];
  }

  async playLevel(maxTime = 60000) {
    const startTime = Date.now();
    const actions = [];

    while (Date.now() - startTime < maxTime) {
      const action = this.chooseAction();
      actions.push(action);

      await this.executeAction(action);
      await this.wait(this.reactionTime);

      // Check if level completed or failed
      if (this.game.state.phase === 'levelComplete') {
        return { success: true, actions, time: Date.now() - startTime };
      }
      if (this.game.state.phase === 'gameOver') {
        return { success: false, actions, time: Date.now() - startTime };
      }
    }

    return { success: false, actions, time: maxTime, reason: 'timeout' };
  }

  chooseAction() {
    const state = this.game.state;
    const player = state.player;

    // Personality-based decision making
    switch (this.personality) {
      case 'aggressive':
        return this.aggressiveStrategy(state, player);
      case 'defensive':
        return this.defensiveStrategy(state, player);
      case 'explorer':
        return this.explorerStrategy(state, player);
      case 'speedrunner':
        return this.speedrunnerStrategy(state, player);
      case 'completionist':
        return this.completionistStrategy(state, player);
      default:
        return this.randomStrategy();
    }
  }

  aggressiveStrategy(state, player) {
    // Find nearest enemy
    const enemies = state.entities.filter(e => e.type === 'enemy');
    if (enemies.length === 0) {
      return { type: 'move', direction: 'right' };
    }

    const nearest = this.findNearest(player, enemies);
    return this.moveToward(player, nearest);
  }

  defensiveStrategy(state, player) {
    // Avoid enemies, collect power-ups
    const enemies = state.entities.filter(e => e.type === 'enemy');
    const powerups = state.entities.filter(e => e.type === 'powerup');

    if (this.isThreatNearby(player, enemies, 100)) {
      const safestDirection = this.findSafestDirection(player, enemies);
      return { type: 'move', direction: safestDirection };
    }

    if (powerups.length > 0) {
      const nearest = this.findNearest(player, powerups);
      return this.moveToward(player, nearest);
    }

    return { type: 'move', direction: 'right' };
  }

  explorerStrategy(state, player) {
    // Try to visit all areas, collect everything
    const unvisited = this.findUnvisitedAreas(state);
    if (unvisited.length > 0) {
      return this.moveToward(player, unvisited[0]);
    }

    const collectibles = state.entities.filter(e => e.type === 'coin' || e.type === 'powerup');
    if (collectibles.length > 0) {
      const nearest = this.findNearest(player, collectibles);
      return this.moveToward(player, nearest);
    }

    return { type: 'move', direction: Math.random() > 0.5 ? 'right' : 'left' };
  }

  speedrunnerStrategy(state, player) {
    // Move right as fast as possible, only dodge if necessary
    const enemies = state.entities.filter(e => e.type === 'enemy');
    const immediateThreat = this.isThreatNearby(player, enemies, 50);

    if (immediateThreat) {
      return { type: 'jump' };
    }

    return { type: 'move', direction: 'right', sprint: true };
  }

  completionistStrategy(state, player) {
    // Collect everything, defeat all enemies
    const collectibles = state.entities.filter(e =>
      e.type === 'coin' || e.type === 'powerup' || e.type === 'secret'
    );

    if (collectibles.length > 0) {
      const nearest = this.findNearest(player, collectibles);
      return this.moveToward(player, nearest);
    }

    const enemies = state.entities.filter(e => e.type === 'enemy');
    if (enemies.length > 0) {
      const nearest = this.findNearest(player, enemies);
      return this.moveToward(player, nearest);
    }

    return { type: 'move', direction: 'right' };
  }

  async executeAction(action) {
    const game = this.game;

    // Add human-like imprecision
    const shouldMiss = Math.random() > this.accuracy;
    if (shouldMiss && action.type === 'jump') {
      return; // Miss the jump input
    }

    switch (action.type) {
      case 'move':
        game.input.keys.add(action.direction === 'right' ? 'ArrowRight' : 'ArrowLeft');
        await this.wait(100);
        game.input.keys.delete(action.direction === 'right' ? 'ArrowRight' : 'ArrowLeft');
        break;

      case 'jump':
        game.input.keys.add(' ');
        await this.wait(50);
        game.input.keys.delete(' ');
        break;

      case 'attack':
        game.input.keys.add('x');
        await this.wait(100);
        game.input.keys.delete('x');
        break;
    }
  }

  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  findNearest(from, entities) {
    let nearest = entities[0];
    let minDist = Infinity;

    for (const entity of entities) {
      const dist = Math.hypot(entity.x - from.x, entity.y - from.y);
      if (dist < minDist) {
        minDist = dist;
        nearest = entity;
      }
    }

    return nearest;
  }

  isThreatNearby(player, enemies, range) {
    return enemies.some(e => Math.hypot(e.x - player.x, e.y - player.y) < range);
  }

  findSafestDirection(player, enemies) {
    const directions = ['left', 'right'];
    let safest = directions[0];
    let maxDistance = 0;

    for (const dir of directions) {
      const testX = player.x + (dir === 'right' ? 50 : -50);
      const minDist = Math.min(...enemies.map(e => Math.abs(e.x - testX)));

      if (minDist > maxDistance) {
        maxDistance = minDist;
        safest = dir;
      }
    }

    return safest;
  }

  moveToward(from, target) {
    if (target.x > from.x) {
      return { type: 'move', direction: 'right' };
    } else {
      return { type: 'move', direction: 'left' };
    }
  }

  findUnvisitedAreas(state) {
    // Track areas player has visited
    if (!this.visitedAreas) {
      this.visitedAreas = new Set();
    }

    const player = state.player;
    const currentArea = Math.floor(player.x / 100);
    this.visitedAreas.add(currentArea);

    // Return coordinates of unvisited areas
    const unvisited = [];
    for (let i = 0; i < state.levelWidth / 100; i++) {
      if (!this.visitedAreas.has(i)) {
        unvisited.push({ x: i * 100, y: player.y });
      }
    }

    return unvisited;
  }

  randomStrategy() {
    const actions = [
      { type: 'move', direction: 'right' },
      { type: 'move', direction: 'left' },
      { type: 'jump' },
      { type: 'attack' },
    ];

    return actions[Math.floor(Math.random() * actions.length)];
  }
}
```

### 2. Recording and Replaying Gameplay

Capture player inputs for regression testing:

```javascript
// gameRecorder.js
export class GameRecorder {
  constructor(game) {
    this.game = game;
    this.recording = null;
    this.playback = null;
  }

  startRecording() {
    this.recording = {
      seed: Math.random(), // For deterministic replay
      inputs: [],
      startTime: Date.now(),
      initialState: this.captureState(),
    };

    this.originalInputHandler = this.game.input;
    this.game.input = new RecordingInputHandler(this.originalInputHandler, this.recording);
  }

  stopRecording() {
    if (!this.recording) return null;

    this.recording.endTime = Date.now();
    this.recording.finalState = this.captureState();

    this.game.input = this.originalInputHandler;

    const recorded = this.recording;
    this.recording = null;
    return recorded;
  }

  async replay(recording, options = {}) {
    const { speed = 1, onFrame = null } = options;

    // Restore initial state
    this.restoreState(recording.initialState);

    // Set seed for deterministic behavior
    Math.seedrandom(recording.seed);

    const startTime = Date.now();
    let currentInputIndex = 0;

    return new Promise((resolve) => {
      const replayFrame = () => {
        const elapsed = (Date.now() - startTime) * speed;

        // Process inputs that should have happened by now
        while (currentInputIndex < recording.inputs.length) {
          const input = recording.inputs[currentInputIndex];
          if (input.timestamp > elapsed) break;

          this.applyInput(input);
          currentInputIndex++;
        }

        // Update game
        this.game.update();

        if (onFrame) {
          onFrame(this.game.state);
        }

        // Check if replay complete
        if (currentInputIndex >= recording.inputs.length) {
          resolve({
            success: true,
            finalState: this.captureState(),
            expectedState: recording.finalState,
          });
        } else {
          requestAnimationFrame(replayFrame);
        }
      };

      requestAnimationFrame(replayFrame);
    });
  }

  captureState() {
    return JSON.parse(JSON.stringify(this.game.state));
  }

  restoreState(state) {
    Object.assign(this.game.state, JSON.parse(JSON.stringify(state)));
  }

  applyInput(input) {
    if (input.type === 'keydown') {
      this.game.input.keys.add(input.key);
    } else if (input.type === 'keyup') {
      this.game.input.keys.delete(input.key);
    }
  }

  async compareStates(state1, state2, tolerance = 0.01) {
    // Compare two game states for differences
    const diffs = [];

    for (const key in state1) {
      if (typeof state1[key] === 'number') {
        const diff = Math.abs(state1[key] - state2[key]);
        if (diff > tolerance) {
          diffs.push({ key, expected: state1[key], actual: state2[key], diff });
        }
      }
    }

    return diffs;
  }
}

class RecordingInputHandler {
  constructor(originalHandler, recording) {
    this.originalHandler = originalHandler;
    this.recording = recording;
    this.keys = new Set();
  }

  handleKeyDown(e) {
    this.recording.inputs.push({
      type: 'keydown',
      key: e.key,
      timestamp: Date.now() - this.recording.startTime,
    });
    this.keys.add(e.key);
    this.originalHandler.handleKeyDown(e);
  }

  handleKeyUp(e) {
    this.recording.inputs.push({
      type: 'keyup',
      key: e.key,
      timestamp: Date.now() - this.recording.startTime,
    });
    this.keys.delete(e.key);
    this.originalHandler.handleKeyUp(e);
  }

  isPressed(key) {
    return this.keys.has(key);
  }
}
```

### 3. Automated Playtest Suite

Run systematic playtests to find bugs:

```javascript
// playtestSuite.test.js
import { Game } from '../src/game';
import { PlayerSimulator } from './playerBehavior';
import { GameRecorder } from './gameRecorder';

describe('Automated Playtesting', () => {
  test('100 random playthroughs complete without crashes', async () => {
    const crashes = [];
    const completions = { success: 0, failure: 0, timeout: 0 };

    for (let i = 0; i < 100; i++) {
      const canvas = document.createElement('canvas');
      const game = new Game(canvas);
      const player = new PlayerSimulator(game);

      try {
        game.start();
        const result = await player.playLevel(30000);

        if (result.success) {
          completions.success++;
        } else if (result.reason === 'timeout') {
          completions.timeout++;
        } else {
          completions.failure++;
        }
      } catch (error) {
        crashes.push({
          playthrough: i,
          error: error.message,
          personality: player.personality,
        });
      }
    }

    console.log('Playtesting Results:', completions);
    expect(crashes.length).toBe(0);
  });

  test('different player personalities can complete level', async () => {
    const personalities = ['aggressive', 'defensive', 'explorer', 'speedrunner', 'completionist'];
    const results = {};

    for (const personality of personalities) {
      const successes = [];

      for (let i = 0; i < 10; i++) {
        const canvas = document.createElement('canvas');
        const game = new Game(canvas);
        const player = new PlayerSimulator(game);
        player.personality = personality;

        game.start();
        const result = await player.playLevel(60000);
        successes.push(result.success);
      }

      const successRate = successes.filter(s => s).length / successes.length;
      results[personality] = successRate;
    }

    console.log('Success rates by personality:', results);

    // All personalities should have at least 30% success rate
    for (const personality in results) {
      expect(results[personality]).toBeGreaterThan(0.3);
    }
  });

  test('recorded gameplay is deterministically replayable', async () => {
    const canvas = document.createElement('canvas');
    const game = new Game(canvas);
    const recorder = new GameRecorder(game);

    // Record a playthrough
    recorder.startRecording();
    const player = new PlayerSimulator(game);
    game.start();
    await player.playLevel(10000);
    const recording = recorder.stopRecording();

    // Replay multiple times
    const replays = [];
    for (let i = 0; i < 3; i++) {
      const replayResult = await recorder.replay(recording);
      replays.push(replayResult.finalState);
    }

    // All replays should produce identical state
    for (let i = 1; i < replays.length; i++) {
      const diffs = await recorder.compareStates(replays[0], replays[i]);
      expect(diffs.length).toBe(0);
    }
  });

  test('no memory leaks during extended play', async () => {
    const canvas = document.createElement('canvas');
    const game = new Game(canvas);
    const player = new PlayerSimulator(game);

    game.start();

    const initialMemory = performance.memory?.usedJSHeapSize || 0;
    const samples = [];

    // Play for 5 minutes
    for (let i = 0; i < 300; i++) {
      await player.playLevel(1000);

      if (i % 30 === 0) {
        const currentMemory = performance.memory?.usedJSHeapSize || 0;
        samples.push(currentMemory);
      }
    }

    // Memory shouldn't grow unbounded
    const finalMemory = samples[samples.length - 1];
    const memoryGrowth = finalMemory - initialMemory;
    const growthPercent = (memoryGrowth / initialMemory) * 100;

    expect(growthPercent).toBeLessThan(50); // Less than 50% memory growth
  });

  test('all collectibles are reachable', async () => {
    const canvas = document.createElement('canvas');
    const game = new Game(canvas);
    const player = new PlayerSimulator(game);
    player.personality = 'completionist';

    game.start();

    const totalCollectibles = game.state.entities.filter(e => e.type === 'coin').length;

    await player.playLevel(120000); // 2 minutes

    const remainingCollectibles = game.state.entities.filter(e => e.type === 'coin').length;
    const collectedPercent = ((totalCollectibles - remainingCollectibles) / totalCollectibles) * 100;

    // Should be able to collect at least 90% of items
    expect(collectedPercent).toBeGreaterThan(90);
  });
});
```

## Performance Regression Testing

Detect performance degradation automatically:

```javascript
// performancePlaytest.test.js
import { Game } from '../src/game';
import { PlayerSimulator } from './playerBehavior';

describe('Performance Regression Tests', () => {
  test('maintains 60fps during typical gameplay', async () => {
    const canvas = document.createElement('canvas');
    const game = new Game(canvas);
    const player = new PlayerSimulator(game);

    game.start();

    const frameTimes = [];
    const measureDuration = 5000; // 5 seconds
    const startTime = Date.now();

    while (Date.now() - startTime < measureDuration) {
      const frameStart = performance.now();

      game.update();
      await player.executeAction(player.chooseAction());

      const frameEnd = performance.now();
      frameTimes.push(frameEnd - frameStart);
    }

    const avgFrameTime = frameTimes.reduce((a, b) => a + b) / frameTimes.length;
    const maxFrameTime = Math.max(...frameTimes);
    const fps = 1000 / avgFrameTime;

    console.log(`Average FPS: ${fps.toFixed(2)}`);
    console.log(`Max frame time: ${maxFrameTime.toFixed(2)}ms`);

    expect(fps).toBeGreaterThan(55); // Allow slight variance from 60
    expect(maxFrameTime).toBeLessThan(32); // No frame should be slower than 30fps
  });

  test('particle system scales gracefully', () => {
    const canvas = document.createElement('canvas');
    const game = new Game(canvas);

    const results = [];

    for (let particleCount = 100; particleCount <= 1000; particleCount += 100) {
      // Spawn particles
      for (let i = 0; i < particleCount; i++) {
        game.particleSystem.emit(400, 300, 1);
      }

      // Measure update time
      const iterations = 100;
      const start = performance.now();

      for (let i = 0; i < iterations; i++) {
        game.particleSystem.update();
      }

      const end = performance.now();
      const avgTime = (end - start) / iterations;

      results.push({ count: particleCount, time: avgTime });

      game.particleSystem.clear();
    }

    // Performance should scale linearly (O(n))
    const timeRatio = results[results.length - 1].time / results[0].time;
    const countRatio = results[results.length - 1].count / results[0].count;

    expect(timeRatio).toBeLessThan(countRatio * 1.5); // Allow 50% overhead
  });
});
```

## AI-Assisted Bug Discovery

Use AI to explore edge cases:

```javascript
// aiBugHunter.js
export class AIBugHunter {
  constructor(game) {
    this.game = game;
    this.bugReports = [];
    this.exploredStates = new Set();
  }

  async hunt(duration = 60000) {
    const startTime = Date.now();
    let iteration = 0;

    while (Date.now() - startTime < duration) {
      iteration++;

      // Try unusual input combinations
      const inputSequence = this.generateUnusualInputs();

      try {
        await this.executeSequence(inputSequence);

        // Check for anomalies
        const anomalies = this.detectAnomalies();
        if (anomalies.length > 0) {
          this.bugReports.push({
            iteration,
            inputs: inputSequence,
            anomalies,
            state: this.captureState(),
          });
        }
      } catch (error) {
        this.bugReports.push({
          iteration,
          inputs: inputSequence,
          error: error.message,
          stack: error.stack,
          state: this.captureState(),
        });
      }

      this.game.reset();
    }

    return this.bugReports;
  }

  generateUnusualInputs() {
    const sequences = [
      // Rapid button mashing
      () => Array(20).fill().map(() => ({ key: ' ', duration: 10 })),

      // Simultaneous opposite directions
      () => [
        { key: 'ArrowLeft', duration: 100 },
        { key: 'ArrowRight', duration: 100 },
      ],

      // Very long holds
      () => [{ key: 'ArrowRight', duration: 10000 }],

      // Random chaos
      () => Array(50).fill().map(() => ({
        key: ['ArrowLeft', 'ArrowRight', ' ', 'x'][Math.floor(Math.random() * 4)],
        duration: Math.random() * 100,
      })),

      // Pause/unpause spam
      () => Array(10).fill().map(() => ({ key: 'Escape', duration: 50 })),
    ];

    return sequences[Math.floor(Math.random() * sequences.length)]();
  }

  async executeSequence(sequence) {
    for (const input of sequence) {
      this.game.input.keys.add(input.key);
      await this.wait(input.duration);
      this.game.input.keys.delete(input.key);
      this.game.update();
    }
  }

  detectAnomalies() {
    const anomalies = [];
    const state = this.game.state;

    // Check for NaN or Infinity
    if (isNaN(state.player.x) || !isFinite(state.player.x)) {
      anomalies.push({ type: 'invalid_position', value: state.player.x });
    }

    // Check for player out of bounds
    if (state.player.x < -1000 || state.player.x > 10000) {
      anomalies.push({ type: 'out_of_bounds', position: state.player.x });
    }

    // Check for negative score
    if (state.score < 0) {
      anomalies.push({ type: 'negative_score', score: state.score });
    }

    // Check for too many entities (memory leak indicator)
    if (state.entities.length > 1000) {
      anomalies.push({ type: 'entity_leak', count: state.entities.length });
    }

    return anomalies;
  }

  captureState() {
    return JSON.parse(JSON.stringify(this.game.state));
  }

  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

## Claude Code Prompts for Playtesting Automation

**Generate player behavior simulator**:
```
Create a PlayerSimulator class that mimics human gameplay for this game:
[describe game mechanics]

Include personalities:
- Aggressive (rushes enemies)
- Defensive (avoids danger)
- Explorer (finds secrets)
- Speedrunner (fastest route)

Add realistic reaction times and accuracy.
```

**Generate automated playtest suite**:
```
Create automated playtests for this game that:
1. Run 100+ random playthroughs
2. Test different player skill levels
3. Find edge cases and exploits
4. Measure performance under load
5. Generate bug reports

Include tests for:
- Crash detection
- Memory leaks
- Performance regression
- Unreachable content
```

**Generate replay system**:
```
Create a game recording and replay system that:
- Records all player inputs with timestamps
- Saves game state snapshots
- Replays deterministically
- Compares replays for consistency
- Supports slow-motion and frame-by-frame analysis

Make it useful for debugging and regression testing.
```

## Best Practices

1. **Test at multiple skill levels** - Simulate novice, intermediate, and expert players
2. **Record failures** - Save input sequences that cause crashes
3. **Use deterministic randomness** - Seed RNG for reproducible tests
4. **Monitor performance** - Track FPS, memory, and CPU usage
5. **Test edge cases** - Unusual input combinations reveal bugs
6. **Analyze heatmaps** - Where do players go? Where do they die?
7. **Regression test** - Replay saved sessions after each update

## Measuring Success

Track these metrics:

- **Crash rate**: Crashes per 1000 playthroughs
- **Completion rate**: % of simulated players who finish
- **Average completion time**: How long does it take?
- **Death hotspots**: Where do players die most?
- **Performance profile**: FPS over time
- **Memory usage**: Any leaks or unbounded growth?

## Next Steps

Automated playtesting is powerful, but it needs infrastructure. Learn how to integrate these tests into your workflow with [CI/CD Pipelines](./ci-cd-pipelines.md).
