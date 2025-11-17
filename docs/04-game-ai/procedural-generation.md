# Procedural Generation

## Introduction

Procedural generation is the algorithmic creation of game content - levels, terrain, items, characters, quests - using code rather than manual design. From the infinite worlds of Minecraft to the roguelike dungeons of The Binding of Isaac, procedural generation enables games to offer near-infinite replayability, unique player experiences, and vast game worlds that would be impossible to handcraft.

The power of procedural generation lies in controlled randomness. Pure randomness creates chaos; procedural generation uses algorithms to create content that's random enough to be unique but structured enough to be playable and interesting. A procedurally generated dungeon should feel different each time while remaining fair, navigable, and fun.

This guide covers fundamental procedural generation techniques, complete implementations of dungeon and terrain generators, noise functions for natural-looking randomness, ensuring playability, and practical examples you can integrate into your games with Claude Code.

## Random Number Generation and Seeding

Good procedural generation starts with controlled randomness. Seeded random number generators (RNGs) let you create the same "random" content from the same seed, crucial for multiplayer games and debugging.

```javascript
class SeededRandom {
    constructor(seed = Date.now()) {
        this.seed = seed;
        this.current = seed;
    }

    // Linear Congruential Generator (LCG)
    next() {
        this.current = (this.current * 1664525 + 1013904223) % 4294967296;
        return this.current / 4294967296; // Normalize to 0-1
    }

    // Random integer between min (inclusive) and max (exclusive)
    nextInt(min, max) {
        return Math.floor(this.next() * (max - min)) + min;
    }

    // Random float between min and max
    nextFloat(min, max) {
        return this.next() * (max - min) + min;
    }

    // Random element from array
    choice(array) {
        return array[this.nextInt(0, array.length)];
    }

    // Shuffle array (Fisher-Yates)
    shuffle(array) {
        const result = [...array];
        for (let i = result.length - 1; i > 0; i--) {
            const j = this.nextInt(0, i + 1);
            [result[i], result[j]] = [result[j], result[i]];
        }
        return result;
    }

    // Reset to original seed
    reset() {
        this.current = this.seed;
    }

    // Create a new RNG with a derived seed
    derive(offset) {
        return new SeededRandom(this.seed + offset);
    }
}

// Example usage
const rng = new SeededRandom(12345);
console.log(rng.next()); // Always 0.3456... for seed 12345
console.log(rng.nextInt(1, 7)); // Dice roll: 1-6

// Create same dungeon from same seed
const dungeonSeed = 42;
const dungeon1 = generateDungeon(dungeonSeed);
const dungeon2 = generateDungeon(dungeonSeed);
// dungeon1 and dungeon2 are identical
```

## Perlin Noise and Simplex Noise

Noise functions create natural-looking randomness - perfect for terrain, clouds, and textures. Unlike pure randomness, noise is smooth and continuous.

