# Music Systems

## Overview

Music is the emotional backbone of your game. While sound effects provide immediate feedback and spatial audio creates immersion, music establishes mood, builds tension, celebrates victories, and guides emotional pacing. A well-designed music system doesn't just play songs - it responds dynamically to gameplay, transitions smoothly between states, and creates a cohesive audio experience that players remember long after they stop playing.

This guide covers everything from basic background music playback to sophisticated dynamic music systems with layering, crossfading, and adaptive responses to gameplay. You'll learn production-ready techniques used in professional games, all implemented with the Web Audio API and optimized for web browsers.

## Background Music Management

The foundation of any music system is reliable background music playback with smooth transitions and proper resource management.

### Basic Music Player

```javascript
class MusicPlayer {
  constructor(audioContext, masterGain) {
    this.context = audioContext;
    this.masterGain = masterGain;
    this.currentTrack = null;
    this.musicGain = null;
    this.source = null;
    this.volume = 0.7;
    this.tracks = new Map();
  }

  /**
   * Load music track (can use MediaElementSource for streaming)
   */
  async loadTrack(name, url, options = {}) {
    const { streaming = true } = options;

    if (streaming) {
      // Use HTML5 Audio element for streaming (doesn't load entire file)
      const audio = new Audio();
      audio.src = url;
      audio.preload = 'auto';
      audio.loop = true;

      // Wait for enough data to play
      await new Promise((resolve, reject) => {
        audio.addEventListener('canplaythrough', resolve, { once: true });
        audio.addEventListener('error', reject, { once: true });
        audio.load();
      });

      // Create Web Audio source from element
      const source = this.context.createMediaElementSource(audio);

      this.tracks.set(name, {
        type: 'streaming',
        audio,
        source,
        url
      });

    } else {
      // Load entire file into buffer
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await this.context.decodeAudioData(arrayBuffer);

      this.tracks.set(name, {
        type: 'buffered',
        buffer: audioBuffer,
        url
      });
    }

    console.log(`Music track loaded: ${name}`);
  }

  /**
   * Play music track
   */
  play(trackName, options = {}) {
    const { loop = true, fadeIn = 1.0 } = options;

    // Stop current track if playing
    this.stop();

    const track = this.tracks.get(trackName);
    if (!track) {
      console.warn(`Track not found: ${trackName}`);
      return;
    }

    const now = this.context.currentTime;

    // Create gain node for volume control
    this.musicGain = this.context.createGain();
    this.musicGain.gain.setValueAtTime(0, now);
    this.musicGain.connect(this.masterGain);

    if (track.type === 'streaming') {
      // Use MediaElementSource
      this.source = track.source;
      this.source.connect(this.musicGain);
      track.audio.currentTime = 0;
      track.audio.loop = loop;
      track.audio.play();

    } else {
      // Use BufferSource
      this.source = this.context.createBufferSource();
      this.source.buffer = track.buffer;
      this.source.loop = loop;
      this.source.connect(this.musicGain);
      this.source.start(now);
    }

    // Fade in
    this.musicGain.gain.linearRampToValueAtTime(
      this.volume,
      now + fadeIn
    );

    this.currentTrack = trackName;
    console.log(`Playing music: ${trackName}`);
  }

  /**
   * Stop music playback
   */
  stop(options = {}) {
    if (!this.source || !this.musicGain) return;

    const { fadeOut = 1.0 } = options;
    const now = this.context.currentTime;

    // Fade out
    this.musicGain.gain.cancelScheduledValues(now);
    this.musicGain.gain.setValueAtTime(this.musicGain.gain.value, now);
    this.musicGain.gain.linearRampToValueAtTime(0, now + fadeOut);

    // Stop and cleanup after fade
    setTimeout(() => {
      if (this.source) {
        const track = this.tracks.get(this.currentTrack);
        if (track && track.type === 'streaming') {
          track.audio.pause();
        } else if (this.source.stop) {
          try {
            this.source.stop();
          } catch (e) {
            // Already stopped
          }
        }

        this.source.disconnect();
        this.source = null;
      }

      if (this.musicGain) {
        this.musicGain.disconnect();
        this.musicGain = null;
      }

      this.currentTrack = null;
    }, fadeOut * 1000);
  }

  /**
   * Set music volume
   */
  setVolume(volume, fadeTime = 0.5) {
    this.volume = Math.max(0, Math.min(1, volume));

    if (this.musicGain) {
      const now = this.context.currentTime;
      this.musicGain.gain.cancelScheduledValues(now);
      this.musicGain.gain.setValueAtTime(this.musicGain.gain.value, now);
      this.musicGain.gain.linearRampToValueAtTime(this.volume, now + fadeTime);
    }
  }

  /**
   * Check if music is playing
   */
  isPlaying() {
    return this.source !== null;
  }

  /**
   * Get current track name
   */
  getCurrentTrack() {
    return this.currentTrack;
  }
}
```

