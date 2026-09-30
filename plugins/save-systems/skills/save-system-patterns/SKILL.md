---
name: save-system-patterns
description: "Save system code patterns: a core save manager, a save data model, slot metadata for load screens, and settings persistence kept separate from game saves. Use when implementing saving and loading in a game."
---

# Save System Patterns

## Core Save Manager

```gdscript
# Save system with versioning, atomic writes, and migration
class_name SaveManager extends Node

const SAVE_DIR := "user://"
const SAVE_VERSION := 2  # Increment when save schema changes

func save_game(slot: int, data: Dictionary) -> Error:
    var path := _get_save_path(slot)
    var tmp_path := path + ".tmp"

    # Add metadata
    data["version"] = SAVE_VERSION
    data["timestamp"] = Time.get_unix_time_from_system()

    var file := FileAccess.open(tmp_path, FileAccess.WRITE)
    if not file:
        return FileAccess.get_open_error()

    file.store_string(JSON.stringify(data, "\t"))
    file.close()

    # Backup existing save before replacing
    if FileAccess.file_exists(path):
        DirAccess.copy_absolute(path, path + ".bak")

    # Atomic rename: if crash happens before this, .tmp exists but save is intact
    var dir := DirAccess.open(SAVE_DIR)
    return dir.rename(tmp_path.get_file(), path.get_file())

func load_game(slot: int) -> Dictionary:
    var path := _get_save_path(slot)
    if not FileAccess.file_exists(path):
        return {}

    var file := FileAccess.open(path, FileAccess.READ)
    if not file:
        return {}

    var parsed := JSON.parse_string(file.get_as_text())
    if not parsed is Dictionary:
        push_error("Save file corrupt at slot %d, trying backup" % slot)
        return _load_backup(slot)

    return _migrate(parsed)

func _migrate(data: Dictionary) -> Dictionary:
    var version: int = data.get("version", 0)
    if version < 1:
        data = _migrate_v0_to_v1(data)
    if version < 2:
        data = _migrate_v1_to_v2(data)
    return data

func _migrate_v0_to_v1(data: Dictionary) -> Dictionary:
    # Example: v0 stored health as "hp", v1 uses "health"
    if "hp" in data:
        data["health"] = data["hp"]
        data.erase("hp")
    data["version"] = 1
    return data

func _migrate_v1_to_v2(data: Dictionary) -> Dictionary:
    # Example: v1 had no settings section
    if "settings" not in data:
        data["settings"] = {"volume_master": 1.0, "fullscreen": false}
    data["version"] = 2
    return data

func _load_backup(slot: int) -> Dictionary:
    var backup_path := _get_save_path(slot) + ".bak"
    if not FileAccess.file_exists(backup_path):
        return {}
    var file := FileAccess.open(backup_path, FileAccess.READ)
    if not file:
        return {}
    var parsed := JSON.parse_string(file.get_as_text())
    return parsed if parsed is Dictionary else {}

func _get_save_path(slot: int) -> String:
    return "user://save_%d.json" % slot

func delete_save(slot: int) -> void:
    var path := _get_save_path(slot)
    if FileAccess.file_exists(path):
        DirAccess.remove_absolute(path)
    if FileAccess.file_exists(path + ".bak"):
        DirAccess.remove_absolute(path + ".bak")
```

## Save Data Model

```gdscript
# Typed save data container - serialize/deserialize explicitly
class_name PlayerSaveData extends RefCounted

var health: float = 100.0
var max_health: float = 100.0
var position: Vector2 = Vector2.ZERO
var current_level: StringName = &"level_01"
var inventory: Array[StringName] = []
var flags: Dictionary = {}  # quest flags, doors opened, etc.
var playtime: float = 0.0

func to_dict() -> Dictionary:
    return {
        "health": health,
        "max_health": max_health,
        "position": {"x": position.x, "y": position.y},
        "current_level": str(current_level),
        "inventory": inventory.map(func(s): return str(s)),
        "flags": flags,
        "playtime": playtime,
    }

static func from_dict(d: Dictionary) -> PlayerSaveData:
    var data := PlayerSaveData.new()
    data.health = float(d.get("health", 100.0))
    data.max_health = float(d.get("max_health", 100.0))
    var pos: Dictionary = d.get("position", {})
    data.position = Vector2(float(pos.get("x", 0.0)), float(pos.get("y", 0.0)))
    data.current_level = StringName(d.get("current_level", "level_01"))
    data.inventory = Array(d.get("inventory", [])).map(func(s): return StringName(s))
    data.flags = d.get("flags", {})
    data.playtime = float(d.get("playtime", 0.0))
    return data
```

