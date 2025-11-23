# SKILL: Meta-Prompt Iterate

## Purpose
Recursively improve LLM outputs through quality-driven iteration with automatic complexity routing, context extraction, and quality assessment.

## Description
The complete meta-prompting workflow:
1. **Analyze** task complexity (auto-routes to optimal strategy)
2. **Generate** initial solution with complexity-appropriate prompt
3. **Extract** context from output (patterns, constraints, successes)
4. **Assess** quality (0.0-1.0 score)
5. **Iterate** if quality < threshold (feeds context into next prompt)
6. **Return** best result with full metadata

## Usage
```bash
/meta-prompt-iterate "Write function to validate email addresses"
/meta-prompt-iterate "task" --max-iterations 5 --threshold 0.95
/meta-prompt-iterate "task" --skill python-programmer
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max-iterations` | 3 | Maximum improvement cycles |
| `--threshold` | 0.90 | Stop when quality reaches this |
| `--skill` | auto | Role/persona (python-programmer, architect, etc.) |
| `--verbose` | true | Show iteration progress |
| `--save-intermediates` | true | Save all iteration outputs |

## Output Structure

```
.prompts/
  001-validate-emails-initial/
    prompt.md          # Meta-prompt used
    output.md          # LLM response
    context.xml        # Extracted learnings
    quality.json       # Score + reasoning
  002-validate-emails-refined/
    prompt.md          # Improved with context
    output.md          # Enhanced response
    context.xml
    quality.json
  FINAL.md             # Best iteration with metadata
```

## Final Output Format

```markdown
# Result: Validate Email Addresses

## Metadata
<result>
<iterations>2</iterations>
<final_quality>0.91</final_quality>
<improvement>+0.18 from iteration 1</improvement>
<complexity score="0.45" level="MEDIUM"/>
<strategy>multi_approach_synthesis</strategy>
<tokens>2847</tokens>
<time>12.3s</time>
<stopped_reason>Quality threshold 0.90 reached</stopped_reason>
</result>

## Solution

[Final code/output from best iteration]

## Quality Assessment

<quality_assessment score="0.91">
<strengths>
  - Comprehensive regex pattern
  - Handles edge cases (plus addressing, subdomains)
  - Clear error messages
  - Well documented
</strengths>
<minor_gaps>
  - Could add internationalized domain support
</minor_gaps>
</quality_assessment>

## Context Extracted

<context>
<patterns>Regex validation, domain verification</patterns>
<constraints>RFC 5322 compliance required</constraints>
</context>
```

## Process Flow

```
           Task Input
               │
               ▼
    ┌──────────────────┐
    │ ANALYZE          │
    │ Complexity: 0.45 │
    │ Strategy: multi  │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │ ITERATION 1      │
    │ Generate prompt  │──► LLM Call
    │ Get output       │◄── Response
    │ Extract context  │──► Patterns found
    │ Assess quality   │──► Score: 0.73
    └────────┬─────────┘
             │ (quality < 0.90)
    ┌────────▼─────────┐
    │ ITERATION 2      │
    │ Enhanced prompt  │──► Context included
    │ + prior patterns │
    │ + improvements   │
    │ Get output       │◄── Better response
    │ Extract context  │──► More patterns
    │ Assess quality   │──► Score: 0.91
    └────────┬─────────┘
             │ (quality >= 0.90)
    ┌────────▼─────────┐
    │ RETURN BEST      │
    │ Output + metadata│
    │ All iterations   │
    │ saved to .prompts│
    └──────────────────┘
```

## Examples

### Example 1: Simple Task (Auto-Optimized)
```bash
$ /meta-prompt-iterate "Write function to check if number is prime"
```
```
Analyzing complexity: 0.15 (SIMPLE)
Strategy: direct_execution

Iteration 1/3:
  Generating solution...
  Quality assessment: 0.88
  Threshold met (0.85 for simple) - stopping early

Result saved to: .prompts/001-prime-check/FINAL.md
Total: 1 iteration, 847 tokens, 3.2s
```

### Example 2: Medium Task
```bash
$ /meta-prompt-iterate "Create a priority queue class with efficient insert/extract-min"
```
```
Analyzing complexity: 0.52 (MEDIUM)
Strategy: multi_approach_synthesis

Iteration 1/3:
  Generating with "compare multiple approaches" prompt...
  Extracted patterns: binary heap, list-based, tree-based
  Quality assessment: 0.76
  Continuing to iteration 2...

Iteration 2/3:
  Enhanced prompt with prior patterns...
  Focus on: heap implementation (best tradeoff)
  Quality assessment: 0.92
  Threshold met (0.90) - complete

Result saved to: .prompts/002-priority-queue/FINAL.md
Total: 2 iterations, 2,403 tokens, 9.5s
Improvement: +0.16 (+21%)
```

