// React Component Patterns - Comprehensive Examples

import React, { useState, useEffect, useCallback, useMemo, useRef, createContext, useContext } from 'react';
import type { FC, ComponentType, ReactNode } from 'react';

// ============================================================================
// Level 1: Component Algebra
// ============================================================================

// Functor pattern for component composition
interface ComponentFunctor<Props> {
  map<A, B>(f: (a: A) => B, component: FC<A>): FC<B>;
}

const ComponentFunctor: ComponentFunctor<any> = {
  map: (f, Component) => (props) => <Component {...f(props)} />
};

// Monoid pattern for component concatenation
interface ComponentMonoid {
  empty: FC;
  concat: (a: FC, b: FC) => FC;
}

const LayoutMonoid: ComponentMonoid = {
  empty: () => null,
  concat: (A, B) => (props) => (
    <>
      <A {...props} />
      <B {...props} />
    </>
  )
};

// Higher-order component as natural transformation
type HOC<InnerProps, OuterProps = InnerProps> = (
  Component: ComponentType<InnerProps>
) => ComponentType<OuterProps>;

// Composition of HOCs
const compose = <P,>(...hocs: HOC<P>[]): HOC<P> => {
  return hocs.reduce((a, b) => (c) => a(b(c)));
};

// ============================================================================
// Level 2: State Management with Optics
// ============================================================================

// Lens for nested state access
interface Lens<S, A> {
  get: (s: S) => A;
  set: (a: A) => (s: S) => S;
  over: (f: (a: A) => A) => (s: S) => S;
}

function lens<S, A>(
  get: (s: S) => A,
  set: (a: A) => (s: S) => S
): Lens<S, A> {
  return {
    get,
    set,
    over: (f) => (s) => set(f(get(s)))(s)
  };
}

// Property lens helper
function prop<S, K extends keyof S>(key: K): Lens<S, S[K]> {
  return lens(
    (s) => s[key],
    (a) => (s) => ({ ...s, [key]: a })
  );
}

// Custom hook using lens
function useLensState<S, A>(
  initial: S,
  lens: Lens<S, A>
): [A, (a: A | ((prev: A) => A)) => void] {
  const [state, setState] = useState(initial);
  const focus = lens.get(state);

  const setFocus = useCallback((value: A | ((prev: A) => A)) => {
    setState((prev) => {
      const newValue = typeof value === 'function'
        ? value(lens.get(prev))
        : value;
      return lens.set(newValue)(prev);
    });
  }, [lens]);

  return [focus, setFocus];
}

// ============================================================================
// Level 3: Performance Optimization
// ============================================================================

// Memoization functor
class MemoizationFunctor {
  static memoize<P extends object>(
    Component: FC<P>,
    arePropsEqual?: (prev: P, next: P) => boolean
  ): FC<P> {
    return React.memo(Component, arePropsEqual);
  }

  static deepMemoize<P extends object>(Component: FC<P>): FC<P> {
    const MemoizedComponent = React.memo(Component);

    return (props: P) => {
      const memoizedChildren = useMemo(() => {
        if (!props.children) return undefined;

        return React.Children.map(props.children, (child) => {
          if (React.isValidElement(child)) {
            return React.cloneElement(child, {
              ...child.props,
              key: child.key
            });
          }
          return child;
        });
      }, [props.children]);

      return <MemoizedComponent {...props}>{memoizedChildren}</MemoizedComponent>;
    };
  }
}

// Virtual list for performance
interface VirtualListProps<T> {
  items: T[];
  height: number;
  itemHeight: number;
  renderItem: (item: T, index: number) => ReactNode;
}

