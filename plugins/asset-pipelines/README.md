# asset-pipelines

Asset pipeline plugin for LibreGameDev. Covers texture compression, import configuration, texture atlasing, LOD generation, audio compression, and CI-based asset validation.

## Scope

The path from source art to runtime-optimized assets. Includes import settings, compression format selection by platform, atlasing strategies, and automated validation. Does not cover 3D modeling, rigging, or audio production.

## Memory Budget Reference

| Platform | Texture Budget | Audio Budget | Recommended Formats |
|----------|---------------|-------------|---------------------|
| Mobile (low-end) | 128 MB | 32 MB | ASTC 6x6, OGG 128kbps |
| Mobile (mid-range) | 256 MB | 64 MB | ASTC 4x4, OGG 160kbps |
| Console / PC | 512 MB - 2 GB | 128 MB | BC7, OGG 192kbps |
| PC (high-end) | 2+ GB | Unlimited | BC7, WAV for SFX |

## Components

- **asset-pipeline-engineer**: Agent for import settings, compression, atlasing, LOD, and CI validation
- **assets**: Command for import, atlas, optimize, and bundle workflows
- **asset-pipeline-patterns**: Skill library with Godot import scripts, Unity AssetPostprocessor, shelf packer, LOD configuration, and CI validation scripts

## Quick Start

Configure texture import for a directory:
```
/assets import "environment textures for mobile with VRAM compression"
```

Audit memory usage:
```
/assets optimize "texture memory over budget on mobile target"
```

Set up CI validation:
```
/assets bundle "add pre-commit check for oversized textures"
```
