# SKILL: Assess Output Quality

## Purpose
Score LLM output quality (0.0-1.0) against task requirements to determine if iteration is needed or solution is complete.

## Description
Evaluates output against four criteria:
1. **Correctness**: Is the logic sound? Does it work?
2. **Completeness**: Are all requirements addressed?
3. **Clarity**: Is it well documented and readable?
4. **Quality**: Is it production-ready?

Returns structured assessment with score, strengths, gaps, and recommendation.

## Usage
```bash
/assess-quality --task "Create palindrome checker" --output output.md
/assess-quality --task "task" --output - # Read from stdin
/assess-quality --task "task" --threshold 0.85
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--task` | required | Original task description |
| `--output` | required | File path or `-` for stdin |
| `--threshold` | 0.90 | Quality bar for acceptance |
| `--verbose` | false | Show detailed reasoning |

## Output Format
```xml
<quality_assessment>
<score>0.87</score>
<verdict>GOOD - Threshold Met (0.85)</verdict>

<criteria>
  <criterion name="Correctness" score="0.90">
    Logic is sound, handles edge cases correctly.
    Algorithm terminates and returns expected values.
  </criterion>
  <criterion name="Completeness" score="0.85">
    All requirements addressed.
    Minor: could add more test cases.
  </criterion>
  <criterion name="Clarity" score="0.88">
    Well documented with docstring.
    Variable names are descriptive.
  </criterion>
  <criterion name="Quality" score="0.85">
    Production ready with error handling.
    Type hints included.
  </criterion>
</criteria>

<strengths>
  <strength>Comprehensive error handling</strength>
  <strength>Clear documentation with examples</strength>
  <strength>Edge cases covered (empty, single char)</strength>
  <strength>Type validation included</strength>
  <strength>Two implementation approaches provided</strength>
</strengths>

<gaps>
  <gap priority="low">Could add performance benchmarks</gap>
  <gap priority="low">Unicode handling not explicit</gap>
</gaps>

<recommendation>
ACCEPT - Output meets quality threshold (0.87 >= 0.85).
No further iteration needed unless performance optimization required.
</recommendation>
</quality_assessment>
```

## Scoring Rubric

| Score | Level | Description |
|-------|-------|-------------|
| **0.95-1.0** | EXCELLENT | Production-ready, comprehensive, exemplary |
| **0.85-0.94** | GOOD | Meets requirements, minor improvements possible |
| **0.70-0.84** | ACCEPTABLE | Works but needs refinement |
| **0.50-0.69** | NEEDS WORK | Significant gaps, iterate required |
| **< 0.50** | POOR | Major issues, likely needs restart |

## Verdicts

- **ACCEPT**: Quality >= threshold, no iteration needed
- **ITERATE**: Quality < threshold, improvement recommended
- **CLARIFY**: Task ambiguous, need more requirements
- **RESTART**: Fundamental issues, new approach needed

## How It Works

1. **Send to LLM** with assessment rubric
2. **Score each criterion** (0.0-1.0)
3. **Aggregate** weighted average
4. **Identify** strengths and gaps
5. **Compare** to threshold
6. **Return** verdict and reasoning

## Assessment Prompt
```markdown
Assess the quality of this output for the given task.

TASK:
{task}

OUTPUT:
{output}

Score each criterion 0.0-1.0:
1. Correctness: Is the logic sound?
2. Completeness: All requirements met?
3. Clarity: Well documented and readable?
4. Quality: Production ready?

Return overall score (0.0-1.0) and detailed reasoning.
```

## Examples

### Example 1: High Quality Output
```bash
$ /assess-quality --task "Implement binary search" --output binary_search.py
```
```xml
<quality_assessment>
<score>0.94</score>
<verdict>EXCELLENT - Exceeds threshold</verdict>

<criteria>
  <criterion name="Correctness" score="0.95">
    Algorithm correct, handles all cases including empty array.
  </criterion>
  <criterion name="Completeness" score="0.93">
    All requirements met, plus bonus insert-position function.
  </criterion>
  <criterion name="Clarity" score="0.95">
    Excellent docstring with examples, clear variable names.
  </criterion>
  <criterion name="Quality" score="0.92">
    Type hints, error handling, overflow-safe calculation.
  </criterion>
</criteria>

<strengths>
  <strength>Production-ready code</strength>
  <strength>Comprehensive documentation</strength>
  <strength>Edge case handling (empty, single, not found)</strength>
  <strength>Bonus utility function included</strength>
</strengths>

<gaps>
  <gap priority="very-low">Could add type stubs file</gap>
</gaps>

<recommendation>
ACCEPT - Excellent quality. Ready for production use.
</recommendation>
</quality_assessment>
```

