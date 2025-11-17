# WebSocket Implementation

## Overview

WebSockets provide the foundation for real-time multiplayer web games. Unlike HTTP's request-response model, WebSockets establish persistent, bidirectional connections that allow servers to push data to clients instantly. This low-latency communication is essential for responsive multiplayer experiences where players need immediate feedback about other players' actions.

Understanding WebSocket implementation is the first step toward building multiplayer games. This guide covers both client-side and server-side WebSocket setup, message protocols, error handling, reconnection strategies, and complete working examples you can use as starting points for your multiplayer games.

## WebSocket Basics

WebSockets operate over TCP, providing reliable, ordered delivery. After an initial HTTP handshake, the connection upgrades to the WebSocket protocol, maintaining an open channel for bidirectional data flow.

### Key WebSocket Characteristics

- **Full-Duplex**: Both client and server can send messages anytime
- **Low Latency**: No HTTP overhead for each message
- **Persistent Connection**: Stays open until explicitly closed
- **Automatic Reconnection**: Requires manual implementation
- **Text or Binary**: Support both string and binary data

## Client-Side WebSocket Implementation

A robust client WebSocket system handles connection lifecycle, automatic reconnection, and message queuing.

### Production-Ready WebSocket Client

```javascript
class GameWebSocketClient {
  constructor(url, options = {}) {
    this.url = url;
    this.ws = null;
    this.connected = false;
    this.reconnecting = false;

    // Configuration
    this.options = {
      reconnectInterval: 1000,
      reconnectDecay: 1.5,
      reconnectAttempts: 10,
      heartbeatInterval: 30000,
      heartbeatTimeout: 5000,
      ...options
    };

    // State
    this.reconnectTimer = null;
    this.heartbeatTimer = null;
    this.heartbeatTimeoutTimer = null;
    this.reconnectCount = 0;
    this.messageQueue = [];
    this.messageHandlers = new Map();
    this.connectionId = null;

    // Callbacks
    this.onOpen = null;
    this.onClose = null;
    this.onError = null;
  }

  /**
   * Connect to WebSocket server
   */
  connect() {
    try {
      console.log(`Connecting to ${this.url}...`);

      this.ws = new WebSocket(this.url);

      // Connection opened
      this.ws.onopen = (event) => {
        console.log('WebSocket connected');
        this.connected = true;
        this.reconnecting = false;
        this.reconnectCount = 0;

        // Start heartbeat
        this.startHeartbeat();

        // Send queued messages
        this.flushMessageQueue();

        // User callback
        if (this.onOpen) {
          this.onOpen(event);
        }
      };

      // Connection closed
      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        this.connected = false;

        // Stop heartbeat
        this.stopHeartbeat();

        // User callback
        if (this.onClose) {
          this.onClose(event);
        }

        // Attempt reconnection
        if (!event.wasClean && this.reconnectCount < this.options.reconnectAttempts) {
          this.attemptReconnect();
        }
      };

      // Error occurred
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);

        if (this.onError) {
          this.onError(error);
        }
      };

      // Message received
      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }

  /**
   * Handle incoming message
   */
  handleMessage(data) {
    try {
      const message = JSON.parse(data);

      // Handle heartbeat response
      if (message.type === 'pong') {
        this.handlePong();
        return;
      }

      // Handle connection acknowledgment
      if (message.type === 'connected') {
        this.connectionId = message.connectionId;
        console.log(`Connection ID: ${this.connectionId}`);
        return;
      }

      // Route to registered handler
      const handler = this.messageHandlers.get(message.type);
      if (handler) {
        handler(message);
      } else {
        console.warn(`No handler for message type: ${message.type}`);
      }

    } catch (error) {
      console.error('Failed to parse message:', error);
    }
  }

  /**
   * Send message to server
   */
  send(type, data = {}) {
    const message = {
      type,
      ...data,
      timestamp: Date.now()
    };

    if (this.connected && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('Failed to send message:', error);
        this.queueMessage(message);
      }
    } else {
      // Queue message for later delivery
      this.queueMessage(message);
    }
  }

  /**
   * Queue message for sending when connected
   */
  queueMessage(message) {
    this.messageQueue.push(message);

    // Limit queue size to prevent memory issues
    if (this.messageQueue.length > 100) {
      console.warn('Message queue overflow, dropping oldest messages');
      this.messageQueue = this.messageQueue.slice(-100);
    }
  }

  /**
   * Send all queued messages
   */
  flushMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('Failed to send queued message:', error);
        // Put it back in the queue
        this.messageQueue.unshift(message);
        break;
      }
    }
  }

  /**
   * Register message handler
   */
  on(messageType, handler) {
    this.messageHandlers.set(messageType, handler);
  }

  /**
   * Unregister message handler
   */
  off(messageType) {
    this.messageHandlers.delete(messageType);
  }

  /**
   * Attempt to reconnect
   */
  attemptReconnect() {
    if (this.reconnecting) return;

    this.reconnecting = true;
    this.reconnectCount++;

    // Calculate backoff delay
    const delay = Math.min(
      this.options.reconnectInterval * Math.pow(this.options.reconnectDecay, this.reconnectCount - 1),
      30000 // Max 30 seconds
    );

    console.log(`Reconnecting in ${(delay / 1000).toFixed(1)}s (attempt ${this.reconnectCount}/${this.options.reconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Start heartbeat to detect connection loss
   */
  startHeartbeat() {
    this.stopHeartbeat();

    this.heartbeatTimer = setInterval(() => {
      if (this.connected) {
        this.send('ping');

        // Set timeout for pong response
        this.heartbeatTimeoutTimer = setTimeout(() => {
          console.warn('Heartbeat timeout - connection may be lost');
          this.disconnect();
        }, this.options.heartbeatTimeout);
      }
    }, this.options.heartbeatInterval);
  }

  /**
   * Handle heartbeat response
   */
  handlePong() {
    // Clear timeout - connection is alive
    if (this.heartbeatTimeoutTimer) {
      clearTimeout(this.heartbeatTimeoutTimer);
      this.heartbeatTimeoutTimer = null;
    }
  }

  /**
   * Stop heartbeat
   */
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }

    if (this.heartbeatTimeoutTimer) {
      clearTimeout(this.heartbeatTimeoutTimer);
      this.heartbeatTimeoutTimer = null;
    }
  }

  /**
   * Disconnect from server
   */
  disconnect() {
    console.log('Disconnecting...');

    this.stopHeartbeat();

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.connected = false;
    this.reconnecting = false;
  }

  /**
   * Get connection status
   */
  getStatus() {
    return {
      connected: this.connected,
      reconnecting: this.reconnecting,
      reconnectCount: this.reconnectCount,
      queuedMessages: this.messageQueue.length,
      connectionId: this.connectionId
    };
  }
}

