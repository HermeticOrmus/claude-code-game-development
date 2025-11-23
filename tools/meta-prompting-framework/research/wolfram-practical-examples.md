# Wolfram Language: Practical Meta-Programming Examples

## Companion to Categorical Meta-Programming Research

---

## 1. Categorical Pattern Examples

### 1.1 Rules as Morphisms

```wolfram
(* Simple morphism *)
f: Integer -> Integer
rule1 = x_Integer :> x^2

(* Apply morphism *)
5 /. rule1
(* → 25 *)

(* Morphism composition *)
rule2 = x_Integer :> x + 1
composedRule = {rule2, rule1}  (* order matters! *)

5 /. composedRule
(* → 36 (not 26) - applies rule1 first, then rule2 *)

(* Functorial application *)
Map[# /. rule1 &, {1, 2, 3, 4, 5}]
(* → {1, 4, 9, 16, 25} *)
```

### 1.2 ReplaceAll as Functor

```wolfram
(* Functor F: Expr -> Expr *)
F = ReplaceAll[#, x -> y] &

(* Functor laws *)

(* 1. Identity: F(id) = id *)
F[expr] == expr  (* when no match *)

(* 2. Composition: F(g ∘ f) = F(g) ∘ F(f) *)
expr = f[g[x]];
rules = {f -> h, g -> k};

(* F preserves structure *)
F[expr] == h[k[x]]

(* Functor on lists (Map is a functor) *)
Map[f, {a, b, c}] == {f[a], f[b], f[c]}
```

### 1.3 Natural Transformations

```wolfram
(* Two functors on lists *)
F[list_] := Map[f, list]
G[list_] := Map[g, list]

(* Natural transformation η: F ⇒ G *)
η[list_] := Map[transform, F[list]]

(* Naturality square commutes *)
list = {a, b, c};

η[F[list]] == G[η[list]]  (* naturality condition *)

(* Example: List -> Association is natural *)
listToAssoc = AssociationThread[Range[Length[#]], #] &;

(* Naturality: *)
listToAssoc[Map[f, list]] == Map[f, listToAssoc[list]]
```

### 1.4 Monoidal Structure

```wolfram
(* Tensor product on expressions *)
tensor[expr1_, expr2_] := {expr1, expr2}

(* Monoidal composition *)
expr1 = f[x];
expr2 = g[y];

tensor[expr1, expr2]
(* → {f[x], g[y]} *)

(* Function composition as monoidal product *)
(f @* g) @* h == f @* (g @* h)  (* associativity *)

(* Identity *)
Identity @* f == f @* Identity == f
```

---

## 2. Meta-Programming Patterns

### 2.1 Code Generation from Specifications

```wolfram
(* Function specification *)
spec = <|
  "Name" -> "processData",
  "Args" -> {"data", "threshold"},
  "ArgTypes" -> {"List", "Real"},
  "Body" -> "Select[data, # > threshold &]"
|>

(* Generator *)
generateFunction[spec_] := Module[
  {name, args, types, body, argPatterns},

  name = spec["Name"];
  args = spec["Args"];
  types = spec["ArgTypes"];
  body = spec["Body"];

  (* Create typed patterns *)
  argPatterns = MapThread[
    #1 <> "_" <> #2 &,
    {args, types}
  ];

  (* Generate function definition *)
  ToExpression[
    name <> "[" <>
    StringRiffle[argPatterns, ", "] <>
    "] := " <> body
  ]
]

(* Generate the function *)
generateFunction[spec]

(* Now you can call it *)
processData[{1, 5, 3, 8, 2}, 4]
(* → {5, 8} *)
```

### 2.2 Template-Based Code Generation

