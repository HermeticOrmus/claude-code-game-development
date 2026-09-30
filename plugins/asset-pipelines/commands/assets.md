---
description: "Import, atlas, optimize, or bundle game assets with the right settings per platform"
argument-hint: "[import|atlas|optimize|bundle] <assets or folder>"
---

# /assets

Asset import, optimization, atlasing, LOD, and compression pipeline management.

## Trigger

`/assets [action] [target]`

## Actions

### `import`
Configure import settings for a specific asset type or directory.

```
/assets import "environment textures need VRAM compression with mipmaps"
/assets import "UI sprites no mipmaps, RGBA8 lossless"
/assets import "music files as OGG streaming with loop points"
/assets import "FBX character with embedded animations"
```

**Output**: Godot .import parameter block or Unity AssetPostprocessor C# snippet.

### `atlas`
Design texture atlas layout and packing strategy.

```
/assets atlas "100 character portraits 128x128 each, mobile target"
/assets atlas "TileMap tileset 32x32 tiles with 2px padding"
/assets atlas "UI elements grouped by screen"
```

**Output**: Atlas dimensions, packing algorithm recommendation, Godot TileSet or Unity Sprite Atlas configuration.

### `optimize`
Audit and reduce asset memory footprint.

```
/assets optimize "texture memory budget exceeded on mobile"
/assets optimize "audio takes too much RAM"
/assets optimize "3D models have no LODs"
```

**Output**: Per-category breakdown, compression format recommendations, estimated savings.

### `bundle`
Structure assets for Addressables (Unity) or dynamic loading (Godot).

```
/assets bundle "separate loading screen assets from gameplay assets"
/assets bundle "DLC content packs with remote delivery"
/assets bundle "scene-specific preload groups"
```

**Output**: Asset group structure, loading code, dependency graph considerations.

## Examples

**Environment texture import (Godot):**
```
/assets import "res://assets/textures/environment/ - all PNG files"
```
Produces `.import` parameter block:
```ini
[params]
compress/mode=3
compress/high_quality=true
mipmaps/generate=true
roughness/mode=1
```
Plus editor script to batch-apply to directory.

**Texture memory audit:**
```
/assets optimize "game uses 800MB texture RAM on mobile, budget is 256MB"
```
Produces: Per-format VRAM cost table, priority list of which textures to downscale or recompress, estimated result.

**Build-time validation:**
```
/assets bundle "add CI check for oversized assets"
```
Produces: Shell script + Godot headless validation pass.

## Compression Format Reference

| Format | Platform | Use Case | Notes |
|--------|----------|----------|-------|
| BC7 | Desktop (DX11+) | Color textures | Best quality, 8bpp |
| BC5 | Desktop | Normal maps | 2-channel RG, 8bpp |
| ASTC 4x4 | Mobile | High-quality color | 8bpp, iOS 7+/Android |
| ASTC 6x6 | Mobile | Balanced color | 3.56bpp |
| ETC2 | Android GL | Color+alpha | OpenGL ES 3.0 |
| DXT1/BC1 | Desktop | Opaque color | 4bpp, no alpha |
| Lossless | Any | UI, icons <512px | No compression artifacts |