// Usage example
const client = new GameWebSocketClient('ws://localhost:8080');

// Set up handlers
client.onOpen = () => {
  console.log('Connected to game server!');
};

client.onClose = (event) => {
  console.log('Disconnected from server');
};

// Register message handlers
client.on('player_joined', (message) => {
  console.log(`Player ${message.playerId} joined the game`);
});

client.on('game_state', (message) => {
  console.log('Received game state update:', message);
});

// Connect
client.connect();

// Send messages
client.send('join_game', { playerName: 'Alice' });
```

**Claude Code Prompt:**
```
Create a production-ready WebSocket client for a multiplayer game that handles
automatic reconnection with exponential backoff, heartbeat for connection
detection, message queuing during disconnections, and type-based message
routing. Include error handling and connection status tracking.
```

## Server-Side WebSocket Implementation (Node.js)

A robust server handles multiple clients, room management, and broadcast messaging.

### WebSocket Server with Room Support

```javascript
// Using 'ws' npm package: npm install ws
const WebSocket = require('ws');
const http = require('http');
const crypto = require('crypto');

class GameWebSocketServer {
  constructor(port = 8080) {
    this.port = port;
    this.server = null;
    this.wss = null;
    this.clients = new Map(); // connectionId -> client data
    this.rooms = new Map(); // roomId -> Set of connectionIds
    this.messageHandlers = new Map();
  }

  /**
   * Start WebSocket server
   */
  start() {
    // Create HTTP server
    this.server = http.createServer((req, res) => {
      res.writeHead(200);
      res.end('Game WebSocket Server');
    });

    // Create WebSocket server
    this.wss = new WebSocket.Server({ server: this.server });

    // Handle new connections
    this.wss.on('connection', (ws, req) => {
      this.handleConnection(ws, req);
    });

    // Start listening
    this.server.listen(this.port, () => {
      console.log(`WebSocket server listening on port ${this.port}`);
    });

    // Setup periodic cleanup
    this.startCleanup();
  }

