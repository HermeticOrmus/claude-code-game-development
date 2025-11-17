# Client-Server Architecture

## Overview

Client-server architecture is the foundation of secure, fair multiplayer games. Unlike peer-to-peer systems where clients communicate directly, client-server architecture places an authoritative server between all clients. The server validates all actions, maintains the canonical game state, and prevents cheating by never trusting client input.

Understanding proper client-server separation is crucial for building competitive multiplayer games. This guide covers authoritative server patterns, client-server communication strategies, security considerations, and complete implementations for different game types.

## Authoritative Server Pattern

The authoritative server pattern makes the server the single source of truth for all game state. Clients send inputs to the server, the server processes them, updates the authoritative state, and broadcasts results back to clients.

### Basic Authoritative Server

```javascript
// Server-side game state
class AuthoritativeGameServer {
  constructor() {
    this.gameState = {
      tick: 0,
      players: new Map(),
      entities: new Map(),
      startTime: Date.now()
    };

    this.tickRate = 20; // 20 updates per second
    this.tickInterval = 1000 / this.tickRate;
    this.gameLoop = null;
  }

  /**
   * Start game loop
   */
  start() {
    console.log(`Starting game loop at ${this.tickRate} ticks/second`);

    this.gameLoop = setInterval(() => {
      this.tick();
    }, this.tickInterval);
  }

  /**
   * Main game tick
   */
  tick() {
    const startTime = Date.now();

    // Increment tick counter
    this.gameState.tick++;

    // Process pending inputs from all players
    this.processInputs();

    // Update game physics and logic
    this.updateGameState();

    // Detect collisions
    this.detectCollisions();

    // Broadcast state to clients
    this.broadcastGameState();

    // Performance monitoring
    const tickTime = Date.now() - startTime;
    if (tickTime > this.tickInterval * 0.8) {
      console.warn(`Slow tick: ${tickTime}ms (${this.tickInterval}ms budget)`);
    }
  }

  /**
   * Process player inputs
   */
  processInputs() {
    for (const [playerId, player] of this.gameState.players) {
      if (player.pendingInputs.length === 0) continue;

      // Process all pending inputs for this player
      while (player.pendingInputs.length > 0) {
        const input = player.pendingInputs.shift();

        // Validate input
        if (!this.validateInput(playerId, input)) {
          console.warn(`Invalid input from player ${playerId}`);
          continue;
        }

        // Apply input to player
        this.applyInput(playerId, input);
      }
    }
  }

  /**
   * Validate player input (server-side security)
   */
  validateInput(playerId, input) {
    const player = this.gameState.players.get(playerId);
    if (!player) return false;

    // Check timestamp is recent
    const age = Date.now() - input.timestamp;
    if (age > 1000 || age < -100) {
      return false; // Input too old or from future
    }

    // Validate input values
    if (input.keys) {
      // Ensure keys is an object with boolean values
      if (typeof input.keys !== 'object') return false;
      for (const value of Object.values(input.keys)) {
        if (typeof value !== 'boolean') return false;
      }
    }

    // Validate mouse coordinates if present
    if (input.mouse) {
      if (typeof input.mouse.x !== 'number' || typeof input.mouse.y !== 'number') {
        return false;
      }

      // Check coordinates are within reasonable bounds
      if (Math.abs(input.mouse.x) > 10000 || Math.abs(input.mouse.y) > 10000) {
        return false;
      }
    }

    return true;
  }

  /**
   * Apply validated input to player
   */
  applyInput(playerId, input) {
    const player = this.gameState.players.get(playerId);
    if (!player) return;

    const moveSpeed = 5;

    // Process movement keys
    if (input.keys) {
      if (input.keys.w || input.keys.ArrowUp) player.vy = -moveSpeed;
      if (input.keys.s || input.keys.ArrowDown) player.vy = moveSpeed;
      if (input.keys.a || input.keys.ArrowLeft) player.vx = -moveSpeed;
      if (input.keys.d || input.keys.ArrowRight) player.vx = moveSpeed;
    }

    // Process mouse input
    if (input.mouse) {
      const dx = input.mouse.x - player.x;
      const dy = input.mouse.y - player.y;
      player.rotation = Math.atan2(dy, dx);
    }

    // Process actions
    if (input.action === 'shoot') {
      this.handleShoot(playerId);
    }

    // Store last processed input sequence for client reconciliation
    player.lastProcessedInput = input.sequence;
  }

  /**
   * Update game state physics
   */
  updateGameState() {
    const dt = this.tickInterval / 1000;

    // Update all players
    for (const player of this.gameState.players.values()) {
      // Apply velocity
      player.x += player.vx * dt;
      player.y += player.vy * dt;

      // Apply friction
      player.vx *= 0.9;
      player.vy *= 0.9;

      // Clamp to world bounds
      player.x = Math.max(0, Math.min(player.x, 1000));
      player.y = Math.max(0, Math.min(player.y, 1000));
    }

    // Update all entities (projectiles, etc.)
    for (const entity of this.gameState.entities.values()) {
      entity.x += entity.vx * dt;
      entity.y += entity.vy * dt;

      // Remove out-of-bounds entities
      if (entity.x < -100 || entity.x > 1100 || entity.y < -100 || entity.y > 1100) {
        this.gameState.entities.delete(entity.id);
      }
    }
  }

  /**
   * Detect and handle collisions
   */
  detectCollisions() {
    // Check projectile-player collisions
    for (const projectile of this.gameState.entities.values()) {
      if (projectile.type !== 'projectile') continue;

      for (const player of this.gameState.players.values()) {
        // Skip owner
        if (player.id === projectile.ownerId) continue;

        // Check collision
        const dx = player.x - projectile.x;
        const dy = player.y - projectile.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < player.radius + projectile.radius) {
          // Hit!
          player.health -= projectile.damage;
          this.gameState.entities.delete(projectile.id);

          console.log(`Player ${player.id} hit! Health: ${player.health}`);

          // Check for death
          if (player.health <= 0) {
            this.handlePlayerDeath(player.id);
          }
        }
      }
    }
  }

  /**
   * Broadcast game state to all clients
   */
  broadcastGameState() {
    const stateUpdate = {
      type: 'game_state',
      tick: this.gameState.tick,
      timestamp: Date.now(),
      players: this.serializePlayers(),
      entities: this.serializeEntities()
    };

    // Send to all connected clients
    for (const player of this.gameState.players.values()) {
      if (player.connection) {
        // Include last processed input for this specific client
        const clientUpdate = {
          ...stateUpdate,
          lastProcessedInput: player.lastProcessedInput
        };

        player.connection.send(JSON.stringify(clientUpdate));
      }
    }
  }

  /**
   * Serialize players for network transmission
   */
  serializePlayers() {
    return Array.from(this.gameState.players.values()).map(player => ({
      id: player.id,
      name: player.name,
      x: Math.round(player.x * 100) / 100, // Round to 2 decimal places
      y: Math.round(player.y * 100) / 100,
      rotation: Math.round(player.rotation * 100) / 100,
      health: player.health
    }));
  }

  /**
   * Serialize entities for network transmission
   */
  serializeEntities() {
    return Array.from(this.gameState.entities.values()).map(entity => ({
      id: entity.id,
      type: entity.type,
      x: Math.round(entity.x * 100) / 100,
      y: Math.round(entity.y * 100) / 100,
      rotation: Math.round(entity.rotation * 100) / 100
    }));
  }

  /**
   * Handle shoot action
   */
  handleShoot(playerId) {
    const player = this.gameState.players.get(playerId);
    if (!player) return;

    // Check cooldown
    if (Date.now() - player.lastShootTime < 500) {
      return; // Too soon
    }

    player.lastShootTime = Date.now();

    // Create projectile
    const projectile = {
      id: `projectile_${Date.now()}_${Math.random()}`,
      type: 'projectile',
      ownerId: playerId,
      x: player.x,
      y: player.y,
      vx: Math.cos(player.rotation) * 500,
      vy: Math.sin(player.rotation) * 500,
      rotation: player.rotation,
      damage: 10,
      radius: 5
    };

    this.gameState.entities.set(projectile.id, projectile);
  }

  /**
   * Handle player death
   */
  handlePlayerDeath(playerId) {
    const player = this.gameState.players.get(playerId);
    if (!player) return;

    console.log(`Player ${playerId} died`);

    // Respawn after delay
    setTimeout(() => {
      if (this.gameState.players.has(playerId)) {
        const player = this.gameState.players.get(playerId);
        player.health = 100;
        player.x = Math.random() * 1000;
        player.y = Math.random() * 1000;
        console.log(`Player ${playerId} respawned`);
      }
    }, 3000);
  }

  /**
   * Add player to game
   */
  addPlayer(playerId, playerName, connection) {
    const player = {
      id: playerId,
      name: playerName,
      x: Math.random() * 1000,
      y: Math.random() * 1000,
      vx: 0,
      vy: 0,
      rotation: 0,
      health: 100,
      radius: 20,
      lastShootTime: 0,
      pendingInputs: [],
      lastProcessedInput: 0,
      connection
    };

    this.gameState.players.set(playerId, player);
    console.log(`Player ${playerId} (${playerName}) joined`);

    return player;
  }

  /**
   * Remove player from game
   */
  removePlayer(playerId) {
    this.gameState.players.delete(playerId);
    console.log(`Player ${playerId} left`);
  }

  /**
   * Queue player input for processing
   */
  queueInput(playerId, input) {
    const player = this.gameState.players.get(playerId);
    if (!player) return;

    player.pendingInputs.push(input);
  }

  /**
   * Stop game loop
   */
  stop() {
    if (this.gameLoop) {
      clearInterval(this.gameLoop);
      this.gameLoop = null;
    }
  }
}
```

