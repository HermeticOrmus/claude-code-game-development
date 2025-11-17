# Mobile Packaging

Mobile devices represent the largest gaming platform in the world, with billions of potential players. This guide shows you how to transform web-based games into mobile experiences, from Progressive Web Apps (PWAs) to native app store submissions.

## Mobile Deployment Options

### Progressive Web Apps (PWAs)
**Best for**: Quick deployment, instant updates, cross-platform reach

**Pros**:
- No app store approval needed
- Instant updates
- Smaller download sizes
- Single codebase for all platforms
- Installable on home screen
- Offline support

**Cons**:
- Limited access to native APIs
- No app store discovery
- Some iOS limitations

### Cordova/Capacitor
**Best for**: Web games that need native features or app store distribution

**Pros**:
- Full app store distribution
- Access to native APIs
- One codebase for iOS and Android
- Plugin ecosystem

**Cons**:
- App store approval process
- Larger app sizes
- Platform-specific quirks

## Progressive Web App (PWA) Complete Setup

PWAs are installable web apps that work offline and feel native. They're the fastest path to mobile deployment.

### 1. Web App Manifest

Create `public/manifest.json`:

```json
{
  "name": "My Awesome Game",
  "short_name": "AwesomeGame",
  "description": "An incredible puzzle platformer adventure",
  "start_url": "/",
  "display": "fullscreen",
  "background_color": "#000000",
  "theme_color": "#4A90E2",
  "orientation": "landscape-primary",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshots/gameplay-1.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide"
    },
    {
      "src": "/screenshots/gameplay-2.png",
      "sizes": "750x1334",
      "type": "image/png",
      "form_factor": "narrow"
    }
  ],
  "categories": ["games", "entertainment"],
  "shortcuts": [
    {
      "name": "New Game",
      "short_name": "New",
      "description": "Start a new game",
      "url": "/?action=new-game",
      "icons": [{ "src": "/icons/new-game.png", "sizes": "96x96" }]
    },
    {
      "name": "Continue",
      "short_name": "Continue",
      "description": "Continue last game",
      "url": "/?action=continue",
      "icons": [{ "src": "/icons/continue.png", "sizes": "96x96" }]
    }
  ]
}
```

**Link manifest in HTML**:
```html
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#4A90E2">

<!-- iOS specific -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="AwesomeGame">
<link rel="apple-touch-icon" href="/icons/icon-192x192.png">
```

### 2. Service Worker for Offline Play

Service workers enable offline functionality and fast loading.

**Create `public/sw.js`**:

```javascript
const CACHE_NAME = 'game-cache-v1';
const RUNTIME_CACHE = 'game-runtime-v1';

// Files to cache immediately
const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/styles.css',
  '/game.js',
  '/assets/sprites.png',
  '/assets/tileset.png',
  '/manifest.json',
];

// Install service worker and cache assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Caching app shell');
      return cache.addAll(PRECACHE_URLS);
    })
  );
  self.skipWaiting();
});

// Activate and clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// Fetch strategy: Cache first, network fallback
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests
  if (url.origin !== location.origin) return;

  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return caches.open(RUNTIME_CACHE).then((cache) => {
        return fetch(request).then((response) => {
          // Cache successful responses
          if (response.status === 200) {
            cache.put(request, response.clone());
          }
          return response;
        });
      });
    })
  );
});

// Background sync for scores (when connection returns)
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-scores') {
    event.waitUntil(syncScores());
  }
});

async function syncScores() {
  const db = await openScoreDB();
  const pendingScores = await db.getAll('pending-scores');

  for (const score of pendingScores) {
    try {
      await fetch('/api/scores', {
        method: 'POST',
        body: JSON.stringify(score),
        headers: { 'Content-Type': 'application/json' },
      });
      await db.delete('pending-scores', score.id);
    } catch (error) {
      console.error('Failed to sync score:', error);
    }
  }
}
```

**Register service worker in your app**:

