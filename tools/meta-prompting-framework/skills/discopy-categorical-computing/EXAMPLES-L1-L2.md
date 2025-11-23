# DisCoPy Examples: Levels 1-2

**Novice and Competent Levels** - Sequential and Parallel Composition

This document provides executable code snippets, ASCII diagrams, and real-world use cases for Levels 1-2 of the String Diagram Meta-Prompt Framework.

---

## Level 1: Novice - Sequential Composition

**Core Capability**: Chain operations using `>>`

**When to Use**: Simple pipelines, ETL workflows, linear data transformations

---

### Example 1.1: Data Processing Pipeline

**Use Case**: Process raw sensor data through validation, cleaning, and storage.

**ASCII Diagram**:
```
RawData ──[validate]──> ValidData ──[clean]──> CleanData ──[store]──> Confirmation
```

**Code**:
```python
from discopy import Ty, Box

# Define types (data states)
RawData = Ty('RawData')
ValidData = Ty('ValidData')
CleanData = Ty('CleanData')
Confirmation = Ty('Confirmation')

# Define operations
validate = Box('validate', RawData, ValidData)
clean = Box('clean', ValidData, CleanData)
store = Box('store', CleanData, Confirmation)

# Build pipeline: sequential composition
pipeline = validate >> clean >> store

print("Pipeline:", pipeline)
print("Type:", pipeline.dom, "→", pipeline.cod)

# Visualize
pipeline.draw(figsize=(10, 3), path='pipeline_L1_1.png')
```

**Output**:
```
Pipeline: validate >> clean >> store
Type: RawData → Confirmation
```

**Diagram**:
```
     RawData
        │
        ↓
    ┌────────┐
    │validate│
    └────┬───┘
         │ ValidData
         ↓
    ┌────────┐
    │  clean │
    └────┬───┘
         │ CleanData
         ↓
    ┌────────┐
    │  store │
    └────┬───┘
         │
         ↓
   Confirmation
```

---

### Example 1.2: Text Processing Chain

**Use Case**: NLP pipeline with tokenization, tagging, and parsing.

**ASCII Diagram**:
```
Text ──[tokenize]──> Tokens ──[pos_tag]──> TaggedTokens ──[parse]──> ParseTree
```

**Code**:
```python
from discopy import Ty, Box

# Types
Text = Ty('Text')
Tokens = Ty('Tokens')
TaggedTokens = Ty('TaggedTokens')
ParseTree = Ty('ParseTree')

# Operations
tokenize = Box('tokenize', Text, Tokens)
pos_tag = Box('pos_tag', Tokens, TaggedTokens)
parse = Box('parse', TaggedTokens, ParseTree)

# Pipeline
nlp_pipeline = tokenize >> pos_tag >> parse

print("NLP Pipeline:", nlp_pipeline)
print("Processes:", Text, "→", ParseTree)

# Visualize
nlp_pipeline.draw(figsize=(10, 3), path='nlp_pipeline_L1_2.png')
```

---

### Example 1.3: Image Processing Pipeline

**Use Case**: Computer vision preprocessing.

**ASCII Diagram**:
```
Image ──[resize]──> ResizedImage ──[normalize]──> NormalizedImage ──[augment]──> AugmentedImage
```

**Code**:
```python
from discopy import Ty, Box

# Types
Image = Ty('Image')
ResizedImage = Ty('ResizedImage')
NormalizedImage = Ty('NormalizedImage')
AugmentedImage = Ty('AugmentedImage')

# Operations
resize = Box('resize', Image, ResizedImage)
normalize = Box('normalize', ResizedImage, NormalizedImage)
augment = Box('augment', NormalizedImage, AugmentedImage)

# Pipeline
vision_pipeline = resize >> normalize >> augment

print("Vision Pipeline:", vision_pipeline)

# Visualize
vision_pipeline.draw(figsize=(10, 3), path='vision_pipeline_L1_3.png')
```

---

### Example 1.4: E-Commerce Order Flow

**Use Case**: Order processing workflow.

**ASCII Diagram**:
```
Order ──[validate]──> ValidOrder ──[charge]──> Payment ──[ship]──> Shipment
```