```wolfram
(* Multi-language code generation *)
pythonTemplate = StringTemplate["
def `name`(`params`):
    \"`doc`\"
    return `body`
"]

jsTemplate = StringTemplate["
function `name`(`params`) {
  // `doc`
  return `body`;
}
"]

cTemplate = StringTemplate["
`returnType` `name`(`params`) {
  /* `doc` */
  return `body`;
}
"]

(* Specification *)
funcSpec = <|
  "name" -> "add",
  "params" -> "x, y",
  "body" -> "x + y",
  "doc" -> "Add two numbers",
  "returnType" -> "double"
|>

(* Generate in multiple languages *)
pythonCode = pythonTemplate[funcSpec]
jsCode = jsTemplate[funcSpec]
cCode = cTemplate[funcSpec]
```

### 2.3 Macro-Like Code Transformation

```wolfram
(* Define a macro for logging *)
withLogging[expr_] := Module[
  {result},
  Print["Executing: ", HoldForm[expr]];
  result = expr;
  Print["Result: ", result];
  result
]

(* Use the macro *)
withLogging[2 + 2]
(* Prints:
   Executing: 2 + 2
   Result: 4
   → 4
*)

(* More complex: timing macro *)
timed[expr_] := Module[
  {start, end, result},
  start = AbsoluteTime[];
  result = expr;
  end = AbsoluteTime[];
  <|
    "Result" -> result,
    "Time" -> end - start
  |>
]

timed[Sum[i^2, {i, 1, 1000000}]]
```

### 2.4 AST Manipulation

```wolfram
(* Walk the AST and transform *)
transformAST[expr_, rules_] := expr //. rules

(* Example: Convert all additions to multiplications *)
ast = Hold[a + b + c + (d + e)]

transformAST[ast, Plus -> Times]
(* → Hold[a * b * c * (d * e)] *)

(* More sophisticated: constant folding *)
constantFold[expr_] := expr //. {
  Plus[x_Integer, y_Integer] :> x + y,
  Times[x_Integer, y_Integer] :> x * y,
  Power[x_Integer, y_Integer] :> x^y
}

ast2 = Hold[2 + 3 + x + 4 * 5]
constantFold[ast2]
(* → Hold[5 + x + 20] *)
```

### 2.5 Dynamic Dispatch Generation

```wolfram
(* Generate type-specialized functions *)
generateTypedFunction[name_, types_] := Module[
  {defs},
  defs = Map[
    type |-> (
      name[x_?type] := "Handling " <> ToString[type]
    ),
    types
  ];
  Scan[ToExpression, defs]
]

(* Create multi-method function *)
generateTypedFunction[
  "process",
  {IntegerQ, StringQ, ListQ}
]

(* Now dispatch works *)
process[42]        (* → "Handling IntegerQ" *)
process["hello"]   (* → "Handling StringQ" *)
process[{1,2,3}]   (* → "Handling ListQ" *)
```

---

## 3. Self-Building System Examples

### 3.1 Complete API Generation

```wolfram
(* Specification *)
apiSpec = <|
  "Name" -> "DataAnalyzer",
  "Endpoints" -> {
    <|
      "Path" -> "mean",
      "Params" -> {"data" -> "NumericArray"},
      "Function" -> (Mean[#data] &)
    |>,
    <|
      "Path" -> "stddev",
      "Params" -> {"data" -> "NumericArray"},
      "Function" -> (StandardDeviation[#data] &)
    |>,
    <|
      "Path" -> "histogram",
      "Params" -> {
        "data" -> "NumericArray",
        "bins" -> "Integer"
      },
      "Function" -> (Histogram[#data, #bins] &)
    |>
  }
|>

(* Generator *)
generateAPI[spec_] := Module[
  {endpoints, apis},
  endpoints = spec["Endpoints"];

  apis = Map[
    endpoint |-> (
      endpoint["Path"] -> APIFunction[
        endpoint["Params"],
        endpoint["Function"]
      ]
    ),
    endpoints
  ];

  (* Deploy all endpoints *)
  Map[
    {path, api} |-> CloudDeploy[api, path],
    apis
  ]
]

(* Generate and deploy entire API *)
urls = generateAPI[apiSpec]
```

