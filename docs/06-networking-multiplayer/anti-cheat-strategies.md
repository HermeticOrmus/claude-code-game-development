# Anti-Cheat Strategies

## Overview

Anti-cheat systems protect multiplayer games from exploitation. Since client code is fully accessible to players, any trust placed in clients will be exploited. This guide covers server validation, input verification, common exploits and their prevention, and production-ready anti-cheat implementations.

## Server-Side Validation

The golden rule: **never trust the client**. All game logic must be validated server-side.

### Comprehensive Server Validator

```javascript
class ServerSideValidator {
  constructor(gameServer) {
    this.server = gameServer;
    this.validationRules = this.defineRules();
    this.violations = new Map();
  }

  /**
   * Define validation rules
   */
  defineRules() {
    return {
      movement: {
        maxSpeed: 10, // units per tick
        maxAcceleration: 2
      },
      combat: {
        minShotInterval: 500, // milliseconds
        maxDamage: 100,
        maxRange: 500
      },
      input: {
        maxRate: 60, // inputs per second
        maxQueueSize: 10
      }
    };
  }

  /**
   * Validate player movement
   */
  validateMovement(playerId, oldPos, newPos, deltaTime) {
    const dx = newPos.x - oldPos.x;
    const dy = newPos.y - oldPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const speed = distance / deltaTime;

    if (speed > this.validationRules.movement.maxSpeed) {
      this.flagViolation(playerId, 'speed_hack', {
        speed: speed.toFixed(2),
        maxSpeed: this.validationRules.movement.maxSpeed,
        distance,
        deltaTime
      });
      return false;
    }

    return true;
  }

  /**
   * Validate shot/attack
   */
  validateShot(playerId, targetId, damage) {
    const player = this.server.players.get(playerId);
    const target = this.server.players.get(targetId);

    if (!player || !target) return false;

    // Check shot interval
    const now = Date.now();
    if (now - player.lastShotTime < this.validationRules.combat.minShotInterval) {
      this.flagViolation(playerId, 'rapid_fire', {
        interval: now - player.lastShotTime,
        minInterval: this.validationRules.combat.minShotInterval
      });
      return false;
    }

    // Check damage value
    if (damage > this.validationRules.combat.maxDamage) {
      this.flagViolation(playerId, 'damage_hack', {
        damage,
        maxDamage: this.validationRules.combat.maxDamage
      });
      return false;
    }

    // Check range
    const dx = target.x - player.x;
    const dy = target.y - player.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance > this.validationRules.combat.maxRange) {
      this.flagViolation(playerId, 'range_hack', {
        distance: distance.toFixed(2),
        maxRange: this.validationRules.combat.maxRange
      });
      return false;
    }

    // Check line of sight (simplified)
    if (!this.hasLineOfSight(player, target)) {
      this.flagViolation(playerId, 'wallhack', {
        from: { x: player.x, y: player.y },
        to: { x: target.x, y: target.y }
      });
      return false;
    }

    player.lastShotTime = now;
    return true;
  }

  /**
   * Validate input rate
   */
  validateInputRate(playerId) {
    const now = Date.now();
    const player = this.server.players.get(playerId);

    if (!player.inputTimestamps) {
      player.inputTimestamps = [];
    }

    // Remove old timestamps
    player.inputTimestamps = player.inputTimestamps.filter(
      t => now - t < 1000
    );

    // Check rate
    if (player.inputTimestamps.length >= this.validationRules.input.maxRate) {
      this.flagViolation(playerId, 'input_spam', {
        rate: player.inputTimestamps.length,
        maxRate: this.validationRules.input.maxRate
      });
      return false;
    }

    player.inputTimestamps.push(now);
    return true;
  }

  /**
   * Check line of sight (simplified)
   */
  hasLineOfSight(player, target) {
    // Implement ray casting against world geometry
    // This is simplified - real implementation needs collision detection
    return true;
  }

  /**
   * Flag validation violation
   */
  flagViolation(playerId, violationType, details) {
    const key = `${playerId}_${violationType}`;
    const count = (this.violations.get(key) || 0) + 1;
    this.violations.set(key, count);

    console.warn(`Violation from ${playerId}: ${violationType}`, details);

    // Take action after threshold
    if (count >= 5) {
      this.takeAction(playerId, violationType, count);
    }
  }

  /**
   * Take action against cheater
   */
  takeAction(playerId, violationType, count) {
    console.log(`Taking action against ${playerId} for ${violationType} (${count} violations)`);

    const player = this.server.players.get(playerId);
    if (!player) return;

    // Kick player
    if (player.connection) {
      player.connection.send(JSON.stringify({
        type: 'kicked',
        reason: violationType,
        details: `Multiple violations detected (${count})`
      }));

      player.connection.close();
    }

    this.server.players.delete(playerId);

    // Log to database (implement based on your backend)
    this.logBan(playerId, violationType, count);
  }

  /**
   * Log ban to persistent storage
   */
  logBan(playerId, reason, violationCount) {
    // Implementation depends on your backend
    console.log(`BAN LOGGED: Player ${playerId} - ${reason} (${violationCount} violations)`);
  }

  /**
   * Get player violation statistics
   */
  getPlayerViolations(playerId) {
    const violations = {};

    for (const [key, count] of this.violations) {
      if (key.startsWith(playerId)) {
        const type = key.substring(playerId.length + 1);
        violations[type] = count;
      }
    }

    return violations;
  }
}
```

