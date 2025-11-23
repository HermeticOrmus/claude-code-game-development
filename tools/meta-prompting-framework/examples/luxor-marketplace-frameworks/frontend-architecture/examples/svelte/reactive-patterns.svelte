<script lang="ts">
  import { onMount, onDestroy, beforeUpdate, afterUpdate, tick, getContext, setContext, createEventDispatcher } from 'svelte';
  import { writable, readable, derived, get, type Writable, type Readable } from 'svelte/store';
  import { tweened } from 'svelte/motion';
  import { fade, fly, slide, scale, crossfade } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import { flip } from 'svelte/animate';

  // ============================================================================
  // Level 1: Reactive Stores and State Management
  // ============================================================================

  // Custom store with history (undo/redo)
  function createHistoryStore<T>(initial: T) {
    const state = writable(initial);
    const history = writable<T[]>([initial]);
    const future = writable<T[]>([]);
    let currentIndex = 0;

    return {
      subscribe: state.subscribe,
      set: (value: T) => {
        state.set(value);
        history.update(h => [...h.slice(0, currentIndex + 1), value]);
        future.set([]);
        currentIndex++;
      },
      update: (updater: (value: T) => T) => {
        state.update(value => {
          const newValue = updater(value);
          history.update(h => [...h.slice(0, currentIndex + 1), newValue]);
          future.set([]);
          currentIndex++;
          return newValue;
        });
      },
      undo: () => {
        const h = get(history);
        if (currentIndex > 0) {
          currentIndex--;
          const prevValue = h[currentIndex];
          state.set(prevValue);
          future.update(f => [h[currentIndex + 1], ...f]);
        }
      },
      redo: () => {
        const f = get(future);
        if (f.length > 0) {
          const [nextValue, ...rest] = f;
          currentIndex++;
          state.set(nextValue);
          future.set(rest);
        }
      },
      canUndo: derived(history, h => currentIndex > 0),
      canRedo: derived(future, f => f.length > 0)
    };
  }

  // Observable pattern with Svelte stores
  class ObservableStore<T> {
    private store: Writable<T>;
    private listeners = new Set<(value: T) => void>();

    constructor(initial: T) {
      this.store = writable(initial);
      this.store.subscribe(value => {
        this.listeners.forEach(listener => listener(value));
      });
    }

    subscribe(listener: (value: T) => void): () => void {
      this.listeners.add(listener);
      return () => this.listeners.delete(listener);
    }

    set(value: T) {
      this.store.set(value);
    }

    update(updater: (value: T) => T) {
      this.store.update(updater);
    }

    derive<U>(transformer: (value: T) => U): Readable<U> {
      return derived(this.store, transformer);
    }

    // Lens-like focus on nested property
    focus<K extends keyof T>(key: K): {
      subscribe: Readable<T[K]>['subscribe'];
      set: (value: T[K]) => void;
    } {
      return {
        subscribe: derived(this.store, s => s[key]).subscribe,
        set: (value: T[K]) => {
          this.store.update(s => ({ ...s, [key]: value }));
        }
      };
    }
  }

  // ============================================================================
  // Level 2: Advanced Reactive Patterns
  // ============================================================================

  // Async derived store with loading states
  function asyncDerived<T, U>(
    stores: Readable<T> | Readable<T>[],
    fn: (values: T | T[]) => Promise<U>,
    initialValue?: U
  ) {
    const loading = writable(true);
    const error = writable<Error | null>(null);
    const data = writable<U | undefined>(initialValue);

    const derivedStore = derived(stores, (values, set) => {
      loading.set(true);
      error.set(null);

      fn(values)
        .then(result => {
          data.set(result);
          loading.set(false);
        })
        .catch(err => {
          error.set(err);
          loading.set(false);
        });
    });

    return {
      subscribe: data.subscribe,
      loading: { subscribe: loading.subscribe },
      error: { subscribe: error.subscribe }
    };
  }

  // Debounced store for performance
  function debouncedStore<T>(initial: T, delay: number = 300) {
    const store = writable(initial);
    const debouncedValue = writable(initial);
    let timeout: NodeJS.Timeout;

    store.subscribe(value => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        debouncedValue.set(value);
      }, delay);
    });

    return {
      set: store.set,
      update: store.update,
      subscribe: store.subscribe,
      debounced: { subscribe: debouncedValue.subscribe }
    };
  }

  // ============================================================================
  // Level 3: Component Composition
  // ============================================================================

  // Event dispatcher for child-parent communication
  const dispatch = createEventDispatcher<{
    save: { data: any };
    delete: { id: string };
    update: { field: string; value: any };
  }>();

  // Context for deeply nested components
  interface AppContext {
    theme: Writable<'light' | 'dark'>;
    user: Readable<{ name: string; role: string }>;
    api: {
      fetch: (url: string) => Promise<any>;
    };
  }

  const appContext: AppContext = {
    theme: writable('light'),
    user: readable({ name: 'John Doe', role: 'admin' }, () => {}),
    api: {
      fetch: async (url: string) => {
        const response = await fetch(url);
        return response.json();
      }
    }
  };

  setContext('app', appContext);

  // ============================================================================
  // Level 4: Performance Optimization
  // ============================================================================

  // Virtual list implementation
  interface VirtualListItem<T> {
    index: number;
    data: T;
    top: number;
    height: number;
  }

  function createVirtualList<T>(items: T[], itemHeight: number = 50) {
    const scrollTop = writable(0);
    const containerHeight = writable(400);

    const visibleItems = derived(
      [scrollTop, containerHeight],
      ([$scrollTop, $containerHeight]) => {
        const start = Math.floor($scrollTop / itemHeight);
        const end = Math.ceil(($scrollTop + $containerHeight) / itemHeight);

        return items.slice(start, end).map((item, index) => ({
          index: start + index,
          data: item,
          top: (start + index) * itemHeight,
          height: itemHeight
        }));
      }
    );

    const totalHeight = items.length * itemHeight;

    return {
      visibleItems,
      totalHeight,
      scrollTop,
      containerHeight
    };
  }

  // Lazy loading with intersection observer
  function lazyLoad(node: HTMLElement, options: { rootMargin?: string; threshold?: number } = {}) {
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            node.dispatchEvent(new CustomEvent('visible'));
            observer.unobserve(node);
          }
        });
      },
      {
        rootMargin: options.rootMargin || '100px',
        threshold: options.threshold || 0
      }
    );

    observer.observe(node);

    return {
      destroy() {
        observer.disconnect();
      }
    };
  }

  // ============================================================================
  // Level 5: Animation and Transitions
  // ============================================================================

  // Tweened values for smooth animations
  const progress = tweened(0, {
    duration: 400,
    easing: quintOut
  });

  // Crossfade for smooth element transitions
  const [send, receive] = crossfade({
    duration: 300,
    fallback(node) {
      const style = getComputedStyle(node);
      const transform = style.transform === 'none' ? '' : style.transform;

      return {
        duration: 300,
        easing: quintOut,
        css: t => `
          transform: ${transform} scale(${t});
          opacity: ${t}
        `
      };
    }
  });

  // Spring physics store
  import { spring } from 'svelte/motion';

  const coords = spring({ x: 0, y: 0 }, {
    stiffness: 0.2,
    damping: 0.4
  });

  // ============================================================================
  // Level 6: Actions and Directives
  // ============================================================================

  // Clickoutside action
  function clickOutside(node: HTMLElement, callback: () => void) {
    const handleClick = (event: MouseEvent) => {
      if (!node.contains(event.target as Node)) {
        callback();
      }
    };

    document.addEventListener('click', handleClick, true);

    return {
      destroy() {
        document.removeEventListener('click', handleClick, true);
      }
    };
  }

  // Tooltip action
  function tooltip(node: HTMLElement, text: string) {
    const tooltipElement = document.createElement('div');
    tooltipElement.className = 'tooltip';
    tooltipElement.textContent = text;

    function showTooltip() {
      document.body.appendChild(tooltipElement);
      const rect = node.getBoundingClientRect();
      tooltipElement.style.top = `${rect.top - tooltipElement.offsetHeight - 5}px`;
      tooltipElement.style.left = `${rect.left + rect.width / 2 - tooltipElement.offsetWidth / 2}px`;
    }

    function hideTooltip() {
      document.body.removeChild(tooltipElement);
    }

    node.addEventListener('mouseenter', showTooltip);
    node.addEventListener('mouseleave', hideTooltip);

    return {
      update(newText: string) {
        tooltipElement.textContent = newText;
      },
      destroy() {
        node.removeEventListener('mouseenter', showTooltip);
        node.removeEventListener('mouseleave', hideTooltip);
        if (document.body.contains(tooltipElement)) {
          document.body.removeChild(tooltipElement);
        }
      }
    };
  }

  // ============================================================================
  // Component State and Logic
  // ============================================================================

  // Main component state
  const counter = createHistoryStore(0);
  const searchQuery = debouncedStore('', 500);
  const selectedTab = writable('tab1');
  const showModal = writable(false);

  // Large dataset for virtual scrolling
  const largeDataset = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    name: `Item ${i}`,
    value: Math.random() * 100
  }));

  const virtualList = createVirtualList(largeDataset);

  // Async data fetching
  const userData = asyncDerived(
    searchQuery.debounced,
    async (query) => {
      if (!query) return [];
      // Simulated API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      return largeDataset.filter(item =>
        item.name.toLowerCase().includes(query.toLowerCase())
      );
    },
    []
  );

  // Lifecycle hooks
  onMount(() => {
    console.log('Component mounted');

    // Setup global listeners
    const handleKeydown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        showModal.set(false);
      }
    };

    window.addEventListener('keydown', handleKeydown);

    return () => {
      window.removeEventListener('keydown', handleKeydown);
    };
  });

  beforeUpdate(() => {
    console.log('Component will update');
  });

  afterUpdate(() => {
    console.log('Component did update');
  });

  onDestroy(() => {
    console.log('Component will destroy');
  });

  // Methods
  function handleIncrement() {
    counter.update(n => n + 1);
  }

  function handleDecrement() {
    counter.update(n => n - 1);
  }

  function handleSave() {
    dispatch('save', { data: get(counter) });
  }

  function handleScroll(event: Event) {
    const target = event.target as HTMLElement;
    virtualList.scrollTop.set(target.scrollTop);
  }

  // Mouse tracking for interactive demo
  function handleMouseMove(event: MouseEvent) {
    coords.set({
      x: event.clientX,
      y: event.clientY
    });
  }

  // Reactive statements
  $: doubled = $counter * 2;
  $: canUndo = $counter.canUndo;
  $: canRedo = $counter.canRedo;
  $: searchResults = $userData;
  $: isLoading = $userData.loading;
  $: error = $userData.error;

  // Complex reactive derivations
  $: statistics = {
    total: largeDataset.length,
    average: largeDataset.reduce((sum, item) => sum + item.value, 0) / largeDataset.length,
    max: Math.max(...largeDataset.map(item => item.value)),
    min: Math.min(...largeDataset.map(item => item.value))
  };
