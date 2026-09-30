---
name: multiplayer-networking
description: "Netcode reference patterns: a model comparison, a common mistakes catalog (rubber-banding, desync, bandwidth), delta encoding and quantization, reconciliation smoothing, a Unity library comparison, NAT traversal, and Godot MultiplayerSynchronizer, prediction, interpolation, and ENet setup. Use when writing or debugging networked game code."
---

# Multiplayer networking pattern library

Reference patterns for game multiplayer netcode.

## Netcode model comparison

| Model | Best for | Latency tolerance | Bandwidth | Determinism required |
|---|---|---|---|---|
| **Rollback** | Fighting games | Very tight | Low | Yes |
| **Lockstep** | RTS, lockstep RTS | Tolerant | Very low | Yes |
| **Client prediction + reconciliation** | FPS, MOBA, action | Medium | Medium | No |
| **Server-authoritative + interpolation** | Racing, MMO movement | Tolerant | Medium-high | No |
| **Pure state snapshots** | Slow-paced games | Very tolerant | High | No |

## Common mistakes catalog

### "Rubber-banding when player runs forward"

The player's client predicts forward motion. Server agrees and confirms. No rubber-band. Then player turns; client predicts turn; server says "no, you didn't turn yet" because the turn input hadn't reached the server when the server's last tick fired. Server position is one tick behind; client snaps back.

Fix: smooth reconciliation. When server position differs from predicted, interpolate over 100-200ms rather than snapping.

### "I shot them dead-on and missed"

Favor-the-target policy. Server's "current" state is what counts; if your shot took 50ms to reach the server, the target may have moved. Either:
- Switch to favor-the-shooter (lag compensation)
- Use projectile weapons (the projectile travels in server time, no compensation needed)

### "I was shot around a corner"

Favor-the-shooter policy working as intended. The shooter saw you at their lag-compensated time; you've since moved behind cover. You're dead on the server before you visually see the threat.

Mitigation: limit lag compensation window (e.g., 100ms max, not 250ms).

### "Multiplayer works in lab, breaks on mobile data"

Mobile cellular has higher jitter and occasional packet loss. Check:

- Tick rate too high for cellular bandwidth budget
- No packet loss tolerance (UDP without reliability layer)
- No connection migration on IP change (mobile data → WiFi)
- Power-save modes throttling background packets

### "Desync after 30 seconds in lockstep RTS"

Nondeterminism. Audit:

- Float math anywhere in game state → switch to fixed-point
- RNG → seed at game start, use same RNG instance for all clients
- Iteration order over collections → use ordered collections (List, sorted Dictionary)
- Time-based logic → use tick count, not wall clock
- Third-party libraries → check determinism guarantees

### "Bandwidth balloons at high player counts"

Need interest management:

- Don't replicate everyone to everyone
- Each client subscribes to entities within its area of interest (visible + nearby)
- Cell-based partitioning or proximity-based subscription

### "Rollback budget exceeded constantly"

Either:
- RTT too high for the chosen input delay; increase input delay
- State serialization is too slow; profile + optimize
- Game state contains nondeterministic elements making rollback impossible

### "Players desync on resume from sleep / app backgrounding"

Game logic kept advancing while suspended (timer-based), or stopped while suspended (frame-based). Either way, syncing the resumed client requires state download from server.

Pattern: on resume, request full state from server before resuming play.

## Bandwidth optimization patterns

### Delta encoding

```
Frame N state:  position = (100, 50, 200), rotation = 45deg, hp = 80
Frame N+1 state: position = (101, 50, 200), rotation = 45deg, hp = 80

Naive send: position + rotation + hp = ~16 bytes
Delta send: position.x changed = 4-byte field + 4-byte value = 8 bytes

Savings: ~50%. Compounds with quantization.
```

### Quantization

