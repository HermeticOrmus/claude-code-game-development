# Meta-Prompting Skills for Claude Code CLI

**Learned from building real meta-prompting engine → Packaged as reusable skills**

---

## Key Learnings from Our Build

### What We Built
1. **ComplexityAnalyzer** - Routes tasks to optimal strategies (simple/medium/complex)
2. **ContextExtractor** - Extracts patterns, constraints, success indicators
3. **MetaPromptingEngine** - Recursive improvement loop with quality assessment
4. **Real validation** - Tested with actual Claude API (3,998 tokens, 89.7s)

### What Works at Scale
✅ **Modular components** - Each piece (complexity, extraction, assessment) independent
✅ **Clear strategies** - Three complexity levels with distinct approaches
✅ **Context accumulation** - Each iteration improves on previous
✅ **Quality-driven** - Stop when threshold met (not fixed iterations)
✅ **Transparent** - Track all API calls, show reasoning

### What Makes Skills Scalable
From the example repo + our experience:
1. **Single clear purpose** per skill
2. **Automatic detection** of context/dependencies
3. **Structured outputs** (XML metadata for chaining)
4. **Numbered iterations** (001-, 002-) for provenance
5. **Task-agnostic** prompts that work across domains

---

## Proposed Skill Structure

### Skill 1: `/analyze-complexity`
**Purpose**: Determine optimal meta-prompting strategy for any task

```markdown
# SKILL: Analyze Task Complexity

## Description
Analyzes task complexity (0.0-1.0) and recommends meta-prompting strategy.

## Usage
/analyze-complexity "Create a distributed rate-limiting system"

## Output
<complexity score="0.78" level="COMPLEX">
<factors>
  <word_count>0.15</word_count>
  <ambiguity>0.08</ambiguity>
  <dependencies>0.18</dependencies>
  <domain_specificity>0.37</domain_specificity>
</factors>
<strategy>autonomous_evolution</strategy>
<reasoning>
  Technical domain (distributed systems, rate-limiting) detected.
  Multiple dependencies (scalability, consistency, fault-tolerance).
  Requires deep expertise and iterative refinement.
</reasoning>
<recommended_approach>
  1. Generate 3+ architectural hypotheses
  2. Evaluate tradeoffs (CAP theorem, consistency models)
  3. Test against constraints (100k req/s target)
  4. Iteratively refine based on bottlenecks
</recommended_approach>
</complexity>

## How It Works
1. Counts words, ambiguous terms, dependencies
2. Detects technical domain keywords
3. Scores 0.0-1.0 across 4 factors
4. Routes to strategy: direct (<0.3), synthesis (0.3-0.7), evolution (>0.7)

## When to Use
- Before starting any complex task
- To decide how many iterations needed
- To choose between quick execution vs thorough exploration
```

**Implementation**: Uses `ComplexityAnalyzer` from our engine

---

### Skill 2: `/extract-context`
**Purpose**: Extract learnings from previous outputs to improve next iteration

```markdown
# SKILL: Extract Context from Output

## Description
Analyzes output to extract patterns, constraints, and success indicators.
Use these to generate improved prompts for next iteration.

## Usage
/extract-context <file or paste output>

## Output
<context>
<domain_primitives>
  <objects>list, array, index, comparison</objects>
  <operations>search, divide, compare, return</operations>
  <relationships>binary division, pointer adjustment</relationships>
</domain_primitives>

<patterns>
  <pattern>Two-pointer technique for O(log n)</pattern>
  <pattern>Guard clause pattern for validation</pattern>
  <pattern>Overflow-safe mid calculation</pattern>
</patterns>

<constraints>
  <hard_requirement>Array must be sorted</hard_requirement>
  <hard_requirement>Handle empty array case</hard_requirement>
  <soft_preference>Use type hints</soft_preference>
  <anti_pattern>Linear search (defeats purpose)</anti_pattern>
</constraints>

<success_indicators>
  <indicator>O(log n) time complexity achieved</indicator>
  <indicator>Edge cases handled</indicator>
  <indicator>Comprehensive docstring</indicator>
</success_indicators>

<improvements_needed>
  <improvement>Add input validation</improvement>
  <improvement>Handle duplicate values</improvement>
  <improvement>Include usage examples</improvement>
</improvements_needed>
</context>

## How It Works
1. Sends output to LLM with extraction prompt
2. Parses JSON response (with fallback heuristics)
3. Returns structured context
4. Auto-detects what worked vs needs improvement

## When to Use
- After completing first draft
- To prepare improved prompt for iteration 2
- To identify gaps before final review
```

