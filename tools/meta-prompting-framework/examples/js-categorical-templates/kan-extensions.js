/**
 * NEXUS Categorical JavaScript Templates
 * ======================================
 *
 * Iterative meta-prompting through the lens of category theory:
 * - Monadic Constructions: Sequential composition with context
 * - Comonadic Extractions: Context-aware value extraction
 * - Kan Extensions: Universal property-based abstraction
 *
 * Theme: Gold (#D4AF37) and Navy Blue (#1B365D)
 *
 * @version 1.0.0
 * @author NEXUS Meta-Prompting System
 */

// =============================================================================
// PART I: FOUNDATIONAL CATEGORICAL TYPES
// =============================================================================

/**
 * Functor - The foundation of categorical composition
 *
 * Laws:
 * - Identity: fmap(id) === id
 * - Composition: fmap(f . g) === fmap(f) . fmap(g)
 */
class Functor {
  constructor(value) {
    this._value = value;
  }

  static of(value) {
    return new this(value);
  }

  map(fn) {
    return new this.constructor(fn(this._value));
  }

  // Extract for debugging
  inspect() {
    return `${this.constructor.name}(${JSON.stringify(this._value)})`;
  }
}

// =============================================================================
// PART II: MONADIC CONSTRUCTIONS (Left Kan Extension Pattern)
// =============================================================================

/**
 * Monad - Enables sequential composition with context
 *
 * In meta-prompting terms:
 * - bind/flatMap: Chain iterations, each depending on previous result
 * - return/of: Lift a value into the meta-prompting context
 *
 * Laws:
 * - Left Identity: return(a).flatMap(f) === f(a)
 * - Right Identity: m.flatMap(return) === m
 * - Associativity: m.flatMap(f).flatMap(g) === m.flatMap(x => f(x).flatMap(g))
 */
class Monad extends Functor {
  flatMap(fn) {
    return fn(this._value);
  }

  // Alias for compatibility
  chain(fn) {
    return this.flatMap(fn);
  }

  // Lift a function into monadic context
  ap(monadWithFn) {
    return monadWithFn.flatMap((fn) => this.map(fn));
  }
}

/**
 * MetaPromptMonad - The core iteration monad
 *
 * Encapsulates:
 * - Current output value
 * - Quality score (0.0 - 1.0)
 * - Iteration count
 * - Extracted context patterns
 */
class MetaPromptMonad extends Monad {
  constructor({ output, quality, iteration, context }) {
    super(output);
    this.quality = quality;
    this.iteration = iteration;
    this.context = context || {};
  }

  static of(output) {
    return new MetaPromptMonad({
      output,
      quality: 0.0,
      iteration: 0,
      context: {},
    });
  }

  static pure(output) {
    return MetaPromptMonad.of(output);
  }

  /**
   * flatMap (>>=) - The core iteration combinator
   *
   * Takes a function that produces a new MetaPromptMonad from the current output,
   * threading quality improvements and context through iterations.
   */
  flatMap(fn) {
    const next = fn(this._value);
    return new MetaPromptMonad({
      output: next._value,
      quality: Math.max(this.quality, next.quality), // Quality can only improve
      iteration: this.iteration + 1,
      context: { ...this.context, ...next.context }, // Accumulate context
    });
  }

  /**
   * iterate - Run multiple improvement passes
   *
   * @param {Function} improver - Function that takes output and returns improved MetaPromptMonad
   * @param {number} maxIterations - Maximum iterations to run
   * @param {number} qualityThreshold - Stop when quality exceeds this
   */
  iterate(improver, maxIterations = 5, qualityThreshold = 0.85) {
    let current = this;

    while (
      current.iteration < maxIterations &&
      current.quality < qualityThreshold
    ) {
      current = current.flatMap(improver);
      console.log(
        `[Iteration ${current.iteration}] Quality: ${current.quality.toFixed(2)}`
      );
    }

    return current;
  }

  inspect() {
    return `MetaPromptMonad {
  output: ${JSON.stringify(this._value, null, 2)},
  quality: ${this.quality},
  iteration: ${this.iteration},
  context: ${JSON.stringify(this.context)}
}`;
  }
}

/**
 * TaskMonad - Represents async meta-prompting operations
 *
 * Left Kan Extension interpretation:
 * Task is the left Kan extension of Identity along the "async" functor
 */
class TaskMonad {
  constructor(fork) {
    this.fork = fork;
  }

  static of(value) {
    return new TaskMonad((reject, resolve) => resolve(value));
  }

