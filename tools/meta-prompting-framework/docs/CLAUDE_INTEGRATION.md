# Claude Code `.claude/` Integration Guide

## Overview

This meta-prompting framework is designed to integrate seamlessly with Claude Code's `.claude/` configuration system, enabling you to:

1. **Generate** custom skills, agents, and commands using meta2
2. **Install** them into `.claude/` for project-wide or global use
3. **Compose** them into powerful workflows
4. **Bootstrap** to progressively higher capability levels

---

## The `.claude/` Directory Structure

```
~/.claude/                          # Global configuration
├── agents/                         # 46+ agents (including meta2, MARS, MERCURIO)
├── skills/                         # 100+ skills (including category-master, discopy)
├── commands/                       # 62+ slash commands
├── workflows/                      # 21+ multi-agent workflows
├── docs/                           # Documentation
├── settings.json                   # Global settings
└── CLAUDE.md                       # Master reference

project/.claude/                    # Project-specific overrides
├── agents/                         # Project agents (inherit + override global)
├── skills/                         # Project skills
├── commands/                       # Project commands
├── workflows/                      # Project workflows
└── settings.json                   # Project settings
```

**Inheritance Pattern**: Project `.claude/` inherits from `~/.claude/` and can override/extend.

---

## Integration Patterns

### Pattern 1: Meta-Prompting as Resource Generator

**Use meta-prompting framework to generate `.claude/` resources**

```yaml
# Use meta2 agent to generate custom skill
workflow: meta-framework-generation
parameters:
  domain_name: "React performance optimization"
  depth_levels: 5
  output_format: "claude_skill"  # New format!

# Output: Generates skill definition ready for ~/.claude/skills/
```

**Generated Output:**
```
~/.claude/skills/react-performance-optimization/
├── SKILL.md                    # Skill definition with 5 levels
├── README.md                   # Usage guide
├── EXAMPLES.md                 # Concrete examples
└── PATTERNS.md                 # Common patterns
```

**Then use it:**
```
Skill: react-performance-optimization
"Optimize this React component for performance"
```

---

### Pattern 2: Workflow Composition

**Compose meta-prompting workflows with Claude Code workflows**

```yaml
# ~/.claude/workflows/research-to-skill.yaml
name: Research to Skill Pipeline
description: Research domain → Generate framework → Create skill

steps:
  - name: research
    agent: deep-researcher
    prompt: "Research ${domain} comprehensively"

  - name: generate_framework
    workflow: meta-framework-generation  # From meta-prompting repo!
    parameters:
      domain_name: ${domain}
      depth_levels: 5

  - name: create_skill
    agent: skill-builder
    prompt: "Convert framework to Claude Code skill"

  - name: install
    command: /actualize
    description: "Sync new skill to .claude/"
```

**Usage:**
```bash
workflow: research-to-skill
  domain: "database query optimization"
```

---

### Pattern 3: Agent Chaining

**Chain meta-prompting agents with Claude Code agents**

```
User Request
     ↓
/meta-command --discover "GraphQL optimization"
     ↓
deep-researcher (Claude Code agent)
     ↓
meta2 (meta-prompting agent)
     ↓
MARS (validation agent)
     ↓
skill-builder (Claude Code agent)
     ↓
/actualize (install to .claude/)
     ↓
New skill available globally!
```

---

### Pattern 4: Progressive Capability Bootstrap

**Use meta-prompting to build better meta-prompting tools**

```
Level 0: Manual prompt engineering
     ↓
Level 1: Use V2 meta-prompts (copy-paste)
     ↓
Level 2: Generate custom frameworks with meta2
     ↓
Level 3: Install frameworks as skills
     ↓
Level 4: Use skills to generate better skills
     ↓
Level 5: Meta-skills that generate meta-prompts
     ↓
Level 6: Self-improving meta-prompting system
```

**Example:**
```bash
# Level 2: Generate framework
meta2.generate("meta-prompt optimization", 7)

# Level 3: Install as skill
skill-builder.create(framework, "meta-prompt-optimizer")

# Level 4: Use skill to improve itself!
Skill: meta-prompt-optimizer
"Optimize the Autonomous Routing meta-prompt for code generation"

# Level 5: Generate meta-skill
meta-skill-builder.create("meta-prompt-generator-skill")
```