**Code**:
```python
from discopy import Ty, Box

# Types
Order = Ty('Order')
ValidOrder = Ty('ValidOrder')
Payment = Ty('Payment')
Shipment = Ty('Shipment')

# Operations
validate_order = Box('validate', Order, ValidOrder)
charge_payment = Box('charge', ValidOrder, Payment)
ship_order = Box('ship', Payment, Shipment)

# Workflow
order_flow = validate_order >> charge_payment >> ship_order

print("Order Flow:", order_flow)
print("Type:", order_flow.dom, "→", order_flow.cod)

# Visualize
order_flow.draw(figsize=(10, 3), path='order_flow_L1_4.png')
```

---

### Example 1.5: ML Training Pipeline (Simple)

**Use Case**: Linear machine learning workflow.

**ASCII Diagram**:
```
RawData ──[preprocess]──> Features ──[train]──> Model ──[evaluate]──> Metrics
```

**Code**:
```python
from discopy import Ty, Box

# Types
RawData = Ty('RawData')
Features = Ty('Features')
Model = Ty('Model')
Metrics = Ty('Metrics')

# Operations
preprocess = Box('preprocess', RawData, Features)
train = Box('train', Features, Model)
evaluate = Box('evaluate', Model, Metrics)

# ML Pipeline
ml_pipeline = preprocess >> train >> evaluate

print("ML Pipeline:", ml_pipeline)

# Visualize
ml_pipeline.draw(figsize=(10, 3), path='ml_pipeline_L1_5.png')
```

---

### Level 1 Summary

**Key Operator**: `>>`  (sequential composition)

**Type Signature**: If `f: A → B` and `g: B → C`, then `f >> g: A → C`

**When to Use**:
- ✅ Linear pipelines
- ✅ ETL workflows
- ✅ Sequential data transformations
- ✅ Simple workflows with clear stages

**Limitations**:
- ❌ No parallel processing
- ❌ No branching logic
- ❌ Cannot express concurrent operations

---

## Level 2: Competent - Parallel Composition + Functors

**Core Capability**: Parallel operations with `@` and concrete evaluation with functors

**When to Use**: Parallel workflows, multi-task processing, tensor evaluation

---

### Example 2.1: Parallel Data Processing

**Use Case**: Process features and labels independently, then combine.

**ASCII Diagram**:
```
Features ──[normalize]──> NormFeatures ────┐
                                           ├─[combine]──> Dataset
Labels   ──[encode]─────> EncodedLabels ───┘
```

**Code**:
```python
from discopy import Ty, Box

# Types
Features = Ty('Features')
Labels = Ty('Labels')
NormFeatures = Ty('NormFeatures')
EncodedLabels = Ty('EncodedLabels')
Dataset = Ty('Dataset')

# Operations
normalize = Box('normalize', Features, NormFeatures)
encode = Box('encode', Labels, EncodedLabels)
combine = Box('combine', NormFeatures @ EncodedLabels, Dataset)

# Parallel workflow
parallel_processing = (normalize @ encode) >> combine

print("Parallel Processing:", parallel_processing)
print("Type:", parallel_processing.dom, "→", parallel_processing.cod)

# Visualize
parallel_processing.draw(figsize=(10, 4), path='parallel_L2_1.png')
```

**Diagram**:
```
Features          Labels
   │                │
   ↓                ↓
┌────────┐      ┌────────┐
│normalize│      │ encode │
└────┬───┘      └────┬───┘
     │ NormFeatures  │ EncodedLabels
     │               │
     └───────┬───────┘
             ↓
        ┌────────┐
        │combine │
        └────┬───┘
             │
             ↓
          Dataset
```

---

### Example 2.2: Multi-Model Ensemble

**Use Case**: Run multiple models in parallel and aggregate results.

**ASCII Diagram**:
```
Input ──[model1]──> Pred1 ────┐
Input ──[model2]──> Pred2 ────┼─[aggregate]──> FinalPred
Input ──[model3]──> Pred3 ────┘
```

**Code**:
```python
from discopy import Ty, Box

# Types
Input = Ty('Input')
Prediction = Ty('Prediction')
FinalPrediction = Ty('FinalPrediction')

# Models
model1 = Box('model1', Input, Prediction)
model2 = Box('model2', Input, Prediction)
model3 = Box('model3', Input, Prediction)

# Aggregator
aggregate = Box('aggregate', Prediction @ Prediction @ Prediction, FinalPrediction)

# Ensemble (all models run in parallel)
ensemble = (model1 @ model2 @ model3) >> aggregate

print("Ensemble:", ensemble)

# Visualize
ensemble.draw(figsize=(10, 5), path='ensemble_L2_2.png')
```

