# Sound Effects

## Overview

Sound effects (SFX) are the immediate audio feedback that makes games feel responsive, alive, and satisfying. Every jump, every collision, every button press deserves audio confirmation. While players might not consciously notice good sound effects, they definitely notice their absence - games without SFX feel sluggish, disconnected, and lifeless.

Unlike music systems that play long, sustained audio, SFX systems must handle dozens or hundreds of short sounds playing simultaneously, often triggered unpredictably by player actions and game events. This requires different approaches: object pooling for performance, priority systems for when too many sounds trigger at once, and careful volume management to prevent audio chaos.

This guide covers professional SFX implementation techniques, from basic one-shot sounds to sophisticated pooling systems and advanced mixing strategies.

## Sound Effect Management

Managing sound effects efficiently is crucial for game performance. Creating new audio nodes for every sound creates memory overhead and can cause performance issues.

### Basic Sound Effect Player

```javascript
class SoundEffectPlayer {
  constructor(audioContext, masterGain) {
    this.context = audioContext;
    this.masterGain = masterGain;
    this.sounds = new Map();
    this.activeSources = new Set();
    this.sfxVolume = 0.8;
  }

  /**
   * Load sound effect
   */
  async loadSound(name, url) {
    try {
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await this.context.decodeAudioData(arrayBuffer);

      this.sounds.set(name, audioBuffer);
      console.log(`Sound loaded: ${name} (${audioBuffer.duration.toFixed(3)}s)`);

      return audioBuffer;
    } catch (error) {
      console.error(`Failed to load sound ${name}:`, error);
      throw error;
    }
  }

  /**
   * Load multiple sounds
   */
  async loadSounds(soundFiles) {
    const promises = Object.entries(soundFiles).map(([name, url]) =>
      this.loadSound(name, url)
    );

    await Promise.all(promises);
    console.log(`Loaded ${promises.length} sound effects`);
  }

  /**
   * Play sound effect
   */
  play(soundName, options = {}) {
    const buffer = this.sounds.get(soundName);
    if (!buffer) {
      console.warn(`Sound not found: ${soundName}`);
      return null;
    }

    const {
      volume = 1,
      playbackRate = 1,
      pan = 0,
      loop = false,
      onEnded = null
    } = options;

    const now = this.context.currentTime;

    // Create source
    const source = this.context.createBufferSource();
    source.buffer = buffer;
    source.playbackRate.value = playbackRate;
    source.loop = loop;

    // Create gain node for volume
    const gainNode = this.context.createGain();
    gainNode.gain.setValueAtTime(volume * this.sfxVolume, now);

    // Create stereo panner
    const panNode = this.context.createStereoPanner();
    panNode.pan.value = Math.max(-1, Math.min(1, pan));

    // Connect: source -> gain -> pan -> master
    source.connect(gainNode);
    gainNode.connect(panNode);
    panNode.connect(this.masterGain);

    // Track active source
    this.activeSources.add(source);

    // Cleanup when finished
    source.onended = () => {
      source.disconnect();
      gainNode.disconnect();
      panNode.disconnect();
      this.activeSources.delete(source);

      if (onEnded) {
        onEnded();
      }
    };

    // Start playback
    source.start(now);

    return {
      source,
      gainNode,
      panNode,
      stop: () => {
        try {
          source.stop();
        } catch (e) {
          // Already stopped
        }
      },
      setVolume: (vol) => {
        gainNode.gain.setTargetAtTime(
          vol * this.sfxVolume,
          this.context.currentTime,
          0.01
        );
      },
      setPan: (p) => {
        panNode.pan.setTargetAtTime(
          Math.max(-1, Math.min(1, p)),
          this.context.currentTime,
          0.01
        );
      }
    };
  }

  /**
   * Play random variation
   */
  playVariation(soundName, options = {}) {
    // Randomize pitch for variation
    const pitchVariation = options.pitchVariation || 0.1;
    const randomPitch = 1 + (Math.random() * 2 - 1) * pitchVariation;

    // Randomize volume slightly
    const volumeVariation = options.volumeVariation || 0.1;
    const baseVolume = options.volume || 1;
    const randomVolume = baseVolume * (1 + (Math.random() * 2 - 1) * volumeVariation);

    return this.play(soundName, {
      ...options,
      volume: randomVolume,
      playbackRate: randomPitch
    });
  }

  /**
   * Set master SFX volume
   */
  setVolume(volume) {
    this.sfxVolume = Math.max(0, Math.min(1, volume));

    // Update all active sources
    for (const source of this.activeSources) {
      // Note: This requires storing gain nodes with sources
      // See pooling system below for better implementation
    }
  }

  /**
   * Stop all sound effects
   */
  stopAll() {
    for (const source of this.activeSources) {
      try {
        source.stop();
      } catch (e) {
        // Already stopped
      }
    }
    this.activeSources.clear();
  }

  /**
   * Get active sound count
   */
  getActiveSoundCount() {
    return this.activeSources.size;
  }
}
```

