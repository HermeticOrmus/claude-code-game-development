# Quick Start Guide

Get started with the Meta-Prompting Framework in 5 minutes.

## What You'll Learn

1. How to use production meta-prompts immediately
2. How to generate custom frameworks for your domain
3. How to integrate meta-prompts into your workflow

---

## Option 1: Use Production Meta-Prompts (Fastest)

### Step 1: Choose Your Meta-Prompt

Based on your task:

| If you need... | Use this meta-prompt |
|----------------|---------------------|
| Default choice, works for everything | **Autonomous Routing** |
| Novel problem, breakthrough thinking | **Principle-Centered** |
| Cross-domain task (code + docs) | **Domain-Bridge** |
| Maximum quality, have time | **Quality-Focused** |
| Creative insight, unconventional | **Emergent Properties** |
| Fast results, good enough | **Cost-Balanced** |

### Step 2: Copy the Meta-Prompt

Open `meta-prompts/v2/META_PROMPTS.md` and copy your chosen meta-prompt.

### Step 3: Apply to Your Task

```
[Paste meta-prompt here]

Your task: Implement a caching layer for our API

Now execute using the meta-prompt approach.
```

### Example

```
You are an autonomous system that analyzes context and adapts your approach.

CONTEXT ANALYSIS:
1. Extract complexity (0.0-1.0): How hard is this task?
2. Identify domain: code? creative? analysis? data?
3. Assess format: structured output? freeform? mixed?
4. Note constraints: speed? quality? clarity? formality?

[... rest of Autonomous Routing meta-prompt ...]

Your task: Design a distributed rate limiter

Now execute using the meta-prompt approach.
```

**Result**: Your AI assistant will analyze the task complexity, choose the appropriate reasoning strategy, and deliver a structured solution.

---

## Option 2: Generate Custom Framework (Most Powerful)

### Step 1: Define Your Domain

What domain do you want a meta-prompting framework for?

Examples:
- "Machine learning pipeline optimization"
- "Technical writing for developers"
- "Database query optimization"
- "UI/UX design patterns"

### Step 2: Choose Parameters

```python
DOMAIN = "database query optimization"
DEPTH_LEVELS = 5  # 3, 5, 7, or 10
CATEGORICAL_FRAMEWORK = "natural_equivalence"  # or "inclusion", "functors", etc.
THEORETICAL_DEPTH = "moderate"  # minimal, moderate, comprehensive, research-level
OUTPUT_FORMAT = "full_specification"  # template, full_specification, examples
```

### Step 3: Use the meta2 Agent

Copy the agent definition from `agents/meta2/agent.md` and provide:

```
I need a meta-prompting framework with these parameters:

DOMAIN: "database query optimization"
DEPTH_LEVELS: 5
CATEGORICAL_FRAMEWORK: "natural_equivalence"
THEORETICAL_DEPTH: "moderate"
OUTPUT_FORMAT: "full_specification"

Generate the complete framework.
```

### Step 4: Receive Your Framework

The agent will generate a complete 5-level framework:

```
Level 1: Simple Queries (SELECT, WHERE, basic indexes)
Level 2: Join Optimization (INNER/OUTER joins, index selection)
Level 3: Query Planning (execution plans, cost models)
Level 4: Advanced Optimization (materialized views, partitioning)
Level 5: Adaptive Systems (query learning, statistics feedback)
```

Each level includes:
- Theoretical foundation
- Architecture diagrams
- Meta-prompt template
- Concrete examples
- Usage guidance
- Equivalence proofs to next level

---

## Option 3: Python Integration (Programmatic)

### Step 1: Install (Coming Soon)

```bash
pip install meta-prompting-framework
```

### Step 2: Use in Code

```python
from meta_prompts.v2 import MetaPromptLibrary

# Create library
lib = MetaPromptLibrary()

# Select and apply
meta = lib.select("principle-centered")
instruction = meta.format(task="Design auth system")

# Use with your AI agent
result = your_ai_agent.execute(instruction)
```

### Step 3: Generate Custom Frameworks

```python
from agents.meta2 import Meta2Agent

agent = Meta2Agent()

framework = agent.generate(
    domain="API design",
    depth_levels=5,
    categorical_framework="inclusion"
)

# framework is a complete meta-prompting system
print(framework.level(3).template)  # Get L3 meta-prompt
```

---

## Common Patterns

### Pattern 1: Progressive Complexity

Use a framework to handle tasks at different complexity levels:

```python
# Simple task → Use L1
if task.complexity < 0.3:
    prompt = framework.level(1).generate(task)

# Complex task → Use L5
elif task.complexity > 0.7:
    prompt = framework.level(5).generate(task)
```

### Pattern 2: Hybrid Approach

Combine multiple meta-prompts:

```
First, apply Principle-Centered to identify core objectives.
Then, apply Quality-Focused to refine the solution.
```

### Pattern 3: Iterative Refinement

Start simple, escalate if needed:

```python
result = framework.level(1).execute(task)
if not result.satisfactory():
    result = framework.level(2).execute(task)
```

---

## Next Steps

### Learn More

- **[Usage Patterns](USAGE_PATTERNS.md)** - Advanced workflows
- **[Selection Guide](../meta-prompts/v2/docs/SELECTION_GUIDE.md)** - Deep dive on choosing meta-prompts
- **[Categorical Glossary](CATEGORICAL_GLOSSARY.md)** - Understand the theory
- **[F* Example](../examples/fstar-framework/FRAMEWORK.md)** - Complete framework example

### Experiment

Try these exercises:

1. **Exercise 1**: Use Autonomous Routing on a coding task. Observe how it analyzes complexity.

2. **Exercise 2**: Generate a 3-level framework for a domain you know well.

3. **Exercise 3**: Compare Principle-Centered vs Quality-Focused on the same task.

### Contribute

Found a great pattern? Share it!

- Open an issue with your use case
- Submit a PR with a new example
- Join discussions on GitHub

---

## Troubleshooting

### "Which meta-prompt should I use?"

**Default answer**: Autonomous Routing (it adapts automatically)

**If that's not working**: Check the decision tree in `meta-prompts/v2/META_PROMPTS.md`

### "How do I know what complexity level to use?"

Use this heuristic:
- **L1**: Can be done with template/pattern
- **L3**: Requires some problem-solving
- **L5**: Novel approach needed
- **L7**: Research-level breakthrough

### "The framework is too theoretical"

Set `THEORETICAL_DEPTH = "minimal"` when generating. You'll get practical guidance with light theory.

### "I need faster results"

Use the **Cost-Balanced** meta-prompt, which optimizes for quality-per-token.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/meta-prompting-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/meta-prompting-framework/discussions)
- **Examples**: See `examples/` directory

---

**You're ready to go!** Start with a production meta-prompt and see the difference in your AI outputs. 🚀
