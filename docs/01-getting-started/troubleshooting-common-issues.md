# Troubleshooting Common Issues

A comprehensive guide to identifying and solving the most common problems when starting with Claude Code for game development. Save hours of frustration by quickly finding solutions to frequent issues.

## Table of Contents

- [How to Use This Guide](#how-to-use-this-guide)
- [Claude Code Issues](#claude-code-issues)
- [Game Development Issues](#game-development-issues)
- [Browser and Performance Issues](#browser-and-performance-issues)
- [Code Not Working as Expected](#code-not-working-as-expected)
- [Reading and Fixing Errors](#reading-and-fixing-errors)
- [Debugging Strategies](#debugging-strategies)
- [When to Ask for Help](#when-to-ask-for-help)
- [Resources for Learning More](#resources-for-learning-more)

---

## How to Use This Guide

**When you encounter a problem**:

1. **Identify the category** - Is it Claude Code, game logic, or browser related?
2. **Find your issue** - Use Ctrl+F to search for keywords
3. **Try the solution** - Follow step-by-step instructions
4. **Verify the fix** - Test that the problem is resolved
5. **Learn why** - Understand the cause to prevent future issues

**Quick Navigation**:
- Browser console errors → [Reading and Fixing Errors](#reading-and-fixing-errors)
- Game behaving strangely → [Game Development Issues](#game-development-issues)
- Claude Code not responding → [Claude Code Issues](#claude-code-issues)
- Slow performance → [Browser and Performance Issues](#browser-and-performance-issues)

---

## Claude Code Issues

### Issue 1: Claude Code Generates Code That Doesn't Work

**Symptoms**:
- Code has syntax errors
- Functions are undefined
- Features don't work as described

**Common Causes**:
- Vague prompt didn't communicate requirements clearly
- Missing context about your existing code
- Requesting features incompatible with your setup

**Solutions**:

1. **Be more specific in prompts**:
   ```
   Bad: "Add enemies"
   Good: "Add 3 enemy objects that move left-to-right between x=100 and x=700,
         bouncing off bounds. Use the same rendering style as my player."
   ```

2. **Provide context**:
   ```
   "Here's my current game code: [paste code]

   Add a scoring system that increments by 10 when player collects coins.
   Display score in top-left corner using the same font as the timer."
   ```

3. **Test incrementally**:
   - Test generated code immediately
   - Don't add multiple features at once
   - Easier to identify what broke

4. **Ask for explanations**:
   ```
   "This code isn't working. Explain what this function does line-by-line
   so I can understand what might be wrong."
   ```

### Issue 2: Claude Code Response Cut Off

**Symptoms**:
- Code ends mid-function
- Incomplete HTML tags
- Missing closing braces

**Cause**: Response length limit reached

**Solutions**:

1. **Request continuation**:
   ```
   "Continue from where you left off"
   ```

2. **Request specific section**:
   ```
   "Provide just the render() function"
   "Show only the collision detection code"
   ```

3. **Break into smaller prompts**:
   ```
   Instead of: "Create complete game with all features"

   Use: "Create basic game structure with canvas and game loop"
   Then: "Add player movement"
   Then: "Add enemy AI"
   ```

### Issue 3: Generated Code Uses Unknown Libraries

**Symptoms**:
- `Cannot find module` errors
- `X is not defined` errors
- Code references frameworks you don't have

**Cause**: Claude assumed you had certain libraries installed

**Solutions**:

1. **Specify vanilla JavaScript**:
   ```
   "Create this using vanilla JavaScript with no external libraries.
   Only use built-in browser APIs."
   ```

2. **Specify your tech stack**:
   ```
   "Using HTML5 Canvas 2D context and standard JavaScript (ES6+).
   No frameworks or libraries."
   ```

3. **Ask for library-free alternatives**:
   ```
   "This code uses the Matter.js physics library but I don't have it.
   Rewrite using simple custom physics instead."
   ```

### Issue 4: Can't Get Claude Code to Understand What You Want

**Symptoms**:
- Multiple attempts yield wrong results
- Generated code doesn't match your vision
- Frustration mounting

**Solutions**:

1. **Reset and start over**:
   - Start fresh conversation
   - Reframe your request completely
   - Use different terminology

2. **Show, don't tell**:
   ```
   "I want movement like classic Mario games where:
   - Running builds up speed over 0.3 seconds
   - Jumping while running = longer jump
   - Releasing jump early = shorter jump
   - Character slides slightly when changing direction"
   ```

3. **Provide examples**:
   ```
   "Create enemy behavior similar to Pac-Man ghosts:
   - Each enemy has different chase pattern
   - Enemies become vulnerable when player gets power-up
   - Scatter to corners periodically"
   ```

4. **Break down the request**:
   ```
   Instead of: "Add combat system"

   Try:
   "Add ability to attack with X key"
   "Add hitbox that appears in front of player during attack"
   "Add damage to enemies touched by hitbox"
   "Add attack cooldown of 0.5 seconds"
   ```

---

## Game Development Issues

### Issue 5: Game Runs Too Fast or Too Slow

**Symptoms**:
- Game speed varies on different computers
- Movement too fast or too slow
- Inconsistent behavior across browsers

**Cause**: Not using delta time for frame-rate independence

**Solution**:

```javascript
// WRONG - Frame-rate dependent
function update() {
  player.x += 5; // Moves 5px every frame, speed varies with FPS
}

// CORRECT - Frame-rate independent
let lastTime = 0;
function update(currentTime) {
  const deltaTime = (currentTime - lastTime) / 1000; // Convert to seconds
  lastTime = currentTime;

  const speed = 200; // pixels per second
  player.x += speed * deltaTime; // Consistent speed regardless of FPS
}

function gameLoop(currentTime) {
  update(currentTime);
  render();
  requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

**Claude Code Fix**:
```
"Make this game frame-rate independent by using delta time.
The game should run at the same speed regardless of FPS."
```

### Issue 6: Collision Detection Doesn't Work Reliably

**Symptoms**:
- Objects pass through each other
- Collisions detected when objects aren't touching
- Collisions work sometimes but not others

**Common Causes & Solutions**:

**Cause 1: High-Speed Tunneling**
- Object moves so fast it skips past collision zone

**Solution**:
```javascript
// Use swept collision detection or limit velocity
const maxVelocity = 10; // Limit to prevent tunneling
ball.dx = Math.max(-maxVelocity, Math.min(maxVelocity, ball.dx));
```

**Cause 2: Wrong Collision Algorithm**
- Using circle collision for rectangles or vice versa

**Solution**:
```
"I'm using circle collision but my objects are rectangles.
Update to use AABB (axis-aligned bounding box) collision detection."
```

**Cause 3: Coordinate System Confusion**
- Mixing world coordinates with screen coordinates

**Solution**:
```javascript
// Ensure all coordinates in same system
// If using camera, transform collision bounds to world space
const worldX = screenX + camera.x;
const worldY = screenY + camera.y;
```

**Debugging Collision**:
```javascript
// Visualize collision boxes
function debugRender() {
  ctx.strokeStyle = 'red';
  ctx.strokeRect(player.x, player.y, player.width, player.height);
  ctx.strokeRect(enemy.x, enemy.y, enemy.width, enemy.height);
}
```

### Issue 7: Physics Feels Wrong or Unrealistic

**Symptoms**:
- Jumps feel floaty
- Objects don't slow down
- Movement feels sluggish or too snappy

**Solutions**:

**For Floaty Jumps**:
```javascript
// Increase gravity
const gravity = 1200; // Higher = faster fall (was 600)

// Reduce gravity at jump peak for better feel
if (Math.abs(player.velocityY) < 50) {
  player.velocityY += gravity * 0.5 * deltaTime; // Half gravity near peak
} else {
  player.velocityY += gravity * deltaTime;
}
```

**For Sluggish Movement**:
```javascript
// Increase acceleration
const acceleration = 800; // Higher = faster response (was 400)

// Or use instant movement
if (keys.left) player.velocityX = -maxSpeed; // Instant max speed
if (keys.right) player.velocityX = maxSpeed;
```

**For No Friction**:
```javascript
// Add friction/deceleration
const friction = 0.85; // 0.8-0.95 typical range
player.velocityX *= friction;
player.velocityY *= friction;
```

**Claude Code Tuning**:
```
"The jumping feels floaty. Make the player fall faster by:
- Increasing gravity from 600 to 1200
- Adding variable jump height (release jump early = shorter jump)
- Reducing gravity slightly at jump peak for better feel"
```

### Issue 8: Game State Not Resetting Properly

**Symptoms**:
- Old enemies still present after restart
- Score doesn't reset
- Player position wrong on new game
- Memory leaks over multiple restarts

**Solution**:

```javascript
// Create initialization function
function initGame() {
  // Reset player
  player.x = canvas.width / 2;
  player.y = canvas.height / 2;
  player.velocityX = 0;
  player.velocityY = 0;
  player.health = 100;

  // Clear and recreate arrays
  enemies = [];
  bullets = [];
  particles = [];

  // Reset score
  score = 0;

  // Reset game state
  gameState = 'PLAYING';
}

// Call on start and restart
initGame(); // Start
// ... later on restart button
initGame(); // Restart
```

**Pattern**:
- Don't just modify values, recreate arrays
- Centralize initialization in one function
- Call same function for start and restart

### Issue 9: Input Lag or Unresponsive Controls

**Symptoms**:
- Delay between pressing key and action
- Controls feel sluggish
- Sometimes input doesn't register

**Causes & Solutions**:

**Cause 1: Checking Keys in Wrong Place**
```javascript
// WRONG - Only checks when event fires
window.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft') {
    player.x -= 5; // Only moves once per keypress
  }
});

// CORRECT - Track key state, check in update loop
const keys = {};
window.addEventListener('keydown', (e) => keys[e.key] = true);
window.addEventListener('keyup', (e) => keys[e.key] = false);

function update(deltaTime) {
  if (keys['ArrowLeft']) {
    player.x -= speed * deltaTime; // Continuous movement
  }
}
```

**Cause 2: Key Repeat Delay**
- Operating system key repeat delay

**Solution**: Use keydown/keyup state tracking (shown above)

**Cause 3: Low Frame Rate**
- Game running slowly causes input lag

**Solution**: See [Browser and Performance Issues](#browser-and-performance-issues)

---

## Browser and Performance Issues

### Issue 10: Game Runs Slowly or Stutters

**Symptoms**:
- FPS drops below 60
- Periodic freezes
- Sluggish animation

**Diagnostic Steps**:

1. **Check FPS**:
```javascript
let fps = 0;
let frameCount = 0;
let lastFpsUpdate = 0;

function update(currentTime) {
  frameCount++;
  if (currentTime - lastFpsUpdate >= 1000) {
    fps = frameCount;
    frameCount = 0;
    lastFpsUpdate = currentTime;
    console.log('FPS:', fps);
  }
}
```

2. **Profile Performance**:
   - Open browser DevTools (F12)
   - Go to Performance tab
   - Click Record, play game for 5 seconds, stop
   - Look for long tasks or bottlenecks

**Common Causes & Solutions**:

**Too Many Objects**:
```javascript
// Limit active entities
const MAX_BULLETS = 50;
if (bullets.length < MAX_BULLETS) {
  bullets.push(createBullet());
}

// Remove off-screen entities
bullets = bullets.filter(b =>
  b.x > 0 && b.x < canvas.width &&
  b.y > 0 && b.y < canvas.height
);
```

**Expensive Rendering**:
```javascript
// Cache instead of recalculating
// WRONG - Creates gradient every frame
ctx.fillStyle = ctx.createLinearGradient(0, 0, 800, 600);

// CORRECT - Create once, reuse
const backgroundGradient = ctx.createLinearGradient(0, 0, 800, 600);
backgroundGradient.addColorStop(0, '#000033');
backgroundGradient.addColorStop(1, '#000011');

function render() {
  ctx.fillStyle = backgroundGradient; // Reuse
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}
```

**Too Many Collision Checks**:
```javascript
// WRONG - O(n²) complexity
for (let i = 0; i < enemies.length; i++) {
  for (let j = 0; j < bullets.length; j++) {
    checkCollision(enemies[i], bullets[j]); // Expensive!
  }
}

// BETTER - Spatial partitioning or early exits
bullets.forEach(bullet => {
  // Only check nearby enemies
  const nearbyEnemies = enemies.filter(e =>
    distance(e, bullet) < 100 // Quick distance check first
  );
  nearbyEnemies.forEach(enemy => {
    checkCollision(enemy, bullet);
  });
});
```

### Issue 11: Canvas Not Displaying or Blank Screen

**Symptoms**:
- Blank white or black canvas
- No errors in console
- Code seems to run but nothing visible

**Diagnostic Checklist**:

1. **Check canvas exists**:
```javascript
const canvas = document.getElementById('gameCanvas');
if (!canvas) {
  console.error('Canvas not found!');
}
```

2. **Verify 2D context**:
```javascript
const ctx = canvas.getContext('2d');
console.log('Context:', ctx); // Should not be null
```

3. **Check drawing commands execute**:
```javascript
function render() {
  console.log('Rendering...'); // Should log every frame
  ctx.fillStyle = 'red';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}
```

4. **Verify canvas size**:
```javascript
console.log('Canvas size:', canvas.width, canvas.height);
// Should not be 0x0
```

**Common Causes**:

**Canvas size not set**:
```html
<!-- WRONG -->
<canvas id="gameCanvas"></canvas>

<!-- CORRECT -->
<canvas id="gameCanvas" width="800" height="600"></canvas>
```

**Clearing canvas incorrectly**:
```javascript
// This works
ctx.clearRect(0, 0, canvas.width, canvas.height);

// Or this
ctx.fillStyle = 'black';
ctx.fillRect(0, 0, canvas.width, canvas.height);
```

**Drawing off-screen**:
```javascript
// Check coordinates are within canvas bounds
console.log('Drawing at:', player.x, player.y);
console.log('Canvas size:', canvas.width, canvas.height);
```

### Issue 12: Audio Not Playing

**Symptoms**:
- No sound effects or music
- No errors in console
- Audio code exists but silent

**Solutions**:

1. **Check browser autoplay policy**:
```javascript
// Audio must be triggered by user interaction
// WRONG - Won't work on page load
const audio = new Audio('sound.mp3');
audio.play(); // Blocked by browser

// CORRECT - Play after user interaction
document.addEventListener('click', () => {
  audio.play(); // Works!
}, { once: true });
```

2. **Verify Web Audio API initialization**:
```javascript
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

// Resume context after user interaction
document.addEventListener('click', () => {
  if (audioContext.state === 'suspended') {
    audioContext.resume();
  }
}, { once: true });
```

3. **Check volume and mute state**:
```javascript
console.log('Volume:', audio.volume); // Should be > 0
console.log('Muted:', audio.muted); // Should be false
```

---

## Code Not Working as Expected

### Issue 13: Variables Showing as Undefined

**Symptoms**:
- `Cannot read property of undefined` errors
- Variables are undefined when they should have values

**Common Causes**:

**Scope Issues**:
```javascript
// WRONG - variable not accessible
function init() {
  let player = { x: 100, y: 100 }; // Only exists in init()
}
function update() {
  player.x += 5; // Error: player is not defined
}

// CORRECT - proper scope
let player; // Declare outside functions
function init() {
  player = { x: 100, y: 100 }; // Initialize
}
function update() {
  player.x += 5; // Works!
}
```

**Timing Issues**:
```javascript
// WRONG - using before initialization
console.log(player.x); // Error!
let player = { x: 100, y: 100 };

// CORRECT - initialize first
let player = { x: 100, y: 100 };
console.log(player.x); // Works!
```

### Issue 14: Code Runs Once But Not Continuously

**Symptoms**:
- Animation doesn't loop
- Game updates once and stops
- No continuous behavior

**Cause**: Missing game loop or not calling recursively

**Solution**:
```javascript
// WRONG - Only runs once
function gameLoop() {
  update();
  render();
  // Stops here!
}
gameLoop();

// CORRECT - Continuous loop
function gameLoop() {
  update();
  render();
  requestAnimationFrame(gameLoop); // Call again!
}
gameLoop(); // Start loop
```

---

## Reading and Fixing Errors

### Common Error Messages

**ReferenceError: X is not defined**
- **Meaning**: Variable doesn't exist or is out of scope
- **Fix**: Declare variable or check scope

**TypeError: Cannot read property 'x' of undefined**
- **Meaning**: Trying to access property of undefined object
- **Fix**: Initialize object or add null check

**SyntaxError: Unexpected token**
- **Meaning**: Code has syntax error (missing bracket, etc.)
- **Fix**: Check for matching braces, parentheses, quotes

**TypeError: X is not a function**
- **Meaning**: Trying to call something that isn't a function
- **Fix**: Verify function exists and is spelled correctly

### Using Browser Console Effectively

**View errors**:
- Open DevTools (F12)
- Click Console tab
- Red messages are errors (click for details)

**Add debug output**:
```javascript
console.log('Player position:', player.x, player.y);
console.log('Collision detected:', hasCollision);
console.table({ x: player.x, y: player.y, velocityX: player.dx });
```

**Set breakpoints**:
- Open Sources tab
- Find your file
- Click line number to set breakpoint
- Refresh page, code pauses at breakpoint
- Inspect variables in Scope panel

---

## Debugging Strategies

### 1. Isolate the Problem

**Divide and conquer**:
- Comment out code sections to find what breaks
- Test one feature at a time
- Revert to last working version

### 2. Add Logging

```javascript
// Log game state
function update() {
  console.log('Update called, player at:', player.x, player.y);
  console.log('Enemies:', enemies.length);
  console.log('Bullets:', bullets.length);
}
```

### 3. Visualize Debug Info

```javascript
// Draw debug information
function debugRender() {
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText(`FPS: ${fps}`, 10, 20);
  ctx.fillText(`Player: ${Math.round(player.x)}, ${Math.round(player.y)}`, 10, 40);
  ctx.fillText(`Velocity: ${player.velocityX.toFixed(2)}, ${player.velocityY.toFixed(2)}`, 10, 60);

  // Draw collision boxes
  ctx.strokeStyle = 'red';
  ctx.strokeRect(player.x, player.y, player.width, player.height);
}
```

### 4. Use Claude Code for Debugging

```
"I have a bug where [describe problem]. Here's the relevant code:
[paste code]

Help me debug this. What could be wrong?"
```

---

## When to Ask for Help

**Ask for help when**:
- Stuck for more than 30 minutes on same issue
- Error message unclear even after research
- Tried multiple solutions without success
- Need architectural guidance

**Before asking**:
1. Check this troubleshooting guide
2. Search GitHub Discussions
3. Try isolating the problem
4. Gather information about the issue

**How to ask effectively**:
```markdown
**What I'm trying to do**: [Goal]
**What's happening**: [Actual behavior]
**What should happen**: [Expected behavior]
**What I've tried**: [Solutions attempted]

**Code**:
[Paste relevant code]

**Error message** (if any):
[Full error text]
```

---

## Resources for Learning More

**Official Documentation**:
- [MDN Web Docs](https://developer.mozilla.org) - JavaScript and Web APIs
- [Canvas API Reference](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)

**Game Development**:
- `docs/02-core-game-concepts/` - Deep dives into game systems
- [Game Programming Patterns](https://gameprogrammingpatterns.com) - Free book

**Community**:
- GitHub Discussions for this repository
- Stack Overflow - tag questions with [html5-canvas] [javascript]

**Remember**: Every developer encounters these issues. Debugging is a skill that improves with practice. Use this guide as your first resource, and don't hesitate to ask for help when needed!

---

**Next**: Continue to [claude-code-fundamentals.md](claude-code-fundamentals.md) or start building with [first-game-in-10-minutes.md](first-game-in-10-minutes.md)
