# Lag Compensation

## Overview

Lag compensation makes multiplayer games feel responsive despite network latency. Without it, players experience frustrating delays between pressing buttons and seeing results. This guide covers client-side prediction, server reconciliation, and entity interpolation - the trilogy of techniques that create smooth multiplayer experiences.

## Client-Side Prediction

Client-side prediction applies inputs immediately on the client while waiting for server confirmation, creating instant responsiveness.

### Complete Prediction System

```javascript
class ClientSidePrediction {
  constructor() {
    this.localPlayer = null;
    this.pendingInputs = [];
    this.inputSequence = 0;
  }

  /**
   * Process local input with prediction
   */
  processInput(input) {
    this.inputSequence++;
    input.sequence = this.inputSequence;
    input.timestamp = Date.now();

    // Apply input locally immediately
    this.applyInput(this.localPlayer, input);

    // Send to server
    this.sendToServer(input);

    // Store for reconciliation
    this.pendingInputs.push(input);

    // Limit buffer
    if (this.pendingInputs.length > 100) {
      this.pendingInputs.shift();
    }
  }

  /**
   * Apply input to entity
   */
  applyInput(entity, input) {
    const speed = 5;
    const dt = 1 / 60;

    if (input.keys.w) entity.y -= speed * dt;
    if (input.keys.s) entity.y += speed * dt;
    if (input.keys.a) entity.x -= speed * dt;
    if (input.keys.d) entity.x += speed * dt;

    entity.x = Math.max(0, Math.min(entity.x, 1000));
    entity.y = Math.max(0, Math.min(entity.y, 1000));
  }

  /**
   * Reconcile with server state
   */
  reconcile(serverState) {
    const serverPlayer = serverState.players.find(p => p.id === this.localPlayer.id);
    if (!serverPlayer) return;

    // Find last processed input by server
    const lastProcessed = serverState.lastProcessedInput || 0;

    // Remove acknowledged inputs
    this.pendingInputs = this.pendingInputs.filter(
      input => input.sequence > lastProcessed
    );

    // Check for prediction error
    const errorX = Math.abs(serverPlayer.x - this.localPlayer.x);
    const errorY = Math.abs(serverPlayer.y - this.localPlayer.y);

    if (errorX > 0.1 || errorY > 0.1) {
      // Server correction needed
      console.log(`Prediction error: ${errorX.toFixed(2)}, ${errorY.toFixed(2)}`);

      // Reset to server position
      this.localPlayer.x = serverPlayer.x;
      this.localPlayer.y = serverPlayer.y;

      // Re-apply pending inputs
      for (const input of this.pendingInputs) {
        this.applyInput(this.localPlayer, input);
      }
    }

    // Update authoritative properties
    this.localPlayer.health = serverPlayer.health;
  }
}
```

**Claude Code Prompt:**
```
Create a client-side prediction system that applies inputs immediately for
responsive controls, tracks pending inputs, and reconciles with server state
by re-applying unacknowledged inputs. Handle prediction errors gracefully.
```

## Server Reconciliation

Server tracks input sequence numbers and tells clients which inputs have been processed.

### Server-Side Input Processing

```javascript
class ServerInputProcessor {
  constructor(gameServer) {
    this.server = gameServer;
  }

  /**
   * Process client input
   */
  processClientInput(playerId, input) {
    const player = this.server.players.get(playerId);
    if (!player) return;

    // Validate input sequence (must be newer)
    if (input.sequence <= player.lastProcessedInput) {
      return; // Old input, ignore
    }

    // Validate input
    if (!this.validateInput(player, input)) {
      console.warn(`Invalid input from ${playerId}`);
      return;
    }

    // Apply input to authoritative state
    this.applyInput(player, input);

    // Update last processed sequence
    player.lastProcessedInput = input.sequence;
  }

  /**
   * Validate input reasonability
   */
  validateInput(player, input) {
    // Check timestamp is recent
    const age = Date.now() - input.timestamp;
    if (age > 1000 || age < -100) return false;

    // Validate input format
    if (input.keys && typeof input.keys !== 'object') return false;

    return true;
  }

  /**
   * Apply input to player
   */
  applyInput(player, input) {
    const speed = 5;
    const dt = this.server.tickInterval / 1000;

    if (input.keys.w) player.y -= speed * dt;
    if (input.keys.s) player.y += speed * dt;
    if (input.keys.a) player.x -= speed * dt;
    if (input.keys.d) player.x += speed * dt;

    player.x = Math.max(0, Math.min(player.x, 1000));
    player.y = Math.max(0, Math.min(player.y, 1000));
  }

  /**
   * Create state update with last processed input
   */
  createStateUpdate(playerId) {
    const player = this.server.players.get(playerId);

    return {
      type: 'state_update',
      tick: this.server.tick,
      timestamp: Date.now(),
      lastProcessedInput: player.lastProcessedInput,
      playerState: {
        x: player.x,
        y: player.y,
        health: player.health
      }
    };
  }
}
```