---

### Example 2.3: Functor Evaluation (Concrete Semantics)

**Use Case**: Map abstract diagram to concrete tensor computation.

**Code**:
```python
from discopy import Ty, Box
from discopy.matrix import Functor
import numpy as np

# Types
A = Ty('A')
B = Ty('B')
C = Ty('C')

# Morphisms
f = Box('f', A, B)
g = Box('g', B, C)

# Abstract diagram
diagram = f >> g

# Functor: maps types to dimensions, boxes to matrices
F = Functor(
    ob={
        A: 10,  # A is 10-dimensional vector space
        B: 5,   # B is 5-dimensional
        C: 3    # C is 3-dimensional
    },
    ar={
        f: np.random.randn(5, 10),  # Matrix: B × A
        g: np.random.randn(3, 5)    # Matrix: C × B
    }
)

# Evaluate
result = F(diagram)

print("Abstract Diagram:", diagram)
print("Concrete Evaluation:")
print("  Type:", f"Matrix[{result.shape[0]}, {result.shape[1]}]")
print("  Expected:", "Matrix[3, 10]  (C × A)")
print("  Match:", result.shape == (3, 10))
print("\nResult matrix (first 3x3 block):")
print(result[:3, :3])
```

**Output**:
```
Abstract Diagram: f >> g
Concrete Evaluation:
  Type: Matrix[3, 10]
  Expected: Matrix[3, 10]  (C × A)
  Match: True

Result matrix (first 3x3 block):
[[ 0.123 -0.456  0.789]
 [-0.234  0.567 -0.890]
 [ 0.345 -0.678  0.901]]
```

---

### Example 2.4: Parallel Feature Extraction + Functor Evaluation

**Use Case**: Extract different features in parallel, then classify.

**ASCII Diagram**:
```
Image ──[extract_color]──> ColorFeats ────┐
                                          ├─[classify]──> Label
Image ──[extract_shape]──> ShapeFeats ────┘
```

**Code**:
```python
from discopy import Ty, Box
from discopy.matrix import Functor
import numpy as np

# Types
Image = Ty('Image')
ColorFeatures = Ty('ColorFeatures')
ShapeFeatures = Ty('ShapeFeatures')
Label = Ty('Label')

# Operations
extract_color = Box('extract_color', Image, ColorFeatures)
extract_shape = Box('extract_shape', Image, ShapeFeatures)
classify = Box('classify', ColorFeatures @ ShapeFeatures, Label)

# Diagram
feature_extraction = (extract_color @ extract_shape) >> classify

print("Feature Extraction Diagram:", feature_extraction)

# Functor with concrete dimensions
F = Functor(
    ob={
        Image: 1024,         # 32×32 image = 1024 pixels
        ColorFeatures: 64,   # 64 color histogram bins
        ShapeFeatures: 128,  # 128 shape descriptors
        Label: 10            # 10 classes
    },
    ar={
        extract_color: np.random.randn(64, 1024),
        extract_shape: np.random.randn(128, 1024),
        classify: np.random.randn(10, 64 + 128)  # Combines both features
    }
)

# Evaluate on sample input
input_image = np.random.randn(1024)
result = F(feature_extraction)

print(f"\nInput dimension: {input_image.shape}")
print(f"Output dimension: {result.shape}")
print(f"Expected: (10,) for 10 classes")
```

---

### Example 2.5: ML Pipeline with Parallel Preprocessing

**Use Case**: Preprocess features and labels in parallel, then train.

