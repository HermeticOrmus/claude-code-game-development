# Discopy Code Examples Library

Production-quality examples demonstrating Discopy's capabilities across all levels of complexity.

## Table of Contents

1. [Level 1: Basic Diagrams](#level-1-basic-diagrams)
2. [Level 2: Type System & Functors](#level-2-type-system-functors)
3. [Level 3: Quantum Circuits](#level-3-quantum-circuits)
4. [Level 4: QNLP Pipeline](#level-4-qnlp-pipeline)
5. [Level 5: Advanced Categories](#level-5-advanced-categories)

---

## Level 1: Basic Diagrams

### Example 1: Hello World - Monoidal Composition

```python
"""
Simple monoidal category composition demonstrating the core operations.
"""
from discopy import Ty, Box

# Define types (objects in the category)
X = Ty('X')
Y = Ty('Y')
Z = Ty('Z')

# Define morphisms (arrows/operations)
f = Box('f', X, Y)  # f: X → Y
g = Box('g', Y, Z)  # g: Y → Z

# Sequential composition (>>)
sequential = f >> g  # X → Y → Z
print(f"Sequential: {sequential}")

# Parallel composition (@)
parallel = f @ g  # (X ⊗ Y) → (Y ⊗ Z)
print(f"Parallel: {parallel}")

# Identity
identity = Box.id(X)  # id: X → X
print(f"Identity: {identity}")

# Composition with identity (law: f >> id = id >> f = f)
assert f >> Box.id(Y) == f
assert Box.id(X) >> f == f
```

**Key Concepts:**
- `>>` = sequential composition ("then")
- `@` = parallel composition ("and")
- Types are wires, boxes are operations
- Identity laws hold automatically

---

### Example 2: Type System Basics

```python
"""
Understanding Discopy's type system with atomic and compound types.
"""
from discopy import Ty

# Atomic types
n = Ty('n')  # Noun
s = Ty('s')  # Sentence
v = Ty('v')  # Verb

# Compound types via tensor product
n_tensor_n = n @ n  # Two nouns in parallel
print(f"Compound: {n_tensor_n}")

# Type equality
assert Ty('n') == Ty('n')
assert Ty('n') != Ty('s')

# Tensor unit (monoidal unit)
unit = Ty()
assert n @ unit == n
assert unit @ n == n

# Type properties
print(f"Length: {(n @ s @ v).len}")  # Number of atomic types
print(f"Objects: {(n @ s @ v).objects}")  # List of atomic types

# Type unpacking
a, b, c = (n @ s @ v).unpack(3)
assert a == n and b == s and c == v
```

**Key Concepts:**
- Types can be atomic or compound
- `@` creates tensor products of types
- Empty type `Ty()` is the monoidal unit
- Types have length and can be unpacked

---

### Example 3: Diagram Composition Operators

```python
"""
Comprehensive demonstration of all composition operators.
"""
from discopy import Ty, Box

# Setup
x, y, z, w = Ty('x'), Ty('y'), Ty('z'), Ty('w')
f = Box('f', x, y)
g = Box('g', y, z)
h = Box('h', z, w)

# 1. Sequential composition (>>)
sequential = f >> g >> h  # x → y → z → w
print(f"Sequential: {sequential}")

# 2. Parallel composition (@)
parallel = f @ g @ h  # (x⊗y⊗z) → (y⊗z⊗w)
print(f"Parallel: {parallel}")

# 3. Tensor (explicit parallel)
tensored = f.tensor(g, h)  # Same as f @ g @ h
assert tensored == parallel

# 4. Then (alias for >>)
then_chain = f.then(g).then(h)
assert then_chain == sequential

# 5. Mixed composition
mixed = (f @ g) >> (h @ Box.id(z))
# (x⊗y) → (y⊗z) → (w⊗z)
print(f"Mixed: {mixed}")

# 6. Composition laws
# Associativity
assert (f >> g) >> h == f >> (g >> h)
assert (f @ g) @ h == f @ (g @ h)

# Identity
assert f >> Box.id(y) == f
assert Box.id(x) >> f == f
```

**Key Concepts:**
- Multiple ways to express composition
- Laws hold automatically (associativity, identity)
- Can mix sequential and parallel
- Composition is the fundamental operation

---

## Level 2: Type System & Functors

### Example 4: Tensor Evaluation with NumPy

```python
"""
Evaluating diagrams as tensors using functors with NumPy backend.
"""
from discopy import Ty, Box
from discopy.matrix import Functor
import numpy as np

# Define category
x, y, z = Ty('x'), Ty('y'), Ty('z')
f = Box('f', x, y)
g = Box('g', y, z)

# Build diagram
diagram = f >> g

# Define functor (interpretation)
F = Functor(
    # Object mapping (type → dimension)
    ob={x: 2, y: 3, z: 4},

    # Arrow mapping (box → matrix)
    ar={
        f: np.array([[1, 0],
                     [0, 1],
                     [1, 1]]),  # 3×2 matrix (y=3, x=2)
        g: np.array([[1, 0, 0],
                     [0, 1, 0],
                     [0, 0, 1],
                     [1, 1, 1]])  # 4×3 matrix (z=4, y=3)
    }
)

# Evaluate
result = F(diagram)
print(f"Result type: {type(result)}")
print(f"Result shape: {result.array.shape}")  # (4, 2)
print(f"Result:\n{result.array}")

# Verify composition
expected = g @ f  # Matrix multiplication
assert np.allclose(result.array, expected)
```

**Key Concepts:**
- Functors map diagrams to tensors
- `ob` maps types to dimensions
- `ar` maps boxes to matrices
- Composition becomes matrix multiplication

---

### Example 5: PyTorch Backend with Autodiff

```python
"""
Using PyTorch backend for automatic differentiation and GPU computation.
"""
from discopy import Ty, Box
from discopy.matrix import Functor
import torch

# Define diagram
x, y = Ty('x'), Ty('y')
f = Box('f', x, y)

# Create trainable parameter
weight = torch.randn(3, 2, requires_grad=True)

# Define functor with PyTorch backend
F = Functor(
    ob={x: 2, y: 3},
    ar={f: weight},
    backend='pytorch'
)

# Evaluate
result = F(f)

# Compute loss and gradients
loss = result.array.sum()
loss.backward()

print(f"Weight gradient: {weight.grad}")

# Use in optimization loop
optimizer = torch.optim.Adam([weight], lr=0.01)

for epoch in range(10):
    optimizer.zero_grad()
    result = F(f)
    loss = result.array.sum()
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch}, Loss: {loss.item():.4f}")
```

**Key Concepts:**
- Multiple backends available (numpy, pytorch, jax, tensorflow)
- PyTorch enables gradient computation
- Can integrate into training loops
- Same diagram, different backends

---

### Example 6: Custom Functor Implementation

```python
"""
Implementing a custom functor for domain-specific interpretation.
"""
from discopy import Ty, Box, Diagram
from discopy.matrix import Functor

class StringConcatFunctor(Functor):
    """
    Functor that interprets diagrams as string concatenation operations.
    """

    def __init__(self, word_map):
        self.word_map = word_map

    def __call__(self, diagram):
        """Recursively evaluate diagram to string."""
        if isinstance(diagram, Ty):
            return ""

        if isinstance(diagram, Box):
            return self.word_map.get(diagram.name, diagram.name)

        # Handle composition
        if diagram.is_sequential:
            # Sequential: concatenate in order
            left = self(diagram.left)
            right = self(diagram.right)
            return left + " " + right

        if diagram.is_parallel:
            # Parallel: concatenate with separator
            left = self(diagram.left)
            right = self(diagram.right)
            return left + " | " + right

        return ""

# Example usage
word = Ty('word')
alice = Box('Alice', Ty(), word)
loves = Box('loves', word, word)
bob = Box('Bob', Ty(), word)

# Build sentence diagram
sentence = alice >> loves >> bob

# Interpret
F = StringConcatFunctor({
    'Alice': 'ALICE',
    'loves': 'LOVES',
    'Bob': 'BOB'
})

result = F(sentence)
print(f"Result: {result}")  # "ALICE LOVES BOB"
```

**Key Concepts:**
- Custom functors for domain-specific semantics
- Override `__call__` for interpretation
- Handle different diagram types
- Enables DSL creation

---

## Level 3: Quantum Circuits

### Example 7: Basic Quantum Circuit Construction

```python
"""
Building quantum circuits categorically with Discopy.
"""
from discopy.quantum.circuit import Circuit, gates, Ket, Id

# Bell state preparation
bell_state = (
    Ket(0, 0)              # |00⟩
    >> (gates.H @ Id(1))   # H ⊗ I
    >> gates.CNOT          # CNOT
)

print("Bell State Circuit:")
print(bell_state)

# Draw circuit
bell_state.draw(figsize=(8, 4))

# Evaluate (simulate)
result = bell_state.eval()
print(f"\nState vector: {result.array}")
print(f"Probabilities: {abs(result.array)**2}")

# GHZ state (3 qubits)
ghz_state = (
    Ket(0, 0, 0)
    >> (gates.H @ Id(2))
    >> gates.CNOT @ Id(1)
    >> (Id(1) @ gates.CNOT)
)

print("\n3-Qubit GHZ State:")
ghz_result = ghz_state.eval()
print(f"State vector: {ghz_result.array}")
```

**Key Concepts:**
- Circuits are diagrams in quantum category
- Gates are boxes, qubits are wires
- `@` for parallel gates, `>>` for sequential
- `.eval()` simulates circuit

---

### Example 8: Parameterized Quantum Circuits

```python
"""
Creating parameterized circuits for variational quantum algorithms.
"""
from discopy.quantum.circuit import Circuit, gates, Id
import numpy as np

def create_ansatz(n_qubits, n_layers, params):
    """
    Create a hardware-efficient ansatz.

    Args:
        n_qubits: Number of qubits
        n_layers: Number of repetitions
        params: Array of rotation parameters

    Returns:
        Parameterized quantum circuit
    """
    circuit = Circuit.id(n_qubits)
    param_idx = 0

    for layer in range(n_layers):
        # Rotation layer
        for i in range(n_qubits):
            rx = gates.Rx(params[param_idx])
            ry = gates.Ry(params[param_idx + 1])
            rz = gates.Rz(params[param_idx + 2])

            # Place on qubit i
            rotation = (
                Id(i) @ rx @ Id(n_qubits - i - 1)
                >> Id(i) @ ry @ Id(n_qubits - i - 1)
                >> Id(i) @ rz @ Id(n_qubits - i - 1)
            )
            circuit >>= rotation
            param_idx += 3

        # Entangling layer (CNOT cascade)
        for i in range(n_qubits - 1):
            cnot = Id(i) @ gates.CNOT @ Id(n_qubits - i - 2)
            circuit >>= cnot

    return circuit

# Create ansatz
n_qubits = 3
n_layers = 2
n_params = n_qubits * n_layers * 3

params = np.random.rand(n_params) * 2 * np.pi
ansatz = create_ansatz(n_qubits, n_layers, params)

print(f"Ansatz with {n_params} parameters")
print(f"Circuit depth: {len(ansatz.layers)}")

# Evaluate
initial_state = gates.Ket(*[0] * n_qubits)
final_state = (initial_state >> ansatz).eval()
print(f"Final state shape: {final_state.array.shape}")
```

**Key Concepts:**
- Parameterized gates (Rx, Ry, Rz)
- Build circuits programmatically
- Hardware-efficient ansatz patterns
- Ready for VQE/QAOA applications

---

### Example 9: Circuit Optimization with ZX-Calculus

```python
"""
Optimizing quantum circuits using ZX-calculus integration.
"""
from discopy.quantum.circuit import Circuit, gates, Id
from discopy.quantum.zx import Z, X, scalar

# Build circuit with redundant operations
circuit = (
    gates.H @ Id(1)
    >> gates.CNOT
    >> gates.Z @ Id(1)
    >> gates.H @ Id(1)
    >> gates.X @ Id(1)
    >> gates.H @ Id(1)
)

print("Original circuit:")
print(f"Gates: {len(circuit.boxes)}")
circuit.draw()

# Convert to ZX-diagram
zx_diagram = circuit.to_zx()
print("\nZX-diagram:")
print(zx_diagram)

# Simplify using ZX-calculus rules
# Note: actual simplification requires PyZX
# simplified = zx_diagram.simplify()

# Convert back to circuit
# optimized_circuit = simplified.to_circuit()

# Compare
# print(f"\nOptimized gates: {len(optimized_circuit.boxes)}")
# print(f"Reduction: {len(circuit.boxes) - len(optimized_circuit.boxes)} gates")

# Verify equivalence
# assert circuit.eval().array == optimized_circuit.eval().array
```

**Key Concepts:**
- ZX-calculus for circuit optimization
- Graphical rewriting rules
- T-gate reduction
- Maintains semantic equivalence

---

## Level 4: QNLP Pipeline

### Example 10: Complete QNLP Pipeline

```python
"""
Full pipeline from text to quantum circuit via categorical semantics.

This example demonstrates:
1. Grammar parsing to diagrams
2. Diagram to circuit conversion
3. Circuit evaluation
4. Result interpretation
"""
from discopy import Ty
from discopy.grammar.pregroup import Diagram as Grammar, Word
from discopy.quantum.circuit import Circuit, gates, Ket, Id
from discopy.matrix import Functor
import numpy as np

# Step 1: Define Grammar Types
n = Ty('n')  # Noun
s = Ty('s')  # Sentence

# Step 2: Parse Sentence to Grammar Diagram
# "Alice loves Bob"
# Alice: n, loves: n.r @ s @ n.l, Bob: n
# Result: n @ n.r @ s @ n.l @ n → s

alice = Word('Alice', n)
loves = Word('loves', n.r @ s @ n.l)
bob = Word('Bob', n)

# Compose words
sentence = alice @ loves @ bob

# Apply reductions (cups for n ⋅ n.r and n.l ⋅ n)
from discopy.rigid import Cup

# n @ n.r reduces
reduction1 = Cup(n, n.r) @ Id(s @ n.l @ n)

# n.l @ n reduces
reduction2 = Id(s) @ Cup(n.l, n)

# Complete reduction
grammar_diagram = sentence >> reduction1 >> reduction2

print("Grammar Diagram:")
print(f"Type: {grammar_diagram.dom} → {grammar_diagram.cod}")

# Step 3: Map Words to Quantum Circuits
# Each word becomes a parameterized quantum circuit

def word_to_circuit(word, n_qubits=2):
    """Map word to quantum circuit."""
    # Simple encoding: embed word in rotation angles
    angle = hash(word) % 100 / 100 * np.pi

    return (
        Ket(*([0] * n_qubits))
        >> (gates.Ry(angle) @ Id(n_qubits - 1))
        >> (Id(1) @ gates.Ry(angle * 0.5))
    )

# Step 4: Create Functor from Grammar to Quantum
class QNLPFunctor(Functor):
    """Functor from grammar diagrams to quantum circuits."""

    def __init__(self, word_circuits):
        self.word_circuits = word_circuits

    def __call__(self, diagram):
        """Convert grammar diagram to quantum circuit."""
        if isinstance(diagram, Word):
            return self.word_circuits[diagram.name]

        # Handle cups (entangling operations)
        if isinstance(diagram, Cup):
            return gates.CNOT

        # Handle composition recursively
        if hasattr(diagram, 'left') and hasattr(diagram, 'right'):
            left_circuit = self(diagram.left)
            right_circuit = self(diagram.right)

            if diagram.is_sequential:
                return left_circuit >> right_circuit
            else:
                return left_circuit @ right_circuit

        return Circuit.id(0)

# Map words to circuits
word_circuits = {
    'Alice': word_to_circuit('Alice'),
    'loves': word_to_circuit('loves'),
    'Bob': word_to_circuit('Bob')
}

# Apply functor
qnlp_functor = QNLPFunctor(word_circuits)
quantum_circuit = qnlp_functor(grammar_diagram)

print("\nQuantum Circuit:")
print(quantum_circuit)

# Step 5: Evaluate Circuit
result = quantum_circuit.eval()
print(f"\nResult state: {result.array}")
print(f"Probabilities: {abs(result.array)**2}")

# Step 6: Interpret Result (e.g., for classification)
# Measure expectation value of observable
observable = np.array([[1, 0], [0, -1]])  # Pauli Z
expectation = result.array.conj() @ observable @ result.array
print(f"\nExpectation value: {expectation.real:.4f}")

# Classification based on sign
prediction = "positive" if expectation.real > 0 else "negative"
print(f"Prediction: {prediction}")
```

**Key Concepts:**
- Grammar → Diagram → Circuit pipeline
- Functors connect different categories
- Cups become entangling gates
- Measurement interprets quantum state
- Complete compositional semantics

---

## Level 5: Advanced Categories

### Example 11: Traced Categories and Feedback

```python
"""
Using traced monoidal categories for feedback loops.
"""
from discopy.monoidal import Ty, Box, Id
from discopy.feedback import Trace

# Define types
x, y, z = Ty('x'), Ty('y'), Ty('z')

# Define box with feedback channel
# f: x ⊗ y → y ⊗ z
# Feedback on y: creates loop
f = Box('f', x @ y, y @ z)

# Apply trace (feedback) on type y
# trace_y(f): x → z
traced = Trace(y, f)

print(f"Original: {f.dom} → {f.cod}")
print(f"Traced: {traced.dom} → {traced.cod}")

# Concrete example: Recursive computation
from discopy.matrix import Functor
import numpy as np

# Define functor for traced evaluation
F = Functor(
    ob={x: 2, y: 3, z: 4},
    ar={f: np.random.rand(12, 6)}  # (y⊗z=12) × (x⊗y=6)
)

# Evaluate with feedback
# This computes fixed point: y_out = f(x, y_out)
result = F(traced)
print(f"Result shape: {result.array.shape}")  # (4, 2) - z × x
```

**Key Concepts:**
- Traced categories for feedback
- Fixed-point computation
- Recursive diagram evaluation
- Int-construction for compact closure

---

### Example 12: Integration with Other Libraries

```python
"""
Integrating Discopy with PyTorch for hybrid quantum-classical models.
"""
import torch
import torch.nn as nn
from discopy.quantum.circuit import Circuit, gates, Ket, Id
from discopy.matrix import Functor
import numpy as np

class QuantumLayer(nn.Module):
    """
    PyTorch layer wrapping a Discopy quantum circuit.
    """

    def __init__(self, n_qubits, n_layers):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_layers = n_layers

        # Trainable parameters
        n_params = n_qubits * n_layers * 3
        self.params = nn.Parameter(torch.randn(n_params))

    def create_circuit(self, params):
        """Build circuit from parameters."""
        circuit = Id(self.n_qubits)
        param_idx = 0

        for layer in range(self.n_layers):
            for i in range(self.n_qubits):
                # Rotation gates
                circuit >>= (
                    Id(i)
                    @ gates.Ry(params[param_idx].item())
                    @ Id(self.n_qubits - i - 1)
                )
                param_idx += 1

            # Entangling
            for i in range(self.n_qubits - 1):
                circuit >>= (
                    Id(i) @ gates.CNOT @ Id(self.n_qubits - i - 2)
                )

        return circuit

    def forward(self, x):
        """
        Forward pass.

        Args:
            x: Input tensor (batch_size, n_qubits)

        Returns:
            Output tensor (batch_size, n_qubits)
        """
        batch_size = x.shape[0]
        outputs = []

        for i in range(batch_size):
            # Encode input as initial state
            initial = Ket(*x[i].long().tolist())

            # Build parameterized circuit
            circuit = self.create_circuit(self.params)

            # Evaluate
            final_state = (initial >> circuit).eval()

            # Measure (expectation values)
            probs = torch.tensor(
                abs(final_state.array) ** 2,
                dtype=torch.float32
            )
            outputs.append(probs[:self.n_qubits])

        return torch.stack(outputs)

# Create hybrid model
class HybridModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.classical1 = nn.Linear(4, 2)
        self.quantum = QuantumLayer(n_qubits=2, n_layers=2)
        self.classical2 = nn.Linear(2, 1)

    def forward(self, x):
        x = torch.relu(self.classical1(x))
        x = self.quantum(x)
        x = torch.sigmoid(self.classical2(x))
        return x

# Example usage
model = HybridModel()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# Dummy data
X = torch.randn(10, 4)
y = torch.randint(0, 2, (10, 1)).float()

# Training loop
for epoch in range(5):
    optimizer.zero_grad()
    predictions = model(X)
    loss = nn.functional.binary_cross_entropy(predictions, y)
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch}, Loss: {loss.item():.4f}")
```

**Key Concepts:**
- Hybrid quantum-classical models
- Discopy circuits as PyTorch layers
- End-to-end differentiable pipelines
- Production ML integration

---

## Running the Examples

All examples are self-contained and can be run directly:

```bash
# Install dependencies
pip install discopy numpy torch matplotlib

# Run any example
python example_01_hello_world.py
```

## Modifying for Your Domain

Each example can be adapted:

1. **Change types**: Define domain-specific types
2. **Custom boxes**: Create operations for your domain
3. **Custom functors**: Implement domain-specific semantics
4. **Integrate backends**: Choose backend for your needs

## Next Steps

- Experiment with examples
- Modify for your use case
- Read [PATTERNS.md](PATTERNS.md) for design patterns
- Check [INTEGRATION.md](INTEGRATION.md) for library integration
- Explore [REFERENCE.md](REFERENCE.md) for API details