  static rejected(error) {
    return new TaskMonad((reject, resolve) => reject(error));
  }

  map(fn) {
    return new TaskMonad((reject, resolve) =>
      this.fork(reject, (x) => resolve(fn(x)))
    );
  }

  flatMap(fn) {
    return new TaskMonad((reject, resolve) =>
      this.fork(reject, (x) => fn(x).fork(reject, resolve))
    );
  }

  // Run the task
  run() {
    return new Promise((resolve, reject) => this.fork(reject, resolve));
  }
}

// =============================================================================
// PART III: COMONADIC EXTRACTIONS (Right Kan Extension Pattern)
// =============================================================================

/**
 * Comonad - Enables context-aware value extraction
 *
 * In meta-prompting terms:
 * - extract: Get the current best output from iteration context
 * - extend: Apply a context-aware transformation
 *
 * Laws:
 * - Left Identity: w.extend(extract) === w
 * - Right Identity: extract(w.extend(f)) === f(w)
 * - Associativity: w.extend(f).extend(g) === w.extend(w => g(w.extend(f)))
 */
class Comonad extends Functor {
  extract() {
    return this._value;
  }

  extend(fn) {
    return new this.constructor(fn(this));
  }

  duplicate() {
    return this.extend((x) => x);
  }
}

/**
 * ContextComonad - Extracts values with surrounding context
 *
 * Right Kan Extension interpretation:
 * Represents the "best" way to extract a value while preserving context
 */
class ContextComonad extends Comonad {
  constructor(focus, context) {
    super(focus);
    this.context = context;
  }

  static of(focus, context = {}) {
    return new ContextComonad(focus, context);
  }

  /**
   * extract - Get the focused value
   *
   * In meta-prompting: Extract the current best output
   */
  extract() {
    return this._value;
  }

  /**
   * extend - Apply a context-aware function
   *
   * In meta-prompting: Transform output while considering all accumulated context
   *
   * @param {Function} fn - Function that receives the entire comonad and returns a new focus
   */
  extend(fn) {
    return new ContextComonad(fn(this), this.context);
  }

  /**
   * withContext - Add to the context without changing focus
   */
  withContext(additionalContext) {
    return new ContextComonad(this._value, {
      ...this.context,
      ...additionalContext,
    });
  }

  /**
   * coflatMap - Alias for extend (dual of flatMap)
   */
  coflatMap(fn) {
    return this.extend(fn);
  }

  inspect() {
    return `ContextComonad {
  focus: ${JSON.stringify(this._value, null, 2)},
  context: ${JSON.stringify(this.context, null, 2)}
}`;
  }
}

/**
 * StreamComonad - Infinite stream with focus (Zipper pattern)
 *
 * Enables:
 * - Looking at past iterations (left)
 * - Current focus (extract)
 * - Looking at future possibilities (right)
 */
class StreamComonad extends Comonad {
  constructor(left, focus, right) {
    super(focus);
    this.left = left; // Past iterations (lazy)
    this.right = right; // Future iterations (lazy)
  }

  static of(focus) {
    return new StreamComonad(
      () => StreamComonad.of(focus), // Infinite past
      focus,
      () => StreamComonad.of(focus) // Infinite future
    );
  }

  /**
   * fromIterations - Create stream from iteration history
   */
  static fromIterations(iterations, currentIndex = 0) {
    const current = iterations[currentIndex];

    const makeLeft = (idx) => {
      if (idx < 0) return StreamComonad.of(iterations[0]);
      return new StreamComonad(
        () => makeLeft(idx - 1),
        iterations[idx],
        () => makeRight(idx + 1)
      );
    };

    const makeRight = (idx) => {
      if (idx >= iterations.length)
        return StreamComonad.of(iterations[iterations.length - 1]);
      return new StreamComonad(
        () => makeLeft(idx - 1),
        iterations[idx],
        () => makeRight(idx + 1)
      );
    };

    return new StreamComonad(
      () => makeLeft(currentIndex - 1),
      current,
      () => makeRight(currentIndex + 1)
    );
  }

  extract() {
    return this._value;
  }

  /**
   * extend - Apply function that can see entire stream context
   */
  extend(fn) {
    return new StreamComonad(
      () => this.left().extend(fn),
      fn(this),
      () => this.right().extend(fn)
    );
  }

  moveLeft() {
    return this.left();
  }

  moveRight() {
    return this.right();
  }