**Claude Code Prompt:**
```
Create an authoritative game server that maintains canonical game state,
processes and validates player inputs, simulates game physics, detects
collisions, and broadcasts state updates to clients. Include input validation
and anti-cheat measures.
```

## Client-Side Architecture

Clients maintain a predicted local state while waiting for authoritative server updates.

### Client Game State Manager

```javascript
class ClientGameManager {
  constructor(webSocketClient) {
    this.ws = webSocketClient;
    this.clientState = {
      players: new Map(),
      entities: new Map(),
      localPlayer: null,
      inputSequence: 0,
      pendingInputs: []
    };

    this.setupMessageHandlers();
  }

  /**
   * Setup WebSocket message handlers
   */
  setupMessageHandlers() {
    this.ws.on('game_state', (message) => {
      this.handleServerState(message);
    });
  }

  /**
   * Handle server state update
   */
  handleServerState(serverState) {
    // Update remote players (just copy server state)
    for (const serverPlayer of serverState.players) {
      if (serverPlayer.id !== this.clientState.localPlayer?.id) {
        this.clientState.players.set(serverPlayer.id, serverPlayer);
      }
    }

    // Update local player with reconciliation
    if (this.clientState.localPlayer) {
      this.reconcileLocalPlayer(serverState);
    }

    // Update entities
    this.clientState.entities.clear();
    for (const entity of serverState.entities) {
      this.clientState.entities.set(entity.id, entity);
    }
  }

  /**
   * Reconcile local player state with server
   */
  reconcileLocalPlayer(serverState) {
    const serverPlayer = serverState.players.find(
      p => p.id === this.clientState.localPlayer.id
    );

    if (!serverPlayer) return;

    // Find which inputs the server has processed
    const lastProcessedInput = serverState.lastProcessedInput || 0;

    // Remove processed inputs from pending list
    this.clientState.pendingInputs = this.clientState.pendingInputs.filter(
      input => input.sequence > lastProcessedInput
    );

    // Start from server's authoritative state
    this.clientState.localPlayer.x = serverPlayer.x;
    this.clientState.localPlayer.y = serverPlayer.y;
    this.clientState.localPlayer.health = serverPlayer.health;

    // Re-apply pending inputs (client-side prediction)
    for (const input of this.clientState.pendingInputs) {
      this.applyInputLocally(input);
    }
  }

  /**
   * Send input to server and apply locally
   */
  processInput(input) {
    // Add sequence number
    this.clientState.inputSequence++;
    input.sequence = this.clientState.inputSequence;
    input.timestamp = Date.now();

    // Send to server
    this.ws.send('player_input', input);

    // Apply locally for immediate feedback
    this.applyInputLocally(input);

    // Store for reconciliation
    this.clientState.pendingInputs.push(input);

    // Limit pending inputs (prevent memory growth)
    if (this.clientState.pendingInputs.length > 100) {
      this.clientState.pendingInputs.shift();
    }
  }

  /**
   * Apply input locally (client-side prediction)
   */
  applyInputLocally(input) {
    const player = this.clientState.localPlayer;
    if (!player) return;

    const moveSpeed = 5;
    const dt = 1 / 20; // Assume 20 ticks/second

    // Apply movement
    if (input.keys) {
      if (input.keys.w) player.y -= moveSpeed * dt;
      if (input.keys.s) player.y += moveSpeed * dt;
      if (input.keys.a) player.x -= moveSpeed * dt;
      if (input.keys.d) player.x += moveSpeed * dt;
    }

    // Apply rotation
    if (input.mouse) {
      const dx = input.mouse.x - player.x;
      const dy = input.mouse.y - player.y;
      player.rotation = Math.atan2(dy, dx);
    }

    // Clamp to bounds
    player.x = Math.max(0, Math.min(player.x, 1000));
    player.y = Math.max(0, Math.min(player.y, 1000));
  }

  /**
   * Get current game state for rendering
   */
  getState() {
    return this.clientState;
  }
}
```