```javascript
class PerlinNoise {
    constructor(seed = 0) {
        this.permutation = this.buildPermutationTable(seed);
    }

    buildPermutationTable(seed) {
        const rng = new SeededRandom(seed);
        const p = [];

        // Fill with values 0-255
        for (let i = 0; i < 256; i++) {
            p[i] = i;
        }

        // Shuffle
        for (let i = 255; i > 0; i--) {
            const j = rng.nextInt(0, i + 1);
            [p[i], p[j]] = [p[j], p[i]];
        }

        // Duplicate for easy wrapping
        return [...p, ...p];
    }

    fade(t) {
        // 6t^5 - 15t^4 + 10t^3
        return t * t * t * (t * (t * 6 - 15) + 10);
    }

    lerp(a, b, t) {
        return a + t * (b - a);
    }

    grad(hash, x, y) {
        // Convert low 2 bits of hash into gradient direction
        const h = hash & 3;
        const u = h < 2 ? x : y;
        const v = h < 2 ? y : x;
        return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v);
    }

    noise(x, y) {
        // Find unit square containing point
        const X = Math.floor(x) & 255;
        const Y = Math.floor(y) & 255;

        // Find relative position in square
        x -= Math.floor(x);
        y -= Math.floor(y);

        // Compute fade curves
        const u = this.fade(x);
        const v = this.fade(y);

        // Hash coordinates of square corners
        const p = this.permutation;
        const a = p[X] + Y;
        const b = p[X + 1] + Y;

        // Blend results from corners
        return this.lerp(
            this.lerp(
                this.grad(p[a], x, y),
                this.grad(p[b], x - 1, y),
                u
            ),
            this.lerp(
                this.grad(p[a + 1], x, y - 1),
                this.grad(p[b + 1], x - 1, y - 1),
                u
            ),
            v
        );
    }

    // Octave noise - layer multiple frequencies for detail
    octaveNoise(x, y, octaves = 4, persistence = 0.5) {
        let total = 0;
        let frequency = 1;
        let amplitude = 1;
        let maxValue = 0;

        for (let i = 0; i < octaves; i++) {
            total += this.noise(x * frequency, y * frequency) * amplitude;
            maxValue += amplitude;
            amplitude *= persistence;
            frequency *= 2;
        }

        return total / maxValue; // Normalize to -1 to 1
    }

    // Generate 2D noise map
    generateNoiseMap(width, height, scale = 50, octaves = 4) {
        const map = [];

        for (let y = 0; y < height; y++) {
            map[y] = [];
            for (let x = 0; x < width; x++) {
                const noise = this.octaveNoise(x / scale, y / scale, octaves);
                map[y][x] = (noise + 1) / 2; // Normalize to 0-1
            }
        }

        return map;
    }
}

// Visualize noise
function visualizeNoise(canvas, noiseMap) {
    const ctx = canvas.getContext('2d');
    const width = noiseMap[0].length;
    const height = noiseMap.length;

    canvas.width = width;
    canvas.height = height;

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const value = Math.floor(noiseMap[y][x] * 255);
            ctx.fillStyle = `rgb(${value}, ${value}, ${value})`;
            ctx.fillRect(x, y, 1, 1);
        }
    }
}

// Example: Terrain from noise
const noise = new PerlinNoise(42);
const terrainMap = noise.generateNoiseMap(200, 200, 30, 4);
```

## Dungeon Generation: Binary Space Partitioning (BSP)

BSP creates dungeons by recursively splitting space into rooms and connecting them with corridors.