---

## Installation Methods

### Method 1: Direct Installation

**Copy resources directly to `.claude/`**

```bash
# Install meta2 agent globally
cp agents/meta2/agent.md ~/.claude/agents/meta2.md

# Install skills
cp -r skills/category-master ~/.claude/skills/
cp -r skills/discopy-categorical-computing ~/.claude/skills/

# Install commands
cp commands/meta-agent.md ~/.claude/commands/
cp commands/meta-command.md ~/.claude/commands/

# Install workflows
cp workflows/meta-framework-generation.yaml ~/.claude/workflows/
cp workflows/quick-meta-prompt.yaml ~/.claude/workflows/

# Sync
/actualize
```

---

### Method 2: Symbolic Links (Recommended)

**Link to keep repository updated**

```bash
# Link agents
ln -s $(pwd)/agents/meta2 ~/.claude/agents/meta2
ln -s $(pwd)/agents/MARS.md ~/.claude/agents/MARS.md

# Link skills
ln -s $(pwd)/skills/category-master ~/.claude/skills/category-master
ln -s $(pwd)/skills/discopy-categorical-computing ~/.claude/skills/discopy-categorical-computing

# Link commands
ln -s $(pwd)/commands/meta-agent.md ~/.claude/commands/meta-agent.md
ln -s $(pwd)/commands/meta-command.md ~/.claude/commands/meta-command.md

# Link workflows
ln -s $(pwd)/workflows/meta-framework-generation.yaml ~/.claude/workflows/meta-framework-generation.yaml
ln -s $(pwd)/workflows/quick-meta-prompt.yaml ~/.claude/workflows/quick-meta-prompt.yaml

# Sync
/actualize
```

**Advantage**: Updates to repository automatically available in Claude Code!

---

### Method 3: Plugin/Marketplace (Future)

**Install as Claude Code plugin**

```bash
# Future feature
claude plugin install meta-prompting-framework

# Or via marketplace
claude marketplace install meta-prompting-framework
```

---

## Configuration

### Global Settings

Add to `~/.claude/settings.json`:

```json
{
  "meta-prompting": {
    "default_framework": "natural_equivalence",
    "default_depth": 5,
    "theoretical_depth": "moderate",
    "auto_validate": true,
    "enable_research_integration": true
  },
  "agents": {
    "meta2": {
      "enabled": true,
      "research_tools": ["WebSearch", "Context7", "MARS"]
    },
    "MARS": {
      "enabled": true,
      "parallel_research": true
    }
  }
}
```

### Project Settings

Override in `project/.claude/settings.json`:

```json
{
  "meta-prompting": {
    "default_framework": "functors",  // Override for this project
    "default_depth": 7,                // More levels for complex project
    "theoretical_depth": "comprehensive"
  }
}
```

---

## Usage Examples

### Example 1: Generate Research Skill

```bash
# In Claude Code
/meta-command --type skill --discover "formal verification with F*"

# Uses:
# 1. deep-researcher to analyze F* domain
# 2. meta2 to generate 5-level framework
# 3. skill-builder to package as skill
# 4. /actualize to install

# Result: New skill in ~/.claude/skills/fstar-verification/
```

### Example 2: Quick Task Enhancement

```bash
# Use installed /meta-agent command
/meta-agent Design a distributed rate limiter with consistency guarantees

# Uses: Autonomous Routing meta-prompt
# Output: Enhanced design with reasoning
```

### Example 3: Custom Framework for Project

```bash
# Project-specific framework
cd my-project
workflow: meta-framework-generation
  domain_name: "GraphQL schema optimization"
  depth_levels: 5

# Installs to my-project/.claude/
# Only available in this project
```

### Example 4: Bootstrap New Capability

```bash
# Want: Skill for quantum algorithm design
# Don't have: Quantum expertise

# Step 1: Research (uses Context7 MCP)
/ctx7 "quantum computing basics"

# Step 2: Generate framework (meta2 researches automatically)
workflow: meta-framework-generation
  domain_name: "quantum algorithm design"
  depth_levels: 7

# Step 3: Create skill
/meta-command --type skill --create "quantum-algorithm-design"

# Step 4: Use immediately
Skill: quantum-algorithm-design
"Design a quantum algorithm for graph coloring"
```

