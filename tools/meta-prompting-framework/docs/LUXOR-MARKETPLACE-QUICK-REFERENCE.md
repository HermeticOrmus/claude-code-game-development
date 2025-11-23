# Quick Reference: Meta-Framework Generator Suite

**Cheat Sheet for Luxor-Claude Marketplace Integration**

---

## Quick Start (5 Minutes)

### 1. Generate Single Framework

```python
from meta_framework_generator import MetaFrameworkGenerator, TopicInput

# Define topic
topic = TopicInput(
    topic="Your Topic Here",
    category="Technology",  # or Data, Design, Business
    depth_levels=7,
    iterations=3
)

# Generate
generator = MetaFrameworkGenerator()
framework = generator.generate(topic)

# Use
result = framework.levels[2].respond(query="How do I...?")
```

### 2. Integrate with Marketplace

```python
from marketplace_integration import MarketplaceIntegration

# Initialize
integration = MarketplaceIntegration(
    marketplace_api="https://luxor-claude-marketplace.com/api"
)

# Register topic
integration.register_topic("blockchain-dev", topic_config)

# Get framework (auto-generated if needed)
framework = integration.get_framework("blockchain-dev")
```

### 3. Generate Multiple Frameworks in Parallel

```python
from parallel_generator import ParallelFrameworkGenerator

# Define topics
topics = [
    TopicInput(topic="Blockchain", ...),
    TopicInput(topic="Data Science", ...),
    TopicInput(topic="UX Design", ...)
]

# Generate in parallel
parallel_gen = ParallelFrameworkGenerator(max_workers=8)
frameworks = parallel_gen.generate_parallel(topics)
```

---

## Topic Input Reference

### Required Fields

```python
TopicInput(
    topic: str,              # Topic name
    category: str,           # Marketplace category
    depth_levels: int,       # 3, 5, 7, or 10
    iterations: int          # Kan iterations (1-4)
)
```

### Optional Fields

```python
TopicInput(
    complexity: float = 0.5,           # 0.0 (simple) to 1.0 (complex)
    maturity: str = 'established',     # 'emerging', 'established', 'mature'
    interdisciplinary: list = [],      # Related domains
    theoretical_depth: str = 'moderate', # 'minimal', 'moderate', 'comprehensive'
    code_examples: bool = True,        # Include code?
    evolution_strategy: str = 'balanced' # 'conservative', 'balanced', 'aggressive'
)
```

---

## Level Structure

### 7-Level Default Names

```python
levels = [
    "Novice",       # L1: Basics, primitives
    "Competent",    # L2: Composition, pipelines
    "Proficient",   # L3: Standard patterns
    "Advanced",     # L4: Complex structures
    "Expert",       # L5: Optimization, scaling
    "Master",       # L6: Novel approaches
    "Visionary"     # L7: Breakthrough innovations
]
```

### Custom Level Configuration

```python
# Override default names
custom_levels = {
    0: {"name": "Foundation", "focus": "Core concepts"},
    1: {"name": "Builder", "focus": "Composition"},
    # ... etc
}

generator.generate(topic, level_config=custom_levels)
```

---

## Framework Composition

### Product (Combine)

```python
from framework_composer import FrameworkComposer

composer = FrameworkComposer()

# Combine two frameworks
combined = composer.product(
    framework1,  # e.g., Blockchain
    framework2   # e.g., Data Science
)
# Result: Crypto analytics framework
```

### Coproduct (Either/Or)

```python
# Branch between frameworks
branched = composer.coproduct(
    framework1,  # e.g., Mobile
    framework2   # e.g., Web
)
# Result: Cross-platform framework
```

### Pullback (Over Shared Context)

```python
# Combine over shared foundation
integrated = composer.pullback(
    framework1,      # e.g., Frontend
    framework2,      # e.g., Backend
    shared_context   # e.g., Web Architecture
)
# Result: Full-stack framework
```

### Kan Extension (Generalize/Specialize)

```python
# Generalize
generalized = composer.kan_compose(
    framework1,
    framework2,
    direction='left'  # Lan_F(G)
)

# Specialize
specialized = composer.kan_compose(
    framework1,
    framework2,
    direction='right'  # Ran_F(G)
)
```

---

## Kan Extension Iterations

### Strategies

