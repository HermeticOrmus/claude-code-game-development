---
name: asset-pipeline-patterns
description: "Asset pipeline patterns: Godot per-directory import overrides, a Unity AssetPostprocessor for texture standards, MaxRects atlas layout, Godot LOD configuration, audio import settings, and a CI asset validation script. Use when setting up or auditing how a game imports and compresses its assets."
---

# Asset Pipeline Patterns

## Godot Import Override by Directory

```
# res://assets/textures/ui/.gdignore does NOT affect imports.
# Instead, use import override files per directory.
# Place in res://assets/textures/ui/.import_defaults (Godot 4 pattern):

# Or use a _meta.godot file approach, or set each .import file.
# Practical approach: GDScript editor tool to batch-set import settings.
```

```gdscript
# Editor tool: batch set texture compression for a directory
@tool
extends EditorScript

const TARGET_DIR := "res://assets/textures/environment/"
const COMPRESS_MODE := 3  # VRAM compressed (BC7/ASTC based on platform)

func _run() -> void:
    var dir := DirAccess.open(TARGET_DIR)
    if not dir:
        push_error("Cannot open directory: %s" % TARGET_DIR)
        return

    dir.list_dir_begin()
    var file_name := dir.get_next()
    while file_name != "":
        if file_name.ends_with(".png") or file_name.ends_with(".jpg"):
            _set_texture_compression(TARGET_DIR + file_name)
        file_name = dir.get_next()

    EditorInterface.get_resource_filesystem().scan()
    print("Batch import settings applied.")

func _set_texture_compression(path: String) -> void:
    var import_path := path + ".import"
    var config := ConfigFile.new()
    config.load(import_path)
    config.set_value("params", "compress/mode", COMPRESS_MODE)
    config.set_value("params", "mipmaps/generate", true)
    config.save(import_path)
```

## Unity AssetPostprocessor for Texture Standards

```csharp
// Enforces texture import settings based on directory convention
// Place in Editor/ folder
using UnityEditor;
using UnityEngine;

public class TextureImportEnforcer : AssetPostprocessor
{
    void OnPreprocessTexture()
    {
        var importer = assetImporter as TextureImporter;
        if (importer == null) return;

        string path = assetPath.ToLower();

        if (path.Contains("/ui/"))
        {
            importer.textureType = TextureImporterType.Sprite;
            importer.mipmapEnabled = false;
            SetPlatformSettings(importer, "Standalone", TextureImporterFormat.BC7);
            SetPlatformSettings(importer, "Android", TextureImporterFormat.ASTC_6x6);
            SetPlatformSettings(importer, "iPhone", TextureImporterFormat.ASTC_6x6);
        }
        else if (path.Contains("/environment/"))
        {
            importer.textureType = TextureImporterType.Default;
            importer.mipmapEnabled = true;
            importer.streamingMipmaps = true;  // Only load needed mip levels
            SetPlatformSettings(importer, "Standalone", TextureImporterFormat.BC7);
            SetPlatformSettings(importer, "Android", TextureImporterFormat.ASTC_4x4);
            SetPlatformSettings(importer, "iPhone", TextureImporterFormat.ASTC_4x4);
        }
        else if (path.Contains("/normalmap/") || path.Contains("_normal"))
        {
            importer.textureType = TextureImporterType.NormalMap;
            SetPlatformSettings(importer, "Standalone", TextureImporterFormat.BC5);
        }
    }

    static void SetPlatformSettings(TextureImporter importer, string platform, TextureImporterFormat format)
    {
        var settings = new TextureImporterPlatformSettings
        {
            name = platform,
            overridden = true,
            format = format,
            maxTextureSize = 2048,
            compressionQuality = (int)TextureCompressionQuality.Best
        };
        importer.SetPlatformTextureSettings(settings);
    }
}
```

## Texture Atlas Layout (MaxRects)

```gdscript
# Simple shelf packer for runtime atlas generation
class_name ShelfPacker
var width: int
var height: int
var _shelves: Array[Dictionary] = []  # [{y, height, x_cursor}]

func _init(atlas_width: int, atlas_height: int) -> void:
    width = atlas_width
    height = atlas_height

# Returns Rect2i placement or Rect2i(-1,-1,0,0) if no space
func pack(item_width: int, item_height: int) -> Rect2i:
    # Try to fit on existing shelf
    for shelf in _shelves:
        if shelf.x_cursor + item_width <= width and item_height <= shelf.height:
            var rect := Rect2i(shelf.x_cursor, shelf.y, item_width, item_height)
            shelf.x_cursor += item_width
            return rect

    # Start a new shelf
    var shelf_y: int = 0
    if not _shelves.is_empty():
        var last := _shelves.back()
        shelf_y = last.y + last.height

    if shelf_y + item_height > height:
        return Rect2i(-1, -1, 0, 0)  # Atlas full

    var new_shelf := { "y": shelf_y, "height": item_height, "x_cursor": item_width }
    _shelves.append(new_shelf)
    return Rect2i(0, shelf_y, item_width, item_height)
```

