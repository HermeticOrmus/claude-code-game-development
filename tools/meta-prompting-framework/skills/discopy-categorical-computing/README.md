# Discopy: Categorical Computing Skill

Comprehensive skill for using Discopy—Python's toolkit for category theory, string diagrams, and compositional computing.

## Quick Start

**Read First**: [SKILL.md](SKILL.md) - Main skill documentation

**Then Explore**:
- [EXAMPLES.md](EXAMPLES.md) - 12 production-ready code examples
- [REFERENCE.md](REFERENCE.md) - Quick API lookup
- [PATTERNS.md](PATTERNS.md) - Design patterns and best practices
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [INTEGRATION.md](INTEGRATION.md) - Using with other libraries

## What is Discopy?

Discopy operationalizes category theory through string diagrams, providing a unified framework for compositional systems across domains:

- **Quantum Natural Language Processing (QNLP)**: Text → Diagrams → Quantum Circuits
- **Compositional Semantics**: Formal models of meaning composition
- **Categorical Quantum Computing**: Quantum circuits as categorical morphisms
- **Tensor Network Computation**: Abstract tensor operations with multiple backends

## Core Concepts

```python
from discopy import Ty, Box

# Types (objects)
x, y = Ty('x'), Ty('y')

# Operations (morphisms)
f = Box('f', x, y)  # f: x → y

# Composition
f >> g  # Sequential (then)
f @ g   # Parallel (and)

# Interpretation (functors)
from discopy.matrix import Functor
F = Functor(ob={...}, ar={...})
result = F(diagram)
```

## File Structure

```
discopy-categorical-computing/
├── SKILL.md              # Main skill (START HERE)
├── EXAMPLES.md           # 12 production examples
│   ├── Level 1: Basic diagrams
│   ├── Level 2: Functors and evaluation
│   ├── Level 3: Quantum circuits
│   ├── Level 4: QNLP pipeline
│   └── Level 5: Advanced categories
├── REFERENCE.md          # API quick reference
│   ├── Core types (Ty, Box, Diagram)
│   ├── Functors (Matrix, Custom)
│   ├── Quantum module (Circuit, gates)
│   ├── Grammar module
│   └── Common patterns cheat sheet
├── PATTERNS.md           # Design patterns
│   ├── Architectural patterns
│   ├── Functor patterns
│   ├── Circuit design patterns
│   ├── Performance patterns
│   └── Anti-patterns to avoid
├── TROUBLESHOOTING.md    # Solutions to common issues
│   ├── Installation issues
│   ├── Type errors
│   ├── Functor evaluation errors
│   ├── Circuit construction issues
│   └── Integration problems
├── INTEGRATION.md        # Library integration guide
│   ├── NLP libraries (Lambeq, spaCy)
│   ├── Quantum frameworks (Qiskit, Cirq, PennyLane)
│   ├── ML frameworks (PyTorch, JAX, TensorFlow)
│   └── Production deployment
└── README.md             # This file
```

## Learning Path

### Beginner (Start Here)

1. Read [SKILL.md](SKILL.md) - Overview and core concepts
2. Run examples in [EXAMPLES.md](EXAMPLES.md) - Start with Level 1
3. Install Discopy: `pip install discopy`
4. Build your first diagram:
   ```python
   from discopy import Ty, Box
   x, y = Ty('x'), Ty('y')
   f = Box('f', x, y)
   diagram = f >> f.dagger()
   diagram.draw()
   ```

### Intermediate

1. Study [PATTERNS.md](PATTERNS.md) - Learn design patterns
2. Work through Level 2-3 examples in [EXAMPLES.md](EXAMPLES.md)
3. Build custom functor for your domain
4. Create quantum circuits categorically
5. Use [REFERENCE.md](REFERENCE.md) for API lookup

### Advanced

1. Level 4-5 examples in [EXAMPLES.md](EXAMPLES.md)
2. Complete QNLP pipeline
3. Implement traced categories with feedback
4. Integrate with ML frameworks ([INTEGRATION.md](INTEGRATION.md))
5. Deploy in production