**Claude Code Prompt:**
```
Create a music player for a web game that supports both streaming (for large
music files) and buffered playback (for smaller files). Include fade in/out,
volume control, loop support, and proper cleanup. Use MediaElementSource
for streaming and BufferSource for buffered playback.
```

## Crossfading Between Tracks

Crossfading creates smooth, professional transitions between music tracks by fading out one track while fading in another.

### Advanced Crossfade System

```javascript
class CrossfadeMusicPlayer extends MusicPlayer {
  constructor(audioContext, masterGain) {
    super(audioContext, masterGain);
    this.crossfading = false;
    this.nextTrack = null;
    this.nextGain = null;
    this.nextSource = null;
  }

  /**
   * Crossfade to new track
   */
  async crossfadeTo(trackName, duration = 2.0) {
    if (this.crossfading) {
      console.warn('Already crossfading');
      return;
    }

    const track = this.tracks.get(trackName);
    if (!track) {
      console.warn(`Track not found: ${trackName}`);
      return;
    }

    // If no current track, just play normally
    if (!this.currentTrack) {
      this.play(trackName, { fadeIn: duration });
      return;
    }

    // Don't crossfade to same track
    if (trackName === this.currentTrack) {
      return;
    }

    this.crossfading = true;
    const now = this.context.currentTime;

    // Create gain for new track
    this.nextGain = this.context.createGain();
    this.nextGain.gain.setValueAtTime(0, now);
    this.nextGain.connect(this.masterGain);

    // Create and start new source
    if (track.type === 'streaming') {
      this.nextSource = track.source;
      this.nextSource.connect(this.nextGain);
      track.audio.currentTime = 0;
      track.audio.loop = true;
      track.audio.play();
    } else {
      this.nextSource = this.context.createBufferSource();
      this.nextSource.buffer = track.buffer;
      this.nextSource.loop = true;
      this.nextSource.connect(this.nextGain);
      this.nextSource.start(now);
    }

    // Crossfade: fade out current, fade in next
    if (this.musicGain) {
      this.musicGain.gain.cancelScheduledValues(now);
      this.musicGain.gain.setValueAtTime(this.musicGain.gain.value, now);
      this.musicGain.gain.linearRampToValueAtTime(0, now + duration);
    }

    this.nextGain.gain.linearRampToValueAtTime(this.volume, now + duration);

    // Switch tracks after crossfade
    setTimeout(() => {
      // Stop old track
      if (this.source) {
        const oldTrack = this.tracks.get(this.currentTrack);
        if (oldTrack && oldTrack.type === 'streaming') {
          oldTrack.audio.pause();
        } else if (this.source.stop) {
          try {
            this.source.stop();
          } catch (e) {
            // Already stopped
          }
        }
        this.source.disconnect();
      }

      if (this.musicGain) {
        this.musicGain.disconnect();
      }

      // Make next track the current track
      this.source = this.nextSource;
      this.musicGain = this.nextGain;
      this.currentTrack = trackName;

      // Reset next track references
      this.nextSource = null;
      this.nextGain = null;
      this.crossfading = false;

      console.log(`Crossfaded to: ${trackName}`);
    }, duration * 1000);
  }

  /**
   * Seamless transition at specific beat/measure
   */
  async crossfadeAtBeat(trackName, beatsPerMinute, beatsPerBar = 4, duration = 2.0) {
    if (!this.currentTrack) {
      this.play(trackName);
      return;
    }

    const currentTime = this.getCurrentTime();
    const secondsPerBeat = 60 / beatsPerMinute;
    const secondsPerBar = secondsPerBeat * beatsPerBar;

    // Calculate time until next bar
    const timeSinceStart = currentTime;
    const timeInCurrentBar = timeSinceStart % secondsPerBar;
    const timeUntilNextBar = secondsPerBar - timeInCurrentBar;

    // Schedule crossfade to start at next bar
    setTimeout(() => {
      this.crossfadeTo(trackName, duration);
    }, timeUntilNextBar * 1000);

    console.log(`Crossfade scheduled in ${timeUntilNextBar.toFixed(2)}s (at next bar)`);
  }

  /**
   * Get current playback time
   */
  getCurrentTime() {
    if (!this.currentTrack) return 0;

    const track = this.tracks.get(this.currentTrack);
    if (track && track.type === 'streaming') {
      return track.audio.currentTime;
    } else if (this.source && this.source.context) {
      return this.source.context.currentTime;
    }

    return 0;
  }
}
```

