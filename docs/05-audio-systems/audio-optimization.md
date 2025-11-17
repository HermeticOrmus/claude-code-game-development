# Audio Optimization

## Overview

Audio optimization is critical for web games. While modern devices handle audio processing well, inefficient audio systems can quickly consume memory, degrade performance, and create poor user experiences - especially on mobile devices. The goal is to deliver high-quality audio that loads quickly, uses minimal memory, and maintains smooth 60 FPS gameplay.

This guide covers advanced optimization techniques: preloading strategies, audio sprite sheets for reducing HTTP requests, memory management for large audio libraries, mobile-specific optimizations, and performance profiling. These techniques are essential for production-ready games that work well across all devices and network conditions.

## Preloading Strategies

Efficient audio loading balances memory usage with responsive playback. Different sounds require different loading strategies.

### Smart Audio Loader with Prioritization

```javascript
class SmartAudioLoader {
  constructor(audioContext) {
    this.context = audioContext;
    this.buffers = new Map();
    this.loading = new Map();
    this.loadQueue = [];
    this.isLoading = false;
    this.maxConcurrentLoads = 3;
    this.activeLoads = 0;
  }

  /**
   * Define audio loading priorities
   */
  async load(audioDefinitions) {
    /*
     * audioDefinitions format:
     * [
     *   { name: 'jump', url: '/sfx/jump.ogg', priority: 10, preload: true },
     *   { name: 'bgm', url: '/music/bgm.ogg', priority: 5, streaming: true },
     *   { name: 'ambient', url: '/sfx/ambient.ogg', priority: 1, preload: false }
     * ]
     *
     * Priority: 10 = critical (load immediately), 1 = low (lazy load)
     * Preload: true = load before game starts, false = load on demand
     * Streaming: true = use MediaElement (doesn't decode), false = use AudioBuffer
     */

    // Separate into preload and lazy-load
    const preloadSounds = audioDefinitions
      .filter(def => def.preload)
      .sort((a, b) => b.priority - a.priority); // Highest priority first

    const lazyLoadSounds = audioDefinitions.filter(def => !def.preload);

    // Load preload sounds with concurrency limit
    await this.loadBatch(preloadSounds);

    // Register lazy-load sounds for on-demand loading
    for (const def of lazyLoadSounds) {
      this.loadQueue.push(def);
    }

    console.log(`Preloaded ${preloadSounds.length} sounds, ${lazyLoadSounds.length} available for lazy loading`);
  }

  /**
   * Load batch with concurrency control
   */
  async loadBatch(definitions) {
    const promises = definitions.map(def => this.loadSingle(def));
    return Promise.all(promises);
  }

  /**
   * Load single audio file
   */
  async loadSingle(definition) {
    const { name, url, streaming = false } = definition;

    // Check cache
    if (this.buffers.has(name)) {
      return this.buffers.get(name);
    }

    // Check if already loading
    if (this.loading.has(name)) {
      return this.loading.get(name);
    }

    // Wait for available load slot
    while (this.activeLoads >= this.maxConcurrentLoads) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    this.activeLoads++;

    const loadPromise = (async () => {
      try {
        if (streaming) {
          // Use MediaElement for streaming (large files, background music)
          const audio = new Audio();
          audio.src = url;
          audio.preload = 'auto';

          await new Promise((resolve, reject) => {
            audio.addEventListener('canplaythrough', resolve, { once: true });
            audio.addEventListener('error', reject, { once: true });
            audio.load();
          });

          const source = this.context.createMediaElementSource(audio);
          const result = { type: 'streaming', audio, source };

          this.buffers.set(name, result);
          return result;

        } else {
          // Load and decode full buffer (small files, sound effects)
          const response = await fetch(url);
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${url}`);
          }

          const arrayBuffer = await response.arrayBuffer();
          const audioBuffer = await this.context.decodeAudioData(arrayBuffer);

          const result = { type: 'buffer', buffer: audioBuffer };
          this.buffers.set(name, result);

          console.log(`Loaded: ${name} (${(arrayBuffer.byteLength / 1024).toFixed(1)}KB, ${audioBuffer.duration.toFixed(2)}s)`);
          return result;
        }

      } catch (error) {
        console.error(`Failed to load ${name}:`, error);
        throw error;
      } finally {
        this.activeLoads--;
        this.loading.delete(name);
      }
    })();

    this.loading.set(name, loadPromise);
    return loadPromise;
  }

  /**
   * Lazy load on-demand audio
   */
  async lazyLoad(name) {
    // Check if already loaded
    if (this.buffers.has(name)) {
      return this.buffers.get(name);
    }

    // Find in lazy queue
    const definition = this.loadQueue.find(def => def.name === name);
    if (!definition) {
      console.warn(`Unknown audio: ${name}`);
      return null;
    }

    // Load it
    return this.loadSingle(definition);
  }

  /**
   * Get loaded audio
   */
  get(name) {
    return this.buffers.get(name);
  }

  /**
   * Unload audio to free memory
   */
  unload(name) {
    const audio = this.buffers.get(name);
    if (audio && audio.type === 'streaming' && audio.audio) {
      audio.audio.src = '';
      audio.audio.load();
    }
    this.buffers.delete(name);
    console.log(`Unloaded: ${name}`);
  }

  /**
   * Get memory usage estimate
   */
  getMemoryUsage() {
    let totalBytes = 0;
    let bufferCount = 0;
    let streamCount = 0;

    for (const [name, audio] of this.buffers) {
      if (audio.type === 'buffer') {
        const buffer = audio.buffer;
        const bytes = buffer.length * buffer.numberOfChannels * 4; // 32-bit floats
        totalBytes += bytes;
        bufferCount++;
      } else {
        streamCount++;
      }
    }

    return {
      totalMB: (totalBytes / 1024 / 1024).toFixed(2),
      totalBytes,
      bufferCount,
      streamCount
    };
  }
}
```

**Claude Code Prompt:**
```
Create a smart audio loader that supports prioritized preloading, lazy loading,
concurrent load limiting, and both streaming (MediaElement) and buffered
(AudioBuffer) playback. Include memory usage tracking and cache management.
```

## Audio Sprite Sheets

Audio sprites combine multiple sounds into a single file, dramatically reducing HTTP requests and improving load times.

### Audio Sprite System

```javascript
class AudioSpriteSheet {
  constructor(audioContext) {
    this.context = audioContext;
    this.sprites = new Map();
  }

