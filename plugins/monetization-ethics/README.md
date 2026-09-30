# monetization-ethics

Monetization ethics plugin for LibreGameDev. Covers dark pattern identification, ethical monetization model design, IAP implementation, battle pass ethics, and player spending protections.

## Core Principle

Every monetization decision must pass: "Does this empower players or extract from them?"

Extraction (dark patterns) destroys player trust and creates regulatory risk. Ethical monetization builds long-term relationships and sustainable revenue.

## Dark Patterns Reference

| Pattern | What it does | Ethical alternative |
|---------|-------------|-------------------|
| FOMO countdown | Creates false urgency | Remove timer from non-scarce goods |
| Artificial scarcity | "Only 3 left!" on infinite digital goods | Honest supply statements |
| Pay-to-win | Money = power advantage | Cosmetics-only; no stat purchases |
| Loot boxes (undisclosed) | Hidden probabilities | Show exact odds (legally required in EU) |
| Premium currency obfuscation | Hides real cost | Show real price alongside currency |
| Roach motel | Easy to start, hard to cancel | 2-click cancellation |
| Orphan coins | Bundles leave unusable remainder | Bundles match item prices exactly |

## Components

- **monetization-advisor**: Agent who evaluates monetization through both ethics and business lens, citing academic dark pattern research
- **monetize**: Command for designing, auditing, implementing, and testing monetization systems
- **ethical-monetization-patterns**: Skill library with dark pattern audit checklist, cosmetics-only store, ethical battle pass, IAP confirmation flow, and voluntary spending limits

## Quick Start

Audit existing monetization:
```
/monetize audit "our current IAP store and currency system"
```

Design ethical F2P:
```
/monetize design "free-to-play mobile game"
```

Implement IAP:
```
/monetize implement "Steam cosmetics store with purchase confirmation"
```