**Claude Code Prompt:**
```
Create a crossfading music system that smoothly transitions between tracks
with configurable crossfade duration. Support timing crossfades to musical
beats and bars for seamless transitions. Handle both streaming and buffered
audio sources.
```

## Dynamic Music (Layering System)

Dynamic music systems layer multiple tracks that play simultaneously, enabling or disabling layers based on gameplay intensity.

### Layered Music System

```javascript
class LayeredMusicSystem {
  constructor(audioContext, masterGain) {
    this.context = audioContext;
    this.masterGain = masterGain;
    this.layers = new Map();
    this.playing = false;
    this.currentIntensity = 0;
    this.intensityLevels = [];
  }

  /**
   * Load music layers
   */
  async loadLayers(layerConfig) {
    /*
     * layerConfig format:
     * {
     *   'base': { url: 'music/base.ogg', intensity: 0 },
     *   'drums': { url: 'music/drums.ogg', intensity: 1 },
     *   'melody': { url: 'music/melody.ogg', intensity: 2 },
     *   'full': { url: 'music/full.ogg', intensity: 3 }
     * }
     */

    const loadPromises = Object.entries(layerConfig).map(async ([name, config]) => {
      const audio = new Audio();
      audio.src = config.url;
      audio.preload = 'auto';
      audio.loop = true;

      await new Promise((resolve, reject) => {
        audio.addEventListener('canplaythrough', resolve, { once: true });
        audio.addEventListener('error', reject, { once: true });
        audio.load();
      });

      const source = this.context.createMediaElementSource(audio);
      const gain = this.context.createGain();
      gain.gain.value = 0; // Start silent

      source.connect(gain);
      gain.connect(this.masterGain);

      this.layers.set(name, {
        audio,
        source,
        gain,
        intensity: config.intensity || 0,
        volume: config.volume || 1
      });

      // Track intensity levels
      if (!this.intensityLevels.includes(config.intensity)) {
        this.intensityLevels.push(config.intensity);
      }
    });

    await Promise.all(loadPromises);

    // Sort intensity levels
    this.intensityLevels.sort((a, b) => a - b);

    console.log(`Loaded ${this.layers.size} music layers`);
  }

  /**
   * Start all layers (synced)
   */
  start(initialIntensity = 0) {
    if (this.playing) return;

    const now = this.context.currentTime;

    // Start all layers simultaneously for sync
    for (const [name, layer] of this.layers) {
      layer.audio.currentTime = 0;
      layer.audio.play();

      // Set initial gain based on intensity
      if (layer.intensity <= initialIntensity) {
        layer.gain.gain.setValueAtTime(layer.volume, now);
      } else {
        layer.gain.gain.setValueAtTime(0, now);
      }
    }

    this.playing = true;
    this.currentIntensity = initialIntensity;
    console.log(`Music layers started at intensity ${initialIntensity}`);
  }

  /**
   * Stop all layers
   */
  stop(fadeOut = 1.0) {
    if (!this.playing) return;

    const now = this.context.currentTime;

    for (const layer of this.layers.values()) {
      layer.gain.gain.linearRampToValueAtTime(0, now + fadeOut);
    }

    setTimeout(() => {
      for (const layer of this.layers.values()) {
        layer.audio.pause();
      }
      this.playing = false;
    }, fadeOut * 1000);
  }

  /**
   * Set music intensity (0 = minimal, higher = more layers)
   */
  setIntensity(intensity, transitionTime = 2.0) {
    if (!this.playing) return;

    intensity = Math.max(0, intensity);
    this.currentIntensity = intensity;

    const now = this.context.currentTime;

    for (const [name, layer] of this.layers) {
      const targetVolume = layer.intensity <= intensity ? layer.volume : 0;

      layer.gain.gain.cancelScheduledValues(now);
      layer.gain.gain.setValueAtTime(layer.gain.gain.value, now);
      layer.gain.gain.linearRampToValueAtTime(targetVolume, now + transitionTime);
    }

    console.log(`Music intensity set to ${intensity}`);
  }

  /**
   * Gradually increase intensity
   */
  increaseIntensity(transitionTime = 2.0) {
    const currentIndex = this.intensityLevels.indexOf(this.currentIntensity);
    if (currentIndex < this.intensityLevels.length - 1) {
      this.setIntensity(this.intensityLevels[currentIndex + 1], transitionTime);
    }
  }

  /**
   * Gradually decrease intensity
   */
  decreaseIntensity(transitionTime = 2.0) {
    const currentIndex = this.intensityLevels.indexOf(this.currentIntensity);
    if (currentIndex > 0) {
      this.setIntensity(this.intensityLevels[currentIndex - 1], transitionTime);
    }
  }

  /**
   * Set volume for specific layer
   */
  setLayerVolume(layerName, volume) {
    const layer = this.layers.get(layerName);
    if (!layer) return;

    layer.volume = volume;

    if (this.playing && layer.intensity <= this.currentIntensity) {
      const now = this.context.currentTime;
      layer.gain.gain.setTargetAtTime(volume, now, 0.1);
    }
  }

  /**
   * Get current intensity
   */
  getIntensity() {
    return this.currentIntensity;
  }
}
```