**Claude Code Prompt:**
```
Create a client-side game state manager that handles server state updates,
implements client-side prediction for local player, reconciles predicted
state with authoritative server state, and manages pending inputs for
smooth, responsive gameplay.
```

## Security Considerations

Never trust the client. All security must be server-side.

### Server-Side Validation System

```javascript
class ServerSecurityValidator {
  constructor(gameServer) {
    this.server = gameServer;
    this.playerStats = new Map(); // Track player behavior
    this.suspiciousActions = new Map();
  }

  /**
   * Validate player position (teleport detection)
   */
  validatePosition(playerId, newX, newY) {
    const player = this.server.gameState.players.get(playerId);
    if (!player) return false;

    // Calculate distance moved
    const dx = newX - player.x;
    const dy = newY - player.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Check if movement is physically possible
    const maxSpeed = 10; // Max units per tick
    const maxDistance = maxSpeed * 2; // Allow some buffer

    if (distance > maxDistance) {
      this.flagSuspicious(playerId, 'impossible_movement', {
        distance,
        maxDistance,
        from: { x: player.x, y: player.y },
        to: { x: newX, y: newY }
      });
      return false;
    }

    return true;
  }

  /**
   * Rate limit player actions
   */
  checkRateLimit(playerId, action, maxPerSecond = 10) {
    const now = Date.now();
    const key = `${playerId}_${action}`;

    if (!this.playerStats.has(key)) {
      this.playerStats.set(key, []);
    }

    const timestamps = this.playerStats.get(key);

    // Remove timestamps older than 1 second
    const recent = timestamps.filter(t => now - t < 1000);
    this.playerStats.set(key, recent);

    // Check rate
    if (recent.length >= maxPerSecond) {
      this.flagSuspicious(playerId, 'rate_limit_exceeded', {
        action,
        count: recent.length,
        limit: maxPerSecond
      });
      return false;
    }

    // Add timestamp
    recent.push(now);
    return true;
  }

  /**
   * Validate shot (aim bot detection)
   */
  validateShot(playerId, targetId, hit) {
    if (!hit) return true; // Don't care about misses

    const stats = this.getPlayerStats(playerId);
    stats.shots++;
    stats.hits++;

    // Calculate hit rate
    const hitRate = stats.hits / stats.shots;

    // Flag if hit rate is suspiciously high
    if (stats.shots > 20 && hitRate > 0.9) {
      this.flagSuspicious(playerId, 'high_accuracy', {
        hitRate: (hitRate * 100).toFixed(1) + '%',
        shots: stats.shots,
        hits: stats.hits
      });
    }

    return true;
  }

  /**
   * Get or create player stats
   */
  getPlayerStats(playerId) {
    if (!this.playerStats.has(playerId)) {
      this.playerStats.set(playerId, {
        shots: 0,
        hits: 0,
        flaggedCount: 0
      });
    }
    return this.playerStats.get(playerId);
  }

  /**
   * Flag suspicious behavior
   */
  flagSuspicious(playerId, reason, details) {
    console.warn(`Suspicious behavior from ${playerId}: ${reason}`, details);

    const key = `${playerId}_${reason}`;
    const count = (this.suspiciousActions.get(key) || 0) + 1;
    this.suspiciousActions.set(key, count);

    // Take action if repeatedly flagged
    if (count > 5) {
      this.kickPlayer(playerId, reason);
    }
  }

  /**
   * Kick player for cheating
   */
  kickPlayer(playerId, reason) {
    console.log(`Kicking player ${playerId} for: ${reason}`);

    const player = this.server.gameState.players.get(playerId);
    if (player && player.connection) {
      player.connection.send(JSON.stringify({
        type: 'kicked',
        reason
      }));

      player.connection.close();
    }

    this.server.removePlayer(playerId);
  }
}
```

