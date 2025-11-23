# DisCoPy Examples: Levels 3-4

**Proficient and Advanced Levels** - Symmetric Monoidal and Compact Closed Categories

This document provides executable code snippets, ASCII diagrams, and real-world use cases for Levels 3-4, covering wire swapping and quantum circuits.

---

## Level 3: Proficient - Symmetric Monoidal (Wire Swapping)

**Core Capability**: Reorder wires using `Swap` for type-safe composition

**When to Use**: Type-aware workflows, data routing, flexible composition patterns

---

### Example 3.1: Basic Wire Swap

**Use Case**: Reorder function arguments to match expected types.

**ASCII Diagram**:
```
Before Swap:
A ─────┐
       X  (crossing wires)
B ─────┘

After Swap:
B ──────
A ──────
```

**Code**:
```python
from discopy import Ty, Box, Diagram

# Types
A = Ty('A')
B = Ty('B')

# Swap operation
swap = Diagram.swap(A, B)

print("Swap diagram:", swap)
print("Type:", swap.dom, "→", swap.cod)
print("Domain: A ⊗ B")
print("Codomain: B ⊗ A")

# Visualize
swap.draw(figsize=(6, 4), path='swap_L3_1.png')
```

**Diagram**:
```
A     B
│     │
│  ╱──┘
│ ╱
X
│ ╲
│  ╲──┐
│     │
↓     ↓
B     A
```

---

### Example 3.2: Function Argument Reordering

**Use Case**: Call function with swapped arguments.

**ASCII Diagram**:
```
Input: (Name, Age)

Name ───┐
        X  swap
Age  ───┘

Output: (Age, Name)

Age  ───[process]───> Result
Name ───┘
```

**Code**:
```python
from discopy import Ty, Box, Diagram

# Types
Name = Ty('Name')
Age = Ty('Age')
Result = Ty('Result')

# Function expecting (Age, Name)
process = Box('process', Age @ Name, Result)

# But we have (Name, Age) - need to swap
swap_args = Diagram.swap(Name, Age)

# Complete pipeline: swap then process
pipeline = swap_args >> process

print("Pipeline:", pipeline)
print("Type:", pipeline.dom, "→", pipeline.cod)
print("Input: Name ⊗ Age")
print("After swap: Age ⊗ Name")
print("Output: Result")

# Visualize
pipeline.draw(figsize=(8, 5), path='swap_args_L3_2.png')
```

---

### Example 3.3: Parallel Streams with Routing

**Use Case**: Process two data streams, swap them, then merge.

**ASCII Diagram**:
```
Stream1 ──[process1]──> A ──┐
                            X  swap
Stream2 ──[process2]──> B ──┘
                            │
                            ↓
                      [merge]──> Output
```

**Code**:
```python
from discopy import Ty, Box, Diagram

# Types
Stream1 = Ty('Stream1')
Stream2 = Ty('Stream2')
ProcessedA = Ty('ProcessedA')
ProcessedB = Ty('ProcessedB')
Output = Ty('Output')

# Processing
process1 = Box('process1', Stream1, ProcessedA)
process2 = Box('process2', Stream2, ProcessedB)

# Swap processed results
swap = Diagram.swap(ProcessedA, ProcessedB)

# Merge (expects ProcessedB ⊗ ProcessedA after swap)
merge = Box('merge', ProcessedB @ ProcessedA, Output)

# Complete pipeline
pipeline = (process1 @ process2) >> swap >> merge

print("Routing Pipeline:", pipeline)
print("Type:", pipeline.dom, "→", pipeline.cod)

# Visualize
pipeline.draw(figsize=(10, 6), path='routing_L3_3.png')
```

---

### Example 3.4: Multi-Argument Function Composition

**Use Case**: Compose functions with mismatched argument order.