### Example 3: Complex Task
```bash
$ /meta-prompt-iterate "Design API rate limiter for 100k req/s with distributed consistency"
```
```
Analyzing complexity: 0.78 (COMPLEX)
Strategy: autonomous_evolution

Iteration 1/3:
  Generating 3+ architectural hypotheses...
  Approaches: token bucket, leaky bucket, sliding window
  Quality assessment: 0.68
  Extracted: Redis atomic ops, TTL patterns, sharding

Iteration 2/3:
  Enhanced with distributed consensus patterns...
  Added: multi-node sync, failure modes
  Quality assessment: 0.82
  Extracted: circuit breaker, fallback strategies

Iteration 3/3:
  Final refinement with monitoring...
  Added: metrics, alerting, degradation modes
  Quality assessment: 0.94
  Threshold met (0.90) - complete

Result saved to: .prompts/003-rate-limiter/FINAL.md
Total: 3 iterations, 4,203 tokens, 18.3s
Improvement: +0.26 (+38%)
```

## Meta-Prompt Templates by Complexity

### Simple (< 0.3)
```markdown
You are {skill}.

Task: {task}

Execute with clear, step-by-step reasoning:
1. Understand the requirements
2. Implement the solution
3. Verify correctness

Provide complete, working code.
```

### Medium (0.3 - 0.7)
```markdown
You are {skill} using meta-cognitive strategies.

Task: {task}

Approach:
1. Generate 2-3 different approaches
2. Evaluate strengths and weaknesses of each
3. Choose the optimal approach with justification
4. Implement the chosen solution
5. Include edge case handling and tests

{previous_context}
```

### Complex (> 0.7)
```markdown
You are {skill} performing autonomous problem evolution.

Task: {task}

Strategy:
1. Generate 3+ architectural hypotheses
2. For each hypothesis, identify:
   - Strengths and use cases
   - Weaknesses and failure modes
   - Key tradeoffs
3. Test hypotheses against constraints
4. Synthesize optimal solution from best elements
5. Document decision rationale

{previous_context}

Previous iteration learnings:
{extracted_patterns}
{improvements_needed}
```

## When to Use

**Use when:**
- Task requires multiple refinements
- Quality is critical (production code)
- Want systematic, measurable improvement
- First attempt was insufficient
- Building something complex

**Don't use when:**
- Simple one-off tasks (just ask directly)
- Exploratory brainstorming
- Time-critical (adds latency)
- Task is ambiguous (clarify first)

## Configuration

Default settings (in `~/.claude/meta-prompting.yaml`):
```yaml
meta_prompt_iterate:
  max_iterations: 3
  quality_threshold: 0.90
  auto_stop: true
  save_intermediates: true
  complexity_thresholds:
    simple: 0.3
    medium: 0.7
  quality_thresholds_by_complexity:
    simple: 0.85
    medium: 0.90
    complex: 0.90
```

## Integration

Chain with other skills:
```bash
# Analyze first, then iterate
$ /analyze-complexity "task" && /meta-prompt-iterate "task"

# Iterate then verify
$ /meta-prompt-iterate "task" && /assess-quality --output .prompts/*/FINAL.md

# Extract context manually
$ /extract-context .prompts/001-*/output.md

# Custom thresholds
$ /meta-prompt-iterate "task" --max-iterations 5 --threshold 0.95
```

## Real Test Results

From actual Claude API testing:

**Test 1: Palindrome Checker**
- Iterations: 2
- Tokens: 4,316
- Time: 92.2s
- Quality: 0.72 -> 0.87 (+21%)
- Output: Two implementations + full test suite

**Test 2: Find Maximum**
- Iterations: 2
- Tokens: 3,998
- Time: 89.7s
- Quality: 0.65 -> 0.78 (+20%)
- Output: Strict + safe implementations with error handling

## Implementation

Uses `MetaPromptingEngine` from the meta-prompting engine:
```python
from meta_prompting_engine.llm_clients.claude import ClaudeClient
from meta_prompting_engine.core import MetaPromptingEngine

llm = ClaudeClient(api_key="...")
engine = MetaPromptingEngine(llm)

result = engine.execute_with_meta_prompting(
    skill="python-programmer",
    task="Create a function to validate email addresses",
    max_iterations=3,
    quality_threshold=0.90
)

print(f"Quality: {result.quality_score}")
print(f"Iterations: {result.iterations}")
print(f"Improvement: {result.improvement_delta:+.2f}")
print(result.output)
```

## Source
- Engine: `/meta_prompting_engine/core.py`
- Complexity: `/meta_prompting_engine/complexity.py`
- Extraction: `/meta_prompting_engine/extraction.py`
- Claude client: `/meta_prompting_engine/llm_clients/claude.py`
- Tests: `/tests/test_core_engine.py`
- Real API test: `/test_real_api.py`
