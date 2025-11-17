# Matchmaking Systems

## Overview

Matchmaking systems connect players for multiplayer games. A good matchmaking system finds appropriate opponents quickly, creates balanced matches, and handles player connectivity gracefully. This guide covers lobby systems, skill-based matchmaking, room creation, and complete working implementations.

## Basic Lobby System

### Simple Lobby Implementation

```javascript
class GameLobby {
  constructor(lobbyId, maxPlayers = 4) {
    this.lobbyId = lobbyId;
    this.maxPlayers = maxPlayers;
    this.players = new Map();
    this.host = null;
    this.state = 'waiting'; // waiting, starting, in_game
    this.createdAt = Date.now();
  }

  /**
   * Add player to lobby
   */
  addPlayer(playerId, playerName, connection) {
    if (this.players.size >= this.maxPlayers) {
      return { success: false, error: 'Lobby full' };
    }

    if (this.state !== 'waiting') {
      return { success: false, error: 'Game already started' };
    }

    const player = {
      id: playerId,
      name: playerName,
      connection,
      ready: false,
      joinedAt: Date.now()
    };

    this.players.set(playerId, player);

    // First player becomes host
    if (this.players.size === 1) {
      this.host = playerId;
    }

    this.broadcastLobbyState();

    return { success: true };
  }

  /**
   * Remove player from lobby
   */
  removePlayer(playerId) {
    this.players.delete(playerId);

    // Assign new host if needed
    if (this.host === playerId && this.players.size > 0) {
      this.host = this.players.keys().next().value;
    }

    this.broadcastLobbyState();
  }

  /**
   * Toggle player ready status
   */
  toggleReady(playerId) {
    const player = this.players.get(playerId);
    if (!player) return;

    player.ready = !player.ready;
    this.broadcastLobbyState();

    // Check if all ready
    if (this.allPlayersReady()) {
      this.startGame();
    }
  }

  /**
   * Check if all players are ready
   */
  allPlayersReady() {
    if (this.players.size < 2) return false;

    for (const player of this.players.values()) {
      if (!player.ready) return false;
    }

    return true;
  }

  /**
   * Start game
   */
  startGame() {
    this.state = 'starting';

    // Countdown
    let countdown = 3;
    const countdownInterval = setInterval(() => {
      this.broadcast({
        type: 'countdown',
        seconds: countdown
      });

      countdown--;

      if (countdown < 0) {
        clearInterval(countdownInterval);
        this.state = 'in_game';

        this.broadcast({
          type: 'game_start',
          players: this.getPlayerList()
        });
      }
    }, 1000);
  }

  /**
   * Broadcast message to all players
   */
  broadcast(message) {
    for (const player of this.players.values()) {
      try {
        player.connection.send(JSON.stringify(message));
      } catch (e) {
        console.error(`Failed to send to ${player.id}:`, e);
      }
    }
  }

  /**
   * Broadcast lobby state
   */
  broadcastLobbyState() {
    this.broadcast({
      type: 'lobby_state',
      lobbyId: this.lobbyId,
      host: this.host,
      state: this.state,
      players: this.getPlayerList(),
      maxPlayers: this.maxPlayers
    });
  }

  /**
   * Get player list for serialization
   */
  getPlayerList() {
    return Array.from(this.players.values()).map(p => ({
      id: p.id,
      name: p.name,
      ready: p.ready,
      isHost: p.id === this.host
    }));
  }

  /**
   * Check if lobby can be deleted
   */
  canDelete() {
    return this.players.size === 0 ||
           (this.state === 'waiting' && Date.now() - this.createdAt > 300000);
  }
}

class LobbyManager {
  constructor() {
    this.lobbies = new Map();
  }

  /**
   * Create new lobby
   */
  createLobby(hostId, hostName, connection, options = {}) {
    const lobbyId = this.generateLobbyId();
    const lobby = new GameLobby(lobbyId, options.maxPlayers || 4);

    this.lobbies.set(lobbyId, lobby);
    lobby.addPlayer(hostId, hostName, connection);

    return { success: true, lobbyId, lobby };
  }

  /**
   * Join existing lobby
   */
  joinLobby(lobbyId, playerId, playerName, connection) {
    const lobby = this.lobbies.get(lobbyId);
    if (!lobby) {
      return { success: false, error: 'Lobby not found' };
    }

    const result = lobby.addPlayer(playerId, playerName, connection);
    return { ...result, lobby };
  }

  /**
   * Get list of available lobbies
   */
  getAvailableLobbies() {
    const available = [];

    for (const lobby of this.lobbies.values()) {
      if (lobby.state === 'waiting' && lobby.players.size < lobby.maxPlayers) {
        available.push({
          lobbyId: lobby.lobbyId,
          playerCount: lobby.players.size,
          maxPlayers: lobby.maxPlayers,
          host: lobby.host
        });
      }
    }

    return available;
  }

  /**
   * Clean up empty lobbies
   */
  cleanup() {
    for (const [lobbyId, lobby] of this.lobbies) {
      if (lobby.canDelete()) {
        this.lobbies.delete(lobbyId);
        console.log(`Deleted lobby ${lobbyId}`);
      }
    }
  }

  /**
   * Generate unique lobby ID
   */
  generateLobbyId() {
    return `lobby_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