**Claude Code Prompt:**
```
Create a sound effect player for a web game that loads and plays short
audio clips. Support volume control, pitch variation, stereo panning,
and track active sounds. Include cleanup to prevent memory leaks.
```

## Sound Effect Pooling

Object pooling reuses audio nodes instead of creating new ones, dramatically improving performance for games with frequent sound effects.

### Advanced SFX Pool System

```javascript
class SoundEffectPool {
  constructor(audioContext, masterGain, poolSize = 20) {
    this.context = audioContext;
    this.masterGain = masterGain;
    this.poolSize = poolSize;
    this.sounds = new Map();
    this.pool = [];
    this.activeInstances = new Set();
    this.sfxVolume = 0.8;

    // Pre-create pool
    this.initializePool();
  }

  /**
   * Initialize reusable audio node pool
   */
  initializePool() {
    for (let i = 0; i < this.poolSize; i++) {
      const instance = {
        source: null,
        gainNode: this.context.createGain(),
        panNode: this.context.createStereoPanner(),
        available: true,
        soundName: null
      };

      // Pre-connect gain and pan
      instance.gainNode.connect(instance.panNode);
      instance.panNode.connect(this.masterGain);

      this.pool.push(instance);
    }

    console.log(`SFX pool initialized with ${this.poolSize} instances`);
  }

  /**
   * Load sound buffer
   */
  async loadSound(name, url) {
    const response = await fetch(url);
    const arrayBuffer = await response.arrayBuffer();
    const audioBuffer = await this.context.decodeAudioData(arrayBuffer);

    this.sounds.set(name, audioBuffer);
    return audioBuffer;
  }

  /**
   * Get available instance from pool
   */
  getAvailableInstance() {
    // Find available instance
    let instance = this.pool.find(inst => inst.available);

    if (!instance) {
      // Pool exhausted - steal oldest active instance
      console.warn('SFX pool exhausted, stealing oldest instance');
      instance = this.pool[0]; // Could implement LRU here

      if (instance.source) {
        try {
          instance.source.stop();
          instance.source.disconnect();
        } catch (e) {
          // Already stopped
        }
      }
    }

    return instance;
  }

  /**
   * Play sound using pooled instance
   */
  play(soundName, options = {}) {
    const buffer = this.sounds.get(soundName);
    if (!buffer) {
      console.warn(`Sound not found: ${soundName}`);
      return null;
    }

    const {
      volume = 1,
      playbackRate = 1,
      pan = 0,
      loop = false
    } = options;

    const instance = this.getAvailableInstance();
    const now = this.context.currentTime;

    // Create new source (sources are single-use)
    instance.source = this.context.createBufferSource();
    instance.source.buffer = buffer;
    instance.source.playbackRate.value = playbackRate;
    instance.source.loop = loop;

    // Configure nodes
    instance.gainNode.gain.setValueAtTime(volume * this.sfxVolume, now);
    instance.panNode.pan.setValueAtTime(Math.max(-1, Math.min(1, pan)), now);

    // Connect source to pre-connected chain
    instance.source.connect(instance.gainNode);

    // Mark as in use
    instance.available = false;
    instance.soundName = soundName;
    this.activeInstances.add(instance);

    // Return to pool when finished
    instance.source.onended = () => {
      instance.source.disconnect();
      instance.source = null;
      instance.available = true;
      instance.soundName = null;
      this.activeInstances.delete(instance);
    };

    // Start playback
    instance.source.start(now);

    return {
      instance,
      stop: () => {
        if (instance.source) {
          try {
            instance.source.stop();
          } catch (e) {
            // Already stopped
          }
        }
      },
      setVolume: (vol) => {
        instance.gainNode.gain.setTargetAtTime(
          vol * this.sfxVolume,
          this.context.currentTime,
          0.01
        );
      }
    };
  }

  /**
   * Play with random variation
   */
  playVariation(soundName, options = {}) {
    const pitchRange = options.pitchRange || 0.1;
    const volumeRange = options.volumeRange || 0.1;

    return this.play(soundName, {
      ...options,
      volume: (options.volume || 1) * (1 + (Math.random() * 2 - 1) * volumeRange),
      playbackRate: 1 + (Math.random() * 2 - 1) * pitchRange
    });
  }

  /**
   * Set master SFX volume
   */
  setVolume(volume) {
    this.sfxVolume = Math.max(0, Math.min(1, volume));

    // Update active instances
    const now = this.context.currentTime;
    for (const instance of this.activeInstances) {
      const currentGain = instance.gainNode.gain.value / this.sfxVolume;
      instance.gainNode.gain.setTargetAtTime(
        currentGain * volume,
        now,
        0.01
      );
    }
  }

  /**
   * Stop all sounds
   */
  stopAll() {
    for (const instance of this.activeInstances) {
      if (instance.source) {
        try {
          instance.source.stop();
        } catch (e) {
          // Already stopped
        }
      }
    }
  }

  /**
   * Get pool statistics
   */
  getStats() {
    return {
      poolSize: this.poolSize,
      active: this.activeInstances.size,
      available: this.pool.filter(i => i.available).length
    };
  }
}
```

