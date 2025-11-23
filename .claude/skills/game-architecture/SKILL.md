# Game Architecture Skill

## Purpose
Design and implement complete game architectures using proven patterns and meta-prompting iteration.

## Activation
This skill activates when the user requests:
- Game project structure design
- Architecture decisions
- System organization
- Code structure planning
- Module relationship design

## Architecture Patterns

### 1. Simple Game Pattern (Pong, Snake, Breakout)
```
src/
  main.js         # Entry point, game loop
  game.js         # Game state and logic
  renderer.js     # Canvas drawing
  input.js        # User input
  entities/       # Game objects
  utils/          # Helper functions
```

**Complexity**: Simple (< 0.3)
**Use When**: Learning, game jams, simple arcade games

### 2. State Machine Pattern (Menus, Levels)
```
src/
  main.js
  game.js
  states/
    State.js        # Base state class
    MenuState.js
    PlayState.js
    PauseState.js
    GameOverState.js
  entities/
  systems/
  ui/
```

**Complexity**: Medium (0.3-0.5)
**Use When**: Games with distinct phases, menu systems

### 3. Entity-Component-System (ECS)
```
src/
  main.js
  ecs/
    World.js          # Entity manager
    Entity.js         # Entity factory
    Component.js      # Component base
    System.js         # System base
  components/
    Position.js
    Velocity.js
    Sprite.js
    Collider.js
  systems/
    MovementSystem.js
    RenderSystem.js
    CollisionSystem.js
    InputSystem.js
  entities/          # Entity prefabs
  scenes/
```

**Complexity**: Complex (> 0.7)
**Use When**: Many entity types, data-driven design, performance critical

### 4. Scene Graph Pattern (2D/3D Games)
```
src/
  main.js
  core/
    SceneGraph.js
    Node.js
    Transform.js
  nodes/
    Sprite.js
    Container.js
    Camera.js
  scenes/
    Scene.js
    LevelScene.js
  managers/
    SceneManager.js
    AssetManager.js
    InputManager.js
```

**Complexity**: Medium-Complex (0.5-0.8)
**Use When**: Hierarchical transforms, camera systems, complex scenes

### 5. Event-Driven Architecture
```
src/
  main.js
  core/
    EventBus.js
    Game.js
  events/
    GameEvents.js
    UIEvents.js
    InputEvents.js
  systems/           # Subscribe to events
  ui/               # Emit and listen
  entities/         # Emit events
```

**Complexity**: Medium (0.4-0.6)
**Use When**: Decoupled systems, UI-heavy games, multiplayer

## Architecture Decision Matrix

| Game Type | Recommended Pattern | Complexity |
|-----------|-------------------|------------|
| Simple Arcade | Simple Game | 0.2 |
| Puzzle | State Machine | 0.3 |
| Platformer | State Machine + Events | 0.5 |
| RPG | ECS + Event-Driven | 0.8 |
| Strategy | ECS + Scene Graph | 0.85 |
| Multiplayer | Event-Driven + State Sync | 0.9 |

## Meta-Prompt for Architecture Design

```
TASK: Design architecture for a [GAME_TYPE] game

ANALYSIS REQUIRED:
1. Number of entity types expected
2. Complexity of entity interactions
3. UI complexity
4. State management needs
5. Performance requirements
6. Multiplayer requirements (if any)

CONSTRAINTS:
- Web-based (JavaScript/TypeScript)
- Target: 60 FPS on mid-range hardware
- Must support save/load
- Must be testable

OUTPUT:
1. Recommended architecture pattern
2. Complete directory structure
3. Key module responsibilities
4. Data flow diagram (ASCII)
5. Bootstrap code for main.js
6. Example of adding new entity type
```

## File Templates

### Game Loop Template
```javascript
// main.js - Standard game loop
class Game {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.lastTime = 0;
        this.running = false;
    }

    start() {
        this.running = true;
        this.lastTime = performance.now();
        requestAnimationFrame(this.loop.bind(this));
    }

    loop(currentTime) {
        if (!this.running) return;

        const deltaTime = (currentTime - this.lastTime) / 1000;
        this.lastTime = currentTime;

        this.update(deltaTime);
        this.render();

        requestAnimationFrame(this.loop.bind(this));
    }

    update(dt) {
        // Override in subclass
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        // Override in subclass
    }
}
```

### State Manager Template
```javascript
// StateManager.js
class StateManager {
    constructor() {
        this.states = new Map();
        this.currentState = null;
    }

    register(name, state) {
        this.states.set(name, state);
        state.manager = this;
    }

    change(name, ...args) {
        if (this.currentState) {
            this.currentState.exit();
        }
        this.currentState = this.states.get(name);
        this.currentState.enter(...args);
    }

    update(dt) {
        this.currentState?.update(dt);
    }

    render(ctx) {
        this.currentState?.render(ctx);
    }
}
```

### ECS World Template
```javascript
// World.js - Basic ECS
class World {
    constructor() {
        this.entities = [];
        this.systems = [];
        this.nextId = 0;
    }

    createEntity() {
        const entity = { id: this.nextId++, components: {} };
        this.entities.push(entity);
        return entity;
    }

    addComponent(entity, name, data) {
        entity.components[name] = data;
        return entity;
    }

    addSystem(system) {
        this.systems.push(system);
    }

    update(dt) {
        for (const system of this.systems) {
            const filtered = this.entities.filter(e =>
                system.requiredComponents.every(c => c in e.components)
            );
            system.update(filtered, dt);
        }
    }
}
```

## Quality Criteria for Architecture

1. **Separation of Concerns (30%)**
   - Clear module boundaries
   - Single responsibility per module
   - Minimal coupling

2. **Extensibility (25%)**
   - Easy to add new entities
   - Easy to add new systems
   - Plugin-friendly design

3. **Testability (20%)**
   - Dependency injection
   - Pure functions where possible
   - Mockable interfaces

4. **Performance Awareness (15%)**
   - Hot path optimization potential
   - Memory allocation patterns
   - Spatial query support

5. **Developer Experience (10%)**
   - Clear file naming
   - Consistent patterns
   - Good defaults

## Output

This skill produces:
- Complete project structure
- Key module implementations
- Data flow documentation
- Bootstrap/setup code
- Testing strategy
