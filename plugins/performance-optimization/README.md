# performance-optimization

Performance plugin for LibreGameDev. Covers GPU profiling with RenderDoc, Godot Profiler custom monitors, draw call batching with MultiMeshInstance3D, LOD configuration, object pooling, and GDScript optimization patterns.

## Core Rule

Profile first. Measure the actual bottleneck. Never optimize by intuition.

## Components

- **game-perf-engineer**: Agent who diagnoses CPU/GPU bottlenecks and applies targeted solutions with measured validation
- **game-perf**: Command for profiling, batching, LOD, and pooling workflows
- **game-perf-patterns**: Skill library with MultiMeshInstance3D foliage, custom monitors, generic object pool, LOD configuration, GDScript hot path optimization, and deferred processing

## Quick Diagnosis Guide

| Symptom | Likely Cause | First Check |
|---------|-------------|-------------|
| Low fps, many objects | Draw calls | Profiler > GPU > Draw Calls |
| Low fps, enemies | Physics or AI script | Profiler > Physics contacts |
| Frame spikes every Ns | GC / instantiate-free | Profiler > Script spikes |
| Mobile < PC performance ratio | Texture memory | VRAM usage in Profiler |
| fps drops when looking at area | Overdraw / transparent | RenderDoc overdraw view |

## Quick Start

Profile a specific bottleneck:
```
/game-perf profile "45fps with 50 active enemies"
```

Reduce foliage draw calls:
```
/game-perf batch "500 tree instances using 500 draw calls"
```

Pool frequently spawned objects:
```
/game-perf pool "bullet projectiles, up to 100 simultaneous"
```