**Claude Code Prompt:**
```
Create a sound effect pooling system that reuses audio nodes for better
performance. Pre-allocate a pool of gain and panner nodes, create
buffer sources on demand, and automatically return instances to the pool
when sounds finish. Handle pool exhaustion gracefully.
```

## Priority-Based SFX System

When many sounds trigger simultaneously, a priority system ensures important sounds always play while culling less critical ones.

### Priority SFX Manager

```javascript
class PrioritySFXManager extends SoundEffectPool {
  constructor(audioContext, masterGain, poolSize = 20, maxConcurrent = 15) {
    super(audioContext, masterGain, poolSize);
    this.maxConcurrent = maxConcurrent;
    this.priorities = new Map();
    this.playingInstances = [];
  }

  /**
   * Register sound priority
   */
  setPriority(soundName, priority) {
    /*
     * Priority scale:
     * 10 = Critical (player actions, UI feedback)
     * 7-9 = High (important gameplay events)
     * 4-6 = Medium (common gameplay sounds)
     * 1-3 = Low (ambient, distant sounds)
     */
    this.priorities.set(soundName, priority);
  }

  /**
   * Get sound priority
   */
  getPriority(soundName) {
    return this.priorities.get(soundName) || 5; // Default medium priority
  }

  /**
   * Play sound with priority check
   */
  play(soundName, options = {}) {
    const priority = options.priority || this.getPriority(soundName);

    // Check if we've hit concurrent limit
    if (this.playingInstances.length >= this.maxConcurrent) {
      // Find lowest priority sound
      const lowestPriorityInstance = this.playingInstances.reduce((lowest, current) => {
        return current.priority < lowest.priority ? current : lowest;
      });

      // Only play if this sound has higher priority
      if (priority <= lowestPriorityInstance.priority) {
        console.log(`SFX ${soundName} rejected (priority ${priority} too low)`);
        return null;
      }

      // Stop lowest priority sound
      console.log(`Stopping ${lowestPriorityInstance.soundName} (priority ${lowestPriorityInstance.priority}) for ${soundName} (priority ${priority})`);
      lowestPriorityInstance.stop();
    }

    // Play sound using parent class method
    const handle = super.play(soundName, options);

    if (handle) {
      // Track with priority
      const instance = {
        soundName,
        priority,
        handle,
        stop: () => handle.stop()
      };

      this.playingInstances.push(instance);

      // Remove from tracking when finished
      const originalOnEnded = handle.instance.source.onended;
      handle.instance.source.onended = () => {
        const index = this.playingInstances.indexOf(instance);
        if (index > -1) {
          this.playingInstances.splice(index, 1);
        }
        if (originalOnEnded) {
          originalOnEnded();
        }
      };
    }

    return handle;
  }

  /**
   * Play with distance-based priority
   */
  playWithDistance(soundName, distance, maxDistance, options = {}) {
    // Calculate priority based on distance
    const distanceFactor = 1 - Math.min(distance / maxDistance, 1);
    const basePriority = this.getPriority(soundName);
    const adjustedPriority = basePriority * distanceFactor;

    // Calculate volume based on distance
    const volume = (options.volume || 1) * distanceFactor * distanceFactor;

    if (volume < 0.01) {
      return null; // Too quiet, don't play
    }

    return this.play(soundName, {
      ...options,
      volume,
      priority: adjustedPriority
    });
  }
}
```

