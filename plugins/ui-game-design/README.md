# ui-game-design

Game UI plugin for LibreGameDev. Covers diegetic vs non-diegetic UI taxonomy, Godot Control anchoring and theme system, HUD composition with CanvasLayer, menu state stacks, inventory drag-and-drop, dialogue systems (Dialogue Manager, Ink), accessibility standards (colorblind, controller navigation, text scaling), and UI performance.

## UI Taxonomy

| Type | Lives In | Examples |
|------|----------|---------|
| Diegetic | Game world | Health bar on character, ammo on gun |
| Non-diegetic (HUD) | Screen overlay | Corner health bar, minimap, cooldowns |
| Meta | Outside game fiction | Pause menu, save screen, settings |
| Spatial | 3D world space | Floating enemy health bars, world tooltips |

## Components

- **game-ui-designer**: Agent with expertise in Godot Control system, HUD design, menu state machines, inventory systems, dialogue display, accessibility standards, and UI performance
- **game-ui**: Command for building HUD elements, menus with controller navigation, inventory grids, dialogue boxes, and accessibility improvements
- **game-ui-patterns**: Skill library with HealthBar (ghost tween), MenuManager (push/pop stack), InventorySlot (drag-and-drop API), TypewriterDialogueBox, SmartTooltip (screen-edge-aware), and SettingsMenu (live preview + cancel)

## Quick Start

Build a health bar:
```
/game-ui hud "animated health bar with red ghost effect showing damage taken"
```

Create a main menu:
```
/game-ui menu "main menu with Play, Settings, Quit - keyboard and controller navigable"
```

Add dialogue:
```
/game-ui dialogue "NPC dialogue with typewriter text, portrait, skip on confirm"
```

## Accessibility Baseline

Minimum requirements for every released game:
- All menus keyboard/controller navigable (no mouse required)
- No critical information communicated by color alone (colorblind)
- Subtitles for all dialogue
- Text size adjustable in settings
- Focus indicator visible when navigating with keyboard/controller
