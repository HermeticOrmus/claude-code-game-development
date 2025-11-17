# Save/Load Systems

Robust save and load systems are essential for game persistence, allowing players to save progress and resume gameplay. This guide covers serialization strategies, storage options, and cloud save integration.

## Table of Contents
- [Save Data Architecture](#save-data-architecture)
- [LocalStorage and IndexedDB](#localstorage-and-indexeddb)
- [Serialization Strategies](#serialization-strategies)
- [Cloud Save Integration](#cloud-save-integration)
- [Save System Implementations](#save-system-implementations)
- [Claude Code Prompts](#claude-code-prompts)

## Save Data Architecture

### Save Data Structure

```typescript
// src/save/SaveData.ts
export interface SaveData {
  version: string;
  timestamp: number;
  player: PlayerData;
  progress: ProgressData;
  settings: SettingsData;
}

export interface PlayerData {
  name: string;
  level: number;
  experience: number;
  health: number;
  maxHealth: number;
  position: { x: number; y: number; z?: number };
  inventory: InventoryItem[];
  equipment: Equipment;
  stats: PlayerStats;
}

export interface ProgressData {
  currentLevel: string;
  completedLevels: string[];
  unlockedAchievements: string[];
  questStates: Map<string, QuestState>;
  discoveredLocations: string[];
}

export interface SettingsData {
  audio: {
    masterVolume: number;
    musicVolume: number;
    sfxVolume: number;
    muted: boolean;
  };
  graphics: {
    quality: 'low' | 'medium' | 'high';
    particles: boolean;
    shadows: boolean;
  };
  controls: {
    keyBindings: Map<string, string>;
    mouseSensitivity: number;
  };
}

export interface InventoryItem {
  id: string;
  quantity: number;
  metadata?: any;
}

export interface Equipment {
  weapon?: string;
  armor?: string;
  accessory?: string;
}

export interface PlayerStats {
  strength: number;
  agility: number;
  intelligence: number;
}

export interface QuestState {
  questId: string;
  status: 'active' | 'completed' | 'failed';
  progress: number;
  objectives: Map<string, boolean>;
}
```

### Save Manager

```typescript
// src/save/SaveManager.ts
export class SaveManager {
  private static readonly SAVE_KEY = 'game-save';
  private static readonly VERSION = '1.0.0';

  private currentSave?: SaveData;

  constructor(
    private storage: IStorageProvider,
    private serializer: ISerializer
  ) {}

  async save(data: Partial<SaveData>): Promise<void> {
    const saveData: SaveData = {
      version: SaveManager.VERSION,
      timestamp: Date.now(),
      player: data.player || this.getDefaultPlayerData(),
      progress: data.progress || this.getDefaultProgressData(),
      settings: data.settings || this.getDefaultSettingsData()
    };

    this.currentSave = saveData;

    const serialized = this.serializer.serialize(saveData);
    await this.storage.save(SaveManager.SAVE_KEY, serialized);

    console.log('Game saved successfully');
  }

  async load(): Promise<SaveData | null> {
    try {
      const serialized = await this.storage.load(SaveManager.SAVE_KEY);
      if (!serialized) return null;

      const saveData = this.serializer.deserialize<SaveData>(serialized);

      // Version migration
      if (saveData.version !== SaveManager.VERSION) {
        this.migrateSave(saveData);
      }

      this.currentSave = saveData;
      return saveData;
    } catch (error) {
      console.error('Failed to load save:', error);
      return null;
    }
  }

  async deleteSave(): Promise<void> {
    await this.storage.delete(SaveManager.SAVE_KEY);
    this.currentSave = undefined;
  }

  hasSave(): Promise<boolean> {
    return this.storage.exists(SaveManager.SAVE_KEY);
  }

  getCurrentSave(): SaveData | undefined {
    return this.currentSave;
  }

  private migrateSave(saveData: SaveData): void {
    // Implement version migration logic
    console.log(`Migrating save from ${saveData.version} to ${SaveManager.VERSION}`);

    // Example migration
    if (saveData.version === '0.9.0') {
      // Add new fields with defaults
      (saveData.player as any).stats = (saveData.player as any).stats || {
        strength: 10,
        agility: 10,
        intelligence: 10
      };
    }

    saveData.version = SaveManager.VERSION;
  }

  private getDefaultPlayerData(): PlayerData {
    return {
      name: 'Player',
      level: 1,
      experience: 0,
      health: 100,
      maxHealth: 100,
      position: { x: 0, y: 0 },
      inventory: [],
      equipment: {},
      stats: { strength: 10, agility: 10, intelligence: 10 }
    };
  }

  private getDefaultProgressData(): ProgressData {
    return {
      currentLevel: 'level-1',
      completedLevels: [],
      unlockedAchievements: [],
      questStates: new Map(),
      discoveredLocations: []
    };
  }

  private getDefaultSettingsData(): SettingsData {
    return {
      audio: {
        masterVolume: 1.0,
        musicVolume: 0.8,
        sfxVolume: 1.0,
        muted: false
      },
      graphics: {
        quality: 'medium',
        particles: true,
        shadows: true
      },
      controls: {
        keyBindings: new Map([
          ['moveForward', 'KeyW'],
          ['moveBack', 'KeyS'],
          ['moveLeft', 'KeyA'],
          ['moveRight', 'KeyD'],
          ['jump', 'Space']
        ]),
        mouseSensitivity: 1.0
      }
    };
  }
}
```

## LocalStorage and IndexedDB

### LocalStorage Provider

```typescript
// src/save/LocalStorageProvider.ts
export interface IStorageProvider {
  save(key: string, data: string): Promise<void>;
  load(key: string): Promise<string | null>;
  delete(key: string): Promise<void>;
  exists(key: string): Promise<boolean>;
}

export class LocalStorageProvider implements IStorageProvider {
  async save(key: string, data: string): Promise<void> {
    try {
      localStorage.setItem(key, data);
    } catch (error) {
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        throw new Error('Storage quota exceeded');
      }
      throw error;
    }
  }

  async load(key: string): Promise<string | null> {
    return localStorage.getItem(key);
  }

  async delete(key: string): Promise<void> {
    localStorage.removeItem(key);
  }

  async exists(key: string): Promise<boolean> {
    return localStorage.getItem(key) !== null;
  }

  async getSize(): Promise<number> {
    let total = 0;
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        total += localStorage.getItem(key)!.length + key.length;
      }
    }
    return total;
  }
}
```

### IndexedDB Provider

```typescript
// src/save/IndexedDBProvider.ts
export class IndexedDBProvider implements IStorageProvider {
  private dbName: string = 'GameDatabase';
  private storeName: string = 'saves';
  private db?: IDBDatabase;

  async initialize(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName);
        }
      };
    });
  }

  async save(key: string, data: string): Promise<void> {
    if (!this.db) await this.initialize();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.put(data, key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async load(key: string): Promise<string | null> {
    if (!this.db) await this.initialize();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.get(key);

      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  }

  async delete(key: string): Promise<void> {
    if (!this.db) await this.initialize();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.delete(key);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async exists(key: string): Promise<boolean> {
    const data = await this.load(key);
    return data !== null;
  }

  async listKeys(): Promise<string[]> {
    if (!this.db) await this.initialize();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.getAllKeys();

      request.onsuccess = () => resolve(request.result as string[]);
      request.onerror = () => reject(request.error);
    });
  }
}
```

## Serialization Strategies

### JSON Serializer

```typescript
// src/save/JSONSerializer.ts
export interface ISerializer {
  serialize(data: any): string;
  deserialize<T>(data: string): T;
}

export class JSONSerializer implements ISerializer {
  serialize(data: any): string {
    return JSON.stringify(data, this.replacer);
  }

  deserialize<T>(data: string): T {
    return JSON.parse(data, this.reviver);
  }

  // Handle Map and Set serialization
  private replacer(key: string, value: any): any {
    if (value instanceof Map) {
      return {
        _type: 'Map',
        _value: Array.from(value.entries())
      };
    }
    if (value instanceof Set) {
      return {
        _type: 'Set',
        _value: Array.from(value)
      };
    }
    return value;
  }

  private reviver(key: string, value: any): any {
    if (typeof value === 'object' && value !== null) {
      if (value._type === 'Map') {
        return new Map(value._value);
      }
      if (value._type === 'Set') {
        return new Set(value._value);
      }
    }
    return value;
  }
}
```

### Compressed Serializer

```typescript
// src/save/CompressedSerializer.ts
export class CompressedSerializer implements ISerializer {
  private jsonSerializer: JSONSerializer;

  constructor() {
    this.jsonSerializer = new JSONSerializer();
  }

  serialize(data: any): string {
    const json = this.jsonSerializer.serialize(data);
    return this.compress(json);
  }

  deserialize<T>(data: string): T {
    const json = this.decompress(data);
    return this.jsonSerializer.deserialize<T>(json);
  }

  private compress(str: string): string {
    // Simple LZW compression (in production, use a library like pako)
    return btoa(encodeURIComponent(str));
  }

  private decompress(str: string): string {
    return decodeURIComponent(atob(str));
  }
}
```

### Binary Serializer

```typescript
// src/save/BinarySerializer.ts
export class BinarySerializer implements ISerializer {
  serialize(data: any): string {
    const buffer = this.encodeToBuffer(data);
    return this.bufferToBase64(buffer);
  }

  deserialize<T>(data: string): T {
    const buffer = this.base64ToBuffer(data);
    return this.decodeFromBuffer(buffer);
  }

  private encodeToBuffer(data: any): ArrayBuffer {
    // Simple implementation - in production, use MessagePack or Protocol Buffers
    const json = JSON.stringify(data);
    const encoder = new TextEncoder();
    return encoder.encode(json).buffer;
  }

  private decodeFromBuffer(buffer: ArrayBuffer): any {
    const decoder = new TextDecoder();
    const json = decoder.decode(buffer);
    return JSON.parse(json);
  }

  private bufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    const binary = Array.from(bytes, byte => String.fromCharCode(byte)).join('');
    return btoa(binary);
  }

  private base64ToBuffer(base64: string): ArrayBuffer {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }
}
```

## Cloud Save Integration

### Cloud Save Provider

```typescript
// src/save/CloudSaveProvider.ts
export class CloudSaveProvider implements IStorageProvider {
  private apiEndpoint: string;
  private authToken?: string;

  constructor(apiEndpoint: string) {
    this.apiEndpoint = apiEndpoint;
  }

  setAuthToken(token: string): void {
    this.authToken = token;
  }

  async save(key: string, data: string): Promise<void> {
    const response = await fetch(`${this.apiEndpoint}/saves/${key}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.authToken}`
      },
      body: JSON.stringify({ data })
    });

    if (!response.ok) {
      throw new Error(`Failed to save to cloud: ${response.statusText}`);
    }
  }

  async load(key: string): Promise<string | null> {
    const response = await fetch(`${this.apiEndpoint}/saves/${key}`, {
      headers: {
        'Authorization': `Bearer ${this.authToken}`
      }
    });

    if (response.status === 404) return null;
    if (!response.ok) {
      throw new Error(`Failed to load from cloud: ${response.statusText}`);
    }

    const result = await response.json();
    return result.data;
  }

  async delete(key: string): Promise<void> {
    const response = await fetch(`${this.apiEndpoint}/saves/${key}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.authToken}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to delete from cloud: ${response.statusText}`);
    }
  }

  async exists(key: string): Promise<boolean> {
    const response = await fetch(`${this.apiEndpoint}/saves/${key}`, {
      method: 'HEAD',
      headers: {
        'Authorization': `Bearer ${this.authToken}`
      }
    });

    return response.ok;
  }

  async listSaves(): Promise<string[]> {
    const response = await fetch(`${this.apiEndpoint}/saves`, {
      headers: {
        'Authorization': `Bearer ${this.authToken}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to list saves: ${response.statusText}`);
    }

    const result = await response.json();
    return result.saves;
  }
}
```

### Hybrid Save System

```typescript
// src/save/HybridSaveSystem.ts
export class HybridSaveSystem {
  private localProvider: IStorageProvider;
  private cloudProvider: CloudSaveProvider;
  private syncEnabled: boolean = false;

  constructor(
    localProvider: IStorageProvider,
    cloudProvider: CloudSaveProvider
  ) {
    this.localProvider = localProvider;
    this.cloudProvider = cloudProvider;
  }

  enableSync(authToken: string): void {
    this.cloudProvider.setAuthToken(authToken);
    this.syncEnabled = true;
  }

  disableSync(): void {
    this.syncEnabled = false;
  }

  async save(key: string, data: string): Promise<void> {
    // Always save locally
    await this.localProvider.save(key, data);

    // Optionally sync to cloud
    if (this.syncEnabled) {
      try {
        await this.cloudProvider.save(key, data);
        console.log('Synced to cloud');
      } catch (error) {
        console.warn('Failed to sync to cloud:', error);
        // Continue even if cloud save fails
      }
    }
  }

  async load(key: string): Promise<string | null> {
    if (this.syncEnabled) {
      try {
        // Try cloud first
        const cloudData = await this.cloudProvider.load(key);
        if (cloudData) {
          // Update local cache
          await this.localProvider.save(key, cloudData);
          return cloudData;
        }
      } catch (error) {
        console.warn('Failed to load from cloud, using local:', error);
      }
    }

    // Fallback to local
    return await this.localProvider.load(key);
  }

  async sync(): Promise<void> {
    if (!this.syncEnabled) {
      throw new Error('Sync not enabled');
    }

    const localKeys = await (this.localProvider as IndexedDBProvider).listKeys?.() || [];
    const cloudKeys = await this.cloudProvider.listSaves();

    // Upload local saves not in cloud
    for (const key of localKeys) {
      if (!cloudKeys.includes(key)) {
        const data = await this.localProvider.load(key);
        if (data) {
          await this.cloudProvider.save(key, data);
        }
      }
    }

    // Download cloud saves not local
    for (const key of cloudKeys) {
      if (!localKeys.includes(key)) {
        const data = await this.cloudProvider.load(key);
        if (data) {
          await this.localProvider.save(key, data);
        }
      }
    }
  }
}
```

## Save System Implementations

### Auto-Save System

```typescript
// src/save/AutoSaveSystem.ts
export class AutoSaveSystem {
  private saveManager: SaveManager;
  private intervalId?: number;
  private isDirty: boolean = false;

  constructor(
    saveManager: SaveManager,
    private autoSaveInterval: number = 60000 // 1 minute
  ) {
    this.saveManager = saveManager;
  }

  start(): void {
    this.intervalId = window.setInterval(() => {
      if (this.isDirty) {
        this.performAutoSave();
      }
    }, this.autoSaveInterval);
  }

  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }
  }

  markDirty(): void {
    this.isDirty = true;
  }

  private async performAutoSave(): Promise<void> {
    try {
      const currentSave = this.saveManager.getCurrentSave();
      if (currentSave) {
        await this.saveManager.save(currentSave);
        this.isDirty = false;
        console.log('Auto-save completed');
      }
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
  }
}
```

### Multiple Save Slots

```typescript
// src/save/SaveSlotManager.ts
export class SaveSlotManager {
  private static readonly MAX_SLOTS = 3;
  private storage: IStorageProvider;
  private serializer: ISerializer;

  constructor(storage: IStorageProvider, serializer: ISerializer) {
    this.storage = storage;
    this.serializer = serializer;
  }

  async saveToSlot(slot: number, data: SaveData): Promise<void> {
    if (slot < 0 || slot >= SaveSlotManager.MAX_SLOTS) {
      throw new Error(`Invalid save slot: ${slot}`);
    }

    const key = this.getSlotKey(slot);
    const serialized = this.serializer.serialize(data);
    await this.storage.save(key, serialized);
  }

  async loadFromSlot(slot: number): Promise<SaveData | null> {
    if (slot < 0 || slot >= SaveSlotManager.MAX_SLOTS) {
      throw new Error(`Invalid save slot: ${slot}`);
    }

    const key = this.getSlotKey(slot);
    const serialized = await this.storage.load(key);
    if (!serialized) return null;

    return this.serializer.deserialize<SaveData>(serialized);
  }

  async deleteSlot(slot: number): Promise<void> {
    const key = this.getSlotKey(slot);
    await this.storage.delete(key);
  }

  async getSlotInfo(slot: number): Promise<SaveSlotInfo | null> {
    const saveData = await this.loadFromSlot(slot);
    if (!saveData) return null;

    return {
      slot,
      playerName: saveData.player.name,
      level: saveData.player.level,
      timestamp: saveData.timestamp,
      playtime: 0 // Could track this in SaveData
    };
  }

  async listSlots(): Promise<Array<SaveSlotInfo | null>> {
    const slots: Array<SaveSlotInfo | null> = [];

    for (let i = 0; i < SaveSlotManager.MAX_SLOTS; i++) {
      slots.push(await this.getSlotInfo(i));
    }

    return slots;
  }

  private getSlotKey(slot: number): string {
    return `game-save-slot-${slot}`;
  }
}

export interface SaveSlotInfo {
  slot: number;
  playerName: string;
  level: number;
  timestamp: number;
  playtime: number;
}
```

## Claude Code Prompts

```
Create a save/load system for my game with LocalStorage and IndexedDB support
```

```
Implement cloud save synchronization for my game
```

```
Add auto-save functionality to my game
```

```
Create a save slot system with multiple save files
```

```
Implement save data versioning and migration
```

```
Add compressed save data to reduce storage size
```

## Best Practices

1. **Version Your Saves**: Always include version number for future migrations
2. **Validate Data**: Check loaded data for corruption/tampering
3. **Backup Saves**: Keep backups before overwriting
4. **Graceful Degradation**: Handle corrupted/missing saves gracefully
5. **Async Operations**: All storage operations should be async
6. **Error Handling**: Comprehensive error handling and user feedback
7. **Privacy**: Don't save sensitive data unencrypted
8. **Size Limits**: Be aware of storage quotas

## Next Steps

- Review all [Advanced Patterns](./README.md)
- Explore [Performance Optimization](../10-performance-optimization/README.md)
- Learn [Testing & QA](../11-testing-qa/README.md)
