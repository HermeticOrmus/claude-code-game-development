---
description: "Build a HUD, menu, inventory, dialogue box, or accessibility options for a game"
argument-hint: "[hud|menu|inventory|dialogue|accessibility] <screen>"
---

# /game-ui

Game interface design and implementation: HUD, menus, inventory, dialogue, and accessibility.

## Trigger

`/game-ui [action] [target]`

## Actions

### `hud`
Design and implement HUD elements.

```
/game-ui hud "health bar with ghost damage effect for 2D action game"
/game-ui hud "ammo counter with reload indicator and grenade count"
/game-ui hud "boss health bar that appears at bottom when boss enters scene"
/game-ui hud "minimap in top-right corner with player dot and enemy markers"
```

**Output**: Godot Control scene structure, GDScript with signal-driven updates, CanvasLayer setup, Tween animations.

### `menu`
Build menu screens with controller navigation.

```
/game-ui menu "main menu: play, settings, quit - controller navigable"
/game-ui menu "pause menu with blur background effect"
/game-ui menu "settings menu with audio, video, controls tabs and live preview"
/game-ui menu "save/load screen with 3 slots showing level, playtime, date"
```

**Output**: MenuManager push/pop stack, Control scene hierarchy, focus_neighbor setup on all buttons, Tween entrance animations.

### `inventory`
Implement inventory systems.

```
/game-ui inventory "10x4 grid inventory with drag-and-drop item swapping"
/game-ui inventory "equipment screen with character preview and slot positions"
/game-ui inventory "hotbar with 8 slots and number key binding"
```

**Output**: InventorySlot with `_get_drag_data`/`_can_drop_data`/`_drop_data`, GridContainer layout, tooltip on hover.

### `dialogue`
Create dialogue display systems.

```
/game-ui dialogue "NPC dialogue box with typewriter effect, speaker portrait, skip"
/game-ui dialogue "choice menu with 3-4 options, keyboard/controller selectable"
/game-ui dialogue "subtitle system for all voiced lines"
```

**Output**: DialogueBox with typewriter tween, choice list with focus navigation, integration hooks for Dialogue Manager plugin.

### `accessibility`
Add accessibility features to existing UI.

```
/game-ui accessibility "colorblind mode: add icon indicators to color-coded elements"
/game-ui accessibility "text scaling: all fonts respond to accessibility size setting"
/game-ui accessibility "ensure all menus navigable with keyboard and controller"
```

**Output**: Theme modifications, font size scaling system, colorblind palette alternatives, focus navigation audit.

## Examples

**Building a complete HUD:**
```
/game-ui hud "top-left: health bar with ghost effect. Top-right: ammo. Bottom: ability cooldowns as radial fills"
```
Produces: CanvasLayer with MarginContainer, HealthBar with ghost ProgressBar + tween, AmmoDisplay label, AbilityCooldown radial TextureProgressBar. All update via signals from GameEvents autoload.

**Pause menu with blur:**
```
/game-ui menu "pause menu that blurs the game world behind it"
```
Produces: SubViewportContainer blur technique via CanvasLayer, resume/settings/main menu buttons, MenuManager push/pop integration.

## Control Hierarchy Guide

```
CanvasLayer (layer=1)            <- HUD root
  MarginContainer                <- Screen-edge padding
    HBoxContainer                <- Layout container
      HealthSection (VBox)       <- Health bar group
        HealthBar (ProgressBar)
        GhostBar (ProgressBar)
      AmmoSection (VBox)         <- Ammo group
        AmmoLabel (Label)
        ReloadBar (ProgressBar)
```

## Focus Navigation Checklist

Every interactive menu must pass this before shipping:
- [ ] First element has `grab_focus()` called on menu open
- [ ] All buttons have `focus_mode = FOCUS_ALL`
- [ ] `focus_neighbor_bottom/top/left/right` set to adjacent elements
- [ ] Tab and arrow keys cycle through all interactive elements
- [ ] No focus trap (player can always reach every element)
- [ ] Visual focus indicator is clearly visible (theme setting)