  /**
   * Load sprite sheet with timing metadata
   */
  async loadSpriteSheet(name, url, spriteData) {
    /*
     * spriteData format:
     * {
     *   'jump': { start: 0, duration: 0.5 },
     *   'coin': { start: 0.5, duration: 0.3 },
     *   'hit': { start: 0.8, duration: 0.4 },
     *   'powerup': { start: 1.2, duration: 0.6 }
     * }
     */

    // Load audio file
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await this.context.decodeAudioData(arrayBuffer);

    // Store sprite sheet
    this.sprites.set(name, {
      buffer: audioBuffer,
      sprites: spriteData
    });

    console.log(`Sprite sheet loaded: ${name} (${Object.keys(spriteData).length} sprites, ${audioBuffer.duration.toFixed(2)}s)`);
    return audioBuffer;
  }

  /**
   * Play sprite from sheet
   */
  playSprite(sheetName, spriteName, gainNode, options = {}) {
    const sheet = this.sprites.get(sheetName);
    if (!sheet) {
      console.warn(`Sprite sheet not found: ${sheetName}`);
      return null;
    }

    const sprite = sheet.sprites[spriteName];
    if (!sprite) {
      console.warn(`Sprite not found: ${spriteName} in ${sheetName}`);
      return null;
    }

    const {
      volume = 1,
      playbackRate = 1,
      loop = false
    } = options;

    const now = this.context.currentTime;

    // Create source
    const source = this.context.createBufferSource();
    source.buffer = sheet.buffer;
    source.playbackRate.value = playbackRate;

    // Create gain
    const spriteGain = this.context.createGain();
    spriteGain.gain.setValueAtTime(volume, now);

    // Connect
    source.connect(spriteGain);
    spriteGain.connect(gainNode);

    // Play sprite section
    if (loop) {
      source.loop = true;
      source.loopStart = sprite.start;
      source.loopEnd = sprite.start + sprite.duration;
      source.start(now, sprite.start);
    } else {
      source.start(now, sprite.start, sprite.duration);
    }

    return {
      source,
      gain: spriteGain,
      stop: () => {
        try {
          source.stop();
          source.disconnect();
          spriteGain.disconnect();
        } catch (e) {
          // Already stopped
        }
      }
    };
  }

