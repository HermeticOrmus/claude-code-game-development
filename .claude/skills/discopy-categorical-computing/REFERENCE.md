# Discopy API Quick Reference

Fast lookup for common Discopy operations and APIs.

## Core Types

### Ty (Type/Object)

```python
from discopy import Ty

# Create atomic type
x = Ty('x')

# Tensor product
x_tensor_y = Ty('x') @ Ty('y')
# Or: Ty('x', 'y')

# Empty type (monoidal unit)
unit = Ty()

# Properties
x.name          # 'x'
x.objects       # ['x']
x.len           # 1
(x @ y).len     # 2

# Unpacking
a, b, c = (Ty('a') @ Ty('b') @ Ty('c')).unpack(3)

# Duals (for rigid categories)
x.l  # Left dual
x.r  # Right dual
```

### Box (Morphism/Operation)

```python
from discopy import Box

# Create box
f = Box('f', dom=Ty('x'), cod=Ty('y'))
# f: x → y

# Properties
f.name          # 'f'
f.dom           # Domain (input type)
f.cod           # Codomain (output type)
f.free_symbols  # Free parameters (if any)

# Identity
id_x = Box.id(Ty('x'))

# Dagger (adjoint)
f_dagger = f.dagger()
# f†: y → x
```

### Diagram (Composition)

```python
from discopy import Diagram

# Sequential composition
f >> g  # f then g

# Parallel composition
f @ g   # f and g in parallel

# Tensor product
f.tensor(g, h)  # Same as f @ g @ h

# Then (alias for >>)
f.then(g)

# Properties
diagram.dom           # Domain type
diagram.cod           # Codomain type
diagram.boxes         # List of all boxes
diagram.layers        # List of layers
diagram.is_sequential # True if sequential composition
diagram.is_parallel   # True if parallel composition
diagram.left          # Left component
diagram.right         # Right component

# Visualization
diagram.draw(
    figsize=(10, 5),
    path='output.png',
    backend='matplotlib'  # or 'tikz'
)

# Equality
diagram1 == diagram2  # Structural equality
```

## Functors (Evaluation)

### Matrix Functor (Tensor Evaluation)

```python
from discopy.matrix import Functor
import numpy as np

# Define functor
F = Functor(
    ob={x: 2, y: 3},  # Type → dimension
    ar={f: np.random.rand(3, 2)},  # Box → matrix
    backend='numpy'  # or 'pytorch', 'jax', 'tensorflow'
)

# Evaluate diagram
result = F(diagram)

# Result properties
result.array         # Underlying array
result.dom           # Input dimension
result.cod           # Output dimension

# Backends
Functor(..., backend='numpy')      # NumPy (default)
Functor(..., backend='pytorch')    # PyTorch
Functor(..., backend='jax')        # JAX
Functor(..., backend='tensorflow') # TensorFlow
```

### Custom Functor

```python
from discopy.matrix import Functor

class MyFunctor(Functor):
    def __call__(self, diagram):
        # Custom evaluation logic
        if isinstance(diagram, Box):
            return self.evaluate_box(diagram)
        # Handle composition
        return super().__call__(diagram)

    def evaluate_box(self, box):
        # Domain-specific interpretation
        pass
```

## Quantum Module

### Circuit Construction

```python
from discopy.quantum.circuit import Circuit, gates, Ket, Bra, Id

# Initial states
Ket(0)           # |0⟩
Ket(1)           # |1⟩
Ket(0, 1)        # |01⟩
Ket(*bits)       # General

# Final states (for inner product)
Bra(0)           # ⟨0|

# Identity
Id(n_qubits)     # Identity on n qubits

# Composition
circuit = Ket(0, 0) >> (gates.H @ Id(1)) >> gates.CNOT
```

### Quantum Gates

```python
from discopy.quantum import gates

# Single-qubit gates
gates.H          # Hadamard
gates.X          # Pauli X (NOT)
gates.Y          # Pauli Y
gates.Z          # Pauli Z
gates.S          # Phase gate
gates.T          # π/8 gate
gates.Rx(theta)  # X rotation
gates.Ry(theta)  # Y rotation
gates.Rz(theta)  # Z rotation

# Two-qubit gates
gates.CNOT       # Controlled-NOT
gates.CZ         # Controlled-Z
gates.SWAP       # Swap gate
gates.CRx(theta) # Controlled-Rx
gates.CRy(theta) # Controlled-Ry
gates.CRz(theta) # Controlled-Rz

# Three-qubit gates
gates.Toffoli    # CCNOT
gates.Fredkin    # CSWAP

# Measurement
gates.Measure    # Computational basis measurement

# Properties
gate.array       # Matrix representation
gate.dagger()    # Adjoint gate
```