```javascript
class BSPDungeonGenerator {
    constructor(width, height, seed = Date.now()) {
        this.width = width;
        this.height = height;
        this.rng = new SeededRandom(seed);
        this.dungeon = this.createEmptyDungeon();
        this.rooms = [];
    }

    createEmptyDungeon() {
        const dungeon = [];
        for (let y = 0; y < this.height; y++) {
            dungeon[y] = [];
            for (let x = 0; x < this.width; x++) {
                dungeon[y][x] = 1; // 1 = wall, 0 = floor
            }
        }
        return dungeon;
    }

    generate(minRoomSize = 6, maxRoomSize = 12) {
        // Create initial container
        const root = {
            x: 1,
            y: 1,
            width: this.width - 2,
            height: this.height - 2,
            left: null,
            right: null,
            room: null
        };

        // Split recursively
        this.split(root, minRoomSize);

        // Create rooms in leaf nodes
        this.createRooms(root, minRoomSize, maxRoomSize);

        // Connect rooms with corridors
        this.connectRooms(root);

        return {
            dungeon: this.dungeon,
            rooms: this.rooms
        };
    }

    split(node, minSize) {
        // Stop splitting if too small
        if (node.width < minSize * 2 || node.height < minSize * 2) {
            return;
        }

        // Randomly choose horizontal or vertical split
        const splitH = this.rng.next() > 0.5;

        if (splitH) {
            // Horizontal split
            const splitPos = this.rng.nextInt(
                minSize,
                node.height - minSize
            );

            node.left = {
                x: node.x,
                y: node.y,
                width: node.width,
                height: splitPos,
                left: null,
                right: null,
                room: null
            };

            node.right = {
                x: node.x,
                y: node.y + splitPos,
                width: node.width,
                height: node.height - splitPos,
                left: null,
                right: null,
                room: null
            };
        } else {
            // Vertical split
            const splitPos = this.rng.nextInt(
                minSize,
                node.width - minSize
            );

            node.left = {
                x: node.x,
                y: node.y,
                width: splitPos,
                height: node.height,
                left: null,
                right: null,
                room: null
            };

            node.right = {
                x: node.x + splitPos,
                y: node.y,
                width: node.width - splitPos,
                height: node.height,
                left: null,
                right: null,
                room: null
            };
        }

        // Recursively split children
        this.split(node.left, minSize);
        this.split(node.right, minSize);
    }

    createRooms(node, minSize, maxSize) {
        if (node.left || node.right) {
            // Not a leaf, recurse
            if (node.left) this.createRooms(node.left, minSize, maxSize);
            if (node.right) this.createRooms(node.right, minSize, maxSize);
        } else {
            // Leaf node - create room
            const roomWidth = this.rng.nextInt(minSize, Math.min(maxSize, node.width - 1));
            const roomHeight = this.rng.nextInt(minSize, Math.min(maxSize, node.height - 1));

            const roomX = node.x + this.rng.nextInt(0, node.width - roomWidth);
            const roomY = node.y + this.rng.nextInt(0, node.height - roomHeight);

            node.room = {
                x: roomX,
                y: roomY,
                width: roomWidth,
                height: roomHeight,
                centerX: Math.floor(roomX + roomWidth / 2),
                centerY: Math.floor(roomY + roomHeight / 2)
            };

            this.rooms.push(node.room);

            // Carve out room
            for (let y = roomY; y < roomY + roomHeight; y++) {
                for (let x = roomX; x < roomX + roomWidth; x++) {
                    this.dungeon[y][x] = 0; // Floor
                }
            }
        }
    }

    connectRooms(node) {
        if (!node.left && !node.right) {
            // Leaf node, no connections needed
            return;
        }

        // Recursively connect children first
        if (node.left) this.connectRooms(node.left);
        if (node.right) this.connectRooms(node.right);

        // Connect left and right subtrees
        if (node.left && node.right) {
            const leftRoom = this.getRandomRoom(node.left);
            const rightRoom = this.getRandomRoom(node.right);

            if (leftRoom && rightRoom) {
                this.createCorridor(
                    leftRoom.centerX, leftRoom.centerY,
                    rightRoom.centerX, rightRoom.centerY
                );
            }
        }
    }

    getRandomRoom(node) {
        if (node.room) {
            return node.room;
        }

        if (node.left && node.right) {
            return this.rng.next() > 0.5 ?
                this.getRandomRoom(node.left) :
                this.getRandomRoom(node.right);
        }

        if (node.left) return this.getRandomRoom(node.left);
        if (node.right) return this.getRandomRoom(node.right);

        return null;
    }

    createCorridor(x1, y1, x2, y2) {
        // L-shaped corridor
        if (this.rng.next() > 0.5) {
            // Horizontal then vertical
            this.carveLine(x1, y1, x2, y1); // Horizontal
            this.carveLine(x2, y1, x2, y2); // Vertical
        } else {
            // Vertical then horizontal
            this.carveLine(x1, y1, x1, y2); // Vertical
            this.carveLine(x1, y2, x2, y2); // Horizontal
        }
    }

    carveLine(x1, y1, x2, y2) {
        const dx = Math.sign(x2 - x1);
        const dy = Math.sign(y2 - y1);

        let x = x1;
        let y = y1;

        while (x !== x2 || y !== y2) {
            if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
                this.dungeon[y][x] = 0; // Floor
            }

            if (x !== x2) x += dx;
            else if (y !== y2) y += dy;
        }
    }

    visualize(canvas) {
        const ctx = canvas.getContext('2d');
        const cellSize = 4;

        canvas.width = this.width * cellSize;
        canvas.height = this.height * cellSize;

        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                ctx.fillStyle = this.dungeon[y][x] === 0 ? '#ddd' : '#222';
                ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }

        // Draw room centers
        ctx.fillStyle = 'red';
        for (const room of this.rooms) {
            ctx.fillRect(
                room.centerX * cellSize,
                room.centerY * cellSize,
                cellSize,
                cellSize
            );
        }
    }
}

// Generate dungeon
const generator = new BSPDungeonGenerator(80, 60, 42);
const result = generator.generate(6, 12);
console.log(`Generated dungeon with ${result.rooms.length} rooms`);
```

