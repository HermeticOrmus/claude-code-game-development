---
description: "Extract strings, manage translations, test, or ship a localized game build"
argument-hint: "[extract|translate|test|ship] <language or scope>"
---

# /localize

Game localization: string extraction, PO file management, plural forms, RTL support, and CJK font setup.

## Trigger

`/localize [action] [target]`

## Actions

### `extract`
Audit codebase for localizable strings and extract to POT template.

```
/localize extract "scan GDScript files for hardcoded strings not wrapped in tr()"
/localize extract "generate POT file from all tr() and tr_n() calls"
/localize extract "find strings concatenated with variables"
```

**Output**: List of untranslated strings with file/line, POT file template, code fixes for concatenation issues.

### `translate`
Generate or validate PO translation files.

```
/localize translate "create French PO file structure from English POT"
/localize translate "add Japanese locale with CJK font configuration"
/localize translate "validate Russian PO file plural forms (3 forms required)"
```

**Output**: PO file structure, plural form header for target language, validation checklist.

### `test`
Set up localization testing and pseudo-localization.

```
/localize test "enable pseudo-localization to find untranslated strings"
/localize test "validate Arabic RTL layout"
/localize test "test German locale for UI overflow"
```

**Output**: Pseudo-localization setup, RTL test checklist, layout expansion testing guide.

### `ship`
Prepare localization artifacts for release.

```
/localize ship "generate translation CSV from PO files for Godot"
/localize ship "font fallback chain covering 8 target locales"
/localize ship "locale selector UI with flag icons"
```

**Output**: CSV generation script, font setup code, locale selector Control implementation.

## Examples

**Finding untranslated strings:**
```
/localize extract "find all hardcoded English strings in res://ui/"
```
Search pattern: strings in quotes not preceded by `tr(` or `tr_n(`. Produces regex for Grep + list of violations.

**Adding Japanese localization:**
```
/localize translate "add Japanese locale with proper CJK font fallback"
```
Produces:
- `messages.ja.po` template with correct header `Plural-Forms: nplurals=1; plural=0;` (Japanese has 1 plural form)
- Font setup loading NotoSansCJK-Regular.ttf as fallback
- RTL: false (Japanese is LTR)
- Line height compensation for CJK taller characters

**Plural forms by language:**
```
/localize translate "add Polish locale with correct plural forms"
```
Polish has 4 forms: 1, 2-4 (but not 12-14), 5-21 (and 12-14), other. Produces header + msgstr[0-3] structure.

## Plural Forms Reference

| Language | Forms | Rule |
|----------|-------|------|
| English | 2 | n != 1 |
| French | 2 | n > 1 |
| German | 2 | n != 1 |
| Russian | 3 | complex (n%10==1, n%10 in 2-4, rest) |
| Polish | 4 | very complex |
| Japanese | 1 | always plural[0] |
| Arabic | 6 | zero, one, two, few, many, other |
| Chinese | 1 | always plural[0] |
