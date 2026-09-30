# input-systems

Input plugin for LibreGameDev. Covers Godot InputMap, Unity new Input System, gamepad deadzone mathematics, input buffering (jump buffer/coyote time), rebinding serialization, and mobile touch input.

## Components

- **input-engineer**: Agent with expertise in Godot InputMap, Unity Input Action Assets, deadzone math, buffering, and multi-platform input
- **input-system**: Command for configuring, rebinding, testing feel, and polishing platform-specific input
- **input-patterns**: Skill library with scaled radial deadzone, jump buffer + coyote time, InputMap configuration, rebinding serialization, virtual joystick, and rumble patterns

## Core Principle

All gameplay code polls actions by name, never by raw key/button:
```gdscript
# Always this:
Input.is_action_pressed(&"jump")
Input.get_vector(&"move_left", &"move_right", &"move_forward", &"move_back")

# Never this:
Input.is_key_pressed(KEY_SPACE)
Input.get_joy_axis(0, JOY_AXIS_LEFT_Y)
```

This makes rebinding, multi-platform support, and accessibility straightforward.

## Quick Start

Configure actions for a game:
```
/input-system configure "platformer: move left/right, jump, attack, dash"
```

Fix unresponsive jump:
```
/input-system test "jump feels inconsistent, sometimes doesn't register"
```

Add rebinding:
```
/input-system rebind "keybinding menu with conflict detection and save/load"
```
