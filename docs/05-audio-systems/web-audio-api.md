# Web Audio API

## Overview

The Web Audio API is a powerful, high-level JavaScript API for processing and synthesizing audio in web applications. Unlike the simple HTML5 `<audio>` element, the Web Audio API provides low-latency playback, precise timing control, real-time audio processing, and a modular routing system that enables complex audio graphs. It's the foundation for all professional web game audio.

Understanding the Web Audio API is essential for game developers. It operates on a fundamentally different paradigm than traditional audio playback: instead of simply playing files, you create directed graphs of audio nodes that process, route, and mix audio in real-time. This architecture enables sophisticated audio effects, spatial positioning, and dynamic mixing impossible with simpler approaches.

This guide covers Web Audio API fundamentals with complete, production-ready implementations you can use immediately in your games.

## Audio Context: The Foundation

Every Web Audio API application starts with an AudioContext. This context manages all audio operations, tracks timing, and contains the audio destination (typically the user's speakers). Think of it as the central hub that coordinates all audio processing.

### Creating and Managing Audio Context

```javascript
class AudioManager {
  constructor() {
    this.context = null;
    this.masterGain = null;
    this.initialized = false;
  }

  /**
   * Initialize audio context - must be called from user interaction
   * on mobile browsers due to autoplay policies
   */
  async initialize() {
    if (this.initialized) return;

    try {
      // Create audio context with optimal settings
      this.context = new (window.AudioContext || window.webkitAudioContext)({
        latencyHint: 'interactive', // Optimize for low latency
        sampleRate: 44100 // Standard sample rate
      });

      // Create master gain node for volume control
      this.masterGain = this.context.createGain();
      this.masterGain.connect(this.context.destination);

      // Handle audio context state changes
      this.context.onstatechange = () => {
        console.log('Audio context state:', this.context.state);
      };

      // Resume context if suspended (common on mobile)
      if (this.context.state === 'suspended') {
        await this.context.resume();
      }

      this.initialized = true;
      console.log('Audio system initialized successfully');
    } catch (error) {
      console.error('Failed to initialize audio:', error);
      throw error;
    }
  }

  /**
   * Set master volume (0 to 1)
   */
  setMasterVolume(volume) {
    if (!this.masterGain) return;

    // Use exponential ramp for smooth, natural volume changes
    const now = this.context.currentTime;
    this.masterGain.gain.setTargetAtTime(
      Math.max(0, Math.min(1, volume)),
      now,
      0.015 // Time constant for smooth transition
    );
  }

  /**
   * Get current time in audio context timeline
   */
  getCurrentTime() {
    return this.context ? this.context.currentTime : 0;
  }

  /**
   * Cleanup audio resources
   */
  async dispose() {
    if (this.context) {
      await this.context.close();
      this.context = null;
      this.initialized = false;
    }
  }
}

// Global audio manager instance
const audioManager = new AudioManager();

// Initialize on first user interaction
document.addEventListener('click', () => {
  audioManager.initialize();
}, { once: true });
```

**Claude Code Prompt:**
```
Create an AudioContext manager for a web game that handles initialization,
master volume control, mobile browser autoplay restrictions, and proper
cleanup. Include error handling and state management.
```

## Audio Nodes and Routing

The Web Audio API uses a modular node-based architecture. Audio flows from source nodes through processing nodes to the destination. Understanding this flow is crucial for creating complex audio systems.

### Basic Audio Node Types

**Source Nodes**: Generate or load audio
- `AudioBufferSourceNode`: Plays loaded audio buffers (for sound effects)
- `MediaElementSourceNode`: Wraps HTML5 audio elements (for streaming music)
- `OscillatorNode`: Generates synthesized tones

**Processing Nodes**: Modify audio
- `GainNode`: Controls volume
- `BiquadFilterNode`: Applies filters (lowpass, highpass, etc.)
- `ConvolverNode`: Creates reverb effects
- `DelayNode`: Creates echo/delay effects
- `PannerNode`: Positions audio in 3D space

**Destination Node**: Final output (`context.destination`)

### Complete Audio Loading and Playback System

```javascript
class AudioLoader {
  constructor(audioManager) {
    this.audioManager = audioManager;
    this.buffers = new Map(); // Cache loaded audio buffers
    this.loading = new Map(); // Track in-progress loads
  }

  /**
   * Load audio file and decode to buffer
   */
  async load(name, url) {
    // Return cached buffer if already loaded
    if (this.buffers.has(name)) {
      return this.buffers.get(name);
    }

    // Return existing promise if already loading
    if (this.loading.has(name)) {
      return this.loading.get(name);
    }

    // Create loading promise
    const loadPromise = (async () => {
      try {
        console.log(`Loading audio: ${name}`);

        // Fetch audio file
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Failed to load ${url}: ${response.statusText}`);
        }

        // Get array buffer
        const arrayBuffer = await response.arrayBuffer();

        // Decode audio data
        const audioBuffer = await this.audioManager.context.decodeAudioData(arrayBuffer);

        // Cache buffer
        this.buffers.set(name, audioBuffer);
        this.loading.delete(name);

        console.log(`Audio loaded: ${name} (${audioBuffer.duration.toFixed(2)}s)`);
        return audioBuffer;

      } catch (error) {
        this.loading.delete(name);
        console.error(`Error loading audio ${name}:`, error);
        throw error;
      }
    })();

    this.loading.set(name, loadPromise);
    return loadPromise;
  }

  /**
   * Load multiple audio files
   */
  async loadAll(audioFiles) {
    const promises = Object.entries(audioFiles).map(([name, url]) =>
      this.load(name, url)
    );

    try {
      await Promise.all(promises);
      console.log('All audio files loaded successfully');
    } catch (error) {
      console.error('Error loading audio files:', error);
      throw error;
    }
  }

  /**
   * Get loaded buffer
   */
  get(name) {
    return this.buffers.get(name);
  }

  /**
   * Check if audio is loaded
   */
  has(name) {
    return this.buffers.has(name);
  }

  /**
   * Unload audio buffer to free memory
   */
  unload(name) {
    this.buffers.delete(name);
  }

  /**
   * Clear all loaded audio
   */
  clear() {
    this.buffers.clear();
    this.loading.clear();
  }
}
```

**Claude Code Prompt:**
```
Create an audio loading system for a web game that fetches and decodes
audio files, caches buffers, prevents duplicate loading, and handles
errors gracefully. Include progress tracking and memory management.
```

## Spatial Audio (3D Positioning)

Spatial audio creates immersive 3D soundscapes by positioning sounds in 3D space relative to a listener. This is crucial for first-person games, racing games, and any experience where sound direction matters.

### 3D Audio Positioning System

```javascript
class SpatialAudioSystem {
  constructor(audioManager) {
    this.audioManager = audioManager;
    this.listener = audioManager.context.listener;
    this.sources = new Map(); // Active spatial sound sources
  }

