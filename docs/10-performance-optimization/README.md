# Performance Optimization for Web Games

Performance optimization is crucial for delivering smooth, responsive game experiences across all devices. This section covers profiling, optimization techniques, and best practices.

## Overview

Web games must maintain consistent frame rates (typically 60 FPS) while managing limited resources. Poor performance leads to choppy gameplay, input lag, and player frustration.

## Optimization Philosophy

### The Three Rules of Optimization

1. **Don't optimize prematurely**: Profile first, optimize later
2. **Measure everything**: Use data to guide decisions
3. **Focus on bottlenecks**: 80% of time is spent in 20% of code

### Performance Budget

Set performance targets for your game:

- **Target FPS**: 60 FPS (16.67ms per frame)
- **Load Time**: < 3 seconds initial load
- **Memory**: < 100 MB on mobile, < 500 MB on desktop
- **Bundle Size**: < 5 MB initial download

## Common Performance Bottlenecks

### Rendering (GPU)

**Symptoms**: Low FPS, stuttering during visual effects

**Common Causes**:
- Too many draw calls
- Overdraw (rendering same pixel multiple times)
- Large textures
- Complex shaders
- Inefficient particle systems

**Solutions**: Covered in [Rendering Optimization](./rendering-optimization.md)

### JavaScript Execution (CPU)

**Symptoms**: Frame drops during gameplay logic, slow AI

**Common Causes**:
- Inefficient algorithms (O(n²) collision detection)
- Excessive object creation
- Synchronous operations blocking main thread
- Unoptimized loops

**Solutions**: Profile code, use efficient algorithms, optimize hot paths

### Memory (RAM)

**Symptoms**: Garbage collection pauses, crashes on mobile

**Common Causes**:
- Memory leaks
- Large object allocations
- No object pooling
- Unoptimized asset loading

**Solutions**: Covered in [Memory Management](./memory-management.md)

### Network (I/O)

**Symptoms**: Slow loading, lag in multiplayer

**Common Causes**:
- Large asset downloads
- No compression
- Blocking asset loads
- Poor CDN configuration

**Solutions**: Covered in [Asset Loading](./asset-loading.md)

## Performance Metrics

### Key Metrics to Track

```typescript
export class PerformanceMonitor {
  private frameCount: number = 0;
  private lastTime: number = performance.now();
  private fps: number = 60;
  private frameTime: number = 16.67;

  update(): void {
    const currentTime = performance.now();
    const deltaTime = currentTime - this.lastTime;

    this.frameCount++;

    if (deltaTime >= 1000) {
      this.fps = (this.frameCount / deltaTime) * 1000;
      this.frameTime = deltaTime / this.frameCount;
      this.frameCount = 0;
      this.lastTime = currentTime;

      this.reportMetrics();
    }
  }

  private reportMetrics(): void {
    console.log(`FPS: ${this.fps.toFixed(2)}`);
    console.log(`Frame Time: ${this.frameTime.toFixed(2)}ms`);

    if ((performance as any).memory) {
      const memory = (performance as any).memory;
      console.log(`Memory: ${(memory.usedJSHeapSize / 1048576).toFixed(2)} MB`);
    }
  }

  getMetrics() {
    return {
      fps: this.fps,
      frameTime: this.frameTime,
      memory: (performance as any).memory?.usedJSHeapSize || 0
    };
  }
}
```

### Target Specifications

| Device | Target FPS | Max Frame Time | Memory Budget |
|--------|------------|----------------|---------------|
| Desktop (High) | 60 | 16.67ms | 500 MB |
| Desktop (Low) | 30 | 33.33ms | 250 MB |
| Mobile (High) | 60 | 16.67ms | 150 MB |
| Mobile (Low) | 30 | 33.33ms | 75 MB |

## Optimization Workflow

### 1. Establish Baseline

```typescript
// Record initial metrics
const before = {
  fps: monitor.getMetrics().fps,
  memory: monitor.getMetrics().memory,
  loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart
};
```

### 2. Profile

Use browser DevTools to identify bottlenecks:
- Performance tab: CPU profiling
- Memory tab: Heap snapshots, allocation timeline
- Network tab: Asset loading

Covered in detail: [Profiling & Debugging](./profiling-debugging.md)

### 3. Optimize

Focus on the biggest bottlenecks first:
- Rendering: Reduce draw calls, optimize shaders
- CPU: Optimize algorithms, use Web Workers
- Memory: Object pooling, reduce allocations
- Network: Compress assets, lazy loading

### 4. Measure Impact

```typescript
const after = {
  fps: monitor.getMetrics().fps,
  memory: monitor.getMetrics().memory,
  loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart
};

const improvement = {
  fps: ((after.fps - before.fps) / before.fps) * 100,
  memory: ((before.memory - after.memory) / before.memory) * 100,
  loadTime: ((before.loadTime - after.loadTime) / before.loadTime) * 100
};

console.log(`FPS improved by ${improvement.fps.toFixed(1)}%`);
console.log(`Memory reduced by ${improvement.memory.toFixed(1)}%`);
console.log(`Load time improved by ${improvement.loadTime.toFixed(1)}%`);
```

