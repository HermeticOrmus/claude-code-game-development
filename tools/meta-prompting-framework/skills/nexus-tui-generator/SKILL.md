# NEXUS TUI Generator Skill

> **Version**: 1.0.0
> **Purpose**: Generate production-ready TUI applications from natural language using iterative meta-prompting
> **Theme**: Gold (#D4AF37) and Navy Blue (#1B365D)

---

## Invocation

```
/nexus-tui-generator "Create a [description of your TUI application]"
```

---

## Core Philosophy

This skill embodies three foundational principles:

### 1. First Principles (Musk Mandate)
- Question every assumption about how TUIs should work
- Strip complexity to atomic units: characters on screen
- 10x improvement or nothing

### 2. Contrarian Insight (Thiel Thesis)
- LLMs can design better UIs than manual coding
- Terminal is AI's native GUI
- Self-improving generation is the moat

### 3. Vertical Integration
- Own intent → design → code → render
- No external bottlenecks
- Each layer enhances the next

---

## Iterative Meta-Prompt Protocol

### PHASE 1: Intent Analysis (Iteration 1)

```xml
<intent_analysis>
  <task>Analyze the user's natural language description</task>

  <actions>
    <action priority="1">
      Extract the PRIMARY GOAL: What is the user trying to accomplish?
      Strip away implementation details. Focus on the outcome.
    </action>

    <action priority="2">
      Identify COMPONENT PRIMITIVES required:
      - Input: textinput, textarea, form fields
      - Display: list, table, viewport, tree
      - Feedback: progress, spinner, gauge
      - Navigation: paginator, tabs, menu
      - Layout: split panes, modals, overlays
    </action>

    <action priority="3">
      Assess COMPLEXITY SCORE (0.0 - 1.0):
      - < 0.3 SIMPLE: Single component, direct implementation
      - 0.3-0.7 MEDIUM: Multi-component, state coordination
      - > 0.7 COMPLEX: Dynamic behavior, external integration
    </action>

    <action priority="4">
      Map to CHARMBRACELET ECOSYSTEM:
      - Bubble Tea: Core framework (Model-Update-View)
      - Bubbles: Pre-built components
      - Lip Gloss: Styling (Gold/Navy theme)
      - Huh: Form generation
    </action>
  </actions>

  <output_format>
    ## Intent Analysis

    **Primary Goal**: [One sentence describing user outcome]

    **Complexity**: [Score] ([SIMPLE/MEDIUM/COMPLEX])

    **Components Required**:
    - [Component 1]: [Purpose]
    - [Component 2]: [Purpose]
    ...

    **Architecture Pattern**: [Pattern name and rationale]
  </output_format>
</intent_analysis>
```

### PHASE 2: Component Synthesis (Iteration 2)

```xml
<component_synthesis>
  <input>Previous iteration intent analysis + quality assessment</input>

  <actions>
    <action priority="1">
      Design COMPONENT HIERARCHY:
      ```
      App (root Model)
      ├── Header (static)
      ├── MainContent (dynamic)
      │   ├── Component A
      │   └── Component B
      └── Footer (keybindings)
      ```
    </action>

    <action priority="2">
      Define STATE FLOW:
      - What state does each component own?
      - How do components communicate?
      - What triggers re-renders?
    </action>

    <action priority="3">
      Apply GOLD/NAVY THEME:
      - Gold (#D4AF37): Actions, focus, highlights
      - Navy (#1B365D): Containers, backgrounds
      - DeepNavy (#0D1B2A): Root background
      - White (#FFFFFF): Primary text
    </action>

    <action priority="4">
      Map KEYBINDINGS:
      - Navigation: j/k, up/down, tab
      - Actions: enter, space, e
      - Global: q (quit), ? (help), / (search)
    </action>
  </actions>

  <output_format>
    ## Component Architecture

    ```
    [ASCII diagram of component hierarchy]
    ```

    ## State Management

    | Component | State | Updates On |
    |-----------|-------|------------|
    | ... | ... | ... |

    ## Theme Application

    | Element | Color | Hex |
    |---------|-------|-----|
    | ... | ... | ... |

    ## Keybindings

    | Key | Action | Scope |
    |-----|--------|-------|
    | ... | ... | ... |
  </output_format>
</component_synthesis>
```

### PHASE 3: Code Generation (Iteration 3+)

```xml
<code_generation>
  <input>Architecture from Phase 2 + extracted patterns + error analysis</input>

  <principles>
    <principle name="idiomatic_go">
      Follow Go conventions: gofmt, error handling, naming
      Use Bubble Tea patterns: Model, Init, Update, View
      Avoid over-engineering: YAGNI applies
    </principle>

    <principle name="lipgloss_mastery">
      Define styles at package level
      Compose styles with Inherit()
      Use adaptive colors for terminal compatibility
    </principle>

    <principle name="accessibility">
      High contrast ratios (Gold on Navy passes WCAG AA)
      Keyboard-navigable (no mouse required)
      Screen reader hints where applicable
    </principle>
  </principles>

  <code_structure>
    main.go:
    - package main
    - import statements
    - Model struct
    - Init() tea.Cmd
    - Update(msg tea.Msg) (tea.Model, tea.Cmd)
    - View() string
    - main()

    styles.go:
    - package main
    - Color constants (Gold, Navy, etc.)
    - Style definitions
    - Theme functions

    components.go (if complex):
    - Sub-models
    - Sub-update functions
    - Sub-view functions
  </code_structure>

  <quality_check>
    Before outputting code, verify:
    [ ] Compiles without errors (go build)
    [ ] No unused imports or variables
    [ ] All keybindings implemented
    [ ] Theme consistently applied
    [ ] Error states handled gracefully
  </quality_check>
</code_generation>
```

---

## Quality Assessment Rubric

Score each dimension 0.0 - 1.0:

### Functionality (30%)
```
1.0: All user requirements met, intuitive interaction, robust error handling
0.8: Core requirements met, minor UX issues, basic error handling
0.6: Most requirements met, some confusion, limited error handling
0.4: Partial implementation, significant gaps
0.2: Minimal functionality, major missing features
0.0: Does not function
```

### Aesthetics (25%)
```
1.0: Gold/Navy theme perfect, clear hierarchy, delightful animations
0.8: Theme consistent, good hierarchy, appropriate animations
0.6: Theme mostly applied, some inconsistency
0.4: Partial theming, unclear hierarchy
0.2: Minimal styling, poor visual design
0.0: No theming applied
```

### Code Quality (25%)
```
1.0: Idiomatic Go, perfect Bubble Tea patterns, highly maintainable
0.8: Clean code, proper patterns, maintainable
0.6: Working code, minor pattern deviations
0.4: Functional but messy, some anti-patterns
0.2: Barely working, significant issues
0.0: Does not compile
```

### Performance (20%)
```
1.0: Instant response, handles large data, efficient rendering
0.8: Fast response, good data handling, minimal redraws
0.6: Acceptable speed, some lag with large data
0.4: Noticeable delays, inefficient rendering
0.2: Slow, frequent lag
0.0: Unusable performance
```

### Decision Matrix
```
Total >= 0.85: ACCEPT - Output is production-ready
Total 0.70-0.84: ITERATE - Improve weakest dimension
Total 0.50-0.69: RESTRUCTURE - Reconsider architecture
Total < 0.50: RESTART - Begin from intent analysis
```

---

## Context Extraction Protocol

After each iteration, extract:

### Patterns (What worked)
```xml
<patterns>
  <pattern type="component">
    Name: [Pattern name]
    Context: [When to use]
    Implementation: [Key code snippet]
  </pattern>

  <pattern type="state">
    Flow: [State transition description]
    Trigger: [What causes transition]
  </pattern>

  <pattern type="style">
    Element: [What was styled]
    Approach: [How it was styled]
    Result: [Visual outcome]
  </pattern>
</patterns>
```

### Constraints (What limits apply)
```xml
<constraints>
  <constraint type="terminal">
    Limitation: [e.g., 256 colors only]
    Adaptation: [How we handled it]
  </constraint>

  <constraint type="framework">
    Limitation: [e.g., Bubble Tea message passing]
    Workaround: [Alternative approach]
  </constraint>
</constraints>
```

### Learnings (What to do differently)
```xml
<learnings>
  <learning>
    Issue: [What went wrong or was suboptimal]
    Root Cause: [Why it happened]
    Improvement: [How to do better next iteration]
  </learning>
</learnings>
```

---

## Example Invocations

### Simple (Complexity < 0.3)
```
/nexus-tui-generator "Progress bar that fills over 10 seconds"
```

**Expected Iterations**: 1-2
**Expected Output**: Single file, ~50 lines

### Medium (Complexity 0.3-0.7)
```
/nexus-tui-generator "Todo list with add, complete, and delete functionality"
```

**Expected Iterations**: 2-3
**Expected Output**: Single file, ~150 lines

### Complex (Complexity > 0.7)
```
/nexus-tui-generator "File browser with fuzzy search, preview pane, and vim keybindings"
```

**Expected Iterations**: 3-5
**Expected Output**: Multiple files, ~400 lines

---

## Theme Quick Reference

### Colors
| Name | Hex | RGB | Use |
|------|-----|-----|-----|
| Gold | #D4AF37 | 212,175,55 | Primary actions, focus |
| Navy | #1B365D | 27,54,93 | Containers, borders |
| DeepNavy | #0D1B2A | 13,27,42 | Background |
| LightGold | #E5C158 | 229,193,88 | Hover states |
| Surface | #2A4A7A | 42,74,122 | Elevated elements |
| White | #FFFFFF | 255,255,255 | Primary text |
| Muted | #A8B5C4 | 168,181,196 | Secondary text |

### Lip Gloss Snippets
```go
// Primary button
ButtonStyle := lipgloss.NewStyle().
    Background(lipgloss.Color("#D4AF37")).
    Foreground(lipgloss.Color("#0D1B2A")).
    Padding(0, 3).
    Bold(true)

// Container
ContainerStyle := lipgloss.NewStyle().
    Background(lipgloss.Color("#1B365D")).
    BorderStyle(lipgloss.RoundedBorder()).
    BorderForeground(lipgloss.Color("#D4AF37")).
    Padding(1, 2)

// Selected item
SelectedStyle := lipgloss.NewStyle().
    Background(lipgloss.Color("#1B365D")).
    Foreground(lipgloss.Color("#D4AF37")).
    Bold(true)
```

---

## Integration Points

### With Meta-Prompting Engine
```python
from meta_prompting_engine.core import MetaPromptingEngine

engine = MetaPromptingEngine()
result = engine.process(
    task="Generate TUI: file browser with search",
    max_iterations=5,
    quality_threshold=0.85
)
```

### With Claude Code CLI
```bash
# Direct invocation
claude "/nexus-tui-generator 'dashboard with metrics'"

# In workflow
- skill: nexus-tui-generator
  input: "Create log viewer with filtering"
```

### With Charmbracelet Tools
```bash
# Generate demo with VHS
vhs demo.tape  # Uses generated application

# Deploy via SSH with Wish
./generated-app --ssh-mode
```

---

## Troubleshooting

### "Generated code doesn't compile"
1. Check Go version (requires 1.21+)
2. Run `go mod tidy` to resolve dependencies
3. Verify import paths match actual packages

### "Theme looks wrong"
1. Check terminal supports TrueColor: `echo $COLORTERM`
2. Fall back to 256-color palette if needed
3. Test in different terminals (iTerm2, Kitty, etc.)

### "Quality score stuck below threshold"
1. Simplify the request (reduce scope)
2. Provide more specific requirements
3. Check if request is actually achievable in TUI

---

## Changelog

- **v1.0.0** (2025-11-22): Initial release with Gold/Navy theme
