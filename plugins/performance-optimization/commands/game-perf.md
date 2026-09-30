---
description: "Profile a game, batch draw calls, configure LODs, or add object pooling"
argument-hint: "[profile|batch|lod|pool] <scene or symptom>"
---

# /game-perf

Game performance profiling, batching, LOD configuration, and object pooling.

## Trigger

`/game-perf [action] [target]`

## Actions

### `profile`
Identify performance bottleneck from symptom description.

```
/game-perf profile "game drops to 45fps with 50 enemies on screen"
/game-perf profile "30fps on mobile with 1000 foliage instances"
/game-perf profile "frame spike every 2 seconds"
```

**Output**: Diagnosis checklist (CPU vs GPU bound, draw calls, physics contacts), profiler setup guide, custom monitor code.

### `batch`
Implement draw call reduction strategies.

```
/game-perf batch "1000 foliage meshes causing 1000 draw calls"
/game-perf batch "200 coins scattered in level all individual"
/game-perf batch "particle effects creating hundreds of draw calls"
```

**Output**: MultiMeshInstance3D implementation, instancing shader, or static batching setup.

### `lod`
Configure LOD transitions for 3D objects.

```
/game-perf lod "character models need LOD at 10, 30, 80 meters"
/game-perf lod "vegetation disappears abruptly instead of fading"
/game-perf lod "impostor LOD for distant buildings"
```

**Output**: LOD node configuration, visibility range values, fade mode setup.

### `pool`
Implement object pool for frequently spawned objects.

```
/game-perf pool "bullet projectiles, 200 active max"
/game-perf pool "enemy spawner, 50 concurrent enemies"
/game-perf pool "audio player pool for SFX"
```

**Output**: GenericPool GDScript, acquire/release usage, pool size calculation.

## Examples

**Diagnosing 45fps with 50 enemies:**
```
/game-perf profile "game runs at 45fps. 50 enemies active. physics on."
```
Diagnostic steps:
1. Open Godot Profiler; check physics % of frame time
2. If physics > 50%: reduce physics body count, use Area3D for detection instead of RigidBody
3. If render > 50%: check draw calls; enable Profiler > GPU
4. If script > 50%: check enemy AI tick rate; reduce to 10Hz for distant enemies

**1000 foliage draw calls:**
```
/game-perf batch "1000 grass meshes using 1000 draw calls, 30fps on target GPU"
```
Produces: FoliageRenderer using MultiMeshInstance3D, terrain-aligned random placement, optional wind shader via instance uniforms.

**Frame spike every 2 seconds:**
```
/game-perf profile "consistent 2-second frame spike of ~50ms"
```
Root cause candidates: GC from queue_free/instantiate cycle (use pool), ResourceLoader blocking (use threaded load), physics broad phase spike (check physics body count).

## Performance Targets by Platform

| Platform | Target FPS | Draw Calls | Physics Bodies | Memory |
|----------|-----------|-----------|---------------|--------|
| Mobile (low-end) | 30 | <200 | <50 | 512 MB |
| Mobile (mid) | 60 | <500 | <100 | 1 GB |
| Console | 60 | <1000 | <200 | 2 GB |
| PC (min spec) | 60 | <2000 | <300 | 4 GB |
| PC (recommended) | 60+ | <5000 | <500 | 8 GB |