  /**
   * Get sprite metadata
   */
  getSpriteInfo(sheetName, spriteName) {
    const sheet = this.sprites.get(sheetName);
    return sheet ? sheet.sprites[spriteName] : null;
  }

  /**
   * Generate sprite sheet from multiple audio files (build tool)
   */
  static async generateSpriteSheet(audioFiles, outputPath) {
    /*
     * This would typically run in a Node.js build process
     * audioFiles: [{ name: 'jump', path: './jump.ogg' }, ...]
     *
     * Steps:
     * 1. Load all audio files
     * 2. Concatenate into single buffer
     * 3. Generate metadata JSON with timings
     * 4. Export combined audio and metadata
     */

    console.log('Sprite sheet generation requires Node.js build tool');
    console.log('Example metadata output:');

    let currentTime = 0;
    const metadata = {};

    for (const file of audioFiles) {
      metadata[file.name] = {
        start: currentTime,
        duration: file.estimatedDuration || 0.5
      };
      currentTime += metadata[file.name].duration;
    }

    return {
      metadata,
      totalDuration: currentTime
    };
  }
}

// Example usage
const spriteSheet = new AudioSpriteSheet(audioContext);

// Load sprite sheet
await spriteSheet.loadSpriteSheet('sfx', '/audio/sfx-sprite.ogg', {
  'jump': { start: 0, duration: 0.453 },
  'coin': { start: 0.453, duration: 0.321 },
  'hit': { start: 0.774, duration: 0.412 },
  'powerup': { start: 1.186, duration: 0.623 },
  'explosion': { start: 1.809, duration: 0.891 }
});

// Play sprite
spriteSheet.playSprite('sfx', 'jump', masterGain, { volume: 0.8 });
```

**Claude Code Prompt:**
```
Create an audio sprite sheet system that loads a single audio file containing
multiple sounds and plays specific segments based on timing metadata. Support
looping individual sprites, volume control, and playback rate adjustment.
Reduces HTTP requests by combining sounds.
```

## Memory Management

Efficient memory management prevents crashes and ensures smooth performance across extended play sessions.

### Audio Memory Manager

```javascript
class AudioMemoryManager {
  constructor(loader, maxMemoryMB = 50) {
    this.loader = loader;
    this.maxMemoryBytes = maxMemoryMB * 1024 * 1024;
    this.accessTimes = new Map();
    this.retainList = new Set(); // Never unload these
  }

  /**
   * Mark audio as essential (never unload)
   */
  retain(audioName) {
    this.retainList.add(audioName);
  }

  /**
   * Remove retention
   */
  release(audioName) {
    this.retainList.delete(audioName);
  }

  /**
   * Track audio access
   */
  markAccessed(audioName) {
    this.accessTimes.set(audioName, Date.now());
  }

  /**
   * Check memory usage and unload if needed
   */
  checkMemory() {
    const usage = this.loader.getMemoryUsage();

    if (usage.totalBytes > this.maxMemoryBytes) {
      console.warn(`Audio memory usage high: ${usage.totalMB}MB / ${(this.maxMemoryBytes / 1024 / 1024).toFixed(2)}MB`);
      this.evictLRU();
    }
  }

