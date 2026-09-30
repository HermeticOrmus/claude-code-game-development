---
description: "Configure, rebind, test, or polish a game's input system"
argument-hint: "[configure|rebind|test|polish] <controls or device>"
---

# /input-system

Input mapping, deadzone configuration, rebinding, input buffering, and multi-platform input support.

## Trigger

`/input-system [action] [target]`

## Actions

### `configure`
Set up InputMap actions with keyboard and gamepad bindings.

```
/input-system configure "third-person action game: move, jump, attack, dodge, interact, camera"
/input-system configure "RTS: select, multi-select, move, attack-move, camera pan/zoom"
/input-system configure "menu navigation with keyboard and gamepad d-pad"
```

**Output**: InputMap action list, default keyboard and gamepad bindings, GDScript configuration code.

### `rebind`
Implement input rebinding UI and serialization.

```
/input-system rebind "in-game keybinding menu with conflict detection"
/input-system rebind "save and load custom bindings to user:// directory"
/input-system rebind "reset to defaults button"
```

**Output**: InputRebinder GDScript, serialization format, conflict detection logic.

### `test`
Input buffering and game feel improvements.

```
/input-system test "jump feels unresponsive on controller"
/input-system test "attack combo drops inputs at high animation speed"
/input-system test "movement feels floaty on gamepad analog stick"
```

**Output**: Root cause analysis, buffer/coyote implementation, deadzone correction.

### `polish`
Platform-specific input polish: rumble, prompts, mobile touch.

```
/input-system polish "show correct button prompts for connected device (keyboard vs controller)"
/input-system polish "haptic rumble for player damage and attacks"
/input-system polish "mobile virtual joystick for movement"
```

**Output**: Device detection code, prompt switching system, rumble pattern library, or VirtualJoystick Control.

## Examples

**Implementing jump buffer + coyote time:**
```
/input-system test "platformer jump feels inconsistent on gamepad"
```
Produces: PlatformerInput node with 8-frame jump buffer and 6-frame coyote time, consume_jump() interface for CharacterBody3D.

**Dynamic controller prompt switching:**
```
/input-system polish "show Xbox prompts for gamepad, keyboard prompts for KBM"
```
Produces: Device detection using `Input.joy_connection_changed` signal, prompt texture atlas lookup, UI label that updates on device switch.

**Complete rebinding system:**
```
/input-system rebind "full rebinding menu with save/load"
```
Produces: InputRebinder class + UI template (VBoxContainer with action list, Listen button, conflict label).

## Deadzone Reference

| Deadzone Type | Formula | When to Use |
|--------------|---------|-------------|
| None | raw value | Mouse, keyboard |
| Axial | threshold per-axis | Simple but diagonal-biased |
| Radial | threshold on magnitude | Symmetric, better feel |
| Scaled Radial | remap [inner,outer] to [0,1] | Best: no deadspot at edge |

**Standard values**: inner=0.15, outer=0.95 for most controllers.

## Platform Action Naming Convention

Use semantic names, not device names:
```
# Wrong
"press_x_button" / "press_space"

# Correct
"jump", "attack_primary", "dodge", "interact", "open_map"
```

Semantic names survive rebinding, device switching, and platform porting.
