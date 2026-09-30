---
name: localization-patterns
description: "Localization code patterns: Godot tr() and TranslationServer usage, PO file structure, ICU plurals, font fallback chains for multi-script text, RTL layout mirroring, pseudo-localization, and string key naming. Use when making a game translatable or fixing text that breaks in another language."
---

# Localization Patterns

## Godot TranslationServer and tr() Usage

```gdscript
# Correct tr() usage patterns
class_name LocalizableUI extends Control

func _ready() -> void:
    # Static string - wrap in tr()
    $Label.text = tr("MENU_PLAY_BUTTON")

    # Dynamic string with variable - use format, not concatenation
    var score := 1500
    $ScoreLabel.text = tr("SCORE_DISPLAY") % score
    # PO file: msgid "SCORE_DISPLAY" msgstr "Score: %d"

    # Plural-aware string
    var item_count := 3
    $ItemLabel.text = tr_n("ITEM_COUNT_SINGULAR", "ITEM_COUNT_PLURAL", item_count) % item_count
    # PO file:
    # msgid "ITEM_COUNT_SINGULAR"
    # msgid_plural "ITEM_COUNT_PLURAL"
    # msgstr[0] "%d item"
    # msgstr[1] "%d items"

    # Listen for locale changes (font swaps, layout updates)
    TranslationServer.connect("locale_changed", _on_locale_changed)

func _on_locale_changed() -> void:
    # Refresh all translatable strings
    _ready()
    _update_fonts_for_locale()

func _update_fonts_for_locale() -> void:
    var locale := TranslationServer.get_locale()
    if locale.begins_with("ja") or locale.begins_with("zh") or locale.begins_with("ko"):
        $Label.add_theme_font_override(&"font", preload("res://fonts/NotoSansCJK.ttf"))
    elif locale.begins_with("ar") or locale.begins_with("he"):
        $Label.add_theme_font_override(&"font", preload("res://fonts/NotoSansArabic.ttf"))
        # Mirror layout for RTL
        layout_direction = Control.LAYOUT_DIRECTION_RTL
    else:
        $Label.remove_theme_font_override(&"font")
        layout_direction = Control.LAYOUT_DIRECTION_AUTO
```

## PO File Structure

```po
# messages.pot (template - generated, not translated)
# and messages.fr.po (French translation)

# Header - required, specifies plural rules
msgid ""
msgstr ""
"Project-Id-Version: MyGame 1.0\n"
"Language: fr\n"
"Plural-Forms: nplurals=2; plural=(n > 1);\n"
"Content-Type: text/plain; charset=UTF-8\n"

# Simple string
msgid "MENU_PLAY_BUTTON"
msgstr "Jouer"

# Contextual disambiguation
msgctxt "main_menu"
msgid "BACK"
msgstr "Retour"

msgctxt "character_anatomy"
msgid "BACK"
msgstr "Dos"

# Plural forms
msgid "ITEM_COUNT_SINGULAR"
msgid_plural "ITEM_COUNT_PLURAL"
msgstr[0] "%d objet"
msgstr[1] "%d objets"

# String with variables (preserve format specifiers)
msgid "SCORE_DISPLAY"
msgstr "Score : %d"

# String with named variables (safer than positional)
msgid "PLAYER_GREETING"
msgstr "Bonjour, {player_name} !"
```

## ICU Message Format for Plurals

```gdscript
# Custom ICU-style formatter for Godot (simplified)
# For full ICU support, use Unity Localization or custom GDExtension

class_name ICUFormatter
# Handles {count, plural, one{...} other{...}} syntax

static func format(template: String, vars: Dictionary) -> String:
    var result := template
    # Replace simple variables
    for key in vars:
        result = result.replace("{%s}" % key, str(vars[key]))
    return result

# Usage:
# tr("FOUND_ITEMS").format({"count": 5}) -> "Found 5 items"
# PO: msgid "FOUND_ITEMS" msgstr "Found {count} items"

# Plural with tr_n (Godot built-in):
func items_text(count: int) -> String:
    # tr_n selects singular or plural form based on count
    return tr_n("ITEM_SINGULAR", "ITEM_PLURAL", count) % count
```