**Implementation**: Uses `ContextExtractor` with 7-phase framework

---

### Skill 3: `/meta-prompt-iterate`
**Purpose**: Complete recursive meta-prompting workflow

```markdown
# SKILL: Meta-Prompt Iteration Workflow

## Description
Full meta-prompting: analyze complexity → generate → extract → assess → iterate.
Automatically improves output quality through recursive refinement.

## Usage
/meta-prompt-iterate "Write function to validate email addresses"

## Process
1. **Analyze** complexity (auto-detects from task)
2. **Generate** initial solution with complexity-appropriate strategy
3. **Extract** context from output (patterns, constraints, successes)
4. **Assess** quality (0.0-1.0 score)
5. **Iterate** if quality < threshold (feeds context into next prompt)
6. **Return** best result with metadata

## Output Structure
.prompts/
  001-validate-emails-initial/
    prompt.md          # Generated meta-prompt
    output.md          # LLM response
    context.xml        # Extracted learnings
    quality.json       # Score + reasoning
  002-validate-emails-refined/
    prompt.md          # Improved with context
    output.md          # Enhanced response
    context.xml
    quality.json
  FINAL.md            # Best iteration with metadata

## Metadata
<iteration number="2" of="2">
<quality_score>0.91</quality_score>
<improvement>+0.18 from iteration 1</improvement>
<strategy>multi_approach_synthesis</strategy>
<tokens_used>2847</tokens_used>
<why_stopped>Quality threshold 0.90 reached</why_stopped>
</iteration>

## Configuration
Max iterations: 3 (configurable)
Quality threshold: 0.90 (configurable)
Auto-stop: Yes (when threshold met)

## When to Use
- Complex tasks requiring multiple refinements
- When first attempt needs improvement
- To systematically enhance output quality
- For production-ready code/designs
```

**Implementation**: Full `MetaPromptingEngine` workflow

---

### Skill 4: `/assess-quality`
**Purpose**: Evaluate output quality to decide if iteration needed

```markdown
# SKILL: Assess Output Quality

## Description
Scores output quality (0.0-1.0) against task requirements.
Determines if further iteration needed or if solution is complete.

## Usage
/assess-quality --task "Create palindrome checker" --output <file>

## Output
<quality_assessment>
<score>0.87</score>
<verdict>GOOD - Threshold Met (0.85)</verdict>

<strengths>
  <strength>Comprehensive error handling</strength>
  <strength>Clear documentation</strength>
  <strength>Edge cases covered</strength>
  <strength>Type validation included</strength>
</strengths>

<gaps>
  <gap priority="low">Could add more test cases</gap>
  <gap priority="low">Performance optimization possible</gap>
</gaps>

<criteria_met>
  <criterion name="Correctness">YES - Logic is sound</criterion>
  <criterion name="Completeness">YES - All requirements addressed</criterion>
  <criterion name="Clarity">YES - Well documented</criterion>
  <criterion name="Quality">YES - Production ready</criterion>
</criteria_met>

<recommendation>
ACCEPT - Output meets quality threshold.
No further iteration needed unless performance optimization required.
</recommendation>
</quality_assessment>

## How It Works
1. Sends task + output to LLM with assessment rubric
2. Scores against 4 criteria (correctness, completeness, clarity, quality)
3. Returns 0.0-1.0 score with reasoning
4. Recommends: accept, iterate, or clarify

## When to Use
- After each iteration to decide if done
- To validate output before delivery
- To justify why solution is complete
- To identify specific improvement areas
```

**Implementation**: Uses quality assessment from engine

---

## How Skills Chain Together

### Example: Complex Task Workflow