```python
# Conservative: Small refinements
framework = generator.kan_iterate(
    framework,
    iteration=1,
    strategy='conservative'
)

# Balanced: Moderate improvements
framework = generator.kan_iterate(
    framework,
    iteration=2,
    strategy='balanced'
)

# Aggressive: Novel structures
framework = generator.kan_iterate(
    framework,
    iteration=3,
    strategy='aggressive'
)
```

### What Each Iteration Does

| Iteration | Focus | Kan Type | Changes |
|-----------|-------|----------|---------|
| 1 | Refinement | Right Kan | Fill gaps, improve examples |
| 2 | Enhancement | Both | Cross-cutting, optimization |
| 3 | Innovation | Left Kan | Novel structures, breakthroughs |
| 4+ | Advanced | Custom | Domain-specific deep improvements |

---

## Self-Evolution

### Enable Auto-Evolution

```python
from adaptive_framework import AdaptiveFramework

# Wrap framework
adaptive = AdaptiveFramework(framework)

# Track usage
adaptive.track_usage(
    level=2,
    query="How do I implement X?",
    success=True
)

# Collect feedback
adaptive.collect_feedback(
    user_id="user123",
    level=2,
    rating=4.5,
    comments="Good but needs more examples"
)

# Auto-evolve when quality drops
if adaptive.should_evolve():
    adaptive.evolve()
```

### Manual Evolution Trigger

```python
from marketplace_integration import MarketplaceIntegration

integration = MarketplaceIntegration(...)

# Evolve based on feedback
evolved = integration.evolve_framework(
    topic_id="blockchain-dev",
    feedback={
        'weak_levels': [2, 5],
        'requested_features': ['more examples', 'clearer explanations'],
        'strategy': 'balanced'
    }
)
```

---

## Parallel Generation

### Simple Parallel

```python
from parallel_generator import ParallelFrameworkGenerator

topics = [topic1, topic2, topic3]

parallel_gen = ParallelFrameworkGenerator(max_workers=4)
frameworks = parallel_gen.generate_parallel(topics)
```

### With Dependencies

```python
from dependency_graph import DependencyGraph

# Build dependency graph
graph = DependencyGraph()
graph.add_topic("topic1", config1, depends_on=[])
graph.add_topic("topic2", config2, depends_on=[])
graph.add_topic("topic3", config3, depends_on=["topic1"])

# Generate in topological order
frameworks = graph.generate_topological(generator)
```

### Async Generation

```python
import asyncio

async def generate_all():
    topics = [topic1, topic2, topic3]
    frameworks = await parallel_gen.generate_async(topics)
    return frameworks

frameworks = asyncio.run(generate_all())
```

---

## API Endpoints

### Framework Management

```http
POST /api/topics/register
Content-Type: application/json

{
  "topic_id": "blockchain-dev",
  "config": { ... }
}
```

```http
GET /api/frameworks/{topic_id}
```

```http
POST /api/frameworks/{topic_id}/evolve
Content-Type: application/json

{
  "strategy": "balanced",
  "feedback": { ... }
}
```

### Composition

```http
POST /api/frameworks/compose
Content-Type: application/json

{
  "framework_ids": ["topic1", "topic2"],
  "composition_type": "product"
}
```

### Batch Generation

```http
POST /api/categories/{category_id}/generate-all
```

---

## Common Patterns

### Pattern 1: Topic → Framework → Query

```python
# 1. Define topic
topic = TopicInput(topic="Machine Learning", ...)

# 2. Generate framework
framework = generator.generate(topic)

# 3. Query specific level
response = framework.levels[3].respond(
    "How do I implement gradient descent?"
)
```

### Pattern 2: Marketplace Integration

```python
# 1. Initialize integration
integration = MarketplaceIntegration(api_url)

# 2. Register all topics
for topic_id, config in marketplace_topics.items():
    integration.register_topic(topic_id, config)

# 3. Generate on-demand
framework = integration.get_framework("topic_id")
```

### Pattern 3: Batch + Cache

```python
# 1. Generate entire category
frameworks = integration.generate_category_frameworks("Technology")

# 2. All frameworks cached automatically
# 3. Subsequent requests instant
framework = integration.get_framework("blockchain-dev")  # From cache
```

### Pattern 4: Evolution Monitoring

