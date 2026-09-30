---
name: playtest-patterns
description: "Playtest instrumentation patterns: death heatmap collection, an analytics event schema, a time-per-zone tracker, a session guide template, and A/B test assignment. Use when adding telemetry to a build or preparing a playtest session."
---

# Playtest Patterns

## Death Heatmap Collection

```gdscript
# Collect and visualize death positions as a heatmap overlay
class_name DeathHeatmap extends Node2D
var _death_positions: Dictionary = {}  # Vector2i -> int (count)

@export var cell_size: int = 16  # Group deaths by cell size (pixels or world units)
@export var max_heat: int = 10   # Deaths at or above this = max color intensity
@export var heat_color_cold: Color = Color(0, 0, 1, 0.3)   # Blue = few deaths
@export var heat_color_hot: Color = Color(1, 0, 0, 0.7)    # Red = many deaths

func record_death(world_position: Vector2) -> void:
    var cell := Vector2i(int(world_position.x / cell_size), int(world_position.y / cell_size))
    _death_positions[cell] = _death_positions.get(cell, 0) + 1
    queue_redraw()
    _save_to_disk()  # Persist across sessions

func _draw() -> void:
    for cell in _death_positions:
        var count: int = _death_positions[cell]
        var heat := clampf(float(count) / float(max_heat), 0.0, 1.0)
        var color := heat_color_cold.lerp(heat_color_hot, heat)
        var rect := Rect2(
            Vector2(cell) * cell_size,
            Vector2(cell_size, cell_size)
        )
        draw_rect(rect, color)

func _save_to_disk() -> void:
    var file := FileAccess.open("user://death_heatmap.json", FileAccess.WRITE)
    if file:
        var serialized := {}
        for cell in _death_positions:
            serialized["%d,%d" % [cell.x, cell.y]] = _death_positions[cell]
        file.store_string(JSON.stringify(serialized))

func load_from_disk() -> void:
    var file := FileAccess.open("user://death_heatmap.json", FileAccess.READ)
    if not file:
        return
    var parsed := JSON.parse_string(file.get_as_text())
    if parsed is Dictionary:
        for key in parsed:
            var parts := key.split(",")
            var cell := Vector2i(int(parts[0]), int(parts[1]))
            _death_positions[cell] = int(parsed[key])
```

## Analytics Event Schema

```gdscript
# Structured analytics events for funnel and behavior analysis
class_name GameAnalytics extends Node
const ANALYTICS_FILE := "user://analytics_session.jsonl"  # JSON Lines format

var _session_id: String
var _session_start: float

func _ready() -> void:
    _session_id = _generate_session_id()
    _session_start = Time.get_unix_time_from_system()
    _log_event("session_start", {})

func _generate_session_id() -> String:
    return "%d_%d" % [Time.get_unix_time_from_system(), randi()]

func _log_event(event_type: String, data: Dictionary) -> void:
    var event := {
        "session_id": _session_id,
        "timestamp": Time.get_unix_time_from_system(),
        "elapsed": Time.get_unix_time_from_system() - _session_start,
        "event": event_type,
        "data": data
    }
    var file := FileAccess.open(ANALYTICS_FILE, FileAccess.READ_WRITE)
    if not file:
        file = FileAccess.open(ANALYTICS_FILE, FileAccess.WRITE)
    if file:
        file.seek_end()
        file.store_line(JSON.stringify(event))

# Specific event types
func log_player_death(position: Vector3, cause: StringName, level: StringName) -> void:
    _log_event("player_death", {
        "position": {"x": position.x, "y": position.y, "z": position.z},
        "cause": cause,
        "level": level,
    })

func log_level_complete(level: StringName, time_seconds: float, deaths: int) -> void:
    _log_event("level_complete", {
        "level": level,
        "time": time_seconds,
        "deaths": deaths,
    })

func log_mechanic_used(mechanic: StringName, context: StringName) -> void:
    _log_event("mechanic_used", {"mechanic": mechanic, "context": context})

func log_checkpoint_reached(checkpoint_id: StringName) -> void:
    _log_event("checkpoint", {"id": checkpoint_id})

func log_quit(reason: StringName = &"unknown") -> void:
    _log_event("session_end", {
        "reason": reason,
        "total_time": Time.get_unix_time_from_system() - _session_start,
    })
```

## Time-Per-Zone Tracker

