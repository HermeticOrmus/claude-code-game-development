---
name: ethical-monetization-patterns
description: "Ethical monetization patterns: a dark pattern audit checklist, a cosmetics-only store, battle pass design, a Godot and GodotSteam IAP purchase flow, a voluntary spending cap, and an explicit list of banned patterns. Use when building a store or reviewing monetization for exploitative design."
---

# Ethical Monetization Patterns

## Dark Pattern Audit Checklist

```
MONETIZATION ETHICS AUDIT
==========================

SECTION 1: Pay-to-Win Assessment
[ ] All spending provides cosmetic/convenience only, no gameplay power
[ ] No stat boosts, ability unlocks, or damage increases tied to spending
[ ] PvP balance unaffected by any purchasable item
[ ] Free players can compete with paying players in all core game modes

SECTION 2: Transparency
[ ] Real currency prices shown prominently (no hiding behind premium currency only)
[ ] Premium currency amounts shown in real money equivalent during purchase flow
[ ] No orphaned premium currency designs (bundles divisible cleanly by item prices)
[ ] "What you get" fully described before payment, no mystery boxes unlabeled

SECTION 3: Psychological Manipulation
[ ] No countdown timers on non-scarce digital goods
[ ] No "only N left" false scarcity on infinitely reproducible items
[ ] No social pressure mechanics ("your friends bought this")
[ ] No progress loss threats to prevent churn
[ ] Loot boxes: are contents and probabilities disclosed? (required in Belgium, Netherlands, China)

SECTION 4: Children's Protections
[ ] Parental control spending limits honored (iOS Screen Time, Google Family Link)
[ ] Purchase confirmation dialog before every transaction
[ ] Opt-in spending limits (monthly cap user can set themselves)
[ ] No targeted advertising based on spending patterns for under-18

SECTION 5: Cancellation and Fairness
[ ] Subscriptions cancel in 2 clicks (no roach motel UI)
[ ] Refund policy clearly stated and honored
[ ] Account deletion removes payment data (GDPR)
[ ] Premium content retained if subscription lapses (no retroactive removal)

RESULT: ___ / 20 checks passed
0-10: Significant ethical issues requiring redesign
11-16: Some concerns to address before launch
17-20: Ethically sound monetization
```

## Cosmetics-Only Store (Path of Exile Model)

```gdscript
# Cosmetics-only item store - no pay-to-win
class_name CosmeticStore extends Node

# Purchasable items: visual only
class CosmeticItem extends Resource:
    @export var item_id: StringName
    @export var display_name: String
    @export var price_real_currency: float  # Show real price, not obscure currency
    @export var item_type: StringName       # "character_skin", "emote", "title", "portrait"
    @export var preview_texture: Texture2D
    # NOT: damage_bonus, stat_modifier, unlock_ability

func purchase(item: CosmeticItem, player_id: int) -> bool:
    # IAP flow - platform-specific
    # On success: write to player's owned_cosmetics save data
    # On failure: show clear error with reason
    return _initiate_platform_purchase(item, player_id)

func apply_cosmetic(player: Player, item_id: StringName) -> void:
    if player.owned_cosmetics.has(item_id):
        player.active_skin = item_id
        # Change visual only - no stats affected
```

## Battle Pass Ethical Design

```gdscript
# Battle pass with ethical constraints enforced in data
class_name BattlePass extends Resource
@export var season_name: String
@export var season_duration_days: int = 90
@export var free_tiers: Array[BattlePassTier]   # Available to all players
@export var paid_tiers: Array[BattlePassTier]   # Available with battle pass purchase

# Tier types allowed per ethical guidelines
class BattlePassTier extends Resource:
    @export var tier_number: int
    @export var reward_type: StringName  # Must be in ALLOWED_REWARD_TYPES
    @export var reward_data: Dictionary

    const ALLOWED_REWARD_TYPES: Array[StringName] = [
        &"cosmetic_skin",
        &"emote",
        &"title_badge",
        &"player_icon",
        &"in_game_currency_small",  # Small amounts of earnable currency
    ]
    # FORBIDDEN types (would make this pay-to-win):
    # &"stat_boost", &"ability_unlock", &"damage_increase", &"rare_equipment"

# Validate pass before publishing
func validate_ethical_design() -> bool:
    for tier in paid_tiers:
        if tier.reward_type not in BattlePassTier.ALLOWED_REWARD_TYPES:
            push_error("Pay-to-win item in battle pass: %s" % tier.reward_type)
            return false
    return true

# Calculate daily XP required to complete at reasonable pace
func daily_xp_required_free() -> float:
    var total_free_xp := free_tiers.reduce(func(acc, t): return acc + t.xp_required, 0)
    var gameplay_days := season_duration_days * 0.8  # Assume 80% of days playing
    return total_free_xp / gameplay_days
    # Target: < 90 minutes of average play per day to complete free track
```

