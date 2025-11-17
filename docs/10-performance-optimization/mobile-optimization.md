# Mobile Optimization

Mobile devices have unique constraints requiring specific optimization strategies. This guide covers performance, touch input, battery efficiency, and responsive design.

## Mobile Performance Considerations

### Hardware Scaling

```typescript
export class MobileOptimizer {
  static detectDevice(): DeviceCapability {
    const gpu = this.detectGPU();
    const memory = (navigator as any).deviceMemory || 4;
    const cores = navigator.hardwareConcurrency || 2;

    if (memory >= 6 && cores >= 4 && gpu === 'high') {
      return 'high';
    } else if (memory >= 4 && cores >= 2) {
      return 'medium';
    } else {
      return 'low';
    }
  }

  static applySettings(capability: DeviceCapability): GameSettings {
    const settings: Record<DeviceCapability, GameSettings> = {
      high: {
        resolution: 1.0,
        particleCount: 1000,
        shadowQuality: 'high',
        textureQuality: 'high'
      },
      medium: {
        resolution: 0.75,
        particleCount: 500,
        shadowQuality: 'medium',
        textureQuality: 'medium'
      },
      low: {
        resolution: 0.5,
        particleCount: 200,
        shadowQuality: 'low',
        textureQuality: 'low'
      }
    };

    return settings[capability];
  }

  private static detectGPU(): 'high' | 'medium' | 'low' {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

    if (!gl) return 'low';

    const debugInfo = (gl as any).getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) {
      const renderer = (gl as any).getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);

      if (/Apple|Mali-G|Adreno [67]/i.test(renderer)) return 'high';
      if (/Adreno [45]/i.test(renderer)) return 'medium';
    }

    return 'low';
  }
}

type DeviceCapability = 'high' | 'medium' | 'low';

interface GameSettings {
  resolution: number;
  particleCount: number;
  shadowQuality: string;
  textureQuality: string;
}
```

## Touch Optimization

```typescript
export class TouchInput {
  private touches: Map<number, Touch> = new Map();

  constructor(element: HTMLElement) {
    element.addEventListener('touchstart', (e) => this.onTouchStart(e), { passive: false });
    element.addEventListener('touchmove', (e) => this.onTouchMove(e), { passive: false });
    element.addEventListener('touchend', (e) => this.onTouchEnd(e), { passive: false });
  }

  private onTouchStart(e: TouchEvent): void {
    e.preventDefault();

    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      this.touches.set(touch.identifier, touch);
    }
  }

  private onTouchMove(e: TouchEvent): void {
    e.preventDefault();

    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      this.touches.set(touch.identifier, touch);
    }
  }

  private onTouchEnd(e: TouchEvent): void {
    e.preventDefault();

    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      this.touches.delete(touch.identifier);
    }
  }

  getTouches(): Touch[] {
    return Array.from(this.touches.values());
  }

  getTouchCount(): number {
    return this.touches.size;
  }
}
```

## Battery Efficiency

```typescript
export class BatteryOptimizer {
  private targetFPS: number = 60;
  private isLowPowerMode: boolean = false;

  async initialize(): Promise<void> {
    if ('getBattery' in navigator) {
      const battery = await (navigator as any).getBattery();

      battery.addEventListener('chargingchange', () => {
        this.updatePowerMode(battery);
      });

      battery.addEventListener('levelchange', () => {
        this.updatePowerMode(battery);
      });

      this.updatePowerMode(battery);
    }
  }

  private updatePowerMode(battery: any): void {
    const isCharging = battery.charging;
    const level = battery.level;

    if (!isCharging && level < 0.2) {
      this.enterLowPowerMode();
    } else {
      this.exitLowPowerMode();
    }
  }

  private enterLowPowerMode(): void {
    this.isLowPowerMode = true;
    this.targetFPS = 30;
    console.log('Entering low power mode: 30 FPS');
  }

  private exitLowPowerMode(): void {
    this.isLowPowerMode = false;
    this.targetFPS = 60;
    console.log('Exiting low power mode: 60 FPS');
  }

  getTargetFPS(): number {
    return this.targetFPS;
  }
}
```