```bash
# 1. Analyze complexity
$ /analyze-complexity "Design distributed cache with consistency guarantees"
> Complexity: 0.82 (COMPLEX) → Strategy: autonomous_evolution

# 2. Generate with appropriate strategy
$ /meta-prompt-iterate "Design distributed cache..." --max-iterations 3
> Iteration 1: Basic design (quality: 0.68)
> Iteration 2: Refined with CAP analysis (quality: 0.81)
> Iteration 3: Added monitoring, failure modes (quality: 0.94)
> DONE - Threshold 0.90 met

# 3. Verify quality
$ /assess-quality --task "..." --output .prompts/003-*/FINAL.md
> Score: 0.94 - EXCELLENT
> All criteria met. Production ready.
```

### Example: Simple Task (Auto-optimized)

```bash
$ /meta-prompt-iterate "Write factorial function"
> Analyzing complexity: 0.12 (SIMPLE) → direct_execution
> Iteration 1: Complete solution (quality: 0.88)
> DONE - Auto-stopped (quality sufficient for simple task)
```

---

## Integration with Luxor Marketplace

### Plugin Structure
```
luxor-meta-prompting/
├── plugin.json
├── README.md
├── skills/
│   ├── analyze-complexity/
│   │   ├── SKILL.md
│   │   └── examples/
│   ├── extract-context/
│   │   ├── SKILL.md
│   │   └── examples/
│   ├── meta-prompt-iterate/
│   │   ├── SKILL.md
│   │   └── examples/
│   └── assess-quality/
│       ├── SKILL.md
│       └── examples/
├── commands/
│   ├── quick-improve.md      # One-shot improvement
│   └── multi-stage.md         # Research → Plan → Implement
└── workflows/
    ├── production-ready.yaml  # Full quality pipeline
    └── rapid-iteration.yaml   # Fast feedback loop
```

### plugin.json
```json
{
  "name": "luxor-meta-prompting",
  "version": "1.0.0",
  "description": "Recursive prompt improvement with quality-driven iteration",
  "skills": [
    {
      "name": "analyze-complexity",
      "description": "Determine optimal meta-prompting strategy",
      "category": "analysis"
    },
    {
      "name": "extract-context",
      "description": "Extract learnings from outputs",
      "category": "analysis"
    },
    {
      "name": "meta-prompt-iterate",
      "description": "Full recursive meta-prompting workflow",
      "category": "generation"
    },
    {
      "name": "assess-quality",
      "description": "Score output quality (0.0-1.0)",
      "category": "validation"
    }
  ],
  "commands": [
    {
      "name": "quick-improve",
      "description": "One-shot prompt improvement"
    },
    {
      "name": "multi-stage",
      "description": "Research → Plan → Implement workflow"
    }
  ],
  "workflows": [
    {
      "name": "production-ready",
      "description": "Full quality pipeline (3 iterations max)"
    },
    {
      "name": "rapid-iteration",
      "description": "Fast feedback (1-2 iterations)"
    }
  ]
}
```

---

## Key Patterns for Scale

### 1. **Structured Metadata** (Like Example Repo)
```xml
<meta_prompt iteration="2">
<dependencies>
  <file>.prompts/001-auth-research/output.md</file>
  <context>Previous iteration identified JWT + bcrypt</context>
</dependencies>
<confidence>0.85</confidence>
<open_questions>
  <question>Should we use refresh tokens?</question>
  <question>Session storage: Redis or in-memory?</question>
</open_questions>
<assumptions>
  <assumption>Using Express.js framework</assumption>
  <assumption>PostgreSQL for user storage</assumption>
</assumptions>
</meta_prompt>
```

**Why**: Machine-readable, chainable, auditable

### 2. **Automatic File Detection**
```python
# In skill implementation
def find_prior_outputs(task_keyword):
    """Scan .prompts/ for related outputs"""
    pattern = f".prompts/*{task_keyword}*/"
    return sorted(glob(pattern))

def suggest_dependencies(task):
    """Auto-link research → plan → implementation"""
    research_files = find_prior_outputs(f"{task}-research")
    plan_files = find_prior_outputs(f"{task}-plan")
    return {"research": research_files, "plans": plan_files}
```

