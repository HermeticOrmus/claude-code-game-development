# Kan Extension 1: Component Algebra

## Overview

This first Kan extension establishes the algebraic foundation for component composition, introducing categorical abstractions that unify component models across different frameworks.

## Left Kan Extension: Component Universality

```typescript
// Universal component construction via left Kan extension
interface LeftKanComponent<F, G, C> {
  // F: Source framework components
  // G: Target framework components
  // C: Common component interface

  // Universal component
  universal: <Props>(
    source: F<Props>
  ) => {
    component: G<Props>;
    isUniversal: true;
  }

  // Naturality condition
  // For any transformation τ: F → G
  natural: <P, Q>(
    transform: (p: P) => Q,
    component: F<P>
  ) => {
    // Lan(F)(transform) ∘ universal = universal ∘ F(transform)
    transformed: G<Q>;
  }

  // Cocone structure
  cocone: <Props>(
    apex: G<Props>,
    injections: ((f: F<Props>) => G<Props>)[]
  ) => G<Props>
}

// Implementation: React to Any Framework
class UniversalComponentAdapter<Props> {
  private reactComponent: React.FC<Props>;

  constructor(component: React.FC<Props>) {
    this.reactComponent = component;
  }

  // Adapt to Vue
  toVue(): VueComponent<Props> {
    return {
      props: this.extractProps(),
      setup(props: Props) {
        const vnode = createVNode(this.reactComponent, props);
        return () => vnode;
      }
    };
  }

  // Adapt to Svelte
  toSvelte(): SvelteComponent<Props> {
    return class extends SvelteComponentBase {
      constructor(options: any) {
        super();
        this.props = options.props;
      }

      render() {
        return renderReactInSvelte(this.reactComponent, this.props);
      }
    };
  }

  // Adapt to Angular
  toAngular(): Type<any> {
    @Component({
      selector: 'universal-component',
      template: '<div [innerHTML]="content"></div>'
    })
    class AngularAdapter implements OnInit {
      @Input() props!: Props;
      content: string = '';

      ngOnInit() {
        this.content = this.renderReact();
      }

      private renderReact(): string {
        return renderToString(
          React.createElement(this.reactComponent, this.props)
        );
      }
    }
    return AngularAdapter;
  }

  private extractProps(): string[] {
    // Extract prop names via static analysis
    return Object.keys(this.reactComponent.defaultProps || {});
  }
}
```

## Right Kan Extension: Component Lifting

```typescript
// Right Kan extension for lifting components to higher abstraction
interface RightKanLift<Lower, Higher> {
  // Lift lower-level component to higher abstraction
  lift: <C extends Lower>(
    component: C
  ) => Higher & {
    original: C;
    lifted: true;
  }

  // Preservation of structure
  preserve: <P>(
    morphism: (c: Lower) => P
  ) => (lifted: Higher) => P

  // Cone structure
  cone: <H extends Higher>(
    apex: H,
    projections: ((h: H) => Lower)[]
  ) => Lower
}

// DOM to React Component lifting
class DOMToReactLifter implements RightKanLift<Element, React.FC> {
  lift(element: Element): React.FC {
    return function LiftedComponent(props: any) {
      const ref = useRef<HTMLDivElement>(null);

      useEffect(() => {
        if (ref.current) {
          ref.current.appendChild(element.cloneNode(true));
        }
        return () => {
          if (ref.current) {
            ref.current.innerHTML = '';
          }
        };
      }, []);

      return <div ref={ref} {...props} />;
    };
  }

  // Preserve DOM operations
  preserve<P>(
    domOp: (el: Element) => P
  ): (component: React.FC) => P {
    return (component) => {
      const container = document.createElement('div');
      ReactDOM.render(React.createElement(component), container);
      return domOp(container.firstElementChild!);
    };
  }
}
```

## Component Algebra Structures

### 1. Compositional Patterns

