# audio-systems

Audio plugin for LibreGameDev. Covers bus architecture, spatial audio, dynamic music systems, audio pooling, 3D occlusion, and FMOD/Wwise integration patterns.

## Scope

Runtime audio implementation: how sounds are played, routed through buses, spatialized, and dynamically mixed. Does not cover audio production (DAW workflows, sound design) or asset compression (covered by asset-pipelines plugin).

## Architecture Overview

```
Master Bus
├── Music Bus (OGG streams, vertical stems)
├── SFX Bus (pool of AudioStreamPlayer3D)
│   ├── Footstep Bus (pitch-randomized pool)
│   └── Combat Bus (impact, weapon, ability)
├── Voice Bus (dialogue, narration)
│   └── [Sidechains: ducks Music when active]
└── Ambient Bus (environment loops, Area3D zones)
    └── Reverb Send Bus (cave, indoor, outdoor presets)
```

## Components

- **game-audio-engineer**: Agent with expertise in FMOD, Wwise, Godot audio, Unity AudioMixer, spatial audio, and dynamic music
- **game-audio**: Command for designing, implementing, mixing, and optimizing audio systems
- **audio-patterns**: Skill library with audio bus setup, audio pool, randomized SFX, vertical remixing, 3D occlusion, and FMOD integration patterns

## Key Concepts

- **Voice polyphony**: Maximum simultaneous sounds per category. Set budgets before implementation.
- **Bus architecture**: Route sound categories to sub-buses for independent volume control, effects, and ducking
- **Vertical remixing**: Multiple simultaneous music stems; mix layers in/out for dynamic feel
- **Audio pooling**: Pre-allocate AudioStreamPlayers; never allocate per sound at runtime
- **Spatial attenuation**: Every in-world sound needs max_distance set; Godot default 0 = no limit

## Quick Start

Design bus layout:
```
/game-audio design "audio bus layout for action RPG"
```

Implement audio pool:
```
/game-audio implement "16-voice SFX pool with priority stealing"
```

Set up dynamic music:
```
/game-audio implement "vertical stem music system for combat/exploration"
```