**Why**: User doesn't manually reference files

### 3. **Numbered Provenance**
```
.prompts/
  001-auth-research/
  002-auth-plan/
  003-auth-implement/
  004-auth-implement-v2/  # Iteration 2
  005-auth-implement-v3/  # Iteration 3
```

**Why**: Clear history, easy rollback, audit trail

### 4. **Quality-Driven Stopping**
```python
# Don't iterate blindly
while quality < threshold and iterations < max_iterations:
    output = generate_with_context(task, context)
    quality = assess_quality(output)
    if quality >= threshold:
        break  # Done!
    context = extract_context(output)
```

**Why**: Stop when good enough (save time/tokens)

### 5. **Complexity-Aware Routing**
```python
def get_strategy(complexity_score):
    if complexity_score < 0.3:
        return "direct_execution"  # Simple: 1 iteration max
    elif complexity_score < 0.7:
        return "multi_approach"    # Medium: 2-3 iterations
    else:
        return "autonomous_evolution"  # Complex: 3-5 iterations
```

**Why**: Right tool for the job, optimized resource usage

---

## Comparison: Example Repo vs Our Approach

| Aspect | Example Repo | Our Meta-Prompting |
|--------|-------------|-------------------|
| **Workflow** | Research → Plan → Implement | Analyze → Generate → Extract → Assess → Iterate |
| **Stages** | 3 fixed stages | Dynamic (quality-driven) |
| **Complexity** | User decides | Auto-detected |
| **Context** | Manual file reference | Auto-extracted patterns |
| **Quality** | Implicit | Explicit scoring (0.0-1.0) |
| **Stopping** | Manual | Automatic (threshold) |
| **Output** | Numbered folders | Numbered + metadata |

**Synergy**: Combine both!
- Use their **structure** (numbered folders, metadata)
- Add our **intelligence** (complexity routing, quality scoring, auto-iteration)

---

## Example Skill: `/meta-prompt-iterate` (Full Implementation)

```markdown
# SKILL: Meta-Prompt Iterate

## Purpose
Recursively improve prompts and outputs through quality-driven iteration.

## Usage
```bash
/meta-prompt-iterate [task description] [--max-iterations N] [--threshold X.XX]
```

## Examples

### Example 1: Simple Task
```bash
$ /meta-prompt-iterate "Write function to check if number is prime"
```

**Output**:
```
Analyzing complexity: 0.15 (SIMPLE)
Strategy: direct_execution

Iteration 1/3:
✓ Generated solution (quality: 0.87)
✓ Threshold met (0.85) - stopping early

Result saved to: .prompts/001-prime-check/FINAL.md
Total: 1 iteration, 847 tokens, 3.2s
```

### Example 2: Complex Task
```bash
$ /meta-prompt-iterate "Design API rate limiter for 100k req/s"
```

**Output**:
```
Analyzing complexity: 0.78 (COMPLEX)
Strategy: autonomous_evolution

Iteration 1/3:
✓ Generated 3 architectural approaches (quality: 0.68)
✓ Extracted patterns: token bucket, leaky bucket, fixed window

Iteration 2/3:
✓ Enhanced with distributed consensus (quality: 0.82)
✓ Extracted: Redis atomic operations, TTL, multi-tenant

Iteration 3/3:
✓ Added monitoring, failure modes (quality: 0.94)
✓ Threshold met (0.90) - complete

Result saved to: .prompts/003-rate-limiter/FINAL.md
Total: 3 iterations, 4,203 tokens, 18.3s
```

## Output Structure

Each iteration creates:
```
.prompts/NNN-{task-slug}/
  prompt.md          # Meta-prompt used
  output.md          # LLM response
  context.xml        # Extracted patterns/constraints
  quality.json       # Assessment scores
