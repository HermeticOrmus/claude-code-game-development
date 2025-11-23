# /game-prototype Command

## Usage
```
/game-prototype [game-type] [features...]
```

## Description
Rapidly prototype a complete, playable game using meta-prompting iteration. This command orchestrates multiple skills to generate a working game in minutes.

## Arguments

### game-type (required)
- `pong` - Classic paddle game
- `snake` - Grid-based snake game
- `breakout` - Brick breaker
- `asteroids` - Space shooter
- `platformer` - Side-scrolling platformer
- `shooter` - Top-down shooter
- `puzzle` - Tile matching puzzle
- `endless-runner` - Infinite side-scroller
- `tower-defense` - Strategy defense game
- `custom` - Describe your own game

### features (optional)
- `--ai` - Include AI opponent/enemies
- `--sound` - Include audio system
- `--particles` - Include particle effects
- `--mobile` - Mobile-friendly (touch controls)
- `--multiplayer` - Local multiplayer (same device)
- `--save` - Save/load functionality
- `--levels` - Multiple levels/progression

## Examples

### Basic Pong
```
/game-prototype pong
```

### Snake with AI and Sound
```
/game-prototype snake --ai --sound
```

### Mobile-Friendly Endless Runner
```
/game-prototype endless-runner --mobile --particles

### Custom Game
```
/game-prototype custom "A roguelike dungeon crawler with procedural generation and turn-based combat"
```

## Process

### Phase 1: Analysis (0-10 seconds)
1. Analyze game type complexity
2. Determine required systems
3. Select appropriate architecture pattern
4. Plan file structure

### Phase 2: Core Generation (10-60 seconds)
Using the meta-prompting engine:

1. **Iteration 1**: Generate core game loop and main systems
   - Game class
   - Input handling
   - Basic rendering

2. **Iteration 2**: Refine based on quality assessment
   - Fix identified issues
   - Improve game feel
   - Add missing edge cases

3. **Iteration 3**: Polish (if quality < 0.90)
   - Performance optimization
   - Code cleanup
   - Documentation

### Phase 3: Feature Integration (30-120 seconds)
For each optional feature:
1. Generate feature module
2. Integrate with core systems
3. Test integration points

### Phase 4: Packaging (5-10 seconds)
1. Generate index.html
2. Create README with instructions
3. Add CSS styling
4. Package as playable game

## Output Structure

```
[game-name]/
├── index.html          # Entry point
├── style.css           # Styling
├── README.md           # Instructions
├── src/
│   ├── main.js         # Game initialization
│   ├── game.js         # Core game logic
│   ├── renderer.js     # Drawing code
│   ├── input.js        # Input handling
│   ├── entities/       # Game objects
│   │   ├── Player.js
│   │   ├── Enemy.js    # (if --ai)
│   │   └── ...
│   ├── systems/        # Game systems
│   │   ├── collision.js
│   │   ├── audio.js    # (if --sound)
│   │   ├── particles.js# (if --particles)
│   │   └── ...
│   └── utils/          # Helpers
│       ├── math.js
│       └── ...
└── assets/             # (if needed)
    ├── sounds/
    └── sprites/
```

## Quality Metrics

The command aims for:
- **Playability**: 100% - Game must be playable
- **Performance**: 60 FPS on mid-range hardware
- **Code Quality**: > 0.85 meta-prompting score
- **Completeness**: All requested features implemented

## Game Type Specifications

### Pong
- Two paddles (player vs AI or player vs player)
- Ball physics with angle variation
- Score tracking (first to 11)
- Increasing difficulty (ball speed)

### Snake
- Grid-based movement
- Growing snake body
- Food spawning
- Self-collision detection
- Wall collision (wrapping or death)

### Breakout
- Paddle at bottom
- Brick grid (min 5x8)
- Ball physics with spin
- Brick health (1-3 hits)
- Power-ups (multi-ball, paddle size, etc.)

### Asteroids
- Vector graphics style
- Ship rotation and thrust
- Asteroid splitting
- Hyperspace (teleport)
- UFO enemy (waves)

### Platformer
- Gravity and jumping
- Multiple platforms
- Enemy AI (patrol, chase)
- Collectibles
- Level completion goal

### Shooter
- 8-directional movement
- Projectile system
- Enemy waves
- Health system
- Boss enemy (every 5 waves)

### Puzzle
- Grid of colored tiles
- Match-3 or higher
- Gravity (tiles fall)
- Chain reactions
- Score multipliers

### Endless Runner
- Auto-run (player controls jump/duck)
- Procedural obstacles
- Increasing speed
- Score = distance
- Power-ups (shield, magnet)

### Tower Defense
- Path-based enemies
- Tower placement grid
- Multiple tower types
- Wave system
- Resource management

## Customization

After generation, the game can be customized by:

1. Modifying constants in `game.js`
2. Adjusting visuals in `renderer.js`
3. Tweaking physics in entity files
4. Adding new features with additional skills

## Related Commands
- `/game-system` - Generate individual game systems
- `/game-debug` - Add debug tools to existing game
- `/game-optimize` - Optimize game performance
- `/game-deploy` - Prepare game for deployment