## Font Fallback Chain for Multi-Script Support

```gdscript
# Set up font fallback chain covering Latin, CJK, and Arabic
func setup_global_font() -> void:
    var theme := ThemeDB.get_project_theme()
    var font := FontFile.new()
    font.load_dynamic_font("res://fonts/NotoSans-Regular.ttf")

    # CJK fallback - activates for CJK codepoints not in base font
    var cjk_font := FontFile.new()
    cjk_font.load_dynamic_font("res://fonts/NotoSansCJK-Regular.ttf")
    font.add_fallback(cjk_font)

    # Arabic fallback
    var arabic_font := FontFile.new()
    arabic_font.load_dynamic_font("res://fonts/NotoSansArabic-Regular.ttf")
    font.add_fallback(arabic_font)

    theme.default_font = font
    ThemeDB.get_project_theme().default_font = font
```

## RTL Layout Mirroring

```gdscript
# Apply RTL layout to all controls in scene
func apply_rtl_layout(root: Control, is_rtl: bool) -> void:
    var direction := Control.LAYOUT_DIRECTION_RTL if is_rtl else Control.LAYOUT_DIRECTION_LTR
    _set_layout_recursive(root, direction)

func _set_layout_recursive(node: Control, direction: Control.LayoutDirection) -> void:
    node.layout_direction = direction
    for child in node.get_children():
        if child is Control:
            _set_layout_recursive(child, direction)

# RTL detection from locale
func is_rtl_locale(locale: String) -> bool:
    const RTL_LANGUAGES: Array[String] = ["ar", "he", "ur", "fa", "dv", "yi"]
    var language := locale.split("_")[0]  # "ar_SA" -> "ar"
    return language in RTL_LANGUAGES
```

## Pseudo-Localization for Early Testing

```gdscript
# Manual pseudo-localization (Godot has built-in, but this shows the logic)
class_name PseudoLocalizer
const CHAR_MAP := {
    "a": "á", "b": "ƀ", "c": "ç", "d": "ď", "e": "é",
    "f": "ƒ", "g": "ĝ", "h": "ĥ", "i": "í", "j": "ĵ",
    "k": "ķ", "l": "ĺ", "m": "m", "n": "ñ", "o": "ó",
    "p": "ƥ", "q": "q", "r": "ŗ", "s": "ŝ", "t": "ţ",
    "u": "ú", "v": "v", "w": "ŵ", "x": "x", "y": "ý",
    "z": "ź",
}

static func pseudo_localize(text: String) -> String:
    var result := "["
    for char in text:
        result += CHAR_MAP.get(char.to_lower(), char)
    # Add 40% length padding to simulate German text expansion
    result += "_".repeat(int(text.length() * 0.4))
    result += "]"
    return result
```

## String Key Naming Convention

```
# Hierarchy: SCREEN_SECTION_ELEMENT_VARIANT
MENU_MAIN_PLAY_BUTTON          # Main menu, Play button
MENU_MAIN_SETTINGS_BUTTON      # Main menu, Settings button
HUD_HEALTH_LABEL               # HUD, health label
INVENTORY_ITEM_NAME_SWORD      # Inventory, sword item name
DIALOGUE_NPC_MERCHANT_GREETING # Merchant NPC greeting line
ERROR_SAVE_FAILED              # Error message for save failure
TUTORIAL_MOVEMENT_HINT         # Tutorial hint for movement
```

## Anti-Patterns

- **String concatenation**: `"Enemy: " + enemy.name` - word order varies by language. Use named substitution: `tr("ENEMY_LABEL").format({"name": enemy.name})`.
- **Hardcoded plural**: `"%d items"` doesn't work in languages with 3+ plural forms (Russian, Polish). Always use `tr_n()`.
- **Empty msgstr**: translators leaving msgstr blank - Godot falls back to msgid. Build QA catches this.
- **Format string reordering**: `"%s found %d items"` - translators need to reorder but `%s %d` positional args can't reorder. Use named: `"{player} found {count} items"`.