## Dungeon Generation: Cellular Automata

Cellular automata creates organic-looking caves by applying simple rules repeatedly.

```javascript
class CellularAutomataCave {
    constructor(width, height, seed = Date.now()) {
        this.width = width;
        this.height = height;
        this.rng = new SeededRandom(seed);
        this.map = this.createEmptyMap();
    }

    createEmptyMap() {
        const map = [];
        for (let y = 0; y < this.height; y++) {
            map[y] = [];
            for (let x = 0; x < this.width; x++) {
                map[y][x] = 0;
            }
        }
        return map;
    }

    generate(fillProbability = 0.45, iterations = 5) {
        // Initialize with random walls
        this.randomFill(fillProbability);

        // Apply cellular automata rules
        for (let i = 0; i < iterations; i++) {
            this.smooth();
        }

        // Clean up isolated regions
        this.removeIsolatedRegions();

        return this.map;
    }

    randomFill(probability) {
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                // Border is always wall
                if (x === 0 || x === this.width - 1 || y === 0 || y === this.height - 1) {
                    this.map[y][x] = 1;
                } else {
                    this.map[y][x] = this.rng.next() < probability ? 1 : 0;
                }
            }
        }
    }

    smooth() {
        const newMap = this.createEmptyMap();

        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                const wallCount = this.countWallsAround(x, y);

                // Cellular automata rule: if 5+ neighbors are walls, become wall
                if (wallCount > 4) {
                    newMap[y][x] = 1;
                } else if (wallCount < 4) {
                    newMap[y][x] = 0;
                } else {
                    newMap[y][x] = this.map[y][x];
                }
            }
        }

        this.map = newMap;
    }

    countWallsAround(x, y, range = 1) {
        let count = 0;

        for (let dy = -range; dy <= range; dy++) {
            for (let dx = -range; dx <= range; dx++) {
                if (dx === 0 && dy === 0) continue;

                const nx = x + dx;
                const ny = y + dy;

                // Out of bounds counts as wall
                if (nx < 0 || nx >= this.width || ny < 0 || ny >= this.height) {
                    count++;
                } else if (this.map[ny][nx] === 1) {
                    count++;
                }
            }
        }

        return count;
    }

    removeIsolatedRegions() {
        // Find all floor regions using flood fill
        const visited = Array(this.height).fill(null).map(() => Array(this.width).fill(false));
        const regions = [];

        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                if (this.map[y][x] === 0 && !visited[y][x]) {
                    const region = this.floodFill(x, y, visited);
                    regions.push(region);
                }
            }
        }

        // Keep only the largest region
        if (regions.length > 0) {
            regions.sort((a, b) => b.length - a.length);
            const largestRegion = new Set(regions[0].map(p => `${p.x},${p.y}`));

            // Fill in small regions
            for (let y = 0; y < this.height; y++) {
                for (let x = 0; x < this.width; x++) {
                    if (this.map[y][x] === 0 && !largestRegion.has(`${x},${y}`)) {
                        this.map[y][x] = 1; // Convert to wall
                    }
                }
            }
        }
    }

    floodFill(startX, startY, visited) {
        const region = [];
        const queue = [{x: startX, y: startY}];
        visited[startY][startX] = true;

        while (queue.length > 0) {
            const {x, y} = queue.shift();
            region.push({x, y});

            // Check 4 neighbors
            const neighbors = [
                {x: x + 1, y},
                {x: x - 1, y},
                {x, y: y + 1},
                {x, y: y - 1}
            ];

            for (const {x: nx, y: ny} of neighbors) {
                if (nx >= 0 && nx < this.width && ny >= 0 && ny < this.height &&
                    !visited[ny][nx] && this.map[ny][nx] === 0) {

                    visited[ny][nx] = true;
                    queue.push({x: nx, y: ny});
                }
            }
        }

        return region;
    }

    visualize(canvas) {
        const ctx = canvas.getContext('2d');
        const cellSize = 4;

        canvas.width = this.width * cellSize;
        canvas.height = this.height * cellSize;

        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                ctx.fillStyle = this.map[y][x] === 0 ? '#8b7355' : '#2a2a2a';
                ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }
    }
}

// Generate cave
const cave = new CellularAutomataCave(100, 80, 123);
const caveMap = cave.generate(0.45, 5);
```

