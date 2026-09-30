# localization

Localization plugin for LibreGameDev. Covers Godot TranslationServer, gettext PO format, ICU plural forms, RTL text for Arabic/Hebrew, CJK font fallback chains, and pseudo-localization testing.

## Components

- **localization-engineer**: Agent with expertise in Godot localization, gettext workflow, plurals, RTL, and CJK font handling
- **localize**: Command for string extraction, PO file generation, localization testing, and shipping
- **localization-patterns**: Skill library with tr() usage, PO file structure, font fallback, RTL layout, and pseudo-localization

## Localization Readiness Checklist

Before first translator handoff:
- [ ] All displayed strings wrapped in `tr()` or `tr_n()`
- [ ] No string concatenation with variables (use format substitution)
- [ ] Pseudo-localization passes with no visible English in any UI
- [ ] German locale UI tested for 40% text expansion
- [ ] Arabic locale UI tested for RTL mirroring
- [ ] Font fallback chain covers all target language scripts
- [ ] POT file extracted and ready for translation memory system

## Quick Start

Audit for missing tr() calls:
```
/localize extract "find hardcoded strings not wrapped in tr()"
```

Add a new language:
```
/localize translate "add Spanish locale"
```

Enable pseudo-localization testing:
```
/localize test "enable pseudo-localization"
```
