# Kan Extension 2: State Management

## Overview

This second Kan extension builds upon component algebra to introduce sophisticated state management patterns using monadic structures, coalgebras, and optics.

## Left Kan Extension: State Universality

```typescript
// Universal state container via left Kan extension
interface StateKanExtension<Local, Global> {
  // Extend local state to global state space
  extend: <S>(local: Local<S>) => Global<S>;

  // Universal property
  universal: <S, T>(
    f: Local<S> => T
  ) => (global: Global<S>) => T;

  // Cocone for state composition
  cocone: {
    apex: Global<any>;
    injections: Map<string, (local: Local<any>) => Global<any>>;
  };
}

// Implementation: Local to Global State
class UniversalStateManager<State> {
  private stores: Map<string, LocalStore<any>> = new Map();
  private global: GlobalStore<State>;

  constructor(initial: State) {
    this.global = new GlobalStore(initial);
  }

  // Left Kan extension: lift local stores
  liftLocal<S>(
    namespace: string,
    local: LocalStore<S>
  ): GlobalSlice<S> {
    return {
      get: () => this.global.select(namespace),
      set: (value: S) => this.global.update(namespace, value),
      subscribe: (fn) => this.global.subscribe(namespace, fn),

      // Universal mapping
      map: <T>(f: (s: S) => T) => f(this.global.select(namespace))
    };
  }

  // Compose multiple local stores
  compose<Stores extends Record<string, LocalStore<any>>>(
    stores: Stores
  ): GlobalStore<InferGlobalState<Stores>> {
    const composed = {} as any;

    for (const [key, store] of Object.entries(stores)) {
      composed[key] = this.liftLocal(key, store);
    }

    return new GlobalStore(composed);
  }
}
```

## Right Kan Extension: State Projection

```typescript
// Project global state to local views via right Kan extension
interface StateProjection<Global, Local> {
  // Project global state to local view
  project: <S>(
    selector: (global: Global) => S
  ) => Local<S>;

  // Cone structure
  cone: {
    apex: Local<any>;
    projections: ((global: Global) => Local<any>)[];
  };

  // Universal property
  universal: <L extends Local<any>>(
    projections: ((g: Global) => L)[]
  ) => (global: Global) => L;
}

// Lens-based projection
class StateLens<Global, Focus> {
  constructor(
    private get: (global: Global) => Focus,
    private set: (focus: Focus, global: Global) => Global
  ) {}

  // Right Kan extension: create local view
  toLocal(): LocalStore<Focus> {
    return {
      get: () => this.get(globalStore.getState()),
      set: (focus) => globalStore.setState(
        this.set(focus, globalStore.getState())
      ),
      subscribe: (fn) => globalStore.subscribe(() =>
        fn(this.get(globalStore.getState()))
      )
    };
  }

  // Compose lenses
  compose<Next>(
    other: StateLens<Focus, Next>
  ): StateLens<Global, Next> {
    return new StateLens(
      (global) => other.get(this.get(global)),
      (next, global) => this.set(
        other.set(next, this.get(global)),
        global
      )
    );
  }
}
```

## State Monads

### 1. Store Monad

```typescript
// Store as monad for state computations
interface StoreMonad<S> {
  // Monadic operations
  of: <A>(value: A) => Store<S, A>;
  map: <A, B>(f: (a: A) => B, store: Store<S, A>) => Store<S, B>;
  chain: <A, B>(
    f: (a: A) => Store<S, B>,
    store: Store<S, A>
  ) => Store<S, B>;

  // Run computation
  runStore: <A>(store: Store<S, A>, initial: S) => [A, S];
}

class Store<S, A> {
  constructor(
    private computation: (state: S) => [A, S]
  ) {}

  static of<S, A>(value: A): Store<S, A> {
    return new Store((state) => [value, state]);
  }

  map<B>(f: (a: A) => B): Store<S, B> {
    return new Store((state) => {
      const [a, newState] = this.computation(state);
      return [f(a), newState];
    });
  }

  chain<B>(f: (a: A) => Store<S, B>): Store<S, B> {
    return new Store((state) => {
      const [a, state1] = this.computation(state);
      return f(a).computation(state1);
    });
  }

  // State operations
  get(): Store<S, S> {
    return new Store((state) => [state, state]);
  }

  put(newState: S): Store<S, void> {
    return new Store(() => [undefined, newState]);
  }

  modify(f: (s: S) => S): Store<S, void> {
    return new Store((state) => [undefined, f(state)]);
  }
}

// Redux-style reducer as algebra
const reduceM = <S, A>(
  reducer: (state: S, action: A) => S,
  actions: A[]
): Store<S, S> => {
  return actions.reduce(
    (store, action) => store.chain(() =>
      new Store((state) => {
        const newState = reducer(state, action);
        return [newState, newState];
      })
    ),
    Store.of<S, S>(null as any)
  );
};
```

