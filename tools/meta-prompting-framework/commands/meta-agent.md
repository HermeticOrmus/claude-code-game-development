# /meta-agent

Analyze agent intent and generate specifications by learning from existing agent patterns. This command studies your current agents, extracts applicable patterns, and produces detailed specifications for the `/agent` command to implement.

## Usage

```bash
/meta-agent "<intent>" [options]
/meta-agent --analyze <agent-name>
/meta-agent --help
```

## Parameters

- `intent` (required): Natural language description of what the agent should do
- `--create` (optional): Automatically pipe specification to `/agent` for creation
- `--analyze` (optional): Analyze an existing agent to understand its patterns
- `--similar` (optional): Find similar agents without generating specification
- `--output` (optional): Save specification to file (default: display inline)

## Examples

### Basic Analysis and Specification

```bash
# Analyze intent and generate specification
/meta-agent "audit security vulnerabilities in AsciiDoc courseware"

# Output shows:
# - Similar agents found (pattern sources)
# - Extracted patterns and structures
# - Recommended agent type
# - Complete specification ready for /agent
```

### Create Agent Directly

```bash
# Analyze and create in one step
/meta-agent "analyze performance of lab implementations" --create

# This automatically:
# 1. Generates specification
# 2. Pipes to /agent command
# 3. Creates all files
```

### Learn from Existing Agents

```bash
# Analyze an existing agent to understand patterns
/meta-agent --analyze asciidoc-ai-writer

# Shows:
# - Agent structure breakdown
# - Instruction patterns
# - Integration patterns
# - Reusable components
```

### Find Similar Agents

```bash
# Find agents with similar purposes
/meta-agent "generate test data" --similar

# Returns:
# - synthetic-data-generator (exact match)
# - mcp-poc-wizard (similar generation pattern)
# - Similarity scores and pattern overlap
```

## What It Does

The command follows a pattern-learning approach, NOT hardcoded rules:

### 1. Intent Parsing

```yaml
Input: "audit security vulnerabilities in AsciiDoc courseware"

Parsed:
  primary_action: "audit"
  domain: "security"
  target: "AsciiDoc courseware"
  constraints: ["read-only", "evidence-based"]  # inferred
```

### 2. Pattern Discovery

Searches existing agents for similar patterns:

```yaml
Similar Agents Found:
  - task-memory-manager (similarity: 0.72)
    Reason: Both analyze content and generate reports
    Patterns: analysis workflow, structured output

  - asciidoc-ai-writer (similarity: 0.68)
    Reason: Both work with AsciiDoc domain
    Patterns: domain knowledge, formatting awareness

  - mcp-poc-wizard (similarity: 0.65)
    Reason: Both follow structured analysis workflows
    Patterns: step-by-step process, quality standards
```

### 3. Pattern Extraction

Extracts reusable structures from similar agents:

```yaml
Extracted Patterns:

  workflow_structure:
    source: mcp-poc-wizard
    pattern:
      - "Core Responsibilities"
      - "Implementation Approach" (numbered steps)
      - "Quality Standards"
      - "Output Format"

  domain_knowledge:
    source: asciidoc-ai-writer
    pattern:
      - Domain-specific guidelines
      - Formatting standards
      - Validation rules

  output_generation:
    source: task-memory-manager
    pattern:
      - Structured reporting
      - Documentation format
      - Command suggestions
```

### 4. Agent Type Determination

Decides whether to create Task-invoked agent or Command-driven tool:

```yaml
Decision Analysis:

  Task-Invoked Agent:
    indicators:
      - Workflow is self-contained
      - Process is multi-step
      - Minimal parameterization
    examples: asciidoc-ai-writer, mcp-poc-wizard
    score: 0.45

  Command-Driven Tool:
    indicators:
      - Frequent invocation needed
      - Requires parameters
      - Integrates with other commands
    examples: /write-lab, /test-lab, /revise-lab
    score: 0.78

  Recommended: Command-Driven (/audit)
  Rationale: High frequency use, parameterized, integrates with formatter
```

### 5. Specification Generation

Produces complete specification following learned patterns:

```yaml
# Generated: security-auditor.spec.yaml

agent:
  name: security-auditor
  type: command-driven
  model: sonnet
  color: red

intent:
  original: "audit security vulnerabilities in AsciiDoc courseware"
  parsed:
    action: audit
    domain: security
    target: asciidoc

capabilities:
  primary:
    - scan_files
    - identify_vulnerabilities
    - generate_reports

  domain_specific:
    - parse_asciidoc
    - recognize_code_blocks
    - validate_security_patterns

  integrations:
    - asciidoc-formatter (sequential: audit → fix)
    - task-memory-manager (reporting: audit → track)

commands:
  primary:
    name: /audit
    parameters:
      - file: required
      - severity: optional (critical|high|medium|low)
      - format: optional (detailed|summary)

  workflows:
    - name: /audit-and-fix
      pattern: audit → format → re-audit
      source: observed from /write-lab → /test-lab pattern

    - name: /audit-report
      pattern: audit → generate detailed report
      source: task-memory-manager output pattern

structure:
  follows: mcp-poc-wizard.md
  sections:
    - "Core Responsibilities"
    - "Analysis Workflow" (from write-lab "What It Does")
    - "Domain Knowledge" (from asciidoc-ai-writer)
    - "Output Format" (from task-memory-manager)
    - "Quality Standards" (from mcp-poc-wizard)
    - "Integration Points"

permissions:
  required:
    - Read(//Users/manu/ASCIIDocs/**)
    - Grep
    - Glob

  prohibited:
    - Write (read-only constraint)
    - Edit (non-destructive constraint)

documentation:
  style: /write-lab (extensive examples, detailed usage)
  sections:
    - Usage syntax
    - Parameters and options
    - What it does (automatic steps)
    - Pattern detection rules
    - Integration workflows
    - Examples (5+ concrete cases)
    - Error handling
```

## Pattern Learning Examples

### Example 1: Security Auditor

**Input:**
```bash
/meta-agent "audit security vulnerabilities in AsciiDoc"
```

**Analysis Process:**

1. **Intent Parsing:**
   ```
   Action: audit
   Domain: security
   Target: AsciiDoc
   ```

2. **Find Similar Agents:**
   ```
   ✓ task-memory-manager (analyzes content)
   ✓ asciidoc-ai-writer (AsciiDoc domain)
   ✓ Write-lab patterns (command structure)
   ```

3. **Extract Patterns:**
   ```
   Workflow: task-memory-manager → step-by-step analysis
   Domain: asciidoc-ai-writer → AsciiDoc knowledge
   Commands: /write-lab → documentation style
   ```

4. **Generate Specification:**
   ```yaml
   agent_type: command-driven
   primary_command: /audit
   structure: follows mcp-poc-wizard workflow pattern
   documentation: follows /write-lab comprehensive style
   ```

**Output:**
Complete specification ready for `/agent` command (shown above in section 5).

### Example 2: Performance Analyzer

**Input:**
```bash
/meta-agent "analyze performance of Python code in labs"
```

**Analysis Process:**

1. **Intent Parsing:**
   ```
   Action: analyze
   Domain: performance
   Target: Python code in labs
   ```

2. **Find Similar Agents:**
   ```
   ✓ /test-lab (tests lab implementations)
   ✓ mcp-poc-wizard (analyzes code quality)
   ✓ asciidoc-ai-writer (works with courseware)
   ```

3. **Pattern Decision:**
   ```
   Similar to: /test-lab (command-driven, testing focus)
   Agent type: command-driven tool
   Primary command: /analyze-performance
   ```

4. **Generated Specification:**
   ```yaml
   commands:
     - /analyze-performance <lab-file>
     - /profile-code <python-file>
     - /benchmark-lab <lab-file>

   workflow:
     - Parse Python code
     - Run performance profiling
     - Compare against benchmarks
     - Generate optimization report

   integrations:
     - /test-lab (run before performance analysis)
     - /revise-lab (apply optimization suggestions)
   ```

### Example 3: Accessibility Checker

**Input:**
```bash
/meta-agent "validate accessibility compliance in courseware"
```

**Analysis Process:**

1. **Similar Agents:**
   ```
   ✓ asciidoc-ai-writer (accessibility requirements section)
   ✓ task-memory-manager (validation and reporting)
   ✓ /write-lab (guideline compliance checking)
   ```

2. **Pattern Extraction:**
   ```
   Validation rules: from asciidoc-ai-writer
   Reporting format: from task-memory-manager
   Command structure: from /write-lab
   ```

3. **Generated Specification:**
   ```yaml
   agent_type: command-driven
   commands:
     - /check-a11y <file>
     - /validate-accessibility --all

   checks:
     - alt text on images (from asciidoc-ai-writer patterns)
     - descriptive link text
     - proper heading hierarchy
     - table accessibility
   ```

## Specification Output Format

The generated specification includes:

### Core Identity
```yaml
agent:
  name: string
  type: task-invoked | command-driven | hybrid
  model: sonnet | opus
  color: string
  description: string
```

### Capability Analysis
```yaml
capabilities:
  primary: [list of core capabilities]
  inferred: [capabilities discovered from intent]
  domain_specific: [specialized knowledge needed]
  integrations: [synergies with other agents]
```