**Claude Code Prompt:**
```
Create a comprehensive server-side anti-cheat validator that checks movement
speed, combat actions, input rates, and line of sight. Flag violations,
accumulate evidence, and take action against repeat offenders.
```

## Input Verification

Verify all inputs are possible and reasonable.

### Input Validation System

```javascript
class InputVerifier {
  constructor() {
    this.lastInputs = new Map();
  }

  /**
   * Verify input is valid
   */
  verifyInput(playerId, input) {
    // Check timestamp
    if (!this.verifyTimestamp(input.timestamp)) {
      return { valid: false, reason: 'invalid_timestamp' };
    }

    // Check sequence number
    if (!this.verifySequence(playerId, input.sequence)) {
      return { valid: false, reason: 'invalid_sequence' };
    }

    // Check input format
    if (!this.verifyFormat(input)) {
      return { valid: false, reason: 'invalid_format' };
    }

    // Check input values
    if (!this.verifyValues(input)) {
      return { valid: false, reason: 'invalid_values' };
    }

    // Store for sequence checking
    this.lastInputs.set(playerId, input);

    return { valid: true };
  }

  /**
   * Verify timestamp is recent
   */
  verifyTimestamp(timestamp) {
    const now = Date.now();
    const age = now - timestamp;

    // Allow 1 second in past, 100ms in future (clock skew)
    return age >= -100 && age <= 1000;
  }

  /**
   * Verify sequence number
   */
  verifySequence(playerId, sequence) {
    const lastInput = this.lastInputs.get(playerId);

    if (!lastInput) return true; // First input

    // Sequence must increment
    return sequence > lastInput.sequence;
  }

  /**
   * Verify input format
   */
  verifyFormat(input) {
    if (!input || typeof input !== 'object') return false;

    if (input.keys && typeof input.keys !== 'object') return false;

    if (input.mouse) {
      if (typeof input.mouse.x !== 'number') return false;
      if (typeof input.mouse.y !== 'number') return false;
    }

    return true;
  }

  /**
   * Verify input values are reasonable
   */
  verifyValues(input) {
    if (input.mouse) {
      // Check coordinates are within reasonable bounds
      if (Math.abs(input.mouse.x) > 100000) return false;
      if (Math.abs(input.mouse.y) > 100000) return false;
    }

    if (input.keys) {
      // Check all values are booleans
      for (const value of Object.values(input.keys)) {
        if (typeof value !== 'boolean') return false;
      }
    }

    return true;
  }
}
```