### 2. IO Monad for Effects

```typescript
// IO monad for side effects in state management
class IO<A> {
  constructor(
    private effect: () => A
  ) {}

  static of<A>(value: A): IO<A> {
    return new IO(() => value);
  }

  map<B>(f: (a: A) => B): IO<B> {
    return new IO(() => f(this.effect()));
  }

  chain<B>(f: (a: A) => IO<B>): IO<B> {
    return new IO(() => f(this.effect()).run());
  }

  run(): A {
    return this.effect();
  }
}

// State with IO effects
class StateIO<S, A> {
  constructor(
    private computation: (state: S) => IO<[A, S]>
  ) {}

  static of<S, A>(value: A): StateIO<S, A> {
    return new StateIO((state) => IO.of([value, state]));
  }

  map<B>(f: (a: A) => B): StateIO<S, B> {
    return new StateIO((state) =>
      this.computation(state).map(([a, s]) => [f(a), s])
    );
  }

  chain<B>(f: (a: A) => StateIO<S, B>): StateIO<S, B> {
    return new StateIO((state) =>
      this.computation(state).chain(([a, s1]) =>
        f(a).computation(s1)
      )
    );
  }

  // Lift IO action
  static liftIO<S, A>(io: IO<A>): StateIO<S, A> {
    return new StateIO((state) =>
      io.map(a => [a, state])
    );
  }
}
```

## State Coalgebras

### 1. Observable State

```typescript
// State as F-coalgebra for observations
interface StateCoalgebra<S, O> {
  // Carrier type
  state: S;

  // Structure map: S → F(S)
  observe: (state: S) => {
    value: O;
    next: S;
    observers: Set<(value: O) => void>;
  };

  // Anamorphism (unfold)
  unfold: <A>(
    seed: A,
    f: (a: A) => { value: O; next: A } | null
  ) => Observable<O>;
}

// Observable state implementation
class ObservableState<S> implements StateCoalgebra<S, S> {
  state: S;
  private observers = new Set<(state: S) => void>();

  constructor(initial: S) {
    this.state = initial;
  }

  observe(state: S) {
    return {
      value: state,
      next: state,
      observers: this.observers
    };
  }

  setState(newState: S | ((prev: S) => S)) {
    const next = typeof newState === 'function'
      ? (newState as Function)(this.state)
      : newState;

    this.state = next;
    this.observers.forEach(observer => observer(next));
  }

  subscribe(observer: (state: S) => void): () => void {
    this.observers.add(observer);
    observer(this.state); // Initial notification

    return () => {
      this.observers.delete(observer);
    };
  }

  // Create derived state via coalgebra
  derive<T>(f: (state: S) => T): ObservableState<T> {
    const derived = new ObservableState(f(this.state));

    this.subscribe((state) => {
      derived.setState(f(state));
    });

    return derived;
  }
}
```

### 2. History Coalgebra

```typescript
// State history as cofree coalgebra
interface HistoryCoalgebra<S> {
  current: S;
  history: HistoryCoalgebra<S>[];

  // Coalgebra operations
  record: (state: S) => HistoryCoalgebra<S>;
  undo: () => HistoryCoalgebra<S> | null;
  redo: () => HistoryCoalgebra<S> | null;

  // Cofree comonad operations
  extract: () => S;
  extend: <B>(
    f: (history: HistoryCoalgebra<S>) => B
  ) => HistoryCoalgebra<B>;
}

class StateHistory<S> implements HistoryCoalgebra<S> {
  constructor(
    public current: S,
    public history: StateHistory<S>[] = [],
    private future: StateHistory<S>[] = []
  ) {}

  record(state: S): StateHistory<S> {
    return new StateHistory(
      state,
      [...this.history, this],
      []
    );
  }

  undo(): StateHistory<S> | null {
    const prev = this.history[this.history.length - 1];
    if (!prev) return null;

    return new StateHistory(
      prev.current,
      this.history.slice(0, -1),
      [this, ...this.future]
    );
  }

  redo(): StateHistory<S> | null {
    const next = this.future[0];
    if (!next) return null;

    return new StateHistory(
      next.current,
      [...this.history, this],
      this.future.slice(1)
    );
  }

  extract(): S {
    return this.current;
  }

  extend<B>(
    f: (history: StateHistory<S>) => B
  ): StateHistory<B> {
    return new StateHistory(
      f(this),
      this.history.map(h => h.extend(f)) as any,
      this.future.map(h => h.extend(f)) as any
    );
  }
}
```