**Claude Code Prompt:**
```
Create server-side input processing that validates inputs, applies them to
authoritative state, tracks sequence numbers, and includes last processed
input in state updates for client reconciliation.
```

## Lag Simulation

Testing lag compensation requires simulating network conditions.

### Network Simulator

```javascript
class NetworkSimulator {
  constructor(ws) {
    this.ws = ws;
    this.enabled = false;
    this.latency = 50; // ms
    this.jitter = 10; // ms
    this.packetLoss = 0; // 0-1
    this.sendQueue = [];
  }

  /**
   * Send message with simulated lag
   */
  send(message) {
    if (!this.enabled) {
      this.ws.send(message);
      return;
    }

    // Simulate packet loss
    if (Math.random() < this.packetLoss) {
      console.log('Packet dropped (simulated)');
      return;
    }

    // Calculate delay
    const delay = this.latency + (Math.random() - 0.5) * this.jitter * 2;

    // Queue message with delay
    setTimeout(() => {
      this.ws.send(message);
    }, Math.max(0, delay));
  }

  /**
   * Enable/disable simulation
   */
  setEnabled(enabled) {
    this.enabled = enabled;
    console.log(`Network simulation: ${enabled ? 'enabled' : 'disabled'}`);
  }

  /**
   * Configure simulation parameters
   */
  configure(options) {
    if (options.latency !== undefined) this.latency = options.latency;
    if (options.jitter !== undefined) this.jitter = options.jitter;
    if (options.packetLoss !== undefined) this.packetLoss = options.packetLoss;

    console.log('Network simulation configured:', {
      latency: this.latency,
      jitter: this.jitter,
      packetLoss: this.packetLoss
    });
  }
}

// Usage
const simulator = new NetworkSimulator(websocket);
simulator.configure({ latency: 100, jitter: 20, packetLoss: 0.05 });
simulator.setEnabled(true);
```

**Claude Code Prompt:**
```
Create a network simulator for testing lag compensation that adds configurable
latency, jitter, and packet loss to WebSocket messages. Essential for testing
multiplayer games under realistic network conditions.
```

## Complete Lag Compensation Example

### Full Implementation

```javascript
class LagCompensationSystem {
  constructor(websocket) {
    this.ws = websocket;
    this.prediction = new ClientSidePrediction();
    this.interpolator = new EntityInterpolator(100);
    this.localPlayer = { id: null, x: 0, y: 0, vx: 0, vy: 0 };
    this.remotePlayers = new Map();
  }

  /**
   * Initialize system
   */
  init(playerId) {
    this.localPlayer.id = playerId;
    this.prediction.localPlayer = this.localPlayer;

    // Setup message handler
    this.ws.on('state_update', (state) => {
      this.handleServerUpdate(state);
    });
  }

  /**
   * Handle player input
   */
  handleInput(input) {
    // Client-side prediction for local player
    this.prediction.processInput(input);
  }

  /**
   * Handle server state update
   */
  handleServerUpdate(state) {
    // Add to interpolation buffer
    this.interpolator.addState(state);

    // Reconcile local player
    this.prediction.reconcile(state);

    // Update remote players (no prediction)
    for (const player of state.players) {
      if (player.id !== this.localPlayer.id) {
        this.remotePlayers.set(player.id, player);
      }
    }
  }

  /**
   * Get render state
   */
  getRenderState() {
    // Get interpolated state for remote entities
    const interpolatedState = this.interpolator.getInterpolatedState();

    return {
      localPlayer: this.localPlayer, // Latest predicted
      remotePlayers: interpolatedState ? interpolatedState.players : this.remotePlayers
    };
  }
}
```

## Best Practices

1. **Always predict local player** - Essential for responsive controls
2. **Never predict remote players** - Interpolate instead
3. **Include sequence numbers** - For reconciliation
4. **Handle prediction errors gracefully** - Smooth corrections
5. **Test with lag simulation** - Essential for development
6. **Don't extrapolate too far** - Causes rubber-banding
7. **Validate inputs server-side** - Never trust predictions
8. **Monitor prediction errors** - Indicates issues
9. **Use fixed timestep** - Consistent physics
10. **Buffer network updates** - Smooth interpolation

## Cross-References

- [Client-Server Architecture](./client-server-architecture.md) - Server authority
- [State Synchronization](./state-synchronization.md) - State updates
- [WebSocket Implementation](./websocket-implementation.md) - Network layer

## Summary

Lag compensation creates responsive multiplayer despite network latency. Master these techniques:

- Client-side prediction for immediate feedback
- Server reconciliation with sequence numbers
- Entity interpolation for smooth remote players
- Network simulation for testing
- Error handling for prediction mismatches

These techniques transform laggy experiences into smooth, competitive gameplay. Claude Code helps implement sophisticated lag compensation efficiently, making your multiplayer game feel responsive across all network conditions.