  /**
   * Evict least recently used audio
   */
  evictLRU() {
    // Get all loaded buffers
    const loadedBuffers = Array.from(this.loader.buffers.keys())
      .filter(name => {
        const audio = this.loader.get(name);
        return audio && audio.type === 'buffer'; // Only evict buffers, not streaming
      })
      .filter(name => !this.retainList.has(name)); // Don't evict retained

    if (loadedBuffers.length === 0) {
      console.warn('No audio available for eviction');
      return;
    }

    // Sort by access time (oldest first)
    loadedBuffers.sort((a, b) => {
      const timeA = this.accessTimes.get(a) || 0;
      const timeB = this.accessTimes.get(b) || 0;
      return timeA - timeB;
    });

    // Evict oldest
    const toEvict = loadedBuffers[0];
    console.log(`Evicting audio: ${toEvict}`);
    this.loader.unload(toEvict);
    this.accessTimes.delete(toEvict);

    // Check again if still over limit
    const usage = this.loader.getMemoryUsage();
    if (usage.totalBytes > this.maxMemoryBytes && loadedBuffers.length > 1) {
      this.evictLRU(); // Recursively evict more
    }
  }

  /**
   * Preload audio for upcoming level/area
   */
  async preloadGroup(groupName, audioList) {
    console.log(`Preloading audio group: ${groupName}`);

    for (const audioName of audioList) {
      await this.loader.lazyLoad(audioName);
      this.markAccessed(audioName);
    }

    this.checkMemory();
  }

  /**
   * Unload audio group when leaving area
   */
  unloadGroup(audioList) {
    for (const audioName of audioList) {
      if (!this.retainList.has(audioName)) {
        this.loader.unload(audioName);
        this.accessTimes.delete(audioName);
      }
    }
  }

  /**
   * Get memory statistics
   */
  getStats() {
    const usage = this.loader.getMemoryUsage();
    return {
      ...usage,
      maxMB: (this.maxMemoryBytes / 1024 / 1024).toFixed(2),
      percentUsed: ((usage.totalBytes / this.maxMemoryBytes) * 100).toFixed(1),
      retained: this.retainList.size
    };
  }
}

// Usage example
const memoryManager = new AudioMemoryManager(smartLoader, 30); // 30MB limit

// Retain critical sounds
memoryManager.retain('jump');
memoryManager.retain('ui_click');

// Preload level 1 audio
await memoryManager.preloadGroup('level1', [
  'level1_music',
  'enemy1_sound',
  'enemy2_sound',
  'boss1_sound'
]);

// When leaving level 1
memoryManager.unloadGroup([
  'level1_music',
  'enemy1_sound',
  'enemy2_sound',
  'boss1_sound'
]);

// Monitor memory
console.log(memoryManager.getStats());
```

**Claude Code Prompt:**
```
Create an audio memory manager that tracks memory usage, implements LRU
eviction when memory limits are exceeded, supports grouping audio by
level/area, and marks essential sounds as never-evict. Include memory
statistics and monitoring.
```

## Mobile Audio Considerations

Mobile devices have unique constraints and behaviors that require special handling.

### Mobile Audio Optimizer

```javascript
class MobileAudioOptimizer {
  constructor(audioSystem) {
    this.audioSystem = audioSystem;
    this.isMobile = this.detectMobile();
    this.isLowEndDevice = this.detectLowEndDevice();
    this.userInteracted = false;
    this.unlockAttempted = false;
  }