## When to Use This Skill

✅ **Good For**:
- Compositional semantics research
- QNLP experiments
- Quantum circuit design
- Category theory education
- Formal grammar implementation
- Tensor network computation
- Diagrammatic reasoning
- Research prototyping

❌ **Not For**:
- Production NLP systems (use spaCy/Transformers)
- Large-scale quantum compilation (use Qiskit/Cirq)
- Standard ML pipelines (use PyTorch/scikit-learn)
- High-performance numerics (use NumPy/SciPy directly)

## Example: Hello World

```python
from discopy import Ty, Box
from discopy.matrix import Functor
import numpy as np

# 1. Define types
x, y, z = Ty('x'), Ty('y'), Ty('z')

# 2. Define operations
f = Box('f', x, y)
g = Box('g', y, z)

# 3. Compose
diagram = f >> g

# 4. Define semantics
F = Functor(
    ob={x: 2, y: 3, z: 4},
    ar={
        f: np.random.rand(3, 2),
        g: np.random.rand(4, 3)
    }
)

# 5. Evaluate
result = F(diagram)
print(f"Shape: {result.array.shape}")  # (4, 2)
```

## Example: Quantum Circuit

```python
from discopy.quantum.circuit import Circuit, gates, Ket

# Bell state
bell = (
    Ket(0, 0)
    >> (gates.H @ Circuit.id(1))
    >> gates.CNOT
)

# Visualize
bell.draw()

# Evaluate
result = bell.eval()
print(f"State: {result.array}")
```

## Installation

```bash
# Basic
pip install discopy

# With quantum features
pip install discopy[quantum]

# With all backends
pip install discopy[pytorch,jax,tensorflow]
```

## Philosophy

Discopy embodies **composition over decomposition**:

- **Traditional**: Break problems into parts
- **Compositional**: Build solutions from composable pieces

Benefits:
- **Formal Guarantees**: Category laws ensure correctness
- **Visual Reasoning**: Diagrams make structure explicit
- **Backend Flexibility**: Same diagram, multiple interpretations
- **Mathematical Rigor**: Proofs about correctness possible

## Resources

- **Discopy Docs**: https://docs.discopy.org
- **Paper**: "DisCoPy: Monoidal Categories in Python" (ACT 2021)
- **GitHub**: https://github.com/discopy/discopy
- **This Skill**: Complete guide with examples, patterns, troubleshooting

## Quick Reference Card

| Operation | Syntax | Meaning |
|-----------|--------|---------|
| Sequential composition | `f >> g` | f then g |
| Parallel composition | `f @ g` | f and g |
| Identity | `Box.id(x)` | Identity on x |
| Dagger | `f.dagger()` | Adjoint/inverse |
| Tensor product | `f.tensor(g)` | Explicit parallel |
| Evaluation | `F(diagram)` | Apply functor |
| Drawing | `diagram.draw()` | Visualize |

## Next Steps

1. **Read**: [SKILL.md](SKILL.md) for overview
2. **Code**: Run examples from [EXAMPLES.md](EXAMPLES.md)
3. **Reference**: Use [REFERENCE.md](REFERENCE.md) for API lookup
4. **Learn**: Study patterns in [PATTERNS.md](PATTERNS.md)
5. **Build**: Create custom functors for your domain
6. **Integrate**: Check [INTEGRATION.md](INTEGRATION.md) for your stack
7. **Debug**: Use [TROUBLESHOOTING.md](TROUBLESHOOTING.md) when stuck

## Contributing

This skill is part of the Claude Code skills system. To improve it:

1. Test examples and report issues
2. Add more domain-specific patterns
3. Contribute integration guides
4. Share your use cases

## License

This skill documentation follows Discopy's BSD-3-Clause license.

---

**Start your journey**: Open [SKILL.md](SKILL.md) and begin with the Quick Start section!