### 3.2 Form Generation with Validation

```wolfram
(* Form specification with custom validation *)
formSpec = <|
  "Title" -> "User Registration",
  "Fields" -> {
    <|
      "Name" -> "username",
      "Type" -> "String",
      "Validation" -> (StringLength[#] >= 3 &),
      "Error" -> "Username must be at least 3 characters"
    |>,
    <|
      "Name" -> "email",
      "Type" -> "EmailAddress",
      "Validation" -> (StringContainsQ[#, "@"] &),
      "Error" -> "Invalid email format"
    |>,
    <|
      "Name" -> "age",
      "Type" -> "Integer",
      "Validation" -> (# >= 18 &),
      "Error" -> "Must be 18 or older"
    |>
  },
  "Handler" -> (
    "Registered: " <> #username <> " (" <> #email <> ")" &
  )
|>

(* Generator *)
generateForm[spec_] := Module[
  {fields, validators, handler},

  (* Extract field specs *)
  fields = Map[
    field |-> (field["Name"] -> field["Type"]),
    spec["Fields"]
  ];

  (* Create validation function *)
  validators = Map[
    field |-> (
      field["Name"] -> (field["Validation"] -> field["Error"])
    ),
    spec["Fields"]
  ];

  (* Build form *)
  FormFunction[
    fields,
    spec["Handler"],
    validators
  ]
]

(* Generate and deploy *)
form = generateForm[formSpec]
CloudDeploy[form, "registration"]
```

### 3.3 Scheduled Data Pipeline

```wolfram
(* Pipeline specification *)
pipelineSpec = <|
  "Name" -> "DataPipeline",
  "Schedule" -> Quantity[1, "Hours"],
  "Stages" -> {
    <|
      "Name" -> "Fetch",
      "Function" -> (URLRead["https://api.example.com/data"] &)
    |>,
    <|
      "Name" -> "Parse",
      "Function" -> (ImportString[#, "JSON"] &)
    |>,
    <|
      "Name" -> "Transform",
      "Function" -> (Map[processRecord, #] &)
    |>,
    <|
      "Name" -> "Store",
      "Function" -> (CloudPut[#, "processed-data"] &)
    |>
  }
|>

(* Generator *)
generatePipeline[spec_] := Module[
  {stages, pipeline},

  (* Compose all stages *)
  stages = spec["Stages"];
  pipeline = Fold[
    #2["Function"] @* #1 &,
    Identity,
    Reverse[stages]
  ];

  (* Create scheduled task *)
  ScheduledTask[
    pipeline[],
    spec["Schedule"]
  ]
]

(* Generate and activate pipeline *)
task = generatePipeline[pipelineSpec]
```

### 3.4 Self-Documenting Code

```wolfram
(* Function with metadata *)
SetAttributes[documentedFunction, HoldAll]

documentedFunction[
  name_,
  args_,
  doc_,
  examples_,
  body_
] := Module[{},
  (* Define the function *)
  ToExpression[
    ToString[name] <>
    ToString[args] <>
    " := " <>
    ToString[body]
  ];

  (* Attach documentation *)
  name::usage = doc;

  (* Attach examples *)
  name::examples = examples;

  (* Generate documentation notebook *)
  CreateDocument[{
    TextCell[ToString[name], "Title"],
    TextCell["Description", "Section"],
    TextCell[doc, "Text"],
    TextCell["Examples", "Section"],
    ExpressionCell[#] & /@ examples
  }]
]

(* Use it *)
documentedFunction[
  factorial,
  {n_Integer},
  "Compute factorial of n",
  {
    factorial[5],
    factorial[10]
  },
  If[n == 0, 1, n * factorial[n - 1]]
]

(* Access documentation *)
?factorial
factorial::examples
```

---

## 4. Advanced Pattern Matching

### 4.1 Structural Patterns