```javascript
// main.js
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((registration) => {
        console.log('Service Worker registered:', registration);

        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;

          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New version available
              showUpdateNotification();
            }
          });
        });
      })
      .catch((error) => {
        console.error('Service Worker registration failed:', error);
      });
  });
}

function showUpdateNotification() {
  const notification = document.createElement('div');
  notification.className = 'update-notification';
  notification.innerHTML = `
    <p>New version available!</p>
    <button onclick="location.reload()">Update</button>
  `;
  document.body.appendChild(notification);
}
```

### 3. Install Prompt

Encourage users to install your PWA:

```javascript
// installPrompt.js
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent automatic prompt
  e.preventDefault();
  deferredPrompt = e;

  // Show custom install button
  showInstallButton();
});

function showInstallButton() {
  const installBtn = document.createElement('button');
  installBtn.textContent = 'Install Game';
  installBtn.className = 'install-button';
  installBtn.onclick = async () => {
    if (!deferredPrompt) return;

    // Show install prompt
    deferredPrompt.prompt();

    // Wait for user choice
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`User ${outcome} the install prompt`);

    deferredPrompt = null;
    installBtn.remove();
  };

  document.body.appendChild(installBtn);
}

// Track installation
window.addEventListener('appinstalled', (e) => {
  console.log('PWA installed');

  // Track with analytics
  if (window.gtag) {
    gtag('event', 'pwa_installed');
  }
});
```

## iOS and Android Considerations

### iOS Specific Optimizations

```html
<!-- Disable auto-zoom on input focus -->
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">

<!-- Splash screens for different devices -->
<link rel="apple-touch-startup-image" href="/splash/iphone5.png" media="(device-width: 320px) and (device-height: 568px)">
<link rel="apple-touch-startup-image" href="/splash/iphone6.png" media="(device-width: 375px) and (device-height: 667px)">
<link rel="apple-touch-startup-image" href="/splash/iphonex.png" media="(device-width: 375px) and (device-height: 812px)">
<link rel="apple-touch-startup-image" href="/splash/ipad.png" media="(device-width: 768px) and (device-height: 1024px)">
```

**Handle iOS safe areas**:
```css
/* Respect notch on iPhone X+ */
body {
  padding: env(safe-area-inset-top) env(safe-area-inset-right)
           env(safe-area-inset-bottom) env(safe-area-inset-left);
}

/* Fullscreen game canvas */
canvas {
  width: 100vw;
  height: 100vh;
  display: block;
}
```

### Android Specific Optimizations

```html
<!-- Theme color for Android status bar -->
<meta name="theme-color" content="#4A90E2">

<!-- Android Chrome custom install prompt -->
<meta name="mobile-web-app-capable" content="yes">
```

## Capacitor for Modern Mobile Deployment

Capacitor is the modern alternative to Cordova, built by the Ionic team.

### Capacitor Setup

```bash
# Install Capacitor
npm install @capacitor/core @capacitor/cli

# Initialize Capacitor
npx cap init

# Add platforms
npx cap add ios
npx cap add android
```

**Configure `capacitor.config.json`**:

```json
{
  "appId": "com.yourdomain.awesomegame",
  "appName": "Awesome Game",
  "webDir": "dist",
  "bundledWebRuntime": false,
  "server": {
    "androidScheme": "https"
  },
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 2000,
      "backgroundColor": "#000000",
      "showSpinner": false,
      "androidSpinnerStyle": "large",
      "iosSpinnerStyle": "small"
    }
  }
}
```

### Build and Sync

```bash
# Build web assets
npm run build

# Sync to native projects
npx cap sync

# Open in native IDEs
npx cap open ios
npx cap open android
```

### Using Native APIs

**Access device features**:

```javascript
// Install plugins
npm install @capacitor/haptics @capacitor/storage @capacitor/share

import { Haptics, ImpactStyle } from '@capacitor/haptics';
import { Storage } from '@capacitor/storage';
import { Share } from '@capacitor/share';

// Haptic feedback on collision
async function onCollision() {
  await Haptics.impact({ style: ImpactStyle.Heavy });
}

// Persistent storage
async function saveGameState(state) {
  await Storage.set({
    key: 'game-state',
    value: JSON.stringify(state),
  });
}

async function loadGameState() {
  const { value } = await Storage.get({ key: 'game-state' });
  return value ? JSON.parse(value) : null;
}

// Share scores
async function shareScore(score) {
  await Share.share({
    title: 'Check out my score!',
    text: `I scored ${score} points in Awesome Game!`,
    url: 'https://awesomegame.com',
    dialogTitle: 'Share your score',
  });
}
```

## Performance Optimization for Mobile

### Touch Input Handling

```javascript
// Optimize touch performance
canvas.addEventListener('touchstart', handleTouchStart, { passive: false });
canvas.addEventListener('touchmove', handleTouchMove, { passive: false });
canvas.addEventListener('touchend', handleTouchEnd, { passive: false });

function handleTouchStart(e) {
  e.preventDefault(); // Prevent scrolling

  const touch = e.touches[0];
  const rect = canvas.getBoundingClientRect();

  const x = (touch.clientX - rect.left) * (canvas.width / rect.width);
  const y = (touch.clientY - rect.top) * (canvas.height / rect.height);

  game.handleInput({ type: 'start', x, y });
}

function handleTouchMove(e) {
  e.preventDefault();

  const touch = e.touches[0];
  const rect = canvas.getBoundingClientRect();

  const x = (touch.clientX - rect.left) * (canvas.width / rect.width);
  const y = (touch.clientY - rect.top) * (canvas.height / rect.height);

  game.handleInput({ type: 'move', x, y });
}

function handleTouchEnd(e) {
  e.preventDefault();
  game.handleInput({ type: 'end' });
}
```

### Virtual Joystick

```javascript
// virtualJoystick.js
export class VirtualJoystick {
  constructor(canvas) {
    this.canvas = canvas;
    this.active = false;
    this.startX = 0;
    this.startY = 0;
    this.currentX = 0;
    this.currentY = 0;
    this.maxDistance = 50;

    this.setupListeners();
  }

  setupListeners() {
    this.canvas.addEventListener('touchstart', (e) => {
      const touch = e.touches[0];
      this.startX = touch.clientX;
      this.startY = touch.clientY;
      this.currentX = touch.clientX;
      this.currentY = touch.clientY;
      this.active = true;
    });

    this.canvas.addEventListener('touchmove', (e) => {
      if (!this.active) return;

      const touch = e.touches[0];
      this.currentX = touch.clientX;
      this.currentY = touch.clientY;
    });

    this.canvas.addEventListener('touchend', () => {
      this.active = false;
    });
  }

  getDirection() {
    if (!this.active) return { x: 0, y: 0 };

    const dx = this.currentX - this.startX;
    const dy = this.currentY - this.startY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance < 10) return { x: 0, y: 0 };

    const clamped = Math.min(distance, this.maxDistance);
    const ratio = clamped / distance;

    return {
      x: (dx * ratio) / this.maxDistance,
      y: (dy * ratio) / this.maxDistance,
    };
  }

  render(ctx) {
    if (!this.active) return;

    // Draw joystick base
    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.beginPath();
    ctx.arc(this.startX, this.startY, this.maxDistance, 0, Math.PI * 2);
    ctx.fill();

    // Draw joystick stick
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.beginPath();
    ctx.arc(this.currentX, this.currentY, 20, 0, Math.PI * 2);
    ctx.fill();
  }
}
```

### Screen Orientation Management

```javascript
// Force landscape orientation
screen.orientation.lock('landscape')
  .catch((error) => {
    console.log('Orientation lock not supported');
  });

// Handle orientation changes
window.addEventListener('orientationchange', () => {
  resizeCanvas();
});

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  game.resize(canvas.width, canvas.height);
}
```

### Battery and Performance

```javascript
// Reduce framerate on low battery
if ('getBattery' in navigator) {
  navigator.getBattery().then((battery) => {
    if (battery.level < 0.2) {
      game.setFramerate(30); // Reduce from 60fps to 30fps
    }

    battery.addEventListener('levelchange', () => {
      if (battery.level < 0.2) {
        game.setFramerate(30);
      } else {
        game.setFramerate(60);
      }
    });
  });
}

// Pause game when app in background
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    game.pause();
  } else {
    game.resume();
  }
});
```