```typescript
// Algebraic component composition
interface ComponentAlgebra<C> {
  // Zero: Empty component
  zero: C;

  // Unit: Identity component
  unit: C;

  // Addition: Parallel composition
  add: (a: C, b: C) => C;

  // Multiplication: Sequential composition
  multiply: (a: C, b: C) => C;

  // Exponentiation: Higher-order composition
  exp: (base: C, exponent: number) => C;
}

// React implementation
const ReactComponentAlgebra: ComponentAlgebra<React.FC> = {
  zero: () => null,

  unit: ({ children }) => <>{children}</>,

  add: (A, B) => (props) => (
    <>
      <A {...props} />
      <B {...props} />
    </>
  ),

  multiply: (A, B) => (props) => (
    <A {...props}>
      <B {...props} />
    </A>
  ),

  exp: (Component, n) => {
    if (n === 0) return ReactComponentAlgebra.unit;
    if (n === 1) return Component;

    return (props) => (
      <>
        {Array.from({ length: n }).map((_, i) => (
          <Component key={i} {...props} />
        ))}
      </>
    );
  }
};
```

### 2. Component Transformations

```typescript
// Natural transformation between component functors
interface ComponentTransformation<F, G> {
  // Transform component from functor F to functor G
  transform: <Props>(component: F<Props>) => G<Props>;

  // Naturality square
  // transform ∘ F(f) = G(f) ∘ transform
  natural: <P, Q>(
    f: (p: P) => Q,
    component: F<P>
  ) => void;
}

// HOC as natural transformation
const withLogging = <P extends object>(
  Component: React.ComponentType<P>
): React.ComponentType<P> => {
  return (props: P) => {
    useEffect(() => {
      console.log('Component rendered with props:', props);
    }, [props]);

    return <Component {...props} />;
  };
};

// Composition of transformations
const compose = <P>(...hocs: HOC<P, P>[]): HOC<P, P> => {
  return hocs.reduce((a, b) => (c) => a(b(c)));
};
```

### 3. Component Monoid

```typescript
// Component monoid with identity and associative operation
interface ComponentMonoid<C> {
  // Identity element
  empty: C;

  // Associative binary operation
  concat: (a: C, b: C) => C;

  // Monoid laws
  // 1. Left identity: concat(empty, a) = a
  // 2. Right identity: concat(a, empty) = a
  // 3. Associativity: concat(concat(a, b), c) = concat(a, concat(b, c))
}

// Layout monoid
const LayoutMonoid: ComponentMonoid<React.FC> = {
  empty: () => null,

  concat: (A, B) => (props) => (
    <div style={{ display: 'flex' }}>
      <A {...props} />
      <B {...props} />
    </div>
  )
};

// Style monoid
interface StyleMonoid extends ComponentMonoid<CSSProperties> {
  empty: {};
  concat: (a: CSSProperties, b: CSSProperties) => ({...a, ...b});
}
```

## Advanced Patterns

### 1. Component Optics

```typescript
// Lens for component props
interface ComponentLens<C, A, B> {
  get: (component: C) => A;
  set: (value: B, component: C) => C;
}

// Prism for conditional components
interface ComponentPrism<C, A> {
  preview: (component: C) => A | undefined;
  review: (value: A) => C;
}

// Implementation
const propLens = <P, K extends keyof P>(
  key: K
): ComponentLens<React.FC<P>, P[K], P[K]> => ({
  get: (Component) => {
    // Extract prop type via TypeScript
    return null as any; // Type-level operation
  },
  set: (value, Component) => {
    return (props: P) => (
      <Component {...props} {...{ [key]: value } as P} />
    );
  }
});
```

### 2. Component Comonads

```typescript
// Context comonad for component environments
interface ComponentComonad<C> {
  // Extract component from context
  extract: (context: WithContext<C>) => C;

  // Extend computation over context
  extend: <B>(
    f: (context: WithContext<C>) => B
  ) => (context: WithContext<C>) => WithContext<B>;

  // Duplicate context
  duplicate: (context: WithContext<C>) => WithContext<WithContext<C>>;
}

// Store comonad for component state
interface StoreComonad<S, C> {
  state: S;
  component: (state: S) => C;

  extract: () => C;
  extend: <B>(f: (store: StoreComonad<S, C>) => B) => StoreComonad<S, B>;
  duplicate: () => StoreComonad<S, StoreComonad<S, C>>;
}
```

