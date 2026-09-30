# Multiplayer Networking

> Rollback netcode, lockstep determinism, client-side prediction, lag compensation, dedicated server vs. P2P, matchmaking. The patterns that make networked games actually playable.

## Overview

Multiplayer networking is the hardest layer in game dev. The mistakes are subtle. The debugging is brutal. The user-visible failures (rubber-banding, desync, hit detection feeling wrong) often look identical despite having different root causes. This plugin encodes the canonical network patterns so the agent reasons about latency, packet loss, and authority correctly rather than picking the simplest approach.

## Contents

### Agents

- **network-engineer** -- Multiplayer netcode specialist. Picks rollback vs. lockstep vs. authoritative-server-with-prediction based on genre + player count + latency tolerance. Designs serialization with bandwidth budgets. Walks the lag-compensation graph for hitscan weapons. Knows the trade-offs cold.

### Commands

- **/multiplayer** -- Netcode architecture + serialization design + prediction/reconciliation patterns. Hand it a multiplayer game scenario with constraints and it returns a netcode choice with reasoning + an implementation outline.

### Skills

- **multiplayer-networking** -- Reference library: netcode model comparison, serialization patterns, prediction state machines, common-mistakes catalog, library comparison.

## Key Capabilities

- **Netcode model selection** based on genre (fighting → rollback, RTS → lockstep, FPS → prediction + reconciliation, MMO → server-authoritative + interpolation)
- **Rollback netcode design** — input delay, prediction window, frame-perfect reconciliation, GGPO-style architecture
- **Lockstep design** — deterministic simulation, input synchronization, the network-as-input-pipeline pattern
- **Client-side prediction + server reconciliation** — predict locally, accept correction, smooth the resync
- **Lag compensation** — favor-the-shooter vs. favor-the-target trade-off, historical position lookup, anti-cheat considerations
- **Serialization bandwidth** — delta encoding, quantization, bit-packing, priority queues for limited bandwidth
- **Connection topology** — P2P vs. dedicated server vs. relay, NAT traversal, regional routing
- **Matchmaking + lobbies** — skill-based, latency-based, party-based matching algorithms
- **Anti-cheat fundamentals** — server authority for critical state, validation hashes, cheat detection patterns

## When to use this plugin

- Adding multiplayer to a single-player game
- Choosing a netcode library (Netcode for GameObjects, Mirror, FishNet, Photon, Nakama, dedicated server)
- Debugging "rubber-banding," "desync," "shot didn't register," "lag spikes"
- Designing for cross-platform multiplayer (different physics behavior, frame rates)
- Anti-cheat hardening for competitive games
- Migrating from P2P to dedicated server architecture

## Compatibility

- **Engines covered**: Unity (Netcode for GameObjects, Mirror, FishNet), Godot (high-level multiplayer API), Unreal (built-in networking + replication graph)
- **Genres covered deeply**: fighting, FPS, RTS, MOBA, racing, MMO (general patterns; full MMO is its own discipline)
- **Player count scales**: 2-player (P2P fine), 4-16 (dedicated server preferred), 64-100+ (replication graph + interest management), MMO-scale (sharding + cell-based)
- **Network conditions covered**: 10-300ms RTT, 0-10% packet loss, intermittent connectivity, mobile data switches

## Limitations the agent will tell you about

- The agent doesn't write your matchmaking backend — that's its own service. Agent helps with the in-game network layer.
- Anti-cheat is partly client-side (detect tampering) and partly server-side (validate actions). Agent covers the design patterns; commercial anti-cheat services (BattlEye, EAC) integration is light.
- VOIP integration is its own protocol set; agent mentions but doesn't deeply cover.