## Terrain Generation: Heightmaps

Use noise functions to create realistic terrain:

```javascript
class TerrainGenerator {
    constructor(width, height, seed = Date.now()) {
        this.width = width;
        this.height = height;
        this.noise = new PerlinNoise(seed);
    }

    generateHeightmap(scale = 50, octaves = 6, persistence = 0.5) {
        const heightmap = [];

        for (let y = 0; y < this.height; y++) {
            heightmap[y] = [];
            for (let x = 0; x < this.width; x++) {
                const height = this.noise.octaveNoise(
                    x / scale,
                    y / scale,
                    octaves,
                    persistence
                );
                heightmap[y][x] = (height + 1) / 2; // Normalize to 0-1
            }
        }

        return heightmap;
    }

    generateTilemap(heightmap, waterLevel = 0.3, mountainLevel = 0.7) {
        const tilemap = [];

        for (let y = 0; y < this.height; y++) {
            tilemap[y] = [];
            for (let x = 0; x < this.width; x++) {
                const height = heightmap[y][x];

                let tile;
                if (height < waterLevel) {
                    tile = 'WATER';
                } else if (height < waterLevel + 0.05) {
                    tile = 'SAND';
                } else if (height < mountainLevel - 0.1) {
                    tile = 'GRASS';
                } else if (height < mountainLevel) {
                    tile = 'DIRT';
                } else if (height < mountainLevel + 0.1) {
                    tile = 'ROCK';
                } else {
                    tile = 'SNOW';
                }

                tilemap[y][x] = tile;
            }
        }

        return tilemap;
    }

    addFeatures(tilemap, heightmap, seed) {
        // Add trees to grass areas
        const rng = new SeededRandom(seed + 1);

        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                if (tilemap[y][x] === 'GRASS') {
                    // Random tree placement with noise influence
                    const treeNoise = this.noise.noise(x / 10, y / 10);
                    if (rng.next() < 0.05 && treeNoise > 0.2) {
                        tilemap[y][x] = 'TREE';
                    }
                }
            }
        }

        return tilemap;
    }

    visualize(canvas, tilemap) {
        const ctx = canvas.getContext('2d');
        const cellSize = 4;

        canvas.width = this.width * cellSize;
        canvas.height = this.height * cellSize;

        const colors = {
            'WATER': '#1e90ff',
            'SAND': '#f4a460',
            'GRASS': '#228b22',
            'DIRT': '#8b7355',
            'ROCK': '#696969',
            'SNOW': '#ffffff',
            'TREE': '#006400'
        };

        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                ctx.fillStyle = colors[tilemap[y][x]] || '#000';
                ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }
    }
}

// Generate terrain
const terrain = new TerrainGenerator(200, 150, 999);
const heightmap = terrain.generateHeightmap(40, 6, 0.5);
const tilemap = terrain.generateTilemap(heightmap, 0.35, 0.65);
const tilemapWithFeatures = terrain.addFeatures(tilemap, heightmap, 999);
```

