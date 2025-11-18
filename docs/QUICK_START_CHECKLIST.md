# Quick Start Checklist: Game Development from Terminal

A condensed checklist for managing your entire game development from Claude Code terminal.

---

## 🚀 Project Setup (One-Time)

- [ ] Install Claude Code, Node.js, Git
- [ ] Install global tools: `npm install -g vite serve eslint`
- [ ] Configure Git identity
- [ ] Set up workspace: `mkdir ~/game-development && cd ~/game-development`

---

## 📁 New Project Initialization

```bash
# Quick project setup
mkdir my-game && cd my-game
git init
npm init -y
npm install --save-dev vite
mkdir -p src/{game,systems,entities} assets public tests

# Create entry files
cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>My Game</title>
<style>body{margin:0;padding:0;overflow:hidden;}canvas{display:block;}</style>
</head><body><script type="module" src="/src/main.js"></script></body></html>
EOF

# .gitignore
echo -e "node_modules/\ndist/\n.DS_Store\n*.log" > .gitignore

# Initial commit
git add . && git commit -m "Initial setup"
```

---

## 💻 Daily Development Workflow

### 1. Start Your Day

```bash
cd ~/game-development/my-game
git pull origin main
npm install  # if package.json changed
npm run dev  # starts dev server
```

### 2. Claude Code Prompts

**Core Systems:**
```
Create src/main.js with:
- Game loop using requestAnimationFrame
- Delta time calculation
- Canvas setup (800x600)
- update() and render() functions
```

**Player System:**
```
Create src/systems/player.js with:
- Player class (position, velocity, size)
- Keyboard input (WASD/Arrows)
- Gravity and jump physics
- Export as ES6 module
```

**Collision System:**
```
Create src/systems/collision.js with:
- AABB collision detection
- Circle collision detection
- Export collision utilities
```

### 3. Testing & Debugging

```bash
# Run tests
npm test

# Check for errors
npm run lint

# View in browser
open http://localhost:3000
```

### 4. Version Control

```bash
# Check status
git status

# Stage and commit
git add .
git commit -m "feat: add player movement system"

# Push changes
git push origin main
```

---

## 🎮 Feature Development Checklist

- [ ] **Core Game Loop**
  - [ ] RequestAnimationFrame setup
  - [ ] Delta time for frame independence
  - [ ] Update/render separation

- [ ] **Input System**
  - [ ] Keyboard input handling
  - [ ] Mouse/touch support
  - [ ] Input buffering

- [ ] **Player System**
  - [ ] Movement controls
  - [ ] Physics (gravity, velocity)
  - [ ] Collision with boundaries
  - [ ] Animation states

- [ ] **Rendering**
  - [ ] Canvas context setup
  - [ ] Sprite rendering
  - [ ] Camera/viewport
  - [ ] Particle effects

- [ ] **Collision Detection**
  - [ ] AABB detection
  - [ ] Circle detection
  - [ ] Spatial partitioning (for optimization)

- [ ] **Enemy AI**
  - [ ] Basic movement patterns
  - [ ] Pathfinding (A*)
  - [ ] Behavior states

- [ ] **Audio System**
  - [ ] Web Audio API setup
  - [ ] Sound effects
  - [ ] Background music
  - [ ] Volume controls

- [ ] **UI/Menus**
  - [ ] Main menu
  - [ ] Pause menu
  - [ ] HUD (score, health, etc.)
  - [ ] Game over screen

- [ ] **Game State**
  - [ ] Menu state
  - [ ] Playing state
  - [ ] Paused state
  - [ ] Game over state

- [ ] **Save/Load**
  - [ ] LocalStorage integration
  - [ ] Save game state
  - [ ] Load game state
  - [ ] High scores

---

## 🧪 Testing Checklist

```bash
# Set up testing
npm install --save-dev jest @types/jest @babel/preset-env

# Create tests with Claude
"Create tests/[system].test.js with Jest tests for [functionality]"

# Run tests
npm test
npm test -- --watch
npm test -- --coverage
```

**Test Coverage:**
- [ ] Core game loop
- [ ] Collision detection
- [ ] Player movement
- [ ] Enemy AI
- [ ] Score calculation
- [ ] State management

---

## 📦 Asset Management

```bash
# Organize assets
mkdir -p assets/{sprites,audio,fonts,data}

# Generate asset loader with Claude
"Create src/utils/assetLoader.js with Promise-based loading,
progress tracking, and error handling"

# Optimize images
npm install --save-dev imagemin imagemin-pngquant
node tools/optimize-assets.js
```

---

## 🔨 Build & Deploy

### Pre-Deploy Checklist

- [ ] All tests pass: `npm test`
- [ ] No console.log in production code
- [ ] Assets optimized
- [ ] Bundle size acceptable (<5MB)
- [ ] Environment variables set

### Build & Deploy