```python
# 1. Deploy framework
framework = integration.get_framework("topic")

# 2. Monitor usage
adaptive = AdaptiveFramework(framework)
adaptive.track_usage(...)
adaptive.collect_feedback(...)

# 3. Auto-evolve
if adaptive.should_evolve():
    new_version = adaptive.evolve()
    integration.registry.update_framework("topic", new_version)
```

---

## Configuration

### Environment Variables

```bash
# Marketplace
MARKETPLACE_API_URL=https://luxor-claude-marketplace.com/api
MARKETPLACE_API_KEY=your-api-key

# Generator
MAX_WORKERS=8
DEFAULT_ITERATIONS=3
DEFAULT_STRATEGY=balanced

# Cache
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_DIR=/var/cache/frameworks

# Evolution
AUTO_EVOLVE=true
EVOLUTION_THRESHOLD=0.7
MIN_FEEDBACK_COUNT=10
```

### Configuration File

```yaml
# config.yaml
marketplace:
  api_url: https://luxor-claude-marketplace.com/api
  api_key: ${MARKETPLACE_API_KEY}

generator:
  max_workers: 8
  default_depth: 7
  default_iterations: 3
  strategies:
    - conservative
    - balanced
    - aggressive

cache:
  enabled: true
  ttl: 3600
  backend: redis
  redis_url: redis://localhost:6379

evolution:
  auto_enabled: true
  threshold: 0.7
  min_feedback: 10
  strategies:
    weak_level: balanced
    low_satisfaction: conservative
    feature_request: aggressive
```

---

## Troubleshooting

### Issue: Generation Slow

**Solution:**
```python
# Use parallel generation
parallel_gen = ParallelFrameworkGenerator(max_workers=16)

# Or reduce iterations
topic.iterations = 1

# Or reduce depth
topic.depth_levels = 5
```

### Issue: Poor Framework Quality

**Solution:**
```python
# Increase iterations
topic.iterations = 4

# Increase theoretical depth
topic.theoretical_depth = 'comprehensive'

# Use aggressive strategy
topic.evolution_strategy = 'aggressive'
```

### Issue: Composition Fails

**Solution:**
```python
# Check compatibility
if not composer.are_compatible(f1, f2):
    # Use Kan extension instead
    composed = composer.kan_compose(f1, f2, direction='left')
```

### Issue: Evolution Not Triggering

**Solution:**
```python
# Check thresholds
scores = adaptive.analyze_feedback()
print(scores)  # Should show levels < 0.7

# Lower threshold
adaptive.evolution_threshold = 0.6

# Manual trigger
adaptive.evolve()
```

---

## Performance Tips

### 1. Use Caching

```python
# Enable caching
generator.cache.enabled = True

# Warm cache for category
integration.generate_category_frameworks("Technology")
```

### 2. Parallel Generation

```python
# Always use parallel for multiple topics
parallel_gen.generate_parallel(topics)  # ✓ Good

# Don't iterate sequentially
for topic in topics:  # ✗ Slow
    generator.generate(topic)
```

### 3. Optimize Iterations

```python
# Start with 1-2 iterations
topic.iterations = 2  # ✓ Good for most cases

# Use 3-4 only for critical frameworks
topic.iterations = 4  # Only if needed
```

### 4. Batch Operations

```python
# Register all topics at once
integration.batch_register(topics)  # ✓ Efficient

# Don't register one-by-one
for topic in topics:  # ✗ Slow
    integration.register_topic(topic)
```

---

## Testing

### Unit Test Example

```python
import pytest
from meta_framework_generator import MetaFrameworkGenerator, TopicInput

def test_framework_generation():
    topic = TopicInput(
        topic="Test Topic",
        category="Test",
        depth_levels=7,
        iterations=1
    )

    generator = MetaFrameworkGenerator()
    framework = generator.generate(topic)

    # Assertions
    assert len(framework.levels) == 7
    assert framework.topic == "Test Topic"
    assert framework.verify_coherence()
```

### Integration Test Example

```python
def test_marketplace_integration():
    integration = MarketplaceIntegration(test_api_url)

    # Register
    integration.register_topic("test-topic", test_config)

    # Generate
    framework = integration.get_framework("test-topic")

    assert framework is not None
    assert len(framework.levels) == test_config.depth_levels
```

---

## Common Gotchas

### 1. Topic ID Uniqueness

