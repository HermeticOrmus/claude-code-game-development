# Meta-Prompting Commands

Slash commands for working with the meta-prompting framework.

## Available Commands

### `/meta-agent`

Generate and invoke meta-prompts using the V2 library.

**Usage:**
```bash
/meta-agent <task description>
```

**What it does:**
- Analyzes task complexity
- Selects optimal meta-prompt from V2 library
- Applies meta-prompt to task
- Returns enhanced output

**Example:**
```bash
/meta-agent Design a distributed caching system with consistency guarantees
```

**See:** `meta-agent.md` for full documentation

---

### `/meta-command`

Meta-command for building multiple skills in parallel using Context7 research and validated workflows.

**Usage:**
```bash
/meta-command [--type TYPE] [--discover] [--spec-only] [--create]
```

**Flags:**
- `--type` - Command type (skill, agent, workflow, command)
- `--discover` - Discover domain primitives
- `--spec-only` - Generate specification without implementation
- `--create` - Create the resource
- `--mcp-include` - Include MCP server integration
- `--dry-run` - Preview without creating
- `--help` - Show help

**Example:**
```bash
/meta-command --type skill --discover --create "PostgreSQL advanced features"
```

**See:** `meta-command.md` for full documentation

---

### `/grok`

Interactive dialogue orchestration with Grok for extended reasoning sessions.

**Usage:**
```bash
/grok [--mode MODE] [--turns N] [--output FILE]
```

**Modes:**
- `loop` - Continuous dialogue loop
- `debate` - Adversarial discussion
- `podcast` - Conversational exploration
- `pipeline` - Sequential processing
- `dynamic` - Adaptive mode selection

**Flags:**
- `--mode` - Interaction mode
- `--turns` - Number of dialogue turns (default: 5)
- `--output` - Save to file
- `--verbose` - Detailed output
- `--quick` - Fast single-turn query

**Example:**
```bash
/grok --mode debate --turns 7 "Should we use microservices or monolith?"
```

**See:** `grok.md` for full documentation

---

## Command Integration Patterns

### Pattern 1: Discovery → Meta-Agent → Create

```bash
# Discover domain
/meta-command --type skill --discover "reinforcement learning"

# Generate meta-prompt for implementation
/meta-agent Create a comprehensive reinforcement learning skill

# Create the skill
/meta-command --type skill --create "reinforcement learning"
```

### Pattern 2: Research → Grok → Synthesize

```bash
# Extended research dialogue
/grok --mode podcast --turns 10 --output research.md "Explore categorical approaches to meta-prompting"

# Analyze findings with meta-agent
/meta-agent Synthesize the research findings into a framework specification
```

### Pattern 3: Progressive Enhancement

```bash
# Start with basic meta-agent
/meta-agent Design an API rate limiter

# Extend with grok exploration
/grok --mode debate "Trade-offs in rate limiting algorithms"

# Create production artifact
/meta-command --type agent --create "rate-limiter-agent"
```

---

## Quick Reference

| Command | Purpose | Best For |
|---------|---------|----------|
| `/meta-agent` | Apply V2 meta-prompts | Quick task enhancement |
| `/meta-command` | Build skills/agents | Resource creation |
| `/grok` | Extended reasoning | Deep exploration |

---

## See Also

- [Meta-Prompts V2](../meta-prompts/v2/META_PROMPTS.md) - Production meta-prompts
- [Meta² Agent](../agents/meta2/README.md) - Framework generator
- [Quick Start](../docs/QUICK_START.md) - Get started guide
