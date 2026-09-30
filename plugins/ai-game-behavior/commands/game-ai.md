---
description: "Design, implement, debug, or tune NPC behavior with behavior trees, FSMs, utility AI, or GOAP"
argument-hint: "[design|implement|debug|tune] <what the NPC should do>"
---

# /game-ai

AI behavior design and implementation for NPCs. Covers behavior trees, FSMs, utility AI, GOAP, navigation, and perception systems.

## Trigger

`/game-ai [action] [target]`

## Actions

### `design`
Design an AI architecture for an NPC type. Outputs ASCII state diagram or BT structure + blackboard schema.

```
/game-ai design "patrol guard with alert states"
/game-ai design "boss enemy with phase transitions"
/game-ai design "companion follower with utility AI"
```

**Output**: Architecture recommendation with rationale, ASCII diagram, blackboard schema as typed GDScript Resource.

### `implement`
Generate GDScript implementation for a specified AI system.

```
/game-ai implement bt "3-state patrol -> investigate -> attack"
/game-ai implement fsm "enemy with push-down automata for interrupts"
/game-ai implement utility "NPC action scorer with 4 considerations"
/game-ai implement goap "action set for combat agent"
```

**Output**: Full GDScript with typed variables, @export parameters, inline comments explaining pattern choices.

### `debug`
Diagnose AI behavior problems from description or code.

```
/game-ai debug "NPC gets stuck between two waypoints"
/game-ai debug "enemy never transitions out of idle state"
/game-ai debug "pathfinding works but NPC stutters on arrival"
```

**Output**: Root cause analysis, specific code fix, prevention pattern.

### `tune`
Tune consideration curves, BT tick rates, or FSM timeout values.

```
/game-ai tune "utility scores all feel equal, no clear winner"
/game-ai tune "BT too expensive, 200 NPCs at 60fps drops to 30fps"
/game-ai tune "patrol timeout too short, NPCs always re-alert"
```

**Output**: Parameter adjustments with reasoning, performance budget calculations.

## Examples

**Designing a stealth game guard:**
```
/game-ai design "stealth guard: unaware -> suspicious -> alerted -> searching"
```
Produces: 4-state HFSM with push-down investigative substates, alert meter as utility consideration, vision cone + hearing radius sensor setup.

**Implementing behavior tree root:**
```
/game-ai implement bt "combat agent: seek cover when low health, attack when in range, patrol otherwise"
```
Produces:
```gdscript
# Root Selector (find something to do)
#   Sequence: LowHealth? -> FindCover -> MoveToCover -> WaitInCover
#   Sequence: TargetInRange? -> TargetVisible? -> AttackTarget
#   Sequence: HasPatrolPath? -> MoveToNextWaypoint
```
Plus full typed GDScript for each node.

**Debugging stuck pathfinding:**
```
/game-ai debug "NPC reaches destination but oscillates back and forth"
```
Root cause: `target_desired_distance` too small relative to agent radius. Fix: set `nav_agent.target_desired_distance = agent_radius * 2.0`. Add `is_navigation_finished()` guard before issuing new path requests.

## Performance Reference

| NPC Count | Recommended Tick Rate | Architecture |
|-----------|----------------------|--------------|
| 1-5 (bosses) | 60 Hz | Full BT every frame |
| 6-30 (combatants) | 20-30 Hz | BT with timer, perception every frame |
| 31-200 (crowd) | 5-10 Hz | Simplified FSM, flow field navigation |
| 200+ (ambient) | 1-2 Hz | Pure FSM, no pathfinding (fake movement) |
