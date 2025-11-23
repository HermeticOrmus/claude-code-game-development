---
name: discopy-categorical-computing
description: Category theory for compositional computing with string diagrams, quantum circuits, and QNLP. Covers monoidal categories, functors, tensor evaluation, and practical applications in quantum natural language processing and diagrammatic reasoning.
tags: [category-theory, quantum-computing, nlp, qnlp, string-diagrams, compositional-semantics, tensor-networks, python]
version: 1.0.0
---

# Discopy: Categorical Computing with String Diagrams

## When to Use This Skill

Use Discopy when you need:

- **Compositional Systems**: Building modular systems with formal composition guarantees
- **Quantum NLP (QNLP)**: Converting natural language to quantum circuits via categorical semantics
- **Diagrammatic Reasoning**: Visual representation of computational flows with mathematical rigor
- **Tensor Network Computation**: Abstract tensor operations with multiple backend support
- **Categorical Quantum Mechanics**: Designing and optimizing quantum circuits categorically
- **Research Prototyping**: Rapid experimentation with compositional models
- **Category Theory Education**: Executable mathematical concepts with visualization

**Sweet Spot**: Research at the mathematics-computer science interface, QNLP experiments, compositional semantics modeling, and educational tools for category theory.

**Not For**: Production NLP systems (use spaCy/Transformers), large-scale quantum compilation (use Qiskit/Cirq), or standard ML pipelines (use PyTorch/scikit-learn).

## Core Concepts

### The Big Picture: Information Plumbing

Discopy treats computation as **information flow through typed channels**:

- **Wires** = Types (information channels)
- **Boxes** = Operations (transformations)
- **Diagrams** = Compositions (pipelines)
- **Functors** = Interpretations (semantics)

```
Text → Parse → Diagram → Functor → Tensor/Circuit → Evaluate → Result
```

### Category Hierarchy

```
Category (objects + morphisms)
  ↓
Monoidal (>> sequential, @ parallel)
  ↓
Symmetric (swap wires)
  ↓
Rigid (duals)
  ↓
Compact (cups/caps)
  ↓
Traced (feedback loops)
```

Each level adds capabilities while maintaining composition guarantees.

### Key Operations

```python
# Sequential composition (then)
f >> g  # "f then g"

# Parallel composition (and)
f @ g   # "f and g simultaneously"

# Dagger (adjoint/inverse)
f.dagger()

# Tensor product
f.tensor(g)

# Feedback
f.feedback()
```

## Quick Start

### Installation

```bash
# Basic installation
pip install discopy

# With quantum features
pip install discopy[quantum]

# With all backends
pip install discopy[pytorch,tensorflow,jax]
```

### Hello World: Simple Composition

```python
from discopy import Ty, Box

# Define types (objects)
x = Ty('X')
y = Ty('Y')
z = Ty('Z')

# Define operations (morphisms)
f = Box('f', x, y)  # f: X → Y
g = Box('g', y, z)  # g: Y → Z

# Sequential composition
diagram = f >> g  # X → Y → Z

# Parallel composition
parallel = f @ g  # X⊗Y → Y⊗Z

# Visualize
diagram.draw()
```

### Tensor Evaluation

```python
from discopy.matrix import Functor
import numpy as np

# Define semantics
F = Functor(
    ob={x: 2, y: 3, z: 4},  # Dimensions
    ar={
        f: np.random.rand(3, 2),  # Y=3, X=2
        g: np.random.rand(4, 3)   # Z=4, Y=3
    }
)

# Evaluate
result = F(diagram)
print(result.array.shape)  # (4, 2)
```

### Quantum Circuit

```python
from discopy.quantum.circuit import Circuit, gates

# Build circuit
circuit = (
    gates.H @ Circuit.id(1)  # Hadamard on qubit 0
    >> gates.CNOT            # CNOT on qubits 0,1
    >> gates.Rx(0.5) @ gates.Ry(0.3)  # Rotations
)

# Visualize
circuit.draw()

# Export to other frameworks
qiskit_circuit = circuit.to_qiskit()
```

## Progressive Disclosure: 7-Level Framework

DisCoPy follows a **7-level progression** from simple pipelines to formally verified systems.