```python
# ✗ Wrong: Duplicate topic IDs
integration.register_topic("blockchain", config1)
integration.register_topic("blockchain", config2)  # Overwrites!

# ✓ Correct: Unique IDs
integration.register_topic("blockchain-dev", config1)
integration.register_topic("blockchain-analysis", config2)
```

### 2. Iteration Order Matters

```python
# ✗ Wrong: Aggressive then conservative
framework = generator.kan_iterate(framework, 1, 'aggressive')
framework = generator.kan_iterate(framework, 2, 'conservative')  # May undo!

# ✓ Correct: Progressive refinement
framework = generator.kan_iterate(framework, 1, 'conservative')
framework = generator.kan_iterate(framework, 2, 'balanced')
framework = generator.kan_iterate(framework, 3, 'aggressive')
```

### 3. Composition Type Selection

```python
# ✗ Wrong: Product when coproduct needed
combined = composer.product(mobile_fw, web_fw)  # Forces both!

# ✓ Correct: Coproduct for alternatives
combined = composer.coproduct(mobile_fw, web_fw)  # Either/or
```

---

## Example Workflows

### Workflow 1: New Marketplace Topic

```python
# 1. Define topic
topic = TopicInput(
    topic="Quantum Computing",
    category="Technology",
    complexity=0.9,
    maturity='emerging',
    depth_levels=7,
    iterations=3
)

# 2. Register with marketplace
integration.register_topic("quantum-computing", topic)

# 3. Generate framework (happens automatically on first request)
framework = integration.get_framework("quantum-computing")

# 4. Monitor usage
adaptive = AdaptiveFramework(framework)

# 5. Evolve as needed
# (automatic based on feedback)
```

### Workflow 2: Entire Category Launch

```python
# 1. Define all topics in category
topics = {
    "topic1": TopicInput(...),
    "topic2": TopicInput(...),
    "topic3": TopicInput(...)
}

# 2. Register all
for tid, config in topics.items():
    integration.register_topic(tid, config)

# 3. Parallel generation
frameworks = integration.generate_category_frameworks("NewCategory")

# 4. Deploy to marketplace
for tid, framework in frameworks.items():
    marketplace.deploy(tid, framework)
```

### Workflow 3: Framework Evolution Cycle

```python
# 1. Initial generation
framework_v1 = generator.generate(topic)

# 2. Deploy and monitor
adaptive = AdaptiveFramework(framework_v1)

# 3. Collect feedback (over time)
while True:
    # User interactions
    adaptive.track_usage(...)
    adaptive.collect_feedback(...)

    # Check weekly
    if should_check():
        if adaptive.should_evolve():
            # Evolve
            adaptive.evolve()
            framework_v2 = adaptive.framework

            # Deploy new version
            marketplace.deploy(topic_id, framework_v2)
```

---

## Resources

### Documentation
- Main Specification: `LUXOR-MARKETPLACE-GENERATOR-SUITE.md`
- Architecture Diagrams: `LUXOR-MARKETPLACE-ARCHITECTURE-DIAGRAMS.md`
- Category Theory Primer: `../theory/CATEGORICAL_FOUNDATIONS.md`

### Code Examples
- Blockchain Framework: `../examples/blockchain-framework/`
- Data Science Framework: `../examples/datascience-framework/`
- UX Design Framework: `../examples/ux-framework/`

### API Reference
- Generator API: `MetaFrameworkGenerator` class
- Integration API: `MarketplaceIntegration` class
- Composition API: `FrameworkComposer` class

---

## Quick Command Reference

```bash
# Generate single framework
python -m meta_framework_generator generate \
  --topic "Blockchain Development" \
  --category Technology \
  --levels 7 \
  --iterations 3

# Generate category
python -m meta_framework_generator generate-category \
  --category Technology \
  --parallel \
  --workers 8

# Evolve framework
python -m meta_framework_generator evolve \
  --topic-id blockchain-dev \
  --strategy balanced

# Compose frameworks
python -m meta_framework_generator compose \
  --frameworks "blockchain,datascience" \
  --type product \
  --output crypto-analytics

# Check framework quality
python -m meta_framework_generator validate \
  --framework-id blockchain-dev
```

---

**Version**: 1.0
**Last Updated**: 2025-11-19
**Quick Reference for**: Meta-Framework Generator Suite

*Keep this handy for rapid development!*