function VirtualList<T>({ items, height, itemHeight, renderItem }: VirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    items.length - 1,
    Math.floor((scrollTop + height) / itemHeight)
  );

  const visibleItems = items.slice(startIndex, endIndex + 1);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;

  return (
    <div
      style={{ height, overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) => (
            <div key={startIndex + index} style={{ height: itemHeight }}>
              {renderItem(item, startIndex + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Level 4: Advanced Patterns
// ============================================================================

// Store comonad pattern
interface StoreComonad<S, A> {
  state: S;
  render: (state: S) => A;
  extract: () => A;
  extend: <B>(f: (store: StoreComonad<S, A>) => B) => StoreComonad<S, B>;
  seek: (state: S) => StoreComonad<S, A>;
}

class Store<S, A> implements StoreComonad<S, A> {
  constructor(public state: S, public render: (state: S) => A) {}

  extract(): A {
    return this.render(this.state);
  }

  extend<B>(f: (store: Store<S, A>) => B): Store<S, B> {
    return new Store(this.state, (s) => f(new Store(s, this.render)));
  }

  seek(state: S): Store<S, A> {
    return new Store(state, this.render);
  }
}

// Observable state with coalgebra
class ObservableState<S> {
  private state: S;
  private observers = new Set<(state: S) => void>();

  constructor(initial: S) {
    this.state = initial;
  }

  getState(): S {
    return this.state;
  }

  setState(newState: S | ((prev: S) => S)): void {
    const nextState = typeof newState === 'function'
      ? (newState as (prev: S) => S)(this.state)
      : newState;

    this.state = nextState;
    this.observers.forEach(observer => observer(nextState));
  }

  subscribe(observer: (state: S) => void): () => void {
    this.observers.add(observer);
    observer(this.state); // Initial notification

    return () => {
      this.observers.delete(observer);
    };
  }

  // Derive new observable via functor map
  map<T>(f: (state: S) => T): ObservableState<T> {
    const derived = new ObservableState(f(this.state));

    this.subscribe((state) => {
      derived.setState(f(state));
    });

    return derived;
  }
}

// Hook for observable state
function useObservable<S>(observable: ObservableState<S>): S {
  const [state, setState] = useState(observable.getState());

  useEffect(() => {
    return observable.subscribe(setState);
  }, [observable]);

  return state;
}

// ============================================================================
// Level 5: Compound Components
// ============================================================================

// Context-based compound component pattern
interface TabsContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextType | null>(null);

interface TabsCompound {
  Root: FC<{ children: ReactNode; defaultTab?: string }>;
  List: FC<{ children: ReactNode }>;
  Tab: FC<{ value: string; children: ReactNode }>;
  Panel: FC<{ value: string; children: ReactNode }>;
}

const Tabs: TabsCompound = {
  Root: ({ children, defaultTab = '' }) => {
    const [activeTab, setActiveTab] = useState(defaultTab);

    return (
      <TabsContext.Provider value={{ activeTab, setActiveTab }}>
        <div className="tabs">{children}</div>
      </TabsContext.Provider>
    );
  },

  List: ({ children }) => (
    <div className="tabs-list" role="tablist">
      {children}
    </div>
  ),

  Tab: ({ value, children }) => {
    const context = useContext(TabsContext);
    if (!context) throw new Error('Tab must be used within Tabs');

    return (
      <button
        role="tab"
        aria-selected={context.activeTab === value}
        onClick={() => context.setActiveTab(value)}
        className={context.activeTab === value ? 'active' : ''}
      >
        {children}
      </button>
    );
  },

  Panel: ({ value, children }) => {
    const context = useContext(TabsContext);
    if (!context) throw new Error('Panel must be used within Tabs');

    if (context.activeTab !== value) return null;

    return (
      <div role="tabpanel" className="tab-panel">
        {children}
      </div>
    );
  }
};

// ============================================================================
// Level 6: Render Props & Hooks Composition
// ============================================================================

// Render prop pattern with type safety
interface RenderPropComponent<T> {
  data: T;
  children: (data: T) => ReactNode;
}

function DataProvider<T>({ data, children }: RenderPropComponent<T>) {
  return <>{children(data)}</>;
}

// Hook composition pattern
function useComposedState<S>(initial: S) {
  const [state, setState] = useState(initial);
  const [history, setHistory] = useState<S[]>([initial]);
  const [future, setFuture] = useState<S[]>([]);

  const set = useCallback((newState: S | ((prev: S) => S)) => {
    setState((prev) => {
      const next = typeof newState === 'function'
        ? (newState as (prev: S) => S)(prev)
        : newState;

      setHistory((h) => [...h, prev]);
      setFuture([]);
      return next;
    });
  }, []);

  const undo = useCallback(() => {
    if (history.length > 1) {
      const previous = history[history.length - 1];
      setHistory((h) => h.slice(0, -1));
      setFuture((f) => [state, ...f]);
      setState(previous);
    }
  }, [state, history]);

  const redo = useCallback(() => {
    if (future.length > 0) {
      const next = future[0];
      setFuture((f) => f.slice(1));
      setHistory((h) => [...h, state]);
      setState(next);
    }
  }, [state, future]);

  return {
    state,
    set,
    undo,
    redo,
    canUndo: history.length > 1,
    canRedo: future.length > 0
  };
}

// ============================================================================
// Level 7: Error Boundaries & Suspense
// ============================================================================

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<
  { children: ReactNode; fallback: (error: Error) => ReactNode },
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError && this.state.error) {
      return this.props.fallback(this.state.error);
    }

    return this.props.children;
  }
}

// Suspense with data fetching
function createResource<T>(promise: Promise<T>) {
  let status: 'pending' | 'success' | 'error' = 'pending';
  let result: T;
  let error: any;

  const suspender = promise.then(
    (data) => {
      status = 'success';
      result = data;
    },
    (err) => {
      status = 'error';
      error = err;
    }
  );

  return {
    read() {
      if (status === 'pending') throw suspender;
      if (status === 'error') throw error;
      return result;
    }
  };
}

// ============================================================================
// Example Usage
// ============================================================================

export function ExampleApp() {
  // Using lens state
  const [user, setUserName] = useLensState(
    { name: 'John', age: 30 },
    prop<{ name: string; age: number }, 'name'>('name')
  );

  // Using composed state with history
  const { state, set, undo, redo, canUndo, canRedo } = useComposedState({
    count: 0,
    text: ''
  });

  // Using observable
  const observable = useMemo(() => new ObservableState({ value: 0 }), []);
  const observedValue = useObservable(observable);

  return (
    <ErrorBoundary fallback={(error) => <div>Error: {error.message}</div>}>
      <div className="app">
        <h1>React Component Patterns</h1>

        {/* Compound Components */}
        <Tabs.Root defaultTab="tab1">
          <Tabs.List>
            <Tabs.Tab value="tab1">Tab 1</Tabs.Tab>
            <Tabs.Tab value="tab2">Tab 2</Tabs.Tab>
          </Tabs.List>
          <Tabs.Panel value="tab1">Content 1</Tabs.Panel>
          <Tabs.Panel value="tab2">Content 2</Tabs.Panel>
        </Tabs.Root>

        {/* Virtual List */}
        <VirtualList
          items={Array.from({ length: 1000 }, (_, i) => `Item ${i}`)}
          height={400}
          itemHeight={50}
          renderItem={(item) => <div>{item}</div>}
        />

        {/* State Management Examples */}
        <div>
          <p>User name (via lens): {user}</p>
          <button onClick={() => setUserName('Jane')}>Change Name</button>
        </div>

        <div>
          <p>Composed state: {JSON.stringify(state)}</p>
          <button onClick={() => set((s) => ({ ...s, count: s.count + 1 }))}>
            Increment
          </button>
          <button onClick={undo} disabled={!canUndo}>Undo</button>
          <button onClick={redo} disabled={!canRedo}>Redo</button>
        </div>

        <div>
          <p>Observable value: {observedValue.value}</p>
          <button onClick={() => observable.setState({ value: observedValue.value + 1 })}>
            Update Observable
          </button>
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default ExampleApp;