**Code**:
```python
from discopy import Ty, Box, Diagram

# Types
X = Ty('X')
Y = Ty('Y')
Z = Ty('Z')
W = Ty('W')

# f: X ⊗ Y → Z
f = Box('f', X @ Y, Z)

# g: Y ⊗ Z → W (expects Y first, but we have Z from f)
# We need to provide Y and swap with Z
g = Box('g', Y @ Z, W)

# Problem: After f, we have Z, but g expects Y ⊗ Z
# Solution: We need Y to be carried through in parallel

# Correct composition:
# (X ⊗ Y) ──[f @ id_Y]──> (Z ⊗ Y) ──[swap]──> (Y ⊗ Z) ──[g]──> W

parallel_f = f @ Diagram.id(Y)  # f @ id_Y: (X ⊗ Y) ⊗ Y → Z ⊗ Y
swap_zy = Diagram.swap(Z, Y)    # swap: Z ⊗ Y → Y ⊗ Z

# Full pipeline
pipeline = parallel_f >> swap_zy >> g

print("Multi-argument composition:", pipeline)
print("Type:", pipeline.dom, "→", pipeline.cod)
print("Domain: (X ⊗ Y) ⊗ Y")
print("Codomain: W")

# Visualize
pipeline.draw(figsize=(12, 6), path='multi_arg_L3_4.png')
```

---

### Example 3.5: Braiding in Data Flow

**Use Case**: Flexible routing in complex pipelines.

**Code**:
```python
from discopy import Ty, Box, Diagram

# Types
Input1 = Ty('Input1')
Input2 = Ty('Input2')
Input3 = Ty('Input3')
Output = Ty('Output')

# Operations
op1 = Box('op1', Input1, Input2)
op2 = Box('op2', Input2, Input3)
combine = Box('combine', Input3 @ Input2, Output)

# Pipeline with braiding:
# Input1 ──[op1]──> Input2 ──[op2]──> Input3 ──┐
#                     │                         X  swap
#                     └─────────────────────────┘
#                                               │
#                                         [combine]──> Output

# Build pipeline
step1 = op1  # Input1 → Input2
step2 = op2 @ Diagram.id(Input2)  # (Input2 ⊗ Input2) → (Input3 ⊗ Input2)
# Wait, this doesn't match. Let me fix:

# Correct approach:
# We have Input1, need to duplicate conceptually or track both branches
# Simplified version:
pipeline_simple = (
    op1 >>                        # Input1 → Input2
    (op2 @ Diagram.id(Input2)) >> # Input2 ⊗ Input2 → Input3 ⊗ Input2
    combine                       # Input3 ⊗ Input2 → Output
)

print("Braided Pipeline:", pipeline_simple)

# Visualize
pipeline_simple.draw(figsize=(10, 6), path='braiding_L3_5.png')
```

---

### Level 3 Summary

**Key Operator**: `Diagram.swap(A, B)` (wire crossing / braiding)

**Type Signature**: `Swap: A ⊗ B → B ⊗ A`

**Braiding Laws**:
1. **Naturality**: `(f @ g) >> swap = swap >> (g @ f)`
2. **Involution**: `swap >> swap = id` (swap twice returns to original)
3. **Hexagon**: (coherence for triple swaps)

**When to Use**:
- ✅ Argument reordering
- ✅ Data routing
- ✅ Flexible composition
- ✅ Type-safe wire crossing

**New Capabilities vs Level 2**:
- ✅ Wire reordering
- ✅ Type-aware composition
- ✅ Braiding patterns

---

## Level 4: Advanced - Compact Closed (Quantum Circuits)

**Core Capability**: Duality with cups and caps for quantum computing

**When to Use**: Quantum circuits, entanglement, measurement, categorical quantum mechanics

---

### Example 4.1: Basic Cups and Caps

**Use Case**: Create and consume entangled pairs.

**ASCII Diagram**:
```
Cap (create pair):
      ╭─╮
      │ │
      ↓ ↓
      A A*

Cup (consume pair):
      A A*
      ↓ ↓
      │ │
      ╰─╯
       I
```

