# Complete Guide: Managing Game Development from Claude Code Terminal

## Table of Contents

1. [Introduction](#1-introduction)
2. [Initial Setup](#2-initial-setup)
3. [Project Initialization](#3-project-initialization)
4. [Development Workflow](#4-development-workflow)
5. [Code Generation with Claude](#5-code-generation-with-claude)
6. [Testing & Debugging](#6-testing--debugging)
7. [Asset Management](#7-asset-management)
8. [Version Control](#8-version-control)
9. [Build & Optimization](#9-build--optimization)
10. [Deployment](#10-deployment)

---

## 1. Introduction

This guide provides a complete 1-100 workflow for managing game development entirely through the Claude Code terminal window. Every command, every prompt, every step needed to go from idea to deployed game.

### What You'll Learn

- How to use Claude Code terminal for every aspect of game development
- Terminal commands for project setup, development, testing, and deployment
- Effective Claude Code prompts for game systems
- Automation and scripting for repetitive tasks
- Complete CI/CD pipeline setup from terminal

### Prerequisites

- Claude Code installed and configured
- Basic terminal/command line knowledge
- Git installed
- Node.js and npm installed (for build tools)

---

## 2. Initial Setup

### Step 1: Verify Your Environment

```bash
# Check Claude Code version
claude --version

# Verify Node.js and npm
node --version
npm --version

# Verify Git
git --version

# Check current directory
pwd
```

### Step 2: Create Your Workspace

```bash
# Create a game development workspace
mkdir ~/game-development
cd ~/game-development

# Create directory structure
mkdir -p projects
mkdir -p templates
mkdir -p assets/shared
mkdir -p tools
```

### Step 3: Set Up Global Tools

```bash
# Install essential development tools
npm install -g serve          # Local web server
npm install -g live-server     # Auto-reload development server
npm install -g vite            # Modern build tool
npm install -g http-server     # Simple HTTP server

# Install optional tools
npm install -g eslint          # Code linting
npm install -g prettier        # Code formatting
npm install -g playwright      # Testing framework
```

### Step 4: Configure Git (if not already done)

```bash
# Set your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Set default editor (optional)
git config --global core.editor "nano"
```

---

## 3. Project Initialization

### Step 5: Start a New Game Project

```bash
# Navigate to projects directory
cd ~/game-development/projects

# Create new project
mkdir my-platformer-game
cd my-platformer-game

# Initialize Git repository
git init

# Create initial directory structure
mkdir -p src/{game,systems,entities,utils}
mkdir -p assets/{sprites,audio,fonts}
mkdir -p public
mkdir -p tests
```

### Step 6: Initialize Package Manager

```bash
# Create package.json
npm init -y

# Install development dependencies
npm install --save-dev vite
npm install --save-dev eslint prettier

# Install game dependencies (as needed)
npm install --save phaser  # If using Phaser
# OR
npm install --save three   # If using Three.js
```

### Step 7: Create Configuration Files

```bash
# Create .gitignore
cat > .gitignore << 'EOF'
node_modules/
dist/
build/
.DS_Store
*.log
.env
.cache/
coverage/
EOF

# Create basic HTML entry point
cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Game</title>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
    <script type="module" src="/src/main.js"></script>
</body>
</html>
EOF

# Create Vite config
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite';

export default defineConfig({
  root: './public',
  publicDir: '../assets',
  build: {
    outDir: '../dist',
    emptyOutDir: true
  },
  server: {
    port: 3000,
    open: true
  }
});
EOF
```

### Step 8: Add npm Scripts

```bash
# Update package.json scripts using Claude Code
```

**Claude Code Prompt:**
```
Add the following scripts to my package.json:
- "dev": start development server with Vite
- "build": create production build
- "preview": preview production build
- "lint": run ESLint on src directory
- "test": run tests with Jest
```

### Step 9: Create Initial Commit

```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Initial project setup"

# View status
git status
```

---

## 4. Development Workflow

### Step 10: Start Development Server

```bash
# Start dev server
npm run dev

# Server starts at http://localhost:3000
# Terminal shows server status and hot reload info
```

### Step 11: Open Claude Code in Project

```bash
# Open Claude Code in current project
claude .

# Or specify the project directory
claude ~/game-development/projects/my-platformer-game
```

### Step 12: Organize Your Terminal Workflow

**Recommended Terminal Setup:**

```bash
# Terminal 1: Development server
npm run dev

# Terminal 2: Git operations and file management
# (Keep this terminal open in project root)

# Terminal 3: Claude Code prompts
# (Use this for generating code and running commands)

# Terminal 4: Testing and debugging
# (Use for running tests and debugging tools)
```

**Using tmux for Terminal Management:**

```bash
# Install tmux (if not installed)
# Ubuntu/Debian: sudo apt install tmux
# macOS: brew install tmux

# Start tmux session
tmux new -s gamedev

# Create split layout
Ctrl+b %    # Split vertical
Ctrl+b "    # Split horizontal
Ctrl+b o    # Switch panes

# Example layout for game development:
# Pane 1: Development server
# Pane 2: Claude Code prompts
# Pane 3: File operations and git
# Pane 4: Testing/debugging
```

### Step 13: Watch Files for Changes

```bash
# Watch and auto-lint files
npm run lint -- --watch

# Watch tests (if using Jest)
npm run test -- --watch

# Watch specific directories
ls src/**/*.js | entr npm run lint
```

---

## 5. Code Generation with Claude

### Step 14: Core Game Loop Prompt

**Claude Code Prompt:**
```
Create a game loop in src/main.js with:
- RequestAnimationFrame for smooth rendering
- Delta time calculation for frame-rate independence
- Separate update() and render() functions
- FPS counter
- Basic canvas setup (800x600)
- Pause/resume functionality
```

### Step 15: Generate Game Systems

**Player System Prompt:**
```
Create src/systems/player.js with:
- Player class with position, velocity, size
- Keyboard input handling (WASD and Arrow keys)
- Gravity and jumping physics
- Collision boundary checking
- Animation state management
- Export as ES6 module
```

**Collision System Prompt:**
```
Create src/systems/collision.js with:
- AABB collision detection function
- Circle collision detection function
- Collision resolution with response
- Spatial hash grid for optimization
- Export collision utilities
```

**Rendering System Prompt:**
```
Create src/systems/renderer.js with:
- Canvas context management
- Layer-based rendering system
- Camera/viewport system
- Debug rendering mode
- Sprite rendering utilities
```

### Step 16: Verify Generated Code

```bash
# Check syntax errors
npm run lint

# View file structure
ls -R src/

# Check file sizes (to ensure code was generated)
du -sh src/**/*.js

# View specific generated file
cat src/systems/player.js
```

### Step 17: Iterative Refinement

**Refinement Prompt Template:**
```
Modify src/systems/player.js to add:
- Double jump capability (max 2 jumps)
- Wall sliding when touching vertical surfaces
- Dash ability with cooldown (3 second cooldown)
- Particle effects on jump and dash
- Sound effect triggers (we'll add audio later)
```

### Step 18: Test Generated Code

```bash
# Start dev server if not running
npm run dev

# Open browser and check console
# Look for errors in terminal

# Check browser console
# Open: http://localhost:3000
# Press F12 for DevTools
```

---

## 6. Testing & Debugging

### Step 19: Set Up Testing Framework

```bash
# Install Jest for testing
npm install --save-dev jest @types/jest
npm install --save-dev @babel/preset-env

# Create Jest config
cat > jest.config.js << 'EOF'
module.exports = {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.js$': 'babel-jest'
  },
  moduleFileExtensions: ['js'],
  testMatch: ['**/tests/**/*.test.js']
};
EOF

# Create Babel config for Jest
cat > babel.config.js << 'EOF'
module.exports = {
  presets: [['@babel/preset-env', {targets: {node: 'current'}}]]
};
EOF
```

### Step 20: Generate Tests with Claude

**Test Generation Prompt:**
```
Create tests/collision.test.js with Jest tests for:
- AABB collision detection (4 test cases)
- Circle collision detection (4 test cases)
- Collision response (3 test cases)
- Edge cases (null inputs, zero-size objects)
- Performance test for 1000 collision checks
```

### Step 21: Run Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- tests/collision.test.js
```

### Step 22: Debug with Browser DevTools

```bash
# Start development server with source maps
npm run dev

# Open browser at http://localhost:3000
# Open DevTools (F12)
# Go to Sources tab
# Set breakpoints in your code

# In terminal, view console logs
# Use console.log() in code to debug
```

### Step 23: Performance Profiling

**Claude Code Prompt:**
```
Create src/utils/profiler.js with:
- FPS tracking and display
- Frame time measurement
- Memory usage monitoring (if available)
- Performance markers for different systems
- Export startProfile(), endProfile(), and displayStats() functions
```

```bash
# Integrate profiler
# Run game and check performance
npm run dev

# For detailed profiling, use Chrome DevTools
# Performance tab > Record > Play game > Stop
```

### Step 24: Debug Rendering Issues

```bash
# Enable debug rendering
# Add ?debug=true to URL: http://localhost:3000?debug=true
```

**Claude Code Prompt for Debug Mode:**
```
Modify src/systems/renderer.js to add debug mode that shows:
- Collision boxes (green rectangles)
- Velocity vectors (blue arrows)
- Grid overlay (light gray)
- Entity centers (red dots)
- FPS counter (top left)
Debug mode should activate when ?debug=true in URL
```

---

## 7. Asset Management

### Step 25: Organize Assets

```bash
# Create asset directory structure
mkdir -p assets/sprites/{characters,enemies,items,tiles}
mkdir -p assets/audio/{music,sfx}
mkdir -p assets/fonts
mkdir -p assets/data

# Create manifest file
cat > assets/manifest.json << 'EOF'
{
  "sprites": [
    "sprites/characters/player.png",
    "sprites/enemies/enemy1.png"
  ],
  "audio": [
    "audio/music/theme.mp3",
    "audio/sfx/jump.wav"
  ],
  "fonts": [
    "fonts/game-font.ttf"
  ]
}
EOF
```

### Step 26: Generate Asset Loader

**Claude Code Prompt:**
```
Create src/utils/assetLoader.js with:
- Load assets from manifest.json
- Promise-based loading with async/await
- Loading progress tracking (percentage)
- Error handling for failed loads
- Cache loaded assets
- Support for images, audio, and JSON
- Export loadAssets() function
```

### Step 27: Optimize Assets

```bash
# Install image optimization tools
npm install --save-dev imagemin imagemin-pngquant imagemin-mozjpeg

# Create optimization script
cat > tools/optimize-assets.js << 'EOF'
const imagemin = require('imagemin');
const imageminPngquant = require('imagemin-pngquant');
const imageminMozjpeg = require('imagemin-mozjpeg');

(async () => {
  await imagemin(['assets/sprites/**/*.{jpg,png}'], {
    destination: 'assets/sprites-optimized',
    plugins: [
      imageminMozjpeg({quality: 80}),
      imageminPngquant({quality: [0.6, 0.8]})
    ]
  });
  console.log('Images optimized!');
})();
EOF

# Run optimization
node tools/optimize-assets.js
```

### Step 28: Audio Management

```bash
# Convert audio to web formats
# Install FFmpeg first (if not installed)

# Convert to multiple formats for compatibility
for file in assets/audio/**/*.wav; do
  ffmpeg -i "$file" -c:a libmp3lame -b:a 128k "${file%.wav}.mp3"
  ffmpeg -i "$file" -c:a libopus -b:a 96k "${file%.wav}.opus"
done
```

**Claude Code Prompt:**
```
Create src/systems/audioManager.js with:
- Web Audio API implementation
- Load and cache audio files
- Play, pause, stop controls
- Volume control and muting
- Support for multiple simultaneous sounds
- Music crossfading (2 second fade)
- Mobile compatibility (unlock audio on first touch)
```

### Step 29: Handle Missing Assets

```bash
# Create placeholder generator script
```

**Claude Code Prompt:**
```
Create tools/generate-placeholders.js that:
- Scans manifest.json for required assets
- Checks if assets exist
- Generates colored placeholder PNGs for missing sprites (using canvas)
- Creates silent audio files for missing sounds
- Logs what placeholders were created
- Run with node tools/generate-placeholders.js
```

---

## 8. Version Control

### Step 30: Git Workflow Strategy

```bash
# View current status
git status

# Create feature branch
git checkout -b feature/player-movement

# View branches
git branch

# Make changes, then stage
git add src/systems/player.js

# Commit with descriptive message
git commit -m "feat: add double jump and wall slide to player"
```

### Step 31: Commit Message Convention

Use conventional commits for clarity:

```bash
# Feature
git commit -m "feat: add enemy AI with pathfinding"

# Bug fix
git commit -m "fix: resolve collision detection false positives"

# Documentation
git commit -m "docs: add setup instructions to README"

# Refactor
git commit -m "refactor: extract rendering logic to separate module"

# Performance
git commit -m "perf: implement object pooling for particles"

# Test
git commit -m "test: add unit tests for collision system"
```

### Step 32: Review Changes Before Commit

```bash
# See what changed
git diff

# See staged changes
git diff --cached

# See file status
git status

# View commit history
git log --oneline --graph --all
```

### Step 33: Stashing Work in Progress

```bash
# Save current work without committing
git stash save "WIP: working on enemy spawning"

# View stashes
git stash list

# Apply most recent stash
git stash pop

# Apply specific stash
git stash apply stash@{0}

# Clear all stashes
git stash clear
```

### Step 34: Branching Strategy

```bash
# Main branch: stable, deployable code
# Develop branch: integration branch
# Feature branches: individual features

# Create develop branch
git checkout -b develop

# Create feature branch from develop
git checkout develop
git checkout -b feature/multiplayer

# Work on feature...
git add .
git commit -m "feat: add WebSocket multiplayer support"

# Merge feature back to develop
git checkout develop
git merge feature/multiplayer

# Delete feature branch
git branch -d feature/multiplayer
```

### Step 35: Remote Repository Setup

```bash
# Create repository on GitHub (through website)

# Add remote
git remote add origin https://github.com/yourusername/my-platformer-game.git

# Push to remote
git push -u origin main

# Push all branches
git push --all

# View remotes
git remote -v
```

### Step 36: Pull and Sync

```bash
# Fetch remote changes
git fetch origin

# Pull and merge
git pull origin main

# Pull with rebase
git pull --rebase origin main

# Push changes
git push origin main
```

### Step 37: Tagging Releases

```bash
# Create version tag
git tag -a v1.0.0 -m "First release"

# List tags
git tag

# Push tags to remote
git push origin --tags

# Checkout specific version
git checkout v1.0.0
```

---

## 9. Build & Optimization

### Step 38: Production Build

```bash
# Create production build
npm run build

# Check build output
ls -lh dist/

# Analyze bundle size
du -sh dist/*
```

### Step 39: Bundle Analysis

```bash
# Install bundle analyzer
npm install --save-dev rollup-plugin-visualizer

# Add to vite.config.js
```

**Claude Code Prompt:**
```
Modify vite.config.js to:
- Add rollup-plugin-visualizer for bundle analysis
- Configure build optimization (minification, tree-shaking)
- Set up code splitting for large dependencies
- Generate stats.html in dist folder after build
```

```bash
# Build and analyze
npm run build

# Open bundle visualization
open dist/stats.html
```

### Step 40: Optimize JavaScript

**Claude Code Prompt:**
```
Review src/main.js and all game systems for optimization:
- Remove console.log statements (except errors)
- Remove debug code
- Minimize object creation in game loop
- Use object pooling for frequently created objects
- Replace Array methods in hot paths with for loops
- Suggest performance improvements
```

### Step 41: Code Splitting

```bash
# Configure dynamic imports for large systems
```

**Claude Code Prompt:**
```
Refactor src/main.js to use dynamic imports for:
- Level data (only load current level)
- Audio system (lazy load on first use)
- Enemy AI (load when enemies spawn)
- Menu system (load on demand)
Show before and after code
```

### Step 42: Minification and Compression

```bash
# Production build includes minification by default with Vite
npm run build

# Check minified size
ls -lh dist/assets/*.js

# Set up gzip compression (for server)
```

**Claude Code Prompt:**
```
Create tools/compress-build.js that:
- Compresses all files in dist/ with gzip
- Creates .gz versions alongside originals
- Reports compression ratios
- Use Node.js zlib module
```

```bash
# Compress build
node tools/compress-build.js
```

### Step 43: Asset Optimization Pipeline

```bash
# Create comprehensive optimization script
```

**Claude Code Prompt:**
```
Create tools/optimize-all.js that orchestrates:
1. Image optimization (imagemin)
2. Audio compression (maintain quality)
3. JSON minification
4. Remove unused assets (check manifest vs. actual usage)
5. Generate sprite atlases from individual sprites
6. Create responsive image sizes
7. Report total size savings
```

### Step 44: Performance Testing

```bash
# Install Lighthouse CI
npm install --save-dev @lhci/cli

# Create Lighthouse config
cat > lighthouserc.json << 'EOF'
{
  "ci": {
    "collect": {
      "staticDistDir": "./dist",
      "url": ["http://localhost:3000/"]
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["warn", {"minScore": 0.8}]
      }
    }
  }
}
EOF

# Run Lighthouse
npx lhci autorun
```

### Step 45: Memory Leak Detection

**Claude Code Prompt:**
```
Create src/utils/memoryMonitor.js that:
- Tracks memory usage over time using performance.memory
- Detects memory leaks (continuously growing memory)
- Logs warning if memory grows beyond threshold
- Export startMonitoring() and getReport() functions
- Include in debug mode only
```

---

## 10. Deployment

### Step 46: Choose Deployment Platform

**GitHub Pages (Free, Simple):**

```bash
# Install gh-pages
npm install --save-dev gh-pages

# Add deploy script to package.json
npm pkg set scripts.deploy="gh-pages -d dist"

# Build and deploy
npm run build
npm run deploy
```

**Netlify (Free, Advanced):**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize site
netlify init

# Deploy
netlify deploy --prod
```

**Vercel (Free, Fast):**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

### Step 47: Environment Configuration

```bash
# Create .env file for different environments
cat > .env.production << 'EOF'
VITE_API_URL=https://api.mygame.com
VITE_ANALYTICS_ID=UA-XXXXXXXXX-X
VITE_ENVIRONMENT=production
EOF

cat > .env.development << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_ANALYTICS_ID=
VITE_ENVIRONMENT=development
EOF

# Add .env* to .gitignore
echo ".env*" >> .gitignore
```

### Step 48: Set Up CI/CD Pipeline

**GitHub Actions:**

```bash
# Create GitHub Actions workflow
mkdir -p .github/workflows

cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy Game

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Run tests
      run: npm test

    - name: Build
      run: npm run build

    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./dist
EOF

# Commit and push
git add .github/workflows/deploy.yml
git commit -m "ci: add GitHub Actions deployment workflow"
git push origin main
```

### Step 49: Add Analytics

**Claude Code Prompt:**
```
Create src/utils/analytics.js that:
- Initializes Google Analytics (or custom analytics)
- Tracks game events: game_start, game_over, level_complete
- Tracks player progression
- Tracks errors and crashes
- Works only in production (check environment)
- Respects user privacy (check for consent)
- Export trackEvent() and trackError() functions
```

### Step 50: Error Tracking

```bash
# Install Sentry for error tracking
npm install @sentry/browser

# Create Sentry initialization
```

**Claude Code Prompt:**
```
Create src/utils/errorTracking.js that:
- Initializes Sentry with DSN from environment variable
- Captures unhandled errors and Promise rejections
- Adds game context to error reports (level, player state)
- Only activates in production
- Export initErrorTracking() function
```

### Step 51: Pre-deployment Checklist

Create automated checklist:

```bash
# Create pre-deploy script
cat > tools/pre-deploy-check.js << 'EOF'
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🚀 Pre-deployment Checklist\n');

const checks = [
  {
    name: 'All tests pass',
    command: 'npm test',
    required: true
  },
  {
    name: 'No console.log statements in production code',
    check: () => {
      // Scan for console.log in src
      const srcFiles = fs.readdirSync('./src', {recursive: true});
      // ... implementation
      return true;
    }
  },
  {
    name: 'Bundle size under 5MB',
    check: () => {
      // Check dist folder size
      return true;
    }
  },
  {
    name: 'All assets optimized',
    check: () => true
  },
  {
    name: 'Environment variables set',
    check: () => fs.existsSync('.env.production')
  }
];

// Run checks...
console.log('✅ All checks passed! Ready to deploy.');
EOF

chmod +x tools/pre-deploy-check.js

# Run pre-deploy check
./tools/pre-deploy-check.js
```

### Step 52: Deploy to Production

```bash
# Final build
npm run build

# Run pre-deploy checks
./tools/pre-deploy-check.js

# Deploy (choose your platform)
npm run deploy          # GitHub Pages
# OR
netlify deploy --prod   # Netlify
# OR
vercel --prod          # Vercel

# Tag release
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0
```

### Step 53: Post-Deployment Verification

```bash
# Check deployed site
curl -I https://yourgame.com

# Test load time
curl -w "@curl-format.txt" -o /dev/null -s https://yourgame.com

# Create curl-format.txt
cat > curl-format.txt << 'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
      time_redirect:  %{time_redirect}\n
   time_pretransfer:  %{time_pretransfer}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
EOF
```

### Step 54: Monitoring and Maintenance

```bash
# Set up uptime monitoring
# Use services like UptimeRobot, Pingdom, or StatusCake

# Create health check endpoint
```

**Claude Code Prompt:**
```
Create public/health.json that returns:
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "<current timestamp>"
}
This file should be served statically for health checks.
```

### Step 55: Rollback Plan

```bash
# If deployment fails, rollback to previous version

# GitHub Pages
git revert HEAD
git push origin main

# Netlify
netlify rollback

# Vercel
vercel rollback

# Or redeploy previous tagged version
git checkout v0.9.0
npm run build
npm run deploy
git checkout main
```

---

## Quick Reference Commands

### Daily Development Workflow

```bash
# Morning startup
cd ~/game-development/projects/my-platformer-game
git pull origin main
npm install  # If dependencies changed
npm run dev

# During development
git status
git add .
git commit -m "feat: add new feature"
npm test

# End of day
git push origin main
```

### Common Claude Code Prompts

```bash
# Generate new system
"Create src/systems/[name].js with [requirements]"

# Refactor code
"Refactor src/systems/[name].js to improve [aspect]"

# Add feature
"Add [feature] to src/systems/[name].js"

# Fix bug
"Fix bug in src/systems/[name].js where [description]"

# Optimize
"Optimize src/systems/[name].js for performance"

# Add tests
"Create tests/[name].test.js with tests for [requirements]"
```

### Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Game development aliases
alias gamedev='cd ~/game-development/projects'
alias gameserve='npm run dev'
alias gamebuild='npm run build'
alias gametest='npm test'
alias gamedeploy='npm run build && npm run deploy'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline --graph --all'

# Reload shell
source ~/.bashrc  # or ~/.zshrc
```

### Keyboard Shortcuts in Terminal

```bash
# Navigation
Ctrl+A    # Move to beginning of line
Ctrl+E    # Move to end of line
Ctrl+U    # Clear line before cursor
Ctrl+K    # Clear line after cursor
Ctrl+L    # Clear screen
Ctrl+R    # Search command history

# Process control
Ctrl+C    # Cancel current command
Ctrl+Z    # Suspend current process
fg        # Resume suspended process
```

---

## Advanced Workflows

### Multi-Project Management

```bash
# Create workspace switcher script
cat > ~/game-development/switch.sh << 'EOF'
#!/bin/bash

echo "Select project:"
select project in projects/*/; do
  if [ -n "$project" ]; then
    cd "$project"
    echo "Switched to: $project"
    echo "Running: npm run dev"
    npm run dev
    break
  fi
done
EOF

chmod +x ~/game-development/switch.sh

# Use it
cd ~/game-development
./switch.sh
```

### Automated Backup

```bash
# Create backup script
cat > ~/game-development/backup.sh << 'EOF'
#!/bin/bash

DATE=$(date +%Y%m%d)
BACKUP_DIR=~/game-development-backups
PROJECT_DIR=~/game-development/projects

mkdir -p $BACKUP_DIR

for project in $PROJECT_DIR/*/; do
  project_name=$(basename "$project")
  tar -czf "$BACKUP_DIR/${project_name}_${DATE}.tar.gz" "$project"
  echo "Backed up: $project_name"
done

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x ~/game-development/backup.sh

# Run manually or add to crontab
# crontab -e
# Add: 0 2 * * * ~/game-development/backup.sh
```

### Performance Monitoring Script

```bash
# Monitor build performance over time
cat > tools/build-stats.js << 'EOF'
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const startTime = Date.now();
execSync('npm run build', { stdio: 'inherit' });
const buildTime = Date.now() - startTime;

const distSize = execSync('du -sb dist').toString().split('\t')[0];

const stats = {
  timestamp: new Date().toISOString(),
  buildTimeMs: buildTime,
  distSizeBytes: parseInt(distSize),
  nodeVersion: process.version
};

// Append to log file
const logFile = 'build-stats.json';
let logs = [];
if (fs.existsSync(logFile)) {
  logs = JSON.parse(fs.readFileSync(logFile, 'utf8'));
}
logs.push(stats);
fs.writeFileSync(logFile, JSON.stringify(logs, null, 2));

console.log(`Build completed in ${buildTime}ms, size: ${(distSize/1024/1024).toFixed(2)}MB`);
EOF
```

---

## Troubleshooting

### Common Issues and Solutions

**Issue: Port already in use**
```bash
# Find process using port 3000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different port
npm run dev -- --port 3001
```

**Issue: Node modules corrupted**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

**Issue: Build fails**
```bash
# Clear cache
rm -rf dist/ .cache/

# Rebuild
npm run build
```

**Issue: Git merge conflicts**
```bash
# See conflicts
git status

# Edit conflicted files
# Look for <<<<<<< markers

# After resolving
git add .
git commit -m "fix: resolve merge conflicts"
```

**Issue: Can't access Claude Code**
```bash
# Check Claude Code status
claude status

# Re-authenticate
claude auth login

# Check version
claude --version
```

---

## Conclusion

This guide covered the complete terminal workflow for game development with Claude Code, from initial setup to deployment. Key takeaways:

1. **Structure matters**: Organized projects are easier to manage
2. **Automate repetitive tasks**: Scripts save time
3. **Use version control religiously**: Git is your safety net
4. **Test continuously**: Catch bugs early
5. **Deploy often**: Iterate based on feedback

### Next Steps

- Customize this workflow to your preferences
- Create your own automation scripts
- Build your first complete game
- Share your creations with the community

### Resources

- Claude Code Documentation: https://docs.claude.com/claude-code
- This Repository: Game development examples and docs
- Git Documentation: https://git-scm.com/doc
- npm Documentation: https://docs.npmjs.com

Happy game development from the terminal!