**Claude Code Prompt:**
```
Create an input verification system that validates timestamps, sequence numbers,
input format, and value ranges. Reject malformed or suspicious inputs before
processing.
```

## Common Exploits and Prevention

### Exploit Prevention Strategies

```javascript
class ExploitPrevention {
  /**
   * Prevent wallhacks by not sending hidden information
   */
  filterVisibleEntities(player, allEntities) {
    const visible = [];

    for (const entity of allEntities) {
      // Check if entity is in player's view range
      const dx = entity.x - player.x;
      const dy = entity.y - player.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance <= player.viewRange) {
        // Additional check: line of sight
        if (this.hasLineOfSight(player, entity)) {
          visible.push(entity);
        }
      }
    }

    return visible;
  }

  /**
   * Prevent aimbots by adding subtle randomness
   */
  applySpreadToShot(shot) {
    const spread = 0.02; // radians

    shot.angle += (Math.random() - 0.5) * spread;

    return shot;
  }

  /**
   * Prevent replay attacks
   */
  preventReplayAttacks(input, processedInputs) {
    // Check if this exact input was already processed
    const hash = this.hashInput(input);

    if (processedInputs.has(hash)) {
      return false; // Replay attack detected
    }

    processedInputs.add(hash);

    // Clean old hashes (keep last 1000)
    if (processedInputs.size > 1000) {
      const oldest = processedInputs.values().next().value;
      processedInputs.delete(oldest);
    }

    return true;
  }

  /**
   * Hash input for replay detection
   */
  hashInput(input) {
    return `${input.sequence}_${input.timestamp}_${JSON.stringify(input.keys)}`;
  }

  /**
   * Detect and prevent resource hacks
   */
  validateResourceChange(playerId, resource, oldValue, newValue) {
    const change = newValue - oldValue;

    // Resources should only increase through valid game actions
    // Never trust client-reported resource values

    console.warn(`Client ${playerId} attempted resource change: ${oldValue} -> ${newValue}`);

    return false; // Reject client-side resource changes
  }
}
```

**Claude Code Prompt:**
```
Create exploit prevention strategies for common multiplayer cheats: wallhacks
(filter invisible entities), aimbots (add spread), replay attacks (hash
tracking), and resource hacks (server-side resource management).
```

## Monitoring and Detection

### Cheat Detection System