  /**
   * Handle new client connection
   */
  handleConnection(ws, req) {
    const connectionId = this.generateConnectionId();
    const clientIp = req.socket.remoteAddress;

    console.log(`Client connected: ${connectionId} from ${clientIp}`);

    // Store client data
    const clientData = {
      connectionId,
      ws,
      ip: clientIp,
      connectedAt: Date.now(),
      lastActivity: Date.now(),
      roomId: null,
      playerId: null,
      playerName: null
    };

    this.clients.set(connectionId, clientData);

    // Send connection acknowledgment
    this.sendToClient(connectionId, {
      type: 'connected',
      connectionId
    });

    // Setup message handler
    ws.on('message', (data) => {
      this.handleMessage(connectionId, data);
    });

    // Handle disconnection
    ws.on('close', () => {
      this.handleDisconnection(connectionId);
    });

    // Handle errors
    ws.on('error', (error) => {
      console.error(`WebSocket error for ${connectionId}:`, error);
    });

    // Setup ping/pong for connection health
    ws.isAlive = true;
    ws.on('pong', () => {
      ws.isAlive = true;
    });
  }

  /**
   * Handle incoming message
   */
  handleMessage(connectionId, data) {
    const client = this.clients.get(connectionId);
    if (!client) return;

    client.lastActivity = Date.now();

    try {
      const message = JSON.parse(data);

      // Handle heartbeat
      if (message.type === 'ping') {
        this.sendToClient(connectionId, { type: 'pong' });
        return;
      }

      // Route to registered handler
      const handler = this.messageHandlers.get(message.type);
      if (handler) {
        handler(connectionId, message, client);
      } else {
        console.warn(`No handler for message type: ${message.type}`);
      }

    } catch (error) {
      console.error(`Failed to parse message from ${connectionId}:`, error);
    }
  }

  /**
   * Handle client disconnection
   */
  handleDisconnection(connectionId) {
    const client = this.clients.get(connectionId);
    if (!client) return;

    console.log(`Client disconnected: ${connectionId}`);

    // Remove from room
    if (client.roomId) {
      this.leaveRoom(connectionId, client.roomId);
    }

    // Remove client
    this.clients.delete(connectionId);
  }

  /**
   * Send message to specific client
   */
  sendToClient(connectionId, message) {
    const client = this.clients.get(connectionId);
    if (!client || client.ws.readyState !== WebSocket.OPEN) {
      return false;
    }

    try {
      client.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error(`Failed to send to ${connectionId}:`, error);
      return false;
    }
  }

  /**
   * Broadcast message to all clients in a room
   */
  broadcastToRoom(roomId, message, excludeConnectionId = null) {
    const room = this.rooms.get(roomId);
    if (!room) return;

    let sentCount = 0;

    for (const connectionId of room) {
      if (connectionId !== excludeConnectionId) {
        if (this.sendToClient(connectionId, message)) {
          sentCount++;
        }
      }
    }

    return sentCount;
  }

  /**
   * Broadcast message to all connected clients
   */
  broadcastToAll(message, excludeConnectionId = null) {
    let sentCount = 0;

    for (const connectionId of this.clients.keys()) {
      if (connectionId !== excludeConnectionId) {
        if (this.sendToClient(connectionId, message)) {
          sentCount++;
        }
      }
    }

    return sentCount;
  }

  /**
   * Create or join room
   */
  joinRoom(connectionId, roomId) {
    const client = this.clients.get(connectionId);
    if (!client) return false;

    // Leave current room if in one
    if (client.roomId) {
      this.leaveRoom(connectionId, client.roomId);
    }

    // Create room if doesn't exist
    if (!this.rooms.has(roomId)) {
      this.rooms.set(roomId, new Set());
    }

    // Add to room
    this.rooms.get(roomId).add(connectionId);
    client.roomId = roomId;

    console.log(`Client ${connectionId} joined room ${roomId}`);

    // Notify room
    this.broadcastToRoom(roomId, {
      type: 'player_joined',
      connectionId,
      playerName: client.playerName,
      roomId
    }, connectionId);

    return true;
  }

  /**
   * Leave room
   */
  leaveRoom(connectionId, roomId) {
    const client = this.clients.get(connectionId);
    const room = this.rooms.get(roomId);

    if (!room) return;

    // Remove from room
    room.delete(connectionId);

    if (client) {
      client.roomId = null;
    }

    // Notify room
    this.broadcastToRoom(roomId, {
      type: 'player_left',
      connectionId,
      playerName: client?.playerName,
      roomId
    });

    // Delete room if empty
    if (room.size === 0) {
      this.rooms.delete(roomId);
      console.log(`Room ${roomId} deleted (empty)`);
    }

    console.log(`Client ${connectionId} left room ${roomId}`);
  }

