# Discopy Integration Guide

How to integrate Discopy with other libraries and frameworks.

## Table of Contents

1. [NLP Libraries](#nlp-libraries)
2. [Quantum Computing Frameworks](#quantum-computing-frameworks)
3. [Machine Learning Frameworks](#machine-learning-frameworks)
4. [Tensor Computation Backends](#tensor-computation-backends)
5. [Visualization Tools](#visualization-tools)
6. [Production Deployment](#production-deployment)

---

## NLP Libraries

### Lambeq (Primary QNLP Framework)

**Relationship**: Lambeq uses Discopy as its backend for diagram manipulation.

**Installation**:
```bash
pip install lambeq
```

**Usage**:
```python
from lambeq import BobcatParser, AtomicType, IQPAnsatz
from discopy.matrix import Functor
import numpy as np

# Parse sentence (returns Discopy diagram)
parser = BobcatParser()
diagram = parser.sentence2diagram("Alice loves Bob")

# Diagram is a Discopy object
print(type(diagram))  # discopy.grammar.pregroup.Diagram

# Convert to quantum circuit
n = AtomicType.NOUN
s = AtomicType.SENTENCE

ansatz = IQPAnsatz({n: 1, s: 1}, n_layers=1)
circuit = ansatz(diagram)

# circuit is a Discopy quantum circuit
print(type(circuit))  # discopy.quantum.circuit.Circuit

# Evaluate with Discopy
result = circuit.eval()
```

**Key Points**:
- Lambeq diagrams are Discopy diagrams
- All Discopy operations work on Lambeq outputs
- Use Lambeq for NLP preprocessing, Discopy for custom functors

**Custom Functor with Lambeq**:
```python
from lambeq import BobcatParser
from discopy.matrix import Functor
import numpy as np

parser = BobcatParser()
diagram = parser.sentence2diagram("The cat sat")

# Define custom semantics
from lambeq import AtomicType
n, s = AtomicType.NOUN, AtomicType.SENTENCE

# Custom word embeddings
word_embeddings = {
    'The': np.random.randn(10),
    'cat': np.random.randn(10),
    'sat': np.random.randn(10, 10)
}

# Create functor
# (Requires mapping all boxes in diagram)
```

---

### spaCy / NLTK (Grammar Extraction)

**Use Case**: Extract grammatical structure to build Discopy diagrams.

**Installation**:
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

**Integration Pattern**:
```python
import spacy
from discopy import Ty, Box
from discopy.grammar.pregroup import Diagram, Word, Cup, Id

# Load spaCy
nlp = spacy.load("en_core_web_sm")

# Define types
n = Ty('n')  # Noun
s = Ty('s')  # Sentence
v = Ty('v')  # Verb

# Parse with spaCy
doc = nlp("Alice runs")

# Convert to Discopy
def pos_to_type(pos):
    """Map POS tags to types."""
    mapping = {
        'NOUN': n,
        'PROPN': n,
        'VERB': n.r @ s,  # Intransitive verb
        'ADP': n @ n.l,    # Preposition
    }
    return mapping.get(pos, Ty('x'))

# Build diagram from parse
words = []
for token in doc:
    word_type = pos_to_type(token.pos_)
    words.append(Word(token.text, word_type))

# Compose
sentence = words[0]
for word in words[1:]:
    sentence = sentence @ word

# Apply reductions (cups)
# (Implementation depends on grammar)
```

**Dependency Grammar**:
```python
from discopy.grammar.dependency import Dependency

# Extract dependencies from spaCy
dependencies = []
for token in doc:
    if token.head != token:
        dep = Dependency(
            token.dep_,
            token.head.text,
            token.text
        )
        dependencies.append(dep)

# Convert to diagram
# (Custom conversion logic)
```

---

## Quantum Computing Frameworks

### Qiskit

**Convert Discopy → Qiskit**:
```python
from discopy.quantum.circuit import Circuit, gates, Ket, Id

# Build Discopy circuit
circuit = (
    Ket(0, 0)
    >> (gates.H @ Id(1))
    >> gates.CNOT
)

# Convert to Qiskit
qiskit_circuit = circuit.to_qiskit()

# Use Qiskit features
from qiskit import transpile
from qiskit.providers.aer import AerSimulator

transpiled = transpile(qiskit_circuit, AerSimulator())
```

**Convert Qiskit → Discopy**:
```python
from qiskit import QuantumCircuit
from discopy.quantum.circuit import Circuit

# Create Qiskit circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# Convert to Discopy
discopy_circuit = Circuit.from_qiskit(qc)

# Use Discopy features
discopy_circuit.draw()
```

**Limitations**:
- Only basic gates supported
- Custom gates may need decomposition
- Measurement conversion may differ

---

### Cirq

**Convert Discopy → Cirq**:
```python
from discopy.quantum.circuit import Circuit, gates

circuit = gates.H @ gates.X >> gates.CNOT

# Convert to Cirq
cirq_circuit = circuit.to_cirq()

# Use Cirq features
import cirq
simulator = cirq.Simulator()
result = simulator.simulate(cirq_circuit)
```

---

### PennyLane (Variational Quantum)

**Integration Pattern**:
```python
import pennylane as qml
from discopy.quantum.circuit import Circuit, gates, Id
import torch

# Define Discopy ansatz
def discopy_ansatz(params, n_qubits):
    circuit = Id(n_qubits)
    for i, param in enumerate(params):
        circuit >>= Id(i) @ gates.Ry(param) @ Id(n_qubits - i - 1)
    return circuit

# Convert to PennyLane QNode
dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev, interface='torch')
def qnode(params):
    # Build Discopy circuit
    circuit = discopy_ansatz(params, n_qubits=2)

    # Convert to PennyLane operations
    # (Manual conversion needed)
    for i, param in enumerate(params):
        qml.RY(param, wires=i)

    return qml.expval(qml.PauliZ(0))

# Optimize
params = torch.tensor([0.1, 0.2], requires_grad=True)
optimizer = torch.optim.Adam([params], lr=0.1)

for step in range(100):
    optimizer.zero_grad()
    loss = qnode(params)
    loss.backward()
    optimizer.step()
```

**Note**: Direct conversion limited; use Discopy for design, implement in PennyLane for training.

---

### PyZX (ZX-Calculus Optimization)

**Installation**:
```bash
pip install pyzx
```

**Usage**:
```python
from discopy.quantum.circuit import Circuit, gates, Id
import pyzx as zx

# Build Discopy circuit
circuit = (
    gates.H @ Id(1)
    >> gates.CNOT
    >> gates.T @ gates.S
    >> gates.CNOT
    >> gates.H @ Id(1)
)

# Convert to ZX-diagram
zx_diagram = circuit.to_zx()

# Optimize with PyZX
# (Full integration requires pyzx installed)
zx.simplify.full_reduce(zx_diagram)

# Convert back
optimized_circuit = zx_diagram.to_circuit()

print(f"Original gates: {len(circuit.boxes)}")
print(f"Optimized gates: {len(optimized_circuit.boxes)}")
```

---

## Machine Learning Frameworks

### PyTorch

**End-to-End Differentiable Pipeline**:
```python
import torch
import torch.nn as nn
from discopy import Ty, Box
from discopy.matrix import Functor

class DiscopyCatSemantics(nn.Module):
    """Categorical semantics as PyTorch module."""

    def __init__(self, vocab_size, embedding_dim):
        super().__init__()
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.composition = nn.Linear(
            embedding_dim * 2,
            embedding_dim
        )

    def forward(self, diagram, word_indices):
        """
        Args:
            diagram: Discopy diagram
            word_indices: Tensor of word indices

        Returns:
            Composed representation
        """
        # Get embeddings
        word_embeds = self.embeddings(word_indices)

        # Build functor with current embeddings
        word = Ty('word')
        functor = Functor(
            ob={word: word_embeds.shape[1]},
            ar={
                Box(f'word_{i}', Ty(), word): word_embeds[i]
                for i in range(len(word_indices))
            },
            backend='pytorch'
        )

        # Evaluate diagram
        result = functor(diagram)
        return result.array

# Training loop
model = DiscopyCatSemantics(vocab_size=1000, embedding_dim=100)
optimizer = torch.optim.Adam(model.parameters())

for diagram, word_indices, label in dataloader:
    optimizer.zero_grad()

    # Forward pass
    representation = model(diagram, word_indices)

    # Classification
    logits = classifier(representation)
    loss = criterion(logits, label)

    # Backward pass
    loss.backward()
    optimizer.step()
```

**Quantum-Classical Hybrid**:
```python
import torch.nn as nn
from discopy.quantum.circuit import Circuit, gates, Id

class HybridModel(nn.Module):
    def __init__(self, n_qubits, classical_dim):
        super().__init__()
        self.encoder = nn.Linear(classical_dim, n_qubits)
        self.quantum_params = nn.Parameter(
            torch.randn(n_qubits * 3)
        )
        self.decoder = nn.Linear(n_qubits, 1)

    def quantum_layer(self, x):
        """Quantum processing."""
        n_qubits = x.shape[1]

        # Encode classical data as quantum state
        # (Simplified - real encoding more complex)
        initial = gates.Ket(*[0] * n_qubits)

        # Build parameterized circuit
        circuit = Id(n_qubits)
        for i in range(n_qubits):
            circuit >>= (
                Id(i)
                @ gates.Ry(self.quantum_params[i])
                @ Id(n_qubits - i - 1)
            )

        # Evaluate
        final_state = (initial >> circuit).eval()

        # Measure (get probabilities)
        probs = abs(final_state.array) ** 2
        return probs[:n_qubits]

    def forward(self, x):
        # Classical encoding
        x = torch.relu(self.encoder(x))

        # Quantum processing
        x = self.quantum_layer(x)

        # Classical decoding
        return self.decoder(x)
```

---

### JAX

**JIT Compilation**:
```python
import jax
import jax.numpy as jnp
from discopy.matrix import Functor

# Define functor with JAX backend
F = Functor(
    ob={x: 10, y: 10},
    ar={
        f: jnp.array([[1.0, 0.0], [0.0, 1.0]]),
        g: jnp.array([[0.0, 1.0], [1.0, 0.0]])
    },
    backend='jax'
)

# JIT compile evaluation
@jax.jit
def evaluate_jit(diagram):
    return F(diagram)

# Use
result = evaluate_jit(diagram)

# Autodiff
def loss_fn(params, diagram):
    # Update functor with params
    # Evaluate
    result = F(diagram)
    return jnp.sum(result.array)

grad_fn = jax.grad(loss_fn)
gradients = grad_fn(params, diagram)
```

---

### TensorFlow

**Integration**:
```python
import tensorflow as tf
from discopy.matrix import Functor

# Define functor with TensorFlow backend
F = Functor(
    ob={x: 10, y: 10},
    ar={
        f: tf.Variable(tf.random.normal([10, 10])),
        g: tf.Variable(tf.random.normal([10, 10]))
    },
    backend='tensorflow'
)

# Use in TensorFlow model
class DiscopyLayer(tf.keras.layers.Layer):
    def __init__(self, diagram, **kwargs):
        super().__init__(**kwargs)
        self.diagram = diagram
        self.functor = None  # Initialize in build()

    def build(self, input_shape):
        # Create trainable weights
        self.weights = {
            box: self.add_weight(
                name=f'weight_{box.name}',
                shape=(output_dim, input_dim),
                initializer='glorot_uniform'
            )
            for box in self.diagram.boxes
        }

        # Build functor
        self.functor = Functor(
            ob={...},
            ar=self.weights,
            backend='tensorflow'
        )

    def call(self, inputs):
        # Evaluate diagram
        result = self.functor(self.diagram)
        return result.array
```

---

## Tensor Computation Backends

### NumPy (Default)

**Best For**: Small diagrams, CPU computation, prototyping

```python
from discopy.matrix import Functor
import numpy as np

F = Functor(
    ob={x: 100, y: 100},
    ar={f: np.random.rand(100, 100)},
    backend='numpy'  # Default
)
```

---

### SymPy (Symbolic Computation)

**Best For**: Symbolic manipulation, formal verification

```python
from discopy.matrix import Functor
from sympy import Symbol, Matrix

# Symbolic parameters
theta = Symbol('theta')
phi = Symbol('phi')

# Symbolic functor
F = Functor(
    ob={x: 2, y: 2},
    ar={
        f: Matrix([
            [sympy.cos(theta), -sympy.sin(theta)],
            [sympy.sin(theta), sympy.cos(theta)]
        ])
    }
)

# Evaluate symbolically
result = F(diagram)
print(result.array)  # Symbolic expression

# Substitute values
result_numeric = result.array.subs(theta, np.pi/4)
```

---

### Quimb (Tensor Networks)

**Best For**: Large quantum states, tensor network contraction

```bash
pip install quimb
```

```python
# Use for large tensor network evaluation
# (Advanced usage - consult Quimb docs)
```

---

## Visualization Tools

### Matplotlib (Default)

```python
diagram.draw(
    backend='matplotlib',
    figsize=(10, 6),
    fontsize=12
)
```

---

### TikZ/LaTeX

**Generate LaTeX**:
```python
# Export TikZ code
tikz_code = diagram.to_tikz()

# Save to file
with open('diagram.tex', 'w') as f:
    f.write(r'\documentclass{standalone}')
    f.write(r'\usepackage{tikz}')
    f.write(r'\begin{document}')
    f.write(tikz_code)
    f.write(r'\end{document}')

# Compile with pdflatex
# pdflatex diagram.tex
```

---

### Graphviz

**Convert to Graphviz**:
```python
# Get plane graph
graph = diagram.to_graph()

# Export to DOT format
# (Manual conversion needed)
```

---

## Production Deployment

### FastAPI Service

```python
from fastapi import FastAPI
from pydantic import BaseModel
from discopy import Ty, Box
from discopy.matrix import Functor
import numpy as np

app = FastAPI()

# Initialize functor
functor = Functor(
    ob={Ty('x'): 10, Ty('y'): 10},
    ar={...},
    backend='numpy'
)

class DiagramRequest(BaseModel):
    boxes: list[dict]
    composition: str

@app.post("/evaluate")
def evaluate_diagram(request: DiagramRequest):
    # Build diagram from request
    diagram = build_diagram_from_spec(request)

    # Evaluate
    result = functor(diagram)

    return {
        "result": result.array.tolist(),
        "shape": list(result.array.shape)
    }
```

---

### Docker Container

```dockerfile
FROM python:3.9

# Install dependencies
RUN pip install discopy numpy torch

# Copy application
COPY app.py /app/app.py

# Run
CMD ["python", "/app/app.py"]
```

---

### Model Serialization

```python
import pickle

# Save functor
with open('functor.pkl', 'wb') as f:
    pickle.dump(functor, f)

# Load functor
with open('functor.pkl', 'rb') as f:
    loaded_functor = pickle.load(f)

# For PyTorch functors
torch.save({
    'ob': functor.ob,
    'ar': functor.ar,
    'backend': functor.backend
}, 'functor.pt')
```

---

## Summary of Integrations

| Library | Purpose | Integration Level | Notes |
|---------|---------|-------------------|-------|
| **Lambeq** | QNLP | Native | Uses Discopy backend |
| **Qiskit** | Quantum circuits | Conversion | to_qiskit(), from_qiskit() |
| **PyTorch** | ML training | Backend | Full gradient support |
| **JAX** | JIT/Autodiff | Backend | Fast evaluation |
| **spaCy** | NLP parsing | Custom | Manual conversion |
| **PennyLane** | VQE/QAOA | Manual | Design in Discopy, train in PL |
| **PyZX** | Circuit optimization | Conversion | ZX-calculus integration |

**General Pattern**:
1. Use Discopy for compositional design
2. Convert to framework for specialized features
3. Results can often be converted back

The key is leveraging each tool for its strengths while maintaining compositional structure with Discopy.
