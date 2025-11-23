# Wolfram Language Quick Reference: Category Theory & Meta-Programming

## Rapid Lookup Guide

---

## Categorical Mappings

### Core Correspondences

| Wolfram | Category Theory | Symbol | Description |
|---------|----------------|--------|-------------|
| `Rule (->)` | Morphism | f: A → B | Immediate transformation |
| `RuleDelayed (:>)` | Morphism | f: A ⇒ B | Delayed transformation |
| `ReplaceAll (/.)` | Functor | F: C → D | Structure-preserving map |
| `Map` | List Functor | F: List(A) → List(B) | Element-wise application |
| `Apply` | Head Functor | F: f[args] → g[args] | Structure change |
| `Composition (@*)` | ∘ | f ∘ g | Morphism composition |
| `Cases` | Pullback | pb | Filtered subobject |
| `Pattern (_)` | Object | A ∈ Ob(C) | Type/structure |
| `Hold` | Quotation | ⌜expr⌝ | Suspend evaluation |

### Advanced Structures

| Wolfram | Category Theory | Description |
|---------|----------------|-------------|
| MultiwaySystem | n-Fold Category | Higher categorical paths |
| Rulial Space | (∞,1)-Topos | Universe of computations |
| Hypergraph | Adhesive Category Object | Compositional graph |
| DPO Rewrite | Pushout | L ← K → R |
| Categorica | Applied CT Framework | Computational categories |

---

## Syntax Quick Reference

### Pattern Matching

```wolfram
_              (* Blank: any expression *)
__             (* BlankSequence: sequence of 1+ *)
___            (* BlankNullSequence: sequence of 0+ *)
x_             (* Named pattern *)
x_Integer      (* Typed pattern *)
x_ /; test     (* Conditional pattern *)
x_:default     (* Optional with default *)
Repeated[p]    (* Pattern repetition *)
```

### Rule Application

```wolfram
expr /. rule                (* ReplaceAll *)
expr //. rule               (* ReplaceRepeated *)
Replace[expr, rule]         (* Replace at top level *)
Replace[expr, rule, {1}]    (* Replace at level 1 *)
```

### Functional Composition

```wolfram
f @* g         (* Left composition: f(g(x)) *)
f /* g         (* Right composition: g(f(x)) *)
f @ x          (* Apply: f[x] *)
x // f         (* Postfix: f[x] *)
f /@ list      (* Map: Map[f, list] *)
f @@@ list     (* Apply at level 1 *)
```

### Holding/Evaluation

```wolfram
Hold[expr]             (* Hold evaluation *)
HoldForm[expr]         (* Hold and display *)
Unevaluated[expr]      (* Temporary hold *)
ToExpression[string]   (* String → Expression *)
ToString[expr]         (* Expression → String *)
FullForm[expr]         (* Internal representation *)
```

---

## Meta-Programming Patterns

### Code Generation Template

```wolfram
(* 1. Define specification *)
spec = <|
  "Name" -> functionName,
  "Args" -> argumentList,
  "Body" -> functionBody
|>

(* 2. Generate code *)
generateFunction[spec_] := ToExpression[
  spec["Name"] <> "[" <>
  StringRiffle[spec["Args"], ","] <>
  "] := " <> spec["Body"]
]

(* 3. Execute generator *)
generateFunction[spec]
```

### Template System

```wolfram
(* String template *)
t = StringTemplate["
function `name`(`params`) {
  return `body`;
}
"]

(* Use template *)
t[<|
  "name" -> "myFunc",
  "params" -> "x, y",
  "body" -> "x + y"
|>]
```

### Macro Pattern

```wolfram
(* Define macro *)
withLogging[expr_] := Module[{result},
  Print["Executing: ", HoldForm[expr]];
  result = expr;
  Print["Result: ", result];
  result
]

(* Use macro *)
withLogging[computation]
```

### AST Walking

