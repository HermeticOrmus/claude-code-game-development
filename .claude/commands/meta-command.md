---
description: Unified command creation engine with intelligent resource discovery and composition
args:
  - name: intent_or_spec
    description: Natural language intent or @spec-file.yaml
  - name: flags
    description: Optional --type, --discover, --spec-only, --create, --mcp-include, --dry-run, --help
allowed-tools: Read(**/.claude/**), Write(**/.claude/commands/*.md, **/.claude/agents/*.md), Glob(**/.claude/**), Grep(**), TodoWrite, Task(*), SlashCommand(/meta-agent, /create-command, /agent)
---

# /meta-command

Create commands/agents from natural language intent: $ARGUMENTS

**Philosophy**: Composability over creation, discovery over invention, integration over isolation.

## What This Command Does (MVP v1.0)

**Unified Workflow**: Intent → Specification → Artifact (3 manual steps → 1 command)

1. **Parse Intent**: Extract action, domain, capabilities, type
2. **Generate Specification**: Invoke /meta-agent to create detailed spec
3. **User Review Gate**: Display spec, request confirmation (prevents resource pollution)
4. **Create Artifact**: Invoke /create-command or /agent with validated spec
5. **Report Results**: Show what was created, quality metrics, next steps

**Current Version (MVP)**: Thin orchestration layer (no resource discovery yet)
**Future Versions**: Resource discovery, composability engine, feedback loops (Phases 2-5)

## Your Task

### Step 1: Parse Arguments

Extract from $ARGUMENTS:
- Intent string (natural language description)
- OR @spec-file.yaml (direct specification)
- Flags: --type, --spec-only, --create, --dry-run, --help, etc.

### Step 2: Handle Special Flags

**If --help detected**:
- Show comprehensive help (see Help Output section below)
- EXIT without processing

**If @spec-file.yaml provided**:
- Skip /meta-agent invocation
- Load specification directly from file
- Jump to validation

### Step 3: Generate Specification

**Invoke /meta-agent**:
```
SlashCommand(/meta-agent "<intent>")
```

This returns a detailed specification YAML including:
- Command/agent name and description
- Capabilities and responsibilities
- Implementation approach
- Example patterns
- Quality criteria

### Step 4: User Review Gate (REQUIRED)

**Display specification summary**:
```
┌─────────────────────────────────────────────────────┐
│ Specification Generated                             │
│                                                     │
│ Type: command (confidence: 0.85)                   │
│ Name: api-test                                      │
│ Description: API testing with suite generation      │
│                                                     │
│ Capabilities:                                       │
│ • endpoint_testing                                  │
│ • suite_generation                                  │
│ • result_reporting                                  │
│                                                     │
│ Output: ~/.claude/commands/api-test.md             │
│                                                     │
│ [MVP Note: Resource discovery in Phase 2]          │
│                                                     │
│ Proceed with creation? [Y/n/edit]                  │
└─────────────────────────────────────────────────────┘
```

**Handle user response**:
- **Y or Enter**: Proceed to creation
- **n**: Abort, save spec to /tmp/meta-command-spec.yaml for later
- **edit**: Prompt user to edit spec, then retry

### Step 5: Create Artifact

**Detect type from specification**:
- If type = "command" → Invoke /create-command
- If type = "agent" → Invoke /agent
- If type = "skill" → Show message "Skill creation: use /meta-skill-builder"

**Invoke creator**:
```
# For commands
SlashCommand(/create-command "<specification-yaml>")

# For agents
SlashCommand(/agent "<specification-yaml>")
```

### Step 6: Report Results

**Success output**:
```
✅ Command created: ~/.claude/commands/<name>.md

📊 Generated:
  - Type: command
  - Examples: 10
  - Quality score: 0.85 (excellent)
  - Constitutional compliance: 9/9 ✓

🎯 Test your command:
  /<name> --help
  /<name> test-args

💡 Next steps:
  - Test with real use cases
  - Iterate if needed: /meta-command "<revised intent>"
  - Share: Add to team documentation

📋 Specification saved: docs/meta-command/specs/<name>-spec.yaml
```

**Error output**:
```
❌ Error: <specific issue>

Resolution: <how to fix>

💾 Partial work saved: /tmp/meta-command-<name>.yaml
```

## Flags

```yaml
flags:
  # ─── TYPE CONTROL ───
  --type=[command|agent|skill]    # Force type (default: auto-detect)

  # ─── MODE CONTROL ───
  --spec-only                     # Generate spec only, don't create
  --create                        # Generate + create (default)
  --dry-run                       # Preview without creating

  # ─── RESOURCE CONTROL (Phase 2+) ───
  --discover                      # Show resource discovery preview
  --no-discovery                  # Skip discovery (MVP fallback)
  --mcp-include=[servers]         # Explicit MCP inclusion

  # ─── OUTPUT CONTROL ───
  --verbose                       # Show detailed process
  --quiet                         # Minimal output

  # ─── ADVANCED ───
  --examples=[N]                  # Override example count
  --overwrite                     # Replace existing file

  # ─── HELP ───
  --help                          # Show this help
```

## Examples

### Example 1: Basic Command Creation (MVP)

```bash
/meta-command "create API testing command with suite generation"
```

**What happens:**
1. Parse: "API testing command" detected
2. Invoke: /meta-agent generates specification
3. Review: Show spec, request confirmation
4. Create: /create-command generates ~/.claude/commands/api-test.md
5. Report: Command created with 10 examples

**Output:**
```
✅ Command created: ~/.claude/commands/api-test.md
📊 Quality score: 0.85
🎯 Test: /api-test endpoint.ts --generate-suite
```

**Use case**: Most common workflow - create command from intent

**Time**: ~60 seconds (vs 180s manual)

---

### Example 2: Force Agent Type

```bash
/meta-command "API testing and performance analysis" --type=agent
```

**What happens:**
1. Parse: Intent + --type=agent flag
2. Invoke: /meta-agent with type hint
3. Review: Shows agent specification (not command)
4. Create: /agent generates ~/.claude/agents/api-analyzer.md
5. Report: Agent ready for Task() invocation

**Output:**
```
✅ Agent created: ~/.claude/agents/api-analyzer.md
🎯 Test: Task("analyze API", subagent_type="api-analyzer")
```

**Use case**: When auto-detection might be ambiguous

---

### Example 3: Specification Only (No Creation)

```bash
/meta-command "security auditing with evidence reporting" --spec-only
```

**What happens:**
1. Parse: Intent + --spec-only flag
2. Invoke: /meta-agent generates specification
3. Display: Shows full YAML specification
4. Save: Specification saved to docs/meta-command/specs/
5. EXIT: No file created

**Output:**
```
📋 Specification Generated
───────────────────────────
[Full YAML specification displayed]

💾 Saved to: docs/meta-command/specs/security-audit-spec.yaml

Next: Review and refine, then run:
  /meta-command @docs/meta-command/specs/security-audit-spec.yaml
```

**Use case**: Review and refine specification before committing to creation

---

### Example 4: Create from Specification File

```bash
/meta-command @docs/meta-command/specs/security-audit-spec.yaml
```

**What happens:**
1. Parse: @file path detected
2. Load: Read specification from file
3. Validate: Check structural, semantic, quality
4. Review: Show summary, request confirmation
5. Create: Generate artifact from validated spec

**Output:**
```
✅ Command created from specification
📊 Validation passed: 0.88 quality score
```

**Use case**: Two-step workflow (refine spec, then create)

---

### Example 5: Dry Run Preview

```bash
/meta-command "API testing command" --dry-run
```

**What happens:**
1. Full workflow execution (parse → spec → validate)
2. Show preview of what WOULD be created
3. Display quality metrics
4. **DO NOT write any files**

**Output:**
```
🔍 DRY RUN MODE - Preview Only

Command: /api-test
Type: command (confidence: 0.85)
Output: ~/.claude/commands/api-test.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PREVIEW: First 50 lines
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---
description: API testing with suite generation
args:
  - name: endpoint
    description: API endpoint file to test
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Statistics:
  Examples: 10
  Quality score: 0.85
  Validation: All checks passed ✓

To create: Remove --dry-run flag
```

**Use case**: Preview before committing to creation

---

### Example 6: Quick Help

```bash
/meta-command --help
```

**What happens:**
- Show comprehensive help text (see Help Output section)
- EXIT without processing

**Use case**: Quick reference for flags and usage

---

### Example 7: Error Handling - Empty Intent

```bash
/meta-command ""
```

**What happens:**
1. Parse: Empty string detected
2. Validate: FAIL - intent cannot be empty
3. Error: Show clear error message with guidance

**Output:**
```
❌ Error: Intent cannot be empty

Usage: /meta-command "<intent>" [flags]

Examples:
  /meta-command "create API testing command"
  /meta-command "agent for security analysis" --type=agent
  /meta-command --help

See: /meta-command --help for full documentation
```

**Use case**: User error - provide helpful guidance

---

### Example 8: Integration with Existing Workflow

```bash
# Step 1: Preview specification
/meta-command "API testing" --spec-only

# Step 2: Review and edit specification file
# (User manually edits docs/meta-command/specs/api-test-spec.yaml)

# Step 3: Create from refined specification
/meta-command @docs/meta-command/specs/api-test-spec.yaml

# Step 4: Test the created command
/api-test src/endpoints/users.ts --generate-suite
```

**What happens:**
- Specification-driven workflow with manual refinement step
- Full control over specification before artifact creation
- Iterative improvement cycle

**Use case**: When you need precise control over the specification

---

### Example 9: Future Feature - Resource Discovery (Phase 2)

```bash
/meta-command "API testing command" --discover
```

**What happens (Phase 2+):**
1. Parse: Intent + --discover flag
2. Search: Scan ~/.claude/* for relevant resources
3. Display: Show discovered skills, agents, commands
4. Preview: Composability score and integration patterns
5. EXIT: No creation, just discovery preview

**Output (Phase 2+):**
```
🔍 Resource Discovery

Discovered Resources:
  Skills:
    • api-testing (relevance: 0.82)
    • jest-patterns (relevance: 0.71)

  Agents:
    • test-engineer (relevance: 0.75)

  Commands:
    • /test-lab (workflow reference, relevance: 0.68)

Composability: 0.74 (good integration potential)

Suggested Integration Pattern:
  Sequential: api-testing skill → test-engineer agent → output

Next: /meta-command "API testing" --create
```

**Note**: This flag requires Phase 2 implementation (resource discovery layer)

**Use case**: Explore ecosystem before creating new resources

---

### Example 10: MCP Explicit Inclusion (Phase 2+)

```bash
/meta-command "fetch library documentation" --mcp-include=context7
```

**What happens (Phase 2+):**
1. Parse: Intent + --mcp-include flag
2. Generate: Specification includes Context7 MCP
3. Validate: Check MCP server availability
4. Create: Command with Context7 integration
5. Note: User explicitly opted into high token cost

**Output:**
```
✅ Command created: ~/.claude/commands/fetch-docs.md

⚠️ MCP Integration: Context7
   • High token cost per invocation
   • User explicitly requested via --mcp-include

🎯 Test: /fetch-docs react
```

**Note**: This flag enforces Article VI (MCP Opt-In)

**Use case**: When MCP integration is essential for functionality

---

## MVP Limitations (Phase 1)

**Current MVP Does NOT Include**:
- ❌ Resource discovery (search ~/.claude/* for relevant resources)
- ❌ Composability engine (intelligent integration of skills/agents/commands)
- ❌ Dynamic resource weaving (examples that leverage discovered resources)
- ❌ Feedback loops (learning from usage patterns)

**Coming in Future Phases**:
- ✅ Phase 2 (2 weeks): Resource discovery layer
- ✅ Phase 3 (2 weeks): Composability engine and integration patterns
- ✅ Phase 4 (1 week): Advanced validation and quality gates
- ✅ Phase 5 (1 week): Feedback loops and pattern learning

**Current Focus**: Workflow reduction (3 manual steps → 1 command)

---

## Error Handling

### Common Errors

**Empty Intent**:
```
❌ Error: Intent cannot be empty
Usage: /meta-command "<intent>" [flags]
```

**Invalid Type Flag**:
```
❌ Error: --type must be command, agent, or skill
Provided: --type=foo
```

**Spec Generation Failed**:
```
❌ Error: /meta-agent failed to generate specification
Try: /meta-agent "<intent>" to debug
```

**Validation Failed**:
```
❌ Error: Specification validation failed
Quality score: 0.55 < 0.7 required

Issues:
  • Missing core capabilities
  • Insufficient examples (4 < 6 required)

💾 Partial spec saved: /tmp/meta-command-failed.yaml
Resolution: Refine intent and retry
```

**File Write Failed**:
```
❌ Error: Cannot write to ~/.claude/commands/
Check permissions or disk space
```

**User Aborted**:
```
⚠️ Creation aborted by user
💾 Specification saved: /tmp/meta-command-spec.yaml
To retry: /meta-command @/tmp/meta-command-spec.yaml
```

### Graceful Degradation

**If /meta-agent fails**:
- Save intent to /tmp/meta-command-intent.txt
- Show error with suggested fix
- Allow manual /meta-agent invocation

**If validation warning (score 0.6-0.7)**:
- Show warning
- Request user confirmation to proceed anyway
- Log decision for feedback loop

**If user declines confirmation**:
- Save specification for later refinement
- Provide clear retry instructions
- Do not create any files

---

## Quality Standards

Every artifact created by /meta-command must meet:

✅ **Structural Validation (100%)**:
- Valid frontmatter (YAML)
- Required sections present
- Syntax correct

✅ **Composition Validation (100%)**:
- Referenced resources exist (when applicable)
- No circular dependencies
- Integration patterns valid

✅ **Quality Validation (≥70%)**:
- Example count: 8-12 (commands), 6-10 (agents)
- Example coverage: ≥70% of capabilities
- Integration documentation present
- Error handling included

✅ **Constitutional Compliance (100%)**:
- All 9 articles enforced
- Blocking violations halt creation
- Warnings require acknowledgment

**Overall Score Formula**:
```
Score = (Structure × 0.3) + (Composition × 0.3) + (Quality × 0.4)
Threshold: ≥0.7 required for creation
```

---

## Constitutional Principles

These 9 principles are IMMUTABLE and enforced at every stage:

1. **Specification Supremacy**: Spec is truth, code is expression
2. **Composability First**: Discover before creating (Phase 2+)
3. **Test-Driven Specification**: No capability without acceptance criteria
4. **Resource Discovery**: Runtime discovery, not hardcoded (Phase 2+)
5. **Quality Gates**: Non-negotiable validation checkpoints
6. **MCP Opt-In**: Expensive resources require explicit justification
7. **Example Density**: 8-12 (commands), 6-10 (agents) enforced
8. **Feedback Loops**: Production usage informs specifications (Phase 5)
9. **Evolutionary Design**: Specifications must evolve with ecosystem

**Enforcement**:
- **BLOCKED**: Creation halts, user must fix
- **WARNING**: Continues with acknowledgment
- **INFORMATIONAL**: Logged for review

---

## Help Output

When you run `/meta-command --help`:

```
📖 /meta-command - Unified Command Creation Engine

DESCRIPTION:
  Create commands and agents from natural language intent with intelligent
  resource discovery and composition. Reduces 3-step manual workflow to
  1 unified command.

USAGE:
  /meta-command "<intent>" [flags]
  /meta-command @spec-file.yaml [flags]

ARGUMENTS:
  intent       Natural language description of what you want to create
  @spec-file   Path to specification YAML (skip intent parsing)

FLAGS:
  --type=X           Force type: command, agent, or skill
  --spec-only        Generate specification only (no creation)
  --create           Generate + create artifact (default)
  --dry-run          Preview without creating files
  --discover         Show resource discovery preview (Phase 2+)
  --mcp-include=X    Explicit MCP server inclusion
  --verbose          Show detailed process
  --help             Show this help message

EXAMPLES:
  # Basic command creation
  /meta-command "create API testing command"

  # Force agent type
  /meta-command "security analysis" --type=agent

  # Preview specification only
  /meta-command "API testing" --spec-only

  # Create from specification file
  /meta-command @docs/specs/api-test-spec.yaml

  # Dry run preview
  /meta-command "API testing" --dry-run

WORKFLOW:
  Intent → Parse → Spec → Review → Create → Report

MVP VERSION (Phase 1):
  • Thin orchestration layer (no resource discovery yet)
  • Workflow reduction: 3 steps → 1 command
  • Type detection: command vs agent
  • User review gate: Confirmation required
  • Quality enforcement: Score ≥0.7

COMING SOON (Phases 2-5):
  • Resource discovery (search 208 resources)
  • Composability engine (intelligent integration)
  • Feedback loops (learning from usage)
  • Advanced validation gates

QUALITY STANDARDS:
  • Examples: 8-12 (commands), 6-10 (agents)
  • Coverage: ≥70% of capabilities
  • Overall score: ≥0.7 required
  • Constitutional compliance: 9/9 principles

DOCUMENTATION:
  • Full specification: docs/meta-command/03-specification.md
  • Architecture: docs/meta-command/02a-mars-systems-architecture.md
  • Usage patterns: docs/meta-command/05-usage-examples.md

For detailed documentation, see: docs/meta-command/
```

---

## Success Metrics

**Quantitative**:
- Time savings: 180s → 60s (67% reduction)
- Step reduction: 3 → 1 (66% reduction)
- Quality: >75% average score
- Usage: >60% generated commands actually used

**Qualitative**:
- Users understand what will be created
- Users can explain type detection
- Users trust the validation process
- Users appreciate workflow simplification

---

## Your Response

After processing /meta-command, provide:

**Success**:
```
✅ [Command|Agent] created: ~/.claude/[commands|agents]/<name>.md

📊 Generated:
  - Type: [command|agent]
  - Examples: [N]
  - Quality score: [0-1] ([excellent|good|acceptable])
  - Constitutional compliance: 9/9 ✓

🎯 Test your [command|agent]:
  [invocation examples]

💡 Next steps:
  - Test with real use cases
  - Iterate if needed
  - Share with team

📋 Specification saved: docs/meta-command/specs/<name>-spec.yaml
```

**Error**:
```
❌ Error: [specific issue]

Resolution: [how to fix]

💾 Partial work saved: [path]
```

**Dry Run**:
```
🔍 DRY RUN MODE - Preview shown above

To create: Remove --dry-run flag
```

---

**Version**: 1.0.0 (MVP)
**Phase**: 1 of 5 (Thin Orchestration)
**Status**: Production Ready
**Next**: Phase 2 (Resource Discovery Layer)