## Framework Integration Examples

### React Pattern

```typescript
// Component algebra in practice
const Button: React.FC<{ label: string }> = ({ label }) => (
  <button>{label}</button>
);

const Icon: React.FC<{ name: string }> = ({ name }) => (
  <i className={`icon-${name}`} />
);

// Algebraic composition
const IconButton = ReactComponentAlgebra.multiply(
  Button,
  Icon
);

// Higher-order lifting
const LiftedButton = new DOMToReactLifter().lift(
  document.createElement('button')
);

// Universal adapter
const UniversalButton = new UniversalComponentAdapter(Button);
const VueButton = UniversalButton.toVue();
const SvelteButton = UniversalButton.toSvelte();
```

### Vue Pattern

```vue
<script setup lang="ts">
// Component algebra in Vue Composition API
import { defineComponent, h } from 'vue';

const componentAlgebra = {
  zero: () => null,
  unit: (_, { slots }) => slots.default?.(),
  add: (a, b) => defineComponent({
    setup(props, ctx) {
      return () => [h(a, props), h(b, props)];
    }
  }),
  multiply: (a, b) => defineComponent({
    setup(props, ctx) {
      return () => h(a, props, () => h(b, props));
    }
  })
};

// Usage
const Combined = componentAlgebra.add(ButtonComponent, IconComponent);
</script>
```

### Svelte Pattern

```svelte
<script>
// Component algebra in Svelte
class ComponentAlgebra {
  static zero = null;
  static unit = ($$slots) => $$slots.default;

  static add(ComponentA, ComponentB) {
    return {
      render: (props) => `
        ${ComponentA.render(props)}
        ${ComponentB.render(props)}
      `
    };
  }

  static multiply(ComponentA, ComponentB) {
    return {
      render: (props) => `
        <div class="wrapper">
          ${ComponentA.render(props)}
          <div class="nested">
            ${ComponentB.render(props)}
          </div>
        </div>
      `
    };
  }
}
</script>
```

## Performance Optimizations

### Memoization Functor

```typescript
// Memoization as endofunctor
interface MemoFunctor {
  map: <P>(
    component: React.FC<P>
  ) => React.FC<P> & { memoized: true };
}

const MemoizationFunctor: MemoFunctor = {
  map: (component) => Object.assign(
    React.memo(component),
    { memoized: true as const }
  )
};

// Recursive memoization
const deepMemo = <P>(component: React.FC<P>): React.FC<P> => {
  const memoized = React.memo(component);

  // Recursively memoize children
  return (props: P) => {
    const children = React.Children.map(
      props.children,
      child => React.isValidElement(child)
        ? React.cloneElement(child, {
            ...child.props,
            component: deepMemo(child.type as any)
          })
        : child
    );

    return memoized({ ...props, children });
  };
};
```

## Testing Strategies

### Property-Based Testing

```typescript
// Component properties as algebraic laws
interface ComponentProperty<C> {
  name: string;
  check: (component: C) => boolean;
}

const componentProperties: ComponentProperty<React.FC>[] = [
  {
    name: 'render-idempotence',
    check: (Component) => {
      const props = generateProps();
      const render1 = renderToString(<Component {...props} />);
      const render2 = renderToString(<Component {...props} />);
      return render1 === render2;
    }
  },
  {
    name: 'composition-associativity',
    check: (Component) => {
      const A = Component;
      const B = Component;
      const C = Component;

      const left = ReactComponentAlgebra.multiply(
        ReactComponentAlgebra.multiply(A, B),
        C
      );

      const right = ReactComponentAlgebra.multiply(
        A,
        ReactComponentAlgebra.multiply(B, C)
      );

      return isEquivalent(left, right);
    }
  }
];
```

## Next Steps

This component algebra foundation enables:

1. **Universal component adapters** across frameworks
2. **Algebraic composition** patterns
3. **Type-safe transformations** via functors
4. **Performance optimizations** through memoization functors
5. **Property-based testing** of components

Proceed to [Iteration 2: State Management](./iteration-2-state-management.md) for state algebra extensions.