```wolfram
(* Transform AST *)
transformAST[expr_, rules_] := expr //. rules

(* Example *)
transformAST[
  Hold[a + b + c],
  Plus -> Times
]
(* → Hold[a * b * c] *)
```

---

## Self-Building Patterns

### API Generation

```wolfram
(* Define API *)
api = APIFunction[
  {"param1" -> "Type1", "param2" -> "Type2"},
  processingFunction
]

(* Deploy *)
url = CloudDeploy[api, "path"]

(* Generate embedding *)
EmbedCode[url, "JavaScript"]
```

### Form Generation

```wolfram
(* Define form *)
form = FormFunction[
  {"field1" -> "Type1", "field2" -> "Type2"},
  handlerFunction
]

(* Deploy *)
CloudDeploy[form, "formPath"]
```

### Automation

```wolfram
(* Scheduled task *)
ScheduledTask[
  computationFunction,
  Quantity[interval, "Units"]
]

(* Auto-refresh *)
AutoRefreshed[
  expression,
  Quantity[interval, "Units"]
]

(* Event-driven *)
MailReceiverFunction[handler]
ChannelReceiverFunction[handler]
```

---

## Sophistication Levels

### Level 1: Simple Symbolic

```wolfram
(* Basic transformations *)
Expand[(x + y)^2]
Factor[x^2 - 1]
expr /. x -> 5
Map[f, list]
```

**Complexity**: O(n) to O(n log n)
**Category**: Basic functors

### Level 2: Advanced Patterns

```wolfram
(* Conditional patterns *)
Cases[data, x_ /; condition[x]]
ReplaceAll[expr, {pattern1 :> result1, pattern2 :> result2}]
SequenceCases[list, {a_, b_, c_} /; a + b == c]
```

**Complexity**: O(n) to O(n²)
**Category**: Natural transformations

### Level 3: Algorithmic

```wolfram
(* Built-in algorithms *)
FindShortestPath[graph, start, end]
Minimize[f[x, y], {x, y}]
DSolve[equation, y[x], x]
```

**Complexity**: Polynomial to exponential
**Category**: Monoidal categories

### Level 4: Knowledge Integration

```wolfram
(* Knowledge-based *)
Entity["City", "NewYork"]["Population"]
WolframAlpha["query"]
GeoDistance[city1, city2]
ElementData["Gold", "AtomicNumber"]
```

**Complexity**: Query-dependent
**Category**: Indexed categories

### Level 5: Custom Algorithms

```wolfram
(* Novel implementations *)
MultiwaySystem[rules, init, steps]
Compile[spec, body, "C"]
ResourceFunction["CustomAlgorithm"]
```

**Complexity**: User-defined
**Category**: Higher categories, topoi

---

## Code Generation

### SymbolicC

```wolfram
Needs["SymbolicC`"]

(* Generate C code *)
cExpr = CBlock[{
  CDeclaration["type", "var"],
  CAssign["var", value],
  CReturn["var"]
}]

ToCCodeString[cExpr]
```

### Compilation

```wolfram
(* Compile to C *)
cf = Compile[
  {{x, _Real}},
  expression,
  CompilationTarget -> "C"
]

(* Use compiled function *)
cf[value]
```

### Python Integration

```wolfram
(* Execute Python *)
ExternalEvaluate["Python", "pythonCode"]