- Position: from 32-bit float to 16-bit fixed-point (sub-mm precision over 1km range): 50% size reduction
- Rotation: from quaternion to compressed quaternion (smallest 3 + sign bit): 4 bytes → ~1.4 bytes
- Velocity: 8-bit per axis when bounded: 32 bytes → 3 bytes
- Time stamps: relative to a known epoch, 16-bit fits ~64 seconds at 1ms precision

### Bit packing

```
Boolean state flags: is_jumping, is_attacking, is_grounded, is_alive
Naive: 4 bytes (one per bool)
Packed: 1 byte (4 bits used, 4 bits header)

State enum (8 states): 1 byte → 3 bits
```

### Priority queues

When bandwidth budget is tight:

```
Priorities:
  Critical (must arrive every tick): player position, HP
  High (every 2-3 ticks): held weapon, ammo
  Medium (every 5-10 ticks): outfit, secondary stats
  Low (every ~100 ticks): emote, name, distant NPCs

Bandwidth-constrained: send only critical + as much high/medium as fits in budget
```

## Reconciliation smoothing

```csharp
private const float SMOOTHING_TIME = 0.15f; // 150ms
private Vector3 _renderOffset = Vector3.zero;

private void OnReconcile(Vector3 serverPosition)
{
    // Don't snap to serverPosition. Save the offset.
    _renderOffset = transform.position - serverPosition;
    transform.position = serverPosition;
}

private void LateUpdate()
{
    // Decay the offset over SMOOTHING_TIME
    _renderOffset = Vector3.Lerp(_renderOffset, Vector3.zero, Time.deltaTime / SMOOTHING_TIME);
    transform.position += _renderOffset; // Visual position uses offset; logical position is correct
}
```

## Library comparison (Unity)

| Library | Type | Maturity | Recommendation |
|---|---|---|---|
| **Netcode for GameObjects (NGO)** | First-party from Unity | Active | Default for new projects |
| **Mirror** | Open source, community-maintained | Mature | When NGO doesn't fit your model |
| **FishNet** | Open source, performance focus | Mature | When you need raw performance |
| **Photon Fusion** | Commercial, hosted | Mature | When you want hosted matchmaking + rooms |
| **Nakama** | Open source backend, multi-engine | Mature | When you want generic multiplayer backend |
| **PlayFab** | Microsoft commercial | Mature | Enterprise / live ops focus |
| **Edgegap** | Dedicated server hosting | Mature | When you need dedicated server scaling |

For Godot: built-in MultiplayerAPI is solid for small projects. Nakama for larger projects + backend services.

For Unreal: built-in networking + replication graph is industry-standard.

## NAT traversal reference

| Connection type | Strategy |
|---|---|
| Both peers same LAN | Direct connection |
| One peer has public IP | Direct to public peer |
| Both peers behind NAT (cone or restricted-cone) | STUN |
| Both peers behind symmetric NAT | TURN (relay through server) |
| ICE handles selection between STUN + TURN |

Steam's P2P API + Photon Cloud + Nakama all handle this for you. If self-hosting, integrate coturn (open source TURN server) or use Cloudflare's tier.

## Godot MultiplayerSynchronizer Setup

```gdscript
# Authoritative multiplayer character with MultiplayerSynchronizer
class_name NetworkedPlayer extends CharacterBody3D

@export var player_id: int = 0

# MultiplayerSynchronizer synchronizes these properties
# Configure in the Inspector on the MultiplayerSynchronizer node:
#   position: unreliable, always (smooth movement)
#   velocity: unreliable, always
#   health: reliable, on_change (critical state)
#   current_animation: reliable, on_change

@onready var sync: MultiplayerSynchronizer = $MultiplayerSynchronizer

func _ready() -> void:
    # Only process input for our own character
    set_physics_process(is_multiplayer_authority())

func _physics_process(delta: float) -> void:
    # Only runs on authority (local player or server)
    var input_dir := Input.get_vector(&"move_left", &"move_right", &"move_forward", &"move_back")
    velocity.x = input_dir.x * 6.0
    velocity.z = input_dir.y * 6.0
    if not is_on_floor():
        velocity.y -= 9.8 * delta
    move_and_slide()
    # MultiplayerSynchronizer broadcasts position/velocity to all peers automatically

# RPC call: client requests action, server validates and executes
@rpc("any_peer", "call_local", "reliable")
func request_attack(target_id: int) -> void:
    if not is_multiplayer_authority():
        return  # Only server processes this
    var target := get_node_or_null("/root/Game/Players/%d" % target_id)
    if target and _is_valid_target(target):
        _apply_damage.rpc(target_id, 10.0)

@rpc("authority", "call_local", "reliable")
func _apply_damage(target_id: int, amount: float) -> void:
    # Called on all clients from server authority
    if multiplayer.get_unique_id() == target_id:
        # Apply to self
        health -= amount
```

