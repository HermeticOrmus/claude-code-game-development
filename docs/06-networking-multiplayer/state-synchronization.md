# State Synchronization

## Overview

State synchronization is the art of keeping game state consistent across multiple clients while minimizing bandwidth and maintaining responsiveness. Every multiplayer game faces the fundamental challenge: how do you ensure all players see the same game world without sending excessive data or introducing lag?

This guide covers state synchronization strategies from simple full-state snapshots to sophisticated delta compression and relevance filtering. You'll learn when to use each technique and how to implement production-ready synchronization systems for different game types.

## Full State Snapshots

The simplest synchronization strategy sends the complete game state every update. Simple to implement but bandwidth-intensive.

### Snapshot System

```javascript
class SnapshotSynchronizer {
  constructor(server, updateRate = 20) {
    this.server = server;
    this.updateRate = updateRate;
    this.updateInterval = 1000 / updateRate;
  }

  /**
   * Create full state snapshot
   */
  createSnapshot() {
    return {
      type: 'snapshot',
      tick: this.server.gameState.tick,
      timestamp: Date.now(),
      players: this.serializePlayers(),
      entities: this.serializeEntities(),
      world: this.serializeWorld()
    };
  }

  /**
   * Serialize all players
   */
  serializePlayers() {
    return Array.from(this.server.gameState.players.values()).map(player => ({
      id: player.id,
      x: player.x,
      y: player.y,
      vx: player.vx,
      vy: player.vy,
      rotation: player.rotation,
      health: player.health,
      score: player.score
    }));
  }

  /**
   * Serialize all entities
   */
  serializeEntities() {
    return Array.from(this.server.gameState.entities.values()).map(entity => ({
      id: entity.id,
      type: entity.type,
      x: entity.x,
      y: entity.y,
      rotation: entity.rotation
    }));
  }

  /**
   * Serialize world state
   */
  serializeWorld() {
    return {
      timeRemaining: this.server.gameState.timeRemaining,
      phase: this.server.gameState.phase
    };
  }

  /**
   * Send snapshot to all clients
   */
  broadcastSnapshot() {
    const snapshot = this.createSnapshot();
    const data = JSON.stringify(snapshot);

    for (const player of this.server.gameState.players.values()) {
      if (player.connection) {
        player.connection.send(data);
      }
    }
  }
}
```

**Claude Code Prompt:**
```
Create a full-state snapshot synchronization system that captures complete
game state and broadcasts to all clients. Include serialization for players,
entities, and world state with configurable update rates.
```

## Delta Compression

Delta compression sends only changes since the last update, dramatically reducing bandwidth for games with many static or slow-moving entities.

### Delta Synchronization System

