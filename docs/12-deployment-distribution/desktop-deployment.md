# Desktop Deployment

Desktop gaming remains a massive market, especially for premium and complex games. This guide shows you how to package web-based games as native desktop applications using Electron and Tauri, and distribute them through platforms like Steam and itch.io.

## Why Desktop Deployment?

**Desktop games command higher prices and reach serious gamers**:

- Better performance than web browsers
- Access to native APIs (file system, system tray, etc.)
- Traditional gaming audience willing to pay
- Offline play by default
- Professional appearance
- Platform-specific optimizations

**Real-world example**: A developer increased revenue 300% by releasing their web game on Steam for $9.99 versus free web version with ads.

## Electron for Desktop Games

Electron powers apps like VS Code, Discord, and Slack. It's the most popular way to create cross-platform desktop apps from web code.

### Electron Setup

```bash
# Install Electron
npm install --save-dev electron electron-builder

# Install development dependencies
npm install --save-dev concurrently wait-on cross-env
```

**Create `electron/main.js`**:

```javascript
const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 720,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    backgroundColor: '#000000',
    show: false, // Don't show until ready
    frame: true,
    icon: path.join(__dirname, '../build/icon.png'),
  });

  // Load game
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Custom menu
  const menu = Menu.buildFromTemplate([
    {
      label: 'Game',
      submenu: [
        { label: 'New Game', accelerator: 'CmdOrCtrl+N', click: () => {
          mainWindow.webContents.send('new-game');
        }},
        { type: 'separator' },
        { label: 'Quit', accelerator: 'CmdOrCtrl+Q', click: () => {
          app.quit();
        }},
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
  ]);

  Menu.setApplicationMenu(menu);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Handle IPC from renderer
const { ipcMain } = require('electron');

ipcMain.handle('save-game', async (event, saveData) => {
  const fs = require('fs').promises;
  const savePath = path.join(app.getPath('userData'), 'save.json');
  await fs.writeFile(savePath, JSON.stringify(saveData));
  return { success: true };
});

ipcMain.handle('load-game', async () => {
  const fs = require('fs').promises;
  const savePath = path.join(app.getPath('userData'), 'save.json');

  try {
    const data = await fs.readFile(savePath, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    return null;
  }
});
```

**Create `electron/preload.js`**:

```javascript
const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to renderer
contextBridge.exposeInMainWorld('electron', {
  saveGame: (data) => ipcRenderer.invoke('save-game', data),
  loadGame: () => ipcRenderer.invoke('load-game'),
  onNewGame: (callback) => ipcRenderer.on('new-game', callback),
});
```

**Use in game code**:

```javascript
// Game.js
async function saveGame() {
  const saveData = {
    level: currentLevel,
    score: score,
    playerPosition: { x: player.x, y: player.y },
    timestamp: Date.now(),
  };

  if (window.electron) {
    // Desktop version
    await window.electron.saveGame(saveData);
  } else {
    // Web version
    localStorage.setItem('save', JSON.stringify(saveData));
  }
}

async function loadGame() {
  let saveData;

  if (window.electron) {
    saveData = await window.electron.loadGame();
  } else {
    saveData = JSON.parse(localStorage.getItem('save'));
  }

  if (saveData) {
    currentLevel = saveData.level;
    score = saveData.score;
    player.x = saveData.playerPosition.x;
    player.y = saveData.playerPosition.y;
  }
}
```

### Building with Electron Builder

**Configure `package.json`**:

```json
{
  "name": "awesome-game",
  "version": "1.0.0",
  "main": "electron/main.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "electron:dev": "concurrently \"npm run dev\" \"wait-on http://localhost:3000 && cross-env NODE_ENV=development electron .\"",
    "electron:build": "npm run build && electron-builder"
  },
  "build": {
    "appId": "com.yourdomain.awesomegame",
    "productName": "Awesome Game",
    "directories": {
      "output": "release"
    },
    "files": [
      "dist/**/*",
      "electron/**/*",
      "package.json"
    ],
    "mac": {
      "category": "public.app-category.games",
      "target": ["dmg", "zip"],
      "icon": "build/icon.icns"
    },
    "win": {
      "target": ["nsis", "portable"],
      "icon": "build/icon.ico"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "category": "Game",
      "icon": "build/icon.png"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

**Build for all platforms**:

```bash
# Build for current platform
npm run electron:build

