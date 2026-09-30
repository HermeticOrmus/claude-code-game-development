---
name: game-ui-patterns
description: "Game UI code patterns: a HUD health bar, a menu state stack, an inventory grid with drag and drop, a typewriter dialogue box, a screen-edge-aware tooltip, and a settings menu with live preview. Use when implementing game interface screens in Godot."
---

# Game UI Patterns

## HUD Health Bar

```gdscript
# Health bar with smooth tween animation and damage flash
class_name HealthBar extends Control
@onready var fill_bar: ProgressBar = $FillBar
@onready var ghost_bar: ProgressBar = $GhostBar  # Lags behind for damage visualization
@onready var flash_overlay: ColorRect = $FlashOverlay

@export var ghost_tween_duration: float = 0.4
@export var flash_duration: float = 0.1

var _ghost_tween: Tween

func _ready() -> void:
    flash_overlay.modulate.a = 0.0

func set_health(current: float, maximum: float) -> void:
    var ratio := current / maximum
    fill_bar.value = ratio * 100.0

    # Flash red overlay
    var flash_tween := create_tween()
    flash_overlay.modulate.a = 0.5
    flash_tween.tween_property(flash_overlay, "modulate:a", 0.0, flash_duration)

    # Ghost bar lags behind with tween
    if _ghost_tween:
        _ghost_tween.kill()
    _ghost_tween = create_tween()
    _ghost_tween.tween_property(ghost_bar, "value", ratio * 100.0, ghost_tween_duration)\
        .set_delay(0.2)\
        .set_ease(Tween.EASE_IN)\
        .set_trans(Tween.TRANS_QUAD)
```

## Menu State Stack

```gdscript
# Push-down automaton for menu navigation
class_name MenuManager extends CanvasLayer
var _stack: Array[Control] = []

func push_menu(menu: Control) -> void:
    if not _stack.is_empty():
        _stack.back().visible = false
    _stack.append(menu)
    add_child(menu)
    menu.visible = true
    # Give focus to first focusable element
    var first_button := menu.find_child("*Button*", true, false) as Button
    if first_button:
        first_button.grab_focus()

func pop_menu() -> void:
    if _stack.is_empty():
        return
    var top := _stack.pop_back()
    top.queue_free()
    if not _stack.is_empty():
        _stack.back().visible = true
        var first_button := _stack.back().find_child("*Button*", true, false) as Button
        if first_button:
            first_button.grab_focus()

func clear_stack() -> void:
    for menu in _stack:
        menu.queue_free()
    _stack.clear()
```

## Inventory Grid with Drag-and-Drop

```gdscript
# Grid inventory slot - handles drag source and drop target
class_name InventorySlot extends Control
signal item_moved(from_slot: int, to_slot: int)

@export var slot_index: int = 0
@onready var item_icon: TextureRect = $ItemIcon
@onready var count_label: Label = $CountLabel

var _item_data: Dictionary = {}

func set_item(data: Dictionary) -> void:
    _item_data = data
    if data.is_empty():
        item_icon.texture = null
        count_label.visible = false
    else:
        item_icon.texture = data.get("icon") as Texture2D
        var count: int = data.get("count", 1)
        count_label.text = str(count)
        count_label.visible = count > 1

# Drag-and-drop API
func _get_drag_data(_at_position: Vector2) -> Variant:
    if _item_data.is_empty():
        return null
    var preview := TextureRect.new()
    preview.texture = item_icon.texture
    preview.size = Vector2(48, 48)
    set_drag_preview(preview)
    return {"slot_index": slot_index, "item": _item_data}

func _can_drop_data(_at_position: Vector2, data: Variant) -> bool:
    return data is Dictionary and "slot_index" in data

func _drop_data(_at_position: Vector2, data: Variant) -> void:
    var from_index: int = data["slot_index"]
    item_moved.emit(from_index, slot_index)
```

## Typewriter Dialogue Box