  /**
   * Detect mobile device
   */
  detectMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    );
  }

  /**
   * Detect low-end device
   */
  detectLowEndDevice() {
    // Check available memory (if supported)
    if (navigator.deviceMemory && navigator.deviceMemory < 4) {
      return true;
    }

    // Check hardware concurrency
    if (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4) {
      return true;
    }

    return false;
  }

  /**
   * Get optimized settings for current device
   */
  getOptimizedSettings() {
    if (this.isLowEndDevice) {
      return {
        maxConcurrentSounds: 8,
        poolSize: 12,
        maxMemoryMB: 15,
        useSpriteSheets: true,
        audioQuality: 'medium',
        enableSpatialAudio: false
      };
    } else if (this.isMobile) {
      return {
        maxConcurrentSounds: 16,
        poolSize: 20,
        maxMemoryMB: 30,
        useSpriteSheets: true,
        audioQuality: 'high',
        enableSpatialAudio: true
      };
    } else {
      return {
        maxConcurrentSounds: 32,
        poolSize: 40,
        maxMemoryMB: 50,
        useSpriteSheets: false,
        audioQuality: 'high',
        enableSpatialAudio: true
      };
    }
  }

  /**
   * Unlock audio on mobile (requires user interaction)
   */
  async unlockAudio() {
    if (this.unlockAttempted || !this.isMobile) return;

    this.unlockAttempted = true;

    try {
      const context = this.audioSystem.audioManager.context;

      // Resume suspended context
      if (context.state === 'suspended') {
        await context.resume();
      }

      // Play silent sound to unlock
      const buffer = context.createBuffer(1, 1, 22050);
      const source = context.createBufferSource();
      source.buffer = buffer;
      source.connect(context.destination);
      source.start(0);

      console.log('Mobile audio unlocked');
      this.userInteracted = true;

    } catch (error) {
      console.error('Failed to unlock audio:', error);
    }
  }

  /**
   * Setup auto-unlock on first interaction
   */
  setupAutoUnlock() {
    if (!this.isMobile) return;

    const unlock = async () => {
      await this.unlockAudio();

      // Remove listeners after first interaction
      document.removeEventListener('touchstart', unlock);
      document.removeEventListener('touchend', unlock);
      document.removeEventListener('click', unlock);
    };

    document.addEventListener('touchstart', unlock, { once: true });
    document.addEventListener('touchend', unlock, { once: true });
    document.addEventListener('click', unlock, { once: true });
  }

  /**
   * Optimize audio for mobile performance
   */
  applyMobileOptimizations() {
    if (!this.isMobile) return;

    const settings = this.getOptimizedSettings();

    // Reduce audio quality on low-end devices
    if (this.isLowEndDevice) {
      console.log('Applying low-end device optimizations');

      // Use lower sample rate
      // Note: Can't change sample rate after context creation,
      // but can use lower quality source files

      // Reduce concurrent sounds
      if (this.audioSystem.sfxPool) {
        this.audioSystem.sfxPool.maxConcurrent = settings.maxConcurrentSounds;
      }

      // Disable expensive effects
      // (implementation depends on your audio system)
    }

    console.log('Mobile optimizations applied:', settings);
  }

  /**
   * Handle page visibility changes (pause/resume audio)
   */
  setupVisibilityHandling() {
    document.addEventListener('visibilitychange', () => {
      const context = this.audioSystem.audioManager.context;

      if (document.hidden) {
        // Page hidden - suspend audio context to save battery
        if (context.state === 'running') {
          context.suspend();
          console.log('Audio suspended (page hidden)');
        }
      } else {
        // Page visible - resume audio context
        if (context.state === 'suspended' && this.userInteracted) {
          context.resume();
          console.log('Audio resumed (page visible)');
        }
      }
    });
  }

  /**
   * Monitor performance metrics
   */
  monitorPerformance() {
    if (!this.isMobile) return;

    setInterval(() => {
      const context = this.audioSystem.audioManager.context;

      // Log performance metrics
      console.log('Audio Performance:', {
        state: context.state,
        currentTime: context.currentTime.toFixed(2),
        baseLatency: context.baseLatency,
        activeSounds: this.audioSystem.sfxPool?.getActiveSoundCount() || 0
      });

    }, 10000); // Every 10 seconds
  }
}

// Usage
const mobileOptimizer = new MobileAudioOptimizer(gameAudioSystem);

// Apply optimizations
mobileOptimizer.setupAutoUnlock();
mobileOptimizer.applyMobileOptimizations();
mobileOptimizer.setupVisibilityHandling();

if (mobileOptimizer.isMobile) {
  console.log('Mobile device detected');
  console.log('Optimized settings:', mobileOptimizer.getOptimizedSettings());
}
```

**Claude Code Prompt:**
```
Create a mobile audio optimizer that detects device capabilities, applies
appropriate performance settings, handles audio unlock requirements, manages
page visibility changes for battery saving, and monitors performance. Support
both low-end and high-end mobile devices.
```

## Performance Benchmarking

Measuring audio performance helps identify bottlenecks and validate optimizations.

### Audio Performance Profiler

```javascript
class AudioPerformanceProfiler {
  constructor(audioSystem) {
    this.audioSystem = audioSystem;
    this.metrics = {
      loadTimes: [],
      playLatencies: [],
      memorySnapshots: [],
      concurrentSounds: []
    };
    this.monitoring = false;
  }