### 5. Repeat

Continue profiling and optimizing until performance targets are met.

## Quick Wins

### Immediate Optimizations

1. **Enable Texture Compression**: Reduces download and GPU memory
2. **Implement Object Pooling**: Eliminates GC pauses
3. **Use Sprite Atlases**: Reduces draw calls dramatically
4. **Lazy Load Assets**: Only load what's needed
5. **Minify and Compress**: Reduce bundle size
6. **Use CDN**: Faster asset delivery

### Code-Level Optimizations

```typescript
// Bad: Creates objects in game loop
function update() {
  const velocity = { x: 0, y: 0 }; // Creates object every frame
  player.move(velocity);
}

// Good: Reuse objects
const velocity = { x: 0, y: 0 }; // Created once
function update() {
  velocity.x = 0;
  velocity.y = 0;
  player.move(velocity);
}

// Bad: O(n²) collision detection
for (let i = 0; i < entities.length; i++) {
  for (let j = 0; j < entities.length; j++) {
    checkCollision(entities[i], entities[j]);
  }
}

// Good: O(n log n) with spatial partitioning
const quadtree = new Quadtree(/* ... */);
entities.forEach(entity => {
  const nearby = quadtree.retrieve(entity);
  nearby.forEach(other => checkCollision(entity, other));
});
```

## Platform-Specific Considerations

### Mobile Optimization

- Reduce draw calls (< 50 per frame)
- Lower texture resolution
- Simplify shaders
- Reduce particle count
- Optimize for battery life

Details: [Mobile Optimization](./mobile-optimization.md)

### Desktop Optimization

- Higher quality settings available
- More aggressive LOD
- Complex post-processing
- Higher particle counts

### Web vs Native

Web constraints:
- No direct GPU access
- Limited multithreading
- Browser overhead
- Sandboxed environment

Advantages:
- Instant loading (if optimized)
- No installation
- Cross-platform by default

## Section Navigation

1. **[Profiling & Debugging](./profiling-debugging.md)** - Identifying performance bottlenecks
2. **[Rendering Optimization](./rendering-optimization.md)** - GPU and draw call optimization
3. **[Memory Management](./memory-management.md)** - Reducing GC pressure and leaks
4. **[Asset Loading](./asset-loading.md)** - Loading strategies and compression
5. **[Web Worker Parallelism](./web-worker-parallelism.md)** - Offloading computation
6. **[Mobile Optimization](./mobile-optimization.md)** - Mobile-specific techniques

## Performance Checklist

### Pre-Launch Checklist

- [ ] Target 60 FPS on mid-range devices
- [ ] No memory leaks detected
- [ ] Load time < 3 seconds
- [ ] Mobile performance tested
- [ ] Assets compressed and optimized
- [ ] Object pooling implemented
- [ ] Spatial partitioning for collisions
- [ ] Profiled on low-end devices
- [ ] Browser compatibility tested
- [ ] Network conditions tested (3G, 4G)

### Continuous Monitoring

- [ ] FPS monitoring in production
- [ ] Error tracking
- [ ] Load time analytics
- [ ] Memory usage tracking
- [ ] Player feedback collection

## Tools and Resources

### Browser Tools
- Chrome DevTools Performance profiler
- Firefox Performance profiler
- Safari Web Inspector

### Libraries
- stats.js: FPS monitoring
- pako: Compression
- Web Workers: Parallelism
- IndexedDB: Client-side storage

### Online Tools
- WebPageTest: Load time testing
- BrowserStack: Cross-browser testing
- GTmetrix: Performance analysis

## Common Mistakes

1. **Premature Optimization**: Optimizing before profiling
2. **Micro-Optimizations**: Focusing on trivial improvements
3. **Ignoring Mobile**: Only testing on desktop
4. **Not Profiling**: Guessing at bottlenecks
5. **Over-Optimization**: Sacrificing code clarity for minor gains

## Claude Code Integration

Each optimization guide includes specific prompts for Claude Code:

```
Profile my game and identify performance bottlenecks
```

```
Optimize rendering for 60 FPS target
```

```
Implement object pooling to reduce garbage collection
```

```
Add Web Worker support for physics calculations
```

```
Optimize my game for mobile devices
```

## Success Criteria

Your game is well-optimized when:

1. Maintains target FPS on minimum spec devices
2. Loads quickly (< 3 seconds initial)
3. Memory usage is stable (no leaks)
4. No janky animations or input lag
5. Works smoothly on mobile devices
6. File size is reasonable (< 10 MB)

Performance optimization is an ongoing process. Start with the basics, measure everything, and continuously improve based on data!
