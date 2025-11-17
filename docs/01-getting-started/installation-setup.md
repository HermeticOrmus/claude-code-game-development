# Installation and Setup Guide

Complete installation instructions for Claude Code and your game development environment. This guide covers all major platforms and includes troubleshooting for common installation issues.

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installing Claude Code](#installing-claude-code)
  - [Web-Based Access](#web-based-access)
  - [CLI Installation](#cli-installation)
  - [API Access](#api-access)
- [Platform-Specific Setup](#platform-specific-setup)
  - [Windows Setup](#windows-setup)
  - [macOS Setup](#macos-setup)
  - [Linux Setup](#linux-setup)
- [Development Environment Configuration](#development-environment-configuration)
  - [Code Editors](#code-editors)
  - [Browser Setup](#browser-setup)
  - [Local Development Server](#local-development-server)
- [Verifying Your Installation](#verifying-your-installation)
- [Optional Tools and Extensions](#optional-tools-and-extensions)
- [Troubleshooting Installation Issues](#troubleshooting-installation-issues)
- [Next Steps](#next-steps)

---

## Overview

Setting up your environment for Claude Code game development involves three main components:

1. **Claude Code Access** - The AI assistant that generates and helps you build game code
2. **Development Environment** - Code editor, browser, and local server for testing
3. **Game Development Tools** - Optional but recommended tools for asset creation and debugging

This guide walks you through each component with platform-specific instructions.

**Estimated Setup Time**: 30-60 minutes for complete installation and configuration

---

## System Requirements

### Minimum Requirements

**Operating System**
- Windows 10 (64-bit) or later
- macOS 10.14 (Mojave) or later
- Linux: Ubuntu 18.04+, Fedora 32+, or equivalent

**Hardware**
- 4GB RAM (8GB recommended for comfortable development)
- 2GB free disk space
- Dual-core processor (quad-core recommended)
- Internet connection (required for Claude Code)

**Browser** (any modern browser)
- Chrome 90+ (recommended for best developer tools)
- Firefox 88+
- Safari 14+ (macOS only)
- Edge 90+

### Recommended Specifications

For the best development experience:
- 8GB+ RAM
- SSD storage
- Modern multi-core processor
- Dedicated GPU (for 3D game development)
- High-speed internet connection

**Note**: All example games in this repository are designed to run on minimum specifications. More powerful hardware enables faster development and testing of complex games.

---

## Installing Claude Code

Claude Code is available in multiple formats. Choose the access method that best fits your workflow.

### Web-Based Access

The simplest way to start using Claude Code for game development.

**Step 1: Create an Account**

1. Visit [https://claude.ai](https://claude.ai)
2. Click "Sign Up" or "Get Started"
3. Create account with email or Google/OAuth
4. Verify your email address
5. Choose a plan (Free tier is sufficient for learning)

**Step 2: Access the Web Interface**

1. Log in to [https://claude.ai](https://claude.ai)
2. You'll see the chat interface
3. Start a new conversation
4. You're ready to use Claude Code!

**Step 3: Configure for Game Development**

Start your conversation with this system prompt to optimize for game development:

```
I'm learning game development with JavaScript and HTML5 Canvas.
I want you to help me build games by generating code, explaining
concepts, and helping me debug issues. Please:

1. Provide complete, working code examples
2. Include detailed comments explaining how the code works
3. Follow modern JavaScript best practices (ES6+)
4. Optimize for readability and learning
5. Point out potential issues or improvements

Let's start building games!
```

**Advantages of Web Access**:
- No installation required
- Works on any device with a browser
- Always up-to-date
- Easy to share conversations

**Limitations**:
- Requires internet connection
- Manual copy/paste of code to your editor
- Cannot directly edit your local files

### CLI Installation

For developers who prefer command-line workflows, Claude Code offers a CLI tool.

**Installation Steps**:

```bash
# Install Node.js (if not already installed)
# Download from https://nodejs.org (LTS version recommended)

# Verify Node.js installation
node --version  # Should show v16+ or later
npm --version   # Should show v8+ or later

# Install Claude Code CLI globally
npm install -g @anthropic-ai/claude-code-cli

# Verify installation
claude --version
```

**Configuration**:

```bash
# Set up your API key
claude auth login

# Follow the prompts to authenticate with your Claude account
# This will open a browser window for authentication
```

**Basic Usage**:

```bash
# Start an interactive session
claude chat

# Generate code from a file prompt
claude generate --prompt "Create a Pong game" --output pong.js

# Get help with a code file
claude explain game.js
```

**Advantages of CLI**:
- Integrate with development scripts
- Automate repetitive tasks
- Work offline after initial setup (limited features)
- Direct file manipulation

### API Access

For advanced users building custom tools or integrations.

**Setup**:

1. Get API key from [https://console.anthropic.com](https://console.anthropic.com)
2. Install the Anthropic SDK:

```bash
npm install @anthropic-ai/sdk
```

**Example: Generate Game Code via API**:

```javascript
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

async function generateGameCode(prompt) {
  const message = await anthropic.messages.create({
    model: "claude-3-5-sonnet-20241022",
    max_tokens: 4096,
    messages: [{
      role: "user",
      content: prompt
    }]
  });

  return message.content[0].text;
}

// Usage
const gameCode = await generateGameCode(
  "Create a simple Pong game using HTML5 Canvas with player and AI paddle"
);

console.log(gameCode);
```

**Use Cases**:
- Custom development tools
- Automated game generation pipelines
- Integration with build systems
- Batch code generation

---

## Platform-Specific Setup

### Windows Setup

**Step 1: Install a Code Editor**

**Option A: Visual Studio Code (Recommended)**

1. Download from [https://code.visualstudio.com](https://code.visualstudio.com)
2. Run the installer (VSCodeUserSetup-x64-x.xx.x.exe)
3. Check "Add to PATH" during installation
4. Launch VS Code

**Option B: Other Editors**
- Sublime Text: [https://www.sublimetext.com](https://www.sublimetext.com)
- Atom: [https://atom.io](https://atom.io)
- Notepad++: [https://notepad-plus-plus.org](https://notepad-plus-plus.org)

**Step 2: Install Node.js**

1. Download Windows installer from [https://nodejs.org](https://nodejs.org)
2. Choose LTS (Long Term Support) version
3. Run installer, accept defaults
4. Verify installation:

```cmd
# Open Command Prompt (Win+R, type "cmd")
node --version
npm --version
```

**Step 3: Install Git (Optional)**

1. Download from [https://git-scm.com](https://git-scm.com)
2. Run installer, use recommended defaults
3. Verify:

```cmd
git --version
```

**Step 4: Set Up Local Development Server**

```cmd
# Install http-server globally
npm install -g http-server

# Verify installation
http-server --version
```

**Step 5: Configure Windows for Web Development**

```cmd
# Create a workspace directory
mkdir C:\GameDev
cd C:\GameDev

# Clone this repository (if using Git)
git clone https://github.com/yourusername/claude-code-game-development.git

# Or download and extract the ZIP from GitHub
```

**Windows-Specific Tips**:
- Use PowerShell instead of Command Prompt for better terminal experience
- Install Windows Terminal from Microsoft Store for modern terminal features
- Configure Windows Defender to exclude your GameDev folder for better performance
- Use forward slashes (/) in file paths for cross-platform compatibility

### macOS Setup

**Step 1: Install Xcode Command Line Tools**

```bash
# Open Terminal (Cmd+Space, type "Terminal")
xcode-select --install

# Click "Install" in the dialog that appears
# Wait for installation to complete
```

**Step 2: Install Homebrew (Package Manager)**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Follow the on-screen instructions
# Add Homebrew to your PATH as instructed

# Verify installation
brew --version
```

**Step 3: Install Node.js**

```bash
# Install via Homebrew
brew install node

# Verify installation
node --version
npm --version
```

**Step 4: Install a Code Editor**

**Option A: Visual Studio Code**
```bash
brew install --cask visual-studio-code

# Or download from https://code.visualstudio.com
```

**Option B: Other Options**
```bash
# Sublime Text
brew install --cask sublime-text

# Atom
brew install --cask atom
```

**Step 5: Install Git**

```bash
# Git is included with Xcode Command Line Tools
git --version

# Or install latest version via Homebrew
brew install git
```

**Step 6: Set Up Development Server**

```bash
# Install http-server
npm install -g http-server

# Verify
http-server --version
```

**Step 7: Create Workspace**

```bash
# Create development directory
mkdir ~/GameDev
cd ~/GameDev

# Clone repository
git clone https://github.com/yourusername/claude-code-game-development.git
```

**macOS-Specific Tips**:
- Use Spotlight (Cmd+Space) to quickly open Terminal and applications
- Safari has excellent WebGL support but Chrome has better DevTools
- Use `pbcopy` and `pbpaste` for clipboard operations in Terminal
- Consider iTerm2 as an alternative to the default Terminal app

### Linux Setup

Instructions for Ubuntu/Debian-based distributions. Adjust package manager commands for other distributions.

**Step 1: Update System**

```bash
# Update package list
sudo apt update
sudo apt upgrade -y
```

**Step 2: Install Node.js**

```bash
# Install Node.js 18.x LTS via NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version
```

**Step 3: Install Code Editor**

**Option A: Visual Studio Code**
```bash
# Download and install .deb package
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update
sudo apt install code

# Or use snap
sudo snap install code --classic
```

**Option B: Other Editors**
```bash
# Sublime Text
sudo snap install sublime-text --classic

# Atom
sudo snap install atom --classic

# Vim/Neovim (for terminal enthusiasts)
sudo apt install neovim
```

**Step 4: Install Git**

```bash
sudo apt install git

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Step 5: Install Development Server**

```bash
# Install http-server globally
sudo npm install -g http-server

# Verify
http-server --version
```

**Step 6: Set Up Workspace**

```bash
# Create development directory
mkdir ~/GameDev
cd ~/GameDev

# Clone repository
git clone https://github.com/yourusername/claude-code-game-development.git
```

**Linux-Specific Tips**:
- Firefox is often pre-installed and works great for game development
- Chrome/Chromium can be installed via `sudo apt install chromium-browser`
- Use `xclip` for clipboard operations: `sudo apt install xclip`
- Consider Tilix or Terminator for advanced terminal features

---

## Development Environment Configuration

### Code Editors

**Visual Studio Code - Recommended Extensions**

Install these extensions for optimal game development:

```
# Open VS Code
# Press Ctrl+Shift+X (Cmd+Shift+X on Mac) to open Extensions

# Search and install:
1. "Live Server" - Auto-refresh browser on code changes
2. "JavaScript (ES6) code snippets" - Faster coding
3. "ESLint" - Code quality checking
4. "Prettier" - Code formatting
5. "GitLens" - Enhanced Git integration (if using Git)
6. "Path Intellisense" - File path autocomplete
```

**VS Code Settings for Game Development**:

Create `.vscode/settings.json` in your project:

```json
{
  "editor.formatOnSave": true,
  "editor.tabSize": 2,
  "editor.detectIndentation": false,
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "liveServer.settings.port": 5500,
  "liveServer.settings.donotShowInfoMsg": true
}
```

### Browser Setup

**Chrome DevTools Configuration** (Recommended for Development)

1. **Enable Developer Tools**:
   - Windows/Linux: F12 or Ctrl+Shift+I
   - macOS: Cmd+Option+I

2. **Useful Panels for Game Development**:
   - **Console**: Debug output, errors, and logging
   - **Sources**: Set breakpoints, step through code
   - **Performance**: Profile game performance
   - **Network**: Monitor asset loading

3. **Performance Settings**:
   ```javascript
   // Add to your game code for performance monitoring
   performance.mark('game-start');

   // ... game loop code ...

   performance.mark('game-end');
   performance.measure('game-loop', 'game-start', 'game-end');
   console.log(performance.getEntriesByName('game-loop'));
   ```

4. **Disable Cache During Development**:
   - Open DevTools
   - Go to Network tab
   - Check "Disable cache"
   - Keep DevTools open while developing

**Firefox Developer Edition** (Alternative)

Download from [https://www.mozilla.org/firefox/developer/](https://www.mozilla.org/firefox/developer/)

Excellent tools for:
- Canvas debugging
- WebGL inspection
- Responsive design testing

### Local Development Server

**Why You Need a Local Server**

Browsers restrict certain features when opening HTML files directly (`file://`):
- Canvas toDataURL() for screenshots
- Loading external JSON files
- Web Workers
- Some modern JavaScript modules

**Setting Up http-server**

Already installed if you followed platform setup. Usage:

```bash
# Navigate to your game directory
cd ~/GameDev/my-game

# Start server
http-server

# Server starts on http://localhost:8080
# Open this URL in your browser
```

**Options and Customization**:

```bash
# Specify port
http-server -p 3000

# Enable CORS (for loading external resources)
http-server --cors

# Open browser automatically
http-server -o

# Common combination
http-server -p 3000 -o --cors
```

**Alternative: VS Code Live Server**

If you installed the Live Server extension:

1. Open your HTML file in VS Code
2. Right-click in the editor
3. Select "Open with Live Server"
4. Browser opens automatically with auto-refresh on save

**Alternative: Python Simple Server**

If you have Python installed:

```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

---

## Verifying Your Installation

Test that everything works with this simple example.

**Step 1: Create Test Game**

Create a new file `test-game.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Installation Test Game</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: #1a1a2e;
      font-family: Arial, sans-serif;
    }
    #gameCanvas {
      border: 2px solid #00ff88;
      box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
    }
  </style>
</head>
<body>
  <canvas id="gameCanvas" width="400" height="400"></canvas>

  <script>
    // Get canvas and context
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    // Ball properties
    let ball = {
      x: canvas.width / 2,
      y: canvas.height / 2,
      radius: 15,
      dx: 3,
      dy: 2,
      color: '#00ff88'
    };

    // Draw ball
    function drawBall() {
      ctx.beginPath();
      ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
      ctx.fillStyle = ball.color;
      ctx.fill();
      ctx.closePath();
    }

    // Update ball position
    function update() {
      ball.x += ball.dx;
      ball.y += ball.dy;

      // Bounce off walls
      if (ball.x + ball.radius > canvas.width || ball.x - ball.radius < 0) {
        ball.dx = -ball.dx;
      }
      if (ball.y + ball.radius > canvas.height || ball.y - ball.radius < 0) {
        ball.dy = -ball.dy;
      }
    }

    // Game loop
    function gameLoop() {
      // Clear canvas
      ctx.fillStyle = 'rgba(26, 26, 46, 0.2)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Update and draw
      update();
      drawBall();

      // Continue loop
      requestAnimationFrame(gameLoop);
    }

    // Start game
    console.log('Installation test game started successfully!');
    console.log('If you see a bouncing ball, everything is working correctly.');
    gameLoop();
  </script>
</body>
</html>
```

**Step 2: Run Test Game**

```bash
# Start server in the directory containing test-game.html
http-server

# Open http://localhost:8080/test-game.html in browser
```

**Expected Result**:
- A green ball bouncing around a canvas
- No errors in browser console
- Smooth animation at 60 FPS

**If it works**: Your environment is correctly configured!

**Step 3: Test Claude Code Integration**

Open Claude Code (web interface or CLI) and try this prompt:

```
Modify the test game to add a second ball with a different color that
bounces independently. Make it red and slightly smaller.
```

Copy the generated code, update your test-game.html, and verify the changes work.

**If this works**: You're ready to start building games!

---

## Optional Tools and Extensions

### Asset Creation Tools

**Graphics**:
- **GIMP** (Free): [https://www.gimp.org](https://www.gimp.org)
- **Aseprite** (Paid, $20): Pixel art editor - [https://www.aseprite.org](https://www.aseprite.org)
- **Piskel** (Free, Web): Pixel art - [https://www.piskelapp.com](https://www.piskelapp.com)

**Audio**:
- **Audacity** (Free): Audio editing - [https://www.audacityteam.org](https://www.audacityteam.org)
- **LMMS** (Free): Music creation - [https://lmms.io](https://lmms.io)
- **Bfxr** (Free, Web): Sound effects - [https://www.bfxr.net](https://www.bfxr.net)

### Browser Extensions

- **Web Developer** - Testing tools
- **JSONView** - Format JSON files
- **VisBug** - Visual debugging

---

## Troubleshooting Installation Issues

### Claude Code Issues

**Problem**: Cannot access Claude.ai
- **Solution**: Check internet connection, try different browser, clear cache

**Problem**: API key not working
- **Solution**: Regenerate key at console.anthropic.com, verify environment variable

**Problem**: Rate limit errors
- **Solution**: Wait and retry, consider upgrading to paid tier for higher limits

### Node.js/npm Issues

**Problem**: `node: command not found`
- **Solution**: Restart terminal, verify PATH, reinstall Node.js

**Problem**: Permission errors during `npm install -g`
- **Solution Linux/Mac**: Use `sudo` or configure npm for global installs without sudo:
  ```bash
  mkdir ~/.npm-global
  npm config set prefix '~/.npm-global'
  echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
  source ~/.bashrc
  ```

### Browser Issues

**Problem**: Canvas not displaying
- **Solution**: Check browser console for errors, verify JavaScript is enabled

**Problem**: Performance issues
- **Solution**: Close other tabs, disable extensions, update graphics drivers

**Problem**: CORS errors
- **Solution**: Use local development server instead of `file://` protocol

### General Debugging

Enable verbose logging:

```bash
# For Node.js issues
npm config set loglevel verbose

# For http-server issues
http-server -v

# Browser DevTools console
# Check for red error messages
```

---

## Next Steps

Your development environment is now fully configured! Next:

1. **Build Your First Game**: Continue to [first-game-in-10-minutes.md](first-game-in-10-minutes.md)
2. **Understand the Tool**: Read [claude-code-fundamentals.md](claude-code-fundamentals.md)
3. **Improve Prompts**: Study [prompt-engineering-for-games.md](prompt-engineering-for-games.md)

---

## Official Resources

- **Claude Documentation**: [https://docs.anthropic.com](https://docs.anthropic.com)
- **Claude API Reference**: [https://docs.anthropic.com/api](https://docs.anthropic.com/api)
- **MDN Web Docs**: [https://developer.mozilla.org](https://developer.mozilla.org)
- **Canvas API Reference**: [https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)

**You're ready to build games with Claude Code!**