**Claude Code Prompt:**
```
Create a layered music system for a web game where multiple synchronized
music tracks play simultaneously. Support dynamic intensity levels that
enable/disable layers with smooth volume transitions. All layers should
stay synchronized.
```

## Adaptive Music Based on Gameplay

Adaptive music responds to gameplay events in real-time, creating a dynamic audio experience that matches player actions.

### Adaptive Music Controller

```javascript
class AdaptiveMusicController {
  constructor() {
    this.musicPlayer = null;
    this.currentState = 'menu';
    this.stateTransitions = new Map();
    this.eventHandlers = new Map();
  }

  /**
   * Initialize with music player
   */
  initialize(musicPlayer) {
    this.musicPlayer = musicPlayer;
  }

  /**
   * Define music for different game states
   */
  defineStates(stateConfig) {
    /*
     * stateConfig format:
     * {
     *   'menu': { track: 'menu_music', loop: true },
     *   'gameplay_calm': { track: 'gameplay_calm', loop: true },
     *   'gameplay_combat': { track: 'gameplay_combat', loop: true },
     *   'boss_fight': { track: 'boss_music', loop: true },
     *   'victory': { track: 'victory_music', loop: false },
     *   'game_over': { track: 'game_over_music', loop: false }
     * }
     */

    this.stateTransitions = new Map(Object.entries(stateConfig));
  }

  /**
   * Transition to new game state
   */
  async transitionToState(newState, options = {}) {
    if (newState === this.currentState) return;

    const config = this.stateTransitions.get(newState);
    if (!config) {
      console.warn(`Unknown music state: ${newState}`);
      return;
    }

    const {
      crossfadeDuration = 2.0,
      immediate = false
    } = options;

    console.log(`Music transitioning: ${this.currentState} -> ${newState}`);

    if (immediate) {
      this.musicPlayer.stop({ fadeOut: 0.5 });
      setTimeout(() => {
        this.musicPlayer.play(config.track, { loop: config.loop });
      }, 500);
    } else {
      await this.musicPlayer.crossfadeTo(config.track, crossfadeDuration);
    }

    this.currentState = newState;
  }

  /**
   * Handle specific gameplay events
   */
  onGameEvent(eventName, handler) {
    this.eventHandlers.set(eventName, handler);
  }

  /**
   * Trigger gameplay event
   */
  triggerEvent(eventName, data = {}) {
    const handler = this.eventHandlers.get(eventName);
    if (handler) {
      handler(data, this);
    }
  }

  /**
   * Get current state
   */
  getCurrentState() {
    return this.currentState;
  }
}

// Example usage with gameplay integration
class GameMusicManager {
  constructor(audioContext, masterGain) {
    this.crossfadePlayer = new CrossfadeMusicPlayer(audioContext, masterGain);
    this.layeredPlayer = new LayeredMusicSystem(audioContext, masterGain);
    this.adaptiveController = new AdaptiveMusicController();
  }

  async initialize() {
    // Load crossfade tracks
    await this.crossfadePlayer.loadTrack('menu', '/music/menu.ogg');
    await this.crossfadePlayer.loadTrack('gameplay_calm', '/music/gameplay_calm.ogg');
    await this.crossfadePlayer.loadTrack('boss_music', '/music/boss.ogg');
    await this.crossfadePlayer.loadTrack('victory', '/music/victory.ogg');

    // Load layered combat music
    await this.layeredPlayer.loadLayers({
      'combat_base': { url: '/music/combat_base.ogg', intensity: 0 },
      'combat_drums': { url: '/music/combat_drums.ogg', intensity: 1 },
      'combat_strings': { url: '/music/combat_strings.ogg', intensity: 2 },
      'combat_full': { url: '/music/combat_full.ogg', intensity: 3 }
    });

    // Setup adaptive controller
    this.adaptiveController.initialize(this.crossfadePlayer);
    this.adaptiveController.defineStates({
      'menu': { track: 'menu', loop: true },
      'exploration': { track: 'gameplay_calm', loop: true },
      'boss_fight': { track: 'boss_music', loop: true },
      'victory': { track: 'victory', loop: false }
    });

    // Define event handlers
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    // Enemy spotted - increase combat intensity
    this.adaptiveController.onGameEvent('enemy_spotted', (data, controller) => {
      if (this.layeredPlayer.playing) {
        this.layeredPlayer.increaseIntensity(1.5);
      }
    });

    // Combat started
    this.adaptiveController.onGameEvent('combat_start', async (data, controller) => {
      // Stop menu/exploration music
      this.crossfadePlayer.stop({ fadeOut: 1.0 });

      // Start layered combat music at low intensity
      setTimeout(() => {
        this.layeredPlayer.start(0);
      }, 1000);
    });

    // Combat intensity changes based on enemy count
    this.adaptiveController.onGameEvent('enemy_count_changed', (data, controller) => {
      const { count } = data;

      let intensity;
      if (count === 0) {
        intensity = 0;
      } else if (count <= 2) {
        intensity = 1;
      } else if (count <= 5) {
        intensity = 2;
      } else {
        intensity = 3;
      }

      this.layeredPlayer.setIntensity(intensity, 1.0);
    });

    // Combat ended
    this.adaptiveController.onGameEvent('combat_end', (data, controller) => {
      // Fade out combat music
      this.layeredPlayer.stop(2.0);

      // Resume exploration music
      setTimeout(() => {
        controller.transitionToState('exploration', { immediate: false });
      }, 2000);
    });

    // Boss fight started
    this.adaptiveController.onGameEvent('boss_start', (data, controller) => {
      this.layeredPlayer.stop({ fadeOut: 1.0 });
      controller.transitionToState('boss_fight', { crossfadeDuration: 1.5 });
    });

    // Victory
    this.adaptiveController.onGameEvent('victory', (data, controller) => {
      this.layeredPlayer.stop({ fadeOut: 1.0 });
      controller.transitionToState('victory', { immediate: true });
    });
  }

  // Game integration methods
  onMenuEnter() {
    this.adaptiveController.transitionToState('menu');
  }

  onGameStart() {
    this.adaptiveController.transitionToState('exploration');
  }

  onEnemySpotted() {
    this.adaptiveController.triggerEvent('enemy_spotted');
  }

  onCombatStart() {
    this.adaptiveController.triggerEvent('combat_start');
  }

  onEnemyCountChanged(count) {
    this.adaptiveController.triggerEvent('enemy_count_changed', { count });
  }

  onCombatEnd() {
    this.adaptiveController.triggerEvent('combat_end');
  }

  onBossStart() {
    this.adaptiveController.triggerEvent('boss_start');
  }

  onVictory() {
    this.adaptiveController.triggerEvent('victory');
  }
}
```