### Command Structure (if command-driven)
```yaml
commands:
  primary:
    name: string
    parameters: [parameter definitions]
    examples: [usage examples]

  workflows:
    - name: string
      pattern: string
      source: string (which agent pattern inspired this)
```

### Pattern Sources
```yaml
patterns:
  structure:
    source: agent-name.md
    sections: [section names]

  workflow:
    source: agent-name.md
    pattern: description

  documentation:
    source: command-name.md
    style: description
```

### Implementation Guide
```yaml
implementation:
  files_to_create:
    - path: string
      content_template: string

  permissions_needed: [tool permissions]

  validation_checks: [what to validate]
```

## Integration with /agent Command

### Sequential Workflow

```bash
# Step 1: Generate specification
/meta-agent "audit security in AsciiDoc"

# Review the specification output
# (displayed in terminal)

# Step 2: Create agent from specification
/agent security-auditor --from-spec

# Or save specification first
/meta-agent "audit security" --output security-auditor.spec.yaml

# Review/edit the file
vim .claude/specs/security-auditor.spec.yaml

# Create agent from saved spec
/agent --from-file .claude/specs/security-auditor.spec.yaml
```

### Direct Creation

```bash
# One-step: analyze and create
/meta-agent "audit security in AsciiDoc" --create

# This internally:
# 1. Runs /meta-agent analysis
# 2. Generates specification
# 3. Pipes to /agent command
# 4. Creates all files
```

### Iterative Refinement

```bash
# Create initial agent
/meta-agent "audit security" --create

# Analyze what was created
/meta-agent --analyze security-auditor

# Learn from usage and propose improvements
# (after using the agent for a while)
/meta-agent --evolve security-auditor
```

## Pattern Discovery Options

### View Pattern Library

```bash
# See all discovered patterns
/meta-agent --list-patterns

# Output:
# Workflow Patterns:
#   - step-by-step-analysis (from mcp-poc-wizard)
#   - validation-reporting (from task-memory-manager)
#   - transformation-pipeline (from /write-lab)
#
# Documentation Patterns:
#   - comprehensive-examples (from /write-lab)
#   - structured-instructions (from asciidoc-ai-writer)
#
# Integration Patterns:
#   - sequential-workflow (audit → format → re-audit)
#   - parallel-invocation (multiple agents on same input)
```

### Similarity Search

```bash
# Find agents similar to a description
/meta-agent --find-similar "generate synthetic data for testing"

# Output:
# Most Similar Agents:
# 1. synthetic-data-generator (0.92 similarity)
#    - Purpose: generate test data
#    - Pattern: generation workflow
#    - Type: task-invoked
#
# 2. mcp-poc-wizard (0.68 similarity)
#    - Purpose: create code examples
#    - Pattern: code generation
#    - Type: task-invoked
```

## Learning from Your Agents

The meta-agent continuously learns:

### Training Data
```yaml
current_training_set:
  agents:
    count: 6
    sources:
      - asciidoc-ai-writer.md
      - synthetic-data-generator.md
      - mcp-poc-wizard.md
      - course-content-editor.md
      - asciidoc-image-curator.md
      - task-memory-manager.md

  commands:
    count: 7
    sources:
      - write-lab.md
      - test-lab.md
      - revise-lab.md
      - review.md
      - review-pr.md
      - help.md
      - write-lab-implementation.md

  patterns_extracted: 23
  integration_patterns: 8
```

### Pattern Evolution

As you create new agents, the pattern library grows:

```yaml
pattern_evolution:
  initial: 23 patterns (from existing agents)

  after_security_auditor_created:
    new_patterns:
      - validation-workflow
      - evidence-based-reporting
      - constraint-enforcement
    total: 26 patterns

  future_agents:
    can_use: all 26 patterns
    improved_quality: "Learn from security-auditor patterns"
```

## Advanced Usage

### Batch Analysis

```bash
# Analyze multiple intents
/meta-agent --batch intents.txt

# intents.txt contains:
# audit security vulnerabilities
# analyze performance metrics
# validate accessibility compliance
# generate API documentation

# Output: specifications for all four agents
```

### Pattern Export

```bash
# Export learned patterns for documentation
/meta-agent --export-patterns patterns.yaml

# Creates comprehensive pattern library
# Useful for understanding meta-agent's learning
```

### Compare Specifications

```bash
# Compare two agent specifications
/meta-agent --compare security-auditor performance-analyzer

# Shows:
# - Shared patterns
# - Differences in approach
# - Potential integration points
```

## Validation and Quality

The meta-agent validates specifications against:

### Structural Validation
- All required sections present
- Pattern sources are valid existing agents
- Commands follow naming conventions
- Permissions are correctly specified

### Consistency Validation
- Agent type matches capability patterns
- Documentation style matches agent type
- Integration points reference real agents
- Examples are concrete and complete

### Quality Validation
- Similar agents correctly identified
- Patterns appropriately applied
- No hardcoded assumptions
- Follows project guidelines (CLAUDE.md)

## Error Handling

### Common Issues

| Issue | Detection | Resolution |
|-------|-----------|------------|
| No similar agents | Similarity scores all < 0.4 | Uses generic patterns, suggests manual review |
| Ambiguous intent | Multiple high-scoring interpretations | Asks for clarification |
| Conflicting patterns | Different agents suggest opposite approaches | Presents options for user choice |
| Invalid agent name | Name conflicts with existing | Suggests alternative names |

### Example Error Output

```bash
/meta-agent "do something with files"

⚠️  Intent Too Vague
Your intent "do something with files" is too ambiguous.

Did you mean:
1. Read and analyze files (similar to task-memory-manager)
2. Transform file formats (similar to /write-lab)
3. Generate new files (similar to synthetic-data-generator)
4. Modify existing files (similar to asciidoc-ai-writer)

Please refine your intent or choose an option.
```

## Tips for Best Results

1. **Be Specific**: "audit security vulnerabilities in AsciiDoc" vs "check security"
2. **Include Domain**: Specify what you're working with (AsciiDoc, Python, labs)
3. **Mention Constraints**: read-only, non-destructive, etc.
4. **Review Similar Agents**: Use `--similar` first to see what exists
5. **Iterate**: Start with specification, review, then create

## Help Output

When you run `/meta-agent --help`, you'll see this condensed guide:

```
/meta-agent - Analyze intent and generate agent specifications from patterns

USAGE:
  /meta-agent "<intent>"                # Generate specification
  /meta-agent "<intent>" --create       # Generate and create agent
  /meta-agent --analyze <agent-name>    # Learn from existing agent
  /meta-agent --similar "<intent>"      # Find similar agents
  /meta-agent --help                    # Show this help

MODES:
  Generate Specification (default)
    Analyzes intent, finds similar agents, extracts patterns,
    and produces detailed specification for /agent command

  Auto-Create (--create)
    Generates specification AND creates agent in one step
    Equivalent to: /meta-agent + /agent --from-spec

  Analyze (--analyze)
    Studies existing agent to understand its patterns
    Learn reusable components and structures

  Find Similar (--similar)
    Discovers similar agents without generating spec
    Useful for exploration before creating

OPTIONS:
  --create            Automatically create agent after generating spec
  --analyze=<name>    Analyze existing agent patterns
  --similar           Find similar agents only (no spec generation)
  --output=<file>     Save specification to file

EXAMPLES:
  # Generate specification for review
  /meta-agent "audit security vulnerabilities in AsciiDoc"

  # Generate and create in one step
  /meta-agent "analyze performance of Python labs" --create

  # Learn from existing agent
  /meta-agent --analyze asciidoc-ai-writer

  # Find similar agents
  /meta-agent "generate test data" --similar

WORKFLOW:
  1. Describe intent: /meta-agent "<what you want>"
  2. Review specification output
  3. Create agent: /agent <agent-name> --from-spec
     OR use --create to skip step 3

WHAT IT DOES:
  • Parses your intent (action, domain, constraints)
  • Finds similar existing agents (pattern sources)
  • Extracts applicable patterns (structure, workflow, docs)
  • Determines agent type (task-invoked, command-driven, hybrid)
  • Generates complete specification for /agent

For full documentation, see: .claude/commands/meta-agent.md
```

## Related Commands

- `/agent` - Create agent from specification
- `/help` - List all available commands
- `/meta-agent --analyze` - Learn from existing agents

## Configuration

Default settings in `.claude/meta-agent-config.yaml`:

```yaml
similarity_threshold: 0.5
max_patterns_per_source: 5
default_agent_model: sonnet
specification_output: inline
auto_create: false
validation_strictness: medium
```

## Version History

- v1.0: Initial pattern-learning meta-agent
- v1.1: Added similarity search and pattern export
- v1.2: Enhanced specification format
- v1.3: Integration with /agent command

## Philosophy

This meta-agent doesn't hardcode rules like "if auditor then create /audit command."

Instead, it **learns** by studying your existing agents:
- How they structure their instructions
- How they define workflows
- How they integrate with each other
- What makes them effective

Then it **applies** those learned patterns to new agent creation, ensuring consistency while allowing for evolution.

Every agent created becomes training data for future agents, continuously improving the system.
