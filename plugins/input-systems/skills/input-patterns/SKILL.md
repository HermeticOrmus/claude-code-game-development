---
name: input-patterns
description: "Game input code patterns: Godot InputMap actions, a scaled radial deadzone, jump buffer with coyote time, rebinding serialization, a mobile virtual joystick, and gamepad rumble. Use when implementing controls, remapping, or controller feel."
---

# Input Patterns

## Godot InputMap Action Configuration

```gdscript
# Define input actions programmatically (useful for testing/CI or runtime setup)
# Normally done in Project Settings > InputMap, but here for reference:

func _setup_default_bindings() -> void:
    # Movement actions
    _add_action_with_keys(&"move_forward", KEY_W, JOY_BUTTON_INVALID, -1, JOY_AXIS_LEFT_Y)
    _add_action_with_keys(&"move_back",    KEY_S, JOY_BUTTON_INVALID,  1, JOY_AXIS_LEFT_Y)
    _add_action_with_keys(&"move_left",    KEY_A, JOY_BUTTON_INVALID, -1, JOY_AXIS_LEFT_X)
    _add_action_with_keys(&"move_right",   KEY_D, JOY_BUTTON_INVALID,  1, JOY_AXIS_LEFT_X)
    _add_action_with_keys(&"jump",         KEY_SPACE, JOY_BUTTON_A, 0.0, -1)
    _add_action_with_keys(&"interact",     KEY_E, JOY_BUTTON_X, 0.0, -1)

func _add_action_with_keys(
    action: StringName,
    key: Key,
    joy_button: JoyButton,
    axis_value: float = 0.0,
    joy_axis: JoyAxis = JOY_AXIS_INVALID
) -> void:
    if not InputMap.has_action(action):
        InputMap.add_action(action, 0.15)  # 0.15 = deadzone for this action

    if key != KEY_NONE:
        var key_event := InputEventKey.new()
        key_event.keycode = key
        InputMap.action_add_event(action, key_event)

    if joy_button != JOY_BUTTON_INVALID:
        var button_event := InputEventJoypadButton.new()
        button_event.button_index = joy_button
        InputMap.action_add_event(action, button_event)
```

## Scaled Radial Deadzone

```gdscript
# Correctly apply radial deadzone with remapping
class_name InputDeadzone

static func apply_radial(raw: Vector2, inner: float = 0.15, outer: float = 0.95) -> Vector2:
    var magnitude := raw.length()

    if magnitude < inner:
        return Vector2.ZERO

    if magnitude > outer:
        return raw.normalized()

    # Remap [inner, outer] -> [0, 1] for smooth transition
    var remapped := (magnitude - inner) / (outer - inner)
    return raw.normalized() * remapped

# Usage in character controller:
func _physics_process(_delta: float) -> void:
    var raw := Input.get_vector(&"move_left", &"move_right", &"move_forward", &"move_back")
    var input := InputDeadzone.apply_radial(raw)
    # input is now clean with no dead zone artifact
```

## Input Buffering (Jump Buffer + Coyote Time)

```gdscript
class_name PlatformerInput extends Node
const JUMP_BUFFER_FRAMES: int = 8   # frames to remember jump input
const COYOTE_FRAMES: int = 6        # frames after leaving platform to still jump

var _jump_buffer: int = 0           # frames remaining in jump buffer
var _coyote_timer: int = 0          # frames remaining in coyote time
var _was_on_floor: bool = false

@onready var body: CharacterBody3D = get_parent()

func _physics_process(_delta: float) -> void:
    _update_coyote_time()
    _update_jump_buffer()

func _update_coyote_time() -> void:
    if body.is_on_floor():
        _coyote_timer = COYOTE_FRAMES
        _was_on_floor = true
    elif _was_on_floor:
        _coyote_timer = max(0, _coyote_timer - 1)

func _update_jump_buffer() -> void:
    if Input.is_action_just_pressed(&"jump"):
        _jump_buffer = JUMP_BUFFER_FRAMES
    elif _jump_buffer > 0:
        _jump_buffer -= 1

func consume_jump() -> bool:
    # Returns true if a buffered jump should execute
    if _jump_buffer > 0 and _coyote_timer > 0:
        _jump_buffer = 0
        _coyote_timer = 0
        _was_on_floor = false
        return true
    return false
```

## Input Rebinding Serialization