**Claude Code Prompt:**
```
Create a priority-based sound effect system that limits concurrent sounds
by stopping lower-priority sounds when the limit is reached. Support
configurable priorities per sound type and distance-based priority
adjustments for spatial audio.
```

## Volume Control and Mixing

Professional audio mixing ensures sound effects blend well together and with music.

### Audio Mixer System

```javascript
class AudioMixer {
  constructor(audioContext) {
    this.context = audioContext;
    this.masterGain = audioContext.createGain();
    this.masterGain.connect(audioContext.destination);

    // Create separate channels
    this.channels = {
      music: this.createChannel('music', 0.7),
      sfx: this.createChannel('sfx', 0.8),
      ui: this.createChannel('ui', 0.9),
      ambient: this.createChannel('ambient', 0.5),
      voice: this.createChannel('voice', 1.0)
    };

    // Ducking configuration
    this.duckingActive = false;
    this.duckingAmount = 0.3; // How much to reduce music/ambient
  }

  /**
   * Create audio channel with gain control
   */
  createChannel(name, defaultVolume = 1.0) {
    const gain = this.context.createGain();
    gain.gain.value = defaultVolume;
    gain.connect(this.masterGain);

    return {
      name,
      gain,
      volume: defaultVolume,
      muted: false
    };
  }

  /**
   * Set channel volume
   */
  setChannelVolume(channelName, volume, fadeTime = 0.1) {
    const channel = this.channels[channelName];
    if (!channel) return;

    channel.volume = Math.max(0, Math.min(1, volume));

    if (channel.muted) return;

    const now = this.context.currentTime;
    channel.gain.gain.cancelScheduledValues(now);
    channel.gain.gain.setValueAtTime(channel.gain.gain.value, now);
    channel.gain.gain.linearRampToValueAtTime(
      channel.volume,
      now + fadeTime
    );
  }

  /**
   * Mute/unmute channel
   */
  setChannelMute(channelName, muted, fadeTime = 0.1) {
    const channel = this.channels[channelName];
    if (!channel) return;

    channel.muted = muted;
    const targetVolume = muted ? 0 : channel.volume;

    const now = this.context.currentTime;
    channel.gain.gain.cancelScheduledValues(now);
    channel.gain.gain.setValueAtTime(channel.gain.gain.value, now);
    channel.gain.gain.linearRampToValueAtTime(targetVolume, now + fadeTime);
  }

  /**
   * Duck music/ambient during dialogue or important sounds
   */
  enableDucking(duration = null) {
    if (this.duckingActive) return;

    this.duckingActive = true;
    const now = this.context.currentTime;
    const fadeTime = 0.3;

    // Duck music and ambient
    const musicGain = this.channels.music.gain.gain;
    const ambientGain = this.channels.ambient.gain.gain;

    musicGain.cancelScheduledValues(now);
    musicGain.setValueAtTime(musicGain.value, now);
    musicGain.linearRampToValueAtTime(
      this.channels.music.volume * this.duckingAmount,
      now + fadeTime
    );

    ambientGain.cancelScheduledValues(now);
    ambientGain.setValueAtTime(ambientGain.value, now);
    ambientGain.linearRampToValueAtTime(
      this.channels.ambient.volume * this.duckingAmount,
      now + fadeTime
    );

    // Auto-disable ducking after duration
    if (duration !== null) {
      setTimeout(() => {
        this.disableDucking();
      }, duration * 1000);
    }
  }

  /**
   * Restore normal volume after ducking
   */
  disableDucking() {
    if (!this.duckingActive) return;

    this.duckingActive = false;
    const now = this.context.currentTime;
    const fadeTime = 0.5;

    // Restore music and ambient
    const musicGain = this.channels.music.gain.gain;
    const ambientGain = this.channels.ambient.gain.gain;

    musicGain.cancelScheduledValues(now);
    musicGain.setValueAtTime(musicGain.value, now);
    musicGain.linearRampToValueAtTime(
      this.channels.music.volume,
      now + fadeTime
    );

    ambientGain.cancelScheduledValues(now);
    ambientGain.setValueAtTime(ambientGain.value, now);
    ambientGain.linearRampToValueAtTime(
      this.channels.ambient.volume,
      now + fadeTime
    );
  }

  /**
   * Set master volume
   */
  setMasterVolume(volume, fadeTime = 0.1) {
    const now = this.context.currentTime;
    this.masterGain.gain.cancelScheduledValues(now);
    this.masterGain.gain.setValueAtTime(this.masterGain.gain.value, now);
    this.masterGain.gain.linearRampToValueAtTime(
      Math.max(0, Math.min(1, volume)),
      now + fadeTime
    );
  }

  /**
   * Get channel gain node for connecting audio
   */
  getChannel(channelName) {
    return this.channels[channelName]?.gain;
  }
}

// Usage example
const mixer = new AudioMixer(audioContext);

// Create SFX player connected to SFX channel
const sfxPlayer = new SoundEffectPool(
  audioContext,
  mixer.getChannel('sfx')
);

// Create music player connected to music channel
const musicPlayer = new MusicPlayer(
  audioContext,
  mixer.getChannel('music')
);

// Adjust volumes
mixer.setChannelVolume('music', 0.6);
mixer.setChannelVolume('sfx', 0.8);

// Duck music during dialogue
mixer.enableDucking(5.0); // Duck for 5 seconds
```