  /**
   * Register message handler
   */
  on(messageType, handler) {
    this.messageHandlers.set(messageType, handler);
  }

  /**
   * Generate unique connection ID
   */
  generateConnectionId() {
    return crypto.randomBytes(16).toString('hex');
  }

  /**
   * Start periodic cleanup
   */
  startCleanup() {
    // Ping clients every 30 seconds
    setInterval(() => {
      this.wss.clients.forEach((ws) => {
        if (ws.isAlive === false) {
          console.log('Terminating inactive connection');
          return ws.terminate();
        }

        ws.isAlive = false;
        ws.ping();
      });
    }, 30000);
  }

  /**
   * Get server statistics
   */
  getStats() {
    return {
      connectedClients: this.clients.size,
      activeRooms: this.rooms.size,
      totalRoomMembers: Array.from(this.rooms.values())
        .reduce((sum, room) => sum + room.size, 0)
    };
  }

  /**
   * Shutdown server
   */
  shutdown() {
    console.log('Shutting down server...');

    // Close all client connections
    for (const client of this.clients.values()) {
      client.ws.close(1001, 'Server shutdown');
    }

    // Close server
    this.wss.close(() => {
      this.server.close(() => {
        console.log('Server shut down');
      });
    });
  }
}

// Usage example
const server = new GameWebSocketServer(8080);

// Register message handlers
server.on('join_game', (connectionId, message, client) => {
  const { playerName, roomId } = message;

  client.playerName = playerName;
  server.joinRoom(connectionId, roomId || 'default');

  // Send current players in room
  const room = server.rooms.get(client.roomId);
  const players = Array.from(room).map(id => {
    const c = server.clients.get(id);
    return { connectionId: id, playerName: c.playerName };
  });

  server.sendToClient(connectionId, {
    type: 'room_joined',
    roomId: client.roomId,
    players
  });
});

server.on('player_input', (connectionId, message, client) => {
  // Broadcast player input to room
  server.broadcastToRoom(client.roomId, {
    type: 'player_input',
    connectionId,
    input: message.input,
    timestamp: message.timestamp
  }, connectionId);
});

server.on('chat_message', (connectionId, message, client) => {
  // Broadcast chat to room
  server.broadcastToRoom(client.roomId, {
    type: 'chat_message',
    playerName: client.playerName,
    message: message.text,
    timestamp: Date.now()
  });
});

// Start server
server.start();

console.log('Game server started');
console.log(`Stats: ${JSON.stringify(server.getStats())}`);
```

**Claude Code Prompt:**
```
Create a production-ready WebSocket server using Node.js that handles multiple
clients, room-based messaging, broadcast functionality, connection health
monitoring with ping/pong, and graceful shutdown. Include statistics tracking
and connection management.
```

## Message Protocol Design

Efficient message protocols minimize bandwidth while remaining debuggable.

### JSON Message Protocol

```javascript
// Message structure for different game events
const MessageProtocol = {
  // Client -> Server
  JOIN_GAME: {
    type: 'join_game',
    playerName: String,
    roomId: String
  },

  PLAYER_INPUT: {
    type: 'player_input',
    input: {
      keys: Object,      // { w: true, a: false, ... }
      mouse: Object,     // { x: 100, y: 200, button: 0 }
      sequence: Number   // Input sequence number for reconciliation
    },
    timestamp: Number
  },

  // Server -> Client
  GAME_STATE: {
    type: 'game_state',
    tick: Number,
    timestamp: Number,
    entities: [
      {
        id: String,
        type: String,      // 'player', 'enemy', 'projectile'
        x: Number,
        y: Number,
        vx: Number,        // velocity
        vy: Number,
        rotation: Number,
        health: Number
      }
    ]
  },

  // Bidirectional
  CHAT_MESSAGE: {
    type: 'chat_message',
    playerName: String,
    message: String,
    timestamp: Number
  }
};

/**
 * Message validator
 */
class MessageValidator {
  static validate(message, schema) {
    if (!message || typeof message !== 'object') {
      return { valid: false, error: 'Invalid message format' };
    }

    if (message.type !== schema.type) {
      return { valid: false, error: 'Type mismatch' };
    }

    // Add specific validation logic here

    return { valid: true };
  }
}
```

## Reconnection Handling

Proper reconnection preserves game state and player progress.

### Reconnection System

```javascript
class ReconnectionManager {
  constructor(server) {
    this.server = server;
    this.disconnectedPlayers = new Map(); // playerId -> player data
    this.reconnectionTimeout = 60000; // 60 seconds
  }

