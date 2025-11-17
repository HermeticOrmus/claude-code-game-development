# Analytics & Telemetry

Understanding how players interact with your game is essential for improvement. This guide covers analytics integration, player behavior tracking, and privacy-compliant data collection.

## Why Analytics Matter

**Data-driven development beats guessing**:

- Identify where players quit (drop-off points)
- Understand which features are used
- Optimize difficulty curves
- Measure engagement and retention
- Validate design decisions with data
- Find bugs through anomaly detection

**Real-world impact**: A developer increased player retention by 40% after analytics showed 60% of players quit at level 3. They reduced difficulty, and completion rates tripled.

## Google Analytics 4 for Games

### Setup

```html
<!-- Add to index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Event Tracking

```javascript
// analytics.js
export class GameAnalytics {
  constructor(measurementId) {
    this.measurementId = measurementId;
    this.sessionStart = Date.now();
    this.eventsQueue = [];
  }

  // Track game start
  trackGameStart() {
    gtag('event', 'game_start', {
      game_version: '1.0.0',
      platform: this.getPlatform(),
    });
  }

  // Track level events
  trackLevelStart(levelNumber) {
    gtag('event', 'level_start', {
      level_number: levelNumber,
      level_name: `Level ${levelNumber}`,
    });
  }

  trackLevelComplete(levelNumber, timeSpent, score) {
    gtag('event', 'level_complete', {
      level_number: levelNumber,
      time_spent: timeSpent,
      score: score,
      success: true,
    });
  }

  trackLevelFailed(levelNumber, timeSpent, attempts) {
    gtag('event', 'level_failed', {
      level_number: levelNumber,
      time_spent: timeSpent,
      attempts: attempts,
    });
  }

  // Track player actions
  trackPlayerDeath(cause, position) {
    gtag('event', 'player_death', {
      cause: cause,
      position_x: Math.floor(position.x),
      position_y: Math.floor(position.y),
      level: game.currentLevel,
    });
  }

  trackPowerupCollected(type) {
    gtag('event', 'powerup_collected', {
      powerup_type: type,
      level: game.currentLevel,
    });
  }

  trackEnemyDefeated(enemyType) {
    gtag('event', 'enemy_defeated', {
      enemy_type: enemyType,
      level: game.currentLevel,
    });
  }

  // Track engagement
  trackSessionDuration() {
    const duration = Math.floor((Date.now() - this.sessionStart) / 1000);

    gtag('event', 'session_duration', {
      value: duration,
      duration_seconds: duration,
    });
  }

  trackAchievement(achievementId) {
    gtag('event', 'unlock_achievement', {
      achievement_id: achievementId,
    });
  }

  // Track monetization
  trackAdViewed(adType) {
    gtag('event', 'ad_viewed', {
      ad_type: adType,
    });
  }

  trackPurchase(productId, value) {
    gtag('event', 'purchase', {
      transaction_id: this.generateTransactionId(),
      value: value,
      currency: 'USD',
      items: [{
        item_id: productId,
        item_name: productId,
        price: value,
      }],
    });
  }

  // Utility methods
  getPlatform() {
    if (window.cordova) return 'mobile_app';
    if (window.electron) return 'desktop_app';
    if (/Mobile/.test(navigator.userAgent)) return 'mobile_web';
    return 'desktop_web';
  }

