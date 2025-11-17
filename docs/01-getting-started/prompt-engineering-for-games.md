# Prompt Engineering for Game Development

Master the art of communicating with Claude Code to build games efficiently. This comprehensive guide covers prompt engineering principles, patterns, and 20+ real examples with results and analysis.

## Table of Contents

- [Introduction to Prompt Engineering](#introduction-to-prompt-engineering)
- [Anatomy of a Good Game Development Prompt](#anatomy-of-a-good-game-development-prompt)
- [Specific vs Vague Prompts](#specific-vs-vague-prompts)
- [Iterative Refinement Strategy](#iterative-refinement-strategy)
- [Domain-Specific Language for Games](#domain-specific-language-for-games)
- [Common Prompt Patterns](#common-prompt-patterns)
- [20+ Example Prompts with Results](#20-example-prompts-with-results)
- [Debugging with Prompts](#debugging-with-prompts)
- [Meta-Prompting Techniques](#meta-prompting-techniques)
- [Advanced Prompting Strategies](#advanced-prompting-strategies)

---

## Introduction to Prompt Engineering

**Prompt engineering** is the skill of crafting effective instructions for AI systems. In game development, good prompts mean the difference between:

- Getting working code in minutes vs hours of back-and-forth
- Clean, maintainable code vs messy, hard-to-modify code
- Learning opportunities vs mysterious code you don't understand
- Successful features vs broken implementations

### Why It Matters

**Poor Prompt Impact**:
```
Time wasted: Hours of refinement
Code quality: Inconsistent
Learning: Minimal
Frustration: High
```

**Great Prompt Impact**:
```
Time saved: 10x faster development
Code quality: Production-ready
Learning: Deep understanding
Satisfaction: High
```

### The Prompt Engineering Mindset

Think of yourself as a **director** communicating with a skilled developer:

- **Be specific** about what you want
- **Provide context** for better decisions
- **Set constraints** to guide implementation
- **Ask questions** to understand the code
- **Iterate** to refine results

---

## Anatomy of a Good Game Development Prompt

### Essential Components

**1. Clear Objective**
What are you building?

```
"Create a particle system" ← Vague
"Create a particle system for explosion effects" ← Clear
```

**2. Technical Specifications**
Concrete requirements:

```
- 50-100 particles per explosion
- Particles fade out over 0.5 seconds
- Radial expansion from origin point
- Random velocity variation
```

**3. Context**
Why and where this is used:

```
"For a space shooter game where asteroids explode when shot"
```

**4. Constraints**
Limitations and requirements:

```
- Must run at 60 FPS with 10+ simultaneous explosions
- Vanilla JavaScript, no libraries
- Compatible with existing Canvas 2D renderer
```

**5. Code Preferences**
Style and structure:

```
- Use object-oriented approach
- Include detailed comments
- Separate update and render logic
```

### Complete Example

**Excellent Prompt Structure**:

```
Create a particle system for asteroid explosion effects in my space shooter.

Requirements:
- Generate 50-100 particles per explosion
- Particles should expand radially from origin
- Each particle fades out over 0.5 seconds
- Random colors from palette: orange, yellow, red, white
- Particles slow down as they travel (friction)

Technical Constraints:
- Must handle 10+ simultaneous explosions at 60 FPS
- Vanilla JavaScript (no libraries)
- Integrate with my existing Canvas 2D rendering

Code Style:
- Object-oriented design with Particle and ParticleSystem classes
- Include comments explaining key concepts
- Use object pooling for performance

Provide usage example showing how to trigger explosion at specific coordinates.
```

**Why This Works**:
- Specific outcome defined
- Technical details provided
- Performance requirements stated
- Integration context given
- Code preferences specified
- Usage example requested

---

## Specific vs Vague Prompts

### Examples with Comparison

#### Example 1: Player Movement

**Vague**:
```
Add player movement
```

**Problems**:
- What type of movement? (8-directional, platformer, top-down)
- What controls? (Keyboard, mouse, gamepad)
- What physics? (Instant, acceleration, momentum)

**Specific**:
```
Add 8-directional player movement for a top-down adventure game:
- Arrow keys or WASD for direction
- Smooth acceleration to max speed of 200 pixels/second
- Deceleration when keys released
- Diagonal movement normalized to prevent faster diagonal speed
- Movement boundary: keep player within canvas bounds
```

**Result Quality**: Specific prompt produces exactly what you need first try.

#### Example 2: Enemy AI

**Vague**:
```
Make enemies chase the player
```

**Specific**:
```
Implement enemy AI for zombie-type enemies in a top-down shooter:
- Enemies detect player within 300 pixel radius
- Move toward player at 100 pixels/second when detected
- Use simple direct pathfinding (straight line to player)
- Stop within 50 pixels of player and attack
- Lose interest and wander randomly if player escapes 400 pixel radius
- Handle collision with other enemies (don't stack on same position)
```

#### Example 3: Collision Detection

**Vague**:
```
Add collision detection
```

**Specific**:
```
Implement collision detection for a 2D platformer:
- Circle-based collision for player (radius 20px)
- Rectangle-based collision for platforms
- Detect which side of platform was hit (top, bottom, left, right)
- Resolve collisions by adjusting player position
- Prevent player from falling through platforms at high speeds
- Return collision information (hasCollided, collisionSide, platform)
```

### Pattern Recognition

**Vague prompts**:
- Single sentence
- General verbs (add, make, create)
- No measurements or specifics
- Ambiguous requirements

**Specific prompts**:
- Multiple requirements
- Concrete measurements (pixels, seconds, counts)
- Clear behaviors described
- Edge cases considered

---

## Iterative Refinement Strategy

Build features progressively through conversation.

### The Refinement Cycle

```
Initial Prompt (Basic Version)
    ↓
Generate & Test
    ↓
Identify Improvements
    ↓
Refinement Prompt
    ↓
Generate & Test
    ↓
[Repeat until perfect]
```

### Real Example: Building a Jump Mechanic

**Iteration 1 - Basic Jump**:
```
Prompt: "Add jumping to the player. Space bar to jump."

Result: Player jumps but feels floaty and unrealistic
```

**Iteration 2 - Improve Feel**:
```
Prompt: "Make the jump feel better:
- Increase gravity to make player fall faster
- Allow higher jumps when holding space longer (variable jump height)
- Add a maximum hold time of 0.3 seconds"

Result: Much better but still lacking
```

**Iteration 3 - Add Polish**:
```
Prompt: "Add these refinements:
- Coyote time: allow jumping for 0.1 seconds after leaving platform
- Jump buffering: remember jump input for 0.1 seconds before landing
- Reduce gravity slightly at peak of jump for better feel"

Result: Professional-feeling jump mechanic
```

**Iteration 4 - Add Advanced Features**:
```
Prompt: "Add double jump ability:
- Press space again while in air for second jump
- Second jump slightly lower than first
- Reset double jump when landing on platform"

Result: Complete, polished jump system
```

### Progressive Complexity

**Start Simple**:
```
"Create basic enemy that moves left and right"
```

**Add Features Incrementally**:
```
"Make enemy turn around at platform edges"
"Add patrol waypoints instead of simple left-right"
"Make enemy chase player when in range"
"Add attack behavior when close to player"
```

**Benefits**:
- Each step is testable
- Easy to identify what broke
- Build understanding gradually
- Maintain working version at each step

---

## Domain-Specific Language for Games

Use game development terminology for better results.

### Movement and Physics Terms

**Use These Terms**:
- Velocity, acceleration, friction, drag
- Gravity, terminal velocity
- Impulse, force
- Collision response, restitution (bounciness)
- Interpolation, extrapolation
- Delta time, frame rate independence

**Example Usage**:
```
"Apply constant downward acceleration (gravity) of 800 pixels/second²
to the player. Limit maximum falling velocity (terminal velocity) to
600 pixels/second."
```

### Game Architecture Terms

**Use These Concepts**:
- Game loop, update/render cycle
- Game states (menu, playing, paused, game over)
- Entity Component System (ECS)
- Object pooling
- Spatial partitioning (quadtree, grid)
- State machine, behavior tree

**Example Usage**:
```
"Implement a state machine for the player with states: idle, walking,
jumping, falling, attacking. Each state has enter, update, and exit methods."
```

### Rendering Terms

**Graphics Concepts**:
- Sprite, sprite sheet, animation frame
- Layer, z-index, draw order
- Camera, viewport, world coordinates
- Particle emitter, particle lifetime
- Screen shake, visual effects

**Example Usage**:
```
"Create a sprite animation system that cycles through frames from a
sprite sheet. Support variable frame duration and looping/non-looping animations."
```

### AI and Behavior Terms

**AI Terminology**:
- Pathfinding (A*, Dijkstra, nav mesh)
- Line of sight, field of view
- Steering behaviors (seek, flee, wander)
- Finite state machine (FSM)
- Aggro range, pursuit, patrol

**Example Usage**:
```
"Implement seek steering behavior: enemy calculates direction vector
to player and accelerates in that direction, with maximum speed limit."
```

---

## Common Prompt Patterns

### Pattern 1: The Complete System Prompt

For generating entire game systems:

```
Template:
Create a [SYSTEM NAME] for [GAME TYPE] with these features:

Core Functionality:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Technical Requirements:
- [Performance requirement]
- [Technology constraint]
- [Integration requirement]

Code Structure:
- [Architectural preference]
- [Style requirement]

Include usage example.
```

### Pattern 2: The Modification Prompt

For changing existing code:

```
Template:
Modify this [SYSTEM/FUNCTION] to [DESIRED CHANGE]:

Current behavior: [What it does now]
Desired behavior: [What you want instead]

Here's the current code:
[PASTE CODE]

Maintain all other functionality.
```

### Pattern 3: The Debugging Prompt

For fixing issues:

```
Template:
I have a bug in my [SYSTEM] where [PROBLEM DESCRIPTION].

Expected: [What should happen]
Actual: [What actually happens]
When: [When/how the bug occurs]

Here's the relevant code:
[PASTE CODE]

Help me identify and fix the issue.
```

### Pattern 4: The Explanation Prompt

For understanding code:

```
Template:
Explain how this [SYSTEM/ALGORITHM] works:

[PASTE CODE]

Please cover:
- Overall approach and algorithm
- Key variables and their purposes
- Step-by-step execution flow
- Why this approach was chosen
- Potential edge cases or limitations
```

### Pattern 5: The Optimization Prompt

For improving performance:

```
Template:
This [SYSTEM] performs poorly when [CONDITION].

Current performance: [Measurements]
Target performance: [Goal]

Code:
[PASTE CODE]

Suggest optimizations while maintaining functionality.
```

---

## 20+ Example Prompts with Results

### Game Initialization Prompts

#### Prompt 1: Basic Game Template

**Prompt**:
```
Create a basic HTML5 game template with:
- Canvas element (800x600)
- Game loop using requestAnimationFrame
- Delta time calculation for frame-rate independence
- Keyboard input handling for arrow keys
- FPS counter display
- Basic project structure with separate update() and render() functions
```

**Result Quality**: ★★★★★
**Generated**: Complete HTML file with professional game loop structure
**Learning Value**: Excellent for understanding game loop fundamentals
**Customization Needed**: Minimal - works out of the box

#### Prompt 2: Game State Management

**Prompt**:
```
Create a game state manager that handles multiple states (MENU, PLAYING, PAUSED, GAME_OVER).
Each state should have:
- enter() - called when entering state
- update(deltaTime) - called every frame
- render(ctx) - for drawing
- exit() - called when leaving state

Include state transition method and example usage with a simple game.
```

**Result Quality**: ★★★★★
**Generated**: Clean state management system with examples
**Use Case**: Any game with multiple screens/states

### Movement and Physics Prompts

#### Prompt 3: Platformer Movement

**Prompt**:
```
Create platformer character movement with:
- Left/Right movement with acceleration (300 px/s max speed)
- Jump with variable height (hold space longer = higher jump, max 0.25s)
- Gravity (1200 px/s²) and terminal velocity (600 px/s)
- Ground detection
- Coyote time (0.1s grace period after leaving platform)
- Air control (can still move left/right in air but reduced acceleration)

Use character object with x, y, velocityX, velocityY, onGround properties.
```

**Result Quality**: ★★★★★
**Generated**: Full movement system with all features
**Feel**: Professional platformer movement
**Note**: May need to tweak numbers for your game's feel

#### Prompt 4: Top-Down Movement

**Prompt**:
```
Implement smooth 8-directional movement for top-down game:
- WASD or arrow keys
- Acceleration to max speed (250 px/s) over 0.2 seconds
- Deceleration when no input (friction coefficient 0.9)
- Normalize diagonal movement (same speed as cardinal directions)
- Rotate player sprite to face movement direction

Player object should have: x, y, velocityX, velocityY, rotation
```

**Result Quality**: ★★★★★
**Generated**: Smooth, polished movement system
**Bonus**: Rotation calculation for sprite direction

#### Prompt 5: Vehicle Physics

**Prompt**:
```
Create simple car physics for top-down racing game:
- Forward/backward acceleration (arrow up/down)
- Steering left/right (arrow keys) - only when moving
- Forward speed: max 400 px/s
- Reverse speed: max 150 px/s
- Steering becomes more effective at higher speeds
- Friction slows car when not accelerating
- Handbrake (space) for drifting - locks steering angle temporarily

Car object: x, y, angle, speed, rotationSpeed
```

**Result Quality**: ★★★★☆
**Generated**: Fun, arcadey car physics
**Note**: May need tweaking for realistic vs arcade feel

### Combat and Interaction Prompts

#### Prompt 6: Projectile System

**Prompt**:
```
Create a bullet/projectile system for top-down shooter:
- Spawn bullets at player position moving in aim direction
- Bullets travel at 500 px/s
- Despawn after 2 seconds or when leaving screen
- Collision detection with array of enemies
- Object pooling (reuse bullet objects) for performance
- Support for different bullet types (normal, fast, spread)

Include BulletManager class and usage example.
```

**Result Quality**: ★★★★★
**Generated**: Complete projectile system with pooling
**Performance**: Excellent with object pooling
**Extensibility**: Easy to add new bullet types

#### Prompt 7: Health and Damage System

**Prompt**:
```
Create health/damage system for game entities:
- Entity has currentHealth, maxHealth
- takeDamage(amount) method with optional damage type
- heal(amount) method that doesn't exceed maxHealth
- isAlive() check
- onDeath() callback
- Invulnerability period (1 second after taking damage)
- Visual feedback: flash red when hit
- Health bar rendering above entity

Create a base Health component that can be added to any entity.
```

**Result Quality**: ★★★★★
**Generated**: Flexible health system
**Integration**: Easy to add to existing entities

#### Prompt 8: Melee Combat System

**Prompt**:
```
Implement melee combat for 2D action game:
- Attack triggered by X key
- 0.3 second attack animation/duration
- Attack hitbox appears in front of player during animation
- Cooldown of 0.5 seconds between attacks
- Damage detection for enemies in hitbox during attack frames
- Each enemy can only be hit once per attack
- Combo system: 3 consecutive attacks if timed correctly (within 0.6s)

Include state management (idle, attacking, cooldown)
```

**Result Quality**: ★★★★☆
**Generated**: Functional melee system
**Polish Needed**: Animation could be enhanced visually

### AI and Enemy Behavior Prompts

#### Prompt 9: Chase AI

**Prompt**:
```
Create enemy AI that chases player:
- Detect player within 400 pixel detection radius
- Chase state: move toward player at 150 px/s
- Stop within 80 pixels (attack range)
- Lose interest if player gets 500+ pixels away, return to wander state
- Wander state: move in random direction for 2-3 seconds, pause 1 second, repeat
- Smooth rotation to face movement direction
- Avoid getting stuck on edges (simple edge detection)

Use state machine pattern (WANDER, CHASE, ATTACK states)
```

**Result Quality**: ★★★★★
**Generated**: Complete AI with state machine
**Behavior**: Believable and fun to play against

#### Prompt 10: Patrol AI

**Prompt**:
```
Create patrolling enemy that follows waypoints:
- Define patrol route as array of {x, y} waypoints
- Move to each waypoint in sequence, loop back to start
- Move at 100 px/s between waypoints
- Pause for 1 second at each waypoint
- When player enters 250 pixel radius, break from patrol and chase
- After losing player, return to nearest waypoint and resume patrol
- Face direction of movement

Include visualization of patrol route (dashed lines) for debugging
```

**Result Quality**: ★★★★★
**Generated**: Professional patrol system with chase
**Debugging**: Helpful route visualization

### Visual Effects Prompts

#### Prompt 11: Particle System

**Prompt**:
```
Create flexible particle system for various effects:
- Emit particles from point or area
- Configurable: count, lifetime, speed, size, color, gravity
- Particles fade out over lifetime
- Support multiple simultaneous emitters
- Object pooling for 200+ particles without lag
- Preset configurations for: explosion, smoke, sparkle, blood

Provide ParticleEmitter class and 3 usage examples
```

**Result Quality**: ★★★★★
**Generated**: Highly configurable particle system
**Performance**: Excellent with pooling
**Versatility**: Works for many effect types

#### Prompt 12: Screen Shake

**Prompt**:
```
Implement camera shake effect:
- shake(intensity, duration) function
- Intensity controls shake magnitude (pixels)
- Duration in seconds
- Decay over time (shake gets smaller)
- Return camera to original position when done
- Multiple shakes stack additively
- Apply shake offset to all rendering

Works with existing camera/viewport system
```

**Result Quality**: ★★★★★
**Generated**: Smooth screen shake implementation
**Feel**: Adds great game feel to impacts

#### Prompt 13: Sprite Animation

**Prompt**:
```
Create sprite animation system using sprite sheets:
- Define animation as sequence of frames
- Variable frame duration support
- Loop or play-once modes
- onComplete callback for non-looping animations
- Play, stop, pause, reset controls
- Smooth frame transitions
- Support multiple animations per sprite (idle, walk, jump, attack)
- Animation manager to switch between animations

Include example with character having 3 animations
```

**Result Quality**: ★★★★★
**Generated**: Complete animation system
**Flexibility**: Easy to define new animations

### UI and Game Feel Prompts

#### Prompt 14: Dialogue System

**Prompt**:
```
Create dialogue/text box system for RPG:
- Display text at bottom of screen in bordered box
- Typewriter effect (reveal text gradually, 30 characters/second)
- Press Space to speed up or advance to next line
- Support for character portraits on left side
- Character name display
- Choice prompts (A/B/C options)
- Pause game while dialogue active
- Callback system for when dialogue completes

Provide example conversation with 5 lines and a choice
```

**Result Quality**: ★★★★★
**Generated**: Full dialogue system
**UX**: Professional RPG-style conversations

#### Prompt 15: Inventory System

**Prompt**:
```
Create inventory system for adventure game:
- Grid-based inventory (5x4 slots)
- Items have: name, icon (color), stackable (yes/no), maxStack
- Add/remove item functions
- Check if inventory has space
- Stack identical items automatically
- Visual rendering of inventory grid
- Mouse hover shows item name
- Click to use/equip item
- Drag and drop to rearrange (bonus feature)

Include example with 5 different item types
```

**Result Quality**: ★★★★☆
**Generated**: Functional inventory system
**Note**: Drag-drop may need refinement

### Procedural Generation Prompts

#### Prompt 16: Random Level Generation

**Prompt**:
```
Generate random platformer level:
- Grid-based (40x20 tiles, 32px per tile)
- Ground layer at bottom with gaps
- 3-5 floating platform groups at varying heights
- Ensure level is beatable (no impossible jumps)
- Place start position and goal (flag)
- Place 5-8 collectible coins on platforms
- Generate obstacles (spikes) on some ground sections
- Seed-based generation (same seed = same level)

Provide function generateLevel(seed) returning tile data
```

**Result Quality**: ★★★★☆
**Generated**: Working level generator
**Playability**: Usually good but occasionally creates difficult sections

#### Prompt 17: Procedural Dungeon

**Prompt**:
```
Generate random dungeon using BSP (Binary Space Partitioning):
- Dungeon size: 50x50 tiles
- Recursively split space into rooms
- 6-10 rooms of varying sizes (min 5x5, max 12x12)
- Connect rooms with corridors
- Place one door per room connection
- Place start room and boss room (furthest apart)
- Populate rooms with 2-4 enemies each (not start/boss rooms)
- Place treasure chests in 3 random rooms

Return dungeon as 2D array with tile types
```

**Result Quality**: ★★★★★
**Generated**: Excellent dungeon generation
**Variety**: Each dungeon feels unique

### Utility and Helper Prompts

#### Prompt 18: Collision Detection Library

**Prompt**:
```
Create collision detection utility library with functions:
- pointInRect(point, rect) - point inside rectangle
- rectIntersect(rect1, rect2) - AABB collision
- circleIntersect(circle1, circle2) - circle collision
- circleRectIntersect(circle, rect) - mixed shapes
- lineIntersect(line1, line2) - line segments
- raycast(origin, direction, objects) - ray intersection

Each function returns boolean or collision details object.
Include comprehensive comments and usage examples.
```

**Result Quality**: ★★★★★
**Generated**: Complete collision library
**Usefulness**: Reusable across many projects

#### Prompt 19: Audio Manager

**Prompt**:
```
Create audio manager using Web Audio API:
- Load and cache sound effects
- playSound(soundName, volume, pitch) method
- Background music with loop, volume control
- Fade in/out for music transitions
- Mute/unmute all audio
- Sound effect pooling (play same sound multiple times simultaneously)
- Programmatic sound generation for simple beeps

Support both audio files and generated sounds.
Include example usage.
```

**Result Quality**: ★★★★☆
**Generated**: Functional audio system
**Note**: File loading may need adjustment for your setup

#### Prompt 20: Debug Overlay

**Prompt**:
```
Create debug overlay for development:
- Toggle on/off with F1 key
- Display: FPS, entity count, mouse position, player coordinates
- Visual debug rendering: collision boxes, velocity vectors, paths
- Performance monitoring: update time, render time
- Console log display (last 5 messages)
- Minimal performance impact when disabled

Overlay should be semi-transparent and not interfere with gameplay
```

**Result Quality**: ★★★★★
**Generated**: Extremely useful debug tools
**Development**: Speeds up debugging significantly

---

## Debugging with Prompts

### Effective Debugging Prompts

#### Pattern 1: Bug Description

```
Template:
I have a bug where [SPECIFIC PROBLEM].

What happens: [Actual behavior]
What should happen: [Expected behavior]
When it occurs: [Conditions that trigger bug]

Relevant code:
[CODE]

What could be causing this?
```

**Example**:
```
I have a bug where the player falls through platforms at high speeds.

What happens: When falling quickly, player passes through platform without collision
What should happen: Player should land on platform regardless of speed
When it occurs: After falling for more than 2 seconds

Relevant code:
[paste collision detection code]

What could be causing this?
```

**Result**: Claude explains tunneling problem and suggests swept collision detection

#### Pattern 2: Error Message

```
Template:
I'm getting this error: "[ERROR MESSAGE]"

It occurs on line X: [CODE LINE]

Context:
[SURROUNDING CODE]

What does this error mean and how do I fix it?
```

### Common Bug Scenarios

**Physics Issues**:
```
"Objects accelerate infinitely instead of reaching max speed - what's wrong?"
"Player sticks to walls when trying to slide along them - how to fix?"
"Collision detection fails at high speeds - suggest solution"
```

**Rendering Issues**:
```
"Sprites flicker when moving - why?"
"Canvas clears unevenly leaving trails - what's the cause?"
"Z-ordering wrong, background renders over sprites - fix?"
```

**Logic Bugs**:
```
"Enemy AI gets stuck in corners - how to prevent?"
"Score increments multiple times for single event - why?"
"Game state doesn't reset properly on restart - missing something?"
```

---

## Meta-Prompting Techniques

### Prompts About Prompts

#### Ask for Prompt Improvements

```
"I want to add enemy AI to my game. How should I structure my prompt
to get the best result? What information should I include?"
```

**Result**: Claude suggests prompt structure and required details

#### Request Examples

```
"Show me 3 example prompts for creating a save/load system, from
beginner-friendly to advanced, explaining the differences"
```

#### Optimization Consultation

```
"I have a platformer game. What order should I prompt for features to
build the game most efficiently? Create a development roadmap."
```

### Explain Before Generating

```
"Before generating code, explain your approach to implementing
A* pathfinding for a grid-based game. What data structures will you
use? What are the key steps?"
```

**Benefit**: Understand the approach before seeing implementation

### Multiple Approaches

```
"Show me 3 different ways to implement player movement for a platformer:
1. Simple velocity-based
2. Physics engine integration
3. State machine approach

Explain pros and cons of each."
```

---

## Advanced Prompting Strategies

### Chain of Thought Prompting

Request step-by-step reasoning:

```
"I want to implement wall-jumping in my platformer. Before showing code,
explain step-by-step:
1. What state checks are needed?
2. How to detect if player is touching a wall?
3. What happens to velocity when wall-jump is triggered?
4. How to prevent infinite wall climbing?

Then provide the implementation."
```

### Constraint-Based Design

Define what you DON'T want:

```
"Create enemy pathfinding that:
- DOES NOT use expensive A* algorithm (too slow for 100 enemies)
- DOES NOT path through walls or obstacles
- DOES NOT require nav mesh generation

Suggest and implement an efficient alternative."
```

### Example-Driven Prompts

Show examples of desired behavior:

```
"Create a combo system where:
- Hit 1: 10 damage
- Hit 2 (within 1s): 15 damage
- Hit 3 (within 1s): 25 damage + knockback
- Break in timing resets to hit 1

Similar to how fighting games like Street Fighter track combos."
```

### Progressive Elaboration

Build complex features through dialogue:

```
You: "Create basic inventory system with 10 slots"
Claude: [Generates basic inventory]

You: "Add item categories (weapon, armor, consumable) with different background colors"
Claude: [Adds categories]

You: "Add equipment slots separate from inventory (helmet, chest, weapon, shield)"
Claude: [Implements equipment]

You: "Add stat bonuses from equipped items that affect player stats"
Claude: [Integrates stat system]
```

---

## Key Takeaways

1. **Specificity Wins**: Detailed prompts produce better first-try results
2. **Iterate Fearlessly**: Refine through conversation, not one perfect prompt
3. **Context Matters**: Explain what you're building and why
4. **Learn the Language**: Use game dev terminology
5. **Ask Questions**: Request explanations to deepen understanding
6. **Experiment**: Try variations to find what works for you
7. **Document Success**: Save prompts that work well

**Practice Exercise**: Take any vague prompt from this guide and rewrite it with maximum specificity. Then try both versions with Claude Code and compare results.

---

## Next Steps

**Continue Learning**:
- [troubleshooting-common-issues.md](troubleshooting-common-issues.md) - Solve common problems
- `docs/02-core-game-concepts/` - Deepen technical knowledge
- `prompts/` directory - More example prompts for specific tasks

**Practice**:
- Build a simple game using only the prompts from this guide
- Modify the example prompts for your own game ideas
- Create your own prompt library for common tasks

**Master prompt engineering and you'll build games 10x faster!**
