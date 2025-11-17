# Asset Loading Optimization

Efficient asset loading improves initial load times and enables progressive enhancement. This guide covers lazy loading, bundling, and loading strategies.

## Lazy Loading Strategies

```typescript
export class LazyAssetLoader {
  private cache: Map<string, any> = new Map();

  async loadOnDemand(assetId: string, url: string): Promise<any> {
    if (this.cache.has(assetId)) {
      return this.cache.get(assetId);
    }

    const asset = await this.load(url);
    this.cache.set(assetId, asset);
    return asset;
  }

  async preloadLevel(levelAssets: string[]): Promise<void> {
    await Promise.all(
      levelAssets.map(asset => this.loadOnDemand(asset, asset))
    );
  }

  private async load(url: string): Promise<any> {
    const response = await fetch(url);
    return response.blob();
  }
}
```

## Progressive Loading

```typescript
export class ProgressiveLoader {
  async loadWithProgress(
    assets: string[],
    onProgress: (percent: number) => void
  ): Promise<void> {
    let loaded = 0;

    for (const asset of assets) {
      await this.loadAsset(asset);
      loaded++;
      onProgress((loaded / assets.length) * 100);
    }
  }

  private loadAsset(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve();
      img.onerror = reject;
      img.src = url;
    });
  }
}
```

## Asset Bundling

```typescript
export class AssetBundle {
  async loadBundle(bundleUrl: string): Promise<Map<string, any>> {
    const response = await fetch(bundleUrl);
    const bundle = await response.json();

    const assets = new Map();
    for (const [key, data] of Object.entries(bundle)) {
      assets.set(key, data);
    }

    return assets;
  }
}
```

## CDN Integration

```typescript
export class CDNAssetLoader {
  private cdnUrl: string;

  constructor(cdnUrl: string) {
    this.cdnUrl = cdnUrl;
  }

  getAssetUrl(path: string): string {
    return `${this.cdnUrl}/${path}`;
  }

  async loadFromCDN(path: string): Promise<any> {
    const url = this.getAssetUrl(path);
    const response = await fetch(url);
    return response.blob();
  }
}
```

## Loading Screens

```typescript
export class LoadingScreen {
  private element: HTMLElement;
  private progressBar: HTMLElement;

  constructor(containerId: string) {
    this.element = document.getElementById(containerId)!;
    this.progressBar = this.element.querySelector('.progress-bar')!;
  }

  show(): void {
    this.element.style.display = 'flex';
  }

  hide(): void {
    this.element.style.display = 'none';
  }

  updateProgress(percent: number): void {
    this.progressBar.style.width = `${percent}%`;
  }
}
```

## Claude Code Prompts

```
Implement lazy loading for game assets
```

```
Create a loading screen with progress bar
```

```
Add CDN support for asset loading
```

```
Optimize asset bundle size and loading time
```

## Next Steps

- Explore [Web Worker Parallelism](./web-worker-parallelism.md)
- Learn [Mobile Optimization](./mobile-optimization.md)
- Review [Memory Management](./memory-management.md)
