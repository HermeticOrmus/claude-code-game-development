<template>
  <div class="vue-patterns-demo">
    <h1>Vue 3 Composition Patterns</h1>

    <!-- Level 1: Component Composition with Slots -->
    <section class="pattern-section">
      <h2>Compound Components with Slots</h2>
      <TabsComponent v-model="activeTab">
        <template #tabs>
          <TabItem value="tab1">Profile</TabItem>
          <TabItem value="tab2">Settings</TabItem>
          <TabItem value="tab3">Security</TabItem>
        </template>
        <template #panels>
          <TabPanel value="tab1">
            <ProfileContent :user="currentUser" />
          </TabPanel>
          <TabPanel value="tab2">
            <SettingsForm @save="handleSettingsSave" />
          </TabPanel>
          <TabPanel value="tab3">
            <SecurityOptions />
          </TabPanel>
        </template>
      </TabsComponent>
    </section>

    <!-- Level 2: Reactive State Management -->
    <section class="pattern-section">
      <h2>Advanced Reactivity Patterns</h2>
      <div class="state-demo">
        <p>Count: {{ state.count }}</p>
        <p>Doubled: {{ doubled }}</p>
        <p>History Length: {{ history.length }}</p>
        <button @click="increment">Increment</button>
        <button @click="decrement">Decrement</button>
        <button @click="undo" :disabled="!canUndo">Undo</button>
        <button @click="redo" :disabled="!canRedo">Redo</button>
      </div>
    </section>

    <!-- Level 3: Virtual List for Performance -->
    <section class="pattern-section">
      <h2>Virtual Scrolling</h2>
      <VirtualList
        :items="largeDataset"
        :item-height="50"
        :height="400"
        v-slot="{ item, index }"
      >
        <div class="list-item">
          Item #{{ index }}: {{ item.name }}
        </div>
      </VirtualList>
    </section>

    <!-- Level 4: Async Components with Suspense -->
    <section class="pattern-section">
      <h2>Async Component Loading</h2>
      <Suspense>
        <template #default>
          <AsyncDataComponent :query="searchQuery" />
        </template>
        <template #fallback>
          <LoadingSkeleton />
        </template>
      </Suspense>
    </section>

    <!-- Level 5: Teleport for Modals -->
    <section class="pattern-section">
      <h2>Portal Pattern with Teleport</h2>
      <button @click="showModal = true">Open Modal</button>
      <Teleport to="body">
        <Modal v-if="showModal" @close="showModal = false">
          <template #header>
            <h3>Modal Title</h3>
          </template>
          <template #body>
            <p>This modal is teleported to body element</p>
          </template>
        </Modal>
      </Teleport>
    </section>

    <!-- Level 6: Renderless Components -->
    <section class="pattern-section">
      <h2>Renderless Component Pattern</h2>
      <MouseTracker v-slot="{ x, y, isInside }">
        <div class="mouse-area" :class="{ active: isInside }">
          Mouse Position: ({{ x }}, {{ y }})
          <span v-if="isInside">Mouse is inside!</span>
        </div>
      </MouseTracker>
    </section>

    <!-- Level 7: Dynamic Components -->
    <section class="pattern-section">
      <h2>Dynamic Component Loading</h2>
      <div class="component-selector">
        <button
          v-for="comp in availableComponents"
          :key="comp.name"
          @click="selectedComponent = comp.component"
          :class="{ active: selectedComponent === comp.component }"
        >
          {{ comp.name }}
        </button>
      </div>
      <KeepAlive>
        <component :is="selectedComponent" v-bind="componentProps" />
      </KeepAlive>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  ref,
  reactive,
  computed,
  watch,
  watchEffect,
  onMounted,
  onUnmounted,
  provide,
  inject,
  defineAsyncComponent,
  shallowRef,
  triggerRef,
  customRef,
  toRefs,
  readonly,
  isProxy,
  toRaw,
  markRaw,
  effectScope,
  getCurrentScope,
  onScopeDispose,
  unref,
  toRef,
  isRef,
  nextTick,
  defineComponent,
  h,
  Fragment,
  Teleport,
  Suspense,
  KeepAlive,
  type Ref,
  type ComputedRef,
  type UnwrapRef,
  type ComponentPublicInstance
} from 'vue';