```gdscript
# Measure how long players spend in each zone/room
class_name ZoneTimer extends Node
signal zone_completed(zone_id: StringName, time_seconds: float)

var _current_zone: StringName = &""
var _zone_enter_time: float = 0.0
var _zone_times: Dictionary = {}  # zone_id -> Array[float] (multiple sessions)

func enter_zone(zone_id: StringName) -> void:
    if _current_zone:
        _record_zone_exit()
    _current_zone = zone_id
    _zone_enter_time = Time.get_unix_time_from_system()

func exit_zone() -> void:
    _record_zone_exit()
    _current_zone = &""

func _record_zone_exit() -> void:
    if not _current_zone:
        return
    var elapsed := Time.get_unix_time_from_system() - _zone_enter_time
    if _current_zone not in _zone_times:
        _zone_times[_current_zone] = []
    _zone_times[_current_zone].append(elapsed)
    zone_completed.emit(_current_zone, elapsed)

func get_average_time(zone_id: StringName) -> float:
    if zone_id not in _zone_times or _zone_times[zone_id].is_empty():
        return 0.0
    var times: Array = _zone_times[zone_id]
    return times.reduce(func(acc, t): return acc + t, 0.0) / times.size()

func print_zone_report() -> void:
    for zone_id in _zone_times:
        var avg := get_average_time(zone_id)
        var count := _zone_times[zone_id].size()
        print("Zone %s: avg %.1fs over %d sessions" % [zone_id, avg, count])
```

## Playtest Session Guide Template

```markdown
# PLAYTEST SESSION GUIDE
## Game: [Game Name] | Version: [Build Number] | Date: [Date]

### TEST OBJECTIVES
1. Do players understand [specific mechanic] without explanation?
2. Do players find [specific area] navigation intuitive?
3. Does [specific challenge] feel appropriately difficult?

### SUCCESS CRITERIA
- 80% of testers complete tutorial section
- < 3 deaths average on [specific challenge]
- Players discover [hidden mechanic] before level end

### SESSION PROTOCOL
**Pre-session (5 minutes)**
- "Please play as you normally would. I'm observing the game, not testing you."
- "Please talk through what you're thinking as you play if you can."
- "I won't answer gameplay questions but I will answer technical problems."

**During session (45 minutes)**
Observer notes format:
[TIME] [PLAYER_ACTION] [VISIBLE_EMOTION] [WHAT_THEY_SAID]
Example: [04:32] Player missed jump platform 3rd time [frustration] "Why does this keep happening"

**Post-session (15 minutes)**
1. "Overall, how was that experience? (1-10)"
2. "What was the most confusing moment?"
3. "Was there anything you wanted to do that you couldn't figure out how?"
4. "What would make this most fun?"

### METRICS TO COLLECT (from analytics log)
- Deaths per level (heatmap)
- Time per zone
- Mechanics used (frequency)
- Checkpoint completion rate
```

## A/B Test Implementation

```gdscript
# Simple A/B test assignment - deterministic per player ID
class_name ABTest extends Node
enum Variant { CONTROL, VARIANT_A }

var _player_id: int
var _active_tests: Dictionary = {}  # test_name -> Variant

func _ready() -> void:
    # Use stable player identifier (not session-based)
    _player_id = _get_stable_player_id()

func get_variant(test_name: StringName) -> Variant:
    if test_name in _active_tests:
        return _active_tests[test_name]
    # Deterministic assignment: hash(player_id + test_name) % 2
    var hash_input := "%d_%s" % [_player_id, test_name]
    var variant := hash(hash_input) % 2
    _active_tests[test_name] = variant as Variant
    return variant as Variant

func _get_stable_player_id() -> int:
    var config := ConfigFile.new()
    config.load("user://player_id.cfg")
    var id: int = config.get_value("player", "id", 0)
    if id == 0:
        id = randi()
        config.set_value("player", "id", id)
        config.save("user://player_id.cfg")
    return id

# Usage:
# if ABTest.get_variant(&"enemy_health_rebalance") == ABTest.Variant.VARIANT_A:
#     enemy.health = 80  # Reduced health for variant group
# else:
#     enemy.health = 100  # Original for control group
```

## Anti-Patterns

- **Testing with developer friends**: Friends know the game, know you, and want to encourage you. Their feedback is systematically biased. Recruit strangers from target demographic.
- **Leading questions**: "Did you enjoy the combat system?" -> "What did you think of the combat?" Listen to what they say, not what you want to hear.
- **Fixing during session**: When tester gets stuck, resist coaching. The frustration IS the data. Note it; don't resolve it.
- **Too many metrics**: Collecting everything = analyzing nothing. Identify 3-5 specific questions per session, build metrics for those.
- **Single playtest session**: One round of playtesting with 5 people is a starting point. Iterate and test again. Minimum 3 rounds before launch.