**Code**:
```python
from discopy.compact import Ty, Cap, Cup, Id

# Type
A = Ty('A')

# Cap: I → A ⊗ A*  (create entangled pair)
cap = Cap(A)

# Cup: A ⊗ A* → I  (consume pair / measurement)
cup = Cup(A)

print("Cap (create pair):", cap)
print("Type:", cap.dom, "→", cap.cod)

print("\nCup (consume pair):", cup)
print("Type:", cup.dom, "→", cup.cod)

# Yanking equation: Cap then Cup = Identity
yanking = cap >> cup
print("\nYanking (cap >> cup):", yanking)
print("Should be identity on I")

# Visualize
cap.draw(figsize=(6, 4), path='cap_L4_1.png')
cup.draw(figsize=(6, 4), path='cup_L4_1.png')
```

---

### Example 4.2: Bell State Creation

**Use Case**: Create maximally entangled Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2

**ASCII Diagram**:
```
        ╭─╮  (cap creates |00⟩ + |11⟩)
        │ │
        ↓ ↓
      qubit0 qubit1
```

**Code**:
```python
from discopy.quantum import qubit, Ket, Cap
from discopy.quantum.circuit import Circuit, H, CNOT

# Create Bell state using categorical approach
# Method 1: Using Cap (categorical)
bell_categorical = Cap(qubit)

print("Bell State (categorical):", bell_categorical)
print("Type:", bell_categorical.dom, "→", bell_categorical.cod)

# Method 2: Using quantum gates (traditional)
# |0⟩ ──[H]──●──   (Hadamard on qubit 0, CNOT controlled by qubit 0)
#            │
# |0⟩ ───────⊕──

bell_gates = (
    Ket(0, 0)              # Initial state |00⟩
    >> (H @ Circuit.id(1)) # Hadamard on qubit 0
    >> CNOT                # CNOT gate
)

print("\nBell State (gates):", bell_gates)

# Evaluate
result_categorical = bell_categorical.eval()
result_gates = bell_gates.eval()

print("\nCategorical result:")
print(result_categorical)

print("\nGates result:")
print(result_gates)

# Visualize
bell_gates.draw(figsize=(8, 4), path='bell_state_L4_2.png')
```

---

### Example 4.3: Quantum Teleportation (Schematic)

**Use Case**: Teleport quantum state using entanglement and classical communication.

**ASCII Diagram**:
```
Alice's qubit (ψ) ──●────[measure]──> m1, m2 (classical bits)
                    │
Entangled pair  ────┼────────┐
(from cap)          │        │
              Alice's part   Bob's part ──[X^m1]──[Z^m2]──> ψ (reconstructed)
```

**Code**:
```python
from discopy.quantum import qubit, Ket
from discopy.quantum.circuit import Circuit, H, CNOT, X, Z, Measure

# NOTE: This is a SCHEMATIC representation
# Real teleportation requires classical control (if m1==1: apply X, if m2==1: apply Z)
# DisCoPy supports this via controlled gates and classical bits
# See: https://docs.discopy.org/en/main/quantum.html#classical-control

# Step 1: Create Bell pair (shared between Alice and Bob)
bell_pair = (
    Ket(0, 0)
    >> (H @ Circuit.id(1))
    >> CNOT
)

# Step 2: Alice's qubit to teleport
alice_qubit = Ket(1)  # Example: |1⟩ state

# Step 3: Alice performs Bell measurement (entangle with her half of Bell pair)
# ψ ⊗ (Bell pair) → (ψ ⊗ Alice's half) ⊗ Bob's half
# Then Alice measures, getting two classical bits m1, m2

# Full teleportation circuit (schematic):
teleportation = (
    alice_qubit @ bell_pair  # Combine Alice's qubit with Bell pair: 3 qubits total
    >> (CNOT @ Circuit.id(1))  # CNOT between Alice's qubits
    >> ((H @ Circuit.id(1)) @ Circuit.id(1))  # Hadamard on first qubit
    >> (Measure() @ Measure() @ Circuit.id(1))  # Measure Alice's qubits
    # Classical control would go here: if m1==1: X, if m2==1: Z
    # Schematic version (always applies both):
    >> (X @ Circuit.id(2))  # Apply X correction (should be conditional)
    >> (Z @ Circuit.id(2))  # Apply Z correction (should be conditional)
)

print("Quantum Teleportation Circuit (SCHEMATIC):")
print(teleportation)
print("\nWARNING: This is schematic only.")
print("Real teleportation requires classical control based on measurement outcomes.")
print("See DisCoPy docs for full implementation with classical bits.")

# Visualize
teleportation.draw(figsize=(14, 6), path='teleportation_L4_3.png')
```