# Build for all platforms (requires macOS for Mac builds)
npm run electron:build -- --mac --win --linux
```

## Tauri: Lightweight Alternative

Tauri is a modern alternative to Electron that produces much smaller apps (3-5MB vs 100MB+).

### Tauri Setup

```bash
# Install Tauri CLI
npm install --save-dev @tauri-apps/cli

# Initialize Tauri
npm run tauri init
```

**Configure `src-tauri/tauri.conf.json`**:

```json
{
  "build": {
    "beforeBuildCommand": "npm run build",
    "beforeDevCommand": "npm run dev",
    "devPath": "http://localhost:3000",
    "distDir": "../dist"
  },
  "package": {
    "productName": "Awesome Game",
    "version": "1.0.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "writeFile": true,
        "readFile": true,
        "scope": ["$APPDATA/*"]
      },
      "dialog": {
        "save": true
      }
    },
    "bundle": {
      "active": true,
      "category": "Game",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ],
      "identifier": "com.yourdomain.awesomegame",
      "targets": "all"
    },
    "windows": [
      {
        "title": "Awesome Game",
        "width": 1280,
        "height": 720,
        "resizable": true,
        "fullscreen": false
      }
    ]
  }
}
```

**Build with Tauri**:

```bash
# Development
npm run tauri dev

# Production build
npm run tauri build
```

## Steam Integration

Steam is the largest PC gaming platform with 120+ million active users.

### Steamworks SDK Setup

1. **Register as Steamworks partner** (free, but requires $100 app fee)
2. **Create app** in Steamworks dashboard
3. **Download Steamworks SDK**

**Integrate Steamworks with Electron**:

```bash
npm install --save greenworks
```

**Use Steam features**:

```javascript
// steamIntegration.js
const greenworks = require('greenworks');

export class SteamIntegration {
  constructor() {
    this.initialized = false;

    try {
      if (greenworks.initAPI()) {
        this.initialized = true;
        console.log('Steam initialized:', greenworks.getSteamId().screenName);
      }
    } catch (error) {
      console.log('Steam not available');
    }
  }

  unlockAchievement(name) {
    if (!this.initialized) return;

    greenworks.activateAchievement(name, () => {
      console.log(`Achievement unlocked: ${name}`);
    }, (error) => {
      console.error('Failed to unlock achievement:', error);
    });
  }

  submitScore(leaderboard, score) {
    if (!this.initialized) return;

    greenworks.findLeaderboard(leaderboard, (handle) => {
      greenworks.uploadLeaderboardScore(handle, score, () => {
        console.log('Score submitted:', score);
      });
    });
  }

  saveToCloud(key, data) {
    if (!this.initialized) return;

    greenworks.saveTextToFile(key, JSON.stringify(data), () => {
      console.log('Saved to Steam Cloud');
    });
  }

  loadFromCloud(key) {
    if (!this.initialized) return null;

    return new Promise((resolve) => {
      greenworks.readTextFromFile(key, (data) => {
        resolve(JSON.parse(data));
      }, () => {
        resolve(null);
      });
    });
  }
}
```

### Steam Depot Upload

```bash
# Build game
npm run electron:build

# Upload to Steam using SteamCmd
steamcmd +login <username> +run_app_build <app_build_script> +quit
```

**Example `app_build.vdf`**:

```
"AppBuild"
{
  "AppID" "123456"
  "Desc" "Version 1.0.0"
  "BuildOutput" "output"
  "ContentRoot" "..\release"
  "SetLive" "default"

  "Depots"
  {
    "123457" // Windows Depot ID
    {
      "FileMapping"
      {
        "LocalPath" "*.exe"
        "DepotPath" "."
      }
    }
  }
}
```

## Itch.io Desktop Distribution

Itch.io is indie-game friendly with no approval process and flexible pricing.

### Butler (Itch.io CLI)

```bash
# Install Butler
npm install -g @itchio/butler

# Login
butler login