### Circuit Evaluation

```python
# Simulate circuit
result = circuit.eval(backend='numpy')

# Result is a state vector
result.array              # NumPy array
abs(result.array) ** 2    # Probabilities

# With specific backend
result = circuit.eval(backend='pytorch')  # Returns torch.Tensor
```

### Circuit Conversion

```python
# Export to other frameworks
qiskit_circuit = circuit.to_qiskit()
cirq_circuit = circuit.to_cirq()
pennylane_qnode = circuit.to_pennylane()

# Import from other frameworks
from_qiskit = Circuit.from_qiskit(qiskit_circuit)
```

### ZX-Calculus

```python
from discopy.quantum.zx import Z, X, scalar

# Convert circuit to ZX-diagram
zx_diagram = circuit.to_zx()

# ZX operations
Z(phase, n_inputs, n_outputs)  # Z spider
X(phase, n_inputs, n_outputs)  # X spider
scalar(phase)                   # Scalar

# Convert back to circuit
circuit = zx_diagram.to_circuit()

# Simplify (requires PyZX)
# simplified = zx_diagram.simplify()
```

## Grammar Module

### Pregroup Grammar

```python
from discopy.grammar.pregroup import Ty, Word, Cup, Id

# Define types
n = Ty('n')   # Noun
s = Ty('s')   # Sentence

# Words with types
alice = Word('Alice', n)
loves = Word('loves', n.r @ s @ n.l)
bob = Word('Bob', n)

# Sentence diagram
sentence = alice @ loves @ bob

# Reductions
reduction = Cup(n, n.r) @ Id(s @ n.l @ n)
reduced = sentence >> reduction

# Properties
word.name        # Word string
word.cod         # Word type
```

### Context-Free Grammar

```python
from discopy.grammar.cfg import CFG, Tree

# Define grammar
grammar = CFG(
    start='S',
    rules=[
        ('S', 'NP', 'VP'),
        ('NP', 'Alice'),
        ('VP', 'runs')
    ]
)

# Parse
tree = grammar.parse('Alice runs')

# Tree properties
tree.root        # Root symbol
tree.children    # Child trees
```

### Dependency Grammar

```python
from discopy.grammar.dependency import Dependency

# Create dependency
dep = Dependency('nsubj', 'loves', 'Alice')

# Properties
dep.head         # Head word
dep.dependent    # Dependent word
dep.relation     # Dependency relation
```

## Rigid Categories

### Cups and Caps

```python
from discopy.rigid import Cup, Cap, Ty, Id

# Define type
x = Ty('x')

# Cup (adjunction)
# x @ x.r → Ty()
cup = Cup(x, x.r)

# Cap (unit)
# Ty() → x.r @ x
cap = Cap(x.r, x)

# Snake equations (guaranteed to hold)
# (id_x @ cup) >> (cap @ id_x) == id_x
assert (Id(x) @ cup) >> (cap @ Id(x)) == Id(x)
```

### Pivotal and Ribbon Categories

```python
from discopy.ribbon import Twist

# Twist
twist_x = Twist(x)

# Properties
twist_x.dom      # x
twist_x.cod      # x
twist_x.dagger() # Inverse twist
```

## Drawing and Visualization

### Drawing Options

```python
# Basic drawing
diagram.draw()

# Custom size
diagram.draw(figsize=(12, 6))

# Save to file
diagram.draw(path='diagram.png')

# Backend selection
diagram.draw(backend='matplotlib')  # Matplotlib (default)
diagram.draw(backend='tikz')        # TikZ/LaTeX

# Advanced options
diagram.draw(
    figsize=(10, 5),
    fontsize=12,
    aspect='auto',
    margins=(0.1, 0.1),
    draw_type_labels=True,
    draw_box_labels=True
)
```

### Plane Graphs

```python
from discopy.drawing import PlaneGraph

# Get plane graph representation
graph = diagram.to_graph()

# Properties
graph.nodes      # Graph nodes
graph.edges      # Graph edges
graph.positions  # Node positions
```

## Hypergraph Categories

```python
from discopy.hypergraph import Hypergraph, Spider

# Create hypergraph diagram
hg = Hypergraph(
    dom=Ty('x', 'y'),
    cod=Ty('z'),
    boxes=[...],
    wires=[...]
)

# Spider (generalized box)
spider = Spider(n_legs_in=2, n_legs_out=3, type=Ty('x'))

# Conversion
diagram.to_hypergraph()  # Diagram → Hypergraph
hypergraph.to_diagram()  # Hypergraph → Diagram
```

## Traced Categories