## Client-Side Prediction with Reconciliation

```gdscript
class_name PredictedPlayer extends CharacterBody3D
const MAX_PREDICTION_TICKS: int = 60  # 1 second buffer at 60Hz

# Input state snapshot for rollback
class InputSnapshot:
    var tick: int
    var input_vector: Vector2
    var jump_pressed: bool

# State snapshot for reconciliation
class StateSnapshot:
    var tick: int
    var position: Vector3
    var velocity: Vector3

var _pending_inputs: Array[InputSnapshot] = []
var _predicted_states: Array[StateSnapshot] = []
var _last_confirmed_tick: int = 0

func _physics_process(delta: float) -> void:
    var input := InputSnapshot.new()
    input.tick = multiplayer.get_remote_sender_id()  # Use tick counter
    input.input_vector = Input.get_vector(&"move_left", &"move_right", &"move_forward", &"move_back")
    input.jump_pressed = Input.is_action_just_pressed(&"jump")

    # Apply locally (prediction)
    _apply_input(input, delta)

    # Send to server
    _send_input_to_server.rpc_id(1, input.tick, input.input_vector, input.jump_pressed)

    # Store for reconciliation
    var state := StateSnapshot.new()
    state.tick = input.tick
    state.position = global_position
    state.velocity = velocity
    _predicted_states.append(state)
    _pending_inputs.append(input)

    # Trim old predictions
    while _predicted_states.size() > MAX_PREDICTION_TICKS:
        _predicted_states.pop_front()
        _pending_inputs.pop_front()

@rpc("authority", "call_local", "reliable")
func _receive_server_correction(confirmed_tick: int, server_position: Vector3, server_velocity: Vector3) -> void:
    # Find matching predicted state
    var mismatch_threshold := 0.1  # meters
    var predicted_state: StateSnapshot = null
    for state in _predicted_states:
        if state.tick == confirmed_tick:
            predicted_state = state
            break

    if not predicted_state:
        return

    if predicted_state.position.distance_to(server_position) > mismatch_threshold:
        # Reconciliation: rollback and re-simulate from confirmed state
        global_position = server_position
        velocity = server_velocity
        # Re-apply all unconfirmed inputs
        for input in _pending_inputs:
            if input.tick > confirmed_tick:
                _apply_input(input, 1.0 / 60.0)

    # Remove confirmed inputs
    _pending_inputs = _pending_inputs.filter(func(i): return i.tick > confirmed_tick)
    _predicted_states = _predicted_states.filter(func(s): return s.tick > confirmed_tick)

func _apply_input(input: InputSnapshot, delta: float) -> void:
    var direction := Vector3(input.input_vector.x, 0, input.input_vector.y).normalized()
    velocity.x = direction.x * 6.0
    velocity.z = direction.z * 6.0
    if not is_on_floor():
        velocity.y -= 9.8 * delta
    move_and_slide()
```

## Entity Interpolation for Remote Players