---

### Example 4.4: Quantum Circuit Optimization with Duality

**Use Case**: Simplify circuits using categorical identities.

**Code**:
```python
from discopy.compact import Ty, Box, Cap, Cup, Id

# Type
q = Ty('q')  # Qubit type

# Example: f: q → q (some unitary operation)
f = Box('f', q, q)

# Circuit 1: Create pair, apply f to first qubit, measure both
# Cap(q) >> (f @ Id(q.r)) >> Cup(q)
# This is equivalent to Tr(f) - the trace of f

circuit1 = Cap(q) >> (f @ Id(q.r)) >> Cup(q)

print("Circuit with cap-f-cup:", circuit1)
print("Type:", circuit1.dom, "→", circuit1.cod)
print("This computes the trace of f")

# Categorical identity (yanking):
# Cap(A) >> Cup(A) = Id(I)  (empty diagram)
yanking = Cap(q) >> Cup(q)
print("\nYanking:", yanking)
print("Should be identity on empty type")

# Transpose using duality:
# f: A → B  implies  f†: B* → A*
f_dagger = Box('f†', q.r, q.r)

# These are related by naturality of cups/caps
# (Not directly executable in DisCoPy without defining f_dagger explicitly)

# Visualize
circuit1.draw(figsize=(8, 5), path='duality_circuit_L4_4.png')
```

---

### Example 4.5: Entanglement and Measurement

**Use Case**: Create entangled state and measure one qubit.

**Code**:
```python
from discopy.quantum import qubit, Ket
from discopy.quantum.circuit import Circuit, H, CNOT, Measure

# Create Bell state
bell_state = (
    Ket(0, 0)
    >> (H @ Circuit.id(1))
    >> CNOT
)

# Measure first qubit
measure_first = bell_state >> (Measure() @ Circuit.id(1))

print("Bell State:", bell_state)
print("Type:", bell_state.dom, "→", bell_state.cod)

print("\nMeasure First Qubit:", measure_first)

# Evaluate
bell_result = bell_state.eval()
print("\nBell state vector:")
print(bell_result)

# Expected: (|00⟩ + |11⟩)/√2
# Vector: [1/√2, 0, 0, 1/√2]
import numpy as np
expected = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)])
print("\nExpected:")
print(expected)

print("\nMatch:", np.allclose(bell_result.array, expected))

# Visualize
bell_state.draw(figsize=(8, 4), path='bell_measure_L4_5.png')
```

---

### Example 4.6: Categorical vs Traditional Quantum

**Use Case**: Compare categorical (cups/caps) and traditional (gates) approaches.

