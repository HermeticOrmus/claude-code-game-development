# SKILL: Analyze Task Complexity

## Purpose
Determine the optimal meta-prompting strategy for any task by analyzing complexity factors and routing to the appropriate approach.

## Description
Analyzes task complexity on a 0.0-1.0 scale based on four factors:
- **Word count** (0.0-0.25): Length and scope indicator
- **Ambiguity** (0.0-0.25): Vague terms and undefined requirements
- **Dependencies** (0.0-0.25): Conditional logic and interconnections
- **Domain specificity** (0.0-0.25): Technical depth required

Returns a structured assessment with recommended strategy.

## Usage
```bash
/analyze-complexity "Create a distributed rate-limiting system for 100k req/s"
```

## Output Format
```xml
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
<suggested_iterations>3-5</suggested_iterations>
</complexity>
```

## Strategy Routing

| Complexity Score | Level | Strategy | Iterations |
|-----------------|-------|----------|------------|
| **< 0.3** | SIMPLE | direct_execution | 1 |
| **0.3 - 0.7** | MEDIUM | multi_approach_synthesis | 2-3 |
| **> 0.7** | COMPLEX | autonomous_evolution | 3-5 |

### Strategy Details

**direct_execution** (Simple tasks)
- Single-pass execution with clear reasoning
- Prompt: "Execute with step-by-step reasoning"
- No iteration needed

**multi_approach_synthesis** (Medium tasks)
- Generate 2-3 approaches
- Evaluate strengths/weaknesses
- Implement best approach
- Prompt: "Consider multiple approaches, evaluate tradeoffs, choose optimal"

**autonomous_evolution** (Complex tasks)
- Generate architectural hypotheses
- Test against constraints iteratively
- Refine based on discovered issues
- Prompt: "Generate hypotheses, test rigorously, evolve solution"

## How It Works

1. **Tokenize** the task description
2. **Count words** and normalize (log scale)
3. **Detect ambiguous terms**: "implement", "create", "design", "system", "handle"
4. **Identify dependencies**: "if", "when", "based on", "depending", "multiple"
5. **Score domain specificity**: Technical keywords, domain-specific terms
6. **Aggregate** weighted scores (0.0-1.0)
7. **Route** to optimal strategy

## Examples

### Example 1: Simple Task
```bash
$ /analyze-complexity "Write function to calculate factorial"
```
```xml
<complexity score="0.12" level="SIMPLE">
<factors>
  <word_count>0.05</word_count>
  <ambiguity>0.02</ambiguity>
  <dependencies>0.00</dependencies>
  <domain_specificity>0.05</domain_specificity>
</factors>
<strategy>direct_execution</strategy>
<reasoning>
  Short task, single operation, well-defined algorithm.
  No ambiguity, no dependencies, basic domain.
</reasoning>
<recommended_approach>
  1. Implement recursive or iterative factorial
  2. Add input validation
  3. Done in single pass
</recommended_approach>
<suggested_iterations>1</suggested_iterations>
</complexity>
```

### Example 2: Medium Task
```bash
$ /analyze-complexity "Create a priority queue class with efficient insert and extract-min operations"
```
```xml
<complexity score="0.52" level="MEDIUM">
<factors>
  <word_count>0.12</word_count>
  <ambiguity>0.10</ambiguity>
  <dependencies>0.15</dependencies>
  <domain_specificity>0.15</domain_specificity>
</factors>
<strategy>multi_approach_synthesis</strategy>
<reasoning>
  Data structure implementation with performance requirements.
  Multiple valid approaches (heap, balanced tree, sorted list).
  Requires evaluation of tradeoffs.
</reasoning>
<recommended_approach>
  1. Consider heap vs balanced tree approaches
  2. Evaluate time complexity tradeoffs
  3. Implement optimal choice with tests
</recommended_approach>
<suggested_iterations>2-3</suggested_iterations>
</complexity>
```

### Example 3: Complex Task
```bash
$ /analyze-complexity "Design a distributed cache system with consistency guarantees, fault tolerance, and horizontal scaling to 1M QPS"
```
```xml
<complexity score="0.85" level="COMPLEX">
<factors>
  <word_count>0.18</word_count>
  <ambiguity>0.15</ambiguity>
  <dependencies>0.22</dependencies>
  <domain_specificity>0.30</domain_specificity>
</factors>
<strategy>autonomous_evolution</strategy>
<reasoning>
  Distributed systems domain with multiple competing concerns.
  Must balance consistency vs availability (CAP theorem).
  Requires architectural decisions across multiple layers.
  Performance target creates hard constraint.
</reasoning>
<recommended_approach>
  1. Generate 3+ architectural approaches
  2. Analyze consistency models (eventual, strong, causal)
  3. Design fault tolerance mechanisms
  4. Test scaling assumptions against 1M QPS target
  5. Iterate on bottlenecks
</recommended_approach>
<suggested_iterations>4-5</suggested_iterations>
</complexity>
```

## When to Use

**Use when:**
- Starting a new task and unsure of approach
- Deciding how many iterations to budget
- Choosing between quick execution vs thorough exploration
- Prioritizing multiple tasks by complexity

**Don't use when:**
- Task is obviously trivial (just do it)
- Already know the optimal approach
- Time-critical (adds latency)

## Integration

Chain with other skills:
```bash
# Analyze then iterate
$ /analyze-complexity "task" && /meta-prompt-iterate "task"

# Batch analyze multiple tasks
$ for task in tasks.txt; do /analyze-complexity "$task"; done

# Route based on result
complexity=$(/analyze-complexity "task" | grep score | cut -d'"' -f2)
if [ $(echo "$complexity > 0.7" | bc) -eq 1 ]; then
  /meta-prompt-iterate "task" --max-iterations 5
fi
```

## Implementation

Uses `ComplexityAnalyzer` from the meta-prompting engine:
```python
from meta_prompting_engine.complexity import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()
result = analyzer.analyze("your task here")

print(f"Score: {result.overall}")
print(f"Strategy: {result.strategy}")
print(f"Factors: {result.factors}")
```

## Source
- Engine: `/meta_prompting_engine/complexity.py`
- Tests: `/tests/test_core_engine.py`
- Validation: `/validate_implementation.py`