## Procedural Level Generation: Platformer

Generate platformer levels with platforms, gaps, and enemies:

```javascript
class PlatformerLevelGenerator {
    constructor(width, height, seed = Date.now()) {
        this.width = width;
        this.height = height;
        this.rng = new SeededRandom(seed);
        this.level = {
            platforms: [],
            enemies: [],
            items: [],
            start: {x: 0, y: 0},
            end: {x: 0, y: 0}
        };
    }

    generate(difficulty = 1) {
        const segmentWidth = 100;
        const numSegments = Math.floor(this.width / segmentWidth);

        let currentY = this.height * 0.7;
        let currentX = 50;

        // Starting platform
        this.level.platforms.push({
            x: 0,
            y: currentY,
            width: 100,
            height: 20
        });

        this.level.start = {x: 50, y: currentY - 50};

        // Generate segments
        for (let i = 0; i < numSegments; i++) {
            const segment = this.generateSegment(
                currentX,
                currentY,
                segmentWidth,
                difficulty
            );

            this.level.platforms.push(...segment.platforms);
            this.level.enemies.push(...segment.enemies);
            this.level.items.push(...segment.items);

            currentX += segmentWidth;
            currentY = segment.endY;
        }

        // Ending platform
        this.level.platforms.push({
            x: currentX,
            y: currentY,
            width: 150,
            height: 20
        });

        this.level.end = {x: currentX + 75, y: currentY - 50};

        return this.level;
    }

    generateSegment(startX, startY, width, difficulty) {
        const segment = {
            platforms: [],
            enemies: [],
            items: [],
            endY: startY
        };

        const patterns = [
            'straight',
            'ascending',
            'descending',
            'gap',
            'staircase'
        ];

        const pattern = this.rng.choice(patterns);

        switch (pattern) {
            case 'straight':
                segment.platforms.push({
                    x: startX,
                    y: startY,
                    width: width,
                    height: 20
                });

                // Add enemy if difficulty allows
                if (difficulty >= 0.3 && this.rng.next() < 0.5) {
                    segment.enemies.push({
                        x: startX + width / 2,
                        y: startY - 30,
                        type: 'walker'
                    });
                }

                segment.endY = startY;
                break;

            case 'ascending':
                const steps = 3;
                const stepHeight = 40;
                for (let i = 0; i < steps; i++) {
                    const platformY = startY - i * stepHeight;
                    segment.platforms.push({
                        x: startX + i * (width / steps),
                        y: platformY,
                        width: width / steps + 10,
                        height: 20
                    });
                }
                segment.endY = startY - (steps - 1) * stepHeight;
                break;

            case 'descending':
                const descSteps = 3;
                const descHeight = 40;
                for (let i = 0; i < descSteps; i++) {
                    const platformY = startY + i * descHeight;
                    segment.platforms.push({
                        x: startX + i * (width / descSteps),
                        y: platformY,
                        width: width / descSteps + 10,
                        height: 20
                    });
                }
                segment.endY = startY + (descSteps - 1) * descHeight;
                break;

            case 'gap':
                const gapSize = this.rng.nextInt(60, 120);
                segment.platforms.push({
                    x: startX,
                    y: startY,
                    width: (width - gapSize) / 2,
                    height: 20
                });
                segment.platforms.push({
                    x: startX + (width + gapSize) / 2,
                    y: startY,
                    width: (width - gapSize) / 2,
                    height: 20
                });

                // Coin over gap
                segment.items.push({
                    x: startX + width / 2,
                    y: startY - 100,
                    type: 'coin'
                });

                segment.endY = startY;
                break;

            case 'staircase':
                const stairs = 4;
                for (let i = 0; i < stairs; i++) {
                    segment.platforms.push({
                        x: startX + i * (width / stairs),
                        y: startY - i * 30,
                        width: width / stairs + 10,
                        height: 20
                    });
                }
                segment.endY = startY - (stairs - 1) * 30;
                break;
        }

        return segment;
    }

    visualize(canvas) {
        const ctx = canvas.getContext('2d');
        canvas.width = this.width;
        canvas.height = this.height;

        // Background
        ctx.fillStyle = '#87CEEB';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Platforms
        ctx.fillStyle = '#8B4513';
        for (const platform of this.level.platforms) {
            ctx.fillRect(platform.x, platform.y, platform.width, platform.height);
        }

        // Start point
        ctx.fillStyle = 'green';
        ctx.beginPath();
        ctx.arc(this.level.start.x, this.level.start.y, 15, 0, Math.PI * 2);
        ctx.fill();

        // End point
        ctx.fillStyle = 'gold';
        ctx.beginPath();
        ctx.arc(this.level.end.x, this.level.end.y, 20, 0, Math.PI * 2);
        ctx.fill();

        // Enemies
        ctx.fillStyle = 'red';
        for (const enemy of this.level.enemies) {
            ctx.beginPath();
            ctx.arc(enemy.x, enemy.y, 10, 0, Math.PI * 2);
            ctx.fill();
        }

        // Items
        ctx.fillStyle = 'yellow';
        for (const item of this.level.items) {
            ctx.beginPath();
            ctx.arc(item.x, item.y, 8, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}

// Generate level
const platformerGen = new PlatformerLevelGenerator(2000, 600, 777);
const level = platformerGen.generate(0.5);
```

