# playtesting

Playtesting plugin for LibreGameDev. Covers session design protocols, quantitative data collection (death heatmaps, zone timers, funnel analytics), A/B testing for game balance, and interpreting behavioral data to drive design iteration.

## When to Playtest

| Signal | Action |
|--------|--------|
| "Is the tutorial clear?" | Observation session: silent, 5 testers, count coaching requests |
| "Is this section too hard?" | Death heatmap + attempts-per-obstacle + exit survey |
| "Which version feels better?" | A/B test with minimum 30 per group, single variable |
| "Why do players quit?" | Funnel analytics + debrief: "what was the most confusing moment?" |
| Pre-launch readiness | Full session: tutorial -> end, completion rate target > 70% |

## Components

- **playtest-coordinator**: Agent with expertise in session protocols, observation vs think-aloud, funnel analysis, recruitment, A/B testing methodology, and finding prioritization
- **playtest**: Command for designing sessions, instrumenting analytics, analyzing results, and generating reports
- **playtest-patterns**: Skill library with DeathHeatmap (Vector2i accumulation, color gradient render), GameAnalytics (JSONL event log, typed event methods), ZoneTimer, playtest session guide template, and ABTest (deterministic per-player assignment)

## Quick Start

Design a session:
```
/playtest design "first external playtest - 2D action game, tutorial + first level, 8 testers"
```

Add death tracking:
```
/playtest instrument "death heatmap overlay for 2D platformer with 32px cells"
```

Analyze what you found:
```
/playtest analyze "7 of 8 testers missed the double jump entirely in first room"
```

## Recruitment Rule

Do not test with developer friends. They know the game, know you, and provide systematically optimistic feedback. Recruit strangers matching your target demographic. Nielsen's rule: 5 users find ~85% of usability issues. Run 8-10 for confidence.

## Session Length

45-90 minutes. Beyond 90 minutes, fatigue skews results toward negativity. Keep debrief to 15 minutes max.
