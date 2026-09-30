---
description: "Design, implement, mix, or optimize a game audio system"
argument-hint: "[design|implement|mix|optimize] <sound or music system>"
---

# /game-audio

Game audio implementation: bus architecture, spatial audio, dynamic music, audio pooling, and FMOD/Wwise integration.

## Trigger

`/game-audio [action] [target]`

## Actions

### `design`
Design audio bus architecture or dynamic music state machine.

```
/game-audio design "audio bus layout for RPG with music, SFX, voice, ambient"
/game-audio design "dynamic music system: exploration -> tension -> combat"
/game-audio design "environmental audio zones: interior, cave, open world"
```

**Output**: Bus graph diagram, AudioBusLayout configuration, state machine structure.

### `implement`
Generate audio system code for Godot, Unity, or FMOD.

```
/game-audio implement "audio pool for SFX with 16 voice polyphony limit"
/game-audio implement "randomized footstep playback with pitch variation"
/game-audio implement "3D audio occlusion through walls"
/game-audio implement "vertical music remixing with 5 stems"
```

**Output**: Typed GDScript or C# with bus routing, pooling pattern, or spatial configuration.

### `mix`
Tune volume levels, attenuation curves, and bus effects.

```
/game-audio mix "footsteps too loud compared to music"
/game-audio mix "combat audio feels thin, no impact"
/game-audio mix "dialogue hard to hear during combat"
```

**Output**: dB adjustment recommendations, bus send levels, compressor/sidechain setup.

### `optimize`
Reduce audio CPU/memory overhead.

```
/game-audio optimize "200 AudioStreamPlayers causing frame drops"
/game-audio optimize "audio memory usage too high on mobile"
/game-audio optimize "streaming audio causing hitches"
```

**Output**: Voice budget per category, pool sizing calculation, streaming threshold recommendations.

## Examples

**Audio pool setup:**
```
/game-audio implement "SFX audio pool for footsteps and combat sounds"
```
Produces: 16-voice AudioPool class with priority stealing, bus assignment, and finished signal reclaim.

**Dynamic music combat transition:**
```
/game-audio implement "music transitions: exploration (calm) -> combat (intense) -> exploration"
```
Produces: MusicSystem with stem-based vertical remixing, beat-aligned transition on BPM grid, crossfade tween.

**Spatial audio configuration:**
```
/game-audio design "cave interior: reverb, muffled ambience, echo on footsteps"
```
Produces: Area3D audio zone with reverb bus override, AudioStreamPlayer3D attenuation parameters, echo effect chain.

## Attenuation Model Reference

| Model | Formula | Use Case |
|-------|---------|----------|
| Inverse | 1/distance | Realistic air propagation |
| InverseSquare | 1/distance² | Real-world point sources |
| Logarithmic | 20*log(d/unit) | Games (most predictable feel) |
| Disabled | No attenuation | 2D / ambient / music |

## Voice Budget Reference

| Category | Polyphony | Priority | Notes |
|----------|-----------|---------|-------|
| Music | 1-2 | High | Never steal |
| Voice/Dialogue | 1 | High | Never interrupt |
| Player SFX | 4 | High | Footstep pool |
| Enemy SFX | 8 | Medium | Distance-scaled |
| Ambient | 4 | Low | Steal freely |
| UI | 2 | Medium | No spatial |