## IAP Purchase Flow (Godot + GodotSteam)

```gdscript
# Steam microtransaction integration
class_name SteamStore extends Node

func initiate_purchase(item_def_id: int, quantity: int = 1) -> void:
    # Show confirmation with real price before initiating
    var price := Steam.getItemPrice(item_def_id)
    _show_purchase_confirmation(item_def_id, price, func(confirmed: bool):
        if not confirmed:
            return
        var purchase_id := Steam.startPurchase([item_def_id], [quantity])
        Steam.purchase_result.connect(_on_purchase_result, CONNECT_ONE_SHOT)
    )

func _on_purchase_result(result: int, purchase_id: int, items: Array) -> void:
    match result:
        1:  # k_EResultOK
            _grant_items(items)
            _show_purchase_success()
        _:
            _show_purchase_failed(result)

func _show_purchase_confirmation(item_id: int, price: float, callback: Callable) -> void:
    # MANDATORY: show real price before purchase
    # MANDATORY: show exactly what the player is buying
    # MANDATORY: provide prominent "Cancel" option equal in size to "Confirm"
    var dialog := ConfirmationDialog.new()
    dialog.title = tr("STORE_CONFIRM_PURCHASE_TITLE")
    dialog.dialog_text = tr("STORE_CONFIRM_PURCHASE_BODY") % [
        Steam.getItemName(item_id),
        "$%.2f" % price  # Always show real currency
    ]
    dialog.confirmed.connect(func(): callback.call(true))
    dialog.canceled.connect(func(): callback.call(false))
    add_child(dialog)
    dialog.popup_centered()
```

## Spending Limit (Voluntary Self-Cap)

```gdscript
# Let players set their own spending limits - ethical responsibility feature
class_name SpendingLimits extends Resource
@export var monthly_limit_cents: int = 0  # 0 = no limit
@export var notify_at_percent: float = 0.8  # Warn at 80% of limit

var _spent_this_month_cents: int = 0
var _month_key: String = ""  # "2026-02" format

func can_purchase(price_cents: int) -> bool:
    _refresh_month()
    if monthly_limit_cents <= 0:
        return true  # No limit set
    return (_spent_this_month_cents + price_cents) <= monthly_limit_cents

func record_purchase(price_cents: int) -> void:
    _refresh_month()
    _spent_this_month_cents += price_cents
    _save()
    if monthly_limit_cents > 0:
        var ratio := float(_spent_this_month_cents) / float(monthly_limit_cents)
        if ratio >= notify_at_percent:
            EventBus.spending_limit_warning.emit(ratio)

func _refresh_month() -> void:
    var now := Time.get_datetime_dict_from_system()
    var current_key := "%04d-%02d" % [now.year, now.month]
    if current_key != _month_key:
        _month_key = current_key
        _spent_this_month_cents = 0
        _save()
```

## Anti-Patterns (Explicitly Banned)

- **Loot boxes without disclosed odds**: Illegal in Belgium and Netherlands. Ethically wrong everywhere. Always show drop rates.
- **Premium currency bundles with remainder**: Bundle 550 gems, items cost 500 - 50 orphaned gems push next purchase. Bundles must be exact multiples of item prices.
- **Countdown timers on digital goods**: "Expires in 3:00:00" on infinitely reproducible virtual goods is a lie that exploits FOMO.
- **Progress reset threats**: "Your account will be deactivated and progress lost if you don't pay" - pure coercion.
- **Pay-to-win in any competitive context**: Buying power in PvP is fundamentally unfair and alienates the player base. Revenue will peak then collapse.