## Ensuring Playability

Procedural content must be playable. Key techniques:

```javascript
class PlayabilityValidator {
    // Check if dungeon has a path from start to end
    static isDungeonPlayable(dungeon, startX, startY, endX, endY) {
        const visited = new Set();
        const queue = [{x: startX, y: startY}];
        visited.add(`${startX},${startY}`);

        while (queue.length > 0) {
            const {x, y} = queue.shift();

            if (x === endX && y === endY) {
                return true; // Path exists!
            }

            // Check 4 neighbors
            const neighbors = [
                {x: x + 1, y},
                {x: x - 1, y},
                {x, y: y + 1},
                {x, y: y - 1}
            ];

            for (const {x: nx, y: ny} of neighbors) {
                const key = `${nx},${ny}`;

                if (nx >= 0 && nx < dungeon[0].length &&
                    ny >= 0 && ny < dungeon.length &&
                    dungeon[ny][nx] === 0 && // Floor
                    !visited.has(key)) {

                    visited.add(key);
                    queue.push({x: nx, y: ny});
                }
            }
        }

        return false; // No path found
    }

    // Ensure platformer level is beatable
    static isPlatformerLevelBeatable(level, maxJumpHeight = 120, maxJumpDistance = 150) {
        const platforms = level.platforms.sort((a, b) => a.x - b.x);

        for (let i = 0; i < platforms.length - 1; i++) {
            const current = platforms[i];
            const next = platforms[i + 1];

            // Check horizontal distance
            const horizontalGap = next.x - (current.x + current.width);
            if (horizontalGap > maxJumpDistance) {
                console.warn(`Gap too wide at x=${current.x}`);
                return false;
            }

            // Check vertical distance
            const verticalGap = Math.abs(next.y - current.y);
            if (next.y < current.y && verticalGap > maxJumpHeight) {
                console.warn(`Platform too high at x=${next.x}`);
                return false;
            }
        }

        return true;
    }

    // Add difficulty rating to generated content
    static rateDifficulty(level) {
        let score = 0;

        // Count gaps
        const platforms = level.platforms.sort((a, b) => a.x - b.x);
        for (let i = 0; i < platforms.length - 1; i++) {
            const current = platforms[i];
            const next = platforms[i + 1];
            const gap = next.x - (current.x + current.width);

            if (gap > 20) score += 1;
            if (gap > 80) score += 2;
        }

        // Count enemies
        score += level.enemies.length * 2;

        // Difficulty rating
        if (score < 5) return 'easy';
        if (score < 15) return 'medium';
        return 'hard';
    }
}

// Validate generated content
const isPlayable = PlayabilityValidator.isDungeonPlayable(
    result.dungeon,
    result.rooms[0].centerX,
    result.rooms[0].centerY,
    result.rooms[result.rooms.length - 1].centerX,
    result.rooms[result.rooms.length - 1].centerY
);

console.log(`Dungeon is playable: ${isPlayable}`);

const canBeat = PlayabilityValidator.isPlatformerLevelBeatable(level);
const difficulty = PlayabilityValidator.rateDifficulty(level);
console.log(`Level beatable: ${canBeat}, Difficulty: ${difficulty}`);
```

