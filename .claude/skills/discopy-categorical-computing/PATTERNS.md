# Discopy Design Patterns and Best Practices

Proven patterns for building compositional systems with Discopy.

## Table of Contents

1. [Architectural Patterns](#architectural-patterns)
2. [Functor Patterns](#functor-patterns)
3. [Circuit Design Patterns](#circuit-design-patterns)
4. [Grammar Integration Patterns](#grammar-integration-patterns)
5. [Performance Patterns](#performance-patterns)
6. [Testing Patterns](#testing-patterns)
7. [Anti-Patterns](#anti-patterns)

---

## Architectural Patterns

### Pattern 1: Syntax-Semantics Separation

**Intent**: Separate diagram construction (syntax) from evaluation (semantics).

**Structure**:
```python
# Syntax layer - pure diagram construction
def build_diagram(inputs):
    """Build diagram without interpretation."""
    return compose_operations(inputs)

# Semantics layer - multiple interpretations
class TensorSemantics(Functor):
    """Interpret as tensors."""
    pass

class QuantumSemantics(Functor):
    """Interpret as quantum circuits."""
    pass

class SymbolicSemantics(Functor):
    """Interpret symbolically."""
    pass

# Usage
diagram = build_diagram(inputs)
tensor_result = TensorSemantics()(diagram)
circuit = QuantumSemantics()(diagram)
symbolic = SymbolicSemantics()(diagram)
```

**Benefits**:
- Same diagram, multiple interpretations
- Easy to add new semantics
- Clear separation of concerns
- Testable without evaluation

**Example**:
```python
from discopy import Ty, Box

# Syntax
def build_pipeline(n_steps):
    x = Ty('x')
    diagram = Box.id(x)
    for i in range(n_steps):
        diagram >>= Box(f'step_{i}', x, x)
    return diagram

# Semantics
from discopy.matrix import Functor
import numpy as np

tensor_functor = Functor(
    ob={Ty('x'): 10},
    ar={Box(f'step_{i}', Ty('x'), Ty('x')): np.eye(10)
        for i in range(5)}
)

# Use
pipeline = build_pipeline(5)
result = tensor_functor(pipeline)
```

---

### Pattern 2: Progressive Type Refinement

**Intent**: Start with simple types, add structure progressively.

**Structure**:
```python
# Level 1: Atomic types
n = Ty('n')
s = Ty('s')

# Level 2: Add duals (rigid category)
n_left = n.l
n_right = n.r

# Level 3: Compound types
noun_phrase = n @ n  # Two nouns
sentence_with_context = s @ n

# Level 4: Higher-order types (if needed)
sentence_modifier = s.r @ s @ s.l  # (s → s)
```

**Benefits**:
- Start simple, add complexity as needed
- Clear progression of capabilities
- Easy to understand incrementally

**Example**:
```python
from discopy.grammar.pregroup import Ty, Word, Cup, Id

# Simple grammar
n, s = Ty('n'), Ty('s')

# Add structure as needed
def simple_sentence():
    return Word('Alice', n) @ Word('runs', n.r @ s)

def transitive_sentence():
    return (
        Word('Alice', n)
        @ Word('loves', n.r @ s @ n.l)
        @ Word('Bob', n)
    )

# Apply reductions
def reduce(sentence):
    # Add cups for type reductions
    # n @ n.r → ()
    # n.l @ n → ()
    pass
```

---

### Pattern 3: Layered Abstraction

**Intent**: Build domain-specific abstractions on top of Discopy primitives.

**Structure**:
```python
# Layer 1: Discopy primitives
from discopy import Ty, Box, Diagram

# Layer 2: Domain abstractions
class DomainType(Ty):
    """Domain-specific type with custom methods."""
    def validate(self):
        pass

class DomainOperation(Box):
    """Domain-specific operation."""
    def __init__(self, name, inputs, outputs, **kwargs):
        super().__init__(name, inputs, outputs)
        self.metadata = kwargs

class DomainDiagram(Diagram):
    """Domain-specific diagram with helpers."""
    @classmethod
    def from_spec(cls, spec):
        """Build from domain specification."""
        pass

# Layer 3: High-level API
class DomainAPI:
    """User-facing API."""
    def create_pipeline(self, config):
        return DomainDiagram.from_spec(config)
```

**Benefits**:
- Hide complexity from users
- Domain-specific validation
- Easier to maintain
- Better error messages

---

## Functor Patterns

### Pattern 4: Composable Functors

**Intent**: Build complex functors from simple ones.

**Structure**:
```python
from discopy.matrix import Functor

# Base functors
identity_functor = Functor(
    ob={x: d_x for x, d_x in type_dims.items()},
    ar={}  # Identity on all boxes
)

embedding_functor = Functor(
    ob=type_to_embedding_dim,
    ar=word_to_embedding
)

transformation_functor = Functor(
    ob=embedding_to_hidden,
    ar=grammar_to_operations
)

# Compose functors
combined = embedding_functor >> transformation_functor
```

**Example**:
```python
from discopy.matrix import Functor
import numpy as np

class EmbeddingFunctor(Functor):
    """Map words to embeddings."""
    def __init__(self, vocab, embedding_dim):
        self.embeddings = {
            word: np.random.randn(embedding_dim)
            for word in vocab
        }
        super().__init__(
            ob={Ty('word'): embedding_dim},
            ar={Word(w, Ty('word')): self.embeddings[w]
                for w in vocab}
        )

class CompositionFunctor(Functor):
    """Compose embeddings."""
    def __init__(self, embedding_dim):
        super().__init__(
            ob={Ty('word'): embedding_dim},
            ar={}  # Use default composition
        )

# Stack functors
embed = EmbeddingFunctor(['Alice', 'Bob'], 100)
compose = CompositionFunctor(100)
pipeline = embed >> compose
```

---

### Pattern 5: Parameterized Functors

**Intent**: Create functors with learnable parameters.

**Structure**:
```python
import torch
import torch.nn as nn

class LearnableFunctor(nn.Module, Functor):
    """Functor with trainable parameters."""

    def __init__(self, type_dims, n_boxes):
        nn.Module.__init__(self)

        # Learnable parameters
        self.weights = nn.ParameterDict({
            f'box_{i}': nn.Parameter(torch.randn(
                type_dims['output'],
                type_dims['input']
            ))
            for i in range(n_boxes)
        })

        # Initialize functor
        Functor.__init__(
            self,
            ob=type_dims,
            ar={Box(f'f_{i}', ...): self.weights[f'box_{i}']
                for i in range(n_boxes)}
        )

    def forward(self, diagram):
        """Evaluate with current parameters."""
        return self(diagram)
```

**Benefits**:
- End-to-end differentiable
- Integrates with PyTorch/JAX
- Enables learning compositional structure

---

### Pattern 6: Caching Functor

**Intent**: Cache functor evaluations for performance.

**Structure**:
```python
from functools import lru_cache

class CachingFunctor(Functor):
    """Functor with result caching."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    def __call__(self, diagram):
        # Create hashable key
        key = self._diagram_hash(diagram)

        if key in self._cache:
            return self._cache[key]

        result = super().__call__(diagram)
        self._cache[key] = result
        return result

    def _diagram_hash(self, diagram):
        """Create hashable representation."""
        return hash((
            tuple(diagram.boxes),
            diagram.dom,
            diagram.cod
        ))

    def clear_cache(self):
        """Clear cached results."""
        self._cache.clear()
```

**Benefits**:
- Avoid redundant computation
- Useful for repetitive evaluations
- Trade memory for speed

---

## Circuit Design Patterns

### Pattern 7: Ansatz Factory

**Intent**: Systematic construction of parameterized quantum circuits.

**Structure**:
```python
from discopy.quantum.circuit import Circuit, gates, Id

class AnsatzFactory:
    """Factory for creating quantum ansatze."""

    @staticmethod
    def hardware_efficient(n_qubits, n_layers, params):
        """Hardware-efficient ansatz."""
        circuit = Id(n_qubits)
        param_idx = 0

        for layer in range(n_layers):
            # Rotation layer
            for i in range(n_qubits):
                circuit >>= (
                    Id(i)
                    @ gates.Ry(params[param_idx])
                    @ Id(n_qubits - i - 1)
                )
                param_idx += 1

            # Entangling layer
            for i in range(n_qubits - 1):
                circuit >>= (
                    Id(i) @ gates.CNOT @ Id(n_qubits - i - 2)
                )

        return circuit

    @staticmethod
    def strongly_entangling(n_qubits, n_layers, params):
        """Strongly entangling ansatz."""
        circuit = Id(n_qubits)
        param_idx = 0

        for layer in range(n_layers):
            # Rotation layer (all 3 rotations)
            for i in range(n_qubits):
                circuit >>= (
                    Id(i)
                    @ gates.Rx(params[param_idx])
                    @ gates.Ry(params[param_idx + 1])
                    @ gates.Rz(params[param_idx + 2])
                    @ Id(n_qubits - i - 1)
                )
                param_idx += 3

            # All-to-all entangling
            for i in range(n_qubits):
                for j in range(i + 1, n_qubits):
                    # CNOT between qubits i and j
                    pass  # Implementation omitted for brevity

        return circuit
```

**Benefits**:
- Reusable ansatz patterns
- Easy experimentation
- Consistent parameterization

---

### Pattern 8: Circuit Builder

**Intent**: Fluent API for circuit construction.

**Structure**:
```python
class CircuitBuilder:
    """Fluent interface for building circuits."""

    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.circuit = Id(n_qubits)

    def h(self, qubit):
        """Apply Hadamard to qubit."""
        self.circuit >>= (
            Id(qubit) @ gates.H @ Id(self.n_qubits - qubit - 1)
        )
        return self

    def cnot(self, control, target):
        """Apply CNOT."""
        if control < target:
            self.circuit >>= (
                Id(control)
                @ gates.CNOT
                @ Id(self.n_qubits - target - 1)
            )
        else:
            # Handle control > target
            pass
        return self

    def ry(self, qubit, angle):
        """Apply Ry rotation."""
        self.circuit >>= (
            Id(qubit)
            @ gates.Ry(angle)
            @ Id(self.n_qubits - qubit - 1)
        )
        return self

    def build(self):
        """Return constructed circuit."""
        return self.circuit

# Usage
circuit = (
    CircuitBuilder(3)
    .h(0)
    .cnot(0, 1)
    .ry(2, 0.5)
    .cnot(1, 2)
    .build()
)
```

**Benefits**:
- Readable circuit construction
- Method chaining
- Encapsulates qubit indexing logic

---

### Pattern 9: Circuit Templates

**Intent**: Reusable circuit patterns as functions.

**Structure**:
```python
def bell_state(qubit1=0, qubit2=1):
    """Create Bell state circuit."""
    return (
        Id(qubit1)
        @ gates.H
        @ Id(qubit2 - qubit1 - 1)
        @ Id(1)
        >> Id(qubit1)
        @ gates.CNOT
        @ Id(max(0, qubit2 - qubit1 - 2))
    )

def ghz_state(n_qubits):
    """Create GHZ state circuit."""
    circuit = gates.H @ Id(n_qubits - 1)
    for i in range(n_qubits - 1):
        circuit >>= Id(i) @ gates.CNOT @ Id(n_qubits - i - 2)
    return circuit

def qft(n_qubits):
    """Quantum Fourier Transform circuit."""
    circuit = Id(n_qubits)
    for i in range(n_qubits):
        # Hadamard
        circuit >>= Id(i) @ gates.H @ Id(n_qubits - i - 1)

        # Controlled rotations
        for j in range(i + 1, n_qubits):
            angle = np.pi / (2 ** (j - i))
            # Apply controlled rotation
            pass
    return circuit

# Usage
bell = bell_state(0, 1)
ghz = ghz_state(5)
fourier = qft(4)
```

---

## Grammar Integration Patterns

### Pattern 10: Grammar Functor Pipeline

**Intent**: Systematic conversion from grammar to computation.

**Structure**:
```python
class GrammarPipeline:
    """Pipeline from text to computation."""

    def __init__(self, parser, grammar_to_diagram, diagram_to_computation):
        self.parser = parser
        self.grammar_functor = grammar_to_diagram
        self.computation_functor = diagram_to_computation

    def __call__(self, text):
        """Process text end-to-end."""
        # Parse
        grammar = self.parser(text)

        # Grammar → Diagram
        diagram = self.grammar_functor(grammar)

        # Diagram → Computation
        result = self.computation_functor(diagram)

        return result

# Usage
pipeline = GrammarPipeline(
    parser=pregroup_parser,
    grammar_to_diagram=grammar_functor,
    diagram_to_computation=tensor_functor
)

result = pipeline("Alice loves Bob")
```

---

### Pattern 11: Word Embedding Integration

**Intent**: Integrate pre-trained word embeddings.

**Structure**:
```python
import numpy as np

class EmbeddingFunctor(Functor):
    """Functor using pre-trained embeddings."""

    def __init__(self, embedding_matrix, vocab):
        """
        Args:
            embedding_matrix: (vocab_size, embedding_dim)
            vocab: {word: index}
        """
        self.embeddings = embedding_matrix
        self.vocab = vocab
        self.embedding_dim = embedding_matrix.shape[1]

        # Map words to embeddings
        word_mappings = {}
        for word, idx in vocab.items():
            word_box = Word(word, Ty('word'))
            word_mappings[word_box] = self.embeddings[idx]

        super().__init__(
            ob={Ty('word'): self.embedding_dim},
            ar=word_mappings
        )

    @classmethod
    def from_gensim(cls, gensim_model):
        """Load from Gensim word2vec."""
        vocab = {word: idx for idx, word in enumerate(gensim_model.index_to_key)}
        matrix = gensim_model.vectors
        return cls(matrix, vocab)

    @classmethod
    def from_glove(cls, glove_file):
        """Load from GloVe file."""
        embeddings = []
        vocab = {}
        with open(glove_file) as f:
            for idx, line in enumerate(f):
                parts = line.split()
                word = parts[0]
                vector = np.array([float(x) for x in parts[1:]])
                vocab[word] = idx
                embeddings.append(vector)
        return cls(np.array(embeddings), vocab)

# Usage
functor = EmbeddingFunctor.from_glove('glove.6B.100d.txt')
result = functor(sentence_diagram)
```

---

## Performance Patterns

### Pattern 12: Lazy Evaluation

**Intent**: Defer computation until results are needed.

**Structure**:
```python
class LazyDiagram:
    """Diagram with lazy evaluation."""

    def __init__(self, diagram, functor):
        self.diagram = diagram
        self.functor = functor
        self._result = None
        self._evaluated = False

    def eval(self):
        """Evaluate if not already done."""
        if not self._evaluated:
            self._result = self.functor(self.diagram)
            self._evaluated = True
        return self._result

    def __repr__(self):
        """Show without evaluating."""
        return f"LazyDiagram({self.diagram})"

# Usage
lazy = LazyDiagram(complex_diagram, expensive_functor)
# ... do other work ...
result = lazy.eval()  # Evaluate when needed
```

---

### Pattern 13: Batch Evaluation

**Intent**: Evaluate multiple diagrams efficiently.

**Structure**:
```python
class BatchFunctor(Functor):
    """Functor for batch evaluation."""

    def eval_batch(self, diagrams):
        """Evaluate multiple diagrams at once."""
        # Group by structure
        grouped = self._group_by_structure(diagrams)

        results = []
        for structure, batch in grouped.items():
            # Batch evaluate same structure
            batch_result = self._eval_batch_same_structure(batch)
            results.extend(batch_result)

        return results

    def _group_by_structure(self, diagrams):
        """Group diagrams with same structure."""
        from collections import defaultdict
        groups = defaultdict(list)
        for d in diagrams:
            key = (d.dom, d.cod, tuple(d.boxes))
            groups[key].append(d)
        return groups

    def _eval_batch_same_structure(self, batch):
        """Evaluate batch with same structure."""
        # Use vectorized operations
        pass
```

---

### Pattern 14: Backend Selection Strategy

**Intent**: Choose backend based on workload characteristics.

**Structure**:
```python
class AdaptiveFunctor(Functor):
    """Automatically select best backend."""

    def __init__(self, ob, ar, auto_backend=True):
        self.auto_backend = auto_backend
        self.backends = ['numpy', 'pytorch', 'jax']
        super().__init__(ob, ar)

    def __call__(self, diagram):
        if self.auto_backend:
            backend = self._select_backend(diagram)
            self.backend = backend

        return super().__call__(diagram)

    def _select_backend(self, diagram):
        """Select backend based on diagram characteristics."""
        # Heuristics:
        # - Small diagrams: NumPy (low overhead)
        # - Need gradients: PyTorch
        # - Need JIT: JAX
        # - Very large: TensorFlow

        n_boxes = len(diagram.boxes)

        if n_boxes < 10:
            return 'numpy'
        elif self._needs_gradients(diagram):
            return 'pytorch'
        elif n_boxes > 100:
            return 'jax'  # JIT for large graphs
        else:
            return 'numpy'

    def _needs_gradients(self, diagram):
        """Check if diagram has parameters."""
        return any(box.free_symbols for box in diagram.boxes)
```

---

## Testing Patterns

### Pattern 15: Property-Based Testing

**Intent**: Test categorical laws automatically.

**Structure**:
```python
import hypothesis.strategies as st
from hypothesis import given

# Strategy for generating types
@st.composite
def types(draw):
    name = draw(st.text(alphabet='xyz', min_size=1, max_size=1))
    return Ty(name)

# Strategy for generating boxes
@st.composite
def boxes(draw, dom, cod):
    name = draw(st.text(alphabet='abcdefgh', min_size=1, max_size=3))
    return Box(name, dom, cod)

# Test categorical laws
@given(boxes(types(), types()),
       boxes(types(), types()),
       boxes(types(), types()))
def test_associativity(f, g, h):
    """Test (f >> g) >> h == f >> (g >> h)."""
    # Ensure types align
    if f.cod == g.dom and g.cod == h.dom:
        left = (f >> g) >> h
        right = f >> (g >> h)
        assert left == right

@given(boxes(types(), types()))
def test_identity(f):
    """Test f >> id == id >> f == f."""
    assert f >> Box.id(f.cod) == f
    assert Box.id(f.dom) >> f == f

# Run tests
# pytest will run these with many random examples
```

---

### Pattern 16: Functor Equivalence Testing

**Intent**: Verify functors preserve structure.

**Structure**:
```python
def test_functor_preserves_composition(functor, f, g):
    """Test F(f >> g) == F(f) >> F(g)."""
    if f.cod == g.dom:
        composed = f >> g
        result1 = functor(composed)
        result2 = functor(f) >> functor(g)

        # Compare results
        assert np.allclose(result1.array, result2.array)

def test_functor_preserves_identity(functor, x):
    """Test F(id_x) == id_F(x)."""
    identity = Box.id(x)
    result = functor(identity)

    # Should be identity matrix
    expected_dim = functor.ob[x]
    expected = np.eye(expected_dim)

    assert np.allclose(result.array, expected)
```

---

## Anti-Patterns

### Anti-Pattern 1: Premature Evaluation

**Problem**: Evaluating diagrams during construction.

**Bad**:
```python
# Evaluating too early
result = functor(f)  # Evaluate
result = result >> functor(g)  # Compose results
result = result >> functor(h)
```

**Good**:
```python
# Build diagram first
diagram = f >> g >> h

# Evaluate once at end
result = functor(diagram)
```

**Why**: Diagrams are cheaper to compose than tensors. Build full diagram first.

---

### Anti-Pattern 2: Type Proliferation

**Problem**: Creating too many similar types.

**Bad**:
```python
# Too specific
noun_singular = Ty('noun_singular')
noun_plural = Ty('noun_plural')
noun_proper = Ty('noun_proper')
noun_common = Ty('noun_common')
# ... hundreds of types
```

**Good**:
```python
# Use type parameters instead
noun = Ty('noun')

# Add metadata to boxes
alice = Box('Alice', Ty(), noun, is_proper=True, is_singular=True)
dogs = Box('dogs', Ty(), noun, is_proper=False, is_singular=False)
```

**Why**: Types control composition; metadata adds information without fragmenting type system.

---

### Anti-Pattern 3: Overfitting Functors

**Problem**: Functor too specific to one diagram.

**Bad**:
```python
class SpecificFunctor(Functor):
    def __call__(self, diagram):
        # Hardcoded for specific diagram structure
        if diagram.boxes[0].name == 'Alice':
            return self.alice_case()
        elif diagram.boxes[0].name == 'Bob':
            return self.bob_case()
        # ...
```

**Good**:
```python
class GeneralFunctor(Functor):
    def __init__(self, ob, ar):
        # Generic mapping
        super().__init__(ob, ar)

    # Use default __call__ implementation
    # Works for any diagram with mapped boxes
```

**Why**: Functors should be compositional, not diagram-specific.

---

### Anti-Pattern 4: Ignoring Types

**Problem**: Not using type system for validation.

**Bad**:
```python
# Composition without type checking
def compose_all(boxes):
    result = boxes[0]
    for box in boxes[1:]:
        result = result >> box  # May fail at runtime
    return result
```

**Good**:
```python
def compose_all(boxes):
    """Compose boxes with type validation."""
    result = boxes[0]
    for box in boxes[1:]:
        if result.cod != box.dom:
            raise TypeError(
                f"Cannot compose: {result.cod} ≠ {box.dom}"
            )
        result = result >> box
    return result
```

**Why**: Type errors should be caught early with clear messages.

---

## Summary of Best Practices

1. **Separate syntax from semantics** - Build diagrams, then interpret
2. **Start simple, add structure** - Progressive type refinement
3. **Compose functors** - Build complex from simple
4. **Use categorical laws** - They hold automatically
5. **Defer evaluation** - Build full diagram first
6. **Test properties** - Verify laws automatically
7. **Choose backends wisely** - Match backend to workload
8. **Cache when appropriate** - Trade memory for speed
9. **Type everything** - Use type system for validation
10. **Document assumptions** - Make functorial mappings explicit

These patterns enable building robust, maintainable compositional systems with Discopy.
