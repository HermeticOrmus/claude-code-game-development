# ai-game-behavior

Game AI plugin for LibreGameDev. Covers NPC intelligence architecture: behavior trees, finite state machines, utility AI, GOAP, navigation, and perception systems.

## Scope

This plugin handles the decision-making layer of NPC agents - the logic between "what the NPC perceives" and "what the NPC does." It does not cover animation, physics, or networking.

## Architecture Decision Guide

| NPC Complexity | States/Behaviors | Recommended Architecture |
|---------------|-----------------|--------------------------|
| Simple pickup, trigger | 1-3 | Script-only, no AI framework |
| Guard, turret, basic enemy | 3-8 | Finite State Machine |
| Combat AI, companion | 8-20 | Behavior Tree |
| Believable civilian | Any | Utility AI |
| Problem-solving agent | Dynamic | GOAP |
| Boss with phases | 3-6 phases, complex sub-behavior | HFSM + BT hybrid |

## Components

- **game-ai-engineer**: Agent with expertise in all major game AI architectures
- **game-ai**: Command for designing, implementing, debugging, and tuning AI systems
- **game-ai-patterns**: Skill library with GDScript patterns for BT nodes, FSM tables, utility curves, GOAP actions, NavMesh configuration, and vision sensing

## Key Literature

- "Behavior Trees in Robotics and AI" - Michele Colledanchise & Petter Ogren
- "GameAIPro" series (volumes 1-4) - edited by Steve Rabin - freely available online
- "Goal-Oriented Action Planning" - Jeff Orkin (F.E.A.R. postmortem)
- "Infinite Axis Utility System" - Dave Mark (GDC 2012)
- "AI Game Programming Wisdom" series - Steve Rabin

## Quick Start

Design an AI system:
```
/game-ai design "combat enemy: patrol, investigate noise, attack on sight, flee when low health"
```

Implement from design:
```
/game-ai implement bt "patrol-investigate-attack with low health flee"
```

Debug behavior problems:
```
/game-ai debug "NPC ignores player after initial attack"
```
