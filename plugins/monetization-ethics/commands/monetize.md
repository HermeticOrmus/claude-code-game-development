---
description: "Design, audit, implement, or test game monetization against a dark pattern checklist"
argument-hint: "[design|audit|implement|test] <store, pass, or offer>"
---

# /monetize

Ethical game monetization design, dark pattern auditing, IAP implementation, and player spending protection.

## Trigger

`/monetize [action] [target]`

## Actions

### `design`
Design an ethical monetization model for a game.

```
/monetize design "free-to-play mobile RPG, target: casual players"
/monetize design "indie premium game with optional DLC"
/monetize design "seasonal battle pass for action game"
```

**Output**: Model recommendation with ethical rationale, revenue projection considerations, player experience impact.

### `audit`
Evaluate existing monetization design against dark pattern checklist.

```
/monetize audit "our loot box system with premium currency"
/monetize audit "battle pass design with 100 tiers"
/monetize audit "limited-time offer countdown timers"
```

**Output**: Full 20-point ethics checklist, flagged dark patterns, ethical redesign recommendations.

### `implement`
Generate IAP integration code for platform-specific store.

```
/monetize implement "Steam microtransaction for cosmetics store"
/monetize implement "Google Play Billing for Android IAP"
/monetize implement "Apple StoreKit 2 for iOS subscriptions"
```

**Output**: Platform IAP code, receipt validation pattern, purchase confirmation UI with ethical requirements.

### `test`
Add player protections and spending analytics.

```
/monetize test "voluntary monthly spending cap for players"
/monetize test "parental control spending limit integration"
/monetize test "purchase analytics without exploitative profiling"
```

**Output**: SpendingLimits class, platform parental control API integration, analytics schema.

## Examples

**Evaluating a battle pass:**
```
/monetize audit "battle pass with 100 tiers, top tiers include stat-boosting equipment"
```
Result: FAILS audit. Items on paid track include stat bonuses = pay-to-win. Redesign: stat items moved to free track or removed; paid track gets cosmetics only.

**Designing ethical F2P:**
```
/monetize design "free-to-play action RPG, need revenue from mobile"
```
Produces: Cosmetics-only store recommendation, premium battle pass design with daily XP calculation showing completion at <90 min/day, optional "supporter pack" DLC for dedicated fans, IAP confirmation flow with mandatory real price display.

**Loot box compliance:**
```
/monetize audit "gacha system with character pulls"
```
Checks: drop rate disclosure (required for EU compliance), pity system (mandatory if selling pulls in Belgium/Netherlands), spending cap option.

## Ethical Revenue Models Ranked

| Model | Player Experience | Revenue Sustainability | Ethical Score |
|-------|------------------|----------------------|--------------|
| Buy once (B2P) | Best | Stable | Highest |
| Premium DLC | Very good | Good | Very high |
| Cosmetics-only F2P | Good | Good | High |
| Ethical battle pass | Good | Good | High |
| Subscription | Acceptable | Good | Medium |
| Loot boxes (disclosed odds) | Poor | Short-term only | Low |
| Pay-to-win | Bad | Collapses on launch | None |
