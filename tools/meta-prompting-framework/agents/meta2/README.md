# Meta² Agent - Universal Meta-Prompting Framework Generator

## Overview

The **meta2** agent is a universal meta-meta-prompt generator that discovers domain structures and produces comprehensive meta-prompting frameworks across arbitrary depth levels using category theory principles.

## What It Does

Given any domain (familiar or unfamiliar), meta2:

1. **Discovers** domain primitives and operations
2. **Designs** N-level sophistication progression
3. **Applies** categorical framework (functors, rewrite, inclusion, etc.)
4. **Generates** complete meta-prompts for each level
5. **Proves** mathematical correctness via category theory

## Quick Example

**Input:**
```
DOMAIN: "code refactoring"
DEPTH_LEVELS: 5
CATEGORICAL_FRAMEWORK: "natural_equivalence"
THEORETICAL_DEPTH: "moderate"
```

**Output:**
```
Level 1: Variable Renaming (simple substitution)
Level 2: Extract Function (control flow analysis)
Level 3: Design Patterns (structural transformation)
Level 4: Architecture Refactoring (system-level changes)
Level 5: Paradigm Shifts (fundamental rethinking)
```

Each with complete meta-prompt templates, examples, and proofs.

## Capabilities

### Works for ANY Domain

- **Familiar domains**: Uses existing knowledge
- **Unfamiliar domains**: Researches using WebSearch/Context7/MARS
- **Mixed domains**: Bridges multiple areas

Examples tested:
- Software: F* verification, API design, code generation
- Creative: Writing, music composition
- Analysis: Data processing, research synthesis
- Formal: Mathematical proofs, verification

### Adaptive Framework Selection

Chooses the best categorical structure:

- **internal_hom**: When exponential objects are natural
- **functors**: When transformations are explicit
- **rewrite**: When task-agnosticity matters most
- **inclusion**: When levels embed hierarchically
- **natural_equivalence**: For elegant minimal proofs

### Flexible Output

- **Template**: Fillable framework for teams
- **Full specification**: Ready-to-use complete system
- **Examples**: Concrete instantiations
- **Theoretical paper**: Publication-ready academic output

## 7-Phase Generation Process

### Phase 1: Domain Analysis

**Discovery Algorithm** (works even for unknown domains):

1. Research domain (WebSearch, Context7, or MARS)
2. Identify primitives (atomic objects)
3. Discover operations (composition patterns)
4. Find identity morphisms
5. Determine complexity drivers

**Output**: Category C_Domain with Objects, Morphisms, Composition

### Phase 2: Level Architecture

Design N-level progression with qualitative leaps:

- L1: Simplest formulation
- L_mid: Progressive capabilities
- L_N: Paradigm-creating sophistication

**Output**: Level names, embeddings, leap specifications

### Phase 3: Categorical Framework Application

Apply chosen framework uniformly:

**Example (natural_equivalence)**:
```
Apply Lemma 1: Hom(Y, Z^X) ≅ Hom(Y × X, Z)
Establish rewrites for each (L_i, L_{i+1})
Conclude functors exist without explicit construction
```

**Output**: Exponential objects, functors/rewrites, theoretical justification

### Phase 4: Level-Specific Generation

For each level i ∈ {1..N}, generate:

- **Theoretical foundation**: Computational model, complexity class
- **Architecture**: Diagrams showing components
- **Meta-prompt template**: Executable prompt for this level
- **Domain example**: Concrete application
- **Usage guidance**: When to use, tradeoffs
- **Equivalence proof**: Connection to next level

**Output**: Complete specifications for all N levels

### Phase 5: Cross-Level Integration

Prove coherence:

- Inclusion chain: L₁ ⊂ L₂ ⊂ ... ⊂ L_N
- Progressive refinement path
- Level selection decision tree

**Output**: Integration proofs and algorithms

### Phase 6: Theoretical Justification

Depth-appropriate mathematical rigor:

- **Minimal**: Brief explanation (1-2 paragraphs)
- **Moderate**: Key proofs (2-3 pages)
- **Comprehensive**: Full treatment (5-10 pages)
- **Research-level**: Novel contributions (publication-ready)

**Output**: Proofs, lemmas, theorems

### Phase 7: Output Formatting

Produce final deliverable in requested format:

- Executive summary
- Categorical foundations
- Level architecture
- N level specifications
- Cross-level integration
- Theoretical justification
- Practical implementation guide
- Extensions and future work
- Appendices

**Output**: Complete framework document

## Usage

### Via Agent System

```python
from agents.meta2 import Meta2Agent

agent = Meta2Agent()

framework = agent.generate(
    domain="distributed systems consensus",
    depth_levels=7,
    categorical_framework="functors",
    theoretical_depth="comprehensive",
    output_format="full_specification"
)
```

### Via Direct Invocation

Copy `agent.md` contents and provide:

```
I need a meta-prompting framework with these parameters:

DOMAIN: "UI component design"
DEPTH_LEVELS: 5
CATEGORICAL_FRAMEWORK: "inclusion"
THEORETICAL_DEPTH: "moderate"
OUTPUT_FORMAT: "full_specification"

Generate the complete framework.
```

### Progressive Elaboration

Start minimal, expand as needed:

```python
# Start with 3 levels
framework_v1 = agent.generate(domain="...", depth_levels=3)

# User reviews, requests expansion
framework_v2 = agent.expand(framework_v1, depth_levels=7)
# Preserves L1-L3, adds L4-L7 with coherence
```