## State Optics

### 1. Lenses for Nested State

```typescript
// Lens for focusing on nested state
interface Lens<S, A> {
  get: (s: S) => A;
  set: (a: A) => (s: S) => S;

  // Functor map over focus
  over: (f: (a: A) => A) => (s: S) => S;

  // Compose lenses
  compose: <B>(other: Lens<A, B>) => Lens<S, B>;
}

// Lens creation helpers
const lens = <S, A>(
  get: (s: S) => A,
  set: (a: A) => (s: S) => S
): Lens<S, A> => ({
  get,
  set,
  over: (f) => (s) => set(f(get(s)))(s),
  compose: <B>(other: Lens<A, B>) => lens(
    (s: S) => other.get(get(s)),
    (b: B) => (s: S) => set(other.set(b)(get(s)))(s)
  )
});

// Property lens
const prop = <S, K extends keyof S>(key: K): Lens<S, S[K]> =>
  lens(
    (s) => s[key],
    (a) => (s) => ({ ...s, [key]: a })
  );

// Index lens for arrays
const index = <A>(i: number): Lens<A[], A | undefined> =>
  lens(
    (arr) => arr[i],
    (a) => (arr) => {
      const copy = [...arr];
      if (a !== undefined) copy[i] = a;
      return copy;
    }
  );
```

### 2. Prisms for Optional State

```typescript
// Prism for optional/variant state
interface Prism<S, A> {
  preview: (s: S) => A | undefined;
  review: (a: A) => S;

  // Compose with lens
  composeLens: <B>(lens: Lens<A, B>) => Optional<S, B>;
}

// Optional combining lens and prism
interface Optional<S, A> {
  getOption: (s: S) => A | undefined;
  set: (a: A) => (s: S) => S;
}

// Sum type prism
const some = <A>(): Prism<A | undefined, A> => ({
  preview: (s) => s,
  review: (a) => a,
  composeLens: (lens) => ({
    getOption: (s) => s !== undefined ? lens.get(s) : undefined,
    set: (a) => (s) => s !== undefined ? lens.set(a)(s) : s
  })
});
```

## Framework Integrations

### React Integration

```typescript
// React hooks for state algebra
function useStateMonad<S, A>(
  initial: S,
  computation: Store<S, A>
): [A, S, (s: S) => void] {
  const [state, setState] = useState(initial);
  const [value] = computation.computation(state);

  return [value, state, setState];
}

// Observable state hook
function useObservableState<S>(
  observable: ObservableState<S>
): S {
  const [state, setState] = useState(observable.state);

  useEffect(() => {
    return observable.subscribe(setState);
  }, [observable]);

  return state;
}

// Lens-based state hook
function useLensState<S, A>(
  initial: S,
  lens: Lens<S, A>
): [A, (a: A) => void] {
  const [state, setState] = useState(initial);
  const focus = lens.get(state);

  const setFocus = useCallback((a: A) => {
    setState(lens.set(a));
  }, [lens]);

  return [focus, setFocus];
}

// History hook
function useStateHistory<S>(
  initial: S
): {
  state: S;
  setState: (s: S) => void;
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;
} {
  const [history, setHistory] = useState(
    () => new StateHistory(initial)
  );

  return {
    state: history.current,
    setState: (s: S) => setHistory(h => h.record(s)),
    undo: () => setHistory(h => h.undo() || h),
    redo: () => setHistory(h => h.redo() || h),
    canUndo: history.history.length > 0,
    canRedo: history.future.length > 0
  };
}
```

### Redux Integration