### Example 2: Needs Iteration
```bash
$ /assess-quality --task "Create API rate limiter" --output rate_limiter_v1.py
```
```xml
<quality_assessment>
<score>0.68</score>
<verdict>NEEDS WORK - Below threshold (0.90)</verdict>

<criteria>
  <criterion name="Correctness" score="0.75">
    Basic logic works but race condition possible in distributed scenario.
  </criterion>
  <criterion name="Completeness" score="0.60">
    Missing: distributed sync, failure handling, monitoring.
  </criterion>
  <criterion name="Clarity" score="0.72">
    Documentation present but lacks architecture explanation.
  </criterion>
  <criterion name="Quality" score="0.65">
    Not production ready - needs error handling, tests.
  </criterion>
</criteria>

<strengths>
  <strength>Token bucket algorithm implemented</strength>
  <strength>Basic rate limiting works for single node</strength>
</strengths>

<gaps>
  <gap priority="high">No distributed consistency mechanism</gap>
  <gap priority="high">Missing failure mode handling</gap>
  <gap priority="medium">No monitoring/metrics</gap>
  <gap priority="medium">Missing test suite</gap>
</gaps>

<recommendation>
ITERATE - Significant gaps remain. Focus next iteration on:
1. Add Redis-based distributed locking
2. Implement circuit breaker for failures
3. Add monitoring hooks
</recommendation>
</quality_assessment>
```

### Example 3: Ambiguous Task
```bash
$ /assess-quality --task "Make it better" --output code.py
```
```xml
<quality_assessment>
<score>N/A</score>
<verdict>CLARIFY - Task requirements unclear</verdict>

<issues>
  <issue>Task "make it better" lacks specific requirements</issue>
  <issue>Cannot assess completeness without clear goals</issue>
  <issue>Quality criteria undefined</issue>
</issues>

<recommendation>
CLARIFY - Please specify:
- What aspects need improvement?
- What are the success criteria?
- What constraints apply?
</recommendation>
</quality_assessment>
```

## When to Use

**Use when:**
- After each iteration to decide if done
- Validating output before delivery
- Justifying why solution is complete
- Identifying specific improvement areas
- Comparing multiple solution versions

**Don't use when:**
- Output is trivially correct (obvious)
- Task is exploratory (no clear criteria)
- Just want quick feedback (ask directly)

## Integration

Chain with other skills:
```bash
# Iterate then assess
$ /meta-prompt-iterate "task" && /assess-quality --output .prompts/*/FINAL.md

# Assess multiple iterations
$ for f in .prompts/*/output.md; do /assess-quality --output "$f"; done

# Use in decision loop
quality=$(/assess-quality --output output.md | grep score | cut -d'>' -f2 | cut -d'<' -f1)
if [ $(echo "$quality < 0.90" | bc) -eq 1 ]; then
  /meta-prompt-iterate "task" --context output.md
fi

# Compare versions
$ /assess-quality --output v1.py > v1-quality.xml
$ /assess-quality --output v2.py > v2-quality.xml
$ diff v1-quality.xml v2-quality.xml
```

## Threshold Guidelines

| Task Type | Suggested Threshold |
|-----------|-------------------|
| Simple utilities | 0.85 |
| Production code | 0.90 |
| Critical systems | 0.95 |
| Documentation | 0.85 |
| Architecture designs | 0.90 |

## Implementation

Uses quality assessment from the meta-prompting engine:
```python
from meta_prompting_engine.llm_clients.claude import ClaudeClient

llm = ClaudeClient(api_key="...")

# Assessment prompt
assessment_prompt = f"""
Assess the quality of this output for the task.

TASK: {task}
OUTPUT: {output}

Return a score 0.0-1.0 based on:
- Correctness (logic sound?)
- Completeness (requirements met?)
- Clarity (documented?)
- Quality (production ready?)
"""

response = llm.complete([
    {"role": "user", "content": assessment_prompt}
], max_tokens=10)

score = float(response.content)
print(f"Quality: {score}")
```

## Source
- Engine: `/meta_prompting_engine/core.py` (quality assessment logic)
- Client: `/meta_prompting_engine/llm_clients/claude.py`
- Tests: `/tests/test_core_engine.py`
- Real results: `/test_real_api.py` output
