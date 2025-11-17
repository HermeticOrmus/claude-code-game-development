# Rendering Optimization

Optimizing rendering is crucial for maintaining 60 FPS in web games. This guide covers draw call reduction, texture optimization, culling, and LOD systems.

## Draw Call Reduction

### Sprite Batching

```typescript
// Bad: Individual draw calls
enemies.forEach(enemy => {
  ctx.drawImage(enemyTexture, enemy.x, enemy.y);
}); // 100 enemies = 100 draw calls

// Good: Batched rendering with sprite atlas
const batch = new SpriteBatch(ctx);
batch.begin();
enemies.forEach(enemy => {
  batch.draw(atlas, enemy.frame, enemy.x, enemy.y);
});
batch.end(); // 100 enemies = 1 draw call
```

### Texture Atlasing

```typescript
export class TextureAtlas {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private frames: Map<string, AtlasFrame> = new Map();

  constructor(width: number = 2048, height: number = 2048) {
    this.canvas = document.createElement('canvas');
    this.canvas.width = width;
    this.canvas.height = height;
    this.ctx = this.canvas.getContext('2d')!;
  }

  async addImage(name: string, url: string): Promise<void> {
    const img = await this.loadImage(url);

    // Simple packing (production: use bin packing algorithm)
    const x = (this.frames.size % 8) * 256;
    const y = Math.floor(this.frames.size / 8) * 256;

    this.ctx.drawImage(img, x, y);

    this.frames.set(name, {
      x, y,
      width: img.width,
      height: img.height
    });
  }

  getFrame(name: string): AtlasFrame | undefined {
    return this.frames.get(name);
  }

  getTexture(): HTMLCanvasElement {
    return this.canvas;
  }

  private loadImage(url: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = url;
    });
  }
}

interface AtlasFrame {
  x: number;
  y: number;
  width: number;
  height: number;
}
```

## Frustum Culling

```typescript
export class FrustumCuller {
  isVisible(
    objectX: number,
    objectY: number,
    objectWidth: number,
    objectHeight: number,
    cameraX: number,
    cameraY: number,
    viewWidth: number,
    viewHeight: number
  ): boolean {
    return (
      objectX + objectWidth > cameraX &&
      objectX < cameraX + viewWidth &&
      objectY + objectHeight > cameraY &&
      objectY < cameraY + viewHeight
    );
  }

  cullEntities<T extends { x: number; y: number; width: number; height: number }>(
    entities: T[],
    camera: { x: number; y: number; width: number; height: number }
  ): T[] {
    return entities.filter(entity =>
      this.isVisible(
        entity.x,
        entity.y,
        entity.width,
        entity.height,
        camera.x,
        camera.y,
        camera.width,
        camera.height
      )
    );
  }
}

// Usage
const culler = new FrustumCuller();
const visibleEntities = culler.cullEntities(allEntities, camera);
visibleEntities.forEach(entity => entity.render(ctx));
```

## Level of Detail (LOD)

```typescript
export class LODSystem {
  private lodLevels: LODLevel[] = [
    { distance: 0, detail: 'high' },
    { distance: 500, detail: 'medium' },
    { distance: 1000, detail: 'low' }
  ];

  getLOD(
    objectX: number,
    objectY: number,
    cameraX: number,
    cameraY: number
  ): string {
    const dx = objectX - cameraX;
    const dy = objectY - cameraY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    for (let i = this.lodLevels.length - 1; i >= 0; i--) {
      if (distance >= this.lodLevels[i].distance) {
        return this.lodLevels[i].detail;
      }
    }

    return 'high';
  }
}

interface LODLevel {
  distance: number;
  detail: string;
}
```

## Occlusion Culling

```typescript
export class OcclusionCuller {
  private occluders: Rectangle[] = [];

  addOccluder(x: number, y: number, width: number, height: number): void {
    this.occluders.push({ x, y, width, height });
  }

  isOccluded(
    objectX: number,
    objectY: number,
    objectWidth: number,
    objectHeight: number
  ): boolean {
    return this.occluders.some(occluder => {
      return this.fullyContains(occluder, {
        x: objectX,
        y: objectY,
        width: objectWidth,
        height: objectHeight
      });
    });
  }

  private fullyContains(container: Rectangle, contained: Rectangle): boolean {
    return (
      contained.x >= container.x &&
      contained.y >= container.y &&
      contained.x + contained.width <= container.x + container.width &&
      contained.y + contained.height <= container.y + container.height
    );
  }
}

interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}
```

## Claude Code Prompts

```
Optimize rendering in my game to reduce draw calls
```

```
Implement texture atlasing for my sprite system
```

```
Add frustum culling to improve rendering performance
```

```
Create LOD system for distant objects
```

## Next Steps

- Explore [Memory Management](./memory-management.md)
- Learn [Asset Loading](./asset-loading.md)
- Review [Mobile Optimization](./mobile-optimization.md)