```typescript
// Redux as state monad
type ReduxStore<S, A> = Store<S, A>;

const createReduxMonad = <S>(
  reducer: (state: S, action: any) => S
): StoreMonad<S> => ({
  of: (value) => Store.of(value),

  map: (f, store) => store.map(f),

  chain: (f, store) => store.chain(f),

  runStore: (store, initial) => {
    const reduxStore = createStore(reducer, initial);
    return store.computation(reduxStore.getState());
  }
});

// Lens-based selectors
const createLensSelector = <S, A>(
  lens: Lens<S, A>
): (state: S) => A => {
  return lens.get;
};

// Coalgebraic middleware
const coalgebraMiddleware = <S>(
  coalgebra: StateCoalgebra<S, any>
): Middleware => {
  return store => next => action => {
    const prevState = store.getState();
    const result = next(action);
    const nextState = store.getState();

    if (prevState !== nextState) {
      const observation = coalgebra.observe(nextState);
      observation.observers.forEach(observer =>
        observer(observation.value)
      );
    }

    return result;
  };
};
```

### Zustand Integration

```typescript
// Zustand with optics
interface ZustandWithOptics<S> {
  useLens: <A>(lens: Lens<S, A>) => [A, (a: A) => void];
  usePrism: <A>(prism: Prism<S, A>) => [A | undefined, (a: A) => void];
}

const createOpticsStore = <S>(
  initial: S
): ZustandWithOptics<S> => {
  const useStore = create<S>(() => initial);

  return {
    useLens: (lens) => {
      const state = useStore();
      const focus = lens.get(state);
      const setFocus = (a: A) => useStore.setState(lens.set(a));
      return [focus, setFocus];
    },

    usePrism: (prism) => {
      const state = useStore();
      const preview = prism.preview(state);
      const review = (a: A) => useStore.setState(prism.review(a));
      return [preview, review];
    }
  };
};
```

### MobX Integration

```typescript
// MobX as coalgebra
class MobXCoalgebra<S> implements StateCoalgebra<S, S> {
  @observable state: S;
  private observers = new Set<(state: S) => void>();

  constructor(initial: S) {
    this.state = initial;
    makeAutoObservable(this);
  }

  observe(state: S) {
    return {
      value: state,
      next: state,
      observers: this.observers
    };
  }

  @action
  setState(newState: S) {
    this.state = newState;
  }

  @computed
  get derived() {
    return this.unfold(
      this.state,
      (s) => ({ value: s, next: s })
    );
  }

  unfold<A>(seed: A, f: (a: A) => { value: S; next: A } | null) {
    const values: S[] = [];
    let current = seed;
    let result = f(current);

    while (result) {
      values.push(result.value);
      current = result.next;
      result = f(current);
    }

    return values;
  }
}
```

## Performance Patterns

### 1. Memoized Selectors

```typescript
// Selector memoization via functor
const memoizeSelector = <S, A>(
  selector: (state: S) => A
): ((state: S) => A) => {
  let lastState: S;
  let lastResult: A;

  return (state: S) => {
    if (state !== lastState) {
      lastState = state;
      lastResult = selector(state);
    }
    return lastResult;
  };
};

// Reselect-style composition
const createSelector = <S, Args extends any[], R>(
  selectors: { [K in keyof Args]: (state: S) => Args[K] },
  combiner: (...args: Args) => R
): (state: S) => R => {
  const memoized = memoizeSelector((state: S) => {
    const args = selectors.map(sel => sel(state)) as Args;
    return combiner(...args);
  });

  return memoized;
};
```

### 2. Batched Updates

```typescript
// Batch state updates using monoid
interface BatchMonoid<Update> {
  empty: Update;
  concat: (a: Update, b: Update) => Update;

  // Batch multiple updates
  batch: (updates: Update[]) => Update;
}

const createBatchedStore = <S>() => {
  let pending: ((s: S) => S)[] = [];
  let state: S;
  let flushing = false;

  const flush = () => {
    if (flushing) return;
    flushing = true;

    const updates = pending;
    pending = [];

    state = updates.reduce((s, update) => update(s), state);
    flushing = false;
  };

  return {
    getState: () => state,
    update: (f: (s: S) => S) => {
      pending.push(f);
      if (!flushing) {
        Promise.resolve().then(flush);
      }
    }
  };
};
```

## Next Steps

State management algebra enables:

1. **Universal state containers** via Kan extensions
2. **Monadic state computations** for predictable updates
3. **Coalgebraic observations** for reactive patterns
4. **Optics** for precise state manipulation
5. **Performance optimizations** through algebraic structures

Proceed to [Iteration 3: Performance](./iteration-3-performance.md) for performance optimization patterns.