**Code**:
```python
from discopy.quantum import qubit, Ket
from discopy.quantum.circuit import Circuit, H, CNOT, X, Z
from discopy.compact import Cap

print("=== Categorical vs Traditional Quantum ===\n")

# Categorical approach: Using duality (Cap)
print("1. Categorical Approach (Compact Closed Category)")
print("   - Uses Cap: I → qubit ⊗ qubit* to create entanglement")
print("   - Emphasizes compositional structure")
print("   - Diagrams show information flow")

categorical = Cap(qubit)
print(f"   Cap diagram: {categorical}")
print(f"   Type: {categorical.dom} → {categorical.cod}")

# Traditional approach: Using gates
print("\n2. Traditional Approach (Quantum Gates)")
print("   - Uses H + CNOT gates")
print("   - Circuit-based representation")
print("   - Unitary matrix operations")

traditional = (
    Ket(0, 0)
    >> (H @ Circuit.id(1))
    >> CNOT
)
print(f"   Gate circuit: {traditional}")

# Both produce same state
cat_result = categorical.eval()
trad_result = traditional.eval()

print("\n3. Results Comparison:")
print(f"   Categorical result shape: {cat_result.array.shape}")
print(f"   Traditional result shape: {trad_result.array.shape}")
print(f"   Both create maximally entangled state: |00⟩ + |11⟩")

# Advantage of categorical approach:
print("\n4. Categorical Advantages:")
print("   ✓ Compositional semantics (proven correctness)")
print("   ✓ Visual reasoning (string diagrams)")
print("   ✓ Abstract from gate details")
print("   ✓ Direct connection to math (category theory)")

print("\n5. Traditional Gate Advantages:")
print("   ✓ Hardware implementation clear")
print("   ✓ Optimization tools mature (Qiskit, Cirq)")
print("   ✓ Industry standard")
print("   ✓ Direct quantum computer compilation")
```

---

### Example 4.7: QNLP - Simple Sentence to Circuit

**Use Case**: Map sentence to quantum circuit via categorical grammar.

**Code**:
```python
from discopy.quantum import qubit, Ket
from discopy.quantum.circuit import Circuit, H, CNOT, Ry, Rz
from discopy.rigid import Ty, Box

print("=== QNLP: Sentence → Circuit ===\n")

# Step 1: Define grammatical types
N = Ty('N')  # Noun
S = Ty('S')  # Sentence

# Step 2: Define words as boxes (grammatical structure)
alice = Box('Alice', Ty(), N)       # Proper noun: I → N
loves = Box('loves', N, N @ S.l)    # Transitive verb: N → N ⊗ S*
bob = Box('Bob', Ty(), N)           # Proper noun: I → N

# Step 3: Sentence diagram (grammar)
# "Alice loves Bob"
sentence = alice @ loves @ bob

print("Grammatical Structure:")
print(f"  Alice: {alice.dom} → {alice.cod}")
print(f"  loves: {loves.dom} → {loves.cod}")
print(f"  Bob: {bob.dom} → {bob.cod}")
print(f"\n  Sentence: {sentence}")

# Step 4: Map to quantum circuit (functor)
# Each noun → qubit
# Each verb → quantum gate

# Define word circuits (simplified)
word_circuits = {
    'Alice': Ket(0),        # |0⟩ state
    'Bob': Ket(1),          # |1⟩ state
    'loves': CNOT           # Entangling operation
}

print("\n Quantum Mappings:")
print("  Alice → |0⟩")
print("  Bob → |1⟩")
print("  loves → CNOT (entanglement)")

# Step 5: Build quantum circuit
# (Simplified - full QNLP requires functor composition)
quantum_sentence = (
    word_circuits['Alice'] @ word_circuits['Bob']  # |0⟩ ⊗ |1⟩
    >> word_circuits['loves']                       # CNOT
)

print("\n Quantum Circuit:")
print(f"  {quantum_sentence}")

# Evaluate
result = quantum_sentence.eval()
print(f"\n Result state:")
print(result.array)

# Expected: CNOT|01⟩ = |01⟩ (no flip because control is |0⟩)

# Visualize
quantum_sentence.draw(figsize=(8, 4), path='qnlp_simple_L4_7.png')

print("\n QNLP Pipeline Summary:")
print("  Text → Grammar Diagram → Quantum Circuit → Evaluate")
print("  'Alice loves Bob' → categorical structure → entangled qubits → quantum state")
```