  /**
   * window - Get a window of values around focus
   */
  window(leftSize, rightSize) {
    const leftValues = [];
    const rightValues = [];

    let current = this;
    for (let i = 0; i < leftSize; i++) {
      current = current.moveLeft();
      leftValues.unshift(current.extract());
    }

    current = this;
    for (let i = 0; i < rightSize; i++) {
      current = current.moveRight();
      rightValues.push(current.extract());
    }

    return {
      left: leftValues,
      focus: this.extract(),
      right: rightValues,
    };
  }
}

// =============================================================================
// PART IV: KAN EXTENSIONS - UNIVERSAL ABSTRACTIONS
// =============================================================================

/**
 * Left Kan Extension (Lan)
 *
 * Given functors F: C → D and G: C → E,
 * the left Kan extension Lan_G(F): E → D is the "best approximation"
 * of F that factors through G.
 *
 * In meta-prompting terms:
 * - F = "ideal output generation"
 * - G = "what we can actually compute"
 * - Lan_G(F) = "best achievable approximation through iteration"
 *
 * Formula: Lan_G(F)(e) = ∫^c Hom(G(c), e) × F(c)
 * (coend weighted by Hom functor)
 */
class LeftKan {
  /**
   * @param {Function} generator - The generative process (F)
   * @param {Function} constraint - The constraint functor (G)
   */
  constructor(generator, constraint) {
    this.generator = generator;
    this.constraint = constraint;
  }

  /**
   * run - Execute the left Kan extension
   *
   * Finds the best output by:
   * 1. Generating candidate via generator
   * 2. Constraining via constraint functor
   * 3. Finding the colimit (best approximation)
   */
  run(input) {
    // Generate all possible outputs
    const generated = this.generator(input);

    // Apply constraints to find feasible outputs
    const constrained = generated.map((g) => this.constraint(g));

    // Colimit: Take the "join" of all constrained outputs
    return this.colimit(constrained);
  }

  /**
   * colimit - Compute the colimit (generative combination)
   *
   * In practice: Select the highest-quality feasible output
   */
  colimit(candidates) {
    if (candidates.length === 0) return null;

    // For meta-prompting: highest quality wins
    return candidates.reduce((best, current) =>
      (current.quality || 0) > (best.quality || 0) ? current : best
    );
  }

  /**
   * Lift a function into the Kan extension context
   */
  map(fn) {
    return new LeftKan(
      (x) => this.generator(x).map(fn),
      this.constraint
    );
  }
}

/**
 * Right Kan Extension (Ran)
 *
 * Given functors F: C → D and G: C → E,
 * the right Kan extension Ran_G(F): E → D is the "conservative approximation"
 * of F that factors through G.
 *
 * In meta-prompting terms:
 * - F = "ideal context extraction"
 * - G = "observable iteration history"
 * - Ran_G(F) = "best context inference from observations"
 *
 * Formula: Ran_G(F)(e) = ∫_c [Hom(e, G(c)), F(c)]
 * (end weighted by Hom functor)
 */
class RightKan {
  /**
   * @param {Function} extractor - The extraction process (F)
   * @param {Function} observer - The observation functor (G)
   */
  constructor(extractor, observer) {
    this.extractor = extractor;
    this.observer = observer;
  }

  /**
   * run - Execute the right Kan extension
   *
   * Extracts context by:
   * 1. Observing the input through observer functor
   * 2. Extracting patterns via extractor
   * 3. Finding the limit (most conservative valid extraction)
   */
  run(input) {
    // Observe all aspects of input
    const observed = this.observer(input);

    // Extract patterns from observations
    const extracted = observed.map((o) => this.extractor(o));

    // Limit: Take the "meet" of all extractions
    return this.limit(extracted);
  }

  /**
   * limit - Compute the limit (conservative intersection)
   *
   * In practice: Only include patterns present in ALL extractions
   */
  limit(extractions) {
    if (extractions.length === 0) return {};

    // For meta-prompting: intersection of all extracted patterns
    return extractions.reduce((acc, extraction) => {
      const result = {};
      for (const key of Object.keys(acc)) {
        if (key in extraction) {
          result[key] = acc[key]; // Keep only common patterns
        }
      }
      return result;
    });
  }

  /**
   * Lift a function into the Kan extension context
   */
  map(fn) {
    return new RightKan(
      (x) => fn(this.extractor(x)),
      this.observer
    );
  }
}

// =============================================================================
// PART V: META-PROMPTING ITERATION ENGINE
// =============================================================================

/**
 * MetaPromptEngine - Full categorical iteration engine
 *
 * Combines:
 * - Monadic composition for sequential iteration
 * - Comonadic extraction for context-aware improvement
 * - Kan extensions for universal abstraction over strategies
 */