```javascript
class DeltaSynchronizer {
  constructor(server) {
    this.server = server;
    this.clientStates = new Map(); // Track last sent state per client
    this.threshold = 0.01; // Minimum change to sync (units)
  }

  /**
   * Send delta update to client
   */
  sendDeltaUpdate(playerId) {
    const connection = this.server.gameState.players.get(playerId)?.connection;
    if (!connection) return;

    // Get last sent state
    let lastState = this.clientStates.get(playerId);

    if (!lastState) {
      // First update - send full state
      lastState = this.createFullState();
      this.sendFullState(playerId, lastState);
      this.clientStates.set(playerId, lastState);
      return;
    }

    // Create delta
    const delta = this.createDelta(lastState);

    // Only send if there are changes
    if (this.hasChanges(delta)) {
      connection.send(JSON.stringify({
        type: 'delta',
        tick: this.server.gameState.tick,
        delta
      }));

      // Update last state
      this.updateLastState(playerId, delta);
    }
  }

  /**
   * Create delta from last state
   */
  createDelta(lastState) {
    const delta = {
      players: this.createPlayerDeltas(lastState.players),
      entities: this.createEntityDeltas(lastState.entities),
      removed: this.findRemovedEntities(lastState)
    };

    return delta;
  }

  /**
   * Create player deltas
   */
  createPlayerDeltas(lastPlayers) {
    const deltas = [];

    for (const [playerId, player] of this.server.gameState.players) {
      const lastPlayer = lastPlayers.get(playerId);

      if (!lastPlayer) {
        // New player
        deltas.push({
          id: playerId,
          type: 'new',
          data: this.serializePlayer(player)
        });
      } else {
        // Check for changes
        const changes = {};
        let hasChanges = false;

        if (Math.abs(player.x - lastPlayer.x) > this.threshold) {
          changes.x = player.x;
          hasChanges = true;
        }

        if (Math.abs(player.y - lastPlayer.y) > this.threshold) {
          changes.y = player.y;
          hasChanges = true;
        }

        if (Math.abs(player.rotation - lastPlayer.rotation) > 0.01) {
          changes.rotation = player.rotation;
          hasChanges = true;
        }

        if (player.health !== lastPlayer.health) {
          changes.health = player.health;
          hasChanges = true;
        }

        if (hasChanges) {
          deltas.push({
            id: playerId,
            type: 'update',
            changes
          });
        }
      }
    }

    return deltas;
  }

  /**
   * Create entity deltas
   */
  createEntityDeltas(lastEntities) {
    const deltas = [];

    for (const [entityId, entity] of this.server.gameState.entities) {
      const lastEntity = lastEntities.get(entityId);

      if (!lastEntity) {
        deltas.push({
          id: entityId,
          type: 'new',
          data: this.serializeEntity(entity)
        });
      } else {
        const changes = {};
        let hasChanges = false;

        if (Math.abs(entity.x - lastEntity.x) > this.threshold) {
          changes.x = entity.x;
          hasChanges = true;
        }

        if (Math.abs(entity.y - lastEntity.y) > this.threshold) {
          changes.y = entity.y;
          hasChanges = true;
        }

        if (hasChanges) {
          deltas.push({
            id: entityId,
            type: 'update',
            changes
          });
        }
      }
    }

    return deltas;
  }

  /**
   * Find removed entities
   */
  findRemovedEntities(lastState) {
    const removed = [];

    for (const playerId of lastState.players.keys()) {
      if (!this.server.gameState.players.has(playerId)) {
        removed.push({ type: 'player', id: playerId });
      }
    }

    for (const entityId of lastState.entities.keys()) {
      if (!this.server.gameState.entities.has(entityId)) {
        removed.push({ type: 'entity', id: entityId });
      }
    }

    return removed;
  }

  /**
   * Check if delta has changes
   */
  hasChanges(delta) {
    return delta.players.length > 0 ||
           delta.entities.length > 0 ||
           delta.removed.length > 0;
  }

  /**
   * Apply delta on client
   */
  applyDelta(clientState, delta) {
    // Apply player updates
    for (const playerDelta of delta.players) {
      if (playerDelta.type === 'new') {
        clientState.players.set(playerDelta.id, playerDelta.data);
      } else if (playerDelta.type === 'update') {
        const player = clientState.players.get(playerDelta.id);
        if (player) {
          Object.assign(player, playerDelta.changes);
        }
      }
    }

    // Apply entity updates
    for (const entityDelta of delta.entities) {
      if (entityDelta.type === 'new') {
        clientState.entities.set(entityDelta.id, entityDelta.data);
      } else if (entityDelta.type === 'update') {
        const entity = clientState.entities.get(entityDelta.id);
        if (entity) {
          Object.assign(entity, entityDelta.changes);
        }
      }
    }

    // Remove deleted entities
    for (const removed of delta.removed) {
      if (removed.type === 'player') {
        clientState.players.delete(removed.id);
      } else {
        clientState.entities.delete(removed.id);
      }
    }
  }

  serializePlayer(player) {
    return {
      id: player.id,
      name: player.name,
      x: player.x,
      y: player.y,
      rotation: player.rotation,
      health: player.health
    };
  }

  serializeEntity(entity) {
    return {
      id: entity.id,
      type: entity.type,
      x: entity.x,
      y: entity.y,
      rotation: entity.rotation
    };
  }

  createFullState() {
    return {
      players: new Map(this.server.gameState.players),
      entities: new Map(this.server.gameState.entities),
      tick: this.server.gameState.tick
    };
  }

  sendFullState(playerId, state) {
    const connection = this.server.gameState.players.get(playerId)?.connection;
    if (!connection) return;

    connection.send(JSON.stringify({
      type: 'full_state',
      tick: state.tick,
      players: Array.from(state.players.values()).map(p => this.serializePlayer(p)),
      entities: Array.from(state.entities.values()).map(e => this.serializeEntity(e))
    }));
  }

  updateLastState(playerId, delta) {
    const lastState = this.clientStates.get(playerId);
    if (!lastState) return;

    // Apply delta to last state
    this.applyDelta(lastState, delta);
    lastState.tick = this.server.gameState.tick;
  }
}
```

**Claude Code Prompt:**
```
Create a delta compression synchronization system that tracks changes since
last update, sends only modified properties, handles new and removed entities,
and includes client-side delta application. Minimize bandwidth usage.
```

## Entity Interpolation

Entity interpolation creates smooth movement by rendering entities slightly behind real-time, interpolating between received snapshots.

### Interpolation System