**Claude Code Prompt:**
```
Create an audio mixer system with separate channels for music, SFX, UI,
ambient, and voice. Support individual channel volume control, muting,
and automatic ducking of music/ambient during dialogue or important sounds.
Use smooth volume transitions.
```

## One-Shot vs Looping Sounds

Different sound types require different handling strategies.

### Specialized Sound Handlers

```javascript
class SpecializedSFXSystem {
  constructor(sfxPool) {
    this.pool = sfxPool;
    this.loopingSounds = new Map();
    this.footstepTimer = null;
  }

  /**
   * Play one-shot sound (most SFX)
   */
  playOneShot(soundName, options = {}) {
    return this.pool.play(soundName, {
      ...options,
      loop: false
    });
  }

  /**
   * Start looping sound (engines, ambient loops)
   */
  startLoop(soundName, loopId, options = {}) {
    // Stop existing loop with this ID
    this.stopLoop(loopId);

    const handle = this.pool.play(soundName, {
      ...options,
      loop: true
    });

    if (handle) {
      this.loopingSounds.set(loopId, handle);
    }

    return handle;
  }

  /**
   * Stop looping sound
   */
  stopLoop(loopId, fadeOut = 0.3) {
    const handle = this.loopingSounds.get(loopId);
    if (!handle) return;

    if (fadeOut > 0) {
      const now = this.pool.context.currentTime;
      handle.instance.gainNode.gain.cancelScheduledValues(now);
      handle.instance.gainNode.gain.setValueAtTime(
        handle.instance.gainNode.gain.value,
        now
      );
      handle.instance.gainNode.gain.linearRampToValueAtTime(0, now + fadeOut);

      setTimeout(() => {
        handle.stop();
        this.loopingSounds.delete(loopId);
      }, fadeOut * 1000);
    } else {
      handle.stop();
      this.loopingSounds.delete(loopId);
    }
  }

  /**
   * Update loop volume (e.g., engine sound based on RPM)
   */
  updateLoopVolume(loopId, volume) {
    const handle = this.loopingSounds.get(loopId);
    if (handle) {
      handle.setVolume(volume);
    }
  }

  /**
   * Footstep system with automatic timing
   */
  startFootsteps(soundName, stepsPerSecond = 2) {
    this.stopFootsteps();

    const interval = 1000 / stepsPerSecond;

    this.footstepTimer = setInterval(() => {
      this.pool.playVariation(soundName, {
        pitchRange: 0.15,
        volumeRange: 0.1
      });
    }, interval);
  }

  /**
   * Stop footsteps
   */
  stopFootsteps() {
    if (this.footstepTimer) {
      clearInterval(this.footstepTimer);
      this.footstepTimer = null;
    }
  }

  /**
   * Play impact sound with intensity
   */
  playImpact(soundName, velocity) {
    // Map velocity to volume (0-1 range expected)
    const volume = Math.min(velocity / 10, 1);

    if (volume < 0.1) {
      return null; // Too soft, don't play
    }

    return this.pool.play(soundName, {
      volume,
      pitchRange: 0.1
    });
  }
}
```