```

Final result:
```
.prompts/NNN-{task-slug}/FINAL.md
```

With metadata:
```xml
<result>
<iterations>3</iterations>
<final_quality>0.94</final_quality>
<improvement>+0.26 from iteration 1</improvement>
<strategy>autonomous_evolution</strategy>
<tokens>4203</tokens>
<time>18.3s</time>
<stopped_reason>Quality threshold 0.90 reached</stopped_reason>
</result>
```

## Configuration

Default settings:
- `max_iterations`: 3
- `quality_threshold`: 0.90
- `auto_stop`: true
- `save_intermediates`: true

Override:
```bash
$ /meta-prompt-iterate "task" --max-iterations 5 --threshold 0.95
```

## When to Use

✅ **Use when**:
- Task requires multiple refinements
- Quality is critical (production code)
- You want systematic improvement
- First attempt was insufficient

❌ **Don't use when**:
- Simple one-off tasks (use direct prompt)
- Exploratory/brainstorming (use /research)
- Time-critical (adds 2-3x latency)

## Behind the Scenes

1. **Complexity Analysis** (ComplexityAnalyzer)
   - Scores 0.0-1.0 based on word count, ambiguity, dependencies, domain
   - Routes to optimal strategy

2. **Meta-Prompt Generation** (MetaPromptingEngine)
   - Simple (<0.3): "Execute with clear reasoning"
   - Medium (0.3-0.7): "Generate 2-3 approaches, evaluate, choose best"
   - Complex (>0.7): "Generate hypotheses, test, refine iteratively"

3. **Context Extraction** (ContextExtractor)
   - Sends output to LLM with extraction prompt
   - Parses: patterns, constraints, success indicators, gaps
   - Feeds into next iteration

4. **Quality Assessment** (QualityAssessor)
   - Scores against: correctness, completeness, clarity, quality
   - Returns 0.0-1.0 with reasoning
   - Decides: continue or stop

5. **Iteration Control**
   - Stops when quality >= threshold
   - Or when max_iterations reached
   - Returns best result from all iterations

## Integration

Works with other skills:
```bash
# Chain with assessment
$ /meta-prompt-iterate "task" && /assess-quality --output .prompts/*/FINAL.md

# Extract context manually
$ /extract-context .prompts/001-*/output.md

# Check complexity first
$ /analyze-complexity "task" && /meta-prompt-iterate "task"
```

## Real Example Output

See: `/examples/palindrome-checker/` for full trace with:
- 2 iterations
- 4,316 tokens
- 92.2 seconds
- Quality improvement: 0.72 → 0.87
- Production-ready code with tests

## Source

Implemented using: `/meta_prompting_engine/`
- `core.py`: MetaPromptingEngine
- `complexity.py`: ComplexityAnalyzer
- `extraction.py`: ContextExtractor
- `llm_clients/claude.py`: Claude Sonnet 4.5
```

---

## Next Steps: Creating the Skills

### 1. Extract Core Algorithms
```bash
# From our engine to skill implementations
cp meta_prompting_engine/complexity.py skills/analyze-complexity/analyzer.py
cp meta_prompting_engine/extraction.py skills/extract-context/extractor.py
cp meta_prompting_engine/core.py skills/meta-prompt-iterate/engine.py
```

### 2. Create SKILL.md Files
Use template from example repo, add our enhancements

### 3. Add Examples
Real examples from our tests (palindrome, max number, etc.)

### 4. Package for Luxor
Follow their plugin structure, test with marketplace

### 5. Document Patterns
Create guides showing:
- When to use each skill
- How to chain them
- Integration with existing workflows

---

## Summary: What Makes This Scalable

1. **Modular** - Each skill does one thing well
2. **Chainable** - Skills work together via structured metadata
3. **Automatic** - Detects complexity, finds dependencies, stops when done
4. **Quality-driven** - Not fixed iterations, stops when good enough
5. **Transparent** - Shows reasoning, tracks provenance
6. **Task-agnostic** - Works for code, design, research, planning
7. **Production-tested** - Validated with real Claude API (3,998 tokens, 89.7s)

**The key insight**: Don't make users think about meta-prompting mechanics. Give them simple commands (`/meta-prompt-iterate "task"`) that handle complexity routing, context extraction, and quality assessment automatically.

Like the example repo's simplicity, but with the intelligence of our engine underneath.