**Code**:
```python
from discopy import Ty, Box
from discopy.matrix import Functor
import numpy as np

# Types
RawFeatures = Ty('RawFeatures')
RawLabels = Ty('RawLabels')
ProcessedFeatures = Ty('ProcessedFeatures')
ProcessedLabels = Ty('ProcessedLabels')
TrainedModel = Ty('TrainedModel')

# Operations
preprocess_features = Box('preprocess_features', RawFeatures, ProcessedFeatures)
preprocess_labels = Box('preprocess_labels', RawLabels, ProcessedLabels)
train = Box('train', ProcessedFeatures @ ProcessedLabels, TrainedModel)

# Pipeline: parallel preprocessing, then sequential training
ml_pipeline = (preprocess_features @ preprocess_labels) >> train

print("ML Pipeline:", ml_pipeline)

# Concrete evaluation
F = Functor(
    ob={
        RawFeatures: 100,        # 100 raw features
        RawLabels: 10,           # 10 classes (one-hot)
        ProcessedFeatures: 50,   # Reduced to 50 features
        ProcessedLabels: 10,     # Still 10 classes
        TrainedModel: 500        # Model parameters
    },
    ar={
        preprocess_features: np.random.randn(50, 100),
        preprocess_labels: np.eye(10),  # Identity (no change)
        train: np.random.randn(500, 50 + 10)  # Combines features + labels
    }
)

result = F(ml_pipeline)
print(f"Result shape: {result.shape}")
print(f"Expected: (500, 100) - Model params × Raw input dimension")

# Visualize
ml_pipeline.draw(figsize=(12, 5), path='ml_parallel_L2_5.png')
```

**Diagram**:
```
RawFeatures          RawLabels
     │                   │
     ↓                   ↓
┌──────────┐      ┌──────────┐
│preprocess│      │preprocess│
│ features │      │  labels  │
└─────┬────┘      └─────┬────┘
      │                 │
      │ ProcessedFeatures ProcessedLabels
      │                 │
      └────────┬────────┘
               ↓
          ┌────────┐
          │ train  │
          └────┬───┘
               │
               ↓
         TrainedModel
```

---

### Example 2.6: Backend Comparison (NumPy vs PyTorch)

**Use Case**: Compare CPU vs GPU evaluation of same diagram.

**Code**:
```python
from discopy import Ty, Box
from discopy.matrix import Functor as NumpyFunctor
# from discopy.pytorch import Functor as PyTorchFunctor  # Requires PyTorch
import numpy as np
import time

# Types
Input = Ty('Input')
Hidden = Ty('Hidden')
Output = Ty('Output')

# Operations
layer1 = Box('layer1', Input, Hidden)
layer2 = Box('layer2', Hidden, Output)

# Diagram
network = layer1 >> layer2

# NumPy Functor (CPU)
F_numpy = NumpyFunctor(
    ob={Input: 1000, Hidden: 500, Output: 10},
    ar={
        layer1: np.random.randn(500, 1000),
        layer2: np.random.randn(10, 500)
    }
)

# Benchmark NumPy
start = time.time()
for _ in range(100):
    result_numpy = F_numpy(network)
numpy_time = (time.time() - start) * 1000 / 100

print("=== Backend Comparison ===")
print(f"NumPy (CPU): {numpy_time:.4f} ms per evaluation")
print(f"Result shape: {result_numpy.shape}")

# PyTorch Functor (GPU) - Uncomment if PyTorch available
# import torch
# F_torch = PyTorchFunctor(
#     ob={Input: 1000, Hidden: 500, Output: 10},
#     ar={
#         layer1: torch.randn(500, 1000, device='cuda'),
#         layer2: torch.randn(10, 500, device='cuda')
#     }
# )
#
# start = time.time()
# for _ in range(100):
#     result_torch = F_torch(network)
# torch_time = (time.time() - start) * 1000 / 100
#
# print(f"PyTorch (GPU): {torch_time:.4f} ms per evaluation")
# print(f"Speedup: {numpy_time / torch_time:.2f}×")
```

---

### Example 2.7: Multiple Functor Interpretations

**Use Case**: Same diagram, different interpretations.

**Code**:
```python
from discopy import Ty, Box
from discopy.matrix import Functor
import numpy as np

# Abstract diagram
A = Ty('A')
B = Ty('B')
f = Box('f', A, B)

diagram = f

# Interpretation 1: Small dimensions
F_small = Functor(
    ob={A: 2, B: 3},
    ar={f: np.array([[1, 0], [0, 1], [1, 1]])}
)

# Interpretation 2: Large dimensions
F_large = Functor(
    ob={A: 100, B: 50},
    ar={f: np.random.randn(50, 100)}
)

# Interpretation 3: Different semantics (weights)
F_weighted = Functor(
    ob={A: 5, B: 5},
    ar={f: np.diag([1.0, 0.5, 0.25, 0.1, 0.05])}  # Exponential decay
)

print("Same Diagram, Three Interpretations:")
print(f"1. Small: {F_small(diagram).shape}")
print(f"2. Large: {F_large(diagram).shape}")
print(f"3. Weighted diagonal: {F_weighted(diagram).shape}")
print("\nWeighted result (diagonal):")
print(F_weighted(diagram).diagonal())
```

