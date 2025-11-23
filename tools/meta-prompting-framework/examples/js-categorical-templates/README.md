# NEXUS Categorical JavaScript Templates

> **Theme**: Gold (#D4AF37) | Navy Blue (#1B365D)

Iterative meta-prompting through categorical abstractions.

## Core Concepts

### Monadic Constructions (Left Kan Extension Pattern)

Monads enable **sequential composition** where each step depends on the previous:

```javascript
const result = MetaPromptMonad.of('Initial prompt')
  .flatMap(improver)  // Iteration 1
  .flatMap(improver)  // Iteration 2
  .flatMap(improver); // Iteration 3
```

**Key Types**:
- `MetaPromptMonad` - Tracks output, quality, iteration count, and context
- `TaskMonad` - Async operations with proper error handling

### Comonadic Extractions (Right Kan Extension Pattern)

Comonads enable **context-aware extraction** where values carry their environment:

```javascript
const comonad = ContextComonad.of(currentIteration, {
  history: [iter1, iter2],
  patterns: extractedPatterns
});

// Extract with full context awareness
const result = comonad.extend(w => ({
  current: w.extract(),
  trend: analyzeTrend(w.context.history)
}));
```

**Key Types**:
- `ContextComonad` - Value + context pair with extend operation
- `StreamComonad` - Infinite stream with focus (zipper pattern)

### Kan Extensions (Universal Abstractions)

```
Left Kan Extension (Generative):
Lan_G(F)(e) = ∫^c Hom(G(c), e) × F(c)

Right Kan Extension (Extractive):
Ran_G(F)(e) = ∫_c [Hom(e, G(c)), F(c)]
```

**In Meta-Prompting Terms**:

| Extension | Purpose | Formula | Application |
|-----------|---------|---------|-------------|
| Left Kan | Best generation | Colimit (join) | Multi-strategy generation |
| Right Kan | Conservative extraction | Limit (meet) | Pattern intersection |

## Usage

### Node.js

```javascript
const {
  MetaPromptMonad,
  MetaPromptEngine,
  LeftKan,
  RightKan
} = require('./kan-extensions');

// Run full engine
const engine = new MetaPromptEngine({
  maxIterations: 5,
  qualityThreshold: 0.85
});

const result = engine.process('Create file browser TUI');
```

### Run Examples

```bash
node kan-extensions.js
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MetaPromptEngine                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │   Left Kan      │         │   Right Kan     │           │
│  │   (Generate)    │ ─────── │   (Extract)     │           │
│  │                 │         │                 │           │
│  │  Strategies:    │         │  Patterns:      │           │
│  │  - direct       │         │  - quality      │           │
│  │  - multi_approach        │  - strategy     │           │
│  │  - autonomous   │         │  - timestamp    │           │
│  └────────┬────────┘         └────────┬────────┘           │
│           │                           │                     │
│           └─────────┬─────────────────┘                     │
│                     │                                       │
│           ┌─────────▼─────────┐                            │
│           │ MetaPromptMonad   │                            │
│           │ (Iteration State) │                            │
│           │                   │                            │
│           │ • output          │                            │
│           │ • quality         │                            │
│           │ • iteration       │                            │
│           │ • context         │                            │
│           └───────────────────┘                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Color Theme Integration

All components support the NEXUS Gold/Navy theme:

```javascript
const theme = {
  primary: '#D4AF37',    // Gold - actions, focus
  secondary: '#1B365D',  // Navy - containers
  background: '#0D1B2A', // Deep navy
  text: '#FFFFFF',       // White
  muted: '#A8B5C4'       // Gray
};
```

## Laws Verification

### Monad Laws

```javascript
// Left Identity
MetaPromptMonad.of(a).flatMap(f) === f(a)

// Right Identity
m.flatMap(MetaPromptMonad.of) === m

// Associativity
m.flatMap(f).flatMap(g) === m.flatMap(x => f(x).flatMap(g))
```

### Comonad Laws

```javascript
// Left Identity
w.extend(extract) === w

// Right Identity
extract(w.extend(f)) === f(w)

// Associativity
w.extend(f).extend(g) === w.extend(w => g(w.extend(f)))
```

## License

MIT - Part of the NEXUS Meta-Prompting Framework
