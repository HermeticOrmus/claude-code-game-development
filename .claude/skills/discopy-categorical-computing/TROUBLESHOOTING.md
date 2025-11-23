# Discopy Troubleshooting Guide

Common issues and their solutions when working with Discopy.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Type Errors](#type-errors)
3. [Functor Evaluation Errors](#functor-evaluation-errors)
4. [Circuit Construction Issues](#circuit-construction-issues)
5. [Performance Problems](#performance-problems)
6. [Visualization Issues](#visualization-issues)
7. [Integration Problems](#integration-problems)

---

## Installation Issues

### Issue: Import Error - Module Not Found

**Symptoms**:
```python
ImportError: No module named 'discopy'
```

**Solutions**:

1. **Install Discopy**:
```bash
pip install discopy
```

2. **Check Python version** (requires Python 3.8+):
```bash
python --version
```

3. **Install with specific extras**:
```bash
# For quantum features
pip install discopy[quantum]

# For all backends
pip install discopy[pytorch,jax,tensorflow]
```

4. **Use virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install discopy
```

---

### Issue: Optional Dependencies Missing

**Symptoms**:
```python
ImportError: No module named 'torch'
ImportError: No module named 'jax'
```

**Solutions**:

```bash
# Install specific backend
pip install torch
pip install jax jaxlib
pip install tensorflow

# Or install all at once
pip install discopy[pytorch,jax,tensorflow]
```

---

## Type Errors

### Issue: Type Mismatch in Composition

**Symptoms**:
```python
ValueError: Cannot compose f: x → y with g: z → w
# f.cod (y) doesn't match g.dom (z)
```

**Diagnosis**:
```python
# Check types
print(f"f: {f.dom} → {f.cod}")
print(f"g: {g.dom} → {g.cod}")

# For composition f >> g, need f.cod == g.dom
```

**Solutions**:

1. **Fix type alignment**:
```python
# Before (ERROR)
f = Box('f', x, y)
g = Box('g', z, w)
composed = f >> g  # Error!

# After (CORRECT)
f = Box('f', x, y)
g = Box('g', y, w)  # g.dom = y = f.cod
composed = f >> g  # Works!
```

2. **Add identity to adjust types**:
```python
from discopy import Id

# Insert identity to match types
f_extended = f @ Id(z)  # x⊗z → y⊗z
composed = f_extended >> g  # Now types match
```

3. **Debug with visualization**:
```python
# See types visually
f.draw()
g.draw()
```

---

### Issue: Empty Type Composition

**Symptoms**:
```python
# Unexpected behavior with Ty()
result = Ty()  # Empty type
```

**Solution**:

```python
# Empty type Ty() is the monoidal unit
assert Ty() @ x == x
assert x @ Ty() == x

# Use explicitly when needed
unit = Ty()
```

**Common Mistake**:
```python
# Creating type from empty string
wrong = Ty('')  # Creates Ty(''), not Ty()
correct = Ty()  # Empty type (monoidal unit)
```

---

### Issue: Type Unification in Rigid Categories

**Symptoms**:
```python
# Cups/caps not working as expected
cup = Cup(n, n.r)
# Type error when composing
```

**Solution**:

```python
from discopy.rigid import Ty, Cup, Cap, Id

# Ensure types and duals match
n = Ty('n')

# Cup: n ⊗ n.r → Ty()
cup = Cup(n, n.r)
assert cup.dom == n @ n.r
assert cup.cod == Ty()

# Cap: Ty() → n.r ⊗ n
cap = Cap(n.r, n)
assert cap.dom == Ty()
assert cap.cod == n.r @ n

# Snake equations must hold
snake = (Id(n) @ cap) >> (cup @ Id(n))
assert snake == Id(n)
```

---

## Functor Evaluation Errors

### Issue: Missing Box Mapping

**Symptoms**:
```python
KeyError: Box('unknown', Ty('x'), Ty('y'))
```

**Diagnosis**:
```python
# Check which boxes are missing
diagram_boxes = set(diagram.boxes)
functor_boxes = set(functor.ar.keys())
missing = diagram_boxes - functor_boxes
print(f"Missing mappings: {missing}")
```

**Solutions**:

1. **Add missing mappings**:
```python
import numpy as np

# Before (ERROR)
F = Functor(
    ob={x: 2, y: 3},
    ar={f: np.random.rand(3, 2)}
    # Missing mapping for g!
)

# After (CORRECT)
F = Functor(
    ob={x: 2, y: 3},
    ar={
        f: np.random.rand(3, 2),
        g: np.random.rand(4, 3)  # Added mapping
    }
)
```

2. **Use default functor**:
```python
# Functor with identity on unmapped boxes
class DefaultFunctor(Functor):
    def __call__(self, diagram):
        if isinstance(diagram, Box) and diagram not in self.ar:
            # Return identity matrix
            dim = self.ob[diagram.dom]
            return np.eye(dim)
        return super().__call__(diagram)
```

---

### Issue: Dimension Mismatch

**Symptoms**:
```python
ValueError: Matrix dimensions don't match type dimensions
# Expected (cod_dim, dom_dim), got (wrong_rows, wrong_cols)
```

**Diagnosis**:
```python
# Check dimensions
print(f"Type dims: {functor.ob}")
print(f"Box dims: {box.dom} → {box.cod}")
print(f"Matrix shape: {matrix.shape}")

# For box: dom → cod
# Matrix should be: (cod_dim, dom_dim)
```

**Solution**:
```python
# Correct dimension matching
x, y = Ty('x'), Ty('y')
f = Box('f', x, y)

F = Functor(
    ob={x: 2, y: 3},
    ar={
        f: np.random.rand(3, 2)  # (cod=3, dom=2) - CORRECT
        # NOT np.random.rand(2, 3)  # Would be wrong!
    }
)

# Verify
assert F.ar[f].shape == (F.ob[f.cod], F.ob[f.dom])
```

---

### Issue: Backend Incompatibility

**Symptoms**:
```python
TypeError: Cannot convert torch.Tensor to numpy array
```

**Solution**:

```python
# Ensure consistent backend
F = Functor(
    ob={x: 2, y: 3},
    ar={f: torch.randn(3, 2)},  # PyTorch tensor
    backend='pytorch'  # Specify backend!
)

# Don't mix backends
# BAD:
ar_mixed = {
    f: np.random.rand(3, 2),  # NumPy
    g: torch.randn(4, 3)       # PyTorch - Error!
}

# GOOD:
ar_consistent = {
    f: torch.randn(3, 2),
    g: torch.randn(4, 3)
}
```

---

## Circuit Construction Issues

### Issue: Qubit Indexing Errors

**Symptoms**:
```python
# Circuit doesn't match intended topology
# Gates applied to wrong qubits
```

**Solution**:

```python
from discopy.quantum.circuit import Id, gates

# Careful with indexing
n_qubits = 3

# Apply H to qubit 1 (middle qubit)
circuit = Id(1) @ gates.H @ Id(1)
# Id(1): skip qubit 0
# H: apply to qubit 1
# Id(1): skip qubit 2

# General pattern for gate on qubit i:
def apply_gate(gate, qubit, n_qubits):
    return (
        Id(qubit)
        @ gate
        @ Id(n_qubits - qubit - 1)
    )

# Use helper
h_on_qubit_1 = apply_gate(gates.H, 1, n_qubits)
```

---

### Issue: CNOT on Non-Adjacent Qubits

**Symptoms**:
```python
# CNOT only works on adjacent qubits
# Need to apply to qubits 0 and 2
```

**Solution**:

```python
# Use SWAP gates to make qubits adjacent
def cnot_distant(control, target, n_qubits):
    """CNOT between non-adjacent qubits."""
    if abs(control - target) == 1:
        # Adjacent - direct CNOT
        min_qubit = min(control, target)
        return Id(min_qubit) @ gates.CNOT @ Id(n_qubits - min_qubit - 2)

    # Non-adjacent - use SWAPs
    circuit = Id(n_qubits)

    # SWAP target next to control
    for i in range(target - 1, control, -1):
        circuit >>= Id(i) @ gates.SWAP @ Id(n_qubits - i - 2)

    # Apply CNOT
    circuit >>= Id(control) @ gates.CNOT @ Id(n_qubits - control - 2)

    # SWAP back
    for i in range(control + 1, target):
        circuit >>= Id(i) @ gates.SWAP @ Id(n_qubits - i - 2)

    return circuit

# Usage
cnot_0_2 = cnot_distant(control=0, target=2, n_qubits=3)
```

---

### Issue: Circuit Parameterization

**Symptoms**:
```python
# Parameters not updating in optimization
# Gradients not flowing
```

**Solution**:

```python
import torch

# Use torch.Tensor for parameters
params = torch.tensor([0.5, 1.0, 1.5], requires_grad=True)

# Create circuit with parameters
circuit = Id(2)
circuit >>= gates.Ry(params[0]) @ Id(1)
circuit >>= Id(1) @ gates.Ry(params[1])

# Evaluate with PyTorch backend
F = Functor(backend='pytorch')
result = F(circuit)

# Compute loss
loss = result.array.sum()
loss.backward()

# Access gradients
print(params.grad)
```

---

## Performance Problems

### Issue: Slow Functor Evaluation

**Symptoms**:
```python
# Evaluation takes too long
# Need to speed up
```

**Solutions**:

1. **Use appropriate backend**:
```python
# Small diagrams: NumPy (low overhead)
F_small = Functor(..., backend='numpy')

# Need gradients: PyTorch
F_grad = Functor(..., backend='pytorch')

# Large diagrams: JAX (JIT compilation)
F_large = Functor(..., backend='jax')
```

2. **Cache results**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_evaluation(diagram_hash):
    return functor(diagram)
```

3. **Batch evaluation**:
```python
# Evaluate multiple diagrams at once
results = [functor(d) for d in diagrams]

# Better: batch if possible
# (depends on diagram structure)
```

---

### Issue: Memory Usage Too High

**Symptoms**:
```python
MemoryError: Unable to allocate array
```

**Solutions**:

1. **Use sparse representations**:
```python
from scipy.sparse import csr_matrix

# For circuits with many qubits
# Use sparse matrices for gates
```

2. **Reduce tensor dimensions**:
```python
# Lower embedding dimensions
F = Functor(
    ob={x: 16, y: 16},  # Instead of 256
    ar={...}
)
```

3. **Clear cache periodically**:
```python
if hasattr(functor, 'clear_cache'):
    functor.clear_cache()
```

---

## Visualization Issues

### Issue: Diagram Not Displaying

**Symptoms**:
```python
# diagram.draw() does nothing
# No image appears
```

**Solutions**:

1. **Install matplotlib**:
```bash
pip install matplotlib
```

2. **Use explicit backend**:
```python
diagram.draw(backend='matplotlib')
```

3. **Save to file instead**:
```python
diagram.draw(path='diagram.png')
```

4. **Check Jupyter setup**:
```python
# In Jupyter notebook
%matplotlib inline
diagram.draw()
```

---

### Issue: TikZ Export Fails

**Symptoms**:
```python
# TikZ backend not working
```

**Solution**:

```python
# Install TikZ dependencies
# Requires LaTeX installation

# Use matplotlib instead
diagram.draw(backend='matplotlib')

# Or export TikZ code to file
tikz_code = diagram.to_tikz()
with open('diagram.tex', 'w') as f:
    f.write(tikz_code)
```

---

### Issue: Large Diagram Visualization

**Symptoms**:
```python
# Diagram too large to display clearly
# Overlapping boxes
```

**Solution**:

```python
# Increase figure size
diagram.draw(figsize=(20, 10))

# Adjust aspect ratio
diagram.draw(figsize=(30, 5), aspect='auto')

# Or simplify diagram first
simplified = diagram.normalize()
simplified.draw()
```

---

## Integration Problems

### Issue: Lambeq Compatibility

**Symptoms**:
```python
# Diagrams from Lambeq not working
```

**Solution**:

```python
# Lambeq uses Discopy backend
# Should work out of the box

from lambeq import BobcatParser

parser = BobcatParser()
diagram = parser.sentence2diagram("Alice loves Bob")

# This is a Discopy diagram
assert hasattr(diagram, 'draw')
assert hasattr(diagram, 'dom')

# Evaluate with Discopy functor
from discopy.matrix import Functor
F = Functor(...)
result = F(diagram)
```

---

### Issue: PyTorch Integration

**Symptoms**:
```python
# Gradient computation not working
# Type errors with tensors
```

**Solution**:

```python
import torch
from discopy.matrix import Functor

# Ensure all arrays are torch tensors
weights = {
    box: torch.randn(cod_dim, dom_dim, requires_grad=True)
    for box in boxes
}

# Use PyTorch backend
F = Functor(
    ob={...},
    ar=weights,
    backend='pytorch'  # Important!
)

# Evaluate
result = F(diagram)

# Compute gradients
loss = result.array.sum()
loss.backward()

# Access gradients
for box, weight in weights.items():
    print(f"{box}: {weight.grad}")
```

---

### Issue: Qiskit/Cirq Conversion

**Symptoms**:
```python
# Circuit conversion fails
# Unsupported gate types
```

**Solution**:

```python
from discopy.quantum.circuit import Circuit

# Only basic gates supported
# May need to decompose custom gates first

try:
    qiskit_circuit = circuit.to_qiskit()
except NotImplementedError as e:
    print(f"Unsupported gate: {e}")
    # Decompose or use different gates

# Alternative: export to QASM
qasm = circuit.to_qasm()
# Then import in Qiskit/Cirq
```

---

## Debugging Strategies

### Strategy 1: Incremental Building

```python
# Build diagram step by step
d1 = f
print(f"Step 1: {d1}")

d2 = d1 >> g
print(f"Step 2: {d2}")

d3 = d2 >> h
print(f"Step 3: {d3}")

# Identify where error occurs
```

---

### Strategy 2: Type Inspection

```python
def inspect_diagram(diagram):
    """Print diagram structure."""
    print(f"Domain: {diagram.dom}")
    print(f"Codomain: {diagram.cod}")
    print(f"Boxes: {len(diagram.boxes)}")
    for i, box in enumerate(diagram.boxes):
        print(f"  {i}: {box.name} : {box.dom} → {box.cod}")
    print(f"Layers: {len(diagram.layers)}")

inspect_diagram(problematic_diagram)
```

---

### Strategy 3: Minimal Example

```python
# Create minimal reproducing example
from discopy import Ty, Box

x, y = Ty('x'), Ty('y')
f = Box('f', x, y)

# Test in isolation
try:
    result = f >> f  # Should fail (type mismatch)
except ValueError as e:
    print(f"Expected error: {e}")

# Fix
g = Box('g', y, y)
result = f >> g  # Should work
```

---

## Getting Help

If issues persist:

1. **Check Documentation**: https://docs.discopy.org
2. **Search Issues**: https://github.com/discopy/discopy/issues
3. **Ask Community**: Discopy Discord/Slack
4. **Create Minimal Example**: Isolate the problem
5. **File Issue**: https://github.com/discopy/discopy/issues/new

**When Reporting Issues**:
- Discopy version: `python -c "import discopy; print(discopy.__version__)"`
- Python version: `python --version`
- Minimal code to reproduce
- Full error traceback
- Expected vs actual behavior

---

## Quick Checklist

When encountering errors:

- [ ] Check types match in composition (`f.cod == g.dom`)
- [ ] Verify functor has mappings for all boxes
- [ ] Ensure matrix dimensions match type dimensions
- [ ] Use consistent backend (NumPy/PyTorch/JAX)
- [ ] Check qubit indexing in circuits
- [ ] Visualize diagram to understand structure
- [ ] Create minimal reproducing example
- [ ] Check documentation for similar cases
- [ ] Update to latest Discopy version

Most issues fall into type mismatches, missing functor mappings, or dimension errors. The type system is your friend—use it!