class MetaPromptEngine {
  constructor(config = {}) {
    this.maxIterations = config.maxIterations || 5;
    this.qualityThreshold = config.qualityThreshold || 0.85;
    this.strategies = config.strategies || [
      'direct',
      'multi_approach',
      'autonomous',
    ];
  }

  /**
   * process - Main entry point
   *
   * Uses Left Kan extension to generate, Right Kan to extract context
   */
  process(task) {
    console.log(`\n${'═'.repeat(60)}`);
    console.log(`  NEXUS Meta-Prompting Engine`);
    console.log(`  Theme: Gold (#D4AF37) | Navy (#1B365D)`);
    console.log(`${'═'.repeat(60)}\n`);

    // Initialize with monadic wrapper
    let state = MetaPromptMonad.of({
      task,
      output: null,
      patterns: [],
    });

    // Create Left Kan for generation
    const generator = new LeftKan(
      (input) => this.strategies.map((s) => this.generateWithStrategy(input, s)),
      (output) => this.assessQuality(output)
    );

    // Create Right Kan for extraction
    const extractor = new RightKan(
      (output) => this.extractPatterns(output),
      (input) => [input.output, input.task, input.patterns]
    );

    // Iterate using monadic composition
    state = state.iterate((current) => {
      // Generate using Left Kan
      const generated = generator.run(current);

      // Extract context using Right Kan
      const context = extractor.run({ ...current, output: generated });

      return new MetaPromptMonad({
        output: generated,
        quality: generated.quality || 0,
        iteration: 0, // Will be incremented by flatMap
        context,
      });
    }, this.maxIterations, this.qualityThreshold);

    return this.formatResult(state);
  }

  /**
   * generateWithStrategy - Generate output using specific strategy
   */
  generateWithStrategy(input, strategy) {
    const strategies = {
      direct: () => ({
        output: `Direct solution for: ${input.task}`,
        quality: 0.6 + Math.random() * 0.2,
        strategy: 'direct',
      }),

      multi_approach: () => ({
        output: `Multi-approach synthesis for: ${input.task}`,
        quality: 0.7 + Math.random() * 0.15,
        strategy: 'multi_approach',
      }),

      autonomous: () => ({
        output: `Autonomous evolution for: ${input.task}`,
        quality: 0.75 + Math.random() * 0.15,
        strategy: 'autonomous',
      }),
    };

    return strategies[strategy] ? strategies[strategy]() : strategies.direct();
  }

  /**
   * assessQuality - Quality assessment (constraint functor)
   */
  assessQuality(output) {
    return {
      ...output,
      quality: output.quality || 0,
      assessed: true,
    };
  }

  /**
   * extractPatterns - Pattern extraction (extractor functor)
   */
  extractPatterns(output) {
    return {
      strategy: output.strategy,
      quality: output.quality,
      timestamp: Date.now(),
    };
  }

  /**
   * formatResult - Format final output
   */
  formatResult(state) {
    return {
      output: state._value,
      quality: state.quality,
      iterations: state.iteration,
      context: state.context,
    };
  }
}

// =============================================================================
// PART VI: PRACTICAL UTILITIES
// =============================================================================

/**
 * pipe - Left-to-right function composition
 */
const pipe =
  (...fns) =>
  (x) =>
    fns.reduce((acc, fn) => fn(acc), x);

/**
 * compose - Right-to-left function composition
 */
const compose =
  (...fns) =>
  (x) =>
    fns.reduceRight((acc, fn) => fn(acc), x);

/**
 * curry - Convert function to curried form
 */
const curry = (fn) => {
  const arity = fn.length;
  return function curried(...args) {
    if (args.length >= arity) {
      return fn.apply(this, args);
    }
    return (...moreArgs) => curried.apply(this, args.concat(moreArgs));
  };
};

/**
 * memoize - Cache function results
 */
const memoize = (fn) => {
  const cache = new Map();
  return (...args) => {
    const key = JSON.stringify(args);
    if (!cache.has(key)) {
      cache.set(key, fn(...args));
    }
    return cache.get(key);
  };
};

// =============================================================================
// PART VII: EXAMPLE USAGE
// =============================================================================

/**
 * Example 1: Basic Monadic Iteration
 */
function exampleMonadicIteration() {
  console.log('\n--- Example 1: Monadic Iteration ---\n');

  const improver = (output) =>
    new MetaPromptMonad({
      output: `Improved: ${output}`,
      quality: Math.min(0.95, 0.5 + Math.random() * 0.4),
      iteration: 0,
      context: { improved: true },
    });

  const result = MetaPromptMonad.of('Initial prompt')
    .flatMap(improver)
    .flatMap(improver)
    .flatMap(improver);

  console.log(result.inspect());
}