(* Create Python function *)
pyFunc = ExternalFunction["Python", "
def func(args):
    return result
"]
```

---

## Pattern Matching Functions

### Search & Filter

```wolfram
Cases[expr, pattern]           (* Find matches *)
Cases[expr, pattern, {level}]  (* Find at level *)
Position[expr, pattern]        (* Find positions *)
Count[expr, pattern]           (* Count matches *)
DeleteCases[expr, pattern]     (* Remove matches *)
```

### Testing

```wolfram
MatchQ[expr, pattern]          (* Test if matches *)
FreeQ[expr, pattern]           (* Test if absent *)
MemberQ[list, element]         (* Test membership *)
```

### Extraction

```wolfram
Extract[expr, positions]       (* Get at positions *)
Part[expr, indices]            (* Get parts *)
First, Last, Rest, Most        (* List operations *)
```

---

## Categorica Functions

### Available in Wolfram Function Repository

```wolfram
(* Abstract structures *)
ResourceFunction["AbstractQuiver"]
ResourceFunction["AbstractCategory"]
ResourceFunction["AbstractFunctor"]
ResourceFunction["AbstractNaturalTransformation"]

(* Diagram operations *)
ResourceFunction["StringDiagram"]
ResourceFunction["CommutativeDiagram"]

(* Rewriting *)
ResourceFunction["HypergraphRewrite"]
ResourceFunction["MultiwayGraph"]
```

---

## Common Idioms

### Functor Composition Chain

```wolfram
(* Chain of transformations *)
data
  // Map[transform1]
  // Select[predicate]
  // Map[transform2]
  // GroupBy[keyFunc]
```

### Pattern-Based Dispatch

```wolfram
(* Multi-method function *)
process[x_Integer] := "Integer case"
process[x_String] := "String case"
process[x_List] := Map[process, x]
process[x_] := "Default case"
```

### Memoization

```wolfram
(* Cache results *)
f[x_] := f[x] = expensiveComputation[x]
```

### Error Handling

```wolfram
(* Check and validate *)
f[x_] /; validationTest[x] := computation[x]
f[x_] := (Message[f::invalid, x]; $Failed)
```

### Type Constraints

```wolfram
(* Function with type checking *)
f[x_?NumberQ, y_?VectorQ] := computation[x, y]
```

---

## Performance Patterns

### Compile for Speed

```wolfram
(* Numerical computation *)
Compile[{{x, _Real, 1}}, Total[x^2]]
```

### Parallel Computation

```wolfram
ParallelMap[f, list]
ParallelTable[expr, {i, n}]
```

### Optimization

```wolfram
(* Memoization *)
ClearCache[]
f[x_] := f[x] = computation[x]

(* Packed arrays *)
Developer`ToPackedArray[list]
```

---

## Debugging Tools

```wolfram
(* Inspection *)
FullForm[expr]           (* Internal form *)
TreeForm[expr]           (* Tree visualization *)
Trace[computation]       (* Execution trace *)
TracePrint[computation]  (* Detailed trace *)

(* Timing *)
Timing[expr]             (* CPU time *)
AbsoluteTiming[expr]     (* Wall clock time *)
RepeatedTiming[expr]     (* Average time *)

(* Memory *)
ByteCount[expr]          (* Memory usage *)
MaxMemoryUsed[]          (* Peak memory *)
```

---

## Resources

### Documentation

- Main: https://reference.wolfram.com/language/
- Categorica: arXiv:2403.16269
- Multiway Systems: https://www.wolframphysics.org/

### Key Packages

- `SymbolicC`: Symbolic C code generation
- `CCodeGenerator`: C code compilation
- Categorica: Applied category theory (Function Repository)

### Community

- Wolfram Community: https://community.wolfram.com/
- Stack Exchange: https://mathematica.stackexchange.com/

---

**Quick Start for Meta-Programming**

1. **Homoiconicity**: Everything is an expression
2. **Hold**: Control evaluation with `Hold`, `HoldForm`
3. **Transform**: Use `/.` and patterns
4. **Generate**: Build code with `ToExpression`
5. **Deploy**: Use `CloudDeploy` for instant web access

**Quick Start for Category Theory**

1. **Rules = Morphisms**: `x -> y` is an arrow
2. **ReplaceAll = Functor**: `/.` preserves structure
3. **Composition**: Use `@*` for function composition
4. **Patterns = Objects**: `_Integer` defines object class
5. **Categorica**: Use for advanced CT computations

---

**End of Quick Reference**
