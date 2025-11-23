# Meta-Prompting Agents

Specialized agents for meta-prompting operations.

## Available Agents

### meta2 (Meta²-Prompt Generator)

**Purpose:** Universal meta-meta-prompt generator that creates comprehensive frameworks for any domain.

**Capabilities:**
- Works for familiar AND unfamiliar domains
- Generates N-level frameworks (3, 5, 7, 10+)
- Multiple categorical frameworks (functors, rewrite, inclusion, natural_equivalence)
- Research integration (WebSearch, Context7, MARS)
- Adaptive theoretical depth (minimal to research-level)

**When to use:**
- Need custom meta-prompting framework for specific domain
- Want hierarchical sophistication levels
- Require categorical rigor and proofs
- Have complex domain needing structured approach

**Example:**
```python
from agents.meta2 import Meta2Agent

agent = Meta2Agent()
framework = agent.generate(
    domain="database query optimization",
    depth_levels=5,
    categorical_framework="natural_equivalence"
)
```

**Location:** `meta2/`
**Documentation:** [meta2/README.md](meta2/README.md)

---

### MARS (Multi-Agent Research Synthesis)

**Purpose:** Orchestrate complex multi-domain operations requiring systems-level intelligence.

**Capabilities:**
- Parallel research across multiple domains
- Strategic decomposition of complex problems
- Integrated framework synthesis
- Organizational blueprint generation
- SpaceX-level innovation patterns

**When to use:**
- Complex multi-domain research needed
- Strategic organizational challenges
- Need parallel discovery and synthesis
- Systems-level optimization required

**Operations:**
- `research` - Parallel discovery
- `synthesize` - Integration
- `apply` - Real-world mapping
- `optimize` - Leverage points
- `validate` - Constraint testing
- `iterate` - Learning loops

**Example:**
```
Use MARS agent to:
1. Research meta-prompting across 5 papers
2. Synthesize categorical foundations
3. Generate unified framework
4. Validate with concrete examples
```

**Location:** `MARS.md`
**Size:** 66KB (comprehensive)

---

### MERCURIO (Mixture of Experts Research Convergence)

**Purpose:** Multi-perspective agent providing integrated wisdom through mental, physical, and spiritual planes.

**Capabilities:**
- Three-plane analysis (mental, physical, spiritual)
- Ethical grounding with practical feasibility
- Intellectual rigor with moral awareness
- Complex decision-making support

**When to use:**
- Complex decisions requiring multiple perspectives
- Need ethical + practical + intellectual balance
- Strategic choice points
- Value-sensitive problems

**Planes:**
- **Mental:** Understanding, analysis, theory
- **Physical:** Execution, feasibility, practice
- **Spiritual:** Ethics, values, purpose

**Example:**
```
Use MERCURIO to:
- Evaluate framework design decisions
- Balance theoretical rigor with usability
- Ensure ethical AI practices
```

**Location:** `MERCURIO.md`
**Size:** 19KB

---

### mercurio-orchestrator

**Purpose:** Research synthesis and strategic orchestration with holistic understanding.

**Capabilities:**
- Comprehensive research synthesis
- Multi-dimensional task orchestration
- Deep knowledge integration
- Balances rigor with practical constraints

**When to use:**
- Beginning new research projects
- Complex multi-dimensional tasks
- Need holistic understanding
- Ethical considerations paramount

**Example:**
```
Use mercurio-orchestrator to:
1. Map knowledge landscape
2. Synthesize research across sources
3. Create comprehensive foundation
4. Ensure ethical alignment
```

**Location:** `mercurio-orchestrator.md`

---

## Agent Selection Matrix

| Need | Use Agent | Why |
|------|-----------|-----|
| Custom framework for domain | **meta2** | Universal generator |
| Multi-domain research | **MARS** | Parallel synthesis |
| Ethical decision-making | **MERCURIO** | Three-plane wisdom |
| Research synthesis | **mercurio-orchestrator** | Holistic integration |

---

## Integration Patterns

### Pattern 1: Research → Synthesize → Generate

```
1. MARS: Research meta-prompting papers
2. mercurio-orchestrator: Synthesize findings
3. meta2: Generate custom framework
```

### Pattern 2: Analyze → Decide → Implement

```
1. MERCURIO: Evaluate framework approaches
2. meta2: Generate selected framework
3. MARS: Validate across domains
```

### Pattern 3: Discovery → Framework → Deployment

```
1. meta2: Generate framework (unfamiliar domain)
   - Uses WebSearch for discovery
   - Creates N-level structure
2. MARS: Validate framework
   - Test across examples
   - Identify gaps
3. mercurio-orchestrator: Document
   - Create comprehensive guide
   - Synthesize learnings
```

---

## Theoretical Foundation

All agents ground in category theory principles:

- **Objects:** Tasks, prompts, frameworks, domains
- **Morphisms:** Transformations, refinements, specializations
- **Functors:** Level-to-level mappings
- **Natural Transformations:** Equivalences between approaches

**Key Theorem (Task-Agnosticity):** Meta-prompt morphisms exist for any task-category.

**Natural Equivalence:** `Hom(Y, Z^X) ≅ Hom(Y × X, Z)`

---

## Agent Composition

Agents can be composed for powerful workflows:

```python
# Example: Complete meta-prompting pipeline

# Phase 1: Research (MARS)
research = MARS.research(
    domain="quantum algorithms",
    sources=["papers", "docs", "examples"]
)

# Phase 2: Synthesis (mercurio-orchestrator)
synthesis = mercurio_orchestrator.synthesize(research)

# Phase 3: Framework (meta2)
framework = meta2.generate(
    domain="quantum algorithms",
    depth_levels=7,
    insights=synthesis
)

# Phase 4: Validation (MARS)
validated = MARS.validate(framework, examples)

# Phase 5: Ethical Review (MERCURIO)
final = MERCURIO.review(validated,
    dimensions=["correctness", "usability", "ethics"]
)
```

---

## See Also

- [Commands](../commands/README.md) - Slash commands
- [Meta-Prompts V2](../meta-prompts/v2/META_PROMPTS.md) - Production meta-prompts
- [Theory](../theory/) - Categorical foundations
- [Examples](../examples/) - Complete frameworks

---

**Making sophisticated meta-prompting accessible through specialized agents.** ✨