# Push build
butler push release/Awesome\ Game-1.0.0.dmg yourusername/awesomegame:osx
butler push release/Awesome\ Game\ Setup\ 1.0.0.exe yourusername/awesomegame:windows
butler push release/Awesome\ Game-1.0.0.AppImage yourusername/awesomegame:linux
```

**Automate with GitHub Actions**:

```yaml
name: Deploy to Itch.io

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: npm ci

    - name: Build Electron app
      run: npm run electron:build

    - name: Upload to Itch.io
      uses: josephbmanley/butler-publish-itchio-action@master
      env:
        BUTLER_CREDENTIALS: ${{ secrets.BUTLER_CREDENTIALS }}
        CHANNEL: ${{ matrix.os }}
        ITCH_GAME: awesomegame
        ITCH_USER: yourusername
        PACKAGE: release/
```

## Auto-Update System

Implement automatic updates for desktop apps:

```javascript
// main.js
const { autoUpdater } = require('electron-updater');

function setupAutoUpdater() {
  autoUpdater.checkForUpdatesAndNotify();

  autoUpdater.on('update-available', () => {
    mainWindow.webContents.send('update-available');
  });

  autoUpdater.on('update-downloaded', () => {
    mainWindow.webContents.send('update-ready');
  });

  // Check for updates every hour
  setInterval(() => {
    autoUpdater.checkForUpdates();
  }, 60 * 60 * 1000);
}

// In renderer
window.electron.onUpdateAvailable(() => {
  showNotification('Update downloading...');
});

window.electron.onUpdateReady(() => {
  if (confirm('Update ready. Restart now?')) {
    window.electron.restartAndUpdate();
  }
});
```

## Platform-Specific Features

### Windows

```javascript
// Add to system tray
const { Tray } = require('electron');

let tray = new Tray('icon.png');
tray.setContextMenu(Menu.buildFromTemplate([
  { label: 'Show Game', click: () => mainWindow.show() },
  { label: 'Quit', click: () => app.quit() },
]));
```

### macOS

```javascript
// Touch Bar support
const { TouchBar } = require('electron');
const { TouchBarButton } = TouchBar;

const touchBar = new TouchBar({
  items: [
    new TouchBarButton({
      label: 'New Game',
      click: () => mainWindow.webContents.send('new-game'),
    }),
  ],
});

mainWindow.setTouchBar(touchBar);
```

### Linux

```javascript
// Create .desktop file
const desktopEntry = `
[Desktop Entry]
Name=Awesome Game
Exec=/usr/bin/awesome-game
Icon=awesome-game
Type=Application
Categories=Game;
`;
```

## Complete Build Script

```javascript
// scripts/build-desktop.js
const builder = require('electron-builder');
const Platform = builder.Platform;

async function buildAll() {
  // Build for all platforms
  await builder.build({
    targets: Platform.MAC.createTarget(),
    config: {
      appId: 'com.yourdomain.awesomegame',
      productName: 'Awesome Game',
      // ... rest of config
    },
  });

  await builder.build({
    targets: Platform.WINDOWS.createTarget(),
  });

  await builder.build({
    targets: Platform.LINUX.createTarget(),
  });

  console.log('Desktop builds complete!');
}

buildAll().catch(console.error);
```

## Claude Code Prompts

**Generate Electron setup**:
```
Create a complete Electron setup for this web game including:
- Main process configuration
- Preload script for secure IPC
- Menu system
- Auto-updater
- File system integration for saves
- Build configuration for Windows, Mac, Linux

Game features: [list features that need native APIs]
```

**Generate Steam integration**:
```
Integrate Steamworks SDK into this Electron game.

Features needed:
- Achievements (list of achievements)
- Leaderboards (list of leaderboards)
- Steam Cloud saves
- Steam overlay support

Provide complete integration code and build configuration.
```

## Best Practices

1. **Code signing** - Sign apps for Mac and Windows to avoid security warnings
2. **Auto-updates** - Keep players on latest version
3. **Crash reporting** - Know when things break
4. **Performance** - Desktop should run better than web
5. **Native feel** - Use platform conventions
6. **Keyboard shortcuts** - Desktop users expect them
7. **Offline mode** - Works without internet
8. **Save data** - Use proper application data directories

## Next Steps

Desktop deployment opens doors to premium pricing and serious gamers. Next, explore [Monetization Strategies](./monetization-strategies.md) to learn how to generate revenue from your games across all platforms.