## Memory Constraints

```typescript
export class MobileMemoryManager {
  private memoryWarning: boolean = false;

  constructor() {
    if ((performance as any).memory) {
      setInterval(() => this.checkMemory(), 5000);
    }
  }

  private checkMemory(): void {
    const memory = (performance as any).memory;
    const used = memory.usedJSHeapSize;
    const limit = memory.jsHeapSizeLimit;
    const usage = used / limit;

    if (usage > 0.9 && !this.memoryWarning) {
      this.memoryWarning = true;
      this.handleMemoryWarning();
    } else if (usage < 0.7) {
      this.memoryWarning = false;
    }
  }

  private handleMemoryWarning(): void {
    console.warn('High memory usage detected');
    // Reduce quality, clear caches, etc.
  }
}
```

## Responsive Design

```typescript
export class ResponsiveCanvas {
  private canvas: HTMLCanvasElement;
  private baseWidth: number = 800;
  private baseHeight: number = 600;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.resize();

    window.addEventListener('resize', () => this.resize());
    window.addEventListener('orientationchange', () => this.resize());
  }

  private resize(): void {
    const container = this.canvas.parentElement!;
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;

    const aspectRatio = this.baseWidth / this.baseHeight;
    let width = containerWidth;
    let height = containerHeight;

    if (width / height > aspectRatio) {
      width = height * aspectRatio;
    } else {
      height = width / aspectRatio;
    }

    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;

    // Actual canvas resolution (can be lower for performance)
    const dpr = window.devicePixelRatio || 1;
    const scale = MobileOptimizer.detectDevice() === 'low' ? 0.5 : 1.0;

    this.canvas.width = width * dpr * scale;
    this.canvas.height = height * dpr * scale;
  }

  getScale(): number {
    return this.canvas.width / this.canvas.style.width.replace('px', '');
  }
}
```

## Testing on Mobile

```typescript
export class MobileDebugger {
  private debugElement: HTMLElement;

  constructor() {
    this.debugElement = document.createElement('div');
    this.debugElement.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 10px;
      font-family: monospace;
      font-size: 12px;
      z-index: 9999;
      pointer-events: none;
    `;
    document.body.appendChild(this.debugElement);
  }

  update(fps: number, memory: number): void {
    const info = [
      `FPS: ${fps.toFixed(1)}`,
      `Memory: ${(memory / 1048576).toFixed(1)} MB`,
      `Device: ${MobileOptimizer.detectDevice()}`,
      `Touch: ${('ontouchstart' in window) ? 'Yes' : 'No'}`,
      `Orientation: ${window.orientation || screen.orientation?.angle || 0}°`
    ];

    this.debugElement.innerHTML = info.join('<br>');
  }
}
```

## Claude Code Prompts

```
Optimize my game for mobile devices
```

```
Add touch controls for mobile gameplay
```

```
Implement battery-aware performance scaling
```

```
Create responsive canvas that adapts to device
```

```
Add mobile-specific debugging tools
```

## Best Practices

1. **Test on Real Devices**: Emulators don't accurately represent performance
2. **Optimize for Low-End**: Target budget devices, not flagships
3. **Reduce Draw Calls**: Aim for <50 draw calls per frame on mobile
4. **Lower Resolution**: Use 0.5-0.75x resolution on low-end devices
5. **Minimize Particles**: Reduce particle count significantly
6. **Touch-Friendly UI**: Large buttons (44x44px minimum)
7. **Battery Awareness**: Reduce FPS when battery is low
8. **Memory Management**: Mobile has much stricter memory limits

## Next Steps

- Review [Profiling & Debugging](./profiling-debugging.md)
- Learn [Rendering Optimization](./rendering-optimization.md)
- Explore [Memory Management](./memory-management.md)