## Save Slot Metadata (for UI)

```gdscript
# Lightweight slot summary for save/load screen - no full deserialization needed
class_name SaveSlotMeta extends RefCounted

var slot: int
var exists: bool = false
var level_name: String = ""
var playtime_seconds: float = 0.0
var timestamp: float = 0.0

func get_playtime_display() -> String:
    var hours := int(playtime_seconds) / 3600
    var minutes := (int(playtime_seconds) % 3600) / 60
    return "%02d:%02d" % [hours, minutes]

func get_date_display() -> String:
    return Time.get_datetime_string_from_unix_time(int(timestamp)).substr(0, 10)

static func read(slot: int) -> SaveSlotMeta:
    var meta := SaveSlotMeta.new()
    meta.slot = slot
    var path := "user://save_%d.json" % slot
    if not FileAccess.file_exists(path):
        return meta  # exists = false
    var file := FileAccess.open(path, FileAccess.READ)
    if not file:
        return meta
    var parsed := JSON.parse_string(file.get_as_text())
    if not parsed is Dictionary:
        return meta
    meta.exists = true
    meta.level_name = str(parsed.get("current_level", "Unknown"))
    meta.playtime_seconds = float(parsed.get("playtime", 0.0))
    meta.timestamp = float(parsed.get("timestamp", 0.0))
    return meta
```

## Settings Persistence (Separate from Game Save)

```gdscript
# Settings use ConfigFile - separate from game saves so reset is safe
class_name GameSettings extends Node

const SETTINGS_PATH := "user://settings.cfg"

@export var volume_master: float = 1.0
@export var volume_music: float = 0.8
@export var volume_sfx: float = 1.0
@export var fullscreen: bool = false
@export var language: String = "en"

func save() -> void:
    var config := ConfigFile.new()
    config.set_value("audio", "volume_master", volume_master)
    config.set_value("audio", "volume_music", volume_music)
    config.set_value("audio", "volume_sfx", volume_sfx)
    config.set_value("display", "fullscreen", fullscreen)
    config.set_value("gameplay", "language", language)
    config.save(SETTINGS_PATH)

func load_settings() -> void:
    var config := ConfigFile.new()
    if config.load(SETTINGS_PATH) != OK:
        return  # Use defaults
    volume_master = config.get_value("audio", "volume_master", 1.0)
    volume_music = config.get_value("audio", "volume_music", 0.8)
    volume_sfx = config.get_value("audio", "volume_sfx", 1.0)
    fullscreen = config.get_value("display", "fullscreen", false)
    language = config.get_value("gameplay", "language", "en")
    _apply()

func _apply() -> void:
    AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Master"), linear_to_db(volume_master))
    DisplayServer.window_set_mode(
        DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED
    )
    TranslationServer.set_locale(language)
```

## Anti-Patterns

- **Saving node references**: Nodes are not serializable; they don't survive scene reload. Save data values (position, health, item IDs), never `NodePath` or `Node` objects.
- **No version field**: Adding a new key in v2 means v1 saves crash on load. Always include `"version": CURRENT_VERSION` and handle missing keys with `.get("key", default)`.
- **Direct file write**: Writing directly to save path without atomic tmp+rename means crash during write = corrupt file = player loses progress.
- **Mixing settings and game saves**: Settings reset should not erase game progress. Keep them in separate files.
- **ResourceSaver for save games**: `.tres` files are text-readable, easy to cheat, and break when GDScript class names change. Use explicit JSON serialization for save data.