  /**
   * Handle player disconnection
   */
  onDisconnect(connectionId) {
    const client = this.server.clients.get(connectionId);
    if (!client || !client.playerId) return;

    // Store player data for reconnection
    const playerData = {
      playerId: client.playerId,
      playerName: client.playerName,
      roomId: client.roomId,
      disconnectedAt: Date.now(),
      gameState: this.capturePlayerState(client)
    };

    this.disconnectedPlayers.set(client.playerId, playerData);

    // Set timeout to remove player data
    setTimeout(() => {
      if (this.disconnectedPlayers.has(client.playerId)) {
        console.log(`Player ${client.playerId} reconnection timeout`);
        this.disconnectedPlayers.delete(client.playerId);

        // Notify room that player is permanently gone
        this.server.broadcastToRoom(playerData.roomId, {
          type: 'player_disconnected',
          playerId: client.playerId
        });
      }
    }, this.reconnectionTimeout);

    console.log(`Player ${client.playerId} disconnected, waiting for reconnection`);
  }

  /**
   * Handle player reconnection
   */
  onReconnect(connectionId, playerId) {
    const playerData = this.disconnectedPlayers.get(playerId);
    if (!playerData) {
      return { success: false, error: 'No reconnection data found' };
    }

    const client = this.server.clients.get(connectionId);
    if (!client) {
      return { success: false, error: 'Invalid connection' };
    }

    // Restore player data
    client.playerId = playerData.playerId;
    client.playerName = playerData.playerName;

    // Rejoin room
    this.server.joinRoom(connectionId, playerData.roomId);

    // Remove from disconnected list
    this.disconnectedPlayers.delete(playerId);

    console.log(`Player ${playerId} reconnected after ${Date.now() - playerData.disconnectedAt}ms`);

    // Send restored state to client
    return {
      success: true,
      playerData: playerData.gameState,
      roomId: playerData.roomId
    };
  }

  /**
   * Capture player state for restoration
   */
  capturePlayerState(client) {
    // Capture relevant game state
    // This depends on your game implementation
    return {
      position: client.position,
      health: client.health,
      inventory: client.inventory,
      // ... other game state
    };
  }
}

// Server-side usage
const reconnectionManager = new ReconnectionManager(server);

server.on('disconnect', (connectionId) => {
  reconnectionManager.onDisconnect(connectionId);
});

server.on('reconnect', (connectionId, message) => {
  const result = reconnectionManager.onReconnect(connectionId, message.playerId);

  server.sendToClient(connectionId, {
    type: 'reconnection_result',
    ...result
  });
});
```

**Claude Code Prompt:**
```
Create a reconnection system that temporarily stores player state when
disconnected, allows players to rejoin within a timeout period, and
restores their game state. Handle reconnection expiry and cleanup.
```

## Best Practices

1. **Always validate messages server-side** - Never trust client data
2. **Use message type routing** - Clean, maintainable message handling
3. **Implement heartbeats** - Detect connection loss early
4. **Handle reconnection** - Players disconnect frequently
5. **Queue messages during disconnection** - Don't lose important updates
6. **Use exponential backoff** - Prevents server hammering during issues
7. **Log everything** - Essential for debugging network issues
8. **Monitor connection health** - Track latency, packet loss
9. **Implement rate limiting** - Prevent message flooding
10. **Graceful shutdown** - Close connections cleanly

## Cross-References

- [Client-Server Architecture](./client-server-architecture.md) - Architectural patterns
- [State Synchronization](./state-synchronization.md) - Syncing game state
- [Lag Compensation](./lag-compensation.md) - Handling latency
- [Core Game Concepts](../02-core-game-concepts/README.md) - Game loop integration

## Summary

WebSocket implementation provides the foundation for multiplayer games. Master these concepts:

- Client-side connection management with automatic reconnection
- Server-side client handling with room support
- Message protocol design and validation
- Heartbeat systems for connection health
- Reconnection handling for seamless player experience
- Error handling and logging for production reliability

With solid WebSocket implementation, you can build responsive, reliable multiplayer experiences. Claude Code helps create production-ready WebSocket systems efficiently, letting you focus on game mechanics rather than networking infrastructure.