### Level 1: Novice - Sequential Composition
→ [EXAMPLES-L1-L2.md](EXAMPLES-L1-L2.md#level-1-novice---sequential-composition) - Basic `>>` pipelines
- **Core**: Chain operations sequentially
- **Use Cases**: ETL, image preprocessing, API chains
- **Examples**: 5 complete implementations with diagrams

### Level 2: Competent - Parallel Composition + Functors
→ [EXAMPLES-L1-L2.md](EXAMPLES-L1-L2.md#level-2-competent---parallel-composition--functors) - Parallel `@` + evaluation
- **Core**: Parallel operations, concrete tensor evaluation
- **Use Cases**: Ensemble ML, feature extraction, backend selection
- **Examples**: 7 complete implementations with NumPy/PyTorch

### Level 3: Proficient - Symmetric Monoidal (Wire Swapping)
→ [EXAMPLES-L3-L4.md](EXAMPLES-L3-L4.md#level-3-proficient---symmetric-monoidal-wire-swapping) - `Diagram.swap()` for routing
- **Core**: Type-aware composition, argument reordering
- **Use Cases**: Microservices routing, flexible composition
- **Examples**: 5 complete implementations with braiding

### Level 4: Advanced - Compact Closed (Quantum)
→ [EXAMPLES-L3-L4.md](EXAMPLES-L3-L4.md#level-4-advanced---compact-closed-quantum-circuits) - Cups, caps, quantum circuits
- **Core**: Duality, entanglement, QNLP
- **Use Cases**: Quantum computing, quantum NLP
- **Examples**: 7 complete quantum circuit implementations

### Level 5: Expert - Traced Monoidal (Feedback Loops)
→ [EXAMPLES-L5-L7.md](EXAMPLES-L5-L7.md#level-5-expert---traced-monoidal-feedback-loops) - `.trace()` for state feedback
- **Core**: RNNs, iterative algorithms, stateful workflows
- **Use Cases**: LSTMs, RL agents, game loops
- **Examples**: 5 complete implementations with traced categories

### Level 6: Master - Custom Functors & Multi-Backend
→ [EXAMPLES-L5-L7.md](EXAMPLES-L5-L7.md#level-6-master---custom-functors--multi-backend) - GPU acceleration, custom semantics
- **Core**: Backend selection (NumPy/PyTorch/JAX), custom functor logic
- **Use Cases**: Production ML, GPU inference, A/B testing
- **Examples**: 5 complete implementations with benchmarks

### Level 7: Genius - Formal Verification
→ [EXAMPLES-L5-L7.md](EXAMPLES-L5-L7.md#level-7-genius---formal-verification) - Proof-carrying code
- **Core**: Runtime assertions, type-level proofs, Coq verification
- **Use Cases**: Safety-critical, medical devices, smart contracts
- **Examples**: 4 complete implementations with proofs

### Real-World Applications
→ [USE-CASES.md](USE-CASES.md) - Complete use cases across all levels
- ETL pipelines, ML ensembles, quantum computing
- RNNs/LSTMs, production ML, verified systems
- Decision tree for level selection

## Common Patterns

### Pattern 1: Build-Interpret-Evaluate

```python
# 1. Build diagram (syntax)
diagram = f >> g >> h

# 2. Define functor (semantics)
functor = Functor(ob={...}, ar={...})

# 3. Evaluate
result = functor(diagram)
```

### Pattern 2: Grammar to Circuit

```python
# 1. Parse text
from discopy.grammar.pregroup import Diagram as Grammar

sentence = parse("Alice loves Bob")

# 2. Convert to quantum
from discopy.quantum.circuit import Functor as CircuitFunctor

to_circuit = CircuitFunctor(word_circuits, grammar_ops)
circuit = to_circuit(sentence)

# 3. Execute
result = circuit.eval()
```

### Pattern 3: Custom Domain Functor

```python
class DomainFunctor(Functor):
    def __init__(self, domain_mappings):
        self.mappings = domain_mappings

    def __call__(self, diagram):
        # Custom interpretation logic
        return self.interpret(diagram)
```

## API Quick Reference

→ [REFERENCE.md](REFERENCE.md) - Complete API lookup

## Best Practices

→ [PATTERNS.md](PATTERNS.md) - Design patterns and idioms

## Troubleshooting

→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions

## Integration Guide

→ [INTEGRATION.md](INTEGRATION.md) - Using Discopy with other libraries

## Learning Path

1. **Start Here**: Run examples in [EXAMPLES.md](EXAMPLES.md)
2. **Understand Types**: Read about Ty and type composition
3. **Master Functors**: Learn evaluation patterns
4. **Build Circuits**: Explore quantum module
5. **Try QNLP**: Complete pipeline example
6. **Create Custom**: Implement domain-specific functors
7. **Optimize**: Learn tensor backend selection

## When NOT to Use Discopy

❌ **Production NLP**: Use spaCy, Transformers (Discopy is research-focused)
❌ **Large Quantum Circuits**: Use Qiskit, Cirq (better optimization)
❌ **Standard Deep Learning**: Use PyTorch, TensorFlow directly
❌ **High-Performance Numerics**: Use NumPy, SciPy (less overhead)
❌ **Commercial Applications**: Wait for hardware maturity (QNLP still experimental)

## Philosophy: Composition Over Decomposition

Discopy inverts traditional programming:

- **Traditional**: Break problems down into parts
- **Compositional**: Build solutions from composable pieces

The categorical approach provides:
- **Formal Guarantees**: Composition laws ensure correctness
- **Visual Reasoning**: Diagrams make structure explicit
- **Backend Flexibility**: Same diagram, multiple interpretations
- **Mathematical Rigor**: Proofs about correctness possible

## Resources

- **Documentation**: https://docs.discopy.org
- **Paper**: "DisCoPy: Monoidal Categories in Python" (ACT 2021)
- **Tutorials**: [EXAMPLES.md](EXAMPLES.md) in this skill
- **API Reference**: [REFERENCE.md](REFERENCE.md)
- **Integration**: [INTEGRATION.md](INTEGRATION.md)

## Next Steps

1. Install: `pip install discopy`
2. Run: Examples in [EXAMPLES.md](EXAMPLES.md)
3. Explore: Modify examples for your domain
4. Build: Create custom functors
5. Share: Contribute back to community