  /**
   * Set listener (player/camera) position and orientation
   */
  setListenerPosition(x, y, z) {
    const listener = this.listener;

    if (listener.positionX) {
      // Modern API (Chrome, Firefox)
      listener.positionX.setValueAtTime(x, this.audioManager.getCurrentTime());
      listener.positionY.setValueAtTime(y, this.audioManager.getCurrentTime());
      listener.positionZ.setValueAtTime(z, this.audioManager.getCurrentTime());
    } else {
      // Fallback for older browsers
      listener.setPosition(x, y, z);
    }
  }

  /**
   * Set listener orientation (forward and up vectors)
   */
  setListenerOrientation(forwardX, forwardY, forwardZ, upX = 0, upY = 1, upZ = 0) {
    const listener = this.listener;

    if (listener.forwardX) {
      // Modern API
      const time = this.audioManager.getCurrentTime();
      listener.forwardX.setValueAtTime(forwardX, time);
      listener.forwardY.setValueAtTime(forwardY, time);
      listener.forwardZ.setValueAtTime(forwardZ, time);
      listener.upX.setValueAtTime(upX, time);
      listener.upY.setValueAtTime(upY, time);
      listener.upZ.setValueAtTime(upZ, time);
    } else {
      // Fallback
      listener.setOrientation(forwardX, forwardY, forwardZ, upX, upY, upZ);
    }
  }