```

**Claude Code Prompt:**
```
Create a lobby system for multiplayer games with room creation, player joining,
ready status, host assignment, and automatic game start when all players are
ready. Include lobby listing and cleanup.
```

## Skill-Based Matchmaking

### ELO-Based Matchmaking

```javascript
class SkillBasedMatchmaking {
  constructor() {
    this.waitingPlayers = [];
    this.matchmakingInterval = null;
    this.maxWaitTime = 30000; // 30 seconds
    this.skillRange = 200; // Initial ELO range
  }

  /**
   * Add player to matchmaking queue
   */
  addToQueue(player) {
    this.waitingPlayers.push({
      ...player,
      queuedAt: Date.now(),
      skillRange: this.skillRange
    });

    console.log(`Player ${player.id} (ELO: ${player.elo}) added to queue`);
    this.tryMatchmaking();
  }

  /**
   * Remove player from queue
   */
  removeFromQueue(playerId) {
    this.waitingPlayers = this.waitingPlayers.filter(p => p.id !== playerId);
  }

  /**
   * Attempt to create matches
   */
  tryMatchmaking() {
    if (this.waitingPlayers.length < 2) return;

    // Update skill ranges based on wait time
    this.updateSkillRanges();

    // Try to find matches
    const matches = this.findMatches();

    // Create lobbies for matches
    for (const match of matches) {
      this.createMatchLobby(match);
    }
  }

  /**
   * Update skill ranges (widen over time)
   */
  updateSkillRanges() {
    const now = Date.now();

    for (const player of this.waitingPlayers) {
      const waitTime = now - player.queuedAt;
      const rangeMultiplier = 1 + (waitTime / this.maxWaitTime);
      player.skillRange = this.skillRange * rangeMultiplier;
    }
  }

  /**
   * Find compatible matches
   */
  findMatches() {
    const matches = [];
    const matched = new Set();

    // Sort by ELO
    const sorted = [...this.waitingPlayers].sort((a, b) => a.elo - b.elo);

    for (let i = 0; i < sorted.length; i++) {
      if (matched.has(sorted[i].id)) continue;

      const player1 = sorted[i];
      const compatiblePlayers = [];

      // Find compatible opponents
      for (let j = i + 1; j < sorted.length; j++) {
        if (matched.has(sorted[j].id)) continue;

        const player2 = sorted[j];
        const eloDiff = Math.abs(player1.elo - player2.elo);

        if (eloDiff <= Math.min(player1.skillRange, player2.skillRange)) {
          compatiblePlayers.push(player2);
        }
      }

      // Create match if found opponent
      if (compatiblePlayers.length > 0) {
        const opponent = compatiblePlayers[0];
        matches.push([player1, opponent]);
        matched.add(player1.id);
        matched.add(opponent.id);
      }
    }

    // Remove matched players from queue
    this.waitingPlayers = this.waitingPlayers.filter(p => !matched.has(p.id));

    return matches;
  }

  /**
   * Create lobby for matched players
   */
  createMatchLobby(players) {
    const avgElo = players.reduce((sum, p) => sum + p.elo, 0) / players.length;

    console.log(`Match created: ${players.map(p => `${p.name}(${p.elo})`).join(' vs ')}`);
    console.log(`Average ELO: ${avgElo.toFixed(0)}`);

    // Create lobby and add players
    // Implementation depends on your lobby system
  }

  /**
   * Start matchmaking loop
   */
  start() {
    this.matchmakingInterval = setInterval(() => {
      this.tryMatchmaking();
    }, 2000); // Try every 2 seconds
  }

  /**
   * Stop matchmaking
   */
  stop() {
    if (this.matchmakingInterval) {
      clearInterval(this.matchmakingInterval);
      this.matchmakingInterval = null;
    }
  }

