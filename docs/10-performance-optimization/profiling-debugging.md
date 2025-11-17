# Profiling and Debugging Performance

Effective profiling is essential for identifying and fixing performance bottlenecks. This guide covers browser DevTools, custom profiling tools, and debugging strategies.

## Table of Contents
- [Browser DevTools Profiling](#browser-devtools-profiling)
- [Performance API](#performance-api)
- [Custom Profiling Tools](#custom-profiling-tools)
- [Identifying Bottlenecks](#identifying-bottlenecks)
- [Memory Leak Detection](#memory-leak-detection)
- [Complete Profiling Examples](#complete-profiling-examples)
- [Claude Code Prompts](#claude-code-prompts)

## Browser DevTools Profiling

### Chrome DevTools Performance Tab

**Step-by-Step Profiling:**

1. Open DevTools (F12)
2. Go to Performance tab
3. Click Record (or Ctrl+E)
4. Perform actions in your game
5. Stop recording
6. Analyze the flame graph

**Reading the Flame Graph:**

```
Main Thread Timeline:
┌─────────────────────────────────────────┐
│ Frame (16.67ms budget)                  │
├─────────────────────────────────────────┤
│  Task: update()          8.2ms          │
│    ├─ physics.update()   3.1ms          │
│    ├─ ai.update()        2.8ms ⚠️       │
│    └─ render.update()    2.3ms          │
├─────────────────────────────────────────┤
│  Task: render()          6.4ms          │
│    ├─ drawCalls          4.1ms ⚠️       │
│    └─ postProcess        2.3ms          │
└─────────────────────────────────────────┘

⚠️ = Potential bottleneck (>15% of frame time)
```

**Key Metrics to Watch:**

- **Scripting (Yellow)**: JavaScript execution
- **Rendering (Purple)**: Style calculations, layout
- **Painting (Green)**: Drawing pixels
- **GPU (Green)**: GPU operations
- **Idle (White)**: Waiting time

### Memory Profiler

**Heap Snapshot:**

```typescript
// Take snapshots to find memory leaks
class MemoryProfiler {
  static takeSnapshot(label: string): void {
    if ((window as any).gc) {
      (window as any).gc(); // Force GC if available
    }

    console.log(`[Memory Snapshot: ${label}]`);

    if ((performance as any).memory) {
      const memory = (performance as any).memory;
      console.log({
        used: `${(memory.usedJSHeapSize / 1048576).toFixed(2)} MB`,
        total: `${(memory.totalJSHeapSize / 1048576).toFixed(2)} MB`,
        limit: `${(memory.jsHeapSizeLimit / 1048576).toFixed(2)} MB`
      });
    }
  }

  static async compareSnapshots(
    before: string,
    action: () => void,
    after: string
  ): Promise<void> {
    this.takeSnapshot(before);
    await new Promise(resolve => setTimeout(resolve, 100));

    action();

    await new Promise(resolve => setTimeout(resolve, 100));
    this.takeSnapshot(after);
  }
}

// Usage
MemoryProfiler.compareSnapshots(
  'Before spawning enemies',
  () => {
    for (let i = 0; i < 1000; i++) {
      spawnEnemy();
    }
  },
  'After spawning enemies'
);
```

**Allocation Timeline:**

1. Open DevTools → Memory tab
2. Select "Allocation instrumentation on timeline"
3. Start recording
4. Perform actions
5. Stop recording
6. Look for blue bars (allocations) that persist

### Network Profiler

```typescript
// Monitor asset loading performance
class NetworkProfiler {
  static logResourceTiming(): void {
    const resources = performance.getEntriesByType('resource');

    console.log('Resource Loading Performance:');
    console.log('==============================\n');

    const grouped = this.groupByType(resources as PerformanceResourceTiming[]);

    Object.entries(grouped).forEach(([type, entries]) => {
      const totalSize = entries.reduce((sum, e) => sum + (e.transferSize || 0), 0);
      const totalTime = entries.reduce((sum, e) => sum + e.duration, 0);

      console.log(`${type}:`);
      console.log(`  Count: ${entries.length}`);
      console.log(`  Size: ${(totalSize / 1024).toFixed(2)} KB`);
      console.log(`  Time: ${totalTime.toFixed(2)}ms\n`);

      if (entries.length > 0) {
        const slowest = entries.reduce((a, b) => a.duration > b.duration ? a : b);
        console.log(`  Slowest: ${slowest.name} (${slowest.duration.toFixed(2)}ms)\n`);
      }
    });
  }

  private static groupByType(
    resources: PerformanceResourceTiming[]
  ): Record<string, PerformanceResourceTiming[]> {
    const groups: Record<string, PerformanceResourceTiming[]> = {};

    resources.forEach(resource => {
      const type = this.getResourceType(resource.name);
      if (!groups[type]) groups[type] = [];
      groups[type].push(resource);
    });

    return groups;
  }

  private static getResourceType(url: string): string {
    const ext = url.split('.').pop()?.toLowerCase() || 'other';
    const types: Record<string, string> = {
      'js': 'JavaScript',
      'css': 'CSS',
      'png': 'Images',
      'jpg': 'Images',
      'jpeg': 'Images',
      'webp': 'Images',
      'mp3': 'Audio',
      'ogg': 'Audio',
      'wasm': 'WebAssembly',
      'json': 'Data'
    };
    return types[ext] || 'Other';
  }
}
```

## Performance API

### High-Resolution Timing

```typescript
export class PerformanceTimer {
  private marks: Map<string, number> = new Map();
  private measures: Map<string, number[]> = new Map();

  // Mark a point in time
  mark(name: string): void {
    performance.mark(name);
    this.marks.set(name, performance.now());
  }

  // Measure between two marks
  measure(name: string, startMark: string, endMark?: string): number {
    const start = this.marks.get(startMark);
    if (!start) {
      console.warn(`Start mark ${startMark} not found`);
      return 0;
    }

    const end = endMark ? this.marks.get(endMark) : performance.now();
    if (!end) {
      console.warn(`End mark ${endMark} not found`);
      return 0;
    }

    const duration = end - start;

    if (!this.measures.has(name)) {
      this.measures.set(name, []);
    }
    this.measures.get(name)!.push(duration);

    return duration;
  }

  // Get statistics for a measure
  getStats(name: string): { min: number; max: number; avg: number; count: number } | null {
    const values = this.measures.get(name);
    if (!values || values.length === 0) return null;

    return {
      min: Math.min(...values),
      max: Math.max(...values),
      avg: values.reduce((a, b) => a + b) / values.length,
      count: values.length
    };
  }

  // Clear all marks and measures
  clear(): void {
    this.marks.clear();
    this.measures.clear();
    performance.clearMarks();
    performance.clearMeasures();
  }

  // Report all measures
  report(): void {
    console.log('Performance Report:');
    console.log('===================\n');

    this.measures.forEach((values, name) => {
      const stats = this.getStats(name)!;
      console.log(`${name}:`);
      console.log(`  Min: ${stats.min.toFixed(2)}ms`);
      console.log(`  Max: ${stats.max.toFixed(2)}ms`);
      console.log(`  Avg: ${stats.avg.toFixed(2)}ms`);
      console.log(`  Count: ${stats.count}\n`);
    });
  }
}

// Usage
const timer = new PerformanceTimer();

function gameLoop() {
  timer.mark('frame-start');

  timer.mark('update-start');
  update();
  timer.measure('update', 'update-start');

  timer.mark('render-start');
  render();
  timer.measure('render', 'render-start');

  timer.measure('frame', 'frame-start');

  requestAnimationFrame(gameLoop);
}

// After 1000 frames
timer.report();
```

### User Timing API

```typescript
export class PerformanceMonitor {
  // Measure function execution
  static measureFunction<T>(
    name: string,
    fn: () => T
  ): T {
    const startMark = `${name}-start`;
    const endMark = `${name}-end`;

    performance.mark(startMark);
    const result = fn();
    performance.mark(endMark);

    performance.measure(name, startMark, endMark);

    const measure = performance.getEntriesByName(name, 'measure').pop();
    console.log(`${name}: ${measure?.duration.toFixed(2)}ms`);

    return result;
  }

  // Measure async function
  static async measureAsync<T>(
    name: string,
    fn: () => Promise<T>
  ): Promise<T> {
    const startMark = `${name}-start`;
    const endMark = `${name}-end`;

    performance.mark(startMark);
    const result = await fn();
    performance.mark(endMark);

    performance.measure(name, startMark, endMark);

    const measure = performance.getEntriesByName(name, 'measure').pop();
    console.log(`${name}: ${measure?.duration.toFixed(2)}ms`);

    return result;
  }

  // Get all measurements
  static getMeasurements(name?: string): PerformanceMeasure[] {
    if (name) {
      return performance.getEntriesByName(name, 'measure') as PerformanceMeasure[];
    }
    return performance.getEntriesByType('measure') as PerformanceMeasure[];
  }

  // Clear all measurements
  static clear(): void {
    performance.clearMarks();
    performance.clearMeasures();
  }
}

// Usage
PerformanceMonitor.measureFunction('collision-detection', () => {
  checkAllCollisions();
});

await PerformanceMonitor.measureAsync('asset-loading', async () => {
  await loadAssets();
});
```

## Custom Profiling Tools

### Frame Profiler

```typescript
export class FrameProfiler {
  private samples: FrameSample[] = [];
  private maxSamples: number = 300; // 5 seconds at 60fps
  private isEnabled: boolean = true;

  private frameStart: number = 0;
  private updateTime: number = 0;
  private renderTime: number = 0;

  startFrame(): void {
    if (!this.isEnabled) return;
    this.frameStart = performance.now();
  }

  endUpdate(): void {
    if (!this.isEnabled) return;
    this.updateTime = performance.now() - this.frameStart;
  }

  endRender(): void {
    if (!this.isEnabled) return;
    this.renderTime = performance.now() - this.frameStart - this.updateTime;
  }

  endFrame(): void {
    if (!this.isEnabled) return;

    const frameTime = performance.now() - this.frameStart;

    this.samples.push({
      timestamp: Date.now(),
      frameTime,
      updateTime: this.updateTime,
      renderTime: this.renderTime,
      idleTime: frameTime - this.updateTime - this.renderTime,
      fps: 1000 / frameTime
    });

    if (this.samples.length > this.maxSamples) {
      this.samples.shift();
    }

    // Log slow frames
    if (frameTime > 33.33) { // Slower than 30 FPS
      console.warn(`Slow frame: ${frameTime.toFixed(2)}ms`);
    }
  }

  getAverageStats(): FrameStats {
    if (this.samples.length === 0) {
      return this.getEmptyStats();
    }

    const avg = (arr: number[]) => arr.reduce((a, b) => a + b) / arr.length;

    return {
      avgFps: avg(this.samples.map(s => s.fps)),
      avgFrameTime: avg(this.samples.map(s => s.frameTime)),
      avgUpdateTime: avg(this.samples.map(s => s.updateTime)),
      avgRenderTime: avg(this.samples.map(s => s.renderTime)),
      minFps: Math.min(...this.samples.map(s => s.fps)),
      maxFps: Math.max(...this.samples.map(s => s.fps)),
      sampleCount: this.samples.length
    };
  }

  getPercentiles(): FramePercentiles {
    if (this.samples.length === 0) {
      return { p50: 0, p95: 0, p99: 0 };
    }

    const sorted = [...this.samples].sort((a, b) => a.frameTime - b.frameTime);
    const getPercentile = (p: number) => {
      const index = Math.floor(sorted.length * p);
      return sorted[index].frameTime;
    };

    return {
      p50: getPercentile(0.5),
      p95: getPercentile(0.95),
      p99: getPercentile(0.99)
    };
  }

  drawGraph(ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number): void {
    if (this.samples.length === 0) return;

    // Background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(x, y, width, height);

    // 60 FPS line
    const fps60Y = y + height - (16.67 / 33.33) * height;
    ctx.strokeStyle = '#00ff00';
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(x, fps60Y);
    ctx.lineTo(x + width, fps60Y);
    ctx.stroke();
    ctx.setLineDash([]);

    // 30 FPS line
    const fps30Y = y + height;
    ctx.strokeStyle = '#ff0000';
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(x, fps30Y);
    ctx.lineTo(x + width, fps30Y);
    ctx.stroke();
    ctx.setLineDash([]);

    // Frame times
    const sampleWidth = width / this.maxSamples;

    this.samples.forEach((sample, i) => {
      const sampleHeight = (sample.frameTime / 33.33) * height;
      const sampleX = x + i * sampleWidth;
      const sampleY = y + height - sampleHeight;

      ctx.fillStyle = sample.frameTime > 16.67 ? '#ff0000' : '#00ff00';
      ctx.fillRect(sampleX, sampleY, sampleWidth, sampleHeight);
    });

    // Stats text
    const stats = this.getAverageStats();
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px monospace';
    ctx.fillText(`FPS: ${stats.avgFps.toFixed(1)}`, x + 5, y + 15);
    ctx.fillText(`Frame: ${stats.avgFrameTime.toFixed(2)}ms`, x + 5, y + 30);
    ctx.fillText(`Update: ${stats.avgUpdateTime.toFixed(2)}ms`, x + 5, y + 45);
    ctx.fillText(`Render: ${stats.avgRenderTime.toFixed(2)}ms`, x + 5, y + 60);
  }

  enable(): void {
    this.isEnabled = true;
  }

  disable(): void {
    this.isEnabled = false;
  }

  clear(): void {
    this.samples = [];
  }

  private getEmptyStats(): FrameStats {
    return {
      avgFps: 0,
      avgFrameTime: 0,
      avgUpdateTime: 0,
      avgRenderTime: 0,
      minFps: 0,
      maxFps: 0,
      sampleCount: 0
    };
  }
}

interface FrameSample {
  timestamp: number;
  frameTime: number;
  updateTime: number;
  renderTime: number;
  idleTime: number;
  fps: number;
}

interface FrameStats {
  avgFps: number;
  avgFrameTime: number;
  avgUpdateTime: number;
  avgRenderTime: number;
  minFps: number;
  maxFps: number;
  sampleCount: number;
}

interface FramePercentiles {
  p50: number;
  p95: number;
  p99: number;
}
```

## Identifying Bottlenecks

### CPU Bottleneck Detection

```typescript
export class BottleneckDetector {
  static analyzeFrameTime(
    updateTime: number,
    renderTime: number,
    frameTime: number
  ): BottleneckReport {
    const targetFrameTime = 16.67; // 60 FPS
    const isSlowFrame = frameTime > targetFrameTime;

    if (!isSlowFrame) {
      return {
        bottleneck: 'none',
        severity: 'low',
        message: 'Frame running smoothly'
      };
    }

    const updatePercent = (updateTime / frameTime) * 100;
    const renderPercent = (renderTime / frameTime) * 100;

    if (updatePercent > 60) {
      return {
        bottleneck: 'cpu',
        severity: 'high',
        message: `Update taking ${updateTime.toFixed(2)}ms (${updatePercent.toFixed(1)}%). Consider optimizing game logic.`,
        suggestions: [
          'Profile update() function',
          'Optimize AI and physics calculations',
          'Use spatial partitioning for collisions',
          'Consider Web Workers for heavy computation'
        ]
      };
    }

    if (renderPercent > 60) {
      return {
        bottleneck: 'gpu',
        severity: 'high',
        message: `Render taking ${renderTime.toFixed(2)}ms (${renderPercent.toFixed(1)}%). Consider optimizing rendering.`,
        suggestions: [
          'Reduce draw calls',
          'Use texture atlases',
          'Implement frustum culling',
          'Optimize shaders'
        ]
      };
    }

    return {
      bottleneck: 'mixed',
      severity: 'medium',
      message: 'Both update and render contributing to slow frame',
      suggestions: [
        'Profile both update and render',
        'Check for blocking operations',
        'Review recent changes'
      ]
    };
  }
}

interface BottleneckReport {
  bottleneck: 'none' | 'cpu' | 'gpu' | 'mixed';
  severity: 'low' | 'medium' | 'high';
  message: string;
  suggestions?: string[];
}
```

## Memory Leak Detection

### Leak Detector

```typescript
export class MemoryLeakDetector {
  private snapshots: MemorySnapshot[] = [];

  takeSnapshot(label: string): void {
    if (!(performance as any).memory) {
      console.warn('Performance.memory not available');
      return;
    }

    const memory = (performance as any).memory;

    this.snapshots.push({
      label,
      timestamp: Date.now(),
      usedJSHeapSize: memory.usedJSHeapSize,
      totalJSHeapSize: memory.totalJSHeapSize
    });
  }

  detectLeaks(): LeakReport | null {
    if (this.snapshots.length < 3) {
      console.warn('Need at least 3 snapshots to detect leaks');
      return null;
    }

    const recent = this.snapshots.slice(-3);
    const growth = recent.map((snapshot, i) => {
      if (i === 0) return 0;
      return snapshot.usedJSHeapSize - recent[i - 1].usedJSHeapSize;
    });

    const avgGrowth = growth.slice(1).reduce((a, b) => a + b) / 2;
    const isLeaking = avgGrowth > 1048576; // Growing by >1MB

    return {
      isLeaking,
      averageGrowth: avgGrowth,
      snapshots: recent,
      message: isLeaking
        ? `Potential memory leak: ${(avgGrowth / 1048576).toFixed(2)}MB average growth`
        : 'No obvious memory leak detected'
    };
  }

  clear(): void {
    this.snapshots = [];
  }
}

interface MemorySnapshot {
  label: string;
  timestamp: number;
  usedJSHeapSize: number;
  totalJSHeapSize: number;
}

interface LeakReport {
  isLeaking: boolean;
  averageGrowth: number;
  snapshots: MemorySnapshot[];
  message: string;
}
```

## Complete Profiling Examples

### Game Profiling Session

```typescript
// Complete profiling setup
const frameProfiler = new FrameProfiler();
const perfTimer = new PerformanceTimer();
const leakDetector = new MemoryLeakDetector();

function gameLoop() {
  // Start frame profiling
  frameProfiler.startFrame();

  // Update
  perfTimer.mark('update-start');
  update(deltaTime);
  perfTimer.measure('update', 'update-start');
  frameProfiler.endUpdate();

  // Render
  perfTimer.mark('render-start');
  render();
  perfTimer.measure('render', 'render-start');
  frameProfiler.endRender();

  // End frame
  frameProfiler.endFrame();

  // Draw profiler graph
  frameProfiler.drawGraph(ctx, 10, 10, 200, 100);

  requestAnimationFrame(gameLoop);
}

// Periodic leak detection
setInterval(() => {
  leakDetector.takeSnapshot('periodic');
  const report = leakDetector.detectLeaks();
  if (report?.isLeaking) {
    console.error(report.message);
  }
}, 10000);

// Report after 60 seconds
setTimeout(() => {
  perfTimer.report();
  console.log('Frame stats:', frameProfiler.getAverageStats());
  console.log('Percentiles:', frameProfiler.getPercentiles());
}, 60000);
```

## Claude Code Prompts

```
Profile my game and identify performance bottlenecks
```

```
Create a frame profiler with visual graph display
```

```
Detect memory leaks in my game
```

```
Analyze render vs update time bottlenecks
```

```
Add performance monitoring to my game
```

```
Create automated performance regression tests
```

## Next Steps

- Explore [Rendering Optimization](./rendering-optimization.md)
- Learn [Memory Management](./memory-management.md)
- Review [Asset Loading](./asset-loading.md)