  /**
   * Measure audio load time
   */
  async profileLoad(name, loadFunction) {
    const startTime = performance.now();

    try {
      const result = await loadFunction();
      const endTime = performance.now();
      const duration = endTime - startTime;

      this.metrics.loadTimes.push({
        name,
        duration,
        timestamp: Date.now()
      });

      console.log(`Load time for ${name}: ${duration.toFixed(2)}ms`);
      return result;

    } catch (error) {
      console.error(`Load failed for ${name}:`, error);
      throw error;
    }
  }

  /**
   * Measure playback latency
   */
  measurePlayLatency(soundName) {
    const startTime = performance.now();

    const handle = this.audioSystem.sfxPool.play(soundName);

    const endTime = performance.now();
    const latency = endTime - startTime;

    this.metrics.playLatencies.push({
      soundName,
      latency,
      timestamp: Date.now()
    });

    if (latency > 50) {
      console.warn(`High play latency for ${soundName}: ${latency.toFixed(2)}ms`);
    }

    return handle;
  }

  /**
   * Start continuous monitoring
   */
  startMonitoring(interval = 1000) {
    if (this.monitoring) return;

    this.monitoring = true;

    this.monitorInterval = setInterval(() => {
      // Snapshot memory usage
      const memoryUsage = this.audioSystem.loader?.getMemoryUsage();
      if (memoryUsage) {
        this.metrics.memorySnapshots.push({
          ...memoryUsage,
          timestamp: Date.now()
        });
      }

      // Snapshot concurrent sounds
      const concurrent = this.audioSystem.sfxPool?.getActiveSoundCount() || 0;
      this.metrics.concurrentSounds.push({
        count: concurrent,
        timestamp: Date.now()
      });

    }, interval);

    console.log('Audio performance monitoring started');
  }

  /**
   * Stop monitoring
   */
  stopMonitoring() {
    if (!this.monitoring) return;

    clearInterval(this.monitorInterval);
    this.monitoring = false;
    console.log('Audio performance monitoring stopped');
  }

  /**
   * Generate performance report
   */
  generateReport() {
    const report = {
      loadTimes: this.analyzeLoadTimes(),
      playLatencies: this.analyzePlayLatencies(),
      memoryUsage: this.analyzeMemoryUsage(),
      concurrency: this.analyzeConcurrency()
    };

    console.log('=== Audio Performance Report ===');
    console.log('Load Times:', report.loadTimes);
    console.log('Play Latencies:', report.playLatencies);
    console.log('Memory Usage:', report.memoryUsage);
    console.log('Concurrency:', report.concurrency);

    return report;
  }

  analyzeLoadTimes() {
    if (this.metrics.loadTimes.length === 0) {
      return { message: 'No load time data' };
    }

    const times = this.metrics.loadTimes.map(m => m.duration);
    return {
      count: times.length,
      average: (times.reduce((a, b) => a + b, 0) / times.length).toFixed(2) + 'ms',
      min: Math.min(...times).toFixed(2) + 'ms',
      max: Math.max(...times).toFixed(2) + 'ms'
    };
  }

  analyzePlayLatencies() {
    if (this.metrics.playLatencies.length === 0) {
      return { message: 'No latency data' };
    }

    const latencies = this.metrics.playLatencies.map(m => m.latency);
    const highLatency = latencies.filter(l => l > 50).length;

    return {
      count: latencies.length,
      average: (latencies.reduce((a, b) => a + b, 0) / latencies.length).toFixed(2) + 'ms',
      min: Math.min(...latencies).toFixed(2) + 'ms',
      max: Math.max(...latencies).toFixed(2) + 'ms',
      highLatencyCount: highLatency,
      highLatencyPercent: ((highLatency / latencies.length) * 100).toFixed(1) + '%'
    };
  }

