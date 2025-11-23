# Game System Generator Skill

## Purpose
Generate complete, production-ready game systems using meta-prompting techniques optimized for game development.

## Activation
This skill activates when the user requests:
- Game mechanic implementations
- Physics systems
- Collision detection
- Input handling
- Animation systems
- Audio managers
- Entity/component systems

## Complexity Analysis for Game Systems

### Simple (< 0.3 complexity)
- Basic input handlers
- Simple collision detection (AABB)
- Score counters
- Basic timers

### Medium (0.3 - 0.7 complexity)
- Physics with gravity and friction
- Sprite animation systems
- State machines for characters
- Audio managers with pooling
- Camera follow systems

### Complex (> 0.7 complexity)
- Entity Component Systems (ECS)
- Spatial partitioning (Quadtree/Octree)
- Pathfinding (A*, Dijkstra)
- Multiplayer networking
- Procedural generation
- Advanced physics (soft body, rope)

## Meta-Prompt Template for Game Systems

```
TASK: Create a [SYSTEM_TYPE] for a [GAME_TYPE] game

CONTEXT:
- Game Genre: [genre]
- Target Platform: Web (HTML5 Canvas/WebGL)
- Performance Target: 60 FPS
- Existing Systems: [list any existing systems to integrate with]

REQUIREMENTS:
1. [requirement 1]
2. [requirement 2]
3. [requirement 3]

CONSTRAINTS:
- Must use ES6+ JavaScript modules
- Must be frame-rate independent (delta time)
- Must handle edge cases gracefully
- Must be testable (dependency injection)

OUTPUT FORMAT:
- Complete, runnable code
- JSDoc comments for all public methods
- Usage example at the end
- Integration notes with other systems
```

## Example Prompts

### Player Controller
```
Create a player controller system with:
- Smooth movement using delta time
- Jump with variable height (hold longer = higher)
- Coyote time (can jump briefly after leaving platform)
- Input buffering (queue jump while in air)
- Wall slide and wall jump
- Export as ES6 module
```

### Collision System
```
Create a collision detection system with:
- AABB collision detection
- Circle collision detection
- Polygon collision (SAT algorithm)
- Collision response with momentum transfer
- Spatial hash grid for optimization (1000+ objects)
- Collision layers and masks
- Debug rendering mode
```

### Animation System
```
Create a sprite animation system with:
- Frame-based animations from sprite sheets
- Animation state machine (idle, walk, jump, attack)
- Transition rules between states
- Event callbacks (on frame, on complete)
- Animation blending for smooth transitions
- Support for both row and column sprite sheets
```

## Quality Assessment Criteria

For game systems, assess quality based on:

1. **Functionality (40%)**
   - Does it work as specified?
   - Does it handle edge cases?
   - Is it frame-rate independent?

2. **Performance (25%)**
   - Minimal object allocation in game loop
   - Efficient algorithms used
   - Proper use of spatial partitioning

3. **Integration (20%)**
   - Easy to plug into existing systems
   - Clear API surface
   - Proper event/callback system

4. **Maintainability (15%)**
   - Well-documented code
   - Testable design
   - Follows game dev conventions

## Iteration Strategies

### First Pass
Focus on core functionality - make it work correctly.

### Second Pass
Optimize for performance - reduce allocations, improve algorithms.

### Third Pass
Polish API - improve ergonomics, add quality-of-life features.

## Game Development Specific Context Extraction

When iterating on game systems, extract:

1. **Performance Bottlenecks**
   - Allocations per frame
   - O(n) operations that could be O(log n)
   - Unnecessary calculations

2. **Integration Issues**
   - Missing callbacks/events
   - Incompatible data formats
   - Coupling with other systems

3. **Game Feel Factors**
   - Response latency
   - Visual feedback opportunities
   - Sound effect trigger points

4. **Edge Cases**
   - Multiple collisions same frame
   - Rapid state changes
   - Pause/resume handling
   - Screen resize handling

## Output

The skill produces:
- Complete JavaScript module
- TypeScript type definitions (if requested)
- Unit test examples
- Integration code example
- Performance notes