  /**
   * Play spatial audio at specific 3D position
   */
  playAtPosition(audioBuffer, x, y, z, options = {}) {
    const {
      volume = 1,
      loop = false,
      refDistance = 1,      // Distance at which volume starts decreasing
      maxDistance = 10000,  // Maximum hearing distance
      rolloffFactor = 1,    // How quickly volume decreases with distance
      coneInnerAngle = 360, // Full volume cone angle
      coneOuterAngle = 360, // Audible cone angle
      coneOuterGain = 0     // Volume outside outer cone
    } = options;

    const context = this.audioManager.context;
    const now = context.currentTime;

    // Create source node
    const source = context.createBufferSource();
    source.buffer = audioBuffer;
    source.loop = loop;

    // Create panner for 3D positioning
    const panner = context.createPanner();
    panner.panningModel = 'HRTF'; // Head-related transfer function for realistic 3D
    panner.distanceModel = 'inverse'; // Natural distance falloff
    panner.refDistance = refDistance;
    panner.maxDistance = maxDistance;
    panner.rolloffFactor = rolloffFactor;
    panner.coneInnerAngle = coneInnerAngle;
    panner.coneOuterAngle = coneOuterAngle;
    panner.coneOuterGain = coneOuterGain;

    // Set position
    if (panner.positionX) {
      panner.positionX.setValueAtTime(x, now);
      panner.positionY.setValueAtTime(y, now);
      panner.positionZ.setValueAtTime(z, now);
    } else {
      panner.setPosition(x, y, z);
    }

    // Create gain for volume control
    const gain = context.createGain();
    gain.gain.setValueAtTime(volume, now);

    // Connect: source -> panner -> gain -> master
    source.connect(panner);
    panner.connect(gain);
    gain.connect(this.audioManager.masterGain);

    // Start playback
    source.start(now);

    // Generate unique ID for this source
    const id = `spatial_${Date.now()}_${Math.random()}`;

    // Store reference
    this.sources.set(id, {
      source,
      panner,
      gain,
      startTime: now
    });

    // Clean up when sound finishes
    source.onended = () => {
      this.stop(id);
    };

    return id;
  }

  /**
   * Update position of playing spatial sound
   */
  updatePosition(id, x, y, z) {
    const sound = this.sources.get(id);
    if (!sound) return;

    const panner = sound.panner;
    const now = this.audioManager.getCurrentTime();

    if (panner.positionX) {
      panner.positionX.setValueAtTime(x, now);
      panner.positionY.setValueAtTime(y, now);
      panner.positionZ.setValueAtTime(z, now);
    } else {
      panner.setPosition(x, y, z);
    }
  }

  /**
   * Stop spatial sound
   */
  stop(id) {
    const sound = this.sources.get(id);
    if (!sound) return;

    try {
      sound.source.stop();
      sound.source.disconnect();
      sound.panner.disconnect();
      sound.gain.disconnect();
    } catch (e) {
      // Already stopped
    }

    this.sources.delete(id);
  }

  /**
   * Stop all spatial sounds
   */
  stopAll() {
    for (const id of this.sources.keys()) {
      this.stop(id);
    }
  }
}
```

**Claude Code Prompt:**
```
Create a 3D spatial audio system for a web game that positions sounds
in 3D space, tracks listener position and orientation, handles distance
attenuation, and supports directional audio cones. Use the Web Audio API
PannerNode with HRTF for realistic spatialization.
```

## Audio Effects

The Web Audio API provides powerful built-in audio effects through processing nodes. Here are the most useful effects for games.

### Complete Audio Effects Library

```javascript
class AudioEffects {
  constructor(audioManager) {
    this.audioManager = audioManager;
    this.context = audioManager.context;
  }