/**
 * Example 2: Comonadic Context Extraction
 */
function exampleComonadicExtraction() {
  console.log('\n--- Example 2: Comonadic Extraction ---\n');

  const iteration1 = { output: 'v1', quality: 0.6 };
  const iteration2 = { output: 'v2', quality: 0.75 };
  const iteration3 = { output: 'v3', quality: 0.88 };

  const comonad = ContextComonad.of(iteration3, {
    history: [iteration1, iteration2],
    patterns: ['pattern-a', 'pattern-b'],
  });

  // Extract with awareness of context
  const extracted = comonad.extend((w) => ({
    current: w.extract(),
    avgQuality:
      (w.context.history.reduce((sum, i) => sum + i.quality, 0) +
        w.extract().quality) /
      (w.context.history.length + 1),
  }));

  console.log(extracted.inspect());
}

/**
 * Example 3: Stream Comonad for Iteration History
 */
function exampleStreamComonad() {
  console.log('\n--- Example 3: Stream Comonad ---\n');

  const iterations = [
    { output: 'iter-1', quality: 0.5 },
    { output: 'iter-2', quality: 0.65 },
    { output: 'iter-3', quality: 0.78 },
    { output: 'iter-4', quality: 0.85 },
  ];

  const stream = StreamComonad.fromIterations(iterations, 2);

  // Get window around current focus
  const window = stream.window(2, 1);
  console.log('Window around iteration 3:', window);

  // Extend with quality trend analysis
  const withTrend = stream.extend((s) => {
    const w = s.window(2, 0);
    const trend =
      w.left.length > 0
        ? s.extract().quality - w.left[w.left.length - 1].quality
        : 0;
    return {
      ...s.extract(),
      trend: trend > 0 ? 'improving' : trend < 0 ? 'declining' : 'stable',
    };
  });

  console.log('With trend:', withTrend.extract());
}

/**
 * Example 4: Kan Extensions for Strategy Selection
 */
function exampleKanExtensions() {
  console.log('\n--- Example 4: Kan Extensions ---\n');

  // Left Kan: Generate best output from multiple strategies
  const leftKan = new LeftKan(
    (task) => [
      { output: `Direct: ${task}`, quality: 0.7 },
      { output: `Multi: ${task}`, quality: 0.8 },
      { output: `Auto: ${task}`, quality: 0.85 },
    ],
    (output) => ({ ...output, constrained: true })
  );

  const generated = leftKan.run('Build TUI component');
  console.log('Left Kan (best generation):', generated);

  // Right Kan: Extract conservative patterns
  const rightKan = new RightKan(
    (obs) => ({
      hasOutput: !!obs,
      length: typeof obs === 'string' ? obs.length : 0,
    }),
    (input) => [input.output, input.task]
  );

  const extracted = rightKan.run({
    output: 'Generated TUI',
    task: 'Build TUI',
  });
  console.log('Right Kan (conservative extraction):', extracted);
}

/**
 * Example 5: Full Engine Demo
 */
function exampleFullEngine() {
  console.log('\n--- Example 5: Full Meta-Prompt Engine ---\n');

  const engine = new MetaPromptEngine({
    maxIterations: 4,
    qualityThreshold: 0.85,
  });

  const result = engine.process('Create a file browser TUI with Gold/Navy theme');
  console.log('\nFinal Result:', JSON.stringify(result, null, 2));
}

// =============================================================================
// PART VIII: EXPORTS & EXECUTION
// =============================================================================

// Export for Node.js/CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    // Functors
    Functor,
    Monad,
    Comonad,

    // Meta-prompting types
    MetaPromptMonad,
    TaskMonad,
    ContextComonad,
    StreamComonad,

    // Kan extensions
    LeftKan,
    RightKan,

    // Engine
    MetaPromptEngine,

    // Utilities
    pipe,
    compose,
    curry,
    memoize,
  };
}

// Run examples if executed directly
if (typeof require !== 'undefined' && require.main === module) {
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║     NEXUS Categorical JavaScript Templates                   ║');
  console.log('║     Gold (#D4AF37) | Navy Blue (#1B365D)                     ║');
  console.log('╚══════════════════════════════════════════════════════════════╝');

  exampleMonadicIteration();
  exampleComonadicExtraction();
  exampleStreamComonad();
  exampleKanExtensions();
  exampleFullEngine();
}