**Claude Code Prompt:**
```
Create an adaptive music system that responds to gameplay events in real-time.
Support state-based transitions (menu, exploration, combat, boss) and
event-driven intensity changes. Integrate crossfading for track transitions
and layered music for combat intensity.
```

## Seamless Loop Implementation

Creating perfectly seamless music loops requires careful timing and buffer preparation.

### Seamless Loop Manager

```javascript
class SeamlessLoopManager {
  constructor(audioContext, masterGain) {
    this.context = audioContext;
    this.masterGain = masterGain;
    this.loops = new Map();
    this.scheduledSources = [];
    this.scheduleAheadTime = 0.1; // How far ahead to schedule (seconds)
    this.lastScheduledTime = 0;
  }

  /**
   * Load and prepare loop
   */
  async loadLoop(name, url, loopStart = 0, loopEnd = null) {
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await this.context.decodeAudioData(arrayBuffer);

    // Auto-detect loop end if not specified
    const actualLoopEnd = loopEnd || audioBuffer.duration;

    this.loops.set(name, {
      buffer: audioBuffer,
      loopStart,
      loopEnd: actualLoopEnd,
      loopDuration: actualLoopEnd - loopStart
    });

    console.log(`Loop loaded: ${name} (${loopStart}s - ${actualLoopEnd}s)`);
  }

  /**
   * Play seamless loop with perfect timing
   */
  playLoop(name, options = {}) {
    const loop = this.loops.get(name);
    if (!loop) {
      console.warn(`Loop not found: ${name}`);
      return null;
    }

    const { volume = 1, fadeIn = 0 } = options;

    // Create gain node
    const gain = this.context.createGain();
    gain.gain.setValueAtTime(fadeIn > 0 ? 0 : volume, this.context.currentTime);
    gain.connect(this.masterGain);

    if (fadeIn > 0) {
      gain.gain.linearRampToValueAtTime(
        volume,
        this.context.currentTime + fadeIn
      );
    }

    // Schedule first iteration
    this.lastScheduledTime = this.context.currentTime;
    this.scheduleLoopIteration(loop, gain, this.lastScheduledTime);

    // Schedule future iterations
    const schedulerInterval = setInterval(() => {
      const currentTime = this.context.currentTime;

      // Schedule next iteration if needed
      while (this.lastScheduledTime < currentTime + this.scheduleAheadTime) {
        this.scheduleLoopIteration(loop, gain, this.lastScheduledTime);
      }
    }, 50); // Check every 50ms

    return {
      gain,
      stop: (fadeOut = 0) => {
        clearInterval(schedulerInterval);

        if (fadeOut > 0) {
          const now = this.context.currentTime;
          gain.gain.cancelScheduledValues(now);
          gain.gain.setValueAtTime(gain.gain.value, now);
          gain.gain.linearRampToValueAtTime(0, now + fadeOut);

          setTimeout(() => {
            this.stopAllScheduled();
            gain.disconnect();
          }, fadeOut * 1000);
        } else {
          this.stopAllScheduled();
          gain.disconnect();
        }
      }
    };
  }

  /**
   * Schedule single loop iteration
   */
  scheduleLoopIteration(loop, gainNode, startTime) {
    const source = this.context.createBufferSource();
    source.buffer = loop.buffer;
    source.connect(gainNode);

    // Play only the loop section
    source.start(
      startTime,
      loop.loopStart,
      loop.loopDuration
    );

    this.scheduledSources.push(source);
    this.lastScheduledTime = startTime + loop.loopDuration;

    // Remove from scheduled list when done
    source.onended = () => {
      const index = this.scheduledSources.indexOf(source);
      if (index > -1) {
        this.scheduledSources.splice(index, 1);
      }
    };
  }

  /**
   * Stop all scheduled sources
   */
  stopAllScheduled() {
    for (const source of this.scheduledSources) {
      try {
        source.stop();
        source.disconnect();
      } catch (e) {
        // Already stopped
      }
    }
    this.scheduledSources = [];
  }
}
```

