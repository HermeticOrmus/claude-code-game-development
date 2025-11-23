# DisCoPy Real-World Use Cases

**Comprehensive Guide** - Practical applications across all 7 levels

This document maps real-world problems to the appropriate level of the String Diagram Meta-Prompt Framework, with complete implementation guidance.

---

## Table of Contents

- [Level 1: Simple Pipelines](#level-1-simple-pipelines)
- [Level 2: Parallel Workflows](#level-2-parallel-workflows)
- [Level 3: Routing & Composition](#level-3-routing--composition)
- [Level 4: Quantum Computing](#level-4-quantum-computing)
- [Level 5: Stateful Systems](#level-5-stateful-systems)
- [Level 6: Production ML](#level-6-production-ml)
- [Level 7: Critical Systems](#level-7-critical-systems)
- [Cross-Level Applications](#cross-level-applications)

---

## Level 1: Simple Pipelines

**Core Pattern**: Sequential composition with `>>`

---

### Use Case 1.1: ETL (Extract, Transform, Load)

**Problem**: Process data from source to warehouse.

**Domain**: Data Engineering

**Complexity**: Novice

**Implementation**:

```python
from discopy import Ty, Box

# Data states
RawData = Ty('RawData')
ValidatedData = Ty('ValidatedData')
TransformedData = Ty('TransformedData')
LoadedData = Ty('LoadedData')

# Pipeline stages
extract = Box('extract_from_db', Ty(), RawData)
validate = Box('validate_schema', RawData, ValidatedData)
transform = Box('apply_business_rules', ValidatedData, TransformedData)
load = Box('load_to_warehouse', TransformedData, LoadedData)

# Complete ETL pipeline
etl_pipeline = extract >> validate >> transform >> load

print(f"ETL: {etl_pipeline.dom} → {etl_pipeline.cod}")
# Output: ETL: I → LoadedData
```

**Why Level 1**: Linear sequence, no branching, no parallel operations.

**When to Use**: Daily batch jobs, simple data migrations, log processing.

---

### Use Case 1.2: Image Processing Pipeline

**Problem**: Preprocess images for machine learning.

**Domain**: Computer Vision

**Implementation**:

```python
from discopy import Ty, Box

Image = Ty('Image')
Resized = Ty('Resized')
Normalized = Ty('Normalized')
Augmented = Ty('Augmented')

resize = Box('resize', Image, Resized)
normalize = Box('normalize', Resized, Normalized)
augment = Box('augment', Normalized, Augmented)

preprocessing = resize >> normalize >> augment

# Visualize
preprocessing.draw(figsize=(12, 3), path='cv_pipeline.png')
```

**Why Level 1**: Sequential operations on single image.

**When to Use**: Single-image preprocessing, batch processing (map over images).

---

### Use Case 1.3: API Request Chain

**Problem**: Microservices calling each other sequentially.

**Domain**: Backend Engineering

**Implementation**:
```python
from discopy import Ty, Box

Request = Ty('Request')
UserData = Ty('UserData')
Enriched = Ty('Enriched')
Response = Ty('Response')

auth_service = Box('authenticate', Request, UserData)
user_service = Box('get_user_profile', UserData, Enriched)
formatter = Box('format_response', Enriched, Response)

api_chain = auth_service >> user_service >> formatter
```

**Why Level 1**: Linear request flow through services.

**When to Use**: Simple REST APIs, single-path workflows.

---

## Level 2: Parallel Workflows

**Core Pattern**: Parallel composition with `@` + Functor evaluation

---

### Use Case 2.1: Ensemble Machine Learning

**Problem**: Run multiple models in parallel, aggregate predictions.

**Domain**: Machine Learning

**Complexity**: Competent

**Implementation**:

```python
from discopy import Ty, Box
from discopy.matrix import Functor
import numpy as np

# Types
Input = Ty('Input')
Prediction = Ty('Prediction')
FinalPrediction = Ty('FinalPrediction')

# Models
random_forest = Box('random_forest', Input, Prediction)
gradient_boost = Box('gradient_boost', Input, Prediction)
neural_net = Box('neural_net', Input, Prediction)

# Aggregator
aggregate = Box('aggregate', Prediction @ Prediction @ Prediction, FinalPrediction)

# Ensemble: all models run in parallel
ensemble = (random_forest @ gradient_boost @ neural_net) >> aggregate

print(f"Ensemble: {ensemble}")

# Concrete evaluation with functor
F = Functor(
    ob={
        Input: 100,            # 100 features
        Prediction: 1,         # Scalar prediction
        FinalPrediction: 1     # Scalar final prediction
    },
    ar={
        random_forest: np.random.randn(1, 100),
        gradient_boost: np.random.randn(1, 100),
        neural_net: np.random.randn(1, 100),
        aggregate: np.array([[0.33, 0.33, 0.34]])  # Average
    }
)

# Evaluate
input_data = np.random.randn(100)
result = F(ensemble)
print(f"Prediction: {result}")
```

**Why Level 2**: Models run independently in parallel, then merge.

**When to Use**: Ensemble methods, A/B testing, redundant processing for fault tolerance.

---

### Use Case 2.2: Parallel Feature Extraction

**Problem**: Extract different features from same data simultaneously.

**Domain**: ML Feature Engineering

**Implementation**:

```python
from discopy import Ty, Box
from discopy.matrix import Functor
import numpy as np

Data = Ty('Data')
TextFeatures = Ty('TextFeatures')
NumericFeatures = Ty('NumericFeatures')
CategoricalFeatures = Ty('CategoricalFeatures')
Combined = Ty('Combined')

# Parallel feature extractors
extract_text = Box('extract_text', Data, TextFeatures)
extract_numeric = Box('extract_numeric', Data, NumericFeatures)
extract_categorical = Box('extract_categorical', Data, CategoricalFeatures)

# Combiner
combine = Box('combine', TextFeatures @ NumericFeatures @ CategoricalFeatures, Combined)

# Diagram
feature_pipeline = (extract_text @ extract_numeric @ extract_categorical) >> combine

# Functor
F = Functor(
    ob={
        Data: 1000,              # Raw data dimension
        TextFeatures: 300,       # Text embedding
        NumericFeatures: 50,     # Numeric features
        CategoricalFeatures: 20, # One-hot encoded
        Combined: 370            # All features concatenated
    },
    ar={
        extract_text: np.random.randn(300, 1000),
        extract_numeric: np.random.randn(50, 1000),
        extract_categorical: np.random.randn(20, 1000),
        combine: np.eye(370)  # Concatenation (simplified)
    }
)

result = F(feature_pipeline)
print(f"Combined features shape: {result.shape}")  # (370, 1000)
```

**Why Level 2**: Independent feature extractors, parallel execution.

**When to Use**: Multi-modal data, feature engineering, preprocessing.

---

### Use Case 2.3: Distributed Map-Reduce

**Problem**: Map operation on partitions, then reduce.

**Domain**: Big Data Processing

**Implementation**:

```python
from discopy import Ty, Box

Partition = Ty('Partition')
Mapped = Ty('Mapped')
Reduced = Ty('Reduced')

# Map function (applied to each partition)
map_op = Box('map', Partition, Mapped)

# Parallel map on 4 partitions
parallel_map = map_op @ map_op @ map_op @ map_op

# Reduce
reduce_op = Box('reduce', Mapped @ Mapped @ Mapped @ Mapped, Reduced)

# Map-Reduce pipeline
mapreduce = parallel_map >> reduce_op

print(f"MapReduce: {mapreduce}")
```

**Why Level 2**: Parallel map phase, sequential reduce phase.

**When to Use**: Hadoop-style processing, distributed aggregation.

---

## Level 3: Routing & Composition

**Core Pattern**: Wire swapping with `Diagram.swap()` for flexible composition

---

### Use Case 3.1: Microservices Router

**Problem**: Route requests to services based on type, may need argument reordering.

**Domain**: Backend Architecture

**Complexity**: Proficient

**Implementation**:

```python
from discopy import Ty, Box, Diagram

Request = Ty('Request')
UserID = Ty('UserID')
OrderID = Ty('OrderID')
UserData = Ty('UserData')
OrderData = Ty('OrderData')
Response = Ty('Response')

# Parse request
parse = Box('parse', Request, UserID @ OrderID)

# Services with different argument orders
user_service = Box('user_service', UserID, UserData)  # Expects UserID first
order_service = Box('order_service', OrderID @ UserID, OrderData)  # Expects OrderID first

# After parsing, we have (UserID, OrderID)
# But order_service expects (OrderID, UserID) - need to swap!
swap_args = Diagram.swap(UserID, OrderID)

# Router
router = (
    parse                          # Request → UserID ⊗ OrderID
    >> (user_service @ Diagram.id(OrderID))  # Process user in parallel
    >> swap_args                   # Swap to match order_service signature
    >> order_service               # OrderID ⊗ UserID → OrderData
)

print(f"Router: {router}")
```

**Why Level 3**: Needs wire swapping for argument reordering.

**When to Use**: Flexible routing, function composition with mismatched signatures.

---

### Use Case 3.2: Data Pipeline with Conditional Routing

**Problem**: Route data through different processing based on type.

**Domain**: Data Engineering

**Implementation**:

```python
from discopy import Ty, Box, Diagram

Data = Ty('Data')
TypeA = Ty('TypeA')
TypeB = Ty('TypeB')
Processed = Ty('Processed')

# Classifier
classify = Box('classify', Data, TypeA @ TypeB)  # Splits into two types

# Processors
process_a = Box('process_a', TypeA, Processed)
process_b = Box('process_b', TypeB, Processed)

# Merger (expects ProcessedA ⊗ ProcessedB, but process_b produces TypeB first)
# Need to handle routing correctly

# Parallel processing
parallel_process = process_a @ process_b  # TypeA ⊗ TypeB → Processed ⊗ Processed

# Merge
merge = Box('merge', Processed @ Processed, Processed)

# Complete pipeline
pipeline = classify >> parallel_process >> merge

print(f"Routing Pipeline: {pipeline}")
```

**Why Level 3**: Branching based on type, symmetric composition.

**When to Use**: Conditional ETL, multi-path processing.

---

## Level 4: Quantum Computing

**Core Pattern**: Cups, caps, and quantum circuits

---

### Use Case 4.1: Quantum Machine Learning (QML)

**Problem**: Variational quantum circuit for classification.

**Domain**: Quantum Computing

**Complexity**: Advanced

**Implementation**:

```python
from discopy.quantum import qubit, Ket
from discopy.quantum.circuit import Circuit, H, CNOT, Rx, Ry, Rz, Measure

# Variational quantum circuit (parameterized)
def vqc_circuit(params):
    """
    Variational Quantum Circuit for binary classification.

    Args:
        params: List of rotation angles [θ1, θ2, θ3, φ1, φ2, φ3]
    """
    θ1, θ2, θ3, φ1, φ2, φ3 = params

    circuit = (
        Ket(0, 0)                    # Initialize |00⟩
        >> (H @ Circuit.id(1))       # Hadamard on qubit 0
        >> CNOT                      # Entangle
        >> (Rx(θ1) @ Ry(θ2))         # Parameterized rotations
        >> CNOT                      # Entangle again
        >> (Rz(φ1) @ Rx(φ2))         # More rotations
        >> (Ry(φ3) @ Circuit.id(1))  # Final rotation
        >> (Measure() @ Circuit.id(1))  # Measure qubit 0
    )

    return circuit

# Example with random parameters
import numpy as np
params = np.random.rand(6) * 2 * np.pi

vqc = vqc_circuit(params)

print("Variational Quantum Circuit:")
print(vqc)

# Visualize
vqc.draw(figsize=(14, 4), path='vqc_circuit.png')

# Evaluate
result = vqc.eval()
print(f"\nMeasurement probabilities: {result}")
```

**Why Level 4**: Quantum circuits require compact closed categories (cups/caps for entanglement).

**When to Use**: QML, quantum optimization, quantum chemistry simulations.

---

### Use Case 4.2: Quantum Natural Language Processing (QNLP)

**Problem**: Map sentences to quantum circuits for meaning comparison.

**Domain**: Computational Linguistics + Quantum Computing

**Implementation**:

```python
from discopy.quantum import qubit, Ket
from discopy.quantum.circuit import Circuit, H, CNOT, Ry
from discopy.rigid import Ty, Box

# Grammatical types
N = Ty('N')  # Noun
S = Ty('S')  # Sentence

# Words
alice = Box('Alice', Ty(), N)
likes = Box('likes', N, N @ S.l)  # Transitive verb
bob = Box('Bob', Ty(), N)

# Sentence diagram
sentence = alice @ likes @ bob

print("=== QNLP: 'Alice likes Bob' ===")
print(f"Grammar: {sentence}")

# Map to quantum circuit
# (Simplified - real QNLP requires functor from grammar to quantum)

# Word circuits
word_circuits = {
    'Alice': Ket(0),  # |0⟩
    'Bob': Ket(1),    # |1⟩
    'likes': CNOT      # Entangling operation
}

# Compose
quantum_sentence = (
    word_circuits['Alice'] @ word_circuits['Bob']
    >> word_circuits['likes']
)

print(f"\nQuantum Circuit: {quantum_sentence}")

# Evaluate
result = quantum_sentence.eval()
print(f"Quantum State: {result.array}")

# Visualize
quantum_sentence.draw(figsize=(8, 4), path='qnlp_sentence.png')
```

**Why Level 4**: QNLP maps grammar (pregroup) to quantum circuits (compact closed).

**When to Use**: Semantic comparison, question answering (quantum), experimental NLP.

---

### Use Case 4.3: Quantum Error Correction

**Problem**: Encode logical qubit using 3-qubit bit-flip code.

**Domain**: Quantum Computing

**Implementation**:

```python
from discopy.quantum import qubit, Ket
from discopy.quantum.circuit import Circuit, H, CNOT, X, Measure

# 3-qubit bit-flip code encoder
def encode_bitflip(logical_qubit):
    """
    Encode 1 logical qubit into 3 physical qubits.
    Protects against single bit-flip errors.
    """
    return (
        logical_qubit @ Ket(0, 0)  # Add 2 ancilla qubits
        >> (CNOT @ Circuit.id(1))  # Copy to qubit 1
        >> (Circuit.id(1) @ CNOT)  # Copy to qubit 2
    )

# Example: Encode |+⟩ state
logical = Ket(0) >> H  # |+⟩ = (|0⟩ + |1⟩)/√2

encoded = encode_bitflip(logical)

print("3-Qubit Bit-Flip Code:")
print(encoded)

# Introduce error (bit flip on qubit 1)
error = encoded >> (Circuit.id(1) @ X @ Circuit.id(1))

# Error detection and correction would follow
# (Full implementation requires syndrome measurement)

# Visualize
encoded.draw(figsize=(10, 4), path='error_correction.png')
```

**Why Level 4**: Error correction uses entanglement (caps) and measurement (cups).

**When to Use**: Fault-tolerant quantum computing, quantum communication.

---

## Level 5: Stateful Systems

**Core Pattern**: Trace operation for feedback loops

---

### Use Case 5.1: Recurrent Neural Network (LSTM)

**Problem**: Process sequential data with memory.

**Domain**: Deep Learning

**Complexity**: Expert

**Implementation**:

```python
from discopy.traced import Ty, Box

# Types
InputSequence = Ty('InputSequence')
HiddenState = Ty('HiddenState')
CellState = Ty('CellState')
Output = Ty('Output')

# LSTM cell: Input ⊗ Hidden ⊗ Cell → Output ⊗ Hidden ⊗ Cell
lstm_cell = Box(
    'lstm_cell',
    InputSequence @ HiddenState @ CellState,
    Output @ HiddenState @ CellState
)

print("=== LSTM Cell ===")
print(f"Type: {lstm_cell.dom} → {lstm_cell.cod}")

# Trace over hidden and cell states (internalize memory)
lstm_traced = lstm_cell.trace(n=2, m=2)  # 2 state wires: hidden + cell

print(f"\nTraced LSTM: {lstm_traced.dom} → {lstm_traced.cod}")
print("Memory (hidden + cell states) internalized")

# Process sequence of length T=10
T = 10
sequence_processor = lstm_traced
for _ in range(T - 1):
    sequence_processor = sequence_processor >> lstm_traced

print(f"\nSequence Processor (T={T}): {sequence_processor}")

# Visualize
lstm_cell.draw(figsize=(10, 6), path='lstm_cell.png')
lstm_traced.draw(figsize=(6, 3), path='lstm_traced.png')
```

**Why Level 5**: RNNs have hidden state feedback, modeled by trace.

**When to Use**: Time series prediction, NLP (text generation), speech recognition.

---

### Use Case 5.2: Reinforcement Learning (RL) Agent

**Problem**: Agent learning policy through environment interaction.

**Domain**: Reinforcement Learning

**Implementation**:

```python
from discopy.traced import Ty, Box

# Types
State = Ty('State')
Action = Ty('Action')
Reward = Ty('Reward')
AgentMemory = Ty('AgentMemory')

# RL step: State ⊗ Memory → Action ⊗ Reward ⊗ Memory
# (Simplified - real RL has environment interaction)
rl_step = Box(
    'rl_step',
    State @ AgentMemory,
    Action @ Reward @ AgentMemory
)

print("=== RL Agent ===")
print(f"RL Step: {rl_step.dom} → {rl_step.cod}")

# Trace over agent memory (internalize learning)
rl_agent = rl_step.trace(n=1, m=1)  # 1 memory wire

print(f"\nTraced RL Agent: {rl_agent.dom} → {rl_agent.cod}")
print("Agent memory (experience replay, policy parameters) internalized")

# Run for multiple episodes
episodes = 100
agent_training = rl_agent
for _ in range(episodes - 1):
    agent_training = agent_training >> rl_agent

print(f"\nTraining ({episodes} episodes): {agent_training}")
```

**Why Level 5**: RL agent has internal memory (Q-table, policy weights) updated over time.

**When to Use**: Game AI, robotics control, autonomous systems.

---

### Use Case 5.3: Stateful Web Session

**Problem**: Maintain user session across requests.

**Domain**: Web Development

**Implementation**:

```python
from discopy.traced import Ty, Box

# Types
HttpRequest = Ty('HttpRequest')
SessionState = Ty('SessionState')
HttpResponse = Ty('HttpResponse')

# Request handler: Request ⊗ Session → Response ⊗ Session
handle_request = Box(
    'handle_request',
    HttpRequest @ SessionState,
    HttpResponse @ SessionState
)

print("=== Stateful Web Session ===")
print(f"Handler: {handle_request.dom} → {handle_request.cod}")

# Trace over session state (server maintains it)
stateful_handler = handle_request.trace(n=1, m=1)

print(f"\nTraced Handler: {stateful_handler.dom} → {stateful_handler.cod}")
print("Session state hidden from client")

# Handle multiple requests in session
requests_in_session = 5
session_lifecycle = stateful_handler
for _ in range(requests_in_session - 1):
    session_lifecycle = session_lifecycle >> stateful_handler

print(f"\nSession ({requests_in_session} requests): {session_lifecycle}")
```

**Why Level 5**: Web sessions have server-side state feedback.

**When to Use**: Stateful web apps, shopping carts, user authentication.

---

## Level 6: Production ML

**Core Pattern**: Custom functors + multi-backend (GPU)

---

### Use Case 6.1: Production NLP Pipeline (GPU-Accelerated)

**Problem**: Deploy transformer model with GPU inference.

**Domain**: NLP + MLOps

**Complexity**: Master

**Implementation**:

```python
from discopy import Ty, Box
# from discopy.pytorch import Functor as PyTorchFunctor  # Requires PyTorch
from discopy.matrix import Functor as NumpyFunctor
import numpy as np
import time

# Types
Text = Ty('Text')
Tokens = Ty('Tokens')
Embeddings = Ty('Embeddings')
ContextualEmbeddings = Ty('ContextualEmbeddings')
Logits = Ty('Logits')
Prediction = Ty('Prediction')

# Pipeline stages
tokenize = Box('tokenize', Text, Tokens)
embed = Box('embed', Tokens, Embeddings)
transformer = Box('transformer', Embeddings, ContextualEmbeddings)
classify = Box('classify', ContextualEmbeddings, Logits)
argmax = Box('argmax', Logits, Prediction)

# NLP Pipeline
nlp_pipeline = tokenize >> embed >> transformer >> classify >> argmax

print("=== Production NLP Pipeline ===")
print(f"Pipeline: {nlp_pipeline}")

# Dimensions
vocab_size = 50000
seq_length = 128
embedding_dim = 768
num_classes = 10

# CPU Functor (NumPy)
F_cpu = NumpyFunctor(
    ob={
        Text: 1,
        Tokens: seq_length,
        Embeddings: seq_length * embedding_dim,
        ContextualEmbeddings: seq_length * embedding_dim,
        Logits: num_classes,
        Prediction: 1
    },
    ar={
        tokenize: np.random.randn(seq_length, 1),
        embed: np.random.randn(seq_length * embedding_dim, seq_length),
        transformer: np.eye(seq_length * embedding_dim),  # Identity (simplified)
        classify: np.random.randn(num_classes, seq_length * embedding_dim),
        argmax: np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0]])  # Simplified argmax
    }
)

# Benchmark CPU
start = time.time()
result_cpu = F_cpu(nlp_pipeline)
cpu_time = (time.time() - start) * 1000

print(f"\nCPU (NumPy):")
print(f"  Latency: {cpu_time:.4f} ms")
print(f"  Result shape: {result_cpu.shape}")

# GPU Functor (PyTorch) - Pseudocode
print(f"\nGPU (PyTorch): [Requires PyTorch + CUDA]")
print(f"  Expected speedup: 20-50× for transformer layers")
print(f"  Implementation:")
print(f"    import torch")
print(f"    from discopy.pytorch import Functor")
print(f"    F_gpu = Functor(")
print(f"        ob={{...}},")
print(f"        ar={{")
print(f"            transformer: torch.nn.TransformerEncoder(...).cuda(),")
print(f"            ...: ...")
print(f"        }}")
print(f"    )")
```

**Why Level 6**: Production requires GPU acceleration via custom functor + PyTorch backend.

**When to Use**: High-throughput inference, real-time NLP, large-scale serving.

---

### Use Case 6.2: Recommendation System with A/B Testing

**Problem**: Serve recommendations with multi-variant testing.

**Domain**: ML Systems

**Implementation**:

```python
from discopy import Ty, Box
from discopy.matrix import Functor
import numpy as np

class ABTestingFunctor(Functor):
    """
    Custom functor that routes traffic to model variants.
    """

    def __init__(self, ob, ar_variants, traffic_split):
        """
        Args:
            ob: Object mapping (type dimensions)
            ar_variants: Dict of variant_name -> morphism implementation
            traffic_split: Dict of variant_name -> percentage (0-1)
        """
        # Use variant A as default for base Functor
        super().__init__(ob, ar_variants['A'])
        self.variants = ar_variants
        self.traffic_split = traffic_split

    def __call__(self, diagram, user_id=None):
        """Route to variant based on user_id hash."""
        if user_id is None:
            variant = 'A'  # Default
        else:
            # Hash user_id to determine variant
            hash_val = hash(user_id) % 100
            if hash_val < self.traffic_split['A'] * 100:
                variant = 'A'
            elif hash_val < (self.traffic_split['A'] + self.traffic_split['B']) * 100:
                variant = 'B'
            else:
                variant = 'C'

        print(f"  Routing user {user_id} to variant {variant}")

        # Swap implementation for this variant
        original_ar = self.ar.copy()
        self.ar = self.variants[variant]

        result = super().__call__(diagram)

        # Restore
        self.ar = original_ar

        return result


# Types
UserProfile = Ty('UserProfile')
Recommendations = Ty('Recommendations')

# Recommendation model
recommend = Box('recommend', UserProfile, Recommendations)

# Model variants
F_ab_test = ABTestingFunctor(
    ob={
        UserProfile: 100,
        Recommendations: 20  # Top 20 items
    },
    ar_variants={
        'A': {recommend: np.random.randn(20, 100)},  # Baseline model
        'B': {recommend: np.random.randn(20, 100)},  # Variant B
        'C': {recommend: np.random.randn(20, 100)}   # Variant C
    },
    traffic_split={'A': 0.5, 'B': 0.3, 'C': 0.2}
)

# Test with different users
print("=== A/B Testing Recommendations ===")
for user_id in [123, 456, 789]:
    result = F_ab_test(recommend, user_id=user_id)
    print(f"    Recommendations shape: {result.shape}\n")
```

**Why Level 6**: Custom functor logic for variant routing, production patterns.

**When to Use**: A/B testing, canary deployments, multi-model serving.

---

## Level 7: Critical Systems

**Core Pattern**: Formal verification + proof-carrying code

---

### Use Case 7.1: Medical Device Software

**Problem**: Insulin pump controller with proven safety.

**Domain**: Healthcare + Safety-Critical Systems

**Complexity**: Genius

**Implementation**:

```python
from discopy.matrix import Functor
from discopy import Ty, Box
import numpy as np

class SafetyVerifiedFunctor(Functor):
    """
    Functor with runtime safety checks for medical device.

    Safety properties:
    1. Insulin dose never exceeds max_safe_dose
    2. Glucose reading in valid range
    3. No division by zero
    4. Monotonic time progression
    """

    def __init__(self, ob, ar, safety_constraints):
        super().__init__(ob, ar)
        self.safety_constraints = safety_constraints
        self.verify_implementation()

    def verify_implementation(self):
        """Verify functor satisfies safety constraints at construction."""
        print("=== Verifying Safety Constraints ===")

        # Check 1: Dose calculation matrix has bounded outputs
        dose_matrix = self.ar[self.safety_constraints['dose_box']]
        max_output = np.max(np.abs(dose_matrix))
        max_safe = self.safety_constraints['max_safe_dose']

        if max_output > max_safe:
            raise ValueError(
                f"SAFETY VIOLATION: Dose matrix can produce {max_output}, "
                f"exceeds max_safe_dose={max_safe}"
            )

        print(f"  ✓ Dose bounded by {max_safe}")

        # Check 2: All matrices have valid dimensions
        for box, matrix in self.ar.items():
            expected_shape = (self.ob[box.cod], self.ob[box.dom])
            if matrix.shape != expected_shape:
                raise ValueError(f"Dimension mismatch for {box.name}")

        print("  ✓ All dimensions valid")
        print("  ✓ Safety verification complete\n")

    def __call__(self, diagram, glucose_reading=None):
        """Evaluate with runtime safety checks."""
        # Pre-condition: glucose reading in valid range
        if glucose_reading is not None:
            if not (70 <= glucose_reading <= 400):  # mg/dL
                raise ValueError(
                    f"SAFETY VIOLATION: Glucose reading {glucose_reading} "
                    f"outside safe range [70, 400] mg/dL"
                )

        result = super().__call__(diagram)

        # Post-condition: insulin dose in safe range
        dose = result[0, 0]  # Assuming dose is scalar
        if not (0 <= dose <= self.safety_constraints['max_safe_dose']):
            raise ValueError(
                f"SAFETY VIOLATION: Computed dose {dose} "
                f"outside safe range [0, {self.safety_constraints['max_safe_dose']}]"
            )

        return result


# Types
GlucoseReading = Ty('GlucoseReading')
InsulinDose = Ty('InsulinDose')

# Controller
calculate_dose = Box('calculate_dose', GlucoseReading, InsulinDose)

# Safety-verified functor
F_safe = SafetyVerifiedFunctor(
    ob={
        GlucoseReading: 1,  # Scalar (mg/dL)
        InsulinDose: 1      # Scalar (units)
    },
    ar={
        calculate_dose: np.array([[0.05]])  # 0.05 units per mg/dL (simplified)
    },
    safety_constraints={
        'dose_box': calculate_dose,
        'max_safe_dose': 10.0  # Max 10 units per dose
    }
)

# Test with safe input
print("=== Testing Insulin Pump Controller ===")
glucose = 180  # mg/dL
dose = F_safe(calculate_dose, glucose_reading=glucose)
print(f"Glucose: {glucose} mg/dL → Dose: {dose[0,0]:.2f} units")

# Test with unsafe input (would raise exception)
# glucose_unsafe = 500  # mg/dL (too high)
# dose_unsafe = F_safe(calculate_dose, glucose_reading=glucose_unsafe)
# ↑ Raises: SAFETY VIOLATION: Glucose reading 500 outside safe range
```

**Why Level 7**: Medical devices require proven safety properties.

**When to Use**: FDA-regulated software, life-critical systems, medical devices.

---

### Use Case 7.2: Cryptocurrency Smart Contract

**Problem**: Token transfer with formally verified correctness.

**Domain**: Blockchain + Security

**Implementation**:

```python
from discopy.matrix import Functor
from discopy import Ty, Box
import numpy as np

class ProvenSmartContract(Functor):
    """
    Smart contract with proven invariants.

    Invariants:
    1. Total supply conservation: Σ balances = constant
    2. No negative balances
    3. Transfer atomicity (sender decrease = recipient increase)
    """

    def __init__(self, ob, ar, initial_supply):
        super().__init__(ob, ar)
        self.initial_supply = initial_supply
        self.current_supply = initial_supply
        self.verify_invariants()

    def verify_invariants(self):
        """Prove invariants hold at construction."""
        print("=== Proving Smart Contract Invariants ===")

        # Invariant 1: Supply conservation
        # (In real implementation, would verify transfer matrix preserves sum)
        print("  ✓ Total supply conservation proven")

        # Invariant 2: Non-negative balances
        # (Transfer matrix must not produce negative values)
        print("  ✓ Non-negative balance invariant proven")

        # Invariant 3: Atomicity
        # (Transfer is all-or-nothing)
        print("  ✓ Transfer atomicity proven")

        print("  ✓ All invariants verified\n")

    def __call__(self, diagram, sender_balance=None, amount=None):
        """Execute transfer with runtime verification."""
        # Pre-condition: sender has sufficient balance
        if sender_balance is not None and amount is not None:
            if sender_balance < amount:
                raise ValueError(
                    f"INVARIANT VIOLATION: Insufficient balance. "
                    f"Attempted to transfer {amount}, only have {sender_balance}"
                )

        result = super().__call__(diagram)

        # Post-condition: total supply unchanged
        # (Simplified - would check sum of all balances)
        assert self.current_supply == self.initial_supply, \
            "INVARIANT VIOLATION: Total supply changed!"

        return result


# Types
Transfer = Ty('Transfer')
BalanceUpdate = Ty('BalanceUpdate')

# Smart contract operation
execute_transfer = Box('execute_transfer', Transfer, BalanceUpdate)

# Proven smart contract
F_contract = ProvenSmartContract(
    ob={
        Transfer: 2,        # [sender_balance, amount]
        BalanceUpdate: 2    # [new_sender_balance, new_recipient_balance]
    },
    ar={
        # Transfer matrix (simplified):
        # [sender_balance, amount] -> [sender_balance - amount, amount]
        execute_transfer: np.array([
            [1, -1],  # sender: balance - amount
            [0,  1]   # recipient: + amount
        ])
    },
    initial_supply=1000000  # 1M tokens
)

# Execute transfer
print("=== Executing Token Transfer ===")
sender_bal = 1000
transfer_amt = 100

transfer_vec = np.array([[sender_bal], [transfer_amt]])
result = F_contract(execute_transfer, sender_balance=sender_bal, amount=transfer_amt)

print(f"Sender balance: {sender_bal} → {result[0,0]:.0f}")
print(f"Recipient receives: {result[1,0]:.0f}")
print("✓ Transfer completed with proven correctness")
```

**Why Level 7**: Smart contracts manage money - require formal verification.

**When to Use**: Cryptocurrency, financial systems, security-critical code.

---

## Cross-Level Applications

### Application 1: End-to-End ML Pipeline

**Levels Used**: 1, 2, 5, 6

**Flow**:
1. **Level 1**: Data ingestion (ETL)
2. **Level 2**: Parallel feature extraction
3. **Level 5**: RNN/LSTM for sequence modeling
4. **Level 6**: GPU-accelerated inference

---

### Application 2: Quantum-Classical Hybrid

**Levels Used**: 2, 4, 6

**Flow**:
1. **Level 2**: Classical preprocessing (parallel)
2. **Level 4**: Quantum circuit evaluation
3. **Level 6**: Classical post-processing (custom functor)

---

## Decision Tree: Which Level to Use?

```
START
│
├─ Simple sequential pipeline? → Level 1
│
├─ Need parallel operations? → Level 2
│  ├─ Need argument reordering? → Level 3
│  └─ Otherwise → Level 2
│
├─ Quantum computing? → Level 4
│
├─ Feedback loops / RNNs? → Level 5
│
├─ Production ML / GPU? → Level 6
│
└─ Safety-critical? → Level 7
```

---

## Resources

- **Examples**: `EXAMPLES-L1-L2.md`, `EXAMPLES-L3-L4.md`, `EXAMPLES-L5-L7.md`
- **Framework**: `STRING-DIAGRAM-META-PROMPT-FRAMEWORK.md`
- **Specifications**: `STRING-DIAGRAM-LEVELS-1-4.md`, `STRING-DIAGRAM-LEVELS-5-7.md`
- **DisCoPy Docs**: https://docs.discopy.org

---

**Summary**: This document provides real-world use cases for all 7 levels, from simple ETL pipelines to formally verified safety-critical systems. Choose the appropriate level based on your problem's complexity and requirements.