```gdscript
class_name InputRebinder extends Node
const SAVE_PATH := "user://input_bindings.cfg"

var _default_bindings: Dictionary = {}

func _ready() -> void:
    # Cache defaults at startup before any user changes
    for action in InputMap.get_actions():
        if not action.begins_with("ui_"):  # Skip UI actions
            _default_bindings[action] = InputMap.action_get_events(action).duplicate()

func save_bindings() -> void:
    var config := ConfigFile.new()
    for action in InputMap.get_actions():
        if action.begins_with("ui_"):
            continue
        var events := InputMap.action_get_events(action)
        var event_data: Array[Dictionary] = []
        for event in events:
            event_data.append(_serialize_event(event))
        config.set_value("bindings", action, event_data)
    config.save(SAVE_PATH)

func load_bindings() -> void:
    var config := ConfigFile.new()
    if config.load(SAVE_PATH) != OK:
        return
    for action in config.get_section_keys("bindings"):
        var event_data: Array = config.get_value("bindings", action, [])
        InputMap.action_erase_events(action)
        for data in event_data:
            var event := _deserialize_event(data)
            if event:
                InputMap.action_add_event(action, event)

func reset_to_defaults() -> void:
    for action in _default_bindings:
        InputMap.action_erase_events(action)
        for event in _default_bindings[action]:
            InputMap.action_add_event(action, event)

func _serialize_event(event: InputEvent) -> Dictionary:
    if event is InputEventKey:
        return {"type": "key", "keycode": (event as InputEventKey).keycode}
    elif event is InputEventJoypadButton:
        return {"type": "joy_button", "button_index": (event as InputEventJoypadButton).button_index}
    elif event is InputEventJoypadMotion:
        var e := event as InputEventJoypadMotion
        return {"type": "joy_axis", "axis": e.axis, "axis_value": e.axis_value}
    return {}

func _deserialize_event(data: Dictionary) -> InputEvent:
    match data.get("type", ""):
        "key":
            var e := InputEventKey.new()
            e.keycode = data["keycode"] as Key
            return e
        "joy_button":
            var e := InputEventJoypadButton.new()
            e.button_index = data["button_index"] as JoyButton
            return e
        "joy_axis":
            var e := InputEventJoypadMotion.new()
            e.axis = data["axis"] as JoyAxis
            e.axis_value = data["axis_value"]
            return e
    return null
```

## Virtual Joystick for Mobile

```gdscript
class_name VirtualJoystick extends Control
signal input_vector_changed(vector: Vector2)

@export var deadzone_radius: float = 10.0   # pixels
@export var outer_radius: float = 60.0      # pixels

var _touch_index: int = -1
var _origin: Vector2 = Vector2.ZERO
var _current_vector: Vector2 = Vector2.ZERO

func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        var touch := event as InputEventScreenTouch
        if touch.pressed and _touch_index == -1:
            if get_rect().has_point(touch.position):
                _touch_index = touch.index
                _origin = touch.position
        elif not touch.pressed and touch.index == _touch_index:
            _touch_index = -1
            _current_vector = Vector2.ZERO
            input_vector_changed.emit(_current_vector)

    elif event is InputEventScreenDrag:
        var drag := event as InputEventScreenDrag
        if drag.index == _touch_index:
            var offset := drag.position - _origin
            var magnitude := offset.length()
            if magnitude < deadzone_radius:
                _current_vector = Vector2.ZERO
            else:
                _current_vector = offset.normalized() * clampf(
                    (magnitude - deadzone_radius) / (outer_radius - deadzone_radius),
                    0.0, 1.0
                )
            input_vector_changed.emit(_current_vector)
```

## Gamepad Rumble Patterns

```gdscript
class_name RumbleManager extends Node
# XInput motors: weak = high-frequency (detail), strong = low-frequency (impact)

func rumble_impact(device: int = 0) -> void:
    # Short sharp impact (sword hit, gunshot)
    Input.start_joy_vibration(device, 0.0, 1.0, 0.1)

func rumble_damage(device: int = 0) -> void:
    # Player took damage - medium duration
    Input.start_joy_vibration(device, 0.6, 0.4, 0.3)

func rumble_explosion(device: int = 0) -> void:
    # Large explosion - full both motors fading
    Input.start_joy_vibration(device, 1.0, 1.0, 0.5)
    # Optionally tween intensity down
    var tween := create_tween()
    tween.tween_interval(0.2)
    tween.tween_callback(func(): Input.start_joy_vibration(device, 0.3, 0.3, 0.3))

func stop_rumble(device: int = 0) -> void:
    Input.stop_joy_vibration(device)
```

## Anti-Patterns

- **Raw key/button polling**: Never `if Input.is_key_pressed(KEY_W)` in gameplay code. Use `Input.is_action_pressed(&"move_forward")`. Raw key polling breaks rebinding.
- **Axial deadzone on analog sticks**: Axial deadzone creates diagonal bias. Use scaled radial deadzone.
- **Jump with no buffer**: `is_action_just_pressed()` misses frames. Players report "jump doesn't work." Implement 8-frame jump buffer minimum.
- **Saving full InputEvent objects**: InputEvent is a Godot object, not serializable to JSON. Serialize to typed dictionaries (keycode, button_index).
- **One-size deadzone**: Console controllers vary from 0.1 to 0.25 natural deadzone. Expose deadzone as a user-configurable setting.
