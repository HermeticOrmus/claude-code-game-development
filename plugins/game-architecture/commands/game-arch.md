---
description: "Design, refactor, test, or profile a game's code architecture"
argument-hint: "[design|refactor|test|profile] <system or codebase area>"
---

# /game-arch

Game architecture design, refactoring, testing, and profiling. Covers ECS, game loops, event systems, ScriptableObject/Resource patterns, and scene management.

## Trigger

`/game-arch [action] [target]`

## Actions

### `design`
Design a game system architecture from requirements.

```
/game-arch design "health system for RPG with status effects, shields, and damage types"
/game-arch design "inventory system supporting items, stacking, equipment slots"
/game-arch design "quest system with objectives, rewards, and branching"
```

**Output**: Component breakdown, data flow diagram, signal/event schema, GDScript skeleton.

### `refactor`
Analyze existing code and propose structural improvements.

```
/game-arch refactor "300-line Player.gd handles movement, combat, and inventory"
/game-arch refactor "12 Autoloads causing circular dependencies"
/game-arch refactor "everything communicates via get_node() path strings"
```

**Output**: Decomposition plan, component extraction steps, dependency graph before/after.

### `test`
Design a testable architecture and write unit tests with GUT.

```
/game-arch test "HealthComponent with damage, healing, and death signal"
/game-arch test "StateMachine with transition table"
/game-arch test "WeaponData Resource with fire rate and damage calculations"
```

**Output**: GUT test class with test_ methods, mock/stub patterns for Node dependencies.

### `profile`
Identify architecture patterns causing performance problems.

```
/game-arch profile "_process() with 500 iterations per frame"
/game-arch profile "signals connected to 1000 receivers"
/game-arch profile "PackedScene.instantiate() called every frame for projectiles"
```

**Output**: Root cause analysis, refactored pattern (object pool, batch processing, deferred signals).

## Examples

**Decomposing a God script:**
```
/game-arch refactor "player script handles input, movement, combat, health, animation, and UI"
```
Produces: Component decomposition into InputComponent, MovementComponent, CombatComponent, HealthComponent; signal wiring between components; scene structure diagram.

**Designing an event bus:**
```
/game-arch design "decoupled event system for cross-scene communication"
```
Produces: EventBus autoload with typed signals, Resource-as-event-channel alternative, usage examples for emitters and receivers.

**Writing testable architecture:**
```
/game-arch test "damage calculation system"
```
Produces: GUT test class, dependency injection via @export to avoid get_parent() in tests, expected signal verification with `watch_signals()`.

## Architecture Decision Record

When recommending a pattern, include:
1. **Problem**: What specific issue does this solve?
2. **Pattern**: Name the pattern (EventBus, Composition, Service Locator)
3. **Tradeoffs**: What does this make harder?
4. **Alternatives**: What else was considered and why rejected?