// ============================================================================
// Composables - Reusable Logic
// ============================================================================

// 1. State History Composable (Undo/Redo)
function useStateHistory<T>(initialValue: T) {
  const state = ref<T>(initialValue);
  const history = ref<T[]>([initialValue]);
  const future = ref<T[]>([]);
  const historyIndex = ref(0);

  const canUndo = computed(() => historyIndex.value > 0);
  const canRedo = computed(() => future.value.length > 0);

  const commit = (newState: T) => {
    // Clear future on new commit
    future.value = [];
    // Add to history
    history.value = history.value.slice(0, historyIndex.value + 1);
    history.value.push(newState);
    historyIndex.value++;
    state.value = newState;
  };

  const undo = () => {
    if (canUndo.value) {
      future.value.unshift(state.value);
      historyIndex.value--;
      state.value = history.value[historyIndex.value];
    }
  };

  const redo = () => {
    if (canRedo.value) {
      historyIndex.value++;
      state.value = future.value.shift()!;
      history.value[historyIndex.value] = state.value;
    }
  };

  return {
    state: readonly(state),
    commit,
    undo,
    redo,
    canUndo: readonly(canUndo),
    canRedo: readonly(canRedo),
    history: readonly(history)
  };
}

// 2. Fetch Composable with Cache
function useFetch<T>(url: Ref<string> | string) {
  const data = ref<T | null>(null);
  const error = ref<Error | null>(null);
  const loading = ref(false);

  const cache = new Map<string, T>();

  const fetchData = async () => {
    const urlValue = unref(url);

    // Check cache
    if (cache.has(urlValue)) {
      data.value = cache.get(urlValue)!;
      return;
    }

    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(urlValue);
      if (!response.ok) throw new Error(response.statusText);

      const result = await response.json();
      data.value = result;
      cache.set(urlValue, result);
    } catch (e) {
      error.value = e as Error;
    } finally {
      loading.value = false;
    }
  };

  watchEffect(() => {
    fetchData();
  });

  return {
    data: readonly(data),
    error: readonly(error),
    loading: readonly(loading),
    refresh: fetchData
  };
}

// 3. Intersection Observer Composable
function useIntersectionObserver(
  target: Ref<Element | null>,
  options: IntersectionObserverInit = {}
) {
  const isIntersecting = ref(false);
  const entries = ref<IntersectionObserverEntry[]>([]);

  let observer: IntersectionObserver | null = null;

  const cleanup = () => {
    if (observer) {
      observer.disconnect();
      observer = null;
    }
  };

  watchEffect(() => {
    cleanup();

    if (target.value) {
      observer = new IntersectionObserver((observerEntries) => {
        entries.value = observerEntries;
        isIntersecting.value = observerEntries.some(entry => entry.isIntersecting);
      }, options);

      observer.observe(target.value);
    }
  });

  onUnmounted(cleanup);

  return {
    isIntersecting: readonly(isIntersecting),
    entries: readonly(entries)
  };
}

// 4. Local Storage Composable
function useLocalStorage<T>(
  key: string,
  defaultValue: T,
  options?: {
    serializer?: (value: T) => string;
    deserializer?: (value: string) => T;
  }
) {
  const serializer = options?.serializer || JSON.stringify;
  const deserializer = options?.deserializer || JSON.parse;

  const data = ref<T>(defaultValue);

  // Read from localStorage
  const stored = localStorage.getItem(key);
  if (stored) {
    try {
      data.value = deserializer(stored);
    } catch {
      data.value = defaultValue;
    }
  }

  // Watch for changes and save
  watchEffect(() => {
    localStorage.setItem(key, serializer(data.value));
  });

  // Listen for storage events (cross-tab sync)
  const handleStorageChange = (e: StorageEvent) => {
    if (e.key === key && e.newValue) {
      try {
        data.value = deserializer(e.newValue);
      } catch {
        // Invalid data
      }
    }
  };

  onMounted(() => {
    window.addEventListener('storage', handleStorageChange);
  });

  onUnmounted(() => {
    window.removeEventListener('storage', handleStorageChange);
  });

  return data;
}

