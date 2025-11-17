# Web Worker Parallelism

Web Workers enable parallel processing in web games by running JavaScript in background threads. This guide covers offloading computation, physics, and pathfinding.

## Web Workers for Games

### Basic Worker Setup

```typescript
// worker.ts
self.addEventListener('message', (e) => {
  const { type, data } = e.data;

  switch (type) {
    case 'calculate':
      const result = heavyCalculation(data);
      self.postMessage({ type: 'result', result });
      break;
  }
});

function heavyCalculation(data: any): any {
  // Intensive computation
  return data;
}

// main.ts
const worker = new Worker('worker.js');

worker.addEventListener('message', (e) => {
  const { type, result } = e.data;
  console.log('Worker result:', result);
});

worker.postMessage({ type: 'calculate', data: { /* ... */ } });
```

### Physics in Workers

```typescript
// physics-worker.ts
class PhysicsWorker {
  private bodies: PhysicsBody[] = [];

  constructor() {
    self.addEventListener('message', (e) => this.handleMessage(e));
  }

  private handleMessage(e: MessageEvent): void {
    const { type, data } = e.data;

    switch (type) {
      case 'init':
        this.bodies = data.bodies;
        break;
      case 'step':
        this.step(data.deltaTime);
        self.postMessage({
          type: 'update',
          bodies: this.bodies
        });
        break;
    }
  }

  private step(deltaTime: number): void {
    this.bodies.forEach(body => {
      body.x += body.vx * deltaTime;
      body.y += body.vy * deltaTime;
      body.vy += 9.8 * deltaTime;
    });
  }
}

interface PhysicsBody {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

new PhysicsWorker();
```

## Pathfinding in Workers

```typescript
// pathfinding-worker.ts
class PathfindingWorker {
  constructor() {
    self.addEventListener('message', (e) => this.handleMessage(e));
  }

  private handleMessage(e: MessageEvent): void {
    const { type, data } = e.data;

    if (type === 'findPath') {
      const path = this.findPath(data.start, data.end, data.grid);
      self.postMessage({ type: 'pathFound', path });
    }
  }

  private findPath(
    start: Point,
    end: Point,
    grid: number[][]
  ): Point[] {
    // A* pathfinding implementation
    return [];
  }
}

interface Point {
  x: number;
  y: number;
}

new PathfindingWorker();
```

## Worker Pool

```typescript
export class WorkerPool {
  private workers: Worker[] = [];
  private availableWorkers: Worker[] = [];
  private taskQueue: Task[] = [];

  constructor(workerScript: string, poolSize: number = 4) {
    for (let i = 0; i < poolSize; i++) {
      const worker = new Worker(workerScript);
      worker.addEventListener('message', (e) => this.handleWorkerMessage(worker, e));
      this.workers.push(worker);
      this.availableWorkers.push(worker);
    }
  }

  async execute<T>(task: any): Promise<T> {
    return new Promise((resolve, reject) => {
      const taskObj: Task = { task, resolve, reject };

      const worker = this.availableWorkers.pop();
      if (worker) {
        this.runTask(worker, taskObj);
      } else {
        this.taskQueue.push(taskObj);
      }
    });
  }

  private runTask(worker: Worker, taskObj: Task): void {
    (worker as any).currentTask = taskObj;
    worker.postMessage(taskObj.task);
  }

  private handleWorkerMessage(worker: Worker, e: MessageEvent): void {
    const task = (worker as any).currentTask as Task;
    if (task) {
      task.resolve(e.data);
      (worker as any).currentTask = null;
    }

    // Process next task or return to pool
    const nextTask = this.taskQueue.shift();
    if (nextTask) {
      this.runTask(worker, nextTask);
    } else {
      this.availableWorkers.push(worker);
    }
  }

  terminate(): void {
    this.workers.forEach(worker => worker.terminate());
    this.workers = [];
    this.availableWorkers = [];
  }
}

interface Task {
  task: any;
  resolve: (value: any) => void;
  reject: (reason: any) => void;
}
```

## Performance Benchmarks

```typescript
export class WorkerBenchmark {
  static async benchmarkWorkerVsMain(iterations: number): Promise<void> {
    // Main thread
    const mainStart = performance.now();
    for (let i = 0; i < iterations; i++) {
      heavyCalculation(i);
    }
    const mainTime = performance.now() - mainStart;

    // Worker thread
    const worker = new Worker('worker.js');
    const workerStart = performance.now();

    await new Promise(resolve => {
      let completed = 0;
      worker.addEventListener('message', () => {
        completed++;
        if (completed === iterations) resolve(null);
      });

      for (let i = 0; i < iterations; i++) {
        worker.postMessage({ type: 'calculate', data: i });
      }
    });

    const workerTime = performance.now() - workerStart;

    console.log(`Main thread: ${mainTime.toFixed(2)}ms`);
    console.log(`Worker thread: ${workerTime.toFixed(2)}ms`);
    console.log(`Improvement: ${((mainTime / workerTime) * 100 - 100).toFixed(1)}%`);

    worker.terminate();
  }
}

function heavyCalculation(n: number): number {
  let result = 0;
  for (let i = 0; i < 1000000; i++) {
    result += Math.sqrt(i * n);
  }
  return result;
}
```

## Claude Code Prompts

```
Implement Web Workers for physics calculations in my game
```

```
Create a worker pool for parallel processing
```

```
Offload pathfinding to Web Workers
```

```
Benchmark worker vs main thread performance
```

## Next Steps

- Explore [Mobile Optimization](./mobile-optimization.md)
- Learn [Memory Management](./memory-management.md)
- Review [Profiling & Debugging](./profiling-debugging.md)