## App Store Submission

### Google Play Store

**1. Prepare app details**:
- App name, description, screenshots
- Privacy policy URL (required)
- Content rating questionnaire
- Feature graphic (1024x500)

**2. Build release APK/AAB**:

```bash
# In Android Studio:
# Build → Generate Signed Bundle/APK → Android App Bundle
# Select release keystore
# Build
```

**3. Submit to Play Console**:
- Upload AAB file
- Set pricing (free or paid)
- Select countries
- Submit for review (usually approved in 1-2 days)

### Apple App Store

**1. Prepare app details**:
- App name, subtitle, description
- Screenshots for all device sizes
- App icon (1024x1024)
- Privacy policy

**2. Build and archive**:

```bash
# In Xcode:
# Product → Archive
# Distribute App → App Store Connect
# Upload
```

**3. Submit via App Store Connect**:
- Create new app
- Upload build
- Complete all required fields
- Submit for review (typically 1-3 days)

## Complete Mobile Build Script

```javascript
// scripts/build-mobile.js
import { exec } from 'child_process';
import fs from 'fs';

async function buildMobile() {
  console.log('Building for mobile...');

  // 1. Build web version
  console.log('Building web assets...');
  await execCommand('npm run build');

  // 2. Optimize for mobile
  console.log('Optimizing for mobile...');
  await optimizeAssets();

  // 3. Sync to Capacitor
  console.log('Syncing to Capacitor...');
  await execCommand('npx cap sync');

  // 4. Build for platforms
  console.log('Building Android...');
  await execCommand('cd android && ./gradlew assembleRelease');

  console.log('Building iOS...');
  await execCommand('cd ios && xcodebuild -workspace App.xcworkspace -scheme App archive');

  console.log('Mobile build complete!');
}

async function optimizeAssets() {
  // Compress images
  await execCommand('imagemin dist/assets/*.png --out-dir=dist/assets');

  // Minify JSON
  const jsonFiles = fs.readdirSync('dist/assets')
    .filter(f => f.endsWith('.json'));

  for (const file of jsonFiles) {
    const data = JSON.parse(fs.readFileSync(`dist/assets/${file}`));
    fs.writeFileSync(`dist/assets/${file}`, JSON.stringify(data));
  }
}

function execCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(stderr);
        reject(error);
      } else {
        console.log(stdout);
        resolve();
      }
    });
  });
}

buildMobile();
```

## Claude Code Prompts for Mobile Deployment

**Generate PWA configuration**:
```
Create a complete PWA setup for this game including:
- Web app manifest with all required fields
- Service worker for offline play
- Install prompt UI
- Update notification system
- iOS and Android optimizations

Game name: [name]
Primary color: [color]
Orientation: [landscape/portrait]
```

**Generate Capacitor integration**:
```
Set up Capacitor for this web game to create native mobile apps.

Include:
- Capacitor configuration
- Plugin integration for haptics, storage, and sharing
- Build scripts for iOS and Android
- Touch input optimization
- Performance optimizations for mobile

Platform features needed: [list features]
```

## Best Practices

1. **Test on real devices** - Emulators don't show real performance
2. **Optimize for touch** - Large touch targets (44x44px minimum)
3. **Handle orientation** - Support both landscape and portrait
4. **Reduce bundle size** - Mobile users have limited data
5. **Implement offline mode** - Games should work without internet
6. **Battery conscious** - Don't drain battery unnecessarily
7. **Respect safe areas** - Notches and system UI
8. **Haptic feedback** - Enhance gameplay feel
9. **Auto-save** - Players switch apps frequently
10. **Fast loading** - Mobile users are impatient

## Next Steps

You've learned how to deploy games to mobile devices. Next, explore [Desktop Deployment](./desktop-deployment.md) to package your game for Windows, Mac, and Linux using Electron and Tauri.