</script>

<!-- ============================================================================
     HTML Template
     ============================================================================ -->

<div class="svelte-patterns-demo" on:mousemove={handleMouseMove}>
  <h1>Svelte Reactive Patterns</h1>

  <!-- Level 1: Basic Reactivity -->
  <section class="pattern-section">
    <h2>State Management with History</h2>
    <div class="counter-demo">
      <p>Count: {$counter}</p>
      <p>Doubled: {doubled}</p>
      <div class="button-group">
        <button on:click={handleIncrement}>+</button>
        <button on:click={handleDecrement}>-</button>
        <button on:click={() => counter.undo()} disabled={!canUndo}>Undo</button>
        <button on:click={() => counter.redo()} disabled={!canRedo}>Redo</button>
        <button on:click={handleSave}>Save</button>
      </div>
    </div>
  </section>

  <!-- Level 2: Debounced Search -->
  <section class="pattern-section">
    <h2>Async Search with Debouncing</h2>
    <div class="search-demo">
      <input
        type="text"
        placeholder="Search items..."
        bind:value={$searchQuery}
      />
      {#if isLoading}
        <p class="loading">Searching...</p>
      {:else if error}
        <p class="error">Error: {error.message}</p>
      {:else if searchResults.length > 0}
        <ul class="results">
          {#each searchResults as item (item.id)}
            <li animate:flip={{ duration: 300 }}>
              {item.name} - {item.value.toFixed(2)}
            </li>
          {/each}
        </ul>
      {:else if $searchQuery.debounced}
        <p>No results found</p>
      {/if}
    </div>
  </section>

  <!-- Level 3: Virtual Scrolling -->
  <section class="pattern-section">
    <h2>Virtual List (10,000 items)</h2>
    <div
      class="virtual-scroll-container"
      style="height: 400px; overflow-y: auto;"
      on:scroll={handleScroll}
    >
      <div style="height: {virtualList.totalHeight}px; position: relative;">
        {#each $virtualList.visibleItems as item (item.index)}
          <div
            class="virtual-item"
            style="
              position: absolute;
              top: {item.top}px;
              height: {item.height}px;
              width: 100%;
            "
          >
            Item #{item.index}: {item.data.name} - Value: {item.data.value.toFixed(2)}
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Level 4: Tabs with Transitions -->
  <section class="pattern-section">
    <h2>Tab Component with Animations</h2>
    <div class="tabs">
      <div class="tab-list">
        {#each ['tab1', 'tab2', 'tab3'] as tab}
          <button
            class="tab-button"
            class:active={$selectedTab === tab}
            on:click={() => selectedTab.set(tab)}
          >
            {tab === 'tab1' ? 'Profile' : tab === 'tab2' ? 'Settings' : 'Security'}
          </button>
        {/each}
      </div>
      <div class="tab-content">
        {#if $selectedTab === 'tab1'}
          <div in:slide={{ duration: 300 }} out:fade={{ duration: 200 }}>
            <h3>Profile Content</h3>
            <p>User profile information goes here.</p>
          </div>
        {:else if $selectedTab === 'tab2'}
          <div in:slide={{ duration: 300 }} out:fade={{ duration: 200 }}>
            <h3>Settings Content</h3>
            <p>Application settings go here.</p>
          </div>
        {:else if $selectedTab === 'tab3'}
          <div in:slide={{ duration: 300 }} out:fade={{ duration: 200 }}>
            <h3>Security Content</h3>
            <p>Security options go here.</p>
          </div>
        {/if}
      </div>
    </div>
  </section>

  <!-- Level 5: Modal with Portal -->
  <section class="pattern-section">
    <h2>Modal with Actions</h2>
    <button on:click={() => showModal.set(true)}>Open Modal</button>

    {#if $showModal}
      <div class="modal-backdrop" transition:fade={{ duration: 200 }}>
        <div
          class="modal"
          transition:scale={{ duration: 300, start: 0.8 }}
          use:clickOutside={() => showModal.set(false)}
        >
          <h3>Modal Title</h3>
          <p>This modal uses the clickOutside action.</p>
          <p>Press ESC or click outside to close.</p>
          <button on:click={() => showModal.set(false)}>Close</button>
        </div>
      </div>
    {/if}
  </section>

  <!-- Level 6: Interactive Elements -->
  <section class="pattern-section">
    <h2>Interactive Elements</h2>

    <!-- Progress bar with tweened animation -->
    <div class="progress-demo">
      <button on:click={() => progress.set(0)}>0%</button>
      <button on:click={() => progress.set(50)}>50%</button>
      <button on:click={() => progress.set(100)}>100%</button>
      <div class="progress-bar">
        <div class="progress-fill" style="width: {$progress}%"></div>
      </div>
      <p>{$progress.toFixed(0)}%</p>
    </div>

    <!-- Tooltip demo -->
    <div class="tooltip-demo">
      <button use:tooltip={'This is a tooltip!'}>
        Hover for tooltip
      </button>
    </div>

    <!-- Mouse follower -->
    <div
      class="mouse-follower"
      style="transform: translate({$coords.x - 10}px, {$coords.y - 10}px)"
    />
  </section>

  <!-- Level 7: Lazy Loading -->
  <section class="pattern-section">
    <h2>Lazy Loaded Content</h2>
    {#each Array(5) as _, i}
      <div
        class="lazy-item"
        use:lazyLoad
        on:visible={() => console.log(`Item ${i} is visible`)}
      >
        <div class="placeholder">
          Lazy loaded item {i}
        </div>
      </div>
    {/each}
  </section>

  <!-- Statistics Display -->
  <section class="pattern-section">
    <h2>Dataset Statistics</h2>
    <div class="stats">
      <div class="stat">
        <span class="label">Total Items:</span>
        <span class="value">{statistics.total}</span>
      </div>
      <div class="stat">
        <span class="label">Average Value:</span>
        <span class="value">{statistics.average.toFixed(2)}</span>
      </div>
      <div class="stat">
        <span class="label">Max Value:</span>
        <span class="value">{statistics.max.toFixed(2)}</span>
      </div>
      <div class="stat">
        <span class="label">Min Value:</span>
        <span class="value">{statistics.min.toFixed(2)}</span>
      </div>
    </div>
  </section>
</div>

<!-- ============================================================================
     Styles
     ============================================================================ -->

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  }

  .svelte-patterns-demo {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    position: relative;
  }

  .pattern-section {
    margin-bottom: 3rem;
    padding: 1.5rem;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background: white;
  }

  .pattern-section h2 {
    margin-top: 0;
    color: #ff3e00;
  }

  /* Counter Demo */
  .counter-demo {
    text-align: center;
  }

  .button-group {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
  }

  button {
    padding: 0.5rem 1rem;
    background: #ff3e00;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
  }

  button:hover:not(:disabled) {
    background: #ff5a00;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Search Demo */
  .search-demo input {
    width: 100%;
    padding: 0.5rem;
    font-size: 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .results {
    list-style: none;
    padding: 0;
    margin: 1rem 0;
  }

  .results li {
    padding: 0.5rem;
    border-bottom: 1px solid #eee;
  }

  .loading {
    color: #666;
    font-style: italic;
  }

  .error {
    color: #d32f2f;
  }

  /* Virtual Scroll */
  .virtual-scroll-container {
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .virtual-item {
    padding: 1rem;
    border-bottom: 1px solid #eee;
    display: flex;
    align-items: center;
  }

  /* Tabs */
  .tabs {
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
  }

  .tab-list {
    display: flex;
    background: #f5f5f5;
  }

  .tab-button {
    flex: 1;
    padding: 1rem;
    background: transparent;
    border: none;
    border-radius: 0;
    color: #666;
  }

  .tab-button.active {
    background: white;
    color: #ff3e00;
    border-bottom: 2px solid #ff3e00;
  }

  .tab-content {
    padding: 1.5rem;
  }

  /* Modal */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    max-width: 500px;
    width: 90%;
  }

  /* Progress Bar */
  .progress-demo {
    text-align: center;
  }

  .progress-bar {
    width: 100%;
    height: 20px;
    background: #f0f0f0;
    border-radius: 10px;
    overflow: hidden;
    margin: 1rem 0;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #ff3e00, #ff5a00);
    transition: width 0.3s;
  }

  /* Tooltip */
  :global(.tooltip) {
    position: absolute;
    background: #333;
    color: white;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
    pointer-events: none;
    z-index: 2000;
  }

  .tooltip-demo {
    margin: 1rem 0;
  }

  /* Mouse Follower */
  .mouse-follower {
    position: fixed;
    width: 20px;
    height: 20px;
    background: radial-gradient(circle, #ff3e00, transparent);
    border-radius: 50%;
    pointer-events: none;
    z-index: 999;
    transition: transform 0.1s;
  }

  /* Lazy Items */
  .lazy-item {
    margin: 1rem 0;
    min-height: 100px;
  }

  .placeholder {
    padding: 2rem;
    background: #f5f5f5;
    border-radius: 4px;
    text-align: center;
  }

  /* Statistics */
  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .stat {
    padding: 1rem;
    background: #f9f9f9;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
  }

  .stat .label {
    font-weight: bold;
    color: #666;
  }

  .stat .value {
    color: #ff3e00;
    font-size: 1.2rem;
  }
</style>