# Object Pooling Pattern

Object pooling is a creational design pattern that reuses objects instead of creating and destroying them, significantly improving performance by reducing garbage collection pressure.

## Table of Contents
- [Why Object Pooling](#why-object-pooling)
- [Pooling Strategies](#pooling-strategies)
- [Performance Benchmarks](#performance-benchmarks)
- [Pool Implementations](#pool-implementations)
- [Claude Code Prompts](#claude-code-prompts)

## Why Object Pooling

### The Problem

```typescript
// Without pooling: Creates garbage
class BulletSystem {
  private bullets: Bullet[] = [];

  update(deltaTime: number) {
    // Remove dead bullets
    this.bullets = this.bullets.filter(bullet => {
      if (bullet.isOutOfBounds()) {
        // Bullet object becomes garbage
        return false;
      }
      bullet.update(deltaTime);
      return true;
    });
  }

  shoot(x: number, y: number) {
    // Creates new object every time
    const bullet = new Bullet(x, y);
    this.bullets.push(bullet);
  }
}

// Problems:
// 1. Frequent object creation
// 2. Garbage collection spikes
// 3. Memory fragmentation
// 4. Inconsistent frame times
```

### The Solution

```typescript
// With pooling: Reuses objects
class BulletPool {
  private pool: Bullet[] = [];
  private active: Bullet[] = [];

  constructor(initialSize: number) {
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(new Bullet(0, 0));
    }
  }

  get(x: number, y: number): Bullet {
    const bullet = this.pool.pop() || new Bullet(0, 0);
    bullet.reset(x, y);
    this.active.push(bullet);
    return bullet;
  }

  release(bullet: Bullet): void {
    const index = this.active.indexOf(bullet);
    if (index !== -1) {
      this.active.splice(index, 1);
      this.pool.push(bullet);
    }
  }

  update(deltaTime: number): void {
    for (let i = this.active.length - 1; i >= 0; i--) {
      const bullet = this.active[i];
      bullet.update(deltaTime);

      if (bullet.isOutOfBounds()) {
        this.release(bullet);
      }
    }
  }
}

// Benefits:
// 1. Minimal object creation
// 2. Predictable memory usage
// 3. Consistent frame times
// 4. Reduced GC pressure
```

## Pooling Strategies

### Fixed-Size Pool

```typescript
export class FixedPool<T> {
  private pool: T[] = [];
  private factory: () => T;
  private reset: (obj: T) => void;

  constructor(
    factory: () => T,
    reset: (obj: T) => void,
    size: number
  ) {
    this.factory = factory;
    this.reset = reset;

    for (let i = 0; i < size; i++) {
      this.pool.push(factory());
    }
  }

  get(): T | null {
    if (this.pool.length === 0) {
      console.warn('Pool exhausted');
      return null;
    }

    const obj = this.pool.pop()!;
    this.reset(obj);
    return obj;
  }

  release(obj: T): void {
    this.pool.push(obj);
  }

  size(): number {
    return this.pool.length;
  }
}

// Usage
const bulletPool = new FixedPool(
  () => new Bullet(),
  (bullet) => bullet.reset(),
  100
);

// Get bullet (returns null if pool exhausted)
const bullet = bulletPool.get();
if (bullet) {
  bullet.setPosition(x, y);
}

// Release bullet
bulletPool.release(bullet);
```

### Growing Pool

```typescript
export class GrowingPool<T> {
  private pool: T[] = [];
  private active: Set<T> = new Set();
  private factory: () => T;
  private reset: (obj: T) => void;
  private growSize: number;

  constructor(
    factory: () => T,
    reset: (obj: T) => void,
    initialSize: number = 10,
    growSize: number = 10
  ) {
    this.factory = factory;
    this.reset = reset;
    this.growSize = growSize;

    for (let i = 0; i < initialSize; i++) {
      this.pool.push(factory());
    }
  }

  get(): T {
    if (this.pool.length === 0) {
      this.grow();
    }

    const obj = this.pool.pop()!;
    this.reset(obj);
    this.active.add(obj);
    return obj;
  }

  release(obj: T): void {
    if (this.active.has(obj)) {
      this.active.delete(obj);
      this.pool.push(obj);
    }
  }

  releaseAll(): void {
    this.active.forEach(obj => this.pool.push(obj));
    this.active.clear();
  }

  private grow(): void {
    for (let i = 0; i < this.growSize; i++) {
      this.pool.push(this.factory());
    }
  }

  getActiveCount(): number {
    return this.active.size;
  }

  getPoolSize(): number {
    return this.pool.length;
  }

  getTotalSize(): number {
    return this.active.size + this.pool.length;
  }
}
```

### Managed Pool with Auto-Release

```typescript
export class ManagedPool<T> {
  private pool: T[] = [];
  private active: Map<T, number> = new Map(); // Object -> timestamp
  private factory: () => T;
  private reset: (obj: T) => void;
  private maxAge: number; // milliseconds

  constructor(
    factory: () => T,
    reset: (obj: T) => void,
    initialSize: number = 10,
    maxAge: number = 5000
  ) {
    this.factory = factory;
    this.reset = reset;
    this.maxAge = maxAge;

    for (let i = 0; i < initialSize; i++) {
      this.pool.push(factory());
    }
  }

  get(): T {
    const obj = this.pool.pop() || this.factory();
    this.reset(obj);
    this.active.set(obj, Date.now());
    return obj;
  }

  release(obj: T): void {
    if (this.active.has(obj)) {
      this.active.delete(obj);
      this.pool.push(obj);
    }
  }

  update(): void {
    const now = Date.now();
    const toRelease: T[] = [];

    this.active.forEach((timestamp, obj) => {
      if (now - timestamp > this.maxAge) {
        toRelease.push(obj);
      }
    });

    toRelease.forEach(obj => this.release(obj));
  }
}
```

## Performance Benchmarks

### Benchmark Code

```typescript
class Particle {
  constructor(
    public x: number = 0,
    public y: number = 0,
    public vx: number = 0,
    public vy: number = 0
  ) {}

  reset(x: number, y: number): void {
    this.x = x;
    this.y = y;
    this.vx = Math.random() * 10 - 5;
    this.vy = Math.random() * 10 - 5;
  }

  update(deltaTime: number): void {
    this.x += this.vx * deltaTime;
    this.y += this.vy * deltaTime;
    this.vy += 9.8 * deltaTime;
  }
}

export class PoolingBenchmark {
  static benchmarkWithoutPooling(iterations: number): number {
    const startTime = performance.now();
    const particles: Particle[] = [];

    for (let i = 0; i < iterations; i++) {
      // Create particles
      for (let j = 0; j < 100; j++) {
        particles.push(new Particle(
          Math.random() * 800,
          Math.random() * 600
        ));
      }

      // Update particles
      particles.forEach(p => p.update(1 / 60));

      // Remove particles (creates garbage)
      particles.length = 0;
    }

    return performance.now() - startTime;
  }

  static benchmarkWithPooling(iterations: number): number {
    const pool = new GrowingPool(
      () => new Particle(),
      (p) => p.reset(0, 0),
      100
    );

    const startTime = performance.now();

    for (let i = 0; i < iterations; i++) {
      const particles: Particle[] = [];

      // Get particles from pool
      for (let j = 0; j < 100; j++) {
        const p = pool.get();
        p.reset(Math.random() * 800, Math.random() * 600);
        particles.push(p);
      }

      // Update particles
      particles.forEach(p => p.update(1 / 60));

      // Release particles back to pool
      particles.forEach(p => pool.release(p));
    }

    return performance.now() - startTime;
  }

  static runBenchmarks(): void {
    const iterations = 1000;

    console.log('Running benchmarks...');

    const withoutPooling = this.benchmarkWithoutPooling(iterations);
    const withPooling = this.benchmarkWithPooling(iterations);

    console.log(`Without pooling: ${withoutPooling.toFixed(2)}ms`);
    console.log(`With pooling: ${withPooling.toFixed(2)}ms`);
    console.log(`Improvement: ${((withoutPooling / withPooling) * 100 - 100).toFixed(1)}% faster`);
  }
}

// Typical results:
// Without pooling: ~450ms
// With pooling: ~150ms
// Improvement: ~200% faster
```

### Memory Profiling

```typescript
export class MemoryProfiler {
  static profileMemoryUsage(): void {
    if (!(performance as any).memory) {
      console.warn('Memory profiling not available');
      return;
    }

    const memory = (performance as any).memory;

    console.log('Memory Usage:');
    console.log(`  Used: ${(memory.usedJSHeapSize / 1048576).toFixed(2)} MB`);
    console.log(`  Total: ${(memory.totalJSHeapSize / 1048576).toFixed(2)} MB`);
    console.log(`  Limit: ${(memory.jsHeapSizeLimit / 1048576).toFixed(2)} MB`);
  }

  static async compareMemory(): Promise<void> {
    console.log('Before test:');
    this.profileMemoryUsage();

    // Test without pooling
    const particles: Particle[] = [];
    for (let i = 0; i < 10000; i++) {
      particles.push(new Particle(0, 0));
    }
    particles.length = 0;

    await new Promise(resolve => setTimeout(resolve, 100));

    console.log('\nAfter creating 10,000 objects without pooling:');
    this.profileMemoryUsage();

    // Force GC (if available)
    if ((global as any).gc) {
      (global as any).gc();
      await new Promise(resolve => setTimeout(resolve, 100));
      console.log('\nAfter GC:');
      this.profileMemoryUsage();
    }
  }
}
```

## Pool Implementations

### Particle Pool

```typescript
export class ParticlePool {
  private pool: Particle[] = [];
  private active: Particle[] = [];
  private maxParticles: number;

  constructor(maxParticles: number = 1000) {
    this.maxParticles = maxParticles;

    for (let i = 0; i < maxParticles; i++) {
      this.pool.push(new Particle());
    }
  }

  emit(x: number, y: number, count: number): void {
    for (let i = 0; i < count; i++) {
      const particle = this.get();
      if (!particle) break;

      particle.reset(x, y);
      particle.vx = Math.random() * 200 - 100;
      particle.vy = Math.random() * 200 - 100;
      particle.lifetime = Math.random() * 2 + 1;
    }
  }

  get(): Particle | null {
    if (this.pool.length === 0) return null;

    const particle = this.pool.pop()!;
    this.active.push(particle);
    return particle;
  }

  release(particle: Particle): void {
    const index = this.active.indexOf(particle);
    if (index !== -1) {
      this.active.splice(index, 1);
      this.pool.push(particle);
    }
  }

  update(deltaTime: number): void {
    for (let i = this.active.length - 1; i >= 0; i--) {
      const particle = this.active[i];
      particle.update(deltaTime);

      if (particle.isDead()) {
        this.release(particle);
      }
    }
  }

  render(ctx: CanvasRenderingContext2D): void {
    this.active.forEach(particle => particle.render(ctx));
  }

  getActiveCount(): number {
    return this.active.length;
  }
}
```

### Bullet Pool

```typescript
export class BulletPool {
  private pool: Bullet[] = [];
  private active: Bullet[] = [];

  constructor(initialSize: number = 50) {
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(new Bullet());
    }
  }

  shoot(x: number, y: number, angle: number, speed: number): Bullet | null {
    const bullet = this.pool.pop();
    if (!bullet) {
      console.warn('Bullet pool exhausted');
      return null;
    }

    bullet.reset(x, y, angle, speed);
    this.active.push(bullet);
    return bullet;
  }

  update(deltaTime: number): void {
    for (let i = this.active.length - 1; i >= 0; i--) {
      const bullet = this.active[i];
      bullet.update(deltaTime);

      if (bullet.isOutOfBounds() || bullet.hasHit) {
        this.release(bullet);
      }
    }
  }

  release(bullet: Bullet): void {
    const index = this.active.indexOf(bullet);
    if (index !== -1) {
      this.active.splice(index, 1);
      this.pool.push(bullet);
    }
  }

  checkCollision(target: { x: number; y: number; radius: number }): Bullet | null {
    for (const bullet of this.active) {
      const dx = bullet.x - target.x;
      const dy = bullet.y - target.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < target.radius + bullet.radius) {
        bullet.hasHit = true;
        return bullet;
      }
    }
    return null;
  }

  render(ctx: CanvasRenderingContext2D): void {
    this.active.forEach(bullet => bullet.render(ctx));
  }

  getActiveCount(): number {
    return this.active.length;
  }

  releaseAll(): void {
    this.active.forEach(bullet => this.pool.push(bullet));
    this.active = [];
  }
}
```

### Enemy Pool

```typescript
export class EnemyPool {
  private pool: Enemy[] = [];
  private active: Enemy[] = [];
  private types: Map<string, () => Enemy> = new Map();

  constructor() {
    this.registerEnemyTypes();
  }

  private registerEnemyTypes(): void {
    this.types.set('basic', () => new BasicEnemy());
    this.types.set('fast', () => new FastEnemy());
    this.types.set('tank', () => new TankEnemy());
  }

  spawn(type: string, x: number, y: number): Enemy | null {
    const factory = this.types.get(type);
    if (!factory) {
      console.error(`Unknown enemy type: ${type}`);
      return null;
    }

    // Try to find an existing enemy of the same type in the pool
    const index = this.pool.findIndex(enemy => enemy.type === type);
    const enemy = index !== -1 ? this.pool.splice(index, 1)[0] : factory();

    enemy.reset(x, y);
    this.active.push(enemy);
    return enemy;
  }

  update(deltaTime: number): void {
    for (let i = this.active.length - 1; i >= 0; i--) {
      const enemy = this.active[i];
      enemy.update(deltaTime);

      if (enemy.isDead()) {
        this.release(enemy);
      }
    }
  }

  release(enemy: Enemy): void {
    const index = this.active.indexOf(enemy);
    if (index !== -1) {
      this.active.splice(index, 1);
      this.pool.push(enemy);
    }
  }

  getActiveEnemies(): Enemy[] {
    return [...this.active];
  }

  getActiveCount(type?: string): number {
    if (type) {
      return this.active.filter(enemy => enemy.type === type).length;
    }
    return this.active.length;
  }

  releaseAll(): void {
    this.active.forEach(enemy => this.pool.push(enemy));
    this.active = [];
  }
}
```

## Claude Code Prompts

```
Create an object pool for bullets in my game with auto-release
```

```
Implement a particle system using object pooling for 1000+ particles
```

```
Add object pooling to my enemy spawning system
```

```
Create a generic object pool class with TypeScript generics
```

```
Benchmark my game with and without object pooling
```

```
Implement a pool manager to handle multiple object types
```

## Best Practices

1. **Pool Sizing**: Start with reasonable size, allow growth if needed
2. **Reset Objects**: Always reset object state when retrieving from pool
3. **Don't Over-Pool**: Not everything needs pooling (UI elements, singletons)
4. **Profile First**: Measure before implementing pooling
5. **Clear References**: Ensure pooled objects don't hold references to active objects
6. **Type Safety**: Use TypeScript generics for type-safe pools
7. **Pool Multiple Types**: Consider separate pools for different object types

## When to Use Pooling

### Good Candidates
- Bullets, projectiles
- Particles, effects
- Enemies, NPCs
- UI elements (damage numbers)
- Audio instances
- Network messages

### Poor Candidates
- Singleton objects
- One-time initialization objects
- Very long-lived objects
- Objects with complex state

## Common Pitfalls

1. **Not Resetting State**: Objects retain state from previous use
2. **Pool Too Small**: Exhausting pool during gameplay
3. **Memory Leaks**: Pooled objects holding references
4. **Over-Optimization**: Pooling everything unnecessarily
5. **Thread Safety**: Pools aren't thread-safe by default

## Next Steps

- Explore [Spatial Partitioning](./spatial-partitioning.md) for collision optimization
- Learn [Entity-Component-System](./entity-component-system.md)
- Review [Performance Optimization](../10-performance-optimization/README.md)