## Parameters

### Required

- **DOMAIN**: Application domain (any field)
- **DEPTH_LEVELS**: N ∈ {3, 5, 7, 10, ...}

### Optional

- **CATEGORICAL_FRAMEWORK**:
  - `natural_equivalence` (default) - Elegant via Lemma 1
  - `functors` - Explicit transformations
  - `rewrite` - Task-agnosticity emphasis
  - `inclusion` - Hierarchical embeddings
  - `internal_hom` - Exponential objects
  - `comprehensive` - All approaches

- **THEORETICAL_DEPTH**:
  - `minimal` - Brief explanation
  - `moderate` (default) - Key proofs
  - `comprehensive` - Full treatment
  - `research_level` - Novel contributions

- **OUTPUT_FORMAT**:
  - `full_specification` (default) - Complete system
  - `template` - Fillable with placeholders
  - `examples` - Concrete instantiations
  - `theoretical_paper` - Academic structure

## Examples

### Example 1: F* Verification Framework

**Input:**
```
DOMAIN: "F* proof-oriented programming"
DEPTH_LEVELS: 7
CATEGORICAL_FRAMEWORK: "natural_equivalence"
THEORETICAL_DEPTH: "comprehensive"
```

**Output:** See `../../examples/fstar-framework/FRAMEWORK.md`

- 7 levels: Refinement Types → Novel Proof Architectures
- 42 F* code examples
- 7 categorical proofs
- ~35,000 words

### Example 2: API Design Framework

**Input:**
```
DOMAIN: "RESTful API design"
DEPTH_LEVELS: 5
CATEGORICAL_FRAMEWORK: "inclusion"
THEORETICAL_DEPTH: "moderate"
```

**Output:**
- L1: Simple CRUD endpoints
- L2: Resource relationships (HATEOAS basics)
- L3: Hypermedia controls (full REST)
- L4: Advanced patterns (versioning, caching, pagination)
- L5: Domain-driven API design (DDD + REST)

## Integration with Other Agents

### With deep-researcher

```python
# Research unfamiliar domain first
research = deep_researcher.research("quantum algorithm design")

# Then generate framework using research
framework = meta2.generate(
    domain="quantum algorithm design",
    depth_levels=7,
    # meta2 incorporates research findings automatically
)
```

### With test-engineer

```python
# Generate framework
framework = meta2.generate(domain="test automation", depth_levels=5)

# Create tests for framework examples
tests = test_engineer.test(framework.examples)
```

### With docs-generator

```python
# Generate framework
framework = meta2.generate(domain="...", depth_levels=7)

# Polish documentation
polished = docs_generator.polish(framework, style="professional")
```

## Theoretical Foundation

Based on "On Meta-Prompting" (de Wynter et al., arXiv:2312.06562v3):

### Key Theorems

**Theorem 1 (Task-Agnosticity)**: Meta-prompt morphisms exist for any task-category.

**Lemma 1 (Rewrite-Functor)**: If task descriptions can be rewritten equivalently, functors exist.

**Theorem 2 (Universal Meta-Prompting)**: Meta-prompts work for ANY two tasks.

### Natural Equivalence

```
Hom(Y, Z^X) ≅ Hom(Y × X, Z)
```

Left side: Level → (Task → Output)
Right side: (Level, Task) → Output

The framework realizes this equivalence through the Rewrite category.

## Self-Verification

Before outputting, meta2 checks:

- ✓ All N levels present and complete?
- ✓ Categorical framework applied consistently?
- ✓ Natural equivalence chain established?
- ✓ Inclusion relationships proven?
- ✓ Examples concrete and domain-appropriate?
- ✓ Theoretical depth matches requested?
- ✓ Output format matches requested?

## Strengths

1. **Universal Discovery**: Works for ANY domain
2. **Research Integration**: Delegates to deep-researcher when needed
3. **Progressive Elaboration**: Supports iterative refinement
4. **Error Recovery**: Handles non-categorical domains gracefully
5. **Tool Mastery**: Orchestrates WebSearch, Context7, Task delegation
6. **Mathematical Rigor**: Maintains category theory correctness
7. **Practical Focus**: Generates immediately usable meta-prompts
8. **Quality Assurance**: Built-in validation

## Limitations

- Complex domains may need significant research (uses tools to overcome)
- Very large N (>10) may become unwieldy (recommends domain decomposition)
- Some domains resist categorical structure (offers alternatives)
- Requires understanding of input domain to validate output quality

## Future Enhancements

- **Auto-detection**: Infer DEPTH_LEVELS from domain complexity
- **ML-guided**: Learn optimal frameworks from usage data
- **Bidirectional**: Generate domain from desired framework properties
- **Cross-domain**: Translate frameworks between domains
- **Meta⁴**: Generate meta-meta-prompts themselves

## Files

- `agent.md` - Complete agent definition (750+ lines)
- `README.md` - This file
- `examples/` - Generated framework examples

## See Also

- [Meta-Meta-Prompting Framework](../../theory/META-META-PROMPTING-FRAMEWORK.md) - Theoretical foundations
- [F* Framework Example](../../examples/fstar-framework/FRAMEWORK.md) - Complete output example
- [Meta-Prompts V2](../../meta-prompts/v2/META_PROMPTS.md) - Production meta-prompts

---

**The bridge between category theory and practical meta-prompting.**
