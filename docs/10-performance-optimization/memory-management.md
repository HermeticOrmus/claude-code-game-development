# Memory Management

Efficient memory management prevents garbage collection pauses and ensures smooth gameplay. This guide covers GC understanding, leak prevention, and memory optimization.

## JavaScript Garbage Collection

### Understanding GC

```typescript
// Bad: Creates garbage every frame
function update() {
  const temp = { x: 0, y: 0 }; // New object each frame
  calculateMovement(temp);
}

// Good: Reuse objects
const temp = { x: 0, y: 0 }; // Created once
function update() {
  temp.x = 0;
  temp.y = 0;
  calculateMovement(temp);
}
```

### Object Pooling Reference

See [Object Pooling](../09-advanced-patterns/object-pooling.md) for detailed implementation.

```typescript
// Reuse objects to avoid GC
const bulletPool = new ObjectPool(() => new Bullet(), 100);

function shoot() {
  const bullet = bulletPool.get();
  bullet.reset(x, y, angle);
}
```

## Memory Leak Prevention

### Common Leak Patterns

```typescript
// Leak: Event listeners not removed
class GameObject {
  constructor() {
    window.addEventListener('resize', this.onResize);
  }

  // Fix: Remove in destroy
  destroy() {
    window.removeEventListener('resize', this.onResize);
  }

  private onResize = () => {
    // Handler
  };
}

// Leak: Circular references
class Parent {
  child?: Child;
}
class Child {
  parent?: Parent;
}

// Fix: Explicit cleanup
destroy() {
  this.child = undefined;
  this.parent = undefined;
}

// Leak: Timers not cleared
const intervalId = setInterval(() => update(), 16);

// Fix: Clear on cleanup
clearInterval(intervalId);
```

### Leak Detection

```typescript
export class LeakDetector {
  private snapshots: number[] = [];

  snapshot(): void {
    if ((performance as any).memory) {
      this.snapshots.push((performance as any).memory.usedJSHeapSize);
    }
  }

  analyze(): LeakAnalysis {
    if (this.snapshots.length < 3) {
      return { isLeaking: false, trend: 'stable' };
    }

    const recent = this.snapshots.slice(-5);
    const growth = recent[recent.length - 1] - recent[0];
    const avgGrowth = growth / recent.length;

    return {
      isLeaking: avgGrowth > 1048576, // >1MB growth
      trend: avgGrowth > 0 ? 'increasing' : 'stable',
      growthRate: avgGrowth
    };
  }
}

interface LeakAnalysis {
  isLeaking: boolean;
  trend: 'increasing' | 'stable' | 'decreasing';
  growthRate?: number;
}
```

## Efficient Data Structures

```typescript
// Use typed arrays for numeric data
const positions = new Float32Array(entityCount * 2);
const velocities = new Float32Array(entityCount * 2);

// Instead of
const entities = entities.map(e => ({ x: e.x, y: e.y, vx: e.vx, vy: e.vy }));
```

## Asset Management

```typescript
export class AssetManager {
  private assets: Map<string, any> = new Map();
  private refCounts: Map<string, number> = new Map();

  retain(key: string): void {
    const count = this.refCounts.get(key) || 0;
    this.refCounts.set(key, count + 1);
  }

  release(key: string): void {
    const count = this.refCounts.get(key) || 0;
    if (count <= 1) {
      this.assets.delete(key);
      this.refCounts.delete(key);
    } else {
      this.refCounts.set(key, count - 1);
    }
  }

  get(key: string): any {
    return this.assets.get(key);
  }
}
```

## Claude Code Prompts

```
Detect and fix memory leaks in my game
```

```
Implement efficient memory management with object pooling
```

```
Optimize data structures for better memory usage
```

## Next Steps

- Explore [Asset Loading](./asset-loading.md)
- Learn [Web Worker Parallelism](./web-worker-parallelism.md)
- Review [Object Pooling](../09-advanced-patterns/object-pooling.md)
