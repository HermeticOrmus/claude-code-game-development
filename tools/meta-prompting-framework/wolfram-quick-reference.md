# Wolfram Language Quick Reference

## Table of Contents
1. [Essential Patterns](#essential-patterns)
2. [API Usage Examples](#api-usage-examples)
3. [Python Integration](#python-integration)
4. [Composition Cheat Sheet](#composition-cheat-sheet)
5. [Common Workflows](#common-workflows)

---

## Essential Patterns

### Pattern Matching Syntax

```mathematica
(* Basic patterns *)
f[x_]              (* any expression *)
f[x_Integer]       (* any integer *)
f[x_?EvenQ]        (* any even number *)
f[x_, y_]          (* two arguments *)
f[x__]             (* one or more arguments *)
f[x___]            (* zero or more arguments *)
f[x_, y_:0]        (* y optional, default 0 *)

(* Named patterns *)
f[x:_Integer]      (* named pattern *)
f[x_Integer|y_Real](* alternatives *)

(* Conditions *)
f[x_ /; x > 0]     (* conditional pattern *)
f[x_?Positive]     (* pattern test *)

(* Replacement *)
expr /. x -> 5            (* replace x with 5 *)
expr /. {a->1, b->2}      (* multiple rules *)
expr //. a -> b           (* repeated replacement *)
expr /. x:_Integer -> x^2 (* pattern-based *)
```

### Pure Functions

```mathematica
(* Slot-based *)
#^2 &                      (* single argument *)
#1 + #2 &                  (* multiple arguments *)
#x + #y &                  (* named slots *)

(* Function syntax *)
Function[x, x^2]
Function[{x,y}, x+y]
x |-> x^2                  (* operator form *)

(* Practical examples *)
Map[#^2 &, {1,2,3}]                    (* {1, 4, 9} *)
Select[#>5 &, {3,6,2,8}]               (* {6, 8} *)
Fold[#1+#2 &, 0, {1,2,3,4}]            (* 10 *)
```

### Composition

```mathematica
(* Composition operators *)
(f @* g)[x]        (* f[g[x]] - compose right to left *)
(f /* g)[x]        (* g[f[x]] - compose left to right *)

(* Application *)
f @ x              (* f[x] - prefix *)
x // f             (* f[x] - postfix *)
x ~f~ y            (* f[x, y] - infix *)

(* Pipeline style *)
data
  // Select[Positive]
  // Map[Sqrt]
  // Total
  // N

(* Operator forms in pipeline *)
{1, -2, 3, -4, 5}
  // Select[Positive]        (* {1, 3, 5} *)
  // Map[#^2 &]              (* {1, 9, 25} *)
  // Apply[Plus]             (* 35 *)
```

---

## API Usage Examples

### Creating Cloud APIs

```mathematica
(* Simple API *)
api = APIFunction[{"n" -> "Integer"}, #n! &]
CloudDeploy[api, "factorial"]
(* Access: https://www.wolframcloud.com/obj/user/factorial?n=5 *)

(* Multi-parameter API with types *)
api = APIFunction[
  {
    "city1" -> "City",
    "city2" -> "City"
  },
  GeoDistance[#city1, #city2] &,
  "JSON"
]
CloudDeploy[api, "city-distance", Permissions -> "Public"]

(* With authentication *)
api = APIFunction[
  {"query" -> "String"},
  processQuery[#query] &
]
CloudDeploy[
  api,
  Permissions -> {PermissionsKey["secret123"] -> "Execute"}
]
(* Access with: ?query=test&_key=secret123 *)

(* Complex processing API *)
api = APIFunction[
  {"data" -> "String"},
  Module[{parsed, result},
    parsed = ImportString[#data, "JSON"];
    result = analyze[parsed];
    ExportString[result, "JSON"]
  ] &
]
CloudDeploy[api, "analyze-data"]
```

### Calling Wolfram|Alpha API

```bash
# Simple API (GET)
curl "http://api.wolframalpha.com/v1/simple?appid=YOUR_APPID&i=integrate+x^2"

# Full Results API (GET)
curl "http://api.wolframalpha.com/v2/query?appid=YOUR_APPID&input=weather+seattle&format=plaintext"

# LLM API (with Bearer token)
curl -H "Authorization: Bearer YOUR_APPID" \
  "https://www.wolframalpha.com/api/v1/llm-api?input=distance+to+moon"
```

### Making REST Requests from Wolfram

```mathematica
(* GET request *)
response = URLRead["https://api.example.com/data"]
data = ImportString[response["Body"], "JSON"]

(* GET with parameters *)
response = URLRead[
  "https://api.example.com/search",
  "Query" -> {"q" -> "wolfram", "limit" -> "10"}
]

(* POST request *)
response = URLRead[
  HTTPRequest[
    "https://api.example.com/submit",
    <|
      "Method" -> "POST",
      "Body" -> ExportString[<|"key"->"value"|>, "JSON"],
      "ContentType" -> "application/json"
    |>
  ]
]

(* With authentication *)
response = URLRead[
  HTTPRequest[
    url,
    <|
      "Method" -> "GET",
      "Headers" -> {
        "Authorization" -> "Bearer YOUR_TOKEN",
        "Accept" -> "application/json"
      }
    |>
  ]
]

(* Handle response *)
If[response["StatusCode"] == 200,
  ImportString[response["Body"], "JSON"],
  $Failed
]
```

---

## Python Integration

### Wolfram Client Library

```python
from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr

# Start session
session = WolframLanguageSession()

# Basic evaluation
result = session.evaluate('2 + 2')
print(result)  # 4

# Use wl factory
result = session.evaluate(wl.Range(10))
print(result)  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Complex expressions
result = session.evaluate(wl.FactorInteger(123456))
print(result)  # [[2, 6], [3, 1], [643, 1]]

# NumPy integration
import numpy as np
matrix = np.array([[1, 2], [3, 4]])
eigenvalues = session.evaluate(wl.Eigenvalues(matrix))
print(eigenvalues)

# String input
result = session.evaluate(wlexpr('Solve[x^2 + 3x + 2 == 0, x]'))

# Cleanup
session.terminate()
```

### Cloud Session

```python
from wolframclient.evaluation import WolframCloudSession

# Authenticate
cloud = WolframCloudSession(credentials=('user', 'password'))

# Or use API key
cloud = WolframCloudSession(credentials='YOUR_API_KEY')

# Evaluate
result = cloud.evaluate('Integrate[x^2, x]')

# Call deployed API
result = cloud.call('myapi', {'x': 5})

cloud.terminate()
```

### WXF Serialization

```python
from wolframclient.serializers import export
from wolframclient.deserializers import binary_deserialize
import io

# Python to WXF
data = {'name': 'Alice', 'values': [1, 2, 3, 4, 5]}
wxf_bytes = export(data, target_format='wxf')

# Save to file
with open('data.wxf', 'wb') as f:
    f.write(wxf_bytes)

# WXF to Python
with open('data.wxf', 'rb') as f:
    wxf_data = f.read()
python_data = binary_deserialize(wxf_data)
print(python_data)
```

### ExternalEvaluate (Python from Wolfram)

```mathematica
(* Execute Python code *)
ExternalEvaluate["Python", "import math; math.factorial(10)"]
(* Returns: 3628800 *)

(* Python session *)
session = StartExternalSession["Python"]

ExternalEvaluate[session, "
import numpy as np
import pandas as pd

data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
df = pd.DataFrame(data)
df.to_json()
"]

(* Pass data between languages *)
data = {1, 2, 3, 4, 5};
ExternalEvaluate[session, "
import json
data = <* data *>
result = [x**2 for x in data]
json.dumps(result)
"]

DeleteObject[session]
```

---

## Composition Cheat Sheet

### Functional Combinators

```mathematica
(* Map family *)
Map[f, list]                     (* f /@ list *)
MapThread[f, {list1, list2}]     (* thread f over lists *)
MapIndexed[f, list]              (* f with index *)
MapAt[f, expr, pos]              (* f at position *)
MapAll[f, expr]                  (* f at all levels *)

(* Apply family *)
Apply[f, {a,b,c}]                (* f[a,b,c] *)
Apply[f, expr, {level}]          (* at specific level *)

(* Select/Filter *)
Select[list, predicate]
Select[list, #>5 &]
Cases[list, pattern]

(* Fold/Reduce *)
Fold[f, init, list]              (* accumulate with function *)
FoldList[f, init, list]          (* show intermediate steps *)
Fold[Plus, 0, {1,2,3,4}]         (* sum *)

(* Nest *)
Nest[f, x, n]                    (* f applied n times *)
NestList[f, x, n]                (* show intermediate *)
NestWhile[f, x, test]            (* while condition *)
FixedPoint[f, x]                 (* until no change *)

(* Composition *)
Composition[f, g, h]             (* f @* g @* h *)
RightComposition[f, g, h]        (* f /* g /* h *)
Identity                         (* identity function *)

(* Operator forms *)
Map[f]           (* operator waiting for list *)
Select[test]     (* operator waiting for list *)
SortBy[f]        (* operator waiting for list *)
```

### Data Processing Pipeline Patterns

```mathematica
(* Pattern 1: Postfix pipeline *)
data
  // Select[#Value > 100 &]
  // SortBy[#Date &]
  // Take[10]
  // Map[#Name &]

(* Pattern 2: Composition *)
process =
  Select[#Value > 100 &] /*
  SortBy[#Date &] /*
  Take[10] /*
  Map[#Name &];

process[data]

(* Pattern 3: Query (for Dataset) *)
dataset[
  Select[#Value > 100 &],
  SortBy[#Date &],
  Take[10],
  All,
  "Name"
]

(* Pattern 4: Nested Map *)
data
  // Map[processRecord]
  // GroupBy[#Category &]
  // Map[aggregateGroup]
  // KeySort

(* Pattern 5: Fold for state *)
Fold[
  Function[{state, item}, updateState[state, item]],
  initialState,
  items
]
```

### Association Patterns

```mathematica
(* Creation *)
assoc = <|"a" -> 1, "b" -> 2, "c" -> 3|>

(* Access *)
assoc["a"]
Lookup[assoc, "b"]
Lookup[assoc, "d", defaultValue]

(* Modification *)
Append[assoc, "d" -> 4]
Prepend[assoc, "z" -> 0]
KeyDrop[assoc, "a"]
KeyTake[assoc, {"a", "c"}]

(* Transformation *)
Map[f, assoc]                    (* apply to values *)
KeyMap[f, assoc]                 (* apply to keys *)
AssociationMap[f, {a, b, c}]     (* create from list *)
GroupBy[list, keyFunc]           (* group into assoc *)
Merge[{assoc1, assoc2}, f]       (* merge with function *)

(* Queries *)
Keys[assoc]
Values[assoc]
KeyExistsQ[assoc, "a"]
Length[assoc]

(* Nested access *)
nested = <|
  "user1" -> <|"name"->"Alice", "age"->30|>,
  "user2" -> <|"name"->"Bob", "age"->25|>
|>

nested["user1"]["name"]
nested[["user1", "name"]]
```

### Dataset Query Patterns

```mathematica
(* Dataset creation *)
ds = Dataset[{
  <|"Name"->"Alice", "Age"->30, "City"->"Seattle"|>,
  <|"Name"->"Bob", "Age"->25, "City"->"Portland"|>,
  <|"Name"->"Charlie", "Age"->35, "City"->"Seattle"|>
}]

(* Select rows *)
ds[Select[#Age > 27 &]]

(* Select columns *)
ds[All, {"Name", "Age"}]
ds[All, "Name"]

(* Group by *)
ds[GroupBy["City"]]
ds[GroupBy["City"], Length]
ds[GroupBy["City"], Mean, "Age"]

(* Aggregation *)
ds[Total, "Age"]
ds[Mean, "Age"]
ds[Max, "Age"]

(* Complex query *)
ds[
  Select[#City == "Seattle" &],
  GroupBy[#Age > 30 &],
  Length
]

(* Descending/Ascending operators *)
ds[
  Select[#Age > 25 &]     (* descending: filters before *)
  /* Mean                (* ascending: aggregates after *)
  ,
  "Age"
]
```

---

## Common Workflows

### Data Import and Analysis

```mathematica
(* Import CSV as Dataset *)
data = Import["data.csv", "Dataset"]

(* Or from URL *)
data = Import["https://example.com/data.csv", "Dataset"]

(* Clean and transform *)
cleaned = data[
  Select[#Value > 0 &],           (* filter rows *)
  All,
  <|                               (* transform columns *)
    "Date" -> DateObject,
    "Value" -> Identity,
    "Category" -> ToUpperCase
  |>
]

(* Group and aggregate *)
summary = cleaned[
  GroupBy["Category"],
  <|
    "Total" -> Query[Total, "Value"],
    "Average" -> Query[Mean, "Value"],
    "Count" -> Length,
    "Max" -> Query[Max, "Value"]
  |>
]

(* Visualize *)
BarChart[
  summary[Values, "Total"],
  ChartLabels -> summary[Keys],
  ChartStyle -> "Pastel",
  ImageSize -> Large
]

(* Export results *)
Export["summary.json", summary, "JSON"]
Export["summary.xlsx", summary]
```

### Machine Learning Pipeline

```mathematica
(* Load data *)
rawData = Import["training_data.csv", "Dataset"]

(* Prepare features and labels *)
features = rawData[All, {"Feature1", "Feature2", "Feature3"}]
labels = rawData[All, "Label"]
trainingData = Thread[Normal[features] -> Normal[labels]]

(* Split train/test *)
{train, test} = TakeDrop[RandomSample[trainingData], 0.8*Length[trainingData]]

(* Train model *)
classifier = Classify[
  train,
  Method -> "RandomForest",
  PerformanceGoal -> "Quality"
]

(* Evaluate *)
cm = ClassifierMeasurements[classifier, test]
Print["Accuracy: ", cm["Accuracy"]]
cm["ConfusionMatrixPlot"]

(* Make predictions *)
newData = {<|"Feature1"->1.2, "Feature2"->3.4, "Feature3"->5.6|>}
predictions = classifier /@ newData

(* Deploy as API *)
api = APIFunction[
  {"feature1"->"Number", "feature2"->"Number", "feature3"->"Number"},
  classifier[<|"Feature1"->#feature1, "Feature2"->#feature2, "Feature3"->#feature3|>] &
]
CloudDeploy[api, "classifier-api", Permissions->"Public"]
```

### Interactive Dashboard

```mathematica
(* Create interactive dashboard *)
Manipulate[
  Module[{filtered, chart},
    (* Filter data based on controls *)
    filtered = data[
      Select[#Date >= startDate && #Date <= endDate &],
      Select[MemberQ[selectedCategories, #Category] &]
    ];

    (* Create visualization *)
    chart = Which[
      chartType == "Bar",
        BarChart[
          filtered[GroupBy["Category"], Total, "Value"]
        ],
      chartType == "Line",
        DateListPlot[
          filtered[All, {"Date", "Value"}] // Normal,
          Joined -> True
        ],
      chartType == "Pie",
        PieChart[
          filtered[GroupBy["Category"], Total, "Value"]
        ]
    ];

    (* Display with summary *)
    Column[{
      Row[{
        "Total Records: ",
        Length[filtered],
        "  |  Total Value: ",
        filtered[Total, "Value"]
      }],
      chart
    }]
  ],
  {{startDate, DateObject[{2024,1,1}], "Start Date"}, DateObject},
  {{endDate, DateObject[{2024,12,31}], "End Date"}, DateObject},
  {{selectedCategories, {"A","B","C"}, "Categories"},
   {"A","B","C","D","E"}, ControlType->CheckboxBar},
  {{chartType, "Bar", "Chart Type"},
   {"Bar", "Line", "Pie"}}
]
```

### API Integration Pattern

```mathematica
(* Generic API client *)
callAPI[endpoint_, method_:"GET", params_:<||>, headers_:<||>] :=
  Module[{url, request, response},
    url = baseURL <> endpoint;

    request = HTTPRequest[
      url,
      <|
        "Method" -> method,
        "Query" -> params,
        "Headers" -> Join[defaultHeaders, headers]
      |>
    ];

    response = URLRead[request];

    If[response["StatusCode"] == 200,
      ImportString[response["Body"], "JSON"],
      Failure["APIError", <|
        "StatusCode" -> response["StatusCode"],
        "Body" -> response["Body"]
      |>]
    ]
  ]

(* Configuration *)
baseURL = "https://api.example.com/";
defaultHeaders = <|
  "Authorization" -> "Bearer " <> apiToken,
  "Content-Type" -> "application/json"
|>

(* Usage *)
users = callAPI["users", "GET", <|"limit"->10|>]
createUser = callAPI["users", "POST", <|>, <|"Body"->userJSON|>]
```

### Cloud Deployment Workflow

```mathematica
(* 1. Develop locally *)
processData[input_] := Module[{result},
  result = (* complex processing *);
  result
]

(* 2. Create API *)
api = APIFunction[
  {"data" -> "String"},
  Module[{parsed, result},
    parsed = ImportString[#data, "JSON"];
    result = processData[parsed];
    ExportString[result, "JSON", "Compact"->True]
  ] &,
  "String"
]

(* 3. Test locally *)
api["data" -> ExportString[testData, "JSON"]]

(* 4. Deploy to cloud *)
obj = CloudDeploy[
  api,
  "my-api-v1",
  Permissions -> "Public",
  CloudObjectNameFormat -> "UUID"
]

(* 5. Get URL *)
url = CloudObject["my-api-v1"]["URL"]

(* 6. Test deployed version *)
response = URLRead[
  url,
  "Query" -> {"data" -> ExportString[testData, "JSON"]}
]

(* 7. Monitor usage *)
CloudObjectInformation[obj, "Permissions"]
CloudObjectInformation[obj, "AccessTimes"]
```

---

## Performance Tips

### Compile for Speed

```mathematica
(* Compile numeric code *)
compiledFunc = Compile[{{x, _Real}},
  Module[{sum = 0.0},
    Do[sum += Sin[i*x], {i, 1000}];
    sum
  ]
]

(* Much faster than interpreted *)
AbsoluteTiming[compiledFunc[0.5]]
```

### Parallelize When Possible

```mathematica
(* Launch kernels *)
LaunchKernels[]

(* Parallel operations *)
ParallelMap[expensiveFunction, largeList]
ParallelTable[compute[i], {i, 1, 10000}]
Parallelize[Map[f, bigList]]

(* Distribute definitions *)
DistributeDefinitions[myFunction, myData]
```

### Use Packed Arrays

```mathematica
(* Packed arrays are much faster *)
Developer`PackedArrayQ[{1, 2, 3, 4, 5}]    (* True *)
Developer`PackedArrayQ[{1, 2, x, 4, 5}]    (* False *)

(* Convert to packed *)
packed = Developer`ToPackedArray[list]

(* Operations maintain packing *)
result = packed + 1  (* still packed *)
```

### Avoid Repeated Evaluation

```mathematica
(* Bad - recomputes every time *)
Table[expensiveComputation[], {i, 100}]

(* Good - compute once *)
result = expensiveComputation[];
Table[result, {i, 100}]

(* Use memoization *)
f[x_] := f[x] = expensiveComputation[x]
```

---

## Error Handling

```mathematica
(* Check for errors *)
result = Quiet[Check[
  riskyOperation[],
  $Failed,
  riskyOperation::msg
]]

(* Use Failure objects *)
myFunction[input_] := If[validQ[input],
  processInput[input],
  Failure["InvalidInput", <|"Input"->input|>]
]

(* Pattern matching on Failure *)
result = myFunction[x];
result /. {
  Failure[___] :> handleError[result],
  _ :> handleSuccess[result]
}

(* Try/Catch style *)
Catch[
  If[badCondition, Throw["Error message"]];
  normalProcessing[]
]
```

---

## Documentation Resources

- **Main Documentation**: https://reference.wolfram.com/language/
- **Function Repository**: https://resources.wolframcloud.com/FunctionRepository/
- **Wolfram U**: https://www.wolfram.com/wolfram-u/
- **Community**: https://community.wolfram.com/
- **Stack Exchange**: https://mathematica.stackexchange.com/