```bash
# Production build
npm run build

# Check build size
du -sh dist/

# Deploy (choose platform)
npm run deploy          # GitHub Pages
# OR
netlify deploy --prod   # Netlify
# OR
vercel --prod          # Vercel

# Tag release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin --tags
```

---

## 🐛 Debug Commands

```bash
# Find process on port
lsof -i :3000
kill -9 <PID>

# Clean rebuild
rm -rf node_modules dist .cache
npm install
npm run build

# Git conflicts
git status  # see conflicts
# Resolve in editor
git add .
git commit

# Check bundle size
npm run build
ls -lh dist/

# Performance profiling
# Open browser DevTools > Performance > Record
```

---

## 📊 Performance Optimization

```bash
# Analyze bundle
npm install --save-dev rollup-plugin-visualizer
npm run build
open dist/stats.html

# Profile with Claude
"Review src/ for performance optimizations:
- Remove debug code
- Use object pooling
- Optimize collision checks
- Add spatial partitioning"

# Lighthouse audit
npm install --save-dev @lhci/cli
npx lhci autorun
```

---

## 🎯 Common Claude Code Prompts

### Generation
```
Create [file] with:
- [requirement 1]
- [requirement 2]
- [requirement 3]
```

### Refinement
```
Modify [file] to add:
- [new feature]
- [improvement]
```

### Debugging
```
Fix bug in [file] where [description of bug]
```

### Optimization
```
Optimize [file] for:
- Performance
- Memory usage
- Code readability
```

### Testing
```
Create tests/[name].test.js with tests for:
- [test case 1]
- [test case 2]
```

---

## 🔄 Git Workflow

```bash
# Daily workflow
git pull origin main
# ... work ...
git add .
git commit -m "type: description"
git push origin main

# Feature branch
git checkout -b feature/new-feature
# ... work ...
git commit -m "feat: add new feature"
git checkout main
git merge feature/new-feature
git push origin main

# Commit types
# feat: new feature
# fix: bug fix
# refactor: code restructure
# perf: performance improvement
# test: add tests
# docs: documentation
```

---

## ⚡ Terminal Productivity

### Useful Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias gd='cd ~/game-development'
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
alias gameserve='npm run dev'
alias gamebuild='npm run build'
alias gametest='npm test'
```

### tmux Layout

```bash
# Start tmux session
tmux new -s game

# Split panes
Ctrl+b %    # Split vertical
Ctrl+b "    # Split horizontal
Ctrl+b o    # Switch pane

# Suggested layout:
# Pane 1: Dev server (npm run dev)
# Pane 2: Claude Code prompts
# Pane 3: Git & file operations
# Pane 4: Testing (npm test -- --watch)
```

---

## 📚 Documentation Reference

- **Full Terminal Workflow**: `docs/TERMINAL_WORKFLOW_GUIDE.md`
- **Getting Started**: `docs/01-getting-started/`
- **Core Concepts**: `docs/02-core-game-concepts/`
- **Graphics**: `docs/03-graphics-rendering/`
- **Game AI**: `docs/04-game-ai/`
- **Audio**: `docs/05-audio-systems/`
- **Multiplayer**: `docs/06-networking-multiplayer/`
- **UI/UX**: `docs/07-ui-ux/`
- **Testing**: `docs/11-testing-qa/`
- **Deployment**: `docs/12-deployment-distribution/`

---

## 🎓 Learning Path

### Week 1: Fundamentals
- Day 1-2: Setup, build Pong
- Day 3-4: Build Snake
- Day 5-6: Study game loops and timing
- Day 7: Build your own variant

### Week 2: Core Mechanics
- Day 8-9: Build Breakout
- Day 10-11: Study collision detection
- Day 12-13: Build Asteroids
- Day 14: Create simple original game

### Week 3: Advanced Features
- Day 15-16: Build Tetris
- Day 17-18: Study state management
- Day 19-20: Build Flappy Bird
- Day 21: Plan original game

### Week 4: Your Game
- Day 22-25: Build original game
- Day 26-27: Polish and audio
- Day 28: Deploy and share

---

## ✅ End of Day Checklist

- [ ] Commit all changes: `git commit -m "..."`
- [ ] Push to remote: `git push origin main`
- [ ] Tests passing: `npm test`
- [ ] Dev server stopped: `Ctrl+C`
- [ ] Document progress/TODOs

---

## 🆘 Quick Help

**Can't start dev server?**
```bash
lsof -i :3000 && kill -9 <PID>
npm run dev
```

**Build failing?**
```bash
rm -rf dist node_modules
npm install
npm run build
```

**Git conflicts?**
```bash
git status
# Edit conflicted files (look for <<<<<<)
git add .
git commit
```

**Claude Code issues?**
```bash
claude status
claude auth login
```

---

**Print this checklist and keep it by your workspace!**