```gdscript
# Smooth remote player rendering with interpolation buffer
class_name InterpolatedRemotePlayer extends Node3D
const INTERPOLATION_DELAY: float = 0.1  # 100ms behind server time

class StateRecord:
    var timestamp: float
    var position: Vector3
    var rotation: Quaternion

var _state_buffer: Array[StateRecord] = []

func receive_state(position: Vector3, rotation: Quaternion) -> void:
    var record := StateRecord.new()
    record.timestamp = Time.get_unix_time_from_system()
    record.position = position
    record.rotation = rotation
    _state_buffer.append(record)
    # Keep buffer bounded
    if _state_buffer.size() > 20:
        _state_buffer.pop_front()

func _process(_delta: float) -> void:
    var render_time := Time.get_unix_time_from_system() - INTERPOLATION_DELAY

    # Find the two states surrounding render_time
    var prev: StateRecord = null
    var next: StateRecord = null

    for i in _state_buffer.size() - 1:
        if _state_buffer[i].timestamp <= render_time and _state_buffer[i + 1].timestamp >= render_time:
            prev = _state_buffer[i]
            next = _state_buffer[i + 1]
            break

    if prev and next:
        var t := (render_time - prev.timestamp) / (next.timestamp - prev.timestamp)
        global_position = prev.position.lerp(next.position, t)
        global_transform.basis = Basis(prev.rotation.slerp(next.rotation, t))
```

## Godot ENet Host/Client Setup

```gdscript
# Game session management
class_name NetworkManager extends Node
signal peer_connected(peer_id: int)
signal peer_disconnected(peer_id: int)
signal connection_failed

const DEFAULT_PORT: int = 28960
const MAX_PEERS: int = 8

func host_game(port: int = DEFAULT_PORT) -> void:
    var peer := ENetMultiplayerPeer.new()
    var error := peer.create_server(port, MAX_PEERS)
    if error != OK:
        push_error("Failed to create server: %d" % error)
        return
    multiplayer.multiplayer_peer = peer
    multiplayer.peer_connected.connect(_on_peer_connected)
    multiplayer.peer_disconnected.connect(_on_peer_disconnected)
    print("Hosting on port %d" % port)

func join_game(address: String, port: int = DEFAULT_PORT) -> void:
    var peer := ENetMultiplayerPeer.new()
    var error := peer.create_client(address, port)
    if error != OK:
        connection_failed.emit()
        return
    multiplayer.multiplayer_peer = peer
    multiplayer.connected_to_server.connect(_on_connected)
    multiplayer.connection_failed.connect(func(): connection_failed.emit())

func disconnect_game() -> void:
    if multiplayer.multiplayer_peer:
        multiplayer.multiplayer_peer.close()
    multiplayer.multiplayer_peer = null

func _on_peer_connected(peer_id: int) -> void:
    peer_connected.emit(peer_id)
    if multiplayer.is_server():
        _spawn_player_for_peer(peer_id)

func _on_peer_disconnected(peer_id: int) -> void:
    peer_disconnected.emit(peer_id)
    if multiplayer.is_server():
        _remove_player_for_peer(peer_id)

func _on_connected() -> void:
    print("Connected to server as peer %d" % multiplayer.get_unique_id())
```

## Anti-Patterns

- **Client-authoritative positions**: `rpc("any_peer")` to set position allows teleport hacks. Server sets positions; clients send inputs.
- **No jitter buffer**: Packets arrive out of order; applying immediately causes stutter. Buffer 2-4 ticks minimum.
- **Synchronizing `randf()` calls**: Random functions diverge across machines. Seed the RNG with network-synchronized seed and use deterministic sequence.
- **RPC every frame for all properties**: Use `MultiplayerSynchronizer` for frequent property sync. RPCs for one-time events only.
- **Trusting damage values from client**: `rpc_id(1, "apply_damage", 9999.0)`. Server always calculates damage from inputs, not from client-submitted values.

## Cross-references

- See `docs/06-networking-multiplayer/` for full reference manual: rollback, lockstep, prediction patterns
- See `docs/09-advanced-patterns/` for replication graph patterns
- See `docs/12-deployment-distribution/` for dedicated server hosting + matchmaking deployment
- See `monetization-ethics` plugin for ethical considerations in match-quality matchmaking