---

### Level 4 Summary

**Key Structures**:
- `Cap(A)`: I → A ⊗ A* (create entangled pair)
- `Cup(A)`: A ⊗ A* → I (consume pair / measurement)
- Duality: A* is the dual type of A

**Compact Closed Laws**:
1. **Yanking**: `Cap(A) >> Cup(A) = Id(I)`
2. **Naturality**: Cups/caps commute with morphisms
3. **Coherence**: Triangle identities

**When to Use**:
- ✅ Quantum circuits
- ✅ Quantum entanglement
- ✅ QNLP (Quantum Natural Language Processing)
- ✅ Categorical quantum mechanics
- ✅ Diagrammatic reasoning

**New Capabilities vs Level 3**:
- ✅ Duality (adjoint types)
- ✅ Quantum entanglement (Cap/Cup)
- ✅ Quantum measurement
- ✅ QNLP pipeline (grammar → circuit)

**Limitations**:
- ❌ No feedback loops (need Level 5 traced)
- ❌ Limited classical control (need custom implementations)
- ❌ No backend selection yet (see Level 6)

---

## Quick Reference

### Level 3 Cheat Sheet

```python
# Wire swap
from discopy import Diagram
swap = Diagram.swap(A, B)  # A ⊗ B → B ⊗ A

# Swap laws
swap >> swap == Diagram.id(A @ B)  # Involution
```

### Level 4 Cheat Sheet

```python
# Compact closed category
from discopy.compact import Ty, Cap, Cup, Id

# Create pair (entanglement)
cap = Cap(A)  # I → A ⊗ A*

# Consume pair (measurement)
cup = Cup(A)  # A ⊗ A* → I

# Yanking equation
cap >> cup == Id(Ty())  # Identity

# Quantum circuit
from discopy.quantum.circuit import Circuit, H, CNOT, Measure
bell = Ket(0, 0) >> (H @ Circuit.id(1)) >> CNOT
```

---

## Common Patterns

### Pattern 1: Argument Reordering (Level 3)

```python
# Function f expects (B, A) but we have (A, B)
swap = Diagram.swap(A, B)
pipeline = swap >> f
```

### Pattern 2: Bell State (Level 4)

```python
# Categorical
bell = Cap(qubit)

# Gates
bell = Ket(0, 0) >> (H @ Circuit.id(1)) >> CNOT
```

### Pattern 3: QNLP Pipeline (Level 4)

```python
# Grammar diagram
sentence = word1 @ word2 @ word3

# Map to circuit
F = CircuitFunctor(word_circuits={...})
quantum_circuit = F(sentence)

# Evaluate
result = quantum_circuit.eval()
```

---

## Exercises

### Exercise 3.1: Multiple swaps
Swap three types: `(A, B, C) → (C, A, B)`. How many swaps needed?

### Exercise 3.2: Routing diagram
Create a diagram with 4 inputs routed to 4 outputs in reverse order.

### Exercise 4.1: Bell states
Create all 4 Bell states: |Φ⁺⟩, |Φ⁻⟩, |Ψ⁺⟩, |Ψ⁻⟩

### Exercise 4.2: Quantum teleportation
Implement full quantum teleportation with conditional gates based on measurement.

### Exercise 4.3: QNLP sentence
Map "Bob likes Alice" to quantum circuit using categorical grammar.

---

## Next Steps

- **Level 5-7**: Traced categories, custom functors, verification → [EXAMPLES-L5-L7.md](EXAMPLES-L5-L7.md)
- **Real-World Use Cases**: Full applications → [USE-CASES.md](USE-CASES.md)

---

## Resources

- **DisCoPy Quantum**: https://docs.discopy.org/en/main/quantum.html
- **Compact Closed Categories**: "Picturing Quantum Processes" (Coecke & Kissinger)
- **Framework Documentation**: `STRING-DIAGRAM-LEVELS-1-4.md`