**Claude Code Prompt:**
```
Create a seamless music loop system that uses precise timing to schedule
buffer playback for perfectly gapless loops. Support custom loop points
(start/end times) and schedule iterations ahead of time to prevent gaps.
```

## Performance Considerations

### Memory Management for Music

```javascript
class MusicMemoryManager {
  constructor(maxBufferedTracks = 3) {
    this.maxBufferedTracks = maxBufferedTracks;
    this.bufferedTracks = new Map();
    this.accessTimes = new Map();
  }

  /**
   * Cache track with LRU eviction
   */
  cacheTrack(name, buffer) {
    // Record access time
    this.accessTimes.set(name, Date.now());

    // Check if we need to evict
    if (this.bufferedTracks.size >= this.maxBufferedTracks) {
      this.evictLeastRecentlyUsed();
    }

    this.bufferedTracks.set(name, buffer);
  }

  /**
   * Evict least recently used track
   */
  evictLeastRecentlyUsed() {
    let oldestName = null;
    let oldestTime = Infinity;

    for (const [name, time] of this.accessTimes) {
      if (time < oldestTime) {
        oldestTime = time;
        oldestName = name;
      }
    }

    if (oldestName) {
      console.log(`Evicting music track: ${oldestName}`);
      this.bufferedTracks.delete(oldestName);
      this.accessTimes.delete(oldestName);
    }
  }

  /**
   * Get cached track
   */
  getTrack(name) {
    if (this.bufferedTracks.has(name)) {
      this.accessTimes.set(name, Date.now());
      return this.bufferedTracks.get(name);
    }
    return null;
  }
}
```

