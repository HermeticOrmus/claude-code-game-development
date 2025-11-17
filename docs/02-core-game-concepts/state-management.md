# State Management in Game Development

Game state management is the art and science of organizing, tracking, and updating all the data that defines your game at any given moment. From menu screens to player health, from level progress to enemy AI behaviors, effective state management is what separates well-architected games from unmaintainable spaghetti code.

## Table of Contents

1. [What is Game State?](#what-is-game-state)
2. [Why State Management Matters](#why-state-management-matters)
3. [Simple State Objects](#simple-state-objects)
4. [State Machines](#state-machines)
5. [Game Phase Management](#game-phase-management)
6. [Separating State Concerns](#separating-state-concerns)
7. [State Persistence and Save Systems](#state-persistence-and-save-systems)
8. [Complete Implementations](#complete-implementations)
9. [Best Practices and Anti-Patterns](#best-practices-and-anti-patterns)

## What is Game State?

Game state is all the data that defines the current condition of your game. This includes:

- **Game Phase**: Menu, playing, paused, game over
- **Player State**: Position, health, inventory, abilities
- **World State**: Level data, enemy positions, collectibles
- **UI State**: Menu selections, dialog state, notifications
- **Meta State**: Settings, save progress, achievements
- **Session State**: Scores, time played, difficulty level

At any point in time, if you could serialize all this data and restore it later, you could perfectly recreate the game state. This is exactly what save systems do.

## Why State Management Matters

### Code Organization

Without proper state management, game logic becomes tangled. You end up with global variables scattered across files, functions that can't determine the current game phase, and bugs that appear because different parts of the code have inconsistent views of the game state.

### Debugging and Testing

Good state management makes debugging trivial. You can log the current state, replay states, and even time-travel through state history. Testing becomes easier because you can set up specific states without playing through the entire game.

### Save Systems and Serialization

If your state is well-organized, implementing save/load becomes straightforward. You just serialize the state object to JSON or another format and restore it later.

### Networking and Multiplayer

Multiplayer games need to synchronize state across clients. Clean state management makes this possible by clearly defining what needs to be synchronized.

### Undo/Redo Systems

Games like puzzle games or strategy games often need undo functionality. With proper state management, you just store previous states and restore them when the player hits undo.

## Simple State Objects

The simplest form of state management is a single object containing all game state.

### Claude Code Prompt

```
Prompt: "Create a simple game state object for a platformer that includes
player position, velocity, health, score, level number, and game status
(menu, playing, paused, game over). Include methods to reset state and
get/set individual properties."
```

### Implementation

```javascript
class SimpleGameState {
    constructor() {
        this.reset();
    }

    reset() {
        // Game phase
        this.status = 'menu'; // menu, playing, paused, gameover

        // Player state
        this.player = {
            x: 100,
            y: 300,
            vx: 0,
            vy: 0,
            health: 100,
            lives: 3,
            invincible: false,
            invincibleTimer: 0
        };

        // World state
        this.level = 1;
        this.score = 0;
        this.time = 0;
        this.coins = 0;
        this.checkpointX = 100;
        this.checkpointY = 300;

        // Collectibles and enemies
        this.collectedItems = [];
        this.defeatedEnemies = [];
    }

    // Getters for common state
    isPlaying() {
        return this.status === 'playing';
    }

    isPaused() {
        return this.status === 'paused';
    }

    isGameOver() {
        return this.status === 'gameover';
    }

    // State transitions
    startGame() {
        this.status = 'playing';
        this.reset();
    }

    pauseGame() {
        if (this.status === 'playing') {
            this.status = 'paused';
        }
    }

    resumeGame() {
        if (this.status === 'paused') {
            this.status = 'playing';
        }
    }

    endGame() {
        this.status = 'gameover';
    }

    // Player actions
    takeDamage(amount) {
        if (!this.player.invincible && this.status === 'playing') {
            this.player.health -= amount;

            if (this.player.health <= 0) {
                this.playerDie();
            } else {
                // Invincibility frames
                this.player.invincible = true;
                this.player.invincibleTimer = 2.0; // 2 seconds
            }
        }
    }

    playerDie() {
        this.player.lives--;

        if (this.player.lives > 0) {
            // Respawn at checkpoint
            this.player.x = this.checkpointX;
            this.player.y = this.checkpointY;
            this.player.health = 100;
            this.player.vx = 0;
            this.player.vy = 0;
        } else {
            // Game over
            this.endGame();
        }
    }

    collectCoin() {
        this.coins++;
        this.score += 100;

        // Extra life every 100 coins
        if (this.coins % 100 === 0) {
            this.player.lives++;
        }
    }

    setCheckpoint(x, y) {
        this.checkpointX = x;
        this.checkpointY = y;
    }

    nextLevel() {
        this.level++;
        this.player.x = 100;
        this.player.y = 300;
        this.player.vx = 0;
        this.player.vy = 0;
        this.collectedItems = [];
        this.defeatedEnemies = [];
    }

    update(dt) {
        if (this.status !== 'playing') return;

        // Update time
        this.time += dt;

        // Update invincibility timer
        if (this.player.invincible) {
            this.player.invincibleTimer -= dt;
            if (this.player.invincibleTimer <= 0) {
                this.player.invincible = false;
                this.player.invincibleTimer = 0;
            }
        }
    }

    // Serialization for save/load
    toJSON() {
        return {
            status: this.status,
            player: { ...this.player },
            level: this.level,
            score: this.score,
            time: this.time,
            coins: this.coins,
            checkpointX: this.checkpointX,
            checkpointY: this.checkpointY,
            collectedItems: [...this.collectedItems],
            defeatedEnemies: [...this.defeatedEnemies]
        };
    }

    fromJSON(data) {
        Object.assign(this, data);
    }

    clone() {
        const cloned = new SimpleGameState();
        cloned.fromJSON(this.toJSON());
        return cloned;
    }
}

// Usage
const gameState = new SimpleGameState();
gameState.startGame();
gameState.collectCoin();
gameState.takeDamage(20);
console.log(`Player health: ${gameState.player.health}`);
console.log(`Score: ${gameState.score}`);
```

### Advantages and Limitations

**Advantages:**
- Simple and easy to understand
- All state in one place
- Easy to serialize for save/load
- Good for small to medium games

**Limitations:**
- Can become unwieldy for large games
- No clear state transition logic
- Doesn't scale well with complexity
- Hard to enforce invariants

## State Machines

State machines provide structure for managing state transitions. Each state is explicit, and transitions between states are well-defined.

### Claude Code Prompt

```
Prompt: "Create a finite state machine for managing game phases (menu, playing,
paused, game over). Each state should have enter, update, and exit methods.
Include state transition validation to prevent invalid transitions. Add visual
indicators showing the current state."
```

### Implementation

```javascript
class GameStateMachine {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Define all possible states
        this.states = {
            menu: new MenuState(this),
            playing: new PlayingState(this),
            paused: new PausedState(this),
            gameover: new GameOverState(this)
        };

        this.currentState = null;
        this.previousState = null;

        // Shared game data
        this.gameData = {
            score: 0,
            level: 1,
            highScore: 0
        };

        // Start in menu state
        this.changeState('menu');
    }

    changeState(stateName) {
        // Validate state exists
        if (!this.states[stateName]) {
            console.error(`State '${stateName}' does not exist`);
            return false;
        }

        // Validate transition
        if (this.currentState && !this.currentState.canTransitionTo(stateName)) {
            console.warn(`Cannot transition from ${this.currentState.name} to ${stateName}`);
            return false;
        }

        // Exit current state
        if (this.currentState) {
            this.currentState.exit();
            this.previousState = this.currentState;
        }

        // Enter new state
        this.currentState = this.states[stateName];
        this.currentState.enter();

        console.log(`State transition: ${this.previousState?.name || 'none'} -> ${this.currentState.name}`);
        return true;
    }

    update(dt) {
        if (this.currentState) {
            this.currentState.update(dt);
        }
    }

    render() {
        if (this.currentState) {
            this.currentState.render(this.ctx);
        }
    }

    handleInput(input) {
        if (this.currentState) {
            this.currentState.handleInput(input);
        }
    }
}

// Base State class
class State {
    constructor(stateMachine, name) {
        this.stateMachine = stateMachine;
        this.name = name;
        this.allowedTransitions = [];
    }

    enter() {
        console.log(`Entering ${this.name} state`);
    }

    exit() {
        console.log(`Exiting ${this.name} state`);
    }

    update(dt) {
        // Override in subclasses
    }

    render(ctx) {
        // Override in subclasses
    }

    handleInput(input) {
        // Override in subclasses
    }

    canTransitionTo(stateName) {
        return this.allowedTransitions.length === 0 ||
               this.allowedTransitions.includes(stateName);
    }
}

// Menu State
class MenuState extends State {
    constructor(stateMachine) {
        super(stateMachine, 'menu');
        this.allowedTransitions = ['playing'];
        this.selectedOption = 0;
        this.options = ['Start Game', 'Options', 'Quit'];
    }

    enter() {
        super.enter();
        this.selectedOption = 0;
    }

    update(dt) {
        // Menu animations could go here
    }

    render(ctx) {
        const canvas = ctx.canvas;

        // Clear screen
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Title
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 48px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('GAME MENU', canvas.width / 2, 100);

        // Options
        ctx.font = '32px Arial';
        this.options.forEach((option, index) => {
            const y = 200 + index * 60;

            if (index === this.selectedOption) {
                ctx.fillStyle = '#ffaa00';
                ctx.fillText('> ' + option + ' <', canvas.width / 2, y);
            } else {
                ctx.fillStyle = '#888888';
                ctx.fillText(option, canvas.width / 2, y);
            }
        });

        // High score
        ctx.fillStyle = '#ffffff';
        ctx.font = '20px Arial';
        ctx.fillText(`High Score: ${this.stateMachine.gameData.highScore}`,
                     canvas.width / 2, canvas.height - 50);
    }

    handleInput(input) {
        if (input.type === 'keydown') {
            switch (input.key) {
                case 'ArrowUp':
                    this.selectedOption = (this.selectedOption - 1 + this.options.length) % this.options.length;
                    break;
                case 'ArrowDown':
                    this.selectedOption = (this.selectedOption + 1) % this.options.length;
                    break;
                case 'Enter':
                    if (this.selectedOption === 0) {
                        this.stateMachine.changeState('playing');
                    }
                    break;
            }
        }
    }
}

// Playing State
class PlayingState extends State {
    constructor(stateMachine) {
        super(stateMachine, 'playing');
        this.allowedTransitions = ['paused', 'gameover'];
        this.playerX = 50;
        this.playerY = 200;
        this.playerSpeed = 200;
    }

    enter() {
        super.enter();
        this.stateMachine.gameData.score = 0;
        this.playerX = 50;
        this.playerY = 200;
    }

    update(dt) {
        // Simple score incrementing
        this.stateMachine.gameData.score += dt * 10;

        // Check game over condition (for demo, after score reaches 1000)
        if (this.stateMachine.gameData.score >= 1000) {
            if (this.stateMachine.gameData.score > this.stateMachine.gameData.highScore) {
                this.stateMachine.gameData.highScore = Math.floor(this.stateMachine.gameData.score);
            }
            this.stateMachine.changeState('gameover');
        }
    }

    render(ctx) {
        const canvas = ctx.canvas;

        // Clear screen
        ctx.fillStyle = '#0f0f1e';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Player (simple square)
        ctx.fillStyle = '#00ff00';
        ctx.fillRect(this.playerX, this.playerY, 40, 40);

        // Score
        ctx.fillStyle = '#ffffff';
        ctx.font = '24px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(`Score: ${Math.floor(this.stateMachine.gameData.score)}`, 10, 30);

        // Instructions
        ctx.font = '16px Arial';
        ctx.fillText('Press ESC to pause', 10, canvas.height - 20);
    }

    handleInput(input) {
        if (input.type === 'keydown') {
            switch (input.key) {
                case 'Escape':
                    this.stateMachine.changeState('paused');
                    break;
                case 'ArrowLeft':
                    this.playerX = Math.max(0, this.playerX - 10);
                    break;
                case 'ArrowRight':
                    this.playerX = Math.min(this.stateMachine.canvas.width - 40, this.playerX + 10);
                    break;
                case 'ArrowUp':
                    this.playerY = Math.max(0, this.playerY - 10);
                    break;
                case 'ArrowDown':
                    this.playerY = Math.min(this.stateMachine.canvas.height - 40, this.playerY + 10);
                    break;
            }
        }
    }
}

// Paused State
class PausedState extends State {
    constructor(stateMachine) {
        super(stateMachine, 'paused');
        this.allowedTransitions = ['playing', 'menu'];
        this.selectedOption = 0;
        this.options = ['Resume', 'Return to Menu'];
    }

    enter() {
        super.enter();
        this.selectedOption = 0;
    }

    render(ctx) {
        const canvas = ctx.canvas;

        // Render the playing state in background (dimmed)
        if (this.stateMachine.previousState && this.stateMachine.previousState.name === 'playing') {
            this.stateMachine.states.playing.render(ctx);
        }

        // Dark overlay
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Pause text
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 48px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('PAUSED', canvas.width / 2, 100);

        // Options
        ctx.font = '32px Arial';
        this.options.forEach((option, index) => {
            const y = 200 + index * 60;

            if (index === this.selectedOption) {
                ctx.fillStyle = '#ffaa00';
                ctx.fillText('> ' + option + ' <', canvas.width / 2, y);
            } else {
                ctx.fillStyle = '#cccccc';
                ctx.fillText(option, canvas.width / 2, y);
            }
        });
    }

    handleInput(input) {
        if (input.type === 'keydown') {
            switch (input.key) {
                case 'Escape':
                    this.stateMachine.changeState('playing');
                    break;
                case 'ArrowUp':
                    this.selectedOption = (this.selectedOption - 1 + this.options.length) % this.options.length;
                    break;
                case 'ArrowDown':
                    this.selectedOption = (this.selectedOption + 1) % this.options.length;
                    break;
                case 'Enter':
                    if (this.selectedOption === 0) {
                        this.stateMachine.changeState('playing');
                    } else if (this.selectedOption === 1) {
                        this.stateMachine.changeState('menu');
                    }
                    break;
            }
        }
    }
}

// Game Over State
class GameOverState extends State {
    constructor(stateMachine) {
        super(stateMachine, 'gameover');
        this.allowedTransitions = ['menu', 'playing'];
        this.timer = 0;
    }

    enter() {
        super.enter();
        this.timer = 0;
    }

    update(dt) {
        this.timer += dt;
    }

    render(ctx) {
        const canvas = ctx.canvas;

        // Clear screen
        ctx.fillStyle = '#2e1a1a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Game Over text with pulsing effect
        const pulse = 0.8 + Math.sin(this.timer * 3) * 0.2;
        ctx.fillStyle = `rgba(255, 0, 0, ${pulse})`;
        ctx.font = 'bold 64px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER', canvas.width / 2, 150);

        // Final score
        ctx.fillStyle = '#ffffff';
        ctx.font = '36px Arial';
        ctx.fillText(`Final Score: ${Math.floor(this.stateMachine.gameData.score)}`,
                     canvas.width / 2, 250);

        // High score
        if (this.stateMachine.gameData.score > this.stateMachine.gameData.highScore) {
            ctx.fillStyle = '#ffaa00';
            ctx.font = 'bold 28px Arial';
            ctx.fillText('NEW HIGH SCORE!', canvas.width / 2, 300);
        } else {
            ctx.fillStyle = '#cccccc';
            ctx.font = '24px Arial';
            ctx.fillText(`High Score: ${this.stateMachine.gameData.highScore}`,
                         canvas.width / 2, 300);
        }

        // Instructions
        ctx.fillStyle = '#ffffff';
        ctx.font = '20px Arial';
        ctx.fillText('Press SPACE to play again', canvas.width / 2, canvas.height - 80);
        ctx.fillText('Press ESC for menu', canvas.width / 2, canvas.height - 50);
    }

    handleInput(input) {
        if (input.type === 'keydown') {
            switch (input.key) {
                case ' ':
                    this.stateMachine.changeState('playing');
                    break;
                case 'Escape':
                    this.stateMachine.changeState('menu');
                    break;
            }
        }
    }
}

// Usage
const canvas = document.getElementById('gameCanvas');
const game = new GameStateMachine(canvas);

// Input handling
document.addEventListener('keydown', (e) => {
    game.handleInput({ type: 'keydown', key: e.key });
});

// Game loop
let lastTime = performance.now();

function gameLoop(timestamp) {
    const dt = (timestamp - lastTime) / 1000;
    lastTime = timestamp;

    game.update(dt);
    game.render();

    requestAnimationFrame(gameLoop);
}

requestAnimationFrame(gameLoop);
```

### State Machine Benefits

1. **Clear State Transitions**: You can see exactly which states can transition to which
2. **State-Specific Logic**: Each state handles its own update, render, and input
3. **Easy to Debug**: Current state is always explicit
4. **Prevents Invalid States**: Transition validation prevents bugs
5. **Maintainable**: Adding new states doesn't affect existing ones

## Game Phase Management

Game phases are high-level states like menu, loading, playing, paused. Let's implement a robust phase manager.

### Claude Code Prompt

```
Prompt: "Create a game phase manager that handles loading, menu, playing,
paused, and game over phases. Include transition animations between phases,
loading progress tracking, and phase-specific update/render logic. Add support
for subphases like tutorial or boss fight within the playing phase."
```

### Implementation

```javascript
class GamePhaseManager {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        this.currentPhase = null;
        this.nextPhase = null;
        this.transitioning = false;
        this.transitionProgress = 0;
        this.transitionDuration = 0.5; // seconds

        // Phase stack for subphases
        this.phaseStack = [];

        // Shared game context
        this.gameContext = {
            score: 0,
            level: 1,
            playerData: null,
            settings: {
                music: true,
                sfx: true,
                difficulty: 'normal'
            }
        };

        this.phases = {
            loading: new LoadingPhase(this),
            menu: new MenuPhase(this),
            playing: new PlayingPhase(this),
            paused: new PausedPhase(this),
            gameover: new GameOverPhase(this),
            tutorial: new TutorialPhase(this),
            bossfight: new BossFightPhase(this)
        };

        // Start with loading phase
        this.setPhase('loading');
    }

    setPhase(phaseName, immediate = false) {
        if (!this.phases[phaseName]) {
            console.error(`Phase ${phaseName} does not exist`);
            return;
        }

        if (immediate) {
            if (this.currentPhase) {
                this.currentPhase.exit();
            }
            this.currentPhase = this.phases[phaseName];
            this.currentPhase.enter();
            this.transitioning = false;
        } else {
            this.nextPhase = this.phases[phaseName];
            this.transitioning = true;
            this.transitionProgress = 0;
        }
    }

    pushPhase(phaseName) {
        // Push current phase onto stack and switch to new phase
        if (this.currentPhase) {
            this.phaseStack.push(this.currentPhase);
        }
        this.setPhase(phaseName, true);
    }

    popPhase() {
        // Return to previous phase from stack
        if (this.phaseStack.length > 0) {
            const previousPhase = this.phaseStack.pop();
            if (this.currentPhase) {
                this.currentPhase.exit();
            }
            this.currentPhase = previousPhase;
            this.currentPhase.resume();
            this.transitioning = false;
        }
    }

    update(dt) {
        if (this.transitioning) {
            this.transitionProgress += dt / this.transitionDuration;

            if (this.transitionProgress >= 0.5 && this.currentPhase !== this.nextPhase) {
                // Midpoint of transition - switch phases
                if (this.currentPhase) {
                    this.currentPhase.exit();
                }
                this.currentPhase = this.nextPhase;
                this.currentPhase.enter();
            }

            if (this.transitionProgress >= 1.0) {
                this.transitioning = false;
                this.transitionProgress = 0;
                this.nextPhase = null;
            }
        }

        if (this.currentPhase && !this.transitioning) {
            this.currentPhase.update(dt);
        }
    }

    render() {
        if (this.currentPhase) {
            this.currentPhase.render(this.ctx);
        }

        if (this.transitioning) {
            this.renderTransition();
        }
    }

    renderTransition() {
        // Fade transition effect
        const alpha = this.transitionProgress < 0.5
            ? this.transitionProgress * 2
            : (1 - this.transitionProgress) * 2;

        this.ctx.fillStyle = `rgba(0, 0, 0, ${alpha})`;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    handleInput(input) {
        if (this.currentPhase && !this.transitioning) {
            this.currentPhase.handleInput(input);
        }
    }
}

// Base Phase class
class Phase {
    constructor(manager, name) {
        this.manager = manager;
        this.name = name;
    }

    enter() {
        console.log(`Entering ${this.name} phase`);
    }

    exit() {
        console.log(`Exiting ${this.name} phase`);
    }

    resume() {
        console.log(`Resuming ${this.name} phase`);
    }

    update(dt) {}
    render(ctx) {}
    handleInput(input) {}
}

// Loading Phase
class LoadingPhase extends Phase {
    constructor(manager) {
        super(manager, 'loading');
        this.progress = 0;
        this.loadingItems = [
            'graphics',
            'sounds',
            'levels',
            'data'
        ];
        this.currentItem = 0;
    }

    enter() {
        super.enter();
        this.progress = 0;
        this.currentItem = 0;
        this.simulateLoading();
    }

    simulateLoading() {
        // Simulate asynchronous loading
        const loadNextItem = () => {
            if (this.currentItem < this.loadingItems.length) {
                this.currentItem++;
                this.progress = this.currentItem / this.loadingItems.length;

                // Simulate load time
                setTimeout(loadNextItem, 300 + Math.random() * 500);
            } else {
                // Loading complete
                this.manager.setPhase('menu');
            }
        };

        loadNextItem();
    }

    render(ctx) {
        const canvas = ctx.canvas;

        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Loading bar
        const barWidth = 400;
        const barHeight = 30;
        const barX = (canvas.width - barWidth) / 2;
        const barY = canvas.height / 2;

        // Background
        ctx.fillStyle = '#333';
        ctx.fillRect(barX, barY, barWidth, barHeight);

        // Progress
        ctx.fillStyle = '#0f0';
        ctx.fillRect(barX, barY, barWidth * this.progress, barHeight);

        // Border
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.strokeRect(barX, barY, barWidth, barHeight);

        // Text
        ctx.fillStyle = '#fff';
        ctx.font = '24px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Loading...', canvas.width / 2, barY - 20);

        if (this.currentItem < this.loadingItems.length) {
            ctx.font = '16px Arial';
            ctx.fillText(`Loading ${this.loadingItems[this.currentItem]}`,
                         canvas.width / 2, barY + barHeight + 30);
        }

        // Percentage
        ctx.font = '20px monospace';
        ctx.fillText(`${Math.floor(this.progress * 100)}%`,
                     canvas.width / 2, barY + barHeight / 2 + 7);
    }
}

// Additional phase implementations (MenuPhase, PlayingPhase, etc.)
// would follow similar patterns to the state machine examples above
```

## Separating State Concerns

Complex games benefit from separating different types of state.

### Claude Code Prompt

```
Prompt: "Create a game with separate state managers for player state, world
state, and UI state. Implement a central state coordinator that manages
communication between these separate state systems. Include serialization
that handles all three state types."
```

### Implementation

```javascript
class PlayerState {
    constructor() {
        this.reset();
    }

    reset() {
        this.position = { x: 100, y: 300 };
        this.velocity = { x: 0, y: 0 };
        this.health = 100;
        this.maxHealth = 100;
        this.energy = 100;
        this.maxEnergy = 100;
        this.inventory = [];
        this.abilities = ['jump', 'dash'];
        this.stats = {
            strength: 10,
            defense: 10,
            speed: 10
        };
    }

    update(dt) {
        // Regenerate energy
        this.energy = Math.min(this.maxEnergy, this.energy + 5 * dt);
    }

    takeDamage(amount) {
        this.health = Math.max(0, this.health - amount);
        return this.health === 0; // Returns true if died
    }

    heal(amount) {
        this.health = Math.min(this.maxHealth, this.health + amount);
    }

    addItem(item) {
        this.inventory.push(item);
    }

    removeItem(itemId) {
        const index = this.inventory.findIndex(item => item.id === itemId);
        if (index !== -1) {
            return this.inventory.splice(index, 1)[0];
        }
        return null;
    }

    hasAbility(abilityName) {
        return this.abilities.includes(abilityName);
    }

    toJSON() {
        return {
            position: { ...this.position },
            velocity: { ...this.velocity },
            health: this.health,
            maxHealth: this.maxHealth,
            energy: this.energy,
            maxEnergy: this.maxEnergy,
            inventory: [...this.inventory],
            abilities: [...this.abilities],
            stats: { ...this.stats }
        };
    }

    fromJSON(data) {
        Object.assign(this, data);
    }
}

class WorldState {
    constructor() {
        this.reset();
    }

    reset() {
        this.level = 1;
        this.time = 0;
        this.weather = 'clear';
        this.timeOfDay = 'day'; // day, night, dawn, dusk
        this.enemies = [];
        this.items = [];
        this.triggers = [];
        this.npcs = [];
        this.checkpoints = [];
        this.activeCheckpoint = null;
    }

    update(dt) {
        this.time += dt;

        // Update time of day (simplified - one cycle per 5 minutes)
        const cycleTime = 300; // seconds
        const dayProgress = (this.time % cycleTime) / cycleTime;

        if (dayProgress < 0.25) this.timeOfDay = 'day';
        else if (dayProgress < 0.35) this.timeOfDay = 'dusk';
        else if (dayProgress < 0.75) this.timeOfDay = 'night';
        else if (dayProgress < 0.85) this.timeOfDay = 'dawn';
        else this.timeOfDay = 'day';

        // Update enemies
        this.enemies = this.enemies.filter(enemy => enemy.health > 0);

        // Check triggers
        this.triggers.forEach(trigger => {
            if (!trigger.activated && this.checkTriggerCondition(trigger)) {
                trigger.activate();
                trigger.activated = true;
            }
        });
    }

    checkTriggerCondition(trigger) {
        // Implement trigger checking logic
        return false;
    }

    addEnemy(enemy) {
        enemy.id = `enemy_${this.enemies.length}_${Date.now()}`;
        this.enemies.push(enemy);
    }

    removeEnemy(enemyId) {
        const index = this.enemies.findIndex(e => e.id === enemyId);
        if (index !== -1) {
            this.enemies.splice(index, 1);
        }
    }

    addItem(item) {
        item.id = `item_${this.items.length}_${Date.now()}`;
        this.items.push(item);
    }

    removeItem(itemId) {
        const index = this.items.findIndex(i => i.id === itemId);
        if (index !== -1) {
            return this.items.splice(index, 1)[0];
        }
        return null;
    }

    activateCheckpoint(checkpoint) {
        this.activeCheckpoint = checkpoint;
        if (!this.checkpoints.includes(checkpoint)) {
            this.checkpoints.push(checkpoint);
        }
    }

    toJSON() {
        return {
            level: this.level,
            time: this.time,
            weather: this.weather,
            timeOfDay: this.timeOfDay,
            enemies: this.enemies.map(e => ({ ...e })),
            items: this.items.map(i => ({ ...i })),
            checkpoints: [...this.checkpoints],
            activeCheckpoint: this.activeCheckpoint
        };
    }

    fromJSON(data) {
        Object.assign(this, data);
    }
}

class UIState {
    constructor() {
        this.reset();
    }

    reset() {
        this.activeMenu = null; // null, 'main', 'inventory', 'map', 'settings'
        this.notifications = [];
        this.dialogActive = false;
        this.dialogText = '';
        this.dialogSpeaker = '';
        this.hudVisible = true;
        this.minimapVisible = true;
        this.tooltipActive = false;
        this.tooltipText = '';
        this.tooltipPosition = { x: 0, y: 0 };
    }

    update(dt) {
        // Update notifications (remove expired ones)
        this.notifications = this.notifications.filter(notif => {
            notif.timeLeft -= dt;
            return notif.timeLeft > 0;
        });
    }

    showNotification(text, duration = 3.0) {
        this.notifications.push({
            text,
            timeLeft: duration,
            timestamp: Date.now()
        });
    }

    showDialog(speaker, text) {
        this.dialogActive = true;
        this.dialogSpeaker = speaker;
        this.dialogText = text;
    }

    hideDialog() {
        this.dialogActive = false;
        this.dialogText = '';
        this.dialogSpeaker = '';
    }

    openMenu(menuName) {
        this.activeMenu = menuName;
    }

    closeMenu() {
        this.activeMenu = null;
    }

    toggleMenu(menuName) {
        if (this.activeMenu === menuName) {
            this.closeMenu();
        } else {
            this.openMenu(menuName);
        }
    }

    showTooltip(text, x, y) {
        this.tooltipActive = true;
        this.tooltipText = text;
        this.tooltipPosition = { x, y };
    }

    hideTooltip() {
        this.tooltipActive = false;
        this.tooltipText = '';
    }

    // UI state typically isn't saved
    toJSON() {
        return {
            hudVisible: this.hudVisible,
            minimapVisible: this.minimapVisible
        };
    }

    fromJSON(data) {
        this.hudVisible = data.hudVisible;
        this.minimapVisible = data.minimapVisible;
    }
}

// State Coordinator
class GameStateCoordinator {
    constructor() {
        this.playerState = new PlayerState();
        this.worldState = new WorldState();
        this.uiState = new UIState();

        this.gamePhase = 'menu'; // menu, playing, paused, gameover
    }

    reset() {
        this.playerState.reset();
        this.worldState.reset();
        this.uiState.reset();
        this.gamePhase = 'menu';
    }

    update(dt) {
        if (this.gamePhase === 'playing') {
            this.playerState.update(dt);
            this.worldState.update(dt);
            this.uiState.update(dt);

            // Cross-state logic
            this.checkPlayerWorldInteractions();
        } else if (this.gamePhase === 'paused') {
            // Only update UI when paused
            this.uiState.update(dt);
        }
    }

    checkPlayerWorldInteractions() {
        // Check if player is collecting items
        this.worldState.items.forEach(item => {
            const dx = item.x - this.playerState.position.x;
            const dy = item.y - this.playerState.position.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 30) { // Collection range
                this.collectItem(item);
            }
        });

        // Check if player reaches checkpoint
        this.worldState.checkpoints.forEach(checkpoint => {
            if (checkpoint !== this.worldState.activeCheckpoint) {
                const dx = checkpoint.x - this.playerState.position.x;
                const dy = checkpoint.y - this.playerState.position.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 50) {
                    this.activateCheckpoint(checkpoint);
                }
            }
        });
    }

    collectItem(item) {
        // Remove from world
        this.worldState.removeItem(item.id);

        // Add to inventory
        this.playerState.addItem(item);

        // Show notification
        this.uiState.showNotification(`Collected ${item.name}!`);
    }

    activateCheckpoint(checkpoint) {
        this.worldState.activateCheckpoint(checkpoint);
        this.uiState.showNotification('Checkpoint activated!');
    }

    // Save system
    save(slotName = 'autosave') {
        const saveData = {
            version: '1.0.0',
            timestamp: Date.now(),
            gamePhase: this.gamePhase,
            player: this.playerState.toJSON(),
            world: this.worldState.toJSON(),
            ui: this.uiState.toJSON()
        };

        localStorage.setItem(`save_${slotName}`, JSON.stringify(saveData));
        this.uiState.showNotification('Game saved!');
        return saveData;
    }

    load(slotName = 'autosave') {
        const savedData = localStorage.getItem(`save_${slotName}`);

        if (!savedData) {
            this.uiState.showNotification('No save found!');
            return false;
        }

        try {
            const saveData = JSON.parse(savedData);

            this.gamePhase = saveData.gamePhase;
            this.playerState.fromJSON(saveData.player);
            this.worldState.fromJSON(saveData.world);
            this.uiState.fromJSON(saveData.ui);

            this.uiState.showNotification('Game loaded!');
            return true;
        } catch (error) {
            console.error('Failed to load save:', error);
            this.uiState.showNotification('Failed to load save!');
            return false;
        }
    }

    deleteSave(slotName) {
        localStorage.removeItem(`save_${slotName}`);
    }

    getAllSaves() {
        const saves = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('save_')) {
                const data = JSON.parse(localStorage.getItem(key));
                saves.push({
                    slotName: key.replace('save_', ''),
                    timestamp: data.timestamp,
                    level: data.world.level,
                    playerHealth: data.player.health
                });
            }
        }
        return saves.sort((a, b) => b.timestamp - a.timestamp);
    }
}

// Usage
const gameState = new GameStateCoordinator();

// Start game
gameState.gamePhase = 'playing';

// Game loop
let lastTime = performance.now();

function gameLoop(timestamp) {
    const dt = (timestamp - lastTime) / 1000;
    lastTime = timestamp;

    gameState.update(dt);

    // Rendering would go here

    requestAnimationFrame(gameLoop);
}

// Save/load controls
document.addEventListener('keydown', (e) => {
    if (e.key === 'F5') {
        e.preventDefault();
        gameState.save('quicksave');
    } else if (e.key === 'F9') {
        e.preventDefault();
        gameState.load('quicksave');
    }
});

requestAnimationFrame(gameLoop);
```

## State Persistence and Save Systems

### Complete Save System with Multiple Slots

```javascript
class SaveSystem {
    constructor(gameId = 'mygame') {
        this.gameId = gameId;
        this.maxSlots = 5;
    }

    save(state, slotNumber, description = '') {
        if (slotNumber < 1 || slotNumber > this.maxSlots) {
            throw new Error(`Invalid slot number. Must be between 1 and ${this.maxSlots}`);
        }

        const saveData = {
            version: '1.0.0',
            gameId: this.gameId,
            slotNumber,
            description,
            timestamp: Date.now(),
            playtime: state.playtime || 0,
            state: this.serializeState(state)
        };

        const key = `${this.gameId}_save_slot_${slotNumber}`;
        localStorage.setItem(key, JSON.stringify(saveData));

        return saveData;
    }

    load(slotNumber) {
        if (slotNumber < 1 || slotNumber > this.maxSlots) {
            throw new Error(`Invalid slot number. Must be between 1 and ${this.maxSlots}`);
        }

        const key = `${this.gameId}_save_slot_${slotNumber}`;
        const data = localStorage.getItem(key);

        if (!data) {
            return null;
        }

        const saveData = JSON.parse(data);
        return this.deserializeState(saveData.state);
    }

    deleteSave(slotNumber) {
        const key = `${this.gameId}_save_slot_${slotNumber}`;
        localStorage.removeItem(key);
    }

    getSaveInfo(slotNumber) {
        const key = `${this.gameId}_save_slot_${slotNumber}`;
        const data = localStorage.getItem(key);

        if (!data) {
            return null;
        }

        const saveData = JSON.parse(data);
        return {
            slotNumber: saveData.slotNumber,
            description: saveData.description,
            timestamp: saveData.timestamp,
            playtime: saveData.playtime,
            level: saveData.state.world?.level,
            playerHealth: saveData.state.player?.health
        };
    }

    getAllSaves() {
        const saves = [];

        for (let i = 1; i <= this.maxSlots; i++) {
            const info = this.getSaveInfo(i);
            saves.push(info);
        }

        return saves;
    }

    serializeState(state) {
        // Deep copy to avoid reference issues
        return JSON.parse(JSON.stringify(state));
    }

    deserializeState(serializedState) {
        return serializedState;
    }

    exportSave(slotNumber) {
        const key = `${this.gameId}_save_slot_${slotNumber}`;
        const data = localStorage.getItem(key);

        if (!data) {
            throw new Error('Save not found');
        }

        // Create a downloadable file
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.gameId}_save_${slotNumber}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    importSave(fileContent, slotNumber) {
        try {
            const saveData = JSON.parse(fileContent);

            // Validate save data
            if (saveData.gameId !== this.gameId) {
                throw new Error('Save file is for a different game');
            }

            // Save to slot
            saveData.slotNumber = slotNumber;
            const key = `${this.gameId}_save_slot_${slotNumber}`;
            localStorage.setItem(key, JSON.stringify(saveData));

            return true;
        } catch (error) {
            console.error('Failed to import save:', error);
            return false;
        }
    }
}

// Usage example
const saveSystem = new SaveSystem('platformer-game');

// Save current state
const currentState = {
    player: { x: 100, y: 200, health: 80 },
    world: { level: 3, time: 456.7 },
    ui: { hudVisible: true }
};

saveSystem.save(currentState, 1, 'Level 3 - Forest');

// Load state
const loadedState = saveSystem.load(1);

// Get all saves for menu
const allSaves = saveSystem.getAllSaves();
allSaves.forEach(save => {
    if (save) {
        console.log(`Slot ${save.slotNumber}: Level ${save.level}, ${new Date(save.timestamp).toLocaleString()}`);
    }
});
```

## Best Practices and Anti-Patterns

### Best Practices

1. **Single Source of Truth**: Don't duplicate state across multiple objects
2. **Immutability**: When possible, create new state objects rather than mutating existing ones
3. **Clear Ownership**: Every piece of state should have a clear owner
4. **Validation**: Validate state transitions to prevent invalid states
5. **Encapsulation**: Use methods to modify state rather than direct property access
6. **Serialization**: Make state serializable from the start (avoid circular references, functions, etc.)
7. **History/Undo**: For some games, maintain state history for undo/replay
8. **State Snapshots**: Take periodic snapshots for debugging and auto-save

### Anti-Patterns to Avoid

1. **Global Variables Everywhere**: Makes testing and debugging impossible
2. **Circular Dependencies**: Player references enemy which references world which references player
3. **God Objects**: One massive state object with hundreds of unrelated properties
4. **Implicit State**: State hidden in closures or scattered across files
5. **State in Render Functions**: Modifying state during rendering
6. **Mutating State Directly**: Changing state without going through methods
7. **No State Validation**: Allowing impossible states (negative health, etc.)
8. **Mixing Concerns**: Putting UI state, game state, and meta-state all together

### Example: State Validation

```javascript
class ValidatedPlayerState {
    constructor() {
        this._health = 100;
        this._maxHealth = 100;
    }

    get health() {
        return this._health;
    }

    set health(value) {
        // Validate: health can't be negative or exceed max
        this._health = Math.max(0, Math.min(this._maxHealth, value));

        // Trigger events
        if (this._health === 0) {
            this.onDeath();
        }
    }

    get maxHealth() {
        return this._maxHealth;
    }

    set maxHealth(value) {
        // Validate: max health must be positive
        this._maxHealth = Math.max(1, value);

        // Adjust current health if needed
        this._health = Math.min(this._health, this._maxHealth);
    }

    takeDamage(amount) {
        if (amount < 0) {
            throw new Error('Damage amount must be positive');
        }
        this.health -= amount;
    }

    heal(amount) {
        if (amount < 0) {
            throw new Error('Heal amount must be positive');
        }
        this.health += amount;
    }

    onDeath() {
        console.log('Player died');
        // Trigger death logic
    }
}
```

## Conclusion

State management is crucial for creating maintainable, debuggable games. Start simple with a basic state object, then evolve to state machines or separate state managers as your game grows in complexity. Always keep state organized, validated, and easy to serialize.

The patterns shown here scale from tiny game jam projects to commercial games. Choose the right approach for your project's complexity, and don't over-engineer early.

---

**Related Documentation:**
- [Game Loops and Timing](./game-loops-and-timing.md)
- [Input Handling](./input-handling.md)
- [Advanced Patterns](../09-advanced-patterns/)