**Claude Code Prompt:**
```
Create a server-side security validation system that detects impossible
movements, rate limits player actions, identifies suspicious accuracy
patterns, and takes action against cheaters. Never trust client data.
```

## Best Practices

1. **Server is authoritative** - Always validate client inputs
2. **Never send full state** - Only send what each client needs
3. **Validate everything** - Speed, position, damage, all game rules
4. **Rate limit actions** - Prevent message flooding
5. **Use sequence numbers** - Track and process inputs in order
6. **Monitor player behavior** - Detect cheating patterns
7. **Separate game logic** - Server and client share game rules, not code paths
8. **Log suspicious activity** - Essential for identifying exploits
9. **Test with malicious clients** - Assume players will try to cheat
10. **Keep secrets server-side** - Enemy AI, loot tables, damage formulas

## Cross-References

- [WebSocket Implementation](./websocket-implementation.md) - Network communication
- [State Synchronization](./state-synchronization.md) - State updates
- [Anti-Cheat Strategies](./anti-cheat-strategies.md) - Security in depth
- [Lag Compensation](./lag-compensation.md) - Client prediction

## Summary

Proper client-server architecture is essential for fair, secure multiplayer games. Master these principles:

- Authoritative server maintains canonical game state
- Clients send inputs, not positions
- Server validates all inputs and game rules
- Client-side prediction for responsive controls
- Server reconciliation corrects predictions
- Security validates everything, trusts nothing

These patterns create secure, cheat-resistant multiplayer experiences that feel responsive despite network latency. Claude Code helps implement robust client-server architectures efficiently, ensuring your game is both fair and fun.