## Best Practices

1. **Use streaming for long music tracks** - Saves memory, faster loading
2. **Preload short jingles/stingers** - Instant playback for UI feedback
3. **Synchronize layered tracks** - Start all layers at the same time
4. **Match tempos for crossfading** - Sounds more professional
5. **Provide user volume control** - Music preferences vary widely
6. **Test loop points carefully** - Clicks/pops indicate timing issues
7. **Schedule loops ahead of time** - Prevents gaps in playback
8. **Limit simultaneous music tracks** - Usually only need one or two
9. **Compress music files appropriately** - Balance quality vs file size
10. **Implement music ducking** - Lower music during dialogue/SFX

## Cross-References

- [Web Audio API](./web-audio-api.md) - Audio context and node fundamentals
- [Sound Effects](./sound-effects.md) - SFX integration with music
- [Audio Optimization](./audio-optimization.md) - Advanced optimization techniques
- [UI/UX](../07-ui-ux/README.md) - Menu music integration

## Summary

Professional music systems require more than simple playback. Master these techniques:

- Background music with smooth crossfading
- Layered music for dynamic intensity
- Adaptive music responding to gameplay
- Seamless loops with perfect timing
- Memory management for large audio files
- State-based music transitions

These systems create immersive, emotionally resonant experiences that elevate your game from functional to memorable. Claude Code helps implement sophisticated music systems efficiently, letting you focus on creating the perfect audio experience for your players.