```gdscript
# Dialogue display with typewriter effect and skip support
class_name DialogueBox extends Control
@onready var text_label: RichTextLabel = $TextLabel
@onready var speaker_label: Label = $SpeakerLabel
@onready var continue_indicator: Control = $ContinueIndicator

@export var chars_per_second: float = 40.0

signal dialogue_advanced
signal dialogue_finished

var _full_text: String = ""
var _tween: Tween
var _is_typing: bool = false

func show_line(speaker: String, text: String) -> void:
    speaker_label.text = speaker
    text_label.text = ""
    _full_text = text
    continue_indicator.visible = false

    if _tween:
        _tween.kill()

    _is_typing = true
    var duration := float(text.length()) / chars_per_second
    _tween = create_tween()
    _tween.tween_method(_set_visible_characters, 0, text.length(), duration)
    _tween.tween_callback(func():
        _is_typing = false
        continue_indicator.visible = true
    )

func _set_visible_characters(count: int) -> void:
    text_label.text = _full_text.substr(0, count)

func advance() -> void:
    if _is_typing:
        # Skip typewriter - show full text immediately
        if _tween:
            _tween.kill()
        text_label.text = _full_text
        _is_typing = false
        continue_indicator.visible = true
    else:
        dialogue_advanced.emit()

func _unhandled_input(event: InputEvent) -> void:
    if visible and event.is_action_pressed(&"ui_accept"):
        advance()
```

## Screen-Edge-Aware Tooltip

```gdscript
# Tooltip that repositions to stay within screen bounds
class_name SmartTooltip extends PanelContainer
@onready var label: RichTextLabel = $Label

var _show_timer: Timer
var _target_item: Control

func _ready() -> void:
    visible = false
    _show_timer = Timer.new()
    _show_timer.wait_time = 0.35
    _show_timer.one_shot = true
    _show_timer.timeout.connect(_on_show_timer_timeout)
    add_child(_show_timer)

func request_show(item: Control, text: String) -> void:
    _target_item = item
    label.text = text
    _show_timer.start()

func hide_tooltip() -> void:
    _show_timer.stop()
    visible = false

func _on_show_timer_timeout() -> void:
    if not _target_item:
        return
    visible = true
    # Position at mouse, adjust to stay on screen
    var mouse_pos := get_viewport().get_mouse_position()
    var screen_size := get_viewport_rect().size
    var tooltip_size := size

    var pos := mouse_pos + Vector2(12, 12)
    if pos.x + tooltip_size.x > screen_size.x:
        pos.x = mouse_pos.x - tooltip_size.x - 12
    if pos.y + tooltip_size.y > screen_size.y:
        pos.y = mouse_pos.y - tooltip_size.y - 12

    global_position = pos
```

## Settings Menu with Live Preview

```gdscript
# Settings menu applies changes immediately for preview, reverts on cancel
class_name SettingsMenu extends Control
@onready var master_slider: HSlider = $AudioSection/MasterSlider
@onready var fullscreen_check: CheckButton = $DisplaySection/FullscreenCheck

var _saved_settings: Dictionary = {}

func _ready() -> void:
    # Store original values for cancel
    _saved_settings = {
        "volume_master": AudioServer.get_bus_volume_db(AudioServer.get_bus_index("Master")),
        "fullscreen": DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN,
    }
    master_slider.value = db_to_linear(AudioServer.get_bus_volume_db(0)) * 100.0
    fullscreen_check.button_pressed = _saved_settings["fullscreen"]

    master_slider.value_changed.connect(_on_volume_changed)
    fullscreen_check.toggled.connect(_on_fullscreen_toggled)

func _on_volume_changed(value: float) -> void:
    AudioServer.set_bus_volume_db(0, linear_to_db(value / 100.0))

func _on_fullscreen_toggled(pressed: bool) -> void:
    DisplayServer.window_set_mode(
        DisplayServer.WINDOW_MODE_FULLSCREEN if pressed else DisplayServer.WINDOW_MODE_WINDOWED
    )

func confirm() -> void:
    # Persist to settings file
    GameSettings.save()
    queue_free()

func cancel() -> void:
    # Restore original values
    AudioServer.set_bus_volume_db(0, _saved_settings["volume_master"])
    DisplayServer.window_set_mode(
        DisplayServer.WINDOW_MODE_FULLSCREEN if _saved_settings["fullscreen"]
        else DisplayServer.WINDOW_MODE_WINDOWED
    )
    queue_free()
```

## Anti-Patterns

- **Hardcoded pixel positions**: `position = Vector2(1200, 50)` breaks at different resolutions. Use anchors (0.0-1.0 of parent) + offsets for all UI positioning.
- **UI nodes without controller focus**: Mouse-only menus lock out gamepad/keyboard players. Set `focus_mode = Control.FOCUS_ALL` and `focus_neighbor_*` on every interactive element.
- **Updating UI every frame**: `label.text = str(score)` in `_process` triggers layout recalculation every frame. Update only on data change via signal.
- **No theme resource**: Hardcoded font sizes and colors across hundreds of Control nodes = unmaintainable. Define one Theme resource; apply globally.
- **Ignoring colorblind accessibility**: Red/green critical information (health OK vs damage) is invisible to ~8% of male players. Add shape/icon redundancy.