// 5. Event Bus Composable
function useEventBus<T = any>() {
  const events = new Map<string, Set<(payload: T) => void>>();

  const on = (event: string, handler: (payload: T) => void) => {
    if (!events.has(event)) {
      events.set(event, new Set());
    }
    events.get(event)!.add(handler);

    // Return cleanup function
    return () => off(event, handler);
  };

  const off = (event: string, handler: (payload: T) => void) => {
    events.get(event)?.delete(handler);
  };

  const emit = (event: string, payload: T) => {
    events.get(event)?.forEach(handler => handler(payload));
  };

  const once = (event: string, handler: (payload: T) => void) => {
    const wrappedHandler = (payload: T) => {
      handler(payload);
      off(event, wrappedHandler);
    };
    on(event, wrappedHandler);
  };

  onUnmounted(() => {
    events.clear();
  });

  return { on, off, emit, once };
}

// ============================================================================
// Component Definitions
// ============================================================================

// Virtual List Component
const VirtualList = defineComponent({
  name: 'VirtualList',
  props: {
    items: {
      type: Array as () => any[],
      required: true
    },
    itemHeight: {
      type: Number,
      required: true
    },
    height: {
      type: Number,
      required: true
    }
  },
  setup(props, { slots }) {
    const scrollTop = ref(0);
    const containerRef = ref<HTMLElement>();

    const visibleRange = computed(() => {
      const start = Math.floor(scrollTop.value / props.itemHeight);
      const end = Math.ceil((scrollTop.value + props.height) / props.itemHeight);
      return { start, end };
    });

    const visibleItems = computed(() => {
      const { start, end } = visibleRange.value;
      return props.items.slice(start, end).map((item, index) => ({
        item,
        index: start + index,
        style: {
          position: 'absolute' as const,
          top: `${(start + index) * props.itemHeight}px`,
          height: `${props.itemHeight}px`,
          width: '100%'
        }
      }));
    });

    const totalHeight = computed(() => props.items.length * props.itemHeight);

    const handleScroll = (e: Event) => {
      scrollTop.value = (e.target as HTMLElement).scrollTop;
    };

    return () => h(
      'div',
      {
        ref: containerRef,
        style: {
          height: `${props.height}px`,
          overflow: 'auto',
          position: 'relative'
        },
        onScroll: handleScroll
      },
      [
        h('div', { style: { height: `${totalHeight.value}px` } }),
        ...visibleItems.value.map(({ item, index, style }) =>
          h('div', { style, key: index },
            slots.default?.({ item, index }))
        )
      ]
    );
  }
});

// Mouse Tracker Renderless Component
const MouseTracker = defineComponent({
  name: 'MouseTracker',
  setup(_, { slots }) {
    const x = ref(0);
    const y = ref(0);
    const isInside = ref(false);
    const elementRef = ref<HTMLElement>();

    const handleMouseMove = (e: MouseEvent) => {
      if (elementRef.value) {
        const rect = elementRef.value.getBoundingClientRect();
        x.value = e.clientX - rect.left;
        y.value = e.clientY - rect.top;
      }
    };

    const handleMouseEnter = () => {
      isInside.value = true;
    };

    const handleMouseLeave = () => {
      isInside.value = false;
    };

    onMounted(() => {
      if (elementRef.value) {
        elementRef.value.addEventListener('mousemove', handleMouseMove);
        elementRef.value.addEventListener('mouseenter', handleMouseEnter);
        elementRef.value.addEventListener('mouseleave', handleMouseLeave);
      }
    });

    onUnmounted(() => {
      if (elementRef.value) {
        elementRef.value.removeEventListener('mousemove', handleMouseMove);
        elementRef.value.removeEventListener('mouseenter', handleMouseEnter);
        elementRef.value.removeEventListener('mouseleave', handleMouseLeave);
      }
    });

    return () => h(
      'div',
      { ref: elementRef },
      slots.default?.({ x: x.value, y: y.value, isInside: isInside.value })
    );
  }
});

// ============================================================================
// Main Component Logic
// ============================================================================

// Component state
const activeTab = ref('tab1');
const showModal = ref(false);
const searchQuery = ref('');
const selectedComponent = shallowRef();

// State history example
const {
  state,
  commit: commitState,
  undo,
  redo,
  canUndo,
  canRedo,
  history
} = useStateHistory({ count: 0 });

// Computed properties
const doubled = computed(() => state.value.count * 2);