  /**
   * Create reverb effect using convolution
   */
  createReverb(duration = 2, decay = 2) {
    const context = this.context;
    const sampleRate = context.sampleRate;
    const length = sampleRate * duration;
    const impulse = context.createBuffer(2, length, sampleRate);
    const impulseL = impulse.getChannelData(0);
    const impulseR = impulse.getChannelData(1);

    // Generate reverb impulse response
    for (let i = 0; i < length; i++) {
      const n = length - i;
      impulseL[i] = (Math.random() * 2 - 1) * Math.pow(n / length, decay);
      impulseR[i] = (Math.random() * 2 - 1) * Math.pow(n / length, decay);
    }

    const convolver = context.createConvolver();
    convolver.buffer = impulse;

    return convolver;
  }

  /**
   * Create delay/echo effect
   */
  createDelay(delayTime = 0.5, feedback = 0.4, mix = 0.5) {
    const context = this.context;

    // Create nodes
    const input = context.createGain();
    const output = context.createGain();
    const delay = context.createDelay(5); // Max 5 seconds delay
    const feedbackGain = context.createGain();
    const mixGain = context.createGain();

    // Set parameters
    delay.delayTime.value = delayTime;
    feedbackGain.gain.value = feedback;
    mixGain.gain.value = mix;

    // Connect: input -> delay -> feedbackGain -> delay (feedback loop)
    input.connect(delay);
    delay.connect(feedbackGain);
    feedbackGain.connect(delay);

    // Mix dry and wet signals
    input.connect(output); // Dry signal
    delay.connect(mixGain);
    mixGain.connect(output); // Wet signal

    return {
      input,
      output,
      setDelayTime: (time) => {
        delay.delayTime.setTargetAtTime(time, context.currentTime, 0.01);
      },
      setFeedback: (fb) => {
        feedbackGain.gain.setTargetAtTime(fb, context.currentTime, 0.01);
      },
      setMix: (m) => {
        mixGain.gain.setTargetAtTime(m, context.currentTime, 0.01);
      }
    };
  }

  /**
   * Create lowpass filter (muffles sound)
   */
  createLowpassFilter(frequency = 1000, q = 1) {
    const filter = this.context.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = frequency;
    filter.Q.value = q;
    return filter;
  }

  /**
   * Create highpass filter (removes bass)
   */
  createHighpassFilter(frequency = 1000, q = 1) {
    const filter = this.context.createBiquadFilter();
    filter.type = 'highpass';
    filter.frequency.value = frequency;
    filter.Q.value = q;
    return filter;
  }

  /**
   * Create dynamic compressor (evens out volume)
   */
  createCompressor(threshold = -24, knee = 30, ratio = 12, attack = 0.003, release = 0.25) {
    const compressor = this.context.createDynamicsCompressor();
    compressor.threshold.value = threshold;
    compressor.knee.value = knee;
    compressor.ratio.value = ratio;
    compressor.attack.value = attack;
    compressor.release.value = release;
    return compressor;
  }

  /**
   * Create stereo panner (left/right positioning)
   */
  createStereoPanner(pan = 0) {
    const panner = this.context.createStereoPanner();
    panner.pan.value = Math.max(-1, Math.min(1, pan)); // Clamp to -1 to 1
    return panner;
  }
}
```

**Claude Code Prompt:**
```
Create an audio effects library for a web game using the Web Audio API
that includes reverb, delay/echo, lowpass/highpass filters, dynamic
compression, and stereo panning. Each effect should be configurable
and chainable.
```

## Complete Game Audio System Implementation

Here's a production-ready audio system combining all concepts:

```javascript
/**
 * Complete game audio system
 */
class GameAudioSystem {
  constructor() {
    this.audioManager = new AudioManager();
    this.loader = null;
    this.spatialAudio = null;
    this.effects = null;
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return;

    await this.audioManager.initialize();
    this.loader = new AudioLoader(this.audioManager);
    this.spatialAudio = new SpatialAudioSystem(this.audioManager);
    this.effects = new AudioEffects(this.audioManager);
    this.initialized = true;
  }

