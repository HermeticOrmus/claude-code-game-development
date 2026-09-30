---
name: audio-patterns
description: "Game audio code patterns: a Godot bus layout, an audio player pool, randomized one-shot playback, vertical-remix dynamic music, 3D occlusion approximation, and FMOD integration in Godot. Use when writing sound playback, music, or mixing code for a game."
---

# Audio Patterns

## Audio Bus Architecture (Godot)

```gdscript
# AudioBusLayout setup - configure programmatically or in AudioBusLayout editor
# Bus hierarchy: Master -> Music, SFX, Voice, Ambient
# Each sub-bus routes to Master, apply effects on sub-buses

class_name AudioManager extends Node
# Bus names must match AudioBusLayout asset
const BUS_MASTER  := &"Master"
const BUS_MUSIC   := &"Music"
const BUS_SFX     := &"SFX"
const BUS_VOICE   := &"Voice"
const BUS_AMBIENT := &"Ambient"

func set_music_volume(db: float) -> void:
    var bus_idx := AudioServer.get_bus_index(BUS_MUSIC)
    AudioServer.set_bus_volume_db(bus_idx, db)

func duck_music(duck_db: float = -12.0, duration: float = 0.3) -> void:
    # Duck music when important SFX or voice plays
    var bus_idx := AudioServer.get_bus_index(BUS_MUSIC)
    var tween := create_tween()
    tween.tween_method(
        func(v: float): AudioServer.set_bus_volume_db(bus_idx, v),
        AudioServer.get_bus_volume_db(bus_idx),
        duck_db,
        duration
    )

func unduck_music(duration: float = 0.5) -> void:
    var bus_idx := AudioServer.get_bus_index(BUS_MUSIC)
    var tween := create_tween()
    tween.tween_method(
        func(v: float): AudioServer.set_bus_volume_db(bus_idx, v),
        AudioServer.get_bus_volume_db(bus_idx),
        0.0,
        duration
    )
```

## Audio Pool Implementation

```gdscript
# Fixed-size audio pool prevents per-sound node allocation
class_name AudioPool extends Node
const POOL_SIZE := 16

var _players: Array[AudioStreamPlayer] = []
var _priorities: Array[float] = []

func _ready() -> void:
    for i in POOL_SIZE:
        var player := AudioStreamPlayer.new()
        player.bus = &"SFX"
        add_child(player)
        player.finished.connect(_on_player_finished.bind(i))
        _players.append(player)
        _priorities.append(0.0)

func play(stream: AudioStream, volume_db: float = 0.0, priority: float = 1.0) -> AudioStreamPlayer:
    # Find free player
    for i in POOL_SIZE:
        if not _players[i].playing:
            return _start_player(i, stream, volume_db, priority)

    # Pool exhausted: steal lowest priority
    var lowest_idx := 0
    for i in POOL_SIZE:
        if _priorities[i] < _priorities[lowest_idx]:
            lowest_idx = i
    return _start_player(lowest_idx, stream, volume_db, priority)

func _start_player(idx: int, stream: AudioStream, volume_db: float, priority: float) -> AudioStreamPlayer:
    _players[idx].stream = stream
    _players[idx].volume_db = volume_db
    _players[idx].play()
    _priorities[idx] = priority
    return _players[idx]

func _on_player_finished(idx: int) -> void:
    _priorities[idx] = 0.0

# 3D variant - takes world position for spatialized pool
class AudioPool3D extends Node:
    # Same pattern but uses AudioStreamPlayer3D with position assignment
    pass
```

## Randomized Sound Playback

```gdscript
# Prevents "machine gun effect" - repeated identical sounds
class_name RandomizedAudioPlayer extends Node
@export var streams: Array[AudioStream]
@export var pitch_range: Vector2 = Vector2(0.9, 1.1)
@export var volume_range_db: Vector2 = Vector2(-3.0, 0.0)
@export var bus: StringName = &"SFX"

var _last_index: int = -1

func play_random() -> void:
    if streams.is_empty():
        return
    # Avoid playing the same clip twice in a row
    var idx := randi() % streams.size()
    if streams.size() > 1 and idx == _last_index:
        idx = (idx + 1) % streams.size()
    _last_index = idx

    var player := AudioStreamPlayer.new()
    player.stream = streams[idx]
    player.pitch_scale = randf_range(pitch_range.x, pitch_range.y)
    player.volume_db = randf_range(volume_range_db.x, volume_range_db.y)
    player.bus = bus
    player.autoplay = true
    player.finished.connect(player.queue_free)
    add_child(player)
```

## Dynamic Music System (Vertical Remixing)