// Methods
const increment = () => {
  commitState({ count: state.value.count + 1 });
};

const decrement = () => {
  commitState({ count: state.value.count - 1 });
};

const handleSettingsSave = (settings: any) => {
  console.log('Settings saved:', settings);
};

// Current user (mock)
const currentUser = reactive({
  id: 1,
  name: 'John Doe',
  email: 'john@example.com'
});

// Large dataset for virtual scrolling
const largeDataset = Array.from({ length: 10000 }, (_, i) => ({
  id: i,
  name: `Item ${i}`,
  value: Math.random()
}));

// Available dynamic components
const availableComponents = [
  { name: 'Chart', component: defineAsyncComponent(() => import('./ChartComponent.vue')) },
  { name: 'Table', component: defineAsyncComponent(() => import('./TableComponent.vue')) },
  { name: 'Form', component: defineAsyncComponent(() => import('./FormComponent.vue')) }
];

const componentProps = reactive({
  data: [],
  options: {}
});

// Async component
const AsyncDataComponent = defineAsyncComponent({
  loader: () => import('./AsyncDataComponent.vue'),
  delay: 200,
  timeout: 3000,
  errorComponent: defineComponent({
    setup: () => () => h('div', 'Error loading component')
  }),
  loadingComponent: defineComponent({
    setup: () => () => h('div', 'Loading...')
  })
});

// Component placeholders (would be separate files in real app)
const TabsComponent = defineComponent({
  name: 'TabsComponent',
  props: ['modelValue'],
  emits: ['update:modelValue'],
  setup: (props, { slots, emit }) => () => h('div', { class: 'tabs' }, [
    h('div', { class: 'tab-list' }, slots.tabs?.()),
    h('div', { class: 'tab-panels' }, slots.panels?.())
  ])
});

const TabItem = defineComponent({
  props: ['value'],
  setup: (props, { slots }) => () => h('button', { class: 'tab-item' }, slots.default?.())
});

const TabPanel = defineComponent({
  props: ['value'],
  setup: (props, { slots }) => () => h('div', { class: 'tab-panel' }, slots.default?.())
});

const ProfileContent = defineComponent({
  props: ['user'],
  setup: (props) => () => h('div', `Profile: ${props.user.name}`)
});

const SettingsForm = defineComponent({
  emits: ['save'],
  setup: (_, { emit }) => () => h('form', [
    h('input', { type: 'text' }),
    h('button', { onClick: () => emit('save', {}) }, 'Save')
  ])
});

const SecurityOptions = defineComponent({
  setup: () => () => h('div', 'Security Options')
});

const LoadingSkeleton = defineComponent({
  setup: () => () => h('div', { class: 'skeleton' }, 'Loading...')
});

const Modal = defineComponent({
  emits: ['close'],
  setup: (_, { slots, emit }) => () => h('div', { class: 'modal' }, [
    h('div', { class: 'modal-header' }, slots.header?.()),
    h('div', { class: 'modal-body' }, slots.body?.()),
    h('button', { onClick: () => emit('close') }, 'Close')
  ])
});

// Effect scope for cleanup
const scope = effectScope();

scope.run(() => {
  // Effects that should be stopped together
  watchEffect(() => {
    console.log('Active tab changed:', activeTab.value);
  });

  watch(searchQuery, (newQuery) => {
    console.log('Search query:', newQuery);
  });
});

// Cleanup on unmount
onUnmounted(() => {
  scope.stop();
});
</script>

<style scoped>
.vue-patterns-demo {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.pattern-section {
  margin-bottom: 3rem;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.pattern-section h2 {
  margin-bottom: 1rem;
  color: #42b983;
}

.state-demo button {
  margin: 0.25rem;
  padding: 0.5rem 1rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.state-demo button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.list-item {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.mouse-area {
  padding: 2rem;
  border: 2px dashed #ccc;
  border-radius: 8px;
  transition: all 0.3s;
}

.mouse-area.active {
  border-color: #42b983;
  background: rgba(66, 185, 131, 0.1);
}

.component-selector button {
  margin-right: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.component-selector button.active {
  background: #42b983;
  color: white;
  border-color: #42b983;
}

.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  height: 200px;
  border-radius: 8px;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}
</style>