```python
from discopy.feedback import Trace, Delay

# Apply trace (feedback)
# f: x @ y → y @ z
# Trace(y, f): x → z
traced = Trace(feedback_type, box)

# Delay (add feedback loop)
delayed = Delay(box)

# Fixed-point computation
result = functor(traced)  # Computes y = f(x, y)
```

## SymPy Integration

```python
from discopy import Ty, Box
from discopy.matrix import Functor
from sympy import Symbol, Matrix

# Symbolic parameters
theta = Symbol('theta')

# Symbolic box
f = Box('f', Ty('x'), Ty('y'), data=theta)

# Symbolic functor
F = Functor(
    ob={Ty('x'): 2, Ty('y'): 2},
    ar={f: Matrix([[Symbol('a'), Symbol('b')],
                   [Symbol('c'), Symbol('d')]])}
)

# Evaluate symbolically
result = F(diagram)
result.array  # SymPy Matrix with symbols
```

## Common Patterns Cheat Sheet

### Pattern: Build-Interpret-Evaluate

```python
# 1. Build
diagram = f >> g >> h

# 2. Interpret
functor = Functor(ob={...}, ar={...})

# 3. Evaluate
result = functor(diagram)
```

### Pattern: Quantum Ansatz

```python
def ansatz(n_qubits, n_layers, params):
    circuit = Id(n_qubits)
    for layer in range(n_layers):
        # Rotations
        for i in range(n_qubits):
            circuit >>= Id(i) @ gates.Ry(params[...]) @ Id(...)
        # Entangling
        for i in range(n_qubits - 1):
            circuit >>= Id(i) @ gates.CNOT @ Id(...)
    return circuit
```

### Pattern: Grammar to Quantum

```python
# 1. Parse to grammar diagram
grammar_diagram = parse(sentence)

# 2. Define functor
qnlp_functor = Functor(
    ob={n: 2, s: 2},  # Qubit dimensions
    ar={word: circuit_for_word(word) for word in vocab}
)

# 3. Convert
quantum_circuit = qnlp_functor(grammar_diagram)

# 4. Evaluate
result = quantum_circuit.eval()
```

### Pattern: Custom Domain

```python
class DomainDiagram(Diagram):
    def custom_method(self):
        # Domain-specific operations
        pass

class DomainFunctor(Functor):
    def __call__(self, diagram):
        # Domain-specific interpretation
        pass

# Usage
diagram = DomainDiagram(...)
functor = DomainFunctor(...)
result = functor(diagram)
```

## Performance Tips

### Backend Selection

```python
# NumPy: Simple, CPU-only
F = Functor(..., backend='numpy')

# PyTorch: Autodiff, GPU support
F = Functor(..., backend='pytorch')

# JAX: JIT compilation, functional
F = Functor(..., backend='jax')

# TensorFlow: Production ML
F = Functor(..., backend='tensorflow')
```

### Optimization

```python
# 1. Rewrite diagrams before evaluation
optimized = diagram.normalize()

# 2. Use hypergraph representation for symmetric categories
hg = diagram.to_hypergraph()
result = functor(hg.to_diagram())

# 3. Cache functor results
from functools import lru_cache

@lru_cache(maxsize=1000)
def evaluate(diagram_hash):
    return functor(diagram)
```

## Error Handling

### Common Exceptions

```python
# Type mismatch in composition
try:
    f >> g  # f.cod must equal g.dom
except ValueError as e:
    print(f"Type mismatch: {e}")

# Invalid functor mapping
try:
    F(diagram)  # All boxes must be in ar dict
except KeyError as e:
    print(f"Missing box mapping: {e}")

# Dimension mismatch
try:
    F = Functor(ob={x: 2}, ar={f: np.ones((3, 4))})
except ValueError as e:
    print(f"Dimension error: {e}")
```

### Debugging

```python
# Inspect diagram structure
print(f"Domain: {diagram.dom}")
print(f"Codomain: {diagram.cod}")
print(f"Boxes: {diagram.boxes}")
print(f"Layers: {len(diagram.layers)}")

# Visualize
diagram.draw()

# Check functor mappings
for box in diagram.boxes:
    if box.name in functor.ar:
        print(f"{box.name}: {functor.ar[box.name].shape}")
    else:
        print(f"{box.name}: MISSING")
```

## Resources

- **Full Documentation**: https://docs.discopy.org
- **API Reference**: https://docs.discopy.org/en/latest/api.html
- **Source Code**: https://github.com/discopy/discopy
- **Examples**: [EXAMPLES.md](EXAMPLES.md)
- **Patterns**: [PATTERNS.md](PATTERNS.md)