```gdscript
# Vertical remixing: multiple stems fade in/out based on game state
class_name MusicSystem extends Node
enum MusicState { EXPLORATION, TENSION, COMBAT, BOSS }

@export var stems: Dictionary = {
    # Format: stem_name -> AudioStreamPlayer
}

var _current_state: MusicState = MusicState.EXPLORATION
var _tween: Tween

# Stem volume levels per state [exploration, tension, combat, boss]
const STEM_LEVELS := {
    "drums":   [0.0,  0.5,  1.0,  1.0],
    "bass":    [0.3,  0.6,  1.0,  1.0],
    "melody":  [1.0,  0.8,  0.3,  0.0],
    "strings": [0.8,  0.5,  0.0,  0.0],
    "intense": [0.0,  0.2,  0.8,  1.0],
}

func set_music_state(state: MusicState, fade_time: float = 2.0) -> void:
    if state == _current_state:
        return
    _current_state = state

    if _tween:
        _tween.kill()
    _tween = create_tween()
    _tween.set_parallel(true)

    for stem_name in STEM_LEVELS:
        if not stems.has(stem_name):
            continue
        var target_volume: float = STEM_LEVELS[stem_name][state]
        var player: AudioStreamPlayer = stems[stem_name]
        # Convert 0-1 to dB (-80 = silent, 0 = full)
        var target_db := linear_to_db(target_volume) if target_volume > 0.0 else -80.0
        _tween.tween_property(player, "volume_db", target_db, fade_time)

# Beat-synchronized transition (horizontal re-sequencing)
func transition_at_next_bar(bpm: float, current_beat: float) -> void:
    var beat_duration := 60.0 / bpm
    var bar_duration := beat_duration * 4.0
    var beats_until_next_bar := 4.0 - fmod(current_beat, 4.0)
    var delay := beats_until_next_bar * beat_duration
    get_tree().create_timer(delay).timeout.connect(_crossfade_to_next_section)
```

## 3D Audio Occlusion Approximation

```gdscript
# Simple raycast occlusion - attenuates audio through walls
class_name AudioOcclusionSystem extends Node
@export var occlude_db_per_wall: float = -12.0
@export var max_walls: int = 3
@export var update_rate_hz: float = 10.0  # Don't update every frame

var _timer: float = 0.0
var _listener: Node3D

func _physics_process(delta: float) -> void:
    _timer += delta
    if _timer < 1.0 / update_rate_hz:
        return
    _timer = 0.0
    _update_occlusion()

func _update_occlusion() -> void:
    if not _listener:
        _listener = get_viewport().get_camera_3d()
        if not _listener:
            return

    var space := get_world_3d().direct_space_state
    for child in get_children():
        if child is AudioStreamPlayer3D:
            _occlude_player(child, space)

func _occlude_player(player: AudioStreamPlayer3D, space: PhysicsDirectSpaceState3D) -> void:
    var from := _listener.global_position
    var to := player.global_position
    var params := PhysicsRayQueryParameters3D.create(from, to, 0b0001)  # environment layer
    params.hit_back_faces = true

    var walls := 0
    var pos := from
    while walls < max_walls:
        var result := space.intersect_ray(params)
        if not result:
            break
        walls += 1
        params.from = result.position + (to - pos).normalized() * 0.01

    # Apply occlusion as volume offset (player's base volume + occlusion)
    player.volume_db = player.volume_db + (occlude_db_per_wall * walls)
```

## FMOD Integration Pattern (Godot GDNative/GDExtension)

```gdscript
# FMOD event playback via GDExtension wrapper (e.g., fmod-gdextension)
class_name FMODAudioManager extends Node
# Assumes fmod-gdextension is installed and FMOD singleton available

func play_one_shot(event_path: String, position: Vector3 = Vector3.ZERO) -> void:
    # 2D event (UI, music - no position)
    if position == Vector3.ZERO:
        FMOD.play_one_shot(event_path)
    else:
        # 3D spatialized event
        FMOD.play_one_shot_at_position(event_path, position)

func create_instance(event_path: String) -> Object:
    return FMOD.create_event_instance(event_path)

func set_combat_intensity(intensity: float) -> void:
    # Drive FMOD global parameter from game state (0.0 = calm, 1.0 = intense)
    FMOD.set_global_parameter_by_name("CombatIntensity", intensity)
```

## Anti-Patterns

- **AudioStreamPlayer per sound effect**: Creates and destroys nodes every sound. Use the AudioPool pattern above.
- **Hard stop on music change**: Always crossfade. A 0.5-2 second overlap eliminates perceived cuts.
- **All sounds on Master bus**: No independent volume control, no effects chain separation, no ducking.
- **Identical pitch footsteps**: Monotonous. Randomize pitch 0.9-1.1 and cycle through 3-5 variants.
- **3D audio with default max_distance=0**: Godot default is 0 = no distance limit. Always set max_distance for 3D emitters.