  /**
   * Load game audio assets
   */
  async loadAssets(audioFiles) {
    await this.loader.loadAll(audioFiles);
  }

  /**
   * Play simple 2D sound effect
   */
  playSFX(name, options = {}) {
    const buffer = this.loader.get(name);
    if (!buffer) {
      console.warn(`Audio not loaded: ${name}`);
      return null;
    }

    const {
      volume = 1,
      playbackRate = 1,
      loop = false,
      pan = 0
    } = options;

    const context = this.audioManager.context;
    const now = context.currentTime;

    // Create source
    const source = context.createBufferSource();
    source.buffer = buffer;
    source.loop = loop;
    source.playbackRate.value = playbackRate;

    // Create gain
    const gain = context.createGain();
    gain.gain.setValueAtTime(volume, now);

    // Create panner
    const panner = context.createStereoPanner();
    panner.pan.value = pan;

    // Connect
    source.connect(gain);
    gain.connect(panner);
    panner.connect(this.audioManager.masterGain);

    // Play
    source.start(now);

    return {
      source,
      gain,
      stop: () => {
        try {
          source.stop();
        } catch (e) {
          // Already stopped
        }
      },
      setVolume: (vol) => {
        gain.gain.setTargetAtTime(vol, context.currentTime, 0.015);
      }
    };
  }

  /**
   * Play 3D positioned sound
   */
  play3D(name, x, y, z, options = {}) {
    const buffer = this.loader.get(name);
    if (!buffer) {
      console.warn(`Audio not loaded: ${name}`);
      return null;
    }

    return this.spatialAudio.playAtPosition(buffer, x, y, z, options);
  }

  /**
   * Update listener position (camera/player)
   */
  setListenerPosition(x, y, z) {
    this.spatialAudio.setListenerPosition(x, y, z);
  }

  /**
   * Update listener orientation
   */
  setListenerOrientation(forwardX, forwardY, forwardZ, upX, upY, upZ) {
    this.spatialAudio.setListenerOrientation(forwardX, forwardY, forwardZ, upX, upY, upZ);
  }

  /**
   * Set master volume
   */
  setMasterVolume(volume) {
    this.audioManager.setMasterVolume(volume);
  }

  /**
   * Clean up
   */
  async dispose() {
    this.spatialAudio.stopAll();
    this.loader.clear();
    await this.audioManager.dispose();
  }
}

// Usage example
async function initGameAudio() {
  const audio = new GameAudioSystem();

  // Initialize (call from user interaction)
  await audio.initialize();

  // Load audio files
  await audio.loadAssets({
    'jump': '/sounds/jump.ogg',
    'coin': '/sounds/coin.ogg',
    'explosion': '/sounds/explosion.ogg',
    'footstep': '/sounds/footstep.ogg',
    'ambient': '/sounds/ambient.ogg'
  });

  // Play 2D sound effect
  audio.playSFX('jump', { volume: 0.8 });

  // Play 3D positioned sound
  audio.play3D('explosion', 10, 0, 5, {
    volume: 1,
    refDistance: 5,
    maxDistance: 50
  });

  // Update listener position each frame
  function gameLoop() {
    const playerX = player.x;
    const playerY = player.y;
    const playerZ = player.z;

    audio.setListenerPosition(playerX, playerY, playerZ);

    requestAnimationFrame(gameLoop);
  }

  return audio;
}
```

**Claude Code Prompt:**
```
Create a complete game audio system that integrates audio loading, 2D
sound effects, 3D spatial audio, effects processing, and listener tracking.
Include initialization handling for mobile browsers, memory management,
and a clean API for game developers.
```

## Performance Considerations

### Memory Management

Audio buffers consume significant memory. Monitor and optimize:

```javascript
// Monitor audio memory usage
function getAudioMemoryEstimate(audioBuffer) {
  const channels = audioBuffer.numberOfChannels;
  const length = audioBuffer.length;
  const sampleSize = 4; // 32-bit float
  const bytes = channels * length * sampleSize;
  return {
    bytes,
    megabytes: (bytes / 1024 / 1024).toFixed(2)
  };
}