## Claude Code Prompts for Procedural Generation

**Dungeon Generation:**
```
"Create a procedural dungeon generator using BSP that creates 5-8 rooms connected by corridors with guaranteed path from start to end"
```

**Terrain Generation:**
```
"Generate a 2D terrain map using Perlin noise with distinct biomes (water, grass, desert, mountains) and smooth transitions between them"
```

**Level Validation:**
```
"Add playability validation to this platformer generator to ensure all platforms are reachable and no gaps are too wide to jump"
```

**Seeded Generation:**
```
"Implement a seeded random number generator so the same seed always produces the same dungeon layout for multiplayer consistency"
```

**Cave Generation:**
```
"Create organic-looking caves using cellular automata with 4-5 smoothing iterations and removal of isolated regions"
```

## Performance Considerations

Procedural generation can be expensive:

- **Generate Once**: Create content during loading, not every frame
- **Chunking**: Generate world in chunks as player explores (like Minecraft)
- **Web Workers**: Offload generation to background threads
- **Caching**: Store generated seeds and reuse results
- **Progressive Generation**: Spread generation across multiple frames

```javascript
// Example: Chunked generation
class ChunkedWorldGenerator {
    constructor(chunkSize = 32, seed = Date.now()) {
        this.chunkSize = chunkSize;
        this.seed = seed;
        this.chunks = new Map();
        this.noise = new PerlinNoise(seed);
    }

    getChunk(chunkX, chunkY) {
        const key = `${chunkX},${chunkY}`;

        if (this.chunks.has(key)) {
            return this.chunks.get(key);
        }

        // Generate chunk
        const chunk = this.generateChunk(chunkX, chunkY);
        this.chunks.set(key, chunk);

        return chunk;
    }

    generateChunk(chunkX, chunkY) {
        const chunk = [];
        const offsetX = chunkX * this.chunkSize;
        const offsetY = chunkY * this.chunkSize;

        for (let y = 0; y < this.chunkSize; y++) {
            chunk[y] = [];
            for (let x = 0; x < this.chunkSize; x++) {
                const worldX = offsetX + x;
                const worldY = offsetY + y;

                const height = this.noise.octaveNoise(worldX / 30, worldY / 30, 4);
                chunk[y][x] = height > 0.2 ? 'GRASS' : 'WATER';
            }
        }

        return chunk;
    }

    unloadChunk(chunkX, chunkY) {
        const key = `${chunkX},${chunkY}`;
        this.chunks.delete(key);
    }
}
```

## Related Documentation

- [Pathfinding Algorithms](./pathfinding-algorithms.md) - Navigate generated levels
- [NPC Behaviors](./npc-behaviors.md) - Populate generated worlds with AI
- [State Management](../02-core-game-concepts/state-management.md) - Manage generated content

Procedural generation unlocks infinite possibilities in your games. Whether you're creating roguelikes with unique dungeons, open worlds with endless terrain, or platformers with fresh levels, these techniques will help you build systems that keep players engaged through constant novelty!