```javascript
class CheatDetectionSystem {
  constructor() {
    this.playerStats = new Map();
    this.suspiciousThresholds = {
      accuracy: 0.95, // 95% hit rate is suspicious
      headshotRatio: 0.8, // 80% headshots is suspicious
      reactionTime: 50 // < 50ms reaction is suspicious
    };
  }

  /**
   * Track player statistics
   */
  trackShot(playerId, hit, headshot = false) {
    const stats = this.getStats(playerId);

    stats.totalShots++;
    if (hit) stats.hits++;
    if (headshot) stats.headshots++;

    this.analyzeStats(playerId, stats);
  }

  /**
   * Track reaction time
   */
  trackReaction(playerId, reactionTime) {
    const stats = this.getStats(playerId);

    stats.reactionTimes.push(reactionTime);

    // Keep last 100
    if (stats.reactionTimes.length > 100) {
      stats.reactionTimes.shift();
    }

    this.analyzeStats(playerId, stats);
  }

  /**
   * Analyze statistics for cheating patterns
   */
  analyzeStats(playerId, stats) {
    // Check accuracy
    if (stats.totalShots > 50) {
      const accuracy = stats.hits / stats.totalShots;

      if (accuracy > this.suspiciousThresholds.accuracy) {
        this.flagSuspicious(playerId, 'high_accuracy', {
          accuracy: (accuracy * 100).toFixed(1) + '%',
          shots: stats.totalShots
        });
      }
    }

    // Check headshot ratio
    if (stats.hits > 20) {
      const headshotRatio = stats.headshots / stats.hits;

      if (headshotRatio > this.suspiciousThresholds.headshotRatio) {
        this.flagSuspicious(playerId, 'high_headshot_ratio', {
          ratio: (headshotRatio * 100).toFixed(1) + '%',
          headshots: stats.headshots,
          hits: stats.hits
        });
      }
    }

    // Check reaction time
    if (stats.reactionTimes.length > 20) {
      const avgReaction = stats.reactionTimes.reduce((a, b) => a + b) / stats.reactionTimes.length;

      if (avgReaction < this.suspiciousThresholds.reactionTime) {
        this.flagSuspicious(playerId, 'inhuman_reactions', {
          avgReaction: avgReaction.toFixed(0) + 'ms',
          threshold: this.suspiciousThresholds.reactionTime + 'ms'
        });
      }
    }
  }

  /**
   * Get or create player statistics
   */
  getStats(playerId) {
    if (!this.playerStats.has(playerId)) {
      this.playerStats.set(playerId, {
        totalShots: 0,
        hits: 0,
        headshots: 0,
        reactionTimes: [],
        flags: []
      });
    }

    return this.playerStats.get(playerId);
  }

  /**
   * Flag suspicious behavior
   */
  flagSuspicious(playerId, reason, details) {
    const stats = this.getStats(playerId);

    stats.flags.push({
      reason,
      details,
      timestamp: Date.now()
    });

    console.warn(`Suspicious behavior from ${playerId}: ${reason}`, details);

    // Review if multiple flags
    if (stats.flags.length >= 3) {
      this.reviewPlayer(playerId);
    }
  }

  /**
   * Review player for potential cheating
   */
  reviewPlayer(playerId) {
    const stats = this.getStats(playerId);

    console.log(`Reviewing player ${playerId} for potential cheating`);
    console.log(`Flags: ${stats.flags.length}`);
    console.log(`Stats:`, {
      accuracy: ((stats.hits / stats.totalShots) * 100).toFixed(1) + '%',
      headshotRatio: ((stats.headshots / stats.hits) * 100).toFixed(1) + '%',
      avgReaction: (stats.reactionTimes.reduce((a, b) => a + b) / stats.reactionTimes.length).toFixed(0) + 'ms'
    });

    // Take action based on flags
    // Could be automatic ban, manual review queue, etc.
  }
}
```

**Claude Code Prompt:**
```
Create a cheat detection system that monitors player statistics (accuracy,
reaction time, headshot ratio), identifies suspicious patterns, and flags
players for review. Track trends over time to distinguish cheaters from
skilled players.
```

## Best Practices

1. **Server is authoritative** - Never trust client data
2. **Validate everything** - Movement, combat, resources, all actions
3. **Monitor statistics** - Detect impossible performance
4. **Rate limit actions** - Prevent input spam
5. **Don't send hidden information** - Prevents wallhacks
6. **Add subtle randomness** - Makes aimbots less effective
7. **Log suspicious activity** - Evidence for bans
8. **Use sequence numbers** - Prevent replay attacks
9. **Implement reporting** - Let players report cheaters
10. **Regular updates** - Stay ahead of new exploits

## Cross-References

- [Client-Server Architecture](./client-server-architecture.md) - Server authority
- [WebSocket Implementation](./websocket-implementation.md) - Secure communication
- [State Synchronization](./state-synchronization.md) - Proper state management

## Summary

Anti-cheat systems protect multiplayer game integrity. Master these strategies:

- Server-side validation of all game actions
- Input verification and rate limiting
- Statistical analysis for cheat detection
- Exploit prevention strategies
- Monitoring and logging systems

No anti-cheat is perfect, but these techniques create significant barriers to cheating while maintaining fair play. Claude Code helps implement robust anti-cheat systems efficiently, protecting your multiplayer game's competitive integrity.