  analyzeMemoryUsage() {
    if (this.metrics.memorySnapshots.length === 0) {
      return { message: 'No memory data' };
    }

    const latest = this.metrics.memorySnapshots[this.metrics.memorySnapshots.length - 1];
    const memoryValues = this.metrics.memorySnapshots.map(m => parseFloat(m.totalMB));

    return {
      current: latest.totalMB + 'MB',
      average: (memoryValues.reduce((a, b) => a + b, 0) / memoryValues.length).toFixed(2) + 'MB',
      peak: Math.max(...memoryValues).toFixed(2) + 'MB',
      bufferCount: latest.bufferCount,
      streamCount: latest.streamCount
    };
  }

  analyzeConcurrency() {
    if (this.metrics.concurrentSounds.length === 0) {
      return { message: 'No concurrency data' };
    }

    const counts = this.metrics.concurrentSounds.map(m => m.count);

    return {
      current: counts[counts.length - 1],
      average: (counts.reduce((a, b) => a + b, 0) / counts.length).toFixed(1),
      peak: Math.max(...counts)
    };
  }

  /**
   * Export metrics as JSON
   */
  exportMetrics() {
    return JSON.stringify(this.metrics, null, 2);
  }

  /**
   * Clear all metrics
   */
  clear() {
    this.metrics = {
      loadTimes: [],
      playLatencies: [],
      memorySnapshots: [],
      concurrentSounds: []
    };
    console.log('Performance metrics cleared');
  }
}

// Usage
const profiler = new AudioPerformanceProfiler(gameAudioSystem);

// Profile loading
await profiler.profileLoad('jump', () =>
  gameAudioSystem.loader.loadSingle({
    name: 'jump',
    url: '/sfx/jump.ogg'
  })
);

// Measure play latency
profiler.measurePlayLatency('jump');

// Start continuous monitoring
profiler.startMonitoring(2000); // Every 2 seconds

// Later: generate report
setTimeout(() => {
  profiler.stopMonitoring();
  const report = profiler.generateReport();
}, 60000); // After 1 minute
```

**Claude Code Prompt:**
```
Create an audio performance profiler that measures load times, play latencies,
memory usage over time, and concurrent sound counts. Generate performance
reports with statistics and identify performance issues. Support continuous
monitoring and metric export.
```

## Best Practices

1. **Preload critical sounds** - UI feedback, player actions
2. **Stream long audio** - Background music, ambient loops
3. **Use audio sprites** - Reduce HTTP requests for small sounds
4. **Implement LRU caching** - Unload unused audio automatically
5. **Limit concurrent sounds** - Especially on mobile devices
6. **Compress appropriately** - OGG Vorbis ~96-128kbps for most sounds
7. **Profile performance** - Measure don't guess
8. **Test on real devices** - Emulators don't reveal real performance
9. **Monitor memory** - Audio can quickly consume available memory
10. **Optimize for mobile first** - Mobile constraints often work well on desktop

## Performance Targets

- **Load time**: < 100ms for small SFX, < 500ms for music
- **Play latency**: < 50ms (< 20ms ideal for responsive feedback)
- **Memory usage**: < 30MB on mobile, < 50MB on desktop
- **Concurrent sounds**: < 16 on mobile, < 32 on desktop
- **Audio format**: OGG Vorbis 96-128kbps for SFX, 128-192kbps for music

## Cross-References

- [Web Audio API](./web-audio-api.md) - Core audio concepts
- [Sound Effects](./sound-effects.md) - SFX pooling and management
- [Music Systems](./music-systems.md) - Music streaming strategies
- [Performance Optimization](../10-performance-optimization/README.md) - General optimization

## Summary

Audio optimization is essential for production-ready web games. Master these techniques:

- Smart preloading with prioritization
- Audio sprite sheets for reduced requests
- LRU memory management
- Mobile-specific optimizations
- Performance profiling and monitoring
- Device capability detection

These optimizations ensure your game delivers high-quality audio experiences across all devices and network conditions, from low-end mobile phones to high-end desktop computers. Claude Code helps implement sophisticated optimization systems efficiently, ensuring your game sounds great everywhere.