**Claude Code Prompt:**
```
Create specialized sound effect handlers for different sound types: one-shot
sounds (explosions, impacts), looping sounds (engines, ambient), footsteps
with automatic timing, and velocity-based impact sounds. Include volume
and pitch variation.
```

## Performance Considerations

1. **Pool size should match peak concurrent sounds** - Monitor active count
2. **Prioritize critical sounds** - Player actions over distant ambient
3. **Limit total concurrent sounds** - 20-30 maximum for most games
4. **Use short audio buffers** - Most SFX should be under 2 seconds
5. **Compress audio appropriately** - Balance quality vs file size
6. **Implement spatial culling** - Don't play distant/off-screen sounds
7. **Reuse audio nodes through pooling** - Avoid creating nodes in loops
8. **Monitor memory usage** - Unload unused sound effects
9. **Test on mobile devices** - Lower limits, different audio behavior
10. **Profile audio performance** - Use DevTools to identify bottlenecks

## Best Practices

1. **Provide volume controls for SFX** - Separate from music volume
2. **Add subtle variations** - Pitch/volume randomization prevents repetition
3. **Mix carefully** - Don't let SFX overpower music or dialogue
4. **Consider accessibility** - Provide visual alternatives to audio cues
5. **Test sound balance** - On different playback devices
6. **Implement ducking** - Lower music during important sounds
7. **Use appropriate formats** - OGG for most sounds, WAV for ultra-short
8. **Add audio feedback to all interactions** - Buttons, pickups, impacts
9. **Layer impact sounds** - Combine low and high frequency elements
10. **Normalize volume levels** - Consistent loudness across all SFX

## Cross-References

- [Web Audio API](./web-audio-api.md) - Audio node fundamentals
- [Music Systems](./music-systems.md) - Music integration and ducking
- [Audio Optimization](./audio-optimization.md) - Advanced optimization
- [UI/UX](../07-ui-ux/README.md) - UI sound feedback

## Summary

Professional sound effect systems require careful performance optimization and mixing strategies. Master these techniques:

- Object pooling for efficient node reuse
- Priority systems for managing concurrent sounds
- Audio mixing with separate channels
- Specialized handlers for different sound types
- Volume control and ducking
- Variation to prevent repetition

These systems create responsive, satisfying audio feedback that makes games feel polished and professional. Claude Code helps implement sophisticated SFX systems efficiently, ensuring your game sounds as good as it plays.