```javascript
class EntityInterpolator {
  constructor(bufferTime = 100) {
    this.bufferTime = bufferTime; // Milliseconds behind server
    this.stateBuffer = [];
    this.maxBufferSize = 60;
  }

  /**
   * Add server state to buffer
   */
  addState(state) {
    this.stateBuffer.push({
      ...state,
      receivedAt: Date.now()
    });

    // Limit buffer size
    if (this.stateBuffer.length > this.maxBufferSize) {
      this.stateBuffer.shift();
    }

    // Sort by timestamp
    this.stateBuffer.sort((a, b) => a.timestamp - b.timestamp);
  }

  /**
   * Get interpolated state for rendering
   */
  getInterpolatedState() {
    if (this.stateBuffer.length < 2) {
      return this.stateBuffer[0] || null;
    }

    const renderTime = Date.now() - this.bufferTime;

    // Find surrounding states
    let i = 0;
    while (i < this.stateBuffer.length - 1 && this.stateBuffer[i + 1].timestamp <= renderTime) {
      i++;
    }

    const before = this.stateBuffer[i];
    const after = this.stateBuffer[i + 1] || before;

    // Calculate interpolation factor
    const totalTime = after.timestamp - before.timestamp;
    if (totalTime === 0) {
      return before;
    }

    const factor = (renderTime - before.timestamp) / totalTime;
    const t = Math.max(0, Math.min(1, factor));

    // Interpolate entities
    return this.interpolateStates(before, after, t);
  }

  /**
   * Interpolate between two states
   */
  interpolateStates(state1, state2, t) {
    const interpolated = {
      tick: state1.tick,
      timestamp: state1.timestamp,
      players: new Map(),
      entities: new Map()
    };

    // Interpolate players
    for (const [playerId, player1] of state1.players) {
      const player2 = state2.players.get(playerId);

      if (player2) {
        interpolated.players.set(playerId, {
          ...player1,
          x: this.lerp(player1.x, player2.x, t),
          y: this.lerp(player1.y, player2.y, t),
          rotation: this.lerpAngle(player1.rotation, player2.rotation, t)
        });
      } else {
        interpolated.players.set(playerId, player1);
      }
    }

    // Interpolate entities
    for (const [entityId, entity1] of state1.entities) {
      const entity2 = state2.entities.get(entityId);

      if (entity2) {
        interpolated.entities.set(entityId, {
          ...entity1,
          x: this.lerp(entity1.x, entity2.x, t),
          y: this.lerp(entity1.y, entity2.y, t),
          rotation: this.lerpAngle(entity1.rotation, entity2.rotation, t)
        });
      } else {
        interpolated.entities.set(entityId, entity1);
      }
    }

    return interpolated;
  }

  /**
   * Linear interpolation
   */
  lerp(a, b, t) {
    return a + (b - a) * t;
  }

  /**
   * Angle interpolation (handles wrapping)
   */
  lerpAngle(a, b, t) {
    const diff = ((b - a + Math.PI) % (2 * Math.PI)) - Math.PI;
    return a + diff * t;
  }

  /**
   * Clean old states from buffer
   */
  cleanup() {
    const cutoff = Date.now() - 1000; // Keep 1 second of history

    this.stateBuffer = this.stateBuffer.filter(
      state => state.receivedAt > cutoff
    );
  }
}
```

**Claude Code Prompt:**
```
Create an entity interpolation system that buffers server states and smoothly
interpolates entity positions for rendering. Handle angle wrapping, missing
entities, and buffer management for smooth visual output.
```

## Best Practices

1. **Start with snapshots** - Optimize later if needed
2. **Use delta compression** - For games with many entities
3. **Interpolate remote entities** - Smooth movement despite packet gaps
4. **Don't interpolate local player** - Use prediction instead
5. **Quantize values** - Round positions to reduce data size
6. **Send relevance-filtered updates** - Don't send what players can't see
7. **Include timestamps** - Essential for interpolation
8. **Handle packet loss** - Buffer multiple states
9. **Monitor bandwidth** - Profile actual network usage
10. **Test on slow connections** - 3G, high latency scenarios

## Cross-References

- [WebSocket Implementation](./websocket-implementation.md) - Network layer
- [Client-Server Architecture](./client-server-architecture.md) - Authoritative patterns
- [Lag Compensation](./lag-compensation.md) - Client prediction
- [Performance Optimization](../10-performance-optimization/README.md) - Bandwidth optimization

## Summary

State synchronization keeps multiplayer games consistent across clients. Master these techniques:

- Full snapshots for simple, reliable synchronization
- Delta compression for bandwidth efficiency
- Entity interpolation for smooth visual output
- State buffering for handling packet gaps
- Relevance filtering for scalability

Choose the right strategy for your game type and player count. Claude Code helps implement sophisticated synchronization systems efficiently, ensuring smooth, consistent multiplayer experiences.