```wolfram
(* Deep pattern matching *)
expr = f[g[a, b], h[c, d[e]]];

(* Find all function applications *)
Cases[expr, _[__], ∞]
(* → {g[a,b], h[c,d[e]], d[e], f[...]} *)

(* Find specific structure *)
Cases[expr, f_[g[__], _], ∞]
(* → {f[g[a,b], h[c,d[e]]]} *)

(* Named patterns with conditions *)
Cases[
  {1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
  x_ /; PrimeQ[x]
]
(* → {2, 3, 5, 7} *)
```

### 4.2 Sequence Patterns

```wolfram
(* Pattern sequences *)
SequenceCases[
  {1, 2, 3, 4, 5, 6},
  {a_, b_, c_} /; a + b == c
]
(* → {{1,2,3}, {2,3,5}} *)

(* Repeated patterns *)
Cases[
  {a, a, b, b, b, c, c},
  Repeated[x_, {2, ∞}]
]

(* Optional patterns *)
f[x_, y_:0] := x + y
f[5]     (* → 5 *)
f[5, 3]  (* → 8 *)
```

### 4.3 Association Patterns

```wolfram
(* Pattern matching on associations *)
data = {
  <|"name" -> "Alice", "age" -> 30|>,
  <|"name" -> "Bob", "age" -> 25|>,
  <|"name" -> "Charlie", "age" -> 35|>
};

(* Select by pattern *)
Cases[
  data,
  KeyValuePattern["age" -> x_ /; x > 28]
]
(* → {<|"name" -> "Alice", "age" -> 30|>,
       <|"name" -> "Charlie", "age" -> 35|>} *)

(* Extract values *)
Cases[
  data,
  KeyValuePattern["name" -> name_] :> name
]
(* → {"Alice", "Bob", "Charlie"} *)
```

---

## 5. Compilation and Optimization

### 5.1 Compile to C

```wolfram
(* Simple compilation *)
cf = Compile[
  {{x, _Real}},
  x^2 + 2*x + 1,
  CompilationTarget -> "C"
]

cf[5.0]  (* Fast compiled version *)

(* Complex compilation with loops *)
sumSq = Compile[
  {{n, _Integer}},
  Module[{sum = 0.0},
    Do[sum += i^2, {i, 1, n}];
    sum
  ],
  CompilationTarget -> "C"
]

(* Benchmark *)
Timing[sumSq[1000000]]
(* Much faster than interpreted version *)
```

### 5.2 SymbolicC Generation

```wolfram
(* Generate symbolic C code *)
Needs["SymbolicC`"]

(* Create symbolic C expression *)
cExpr = CBlock[{
  CDeclaration["double", "x"],
  CDeclaration["double", "result"],
  CAssign["x", 5.0],
  CAssign["result", CExpression["x * x + 2 * x + 1"]],
  CReturn["result"]
}]

(* Convert to C string *)
ToCCodeString[cExpr]
```

### 5.3 Optimization Patterns

```wolfram
(* Memoization *)
fib[n_] := fib[n] = If[n <= 1, n, fib[n-1] + fib[n-2]]

(* Common subexpression elimination *)
optimizeExpr[expr_] := Module[
  {subexprs, replacements},

  (* Find repeated subexpressions *)
  subexprs = Cases[
    expr,
    _[__],
    ∞,
    Heads -> False
  ];

  subexprs = Select[
    Tally[subexprs],
    #[[2]] > 1 &
  ][[All, 1]];

  (* Create replacements *)
  replacements = MapIndexed[
    #1 -> Symbol["temp" <> ToString[#2[[1]]]] &,
    subexprs
  ];

  (* Apply optimization *)
  expr /. replacements
]
```

---

## 6. Multiway System Examples

### 6.1 Basic Multiway System

```wolfram
(* Define rewrite rules *)
rules = {
  {A, B} -> {C},
  {C, C} -> {D, A},
  {A, A} -> {B, B}
};

(* Generate multiway system *)
MultiwaySystem[
  rules,
  {A, B},  (* initial state *)
  5        (* steps *)
]