  generateTransactionId() {
    return `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Usage in game
const analytics = new GameAnalytics('G-XXXXXXXXXX');

// On game start
analytics.trackGameStart();

// On level events
analytics.trackLevelStart(currentLevel);
analytics.trackLevelComplete(currentLevel, timeSpent, score);

// On player death
analytics.trackPlayerDeath('fell_into_pit', player.position);

// Track session on close
window.addEventListener('beforeunload', () => {
  analytics.trackSessionDuration();
});
```

## Custom Analytics System

For full control and no third-party dependencies:

```javascript
// customAnalytics.js
export class CustomAnalytics {
  constructor(endpoint) {
    this.endpoint = endpoint;
    this.sessionId = this.generateSessionId();
    this.userId = this.getUserId();
    this.events = [];
    this.batchSize = 10;
    this.flushInterval = 30000; // 30 seconds

    this.startAutoFlush();
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  getUserId() {
    let userId = localStorage.getItem('analytics_user_id');

    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('analytics_user_id', userId);
    }

    return userId;
  }

  track(eventName, properties = {}) {
    const event = {
      event: eventName,
      properties: {
        ...properties,
        timestamp: Date.now(),
        session_id: this.sessionId,
        user_id: this.userId,
        url: window.location.href,
        screen_width: window.innerWidth,
        screen_height: window.innerHeight,
      },
    };

    this.events.push(event);

    if (this.events.length >= this.batchSize) {
      this.flush();
    }
  }

  async flush() {
    if (this.events.length === 0) return;

    const eventsToSend = [...this.events];
    this.events = [];

    try {
      await fetch(this.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          events: eventsToSend,
        }),
      });
    } catch (error) {
      console.error('Failed to send analytics:', error);
      // Re-add events to queue
      this.events.unshift(...eventsToSend);
    }
  }

  startAutoFlush() {
    setInterval(() => {
      this.flush();
    }, this.flushInterval);

    // Flush on page unload
    window.addEventListener('beforeunload', () => {
      this.flush();
    });
  }
}

// Backend endpoint (Node.js example)
app.post('/api/analytics', async (req, res) => {
  const { events } = req.body;

  // Store in database
  for (const event of events) {
    await db.collection('analytics').insertOne(event);
  }

  res.json({ success: true });
});
```

## Player Behavior Heatmaps

Track where players go and where they die:

```javascript
// heatmap.js
export class HeatmapTracker {
  constructor(levelWidth, levelHeight, resolution = 20) {
    this.levelWidth = levelWidth;
    this.levelHeight = levelHeight;
    this.resolution = resolution;

    this.gridWidth = Math.ceil(levelWidth / resolution);
    this.gridHeight = Math.ceil(levelHeight / resolution);

    this.deathMap = this.createGrid();
    this.movementMap = this.createGrid();
  }

  createGrid() {
    return Array(this.gridHeight).fill(0).map(() =>
      Array(this.gridWidth).fill(0)
    );
  }

  recordDeath(x, y) {
    const gridX = Math.floor(x / this.resolution);
    const gridY = Math.floor(y / this.resolution);

    if (this.isValidPosition(gridX, gridY)) {
      this.deathMap[gridY][gridX]++;
    }
  }

  recordMovement(x, y) {
    const gridX = Math.floor(x / this.resolution);
    const gridY = Math.floor(y / this.resolution);

    if (this.isValidPosition(gridX, gridY)) {
      this.movementMap[gridY][gridX]++;
    }
  }

  isValidPosition(gridX, gridY) {
    return gridX >= 0 && gridX < this.gridWidth &&
           gridY >= 0 && gridY < this.gridHeight;
  }

  exportData() {
    return {
      deathMap: this.deathMap,
      movementMap: this.movementMap,
      levelDimensions: {
        width: this.levelWidth,
        height: this.levelHeight,
      },
      resolution: this.resolution,
    };
  }

  async sendToServer() {
    const data = this.exportData();

    await fetch('/api/heatmap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        level: game.currentLevel,
        data: data,
      }),
    });
  }
}

// Usage
const heatmap = new HeatmapTracker(800, 600);

// In game loop
if (frameCount % 60 === 0) { // Every second
  heatmap.recordMovement(player.x, player.y);
}

// On player death
heatmap.recordDeath(player.x, player.y);

// On level complete
heatmap.sendToServer();
```

## Funnel Analysis

Track player progression through your game:

```javascript
// funnelAnalytics.js
export class FunnelAnalytics {
  constructor() {
    this.funnel = {
      gameStarted: 0,
      tutorial_completed: 0,
      level1_completed: 0,
      level5_completed: 0,
      level10_completed: 0,
      game_completed: 0,
    };
  }

  trackFunnelStep(step) {
    this.funnel[step]++;
    this.sendToAnalytics(step);
  }

  getConversionRates() {
    const total = this.funnel.gameStarted;

    return {
      tutorial_completion: (this.funnel.tutorial_completed / total) * 100,
      level1_completion: (this.funnel.level1_completed / total) * 100,
      level5_completion: (this.funnel.level5_completed / total) * 100,
      level10_completion: (this.funnel.level10_completed / total) * 100,
      game_completion: (this.funnel.game_completed / total) * 100,
    };
  }

  identifyDropoffPoints() {
    const rates = this.getConversionRates();
    const dropoffs = [];

    for (let i = 0; i < Object.keys(rates).length - 1; i++) {
      const current = Object.values(rates)[i];
      const next = Object.values(rates)[i + 1];
      const drop = current - next;

      if (drop > 20) { // More than 20% drop
        dropoffs.push({
          from: Object.keys(rates)[i],
          to: Object.keys(rates)[i + 1],
          dropPercentage: drop,
        });
      }
    }

    return dropoffs;
  }

  sendToAnalytics(step) {
    gtag('event', 'funnel_step', {
      step_name: step,
      step_number: Object.keys(this.funnel).indexOf(step),
    });
  }
}
```

## A/B Testing

Test different game configurations:

```javascript
// abTesting.js
export class ABTesting {
  constructor() {
    this.variant = this.assignVariant();
    this.trackAssignment();
  }

  assignVariant() {
    let variant = localStorage.getItem('ab_variant');

    if (!variant) {
      // Assign user to variant A or B
      variant = Math.random() < 0.5 ? 'A' : 'B';
      localStorage.setItem('ab_variant', variant);
    }

    return variant;
  }

  trackAssignment() {
    gtag('event', 'ab_test_assigned', {
      variant: this.variant,
    });
  }

  getConfig(key, defaultValue) {
    const configs = {
      A: {
        difficulty: 'normal',
        startingLives: 3,
        tutorialEnabled: true,
        enemySpeed: 1.0,
      },
      B: {
        difficulty: 'easy',
        startingLives: 5,
        tutorialEnabled: true,
        enemySpeed: 0.8,
      },
    };

    const config = configs[this.variant];
    return config[key] !== undefined ? config[key] : defaultValue;
  }

  trackOutcome(metric, value) {
    gtag('event', 'ab_test_outcome', {
      variant: this.variant,
      metric: metric,
      value: value,
    });
  }
}

// Usage
const abTest = new ABTesting();

// Use variant-specific configuration
game.difficulty = abTest.getConfig('difficulty');
game.player.lives = abTest.getConfig('startingLives');

// Track outcomes
abTest.trackOutcome('level_completion_rate', completionRate);
abTest.trackOutcome('session_duration', sessionDuration);
```

## Privacy Compliance (GDPR)

Ensure compliance with data protection laws:

```javascript
// privacyManager.js
export class PrivacyManager {
  constructor() {
    this.consent = this.loadConsent();
  }

  loadConsent() {
    const saved = localStorage.getItem('privacy_consent');
    return saved ? JSON.parse(saved) : null;
  }

  async requestConsent() {
    if (this.consent) return this.consent;

    return new Promise((resolve) => {
      const modal = this.createConsentModal();

      modal.onAccept = (preferences) => {
        this.consent = {
          analytics: preferences.analytics,
          advertising: preferences.advertising,
          timestamp: Date.now(),
        };

        localStorage.setItem('privacy_consent', JSON.stringify(this.consent));
        this.applyConsent();
        resolve(this.consent);
      };
    });
  }

  applyConsent() {
    if (this.consent.analytics) {
      this.enableAnalytics();
    } else {
      this.disableAnalytics();
    }

    if (this.consent.advertising) {
      this.enableAds();
    } else {
      this.disableAds();
    }
  }

  enableAnalytics() {
    gtag('consent', 'update', {
      'analytics_storage': 'granted',
    });
  }

  disableAnalytics() {
    gtag('consent', 'update', {
      'analytics_storage': 'denied',
    });
  }

  enableAds() {
    gtag('consent', 'update', {
      'ad_storage': 'granted',
    });
  }

  disableAds() {
    gtag('consent', 'update', {
      'ad_storage': 'denied',
    });
  }

  createConsentModal() {
    // Create and return consent UI
    const modal = document.createElement('div');
    modal.className = 'privacy-consent-modal';
    modal.innerHTML = `
      <h2>Privacy Settings</h2>
      <p>We use cookies and analytics to improve your experience.</p>

      <label>
        <input type="checkbox" id="analytics-consent" checked>
        Analytics (helps us improve the game)
      </label>

      <label>
        <input type="checkbox" id="ads-consent" checked>
        Advertising (supports free gameplay)
      </label>

      <button id="accept-consent">Save Preferences</button>
    `;

    document.body.appendChild(modal);

    return {
      onAccept: null,
      element: modal,
    };
  }
}

// Usage
const privacy = new PrivacyManager();

async function initGame() {
  await privacy.requestConsent();

  // Only track if user consented
  if (privacy.consent.analytics) {
    analytics.trackGameStart();
  }
}
```

## Performance Telemetry

Track game performance metrics:

```javascript
// performanceTelemetry.js
export class PerformanceTelemetry {
  constructor() {
    this.metrics = {
      fps: [],
      frameTime: [],
      memory: [],
    };

    this.startMonitoring();
  }

  startMonitoring() {
    let lastTime = performance.now();
    let frameCount = 0;

    const monitor = () => {
      const now = performance.now();
      const delta = now - lastTime;

      frameCount++;

      // Track FPS every second
      if (delta >= 1000) {
        const fps = Math.round((frameCount * 1000) / delta);
        this.metrics.fps.push(fps);

        frameCount = 0;
        lastTime = now;

        // Track memory if available
        if (performance.memory) {
          const memoryMB = Math.round(performance.memory.usedJSHeapSize / 1048576);
          this.metrics.memory.push(memoryMB);
        }
      }

      requestAnimationFrame(monitor);
    };

    requestAnimationFrame(monitor);
  }

  getAverageFPS() {
    return this.metrics.fps.reduce((a, b) => a + b, 0) / this.metrics.fps.length;
  }

  getMinFPS() {
    return Math.min(...this.metrics.fps);
  }

  async sendReport() {
    const report = {
      avgFPS: this.getAverageFPS(),
      minFPS: this.getMinFPS(),
      avgMemory: this.metrics.memory.reduce((a, b) => a + b, 0) / this.metrics.memory.length,
      device: {
        userAgent: navigator.userAgent,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        devicePixelRatio: window.devicePixelRatio,
      },
    };

    await fetch('/api/performance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(report),
    });
  }
}
```

## Claude Code Prompts

**Generate analytics system**:
```
Create a comprehensive analytics system for this game that tracks:
- Player progression through levels
- Death locations and causes
- Session duration and retention
- Feature usage
- Performance metrics

Include:
- Google Analytics 4 integration
- Custom event tracking
- Heatmap generation
- Funnel analysis
- GDPR compliance

Game type: [describe game]
```

**Generate A/B testing framework**:
```
Create an A/B testing framework for this game to test:
- Difficulty levels
- Tutorial approaches
- UI/UX variations
- Monetization strategies

Include:
- Variant assignment
- Configuration management
- Outcome tracking
- Statistical significance calculation

Provide complete implementation and analysis tools.
```

## Best Practices

1. **Start tracking early** - Historical data is valuable
2. **Track meaningful events** - Not everything needs tracking
3. **Respect privacy** - Get consent, be transparent
4. **Use data to improve** - Analytics is worthless without action
5. **Set up alerts** - Know immediately if something breaks
6. **Sample if needed** - Don't track every frame, track strategically
7. **Test your tracking** - Ensure events fire correctly
8. **Document events** - Keep a registry of what you track

## Key Metrics to Track

**Engagement**:
- Daily Active Users (DAU)
- Monthly Active Users (MAU)
- Average session duration
- Sessions per user

**Retention**:
- Day 1 retention
- Day 7 retention
- Day 30 retention

**Progression**:
- Level completion rates
- Average playtime per level
- Drop-off points

**Monetization**:
- Conversion rate
- Average Revenue Per User (ARPU)
- Lifetime Value (LTV)

## Next Steps

You've completed the Deployment & Distribution section! Next, explore real-world [Case Studies](../13-case-studies/README.md) to see how these concepts come together in actual game development projects.
