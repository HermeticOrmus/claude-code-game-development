---
description: "Design a playtest, instrument a build, analyze results, or write the findings report"
argument-hint: "[design|instrument|analyze|report] <build or question>"
---

# /playtest

Playtesting session design, data collection, analytics implementation, and findings analysis.

## Trigger

`/playtest [action] [target]`

## Actions

### `design`
Create a structured playtest session plan.

```
/playtest design "first playtest of tutorial level - want to know if jump mechanic is taught"
/playtest design "mid-game difficulty spike at boss - 5 testers, 45 min sessions"
/playtest design "A/B test: original vs reduced enemy health in zone 3"
```

**Output**: Session objectives, success criteria, recruitment profile, session guide with timing, observation sheet, debrief questions.

### `instrument`
Implement analytics and data collection code.

```
/playtest instrument "death heatmap for 2D platformer"
/playtest instrument "time-per-room tracker across 12 rooms"
/playtest instrument "funnel: tutorial -> first combat -> checkpoint 1 -> level end"
/playtest instrument "A/B test for jump height: 6.0 vs 8.0 units"
```

**Output**: Typed GDScript with event logging, heatmap nodes, zone timers, funnel stage tracking, or A/B assignment.

### `analyze`
Interpret playtesting data and identify actionable findings.

```
/playtest analyze "heatmap shows 40% of deaths cluster at platform gap in room 4"
/playtest analyze "3 of 5 testers quit without finding the secondary weapon"
/playtest analyze "average time in zone 2 is 8 minutes, zone 3 is 45 seconds"
/playtest analyze "A/B test: variant group completed level 22% more often"
```

**Output**: Root cause hypotheses, severity rating (frequency × impact), prioritized fix recommendations.

### `report`
Structure findings into a shareable format.

```
/playtest report "3 sessions done, main issues found"
/playtest report "post-launch retention data from first 500 sessions"
```

**Output**: Findings table (issue, frequency, severity, recommended fix), funnel chart description, next test priorities.

## Examples

**Designing a session for tutorial feedback:**
```
/playtest design "tutorial for 2D platformer - verify players understand wall jump without text explanation"
```
Produces: Pre-session script ("Play as you would normally. I won't answer questions about the game."), 5 observation tasks with success/fail criteria, debrief questions focused on discovery, metrics (wall jump first attempt time, coaching requests count).

**Implementing funnel analytics:**
```
/playtest instrument "track player funnel: start -> tutorial_end -> first_boss_attempt -> first_boss_kill -> mid_game"
```
Produces: GameAnalytics autoload with log_funnel_stage(), session JSONL output, completion rate calculation per stage.

**Interpreting death cluster data:**
```
/playtest analyze "death heatmap: 60% of deaths in 16x16 cell at position (240, 180), rest scattered"
```
Analysis: High-density cluster = signaling failure or invisible obstacle. Check: Is floor visible? Is hazard clearly telegraphed? Are players attempting same failed action repeatedly?

## Session Metrics Reference

| Metric | What It Reveals | Good Threshold |
|--------|----------------|----------------|
| Tutorial completion rate | Onboarding clarity | > 80% |
| Deaths per obstacle | Difficulty calibration | < 5 avg |
| Time-per-zone | Pacing, exploration depth | Varies by design |
| Mechanic discovery rate | Feature visibility | > 60% for core mechanics |
| Session abandonment | Engagement, frustration point | < 20% before first checkpoint |
| Retry rate | Difficulty acceptance | Players retry = fair; quit = unfair |

## Observer Note Format

```
[MM:SS] ACTION | EMOTION | QUOTE
[04:32] Missed gap 3rd time | frustration | "why does this keep happening"
[07:18] Discovered secret room | surprise | said nothing, paused to look around
[12:00] Opened menu, did not continue | confusion | "how do I use this thing"
```