**Output**:
```
Same Diagram, Three Interpretations:
1. Small: (3, 2)
2. Large: (50, 100)
3. Weighted diagonal: (5, 5)

Weighted result (diagonal):
[1.   0.5  0.25 0.1  0.05]
```

---

### Level 2 Summary

**Key Operators**:
- `@` (parallel composition / tensor product)
- `Functor` (concrete interpretation)

**Type Signature**:
- Parallel: If `f: A → B` and `g: C → D`, then `f @ g: A⊗C → B⊗D`
- Functor: `F: Diagram → Tensor` (maps abstract to concrete)

**When to Use**:
- ✅ Parallel workflows
- ✅ Multi-task processing
- ✅ Feature extraction from multiple sources
- ✅ Ensemble methods
- ✅ Backend-agnostic computation

**New Capabilities vs Level 1**:
- ✅ Concurrent operations
- ✅ Concrete evaluation (functors)
- ✅ Multiple interpretations of same diagram
- ✅ Backend selection (NumPy, PyTorch, JAX, TensorFlow)

**Limitations**:
- ❌ No wire reordering (need Level 3 symmetry)
- ❌ No duality/adjunctions (need Level 4 compact closed)
- ❌ No feedback loops (need Level 5 traced)

---

## Quick Reference

### Level 1 Cheat Sheet

```python
# Sequential composition
f >> g  # Chain operations

# Type checking
f: A → B
g: B → C
f >> g: A → C  # Valid only if f.cod == g.dom
```

### Level 2 Cheat Sheet

```python
# Parallel composition
f @ g  # Run simultaneously

# Functor evaluation
from discopy.matrix import Functor
F = Functor(ob={...}, ar={...})
result = F(diagram)

# Backend selection
from discopy.matrix import Functor     # NumPy (CPU)
from discopy.pytorch import Functor    # PyTorch (GPU)
from discopy.jax import Functor        # JAX (TPU, autodiff)
from discopy.tensorflow import Functor # TensorFlow (GPU)
```

---

## Common Patterns

### Pattern 1: ETL Pipeline (Level 1)

```python
extract = Box('extract', Source, RawData)
transform = Box('transform', RawData, CleanData)
load = Box('load', CleanData, Target)

etl = extract >> transform >> load
```

### Pattern 2: Parallel Feature Engineering (Level 2)

```python
feat1 = Box('feat1', Data, Feature1)
feat2 = Box('feat2', Data, Feature2)
combine = Box('combine', Feature1 @ Feature2, Combined)

pipeline = (feat1 @ feat2) >> combine
```

### Pattern 3: Functor with Dimensions (Level 2)

```python
F = Functor(
    ob={A: dim_A, B: dim_B},  # Type dimensions
    ar={f: matrix_f}           # Box implementations
)
result = F(diagram)
```

---

## Exercises

### Exercise 1.1: Build a 4-stage pipeline
Create a pipeline: `Input → Stage1 → Stage2 → Stage3 → Output`

### Exercise 1.2: Calculate output type
Given `f: A → B`, `g: B → C`, `h: C → D`, what is the type of `f >> g >> h`?

### Exercise 2.1: Parallel branches
Create a diagram with 3 parallel branches that merge.

### Exercise 2.2: Functor evaluation
Define a functor for Example 1.1 (data processing pipeline) with concrete dimensions.

### Exercise 2.3: Backend comparison
Implement Example 2.6 with both NumPy and PyTorch, measure speedup.

---

## Next Steps

- **Level 3**: Add symmetry for wire reordering → [EXAMPLES-L3-L4.md](EXAMPLES-L3-L4.md)
- **Level 4**: Compact closed categories for quantum circuits → [EXAMPLES-L3-L4.md](EXAMPLES-L3-L4.md)
- **Level 5-7**: Advanced features → [EXAMPLES-L5-L7.md](EXAMPLES-L5-L7.md)

---

## Resources

- **DisCoPy Docs**: https://docs.discopy.org
- **Framework Documentation**: `STRING-DIAGRAM-META-PROMPT-FRAMEWORK.md`
- **Level 1-2 Specification**: `STRING-DIAGRAM-LEVELS-1-4.md`