---

## Advanced Patterns

### Pattern 1: Meta-Skill Generation

**Create skills that generate skills**

```yaml
# ~/.claude/workflows/meta-skill-generator.yaml
name: Meta-Skill Generator
description: Generate skills that generate skills

steps:
  - name: analyze_pattern
    agent: meta2
    prompt: |
      Analyze the pattern of skill generation for ${domain_category}.
      Create a meta-level framework that can generate skills for
      any specific domain in this category.

  - name: create_meta_skill
    agent: skill-builder
    prompt: |
      Create a meta-skill that uses the framework to generate
      specific skills on demand.
```

**Usage:**
```bash
workflow: meta-skill-generator
  domain_category: "web frameworks"

# Creates: web-framework-skill-generator
# Which can then generate: react-skill, vue-skill, angular-skill, etc.
```

---

### Pattern 2: Cross-Domain Translation

**Translate frameworks between domains**

```yaml
workflow: framework-translator
  source_framework: "fstar-verification"
  target_domain: "Coq theorem proving"

# Uses meta2 to:
# 1. Extract categorical structure from source
# 2. Map to target domain primitives
# 3. Generate equivalent framework
# 4. Validate with MARS
```

---

### Pattern 3: Workflow Library

**Build library of domain-specific workflows**

```
~/.claude/workflows/
├── meta-framework-generation.yaml      # Universal
├── quick-meta-prompt.yaml              # Universal
├── code-to-spec.yaml                   # Software
├── research-to-paper.yaml              # Academic
├── idea-to-prototype.yaml              # Innovation
└── problem-to-solution.yaml            # Engineering
```

Each uses meta-prompting agents under the hood!

---

## Best Practices

### 1. Start Global, Specialize Locally

```bash
# Install meta-prompting globally
~/.claude/agents/meta2/
~/.claude/skills/category-master/

# Create project-specific frameworks
my-project/.claude/skills/project-specific-optimization/
```

### 2. Use Symbolic Links for Development

```bash
# During development
ln -s ~/dev/meta-prompting-framework/agents/meta2 ~/.claude/agents/meta2

# Easy to update and test
git pull  # In framework repo
/actualize  # Changes immediately available
```

### 3. Version Your Frameworks

```bash
~/.claude/skills/
├── api-design-v1/
├── api-design-v2/      # Improved version
└── api-design/         # Symlink to latest
```

### 4. Document Integration

```markdown
# my-project/.claude/CLAUDE.md

## Project-Specific Resources

- **api-optimization** skill (5 levels, generated with meta2)
- **research-synthesis** workflow (uses MARS + mercurio-orchestrator)
- Custom meta-prompts in `prompts/`
```

---

## Troubleshooting

### Q: meta2 agent not found

**A:** Ensure installed and synced:
```bash
ls ~/.claude/agents/ | grep meta2
/actualize
```

### Q: Workflow fails to find meta-prompting resources

**A:** Check paths in workflow YAML:
```yaml
# Absolute path
agent: /Users/you/.claude/agents/meta2/agent.md

# Or relative to .claude/
agent: agents/meta2/agent.md
```

### Q: Generated skills not loading

**A:** Run validation:
```bash
/actualize --validate
# Checks all skills/agents/commands for errors
```

---

## Migration Guide

### From Standalone to Integrated

**Before:**
```bash
# Manual copy-paste from meta-prompts/v2/META_PROMPTS.md
```

**After:**
```bash
# Installed command
/meta-agent Design API

# Installed workflow
workflow: quick-meta-prompt
  task: "Design API"
```

---

## Future Enhancements

### Planned Features

1. **Auto-Installation**: `/install-meta-prompting` command
2. **Plugin System**: One-command install of entire framework
3. **Marketplace Integration**: Share generated frameworks
4. **Version Management**: Track framework versions
5. **Dependency Resolution**: Auto-install required agents/skills

---

## See Also

- [Quick Start](QUICK_START.md) - Get started with meta-prompting
- [Agents README](../agents/README.md) - Agent selection matrix
- [Commands README](../commands/README.md) - Command reference
- [Workflows README](../workflows/README.md) - Workflow patterns
- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code) - Official documentation

---

**Seamlessly integrate meta-prompting into your Claude Code workflow.** ✨