## LOD Configuration (Godot)

```gdscript
# Configure LOD visibility ranges on MeshInstance3D nodes
@tool
class_name LODConfigurator extends EditorScript

# LOD ranges in meters from camera
const LOD_RANGES := [
    0.0,    # LOD0: full quality
    10.0,   # LOD1: starts at 10m
    25.0,   # LOD2: starts at 25m
    60.0,   # LOD3 (impostor): starts at 60m
    150.0,  # Fade out starts
]

func configure_lod(mesh_instance: MeshInstance3D, lod_meshes: Array[Mesh]) -> void:
    # Godot uses visibility_range_begin/end for per-mesh LOD switching
    # Requires GeometryInstance3D nodes named LOD0, LOD1, LOD2 as children
    var lod_nodes := mesh_instance.get_children().filter(
        func(c): return c is MeshInstance3D and c.name.begins_with("LOD")
    )
    lod_nodes.sort_custom(func(a, b): return a.name < b.name)

    for i in lod_nodes.size():
        var node: MeshInstance3D = lod_nodes[i]
        node.visibility_range_begin = LOD_RANGES[i]
        node.visibility_range_end = LOD_RANGES[i + 1] if i + 1 < LOD_RANGES.size() else 0.0
        node.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
```

## Audio Import Settings Pattern

```gdscript
# Audio import decision logic (document this in project wiki)
# Short SFX (<0.5s): WAV, no loop, 44100 Hz, mono where possible
# Medium SFX (0.5-3s): OGG Vorbis, no loop, 44100 Hz
# Music (>3s): OGG Vorbis, streaming enabled, loop points set
# Voice: OGG Vorbis, 22050 Hz (saves 50% memory, voice range is 300-3400 Hz)

# Godot .import file for a music track:
# [params]
# compress/mode=0          ; 0=PCM, 1=IMA ADPCM, 2=Ogg Vorbis, 3=MP3
# compress/mode=2          ; OGG for music
# edit/loop_mode=1         ; 1=forward loop
# edit/loop_begin=0
# edit/loop_end=-1         ; -1=end of file
```

## CI Asset Validation Script

```bash
#!/bin/bash
# Validates asset sizes and formats before build
# Run as pre-commit hook or CI step

ERRORS=0
MAX_TEXTURE_SIZE=2048

# Check for oversized textures
find res/assets -name "*.png" -o -name "*.jpg" | while read img; do
    SIZE=$(identify -format "%wx%h" "$img" 2>/dev/null)
    W=$(echo $SIZE | cut -dx -f1)
    H=$(echo $SIZE | cut -dx -f2)
    if [ "$W" -gt "$MAX_TEXTURE_SIZE" ] || [ "$H" -gt "$MAX_TEXTURE_SIZE" ]; then
        echo "ERROR: Oversized texture: $img ($SIZE)"
        ERRORS=$((ERRORS+1))
    fi
done

# Check for uncompressed audio used as music (WAV > 5MB)
find res/assets/audio/music -name "*.wav" | while read wav; do
    SIZE=$(stat -c%s "$wav")
    if [ "$SIZE" -gt 5242880 ]; then
        echo "WARN: Large WAV in music folder (use OGG): $wav"
    fi
done

exit $ERRORS
```

## Anti-Patterns

- **Importing PSD/AI directly**: Source files in repo bloat Git history. Export PNG from Figma/Photoshop, commit PNG + source file separately.
- **RGBA textures for opaque surfaces**: BC7/ASTC store 4 channels; use BC1/ASTC opaque variant for fully opaque textures (saves 50% VRAM).
- **No mipmaps on 3D textures**: Without mipmaps, texture sampling aliases at distance. Always enable mipmaps for 3D world textures.
- **Streaming audio for short SFX**: Streaming has disk seek overhead. Only stream files >3 seconds. Load short sounds fully into memory.
- **Single atlas for all sprites**: Atlas invalidation (one sprite change = full atlas reimport). Group by scene/screen or update frequency.