// Unload unused audio
function optimizeAudioMemory(loader, activeAudio) {
  const loaded = Array.from(loader.buffers.keys());
  const unused = loaded.filter(name => !activeAudio.includes(name));

  unused.forEach(name => {
    console.log(`Unloading unused audio: ${name}`);
    loader.unload(name);
  });
}
```

### Limiting Simultaneous Sounds

```javascript
class SoundPool {
  constructor(maxSounds = 32) {
    this.maxSounds = maxSounds;
    this.activeSounds = [];
  }

  play(playFunction) {
    // Remove finished sounds
    this.activeSounds = this.activeSounds.filter(sound =>
      sound.source.playbackState !== 'finished'
    );

    // Limit simultaneous sounds
    if (this.activeSounds.length >= this.maxSounds) {
      // Stop oldest sound
      const oldest = this.activeSounds.shift();
      oldest.stop();
    }

    // Play new sound
    const sound = playFunction();
    if (sound) {
      this.activeSounds.push(sound);
    }

    return sound;
  }
}
```

## Mobile Considerations

Mobile browsers require special handling:

```javascript
class MobileAudioHandler {
  constructor(audioSystem) {
    this.audioSystem = audioSystem;
    this.unlocked = false;
  }

  /**
   * Unlock audio on mobile (must be called from user interaction)
   */
  async unlock() {
    if (this.unlocked) return;

    const context = this.audioSystem.audioManager.context;

    if (context.state === 'suspended') {
      await context.resume();
    }

    // Play silent sound to unlock
    const buffer = context.createBuffer(1, 1, 22050);
    const source = context.createBufferSource();
    source.buffer = buffer;
    source.connect(context.destination);
    source.start(0);

    this.unlocked = true;
    console.log('Mobile audio unlocked');
  }

  /**
   * Setup auto-unlock on first touch
   */
  setupAutoUnlock() {
    const unlock = async () => {
      await this.unlock();
      document.removeEventListener('touchstart', unlock);
      document.removeEventListener('touchend', unlock);
      document.removeEventListener('click', unlock);
    };

    document.addEventListener('touchstart', unlock, { once: true });
    document.addEventListener('touchend', unlock, { once: true });
    document.addEventListener('click', unlock, { once: true });
  }
}
```

## Best Practices

1. **Always initialize AudioContext from user interaction** - Required by browser autoplay policies
2. **Reuse AudioBufferSourceNodes through pooling** - Avoid creating new nodes in game loops
3. **Disconnect nodes when done** - Prevent memory leaks
4. **Use exponential ramps for volume changes** - Sounds more natural than linear
5. **Limit simultaneous sounds** - Especially on mobile devices
6. **Preload critical sounds** - Stream background music
7. **Test on real mobile devices** - Desktop doesn't reveal mobile audio quirks
8. **Monitor memory usage** - Audio buffers add up quickly
9. **Provide volume controls** - Let players adjust audio to their preference
10. **Gracefully handle audio failures** - Games should work without audio

## Cross-References

- [Sound Effects](./sound-effects.md) - Practical SFX system implementation
- [Music Systems](./music-systems.md) - Background music and dynamic audio
- [Audio Optimization](./audio-optimization.md) - Advanced optimization techniques
- [Core Game Concepts](../02-core-game-concepts/README.md) - Game loop integration

## Summary

The Web Audio API provides a powerful foundation for game audio. Master these concepts:

- AudioContext manages all audio operations
- Audio nodes create modular processing graphs
- Spatial audio positions sounds in 3D space
- Built-in effects enable sophisticated audio processing
- Proper initialization handles mobile restrictions
- Memory management prevents performance issues

With these fundamentals, you can build professional audio systems that create immersive, responsive game experiences. Claude Code helps implement these systems efficiently, letting you focus on creating great gameplay rather than wrestling with audio APIs.