(* Visualize as graph *)
ResourceFunction["MultiwayGraph"][
  rules,
  {A, B},
  5
]
```

### 6.2 String Rewriting System

```wolfram
(* String rewrite rules *)
stringRules = {
  "AB" -> "C",
  "CC" -> "DA",
  "AA" -> "BB"
};

(* Apply multiway *)
MultiwaySystem[
  "StringRewritingSystem",
  stringRules,
  "AB",
  4
]
```

### 6.3 Categorical Multiway Analysis

```wolfram
(* Analyze categorical structure *)
mw = MultiwaySystem[rules, init, steps];

(* Get states (objects) *)
states = VertexList[mw]

(* Get transitions (morphisms) *)
transitions = EdgeList[mw]

(* Find equivalence classes *)
ConnectedComponents[mw]

(* Causal structure *)
ResourceFunction["CausalGraph"][mw]
```

---

## 7. Integration Examples

### 7.1 Python Integration

```wolfram
(* Execute Python code *)
ExternalEvaluate["Python", "
import numpy as np
result = np.array([1, 2, 3, 4, 5]).mean()
result
"]
(* → 3.0 *)

(* Create Python function *)
pyFunc = ExternalFunction["Python", "
def process(data, threshold):
    return [x for x in data if x > threshold]
"]

pyFunc[{1, 5, 3, 8, 2}, 4]
(* → {5, 8} *)

(* Bidirectional data flow *)
data = RandomReal[1, 100];
ExternalEvaluate["Python",
  <|
    "Command" -> "
import numpy as np
result = np.std(<*data*>)
result",
    "ReturnType" -> "Real"
  |>
]
```

### 7.2 Database Integration

```wolfram
(* Connect to database *)
conn = DatabaseReference[
  <|
    "Type" -> "SQLite",
    "Database" -> "mydata.db"
  |>
]

(* Generate queries from specifications *)
querySpec = <|
  "Table" -> "users",
  "Columns" -> {"name", "age"},
  "Where" -> "age > 25",
  "OrderBy" -> "name"
|>

generateQuery[spec_] := StringTemplate["
SELECT `columns`
FROM `table`
WHERE `where`
ORDER BY `orderby`
"][<|
  "columns" -> StringRiffle[spec["Columns"], ", "],
  "table" -> spec["Table"],
  "where" -> spec["Where"],
  "orderby" -> spec["OrderBy"]
|>]

(* Execute *)
SQLExecute[conn, generateQuery[querySpec]]
```

---

## 8. Testing and Validation

### 8.1 Property-Based Testing

```wolfram
(* Generate test cases *)
generateTests[func_, property_, n_:100] := Module[
  {testCases, results},

  (* Generate random inputs *)
  testCases = Table[RandomInteger[{-100, 100}], n];

  (* Test property *)
  results = Map[
    input |-> property[func[input], input],
    testCases
  ];

  (* Report *)
  <|
    "Passed" -> Count[results, True],
    "Failed" -> Count[results, False],
    "Rate" -> N[Count[results, True] / Length[results]]
  |>
]

(* Example property: reversing twice gives original *)
reverseProperty[result_, input_] := (Reverse[Reverse[input]] == input)

generateTests[Identity, reverseProperty]
```

### 8.2 Type Checking

```wolfram
(* Simple type checker *)
typeCheck[expr_, expectedType_] := Module[
  {actualType},

  actualType = Head[expr];

  If[actualType === expectedType,
    True,
    Message[typeCheck::mismatch, actualType, expectedType];
    False
  ]
]

typeCheck::mismatch = "Type mismatch: expected `2`, got `1`";

(* Use in function *)
safeAdd[x_, y_] := If[
  typeCheck[x, Integer] && typeCheck[y, Integer],
  x + y,
  $Failed
]
```

---

**End of Practical Examples**

These examples demonstrate the practical application of categorical concepts and meta-programming patterns discussed in the main research document.