  /**
   * Get queue statistics
   */
  getStats() {
    return {
      playersInQueue: this.waitingPlayers.length,
      averageWaitTime: this.calculateAverageWaitTime(),
      eloRange: {
        min: Math.min(...this.waitingPlayers.map(p => p.elo)),
        max: Math.max(...this.waitingPlayers.map(p => p.elo))
      }
    };
  }

  calculateAverageWaitTime() {
    if (this.waitingPlayers.length === 0) return 0;

    const now = Date.now();
    const totalWait = this.waitingPlayers.reduce(
      (sum, p) => sum + (now - p.queuedAt),
      0
    );

    return totalWait / this.waitingPlayers.length;
  }
}
```

**Claude Code Prompt:**
```
Create a skill-based matchmaking system using ELO ratings that finds balanced
matches, widens skill range over time for long-waiting players, and creates
lobbies when suitable opponents are found.
```

## Quick Match System

### Fast Matchmaking

```javascript
class QuickMatchSystem {
  constructor(lobbyManager) {
    this.lobbyManager = lobbyManager;
    this.quickMatchQueue = [];
  }

  /**
   * Add player to quick match
   */
  addPlayer(playerId, playerName, connection) {
    this.quickMatchQueue.push({
      playerId,
      playerName,
      connection,
      joinedAt: Date.now()
    });

    // Try to fill existing lobbies first
    const joined = this.tryJoinExistingLobby(playerId, playerName, connection);

    if (!joined) {
      // Create new lobby if 2+ players waiting
      if (this.quickMatchQueue.length >= 2) {
        this.createQuickMatchLobby();
      }
    }
  }

  /**
   * Try to join existing lobby
   */
  tryJoinExistingLobby(playerId, playerName, connection) {
    const available = this.lobbyManager.getAvailableLobbies();

    for (const lobbyInfo of available) {
      const result = this.lobbyManager.joinLobby(
        lobbyInfo.lobbyId,
        playerId,
        playerName,
        connection
      );

      if (result.success) {
        this.removeFromQueue(playerId);
        return true;
      }
    }

    return false;
  }

  /**
   * Create lobby from queue
   */
  createQuickMatchLobby() {
    if (this.quickMatchQueue.length < 2) return;

    // Take first 2-4 players
    const players = this.quickMatchQueue.splice(0, 4);

    // Create lobby
    const host = players[0];
    const result = this.lobbyManager.createLobby(
      host.playerId,
      host.playerName,
      host.connection,
      { maxPlayers: 4 }
    );

    if (!result.success) return;

    // Add remaining players
    for (let i = 1; i < players.length; i++) {
      const p = players[i];
      this.lobbyManager.joinLobby(
        result.lobbyId,
        p.playerId,
        p.playerName,
        p.connection
      );
    }

    console.log(`Quick match lobby created with ${players.length} players`);
  }

  /**
   * Remove player from queue
   */
  removeFromQueue(playerId) {
    this.quickMatchQueue = this.quickMatchQueue.filter(
      p => p.playerId !== playerId
    );
  }
}
```

**Claude Code Prompt:**
```
Create a quick match system that fills existing lobbies first, creates new
lobbies when enough players are waiting, and gets players into games as
fast as possible without complex matchmaking logic.
```

## Best Practices

1. **Prioritize speed over perfect matches** - Players want to play
2. **Widen skill range over time** - Don't let players wait forever
3. **Show queue position and estimated time** - Set expectations
4. **Allow party/group matchmaking** - Friends want to play together
5. **Handle disconnections gracefully** - Replace or pause game
6. **Region-based matchmaking** - Reduce latency
7. **Skill decay for inactive players** - Keep ratings current
8. **Monitor matchmaking metrics** - Wait times, match quality
9. **Provide quick match option** - Not everyone wants ranked
10. **Cancel matchmaking easily** - Don't trap players

## Cross-References

- [WebSocket Implementation](./websocket-implementation.md) - Network layer
- [Client-Server Architecture](./client-server-architecture.md) - Server structure
- [State Synchronization](./state-synchronization.md) - In-game sync

## Summary

Matchmaking systems connect players for great multiplayer experiences. Master these techniques:

- Lobby systems for room-based matchmaking
- Skill-based matchmaking with ELO ratings
- Quick match for fast games
- Queue management and player removal
- Host assignment and migration

Good matchmaking gets players into balanced, fun matches quickly. Claude Code helps implement sophisticated matchmaking systems efficiently, creating engaging multiplayer experiences.
