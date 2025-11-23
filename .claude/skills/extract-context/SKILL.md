# SKILL: Extract Context from Output

## Purpose
Analyze LLM outputs to extract patterns, constraints, and success indicators that can improve subsequent iterations.

## Description
Uses a 7-phase extraction framework to pull structured context from any LLM output:
1. **Domain primitives**: Objects, operations, relationships
2. **Patterns**: Identified techniques and approaches
3. **Constraints**: Hard requirements, preferences, anti-patterns
4. **Complexity factors**: What makes this task challenging
5. **Success indicators**: What's working well
6. **Error patterns**: Potential failure modes
7. **Improvements needed**: Gaps to address in next iteration

## Usage
```bash
/extract-context <output-file>
# or
/extract-context --paste  # Then paste output
```

## Output Format
```xml
<context iteration="1" task="implement binary search">
<domain_primitives>
  <objects>array, index, target, midpoint, bounds</objects>
  <operations>search, compare, divide, return</operations>
  <relationships>binary division, pointer adjustment, convergence</relationships>
</domain_primitives>

<patterns>
  <pattern confidence="0.95">Two-pointer technique for O(log n)</pattern>
  <pattern confidence="0.90">Guard clause pattern for edge cases</pattern>
  <pattern confidence="0.85">Overflow-safe midpoint calculation</pattern>
</patterns>

<constraints>
  <hard_requirement>Array must be sorted (ascending)</hard_requirement>
  <hard_requirement>Handle empty array case</hard_requirement>
  <hard_requirement>Return -1 if not found</hard_requirement>
  <soft_preference>Use type hints for clarity</soft_preference>
  <soft_preference>Include docstring with examples</soft_preference>
  <anti_pattern>Linear search (defeats purpose)</anti_pattern>
  <anti_pattern>Integer overflow on mid calculation</anti_pattern>
</constraints>

<complexity_factors>
  <factor>Edge case handling (empty, single element, not found)</factor>
  <factor>Integer overflow prevention</factor>
  <factor>Off-by-one errors in bounds</factor>
</complexity_factors>

<success_indicators>
  <indicator>O(log n) time complexity achieved</indicator>
  <indicator>Handles empty array correctly</indicator>
  <indicator>Comprehensive docstring included</indicator>
  <indicator>Type validation present</indicator>
</success_indicators>

<error_patterns>
  <error>Fails on unsorted input (silent wrong answer)</error>
  <error>Does not handle duplicate values specially</error>
</error_patterns>

<improvements_needed priority="high">
  <improvement>Add input validation for list type</improvement>
  <improvement>Consider returning all indices for duplicates</improvement>
  <improvement>Add usage examples in docstring</improvement>
</improvements_needed>
</context>
```

## How It Works

1. **Send to LLM** with structured extraction prompt
2. **Parse JSON response** from LLM
3. **Fallback to heuristics** if JSON parsing fails:
   - Regex for code patterns (function defs, classes)
   - Keyword detection for constraints
   - Error keyword scanning
4. **Merge results** from LLM + heuristics
5. **Return structured context** for next iteration

## Extraction Prompt
```
Analyze this agent output and extract structured context.

OUTPUT:
{agent_output}

TASK:
{original_task}

Extract and return as JSON:
{
  "domain_primitives": {"objects": [], "operations": [], "relationships": []},
  "patterns": [],
  "constraints": {"hard_requirements": [], "soft_preferences": [], "anti_patterns": []},
  "complexity_factors": [],
  "success_indicators": [],
  "error_patterns": []
}
```

## Examples

### Example 1: Extracting from Code Output
```bash
$ /extract-context ./prompts/001-palindrome/output.md
```

**Input** (LLM output):
```python
def is_palindrome(s):
    """Check if string is palindrome."""
    if not isinstance(s, str):
        raise TypeError("Input must be string")
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]
```

**Output**:
```xml
<context>
<patterns>
  <pattern>String reversal comparison</pattern>
  <pattern>Type validation with guard clause</pattern>
  <pattern>Character filtering for alphanumeric only</pattern>
</patterns>
<constraints>
  <hard_requirement>Input must be string type</hard_requirement>
  <soft_preference>Case-insensitive comparison</soft_preference>
  <soft_preference>Ignore non-alphanumeric characters</soft_preference>
</constraints>
<success_indicators>
  <indicator>Handles non-string input with clear error</indicator>
  <indicator>Normalizes case for comparison</indicator>
</success_indicators>
<improvements_needed>
  <improvement>Add docstring examples</improvement>
  <improvement>Consider two-pointer approach for efficiency</improvement>
</improvements_needed>
</context>
```

### Example 2: Extracting from Design Output
```bash
$ /extract-context ./prompts/001-rate-limiter/output.md
```

**Output**:
```xml
<context>
<domain_primitives>
  <objects>token bucket, request counter, time window</objects>
  <operations>increment, check, reset, distribute</operations>
  <relationships>bucket per client, distributed sync</relationships>
</domain_primitives>
<patterns>
  <pattern>Token bucket algorithm</pattern>
  <pattern>Sliding window for burst handling</pattern>
  <pattern>Redis atomic operations for distribution</pattern>
</patterns>
<constraints>
  <hard_requirement>100k req/s throughput</hard_requirement>
  <hard_requirement>Sub-millisecond latency</hard_requirement>
  <anti_pattern>Single point of failure</anti_pattern>
</constraints>
<improvements_needed>
  <improvement>Add circuit breaker for Redis failures</improvement>
  <improvement>Design multi-region replication</improvement>
</improvements_needed>
</context>
```

## When to Use

**Use when:**
- After completing first iteration
- Preparing improved prompt for iteration 2+
- Identifying gaps before final review
- Building context for handoff to another agent

**Don't use when:**
- Output is trivial (nothing to extract)
- Already have clear requirements
- Final iteration (no more improvements planned)

## Integration

Chain with other skills:
```bash
# Extract then improve
$ /extract-context output.md | /meta-prompt-iterate "task" --context -

# Build context over multiple iterations
$ /extract-context iter1.md >> context.xml
$ /extract-context iter2.md >> context.xml

# Feed into assessment
$ /extract-context output.md && /assess-quality --output output.md
```

## Feeding Context to Next Iteration

The extracted context is automatically formatted into the next prompt:

```markdown
## Previous Iteration Context

Based on iteration 1, incorporate these learnings:

**Patterns that worked:**
- Two-pointer technique (efficient)
- Guard clause pattern (robust)

**Must satisfy:**
- Array must be sorted
- Handle empty array case

**Improvements needed:**
- Add input validation
- Include usage examples

Now improve the solution...
```

## Implementation

Uses `ContextExtractor` from the meta-prompting engine:
```python
from meta_prompting_engine.extraction import ContextExtractor
from meta_prompting_engine.llm_clients.claude import ClaudeClient

llm = ClaudeClient(api_key="...")
extractor = ContextExtractor(llm)

context = extractor.extract_context_hierarchy(
    agent_output="def binary_search...",
    task="implement binary search"
)

print(f"Patterns: {context.patterns}")
print(f"Constraints: {context.constraints}")
print(f"Improvements: {context.improvements_needed}")
```

## Source
- Engine: `/meta_prompting_engine/extraction.py`
- Tests: `/tests/test_core_engine.py`
- Real examples: `/test_real_api.py` output
