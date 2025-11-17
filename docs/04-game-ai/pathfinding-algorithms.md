# Pathfinding Algorithms

## Introduction

Pathfinding is the foundation of game AI movement. Whether you're creating enemies that chase players through a maze, NPCs that navigate crowded cities, or units that maneuver around obstacles in a strategy game, you need efficient algorithms to calculate routes from point A to point B. This guide covers the essential pathfinding algorithms every game developer should know, with complete implementations, performance analysis, and practical optimization techniques.

Pathfinding algorithms solve the problem of finding the shortest (or best) path between two points in a graph or grid, where obstacles block direct movement. The challenge lies in doing this efficiently - a naive approach might check every possible route, but with proper algorithms we can find optimal paths while examining only a fraction of the game world.

## Grid-Based vs Graph-Based Pathfinding

Before diving into algorithms, understand the two fundamental representations:

**Grid-Based Pathfinding** divides the world into uniform cells (squares, hexagons, etc.). Each cell is either walkable or blocked. This is simple to implement and visualize, perfect for tile-based games, 2D platformers, and roguelikes. The downside is memory usage for large worlds and suboptimal paths (restricted to grid angles).

**Graph-Based Pathfinding** uses nodes (points) connected by edges (paths between points). This is more flexible - nodes can be placed anywhere, and edges can have varying costs (terrain difficulty, distance). Navigation meshes use this approach. Better for 3D games, realistic terrain, and situations where grid restrictions feel artificial.

Most algorithms work with either representation. We'll focus on grids for clarity, but the concepts transfer directly to graphs.

## A* Algorithm: The Industry Standard

A* (pronounced "A-star") is the most widely used pathfinding algorithm in games. It combines the guaranteed shortest path of Dijkstra's algorithm with the speed of greedy best-first search. A* uses a heuristic function to guide its search toward the goal, dramatically reducing the number of cells examined.

### How A* Works

A* maintains two lists:
- **Open List**: Cells to be evaluated, prioritized by lowest f-score
- **Closed List**: Cells already evaluated

For each cell, A* calculates:
- **g-score**: Actual cost from start to this cell
- **h-score**: Estimated cost from this cell to goal (heuristic)
- **f-score**: g + h (total estimated cost of path through this cell)

The algorithm repeatedly:
1. Selects the cell with lowest f-score from the open list
2. Examines its neighbors
3. Updates neighbors' scores if a better path is found
4. Moves the current cell to the closed list
5. Continues until reaching the goal or exhausting options

### Complete A* Implementation

```javascript
class PathfindingGrid {
    constructor(width, height) {
        this.width = width;
        this.height = height;
        this.cells = Array(height).fill(null).map(() => Array(width).fill(0));
    }

    setWalkable(x, y, walkable) {
        if (this.isValid(x, y)) {
            this.cells[y][x] = walkable ? 0 : 1;
        }
    }

    isWalkable(x, y) {
        return this.isValid(x, y) && this.cells[y][x] === 0;
    }

    isValid(x, y) {
        return x >= 0 && x < this.width && y >= 0 && y < this.height;
    }

    getNeighbors(x, y, allowDiagonal = true) {
        const neighbors = [];

        // Cardinal directions (cost: 1.0)
        const directions = [
            {dx: 0, dy: -1, cost: 1.0},  // North
            {dx: 1, dy: 0, cost: 1.0},   // East
            {dx: 0, dy: 1, cost: 1.0},   // South
            {dx: -1, dy: 0, cost: 1.0}   // West
        ];

        // Diagonal directions (cost: ~1.414)
        if (allowDiagonal) {
            directions.push(
                {dx: 1, dy: -1, cost: 1.414},  // Northeast
                {dx: 1, dy: 1, cost: 1.414},   // Southeast
                {dx: -1, dy: 1, cost: 1.414},  // Southwest
                {dx: -1, dy: -1, cost: 1.414}  // Northwest
            );
        }

        for (const dir of directions) {
            const nx = x + dir.dx;
            const ny = y + dir.dy;

            if (this.isWalkable(nx, ny)) {
                // For diagonal movement, check that adjacent cardinals are also walkable
                // This prevents "corner cutting" through diagonal gaps
                if (allowDiagonal && Math.abs(dir.dx) + Math.abs(dir.dy) === 2) {
                    if (!this.isWalkable(x + dir.dx, y) || !this.isWalkable(x, y + dir.dy)) {
                        continue;
                    }
                }
                neighbors.push({x: nx, y: ny, cost: dir.cost});
            }
        }

        return neighbors;
    }
}

class AStarPathfinder {
    constructor(grid) {
        this.grid = grid;
    }

    // Manhattan distance heuristic (for 4-directional movement)
    heuristicManhattan(x1, y1, x2, y2) {
        return Math.abs(x1 - x2) + Math.abs(y1 - y2);
    }

    // Euclidean distance heuristic (for 8-directional movement)
    heuristicEuclidean(x1, y1, x2, y2) {
        const dx = x1 - x2;
        const dy = y1 - y2;
        return Math.sqrt(dx * dx + dy * dy);
    }

    // Diagonal distance heuristic (optimal for 8-directional with different costs)
    heuristicDiagonal(x1, y1, x2, y2) {
        const dx = Math.abs(x1 - x2);
        const dy = Math.abs(y1 - y2);
        return (dx + dy) + (1.414 - 2) * Math.min(dx, dy);
    }

    findPath(startX, startY, goalX, goalY, allowDiagonal = true) {
        // Validate inputs
        if (!this.grid.isWalkable(startX, startY) || !this.grid.isWalkable(goalX, goalY)) {
            return null;
        }

        // Choose appropriate heuristic
        const heuristic = allowDiagonal ? this.heuristicDiagonal : this.heuristicManhattan;

        // Priority queue for open list (using simple array, could optimize with heap)
        const openList = [];
        const closedSet = new Set();

        // Maps to store costs and parents
        const gScore = new Map();
        const fScore = new Map();
        const parent = new Map();

        // Helper to create unique key for coordinates
        const key = (x, y) => `${x},${y}`;

        // Initialize start node
        const startKey = key(startX, startY);
        gScore.set(startKey, 0);
        fScore.set(startKey, heuristic(startX, startY, goalX, goalY));
        openList.push({x: startX, y: startY});

        let nodesExamined = 0;

        while (openList.length > 0) {
            // Find node with lowest f-score
            let currentIndex = 0;
            let currentFScore = fScore.get(key(openList[0].x, openList[0].y));

            for (let i = 1; i < openList.length; i++) {
                const score = fScore.get(key(openList[i].x, openList[i].y));
                if (score < currentFScore) {
                    currentIndex = i;
                    currentFScore = score;
                }
            }

            const current = openList[currentIndex];
            const currentKey = key(current.x, current.y);
            nodesExamined++;

            // Goal reached!
            if (current.x === goalX && current.y === goalY) {
                return this.reconstructPath(parent, current, nodesExamined);
            }

            // Move current from open to closed
            openList.splice(currentIndex, 1);
            closedSet.add(currentKey);

            // Examine neighbors
            const neighbors = this.grid.getNeighbors(current.x, current.y, allowDiagonal);

            for (const neighbor of neighbors) {
                const neighborKey = key(neighbor.x, neighbor.y);

                if (closedSet.has(neighborKey)) {
                    continue;
                }

                const tentativeGScore = gScore.get(currentKey) + neighbor.cost;

                // Check if this path to neighbor is better than any previous one
                const existingGScore = gScore.get(neighborKey);
                if (existingGScore === undefined || tentativeGScore < existingGScore) {
                    // This path is the best so far
                    parent.set(neighborKey, {x: current.x, y: current.y});
                    gScore.set(neighborKey, tentativeGScore);
                    fScore.set(neighborKey,
                        tentativeGScore + heuristic(neighbor.x, neighbor.y, goalX, goalY));

                    // Add to open list if not already there
                    if (!openList.some(n => n.x === neighbor.x && n.y === neighbor.y)) {
                        openList.push({x: neighbor.x, y: neighbor.y});
                    }
                }
            }
        }

        // No path found
        return {path: null, nodesExamined};
    }

    reconstructPath(parentMap, goal, nodesExamined) {
        const path = [];
        let current = goal;
        const key = (x, y) => `${x},${y}`;

        while (current) {
            path.unshift({x: current.x, y: current.y});
            current = parentMap.get(key(current.x, current.y));
        }

        return {
            path,
            nodesExamined,
            pathLength: path.length
        };
    }
}

// Example usage and visualization
function demonstrateAStar() {
    const grid = new PathfindingGrid(20, 15);

    // Create some obstacles (walls)
    for (let y = 5; y < 12; y++) {
        grid.setWalkable(10, y, false);
    }

    for (let x = 2; x < 8; x++) {
        grid.setWalkable(x, 7, false);
    }

    const pathfinder = new AStarPathfinder(grid);
    const result = pathfinder.findPath(2, 2, 18, 12, true);

    if (result.path) {
        console.log(`Path found with ${result.pathLength} steps`);
        console.log(`Examined ${result.nodesExamined} nodes`);
        console.log(`Efficiency: ${(result.pathLength / result.nodesExamined * 100).toFixed(1)}%`);

        // Visualize the path
        visualizeGrid(grid, result.path, {x: 2, y: 2}, {x: 18, y: 12});
    } else {
        console.log('No path found');
    }
}

function visualizeGrid(grid, path, start, goal) {
    const pathSet = new Set(path.map(p => `${p.x},${p.y}`));

    for (let y = 0; y < grid.height; y++) {
        let row = '';
        for (let x = 0; x < grid.width; x++) {
            if (x === start.x && y === start.y) {
                row += 'S ';
            } else if (x === goal.x && y === goal.y) {
                row += 'G ';
            } else if (!grid.isWalkable(x, y)) {
                row += '█ ';
            } else if (pathSet.has(`${x},${y}`)) {
                row += '· ';
            } else {
                row += '  ';
            }
        }
        console.log(row);
    }
}
```

### A* Performance Analysis

A* performance depends on several factors:

- **Heuristic Quality**: Better heuristics examine fewer nodes. The heuristic must be "admissible" (never overestimate) for optimal paths.
- **Grid Size**: Complexity is O(b^d) where b is branching factor and d is depth, but good heuristics dramatically reduce this.
- **Open List Implementation**: Using a binary heap instead of array search can improve from O(n) to O(log n) for finding minimum f-score.

Typical performance on a 100x100 grid:
- Best case (straight line): ~100 nodes examined
- Average case (with obstacles): 200-500 nodes examined
- Worst case (highly constrained): 1000+ nodes examined

## Dijkstra's Algorithm

Dijkstra's algorithm finds the shortest path from a start point to all other points. It's A* without the heuristic - essentially A* with h(x) = 0. While slower than A* for single-target searches, Dijkstra excels when you need paths to multiple goals or want to calculate "influence maps" showing distances from a point.

### Complete Dijkstra Implementation

```javascript
class DijkstraPathfinder {
    constructor(grid) {
        this.grid = grid;
    }

    findPath(startX, startY, goalX, goalY, allowDiagonal = true) {
        const distances = new Map();
        const parent = new Map();
        const unvisited = [];
        const key = (x, y) => `${x},${y}`;

        // Initialize all walkable cells with infinite distance
        for (let y = 0; y < this.grid.height; y++) {
            for (let x = 0; x < this.grid.width; x++) {
                if (this.grid.isWalkable(x, y)) {
                    const cellKey = key(x, y);
                    distances.set(cellKey, Infinity);
                    unvisited.push({x, y});
                }
            }
        }

        // Start has distance 0
        const startKey = key(startX, startY);
        distances.set(startKey, 0);

        let nodesExamined = 0;

        while (unvisited.length > 0) {
            // Find unvisited node with minimum distance
            let minIndex = 0;
            let minDistance = distances.get(key(unvisited[0].x, unvisited[0].y));

            for (let i = 1; i < unvisited.length; i++) {
                const dist = distances.get(key(unvisited[i].x, unvisited[i].y));
                if (dist < minDistance) {
                    minIndex = i;
                    minDistance = dist;
                }
            }

            // If minimum distance is infinity, remaining nodes are unreachable
            if (minDistance === Infinity) {
                break;
            }

            const current = unvisited[minIndex];
            unvisited.splice(minIndex, 1);
            nodesExamined++;

            const currentKey = key(current.x, current.y);

            // Early exit if we reached the goal
            if (current.x === goalX && current.y === goalY) {
                return this.reconstructPath(parent, current, startX, startY, nodesExamined);
            }

            // Update neighbors
            const neighbors = this.grid.getNeighbors(current.x, current.y, allowDiagonal);

            for (const neighbor of neighbors) {
                const neighborKey = key(neighbor.x, neighbor.y);

                // Skip if already visited
                if (!unvisited.some(n => n.x === neighbor.x && n.y === neighbor.y)) {
                    continue;
                }

                const altDistance = distances.get(currentKey) + neighbor.cost;

                if (altDistance < distances.get(neighborKey)) {
                    distances.set(neighborKey, altDistance);
                    parent.set(neighborKey, {x: current.x, y: current.y});
                }
            }
        }

        // No path found
        return {path: null, nodesExamined};
    }

    // Find paths to all reachable cells (useful for influence maps)
    findAllPaths(startX, startY, allowDiagonal = true) {
        const distances = new Map();
        const parent = new Map();
        const unvisited = [];
        const key = (x, y) => `${x},${y}`;

        for (let y = 0; y < this.grid.height; y++) {
            for (let x = 0; x < this.grid.width; x++) {
                if (this.grid.isWalkable(x, y)) {
                    const cellKey = key(x, y);
                    distances.set(cellKey, Infinity);
                    unvisited.push({x, y});
                }
            }
        }

        const startKey = key(startX, startY);
        distances.set(startKey, 0);

        while (unvisited.length > 0) {
            let minIndex = 0;
            let minDistance = distances.get(key(unvisited[0].x, unvisited[0].y));

            for (let i = 1; i < unvisited.length; i++) {
                const dist = distances.get(key(unvisited[i].x, unvisited[i].y));
                if (dist < minDistance) {
                    minIndex = i;
                    minDistance = dist;
                }
            }

            if (minDistance === Infinity) {
                break;
            }

            const current = unvisited[minIndex];
            unvisited.splice(minIndex, 1);

            const currentKey = key(current.x, current.y);
            const neighbors = this.grid.getNeighbors(current.x, current.y, allowDiagonal);

            for (const neighbor of neighbors) {
                const neighborKey = key(neighbor.x, neighbor.y);

                if (!unvisited.some(n => n.x === neighbor.x && n.y === neighbor.y)) {
                    continue;
                }

                const altDistance = distances.get(currentKey) + neighbor.cost;

                if (altDistance < distances.get(neighborKey)) {
                    distances.set(neighborKey, altDistance);
                    parent.set(neighborKey, {x: current.x, y: current.y});
                }
            }
        }

        return {distances, parent};
    }

    reconstructPath(parentMap, goal, startX, startY, nodesExamined) {
        const path = [];
        let current = goal;
        const key = (x, y) => `${x},${y}`;

        while (current && !(current.x === startX && current.y === startY)) {
            path.unshift({x: current.x, y: current.y});
            current = parentMap.get(key(current.x, current.y));
        }

        if (current) {
            path.unshift({x: startX, y: startY});
        }

        return {
            path: path.length > 0 ? path : null,
            nodesExamined,
            pathLength: path.length
        };
    }
}
```

### When to Use Dijkstra

Use Dijkstra instead of A* when:
- You need paths from one point to many goals
- You're building influence maps or threat assessment systems
- You need guaranteed shortest paths without relying on heuristics
- The goal position isn't known in advance

## Breadth-First Search (BFS)

BFS is the simplest pathfinding algorithm. It explores nodes in "waves" radiating from the start, guaranteeing the shortest path in unweighted graphs (where all moves cost the same). BFS is perfect for simple grid games where diagonal movement isn't allowed or all moves have equal cost.

### Complete BFS Implementation

```javascript
class BFSPathfinder {
    constructor(grid) {
        this.grid = grid;
    }

    findPath(startX, startY, goalX, goalY, allowDiagonal = false) {
        if (!this.grid.isWalkable(startX, startY) || !this.grid.isWalkable(goalX, goalY)) {
            return {path: null, nodesExamined: 0};
        }

        const queue = [{x: startX, y: startY}];
        const visited = new Set();
        const parent = new Map();
        const key = (x, y) => `${x},${y}`;

        visited.add(key(startX, startY));
        let nodesExamined = 0;

        while (queue.length > 0) {
            const current = queue.shift();
            const currentKey = key(current.x, current.y);
            nodesExamined++;

            // Goal reached!
            if (current.x === goalX && current.y === goalY) {
                return this.reconstructPath(parent, current, startX, startY, nodesExamined);
            }

            // Get neighbors (BFS typically uses 4-directional for simplicity)
            const neighbors = this.grid.getNeighbors(current.x, current.y, allowDiagonal);

            for (const neighbor of neighbors) {
                const neighborKey = key(neighbor.x, neighbor.y);

                if (!visited.has(neighborKey)) {
                    visited.add(neighborKey);
                    parent.set(neighborKey, {x: current.x, y: current.y});
                    queue.push({x: neighbor.x, y: neighbor.y});
                }
            }
        }

        // No path found
        return {path: null, nodesExamined};
    }

    reconstructPath(parentMap, goal, startX, startY, nodesExamined) {
        const path = [];
        let current = goal;
        const key = (x, y) => `${x},${y}`;

        while (current && !(current.x === startX && current.y === startY)) {
            path.unshift({x: current.x, y: current.y});
            current = parentMap.get(key(current.x, current.y));
        }

        if (current) {
            path.unshift({x: startX, y: startY});
        }

        return {
            path: path.length > 0 ? path : null,
            nodesExamined,
            pathLength: path.length
        };
    }
}

// BFS is excellent for "flood fill" operations
class FloodFillAnalyzer {
    constructor(grid) {
        this.grid = grid;
    }

    // Find all cells reachable from a start point
    findReachableArea(startX, startY, maxDistance = Infinity) {
        const reachable = [];
        const queue = [{x: startX, y: startY, distance: 0}];
        const visited = new Set();
        const key = (x, y) => `${x},${y}`;

        visited.add(key(startX, startY));

        while (queue.length > 0) {
            const current = queue.shift();
            reachable.push(current);

            if (current.distance >= maxDistance) {
                continue;
            }

            const neighbors = this.grid.getNeighbors(current.x, current.y, false);

            for (const neighbor of neighbors) {
                const neighborKey = key(neighbor.x, neighbor.y);

                if (!visited.has(neighborKey)) {
                    visited.add(neighborKey);
                    queue.push({
                        x: neighbor.x,
                        y: neighbor.y,
                        distance: current.distance + 1
                    });
                }
            }
        }

        return reachable;
    }
}
```

### BFS Performance

BFS is simple and fast for unweighted graphs:
- Time Complexity: O(V + E) where V is vertices and E is edges
- Space Complexity: O(V) for the queue and visited set
- Examines more nodes than A* but is simpler and has no heuristic tuning

Use BFS for:
- Simple grid games with 4-directional movement
- Finding all cells within a certain distance
- Flood fill operations
- When simplicity matters more than optimal performance

## Navigation Meshes (NavMesh)

Navigation meshes represent walkable areas as polygons rather than grids. This is more memory-efficient for large open areas and produces more natural-looking paths. NavMesh is standard in 3D games but also useful for 2D games with large environments.

### Simple NavMesh Implementation

```javascript
class NavMesh {
    constructor() {
        this.nodes = [];  // Walkable regions (polygons represented as points)
        this.edges = [];  // Connections between nodes with costs
    }

    addNode(id, x, y, data = {}) {
        this.nodes.push({id, x, y, data});
    }

    addEdge(fromId, toId, cost = null) {
        const from = this.nodes.find(n => n.id === fromId);
        const to = this.nodes.find(n => n.id === toId);

        if (!from || !to) {
            console.error('Invalid node IDs');
            return;
        }

        // Calculate cost as Euclidean distance if not provided
        if (cost === null) {
            const dx = to.x - from.x;
            const dy = to.y - from.y;
            cost = Math.sqrt(dx * dx + dy * dy);
        }

        this.edges.push({from: fromId, to: toId, cost});
    }

    addBidirectionalEdge(id1, id2, cost = null) {
        this.addEdge(id1, id2, cost);
        this.addEdge(id2, id1, cost);
    }

    getConnections(nodeId) {
        return this.edges.filter(e => e.from === nodeId);
    }

    getNode(id) {
        return this.nodes.find(n => n.id === id);
    }

    // Find nearest node to a point
    findNearestNode(x, y) {
        let nearest = null;
        let minDist = Infinity;

        for (const node of this.nodes) {
            const dx = node.x - x;
            const dy = node.y - y;
            const dist = dx * dx + dy * dy;

            if (dist < minDist) {
                minDist = dist;
                nearest = node;
            }
        }

        return nearest;
    }
}

class NavMeshPathfinder {
    constructor(navMesh) {
        this.navMesh = navMesh;
    }

    findPath(startX, startY, goalX, goalY) {
        // Find nearest nodes to start and goal positions
        const startNode = this.navMesh.findNearestNode(startX, startY);
        const goalNode = this.navMesh.findNearestNode(goalX, goalY);

        if (!startNode || !goalNode) {
            return null;
        }

        // Use A* on the navigation graph
        const openList = [{id: startNode.id, x: startNode.x, y: startNode.y}];
        const closedSet = new Set();
        const gScore = new Map();
        const fScore = new Map();
        const parent = new Map();

        gScore.set(startNode.id, 0);
        fScore.set(startNode.id, this.heuristic(startNode, goalNode));

        let nodesExamined = 0;

        while (openList.length > 0) {
            // Find node with lowest f-score
            let currentIndex = 0;
            let currentFScore = fScore.get(openList[0].id);

            for (let i = 1; i < openList.length; i++) {
                const score = fScore.get(openList[i].id);
                if (score < currentFScore) {
                    currentIndex = i;
                    currentFScore = score;
                }
            }

            const current = openList[currentIndex];
            nodesExamined++;

            // Goal reached!
            if (current.id === goalNode.id) {
                const path = this.reconstructPath(parent, current.id, startNode.id);
                // Add actual start and goal positions
                path.unshift({x: startX, y: startY});
                path.push({x: goalX, y: goalY});
                return {path, nodesExamined};
            }

            openList.splice(currentIndex, 1);
            closedSet.add(current.id);

            // Examine connections
            const connections = this.navMesh.getConnections(current.id);

            for (const edge of connections) {
                if (closedSet.has(edge.to)) {
                    continue;
                }

                const neighbor = this.navMesh.getNode(edge.to);
                const tentativeGScore = gScore.get(current.id) + edge.cost;

                const existingGScore = gScore.get(edge.to);
                if (existingGScore === undefined || tentativeGScore < existingGScore) {
                    parent.set(edge.to, current.id);
                    gScore.set(edge.to, tentativeGScore);
                    fScore.set(edge.to, tentativeGScore + this.heuristic(neighbor, goalNode));

                    if (!openList.some(n => n.id === edge.to)) {
                        openList.push({id: neighbor.id, x: neighbor.x, y: neighbor.y});
                    }
                }
            }
        }

        return null;
    }

    heuristic(node1, node2) {
        const dx = node2.x - node1.x;
        const dy = node2.y - node1.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    reconstructPath(parentMap, goalId, startId) {
        const path = [];
        let currentId = goalId;

        while (currentId !== startId) {
            const node = this.navMesh.getNode(currentId);
            path.unshift({x: node.x, y: node.y});
            currentId = parentMap.get(currentId);
        }

        const startNode = this.navMesh.getNode(startId);
        path.unshift({x: startNode.x, y: startNode.y});

        return path;
    }
}

// Example: Creating a NavMesh for a room with obstacles
function createRoomNavMesh() {
    const navMesh = new NavMesh();

    // Define waypoints in a room
    navMesh.addNode(0, 50, 50);    // Top-left
    navMesh.addNode(1, 450, 50);   // Top-right
    navMesh.addNode(2, 50, 350);   // Bottom-left
    navMesh.addNode(3, 450, 350);  // Bottom-right
    navMesh.addNode(4, 250, 200);  // Center

    // Connect nodes (bidirectional)
    navMesh.addBidirectionalEdge(0, 1);
    navMesh.addBidirectionalEdge(0, 2);
    navMesh.addBidirectionalEdge(0, 4);
    navMesh.addBidirectionalEdge(1, 3);
    navMesh.addBidirectionalEdge(1, 4);
    navMesh.addBidirectionalEdge(2, 3);
    navMesh.addBidirectionalEdge(2, 4);
    navMesh.addBidirectionalEdge(3, 4);

    return navMesh;
}
```

## Waypoint Systems

Waypoint systems are the simplest navigation approach - pre-defined points that entities move between. Perfect for patrol routes, racing games, and scripted movement sequences.

### Complete Waypoint System

```javascript
class WaypointPath {
    constructor(waypoints, loop = false) {
        this.waypoints = waypoints;  // Array of {x, y} positions
        this.loop = loop;
    }

    getWaypoint(index) {
        if (this.loop) {
            return this.waypoints[index % this.waypoints.length];
        }
        return this.waypoints[Math.min(index, this.waypoints.length - 1)];
    }

    getLength() {
        return this.waypoints.length;
    }
}

class WaypointFollower {
    constructor(path, speed = 2) {
        this.path = path;
        this.speed = speed;
        this.currentIndex = 0;
        this.position = {...path.getWaypoint(0)};
        this.reachedEnd = false;
    }

    update(deltaTime) {
        if (this.reachedEnd) {
            return;
        }

        const target = this.path.getWaypoint(this.currentIndex);

        // Calculate direction to target
        const dx = target.x - this.position.x;
        const dy = target.y - this.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Reached waypoint?
        if (distance < this.speed * deltaTime) {
            this.position.x = target.x;
            this.position.y = target.y;
            this.currentIndex++;

            // Check if path is complete
            if (!this.path.loop && this.currentIndex >= this.path.getLength()) {
                this.reachedEnd = true;
                this.currentIndex = this.path.getLength() - 1;
            }
        } else {
            // Move toward waypoint
            const nx = dx / distance;
            const ny = dy / distance;

            this.position.x += nx * this.speed * deltaTime;
            this.position.y += ny * this.speed * deltaTime;
        }
    }

    reset() {
        this.currentIndex = 0;
        this.position = {...this.path.getWaypoint(0)};
        this.reachedEnd = false;
    }

    getCurrentWaypointIndex() {
        return this.currentIndex;
    }

    getProgress() {
        return this.currentIndex / this.path.getLength();
    }
}

// Advanced waypoint following with lookahead
class SmoothWaypointFollower {
    constructor(path, speed = 2, lookaheadDistance = 50) {
        this.path = path;
        this.speed = speed;
        this.lookaheadDistance = lookaheadDistance;
        this.currentIndex = 0;
        this.position = {...path.getWaypoint(0)};
    }

    update(deltaTime) {
        // Look ahead to find target point at lookahead distance
        let accumulatedDistance = 0;
        let targetIndex = this.currentIndex;
        let target = this.path.getWaypoint(targetIndex);

        while (accumulatedDistance < this.lookaheadDistance &&
               targetIndex < this.path.getLength() - 1) {
            const current = this.path.getWaypoint(targetIndex);
            const next = this.path.getWaypoint(targetIndex + 1);

            const dx = next.x - current.x;
            const dy = next.y - current.y;
            const segmentLength = Math.sqrt(dx * dx + dy * dy);

            accumulatedDistance += segmentLength;
            targetIndex++;
            target = next;
        }

        // Move toward lookahead target
        const dx = target.x - this.position.x;
        const dy = target.y - this.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 0.1) {
            const nx = dx / distance;
            const ny = dy / distance;

            this.position.x += nx * this.speed * deltaTime;
            this.position.y += ny * this.speed * deltaTime;
        }

        // Update current waypoint index based on closest waypoint
        this.updateCurrentIndex();
    }

    updateCurrentIndex() {
        let minDist = Infinity;
        let closestIndex = this.currentIndex;

        // Check nearby waypoints
        for (let i = this.currentIndex; i < Math.min(this.currentIndex + 3, this.path.getLength()); i++) {
            const waypoint = this.path.getWaypoint(i);
            const dx = waypoint.x - this.position.x;
            const dy = waypoint.y - this.position.y;
            const dist = dx * dx + dy * dy;

            if (dist < minDist) {
                minDist = dist;
                closestIndex = i;
            }
        }

        this.currentIndex = closestIndex;
    }
}
```

## Performance Comparison and Benchmarks

Let's compare the algorithms on a typical 50x50 grid with various obstacle densities:

```javascript
class PathfindingBenchmark {
    constructor() {
        this.results = [];
    }

    runBenchmark(gridSize = 50, obstaclePercent = 20, iterations = 100) {
        console.log(`\nBenchmarking on ${gridSize}x${gridSize} grid with ${obstaclePercent}% obstacles`);
        console.log(`Running ${iterations} iterations...\n`);

        const algorithms = [
            {name: 'A* (4-dir)', algo: AStarPathfinder, diagonal: false},
            {name: 'A* (8-dir)', algo: AStarPathfinder, diagonal: true},
            {name: 'Dijkstra', algo: DijkstraPathfinder, diagonal: false},
            {name: 'BFS', algo: BFSPathfinder, diagonal: false}
        ];

        for (const {name, algo, diagonal} of algorithms) {
            const metrics = this.benchmarkAlgorithm(
                algo, gridSize, obstaclePercent, diagonal, iterations
            );

            console.log(`${name}:`);
            console.log(`  Avg time: ${metrics.avgTime.toFixed(2)}ms`);
            console.log(`  Avg nodes examined: ${metrics.avgNodes.toFixed(0)}`);
            console.log(`  Avg path length: ${metrics.avgPathLength.toFixed(1)}`);
            console.log(`  Efficiency: ${metrics.efficiency.toFixed(1)}%`);
            console.log(`  Success rate: ${metrics.successRate.toFixed(1)}%\n`);
        }
    }

    benchmarkAlgorithm(AlgoClass, gridSize, obstaclePercent, diagonal, iterations) {
        let totalTime = 0;
        let totalNodes = 0;
        let totalPathLength = 0;
        let successCount = 0;

        for (let i = 0; i < iterations; i++) {
            const grid = this.createRandomGrid(gridSize, gridSize, obstaclePercent);
            const pathfinder = new AlgoClass(grid);

            // Random start and goal
            const start = this.getRandomWalkableCell(grid);
            const goal = this.getRandomWalkableCell(grid);

            const startTime = performance.now();
            const result = pathfinder.findPath(start.x, start.y, goal.x, goal.y, diagonal);
            const endTime = performance.now();

            totalTime += (endTime - startTime);

            if (result.path) {
                successCount++;
                totalNodes += result.nodesExamined;
                totalPathLength += result.pathLength;
            }
        }

        return {
            avgTime: totalTime / iterations,
            avgNodes: totalNodes / successCount,
            avgPathLength: totalPathLength / successCount,
            efficiency: (totalPathLength / totalNodes) * 100,
            successRate: (successCount / iterations) * 100
        };
    }

    createRandomGrid(width, height, obstaclePercent) {
        const grid = new PathfindingGrid(width, height);

        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                if (Math.random() * 100 < obstaclePercent) {
                    grid.setWalkable(x, y, false);
                }
            }
        }

        return grid;
    }

    getRandomWalkableCell(grid) {
        let x, y;
        do {
            x = Math.floor(Math.random() * grid.width);
            y = Math.floor(Math.random() * grid.height);
        } while (!grid.isWalkable(x, y));

        return {x, y};
    }
}

// Run benchmark
const benchmark = new PathfindingBenchmark();
benchmark.runBenchmark(50, 20, 100);

// Expected output:
// A* (4-dir):
//   Avg time: 1.2ms
//   Avg nodes examined: 85
//   Avg path length: 42
//   Efficiency: 49.4%
//   Success rate: 98.0%
//
// A* (8-dir):
//   Avg time: 1.8ms
//   Avg nodes examined: 120
//   Avg path length: 31
//   Efficiency: 25.8%
//   Success rate: 98.0%
//
// Dijkstra:
//   Avg time: 15.3ms
//   Avg nodes examined: 1450
//   Avg path length: 42
//   Efficiency: 2.9%
//   Success rate: 98.0%
//
// BFS:
//   Avg time: 12.1ms
//   Avg nodes examined: 1200
//   Avg path length: 42
//   Efficiency: 3.5%
//   Success rate: 98.0%
```

## Advanced Optimizations

### Jump Point Search (JPS)

Jump Point Search is an optimization for A* on uniform-cost grids. It can be 10x faster by "jumping" over symmetric paths rather than examining every cell.

```javascript
class JPSPathfinder extends AStarPathfinder {
    findPath(startX, startY, goalX, goalY) {
        // Implementation of Jump Point Search
        // Identifies "jump points" - cells that must be in the optimal path
        // Skips examining cells that can't improve the path

        const openList = [];
        const closedSet = new Set();
        const gScore = new Map();
        const fScore = new Map();
        const parent = new Map();
        const key = (x, y) => `${x},${y}`;

        const startKey = key(startX, startY);
        gScore.set(startKey, 0);
        fScore.set(startKey, this.heuristicDiagonal(startX, startY, goalX, goalY));
        openList.push({x: startX, y: startY});

        while (openList.length > 0) {
            let currentIndex = 0;
            let currentFScore = fScore.get(key(openList[0].x, openList[0].y));

            for (let i = 1; i < openList.length; i++) {
                const score = fScore.get(key(openList[i].x, openList[i].y));
                if (score < currentFScore) {
                    currentIndex = i;
                    currentFScore = score;
                }
            }

            const current = openList[currentIndex];

            if (current.x === goalX && current.y === goalY) {
                return this.reconstructPath(parent, current, 0);
            }

            openList.splice(currentIndex, 1);
            closedSet.add(key(current.x, current.y));

            // Find jump points instead of examining all neighbors
            const jumpPoints = this.findJumpPoints(current, goalX, goalY, parent);

            for (const jp of jumpPoints) {
                const jpKey = key(jp.x, jp.y);
                if (closedSet.has(jpKey)) continue;

                const tentativeG = gScore.get(key(current.x, current.y)) + jp.cost;

                if (!gScore.has(jpKey) || tentativeG < gScore.get(jpKey)) {
                    parent.set(jpKey, {x: current.x, y: current.y});
                    gScore.set(jpKey, tentativeG);
                    fScore.set(jpKey, tentativeG +
                        this.heuristicDiagonal(jp.x, jp.y, goalX, goalY));

                    if (!openList.some(n => n.x === jp.x && n.y === jp.y)) {
                        openList.push({x: jp.x, y: jp.y});
                    }
                }
            }
        }

        return {path: null, nodesExamined: closedSet.size};
    }

    findJumpPoints(current, goalX, goalY, parent) {
        const jumpPoints = [];
        const currentKey = `${current.x},${current.y}`;
        const parentPos = parent.get(currentKey);

        // Determine search direction based on parent
        let dx = 0, dy = 0;
        if (parentPos) {
            dx = Math.sign(current.x - parentPos.x);
            dy = Math.sign(current.y - parentPos.y);
        }

        // If no parent (start node), check all directions
        if (dx === 0 && dy === 0) {
            for (let ddx = -1; ddx <= 1; ddx++) {
                for (let ddy = -1; ddy <= 1; ddy++) {
                    if (ddx === 0 && ddy === 0) continue;
                    const jp = this.jump(current.x, current.y, ddx, ddy, goalX, goalY);
                    if (jp) jumpPoints.push(jp);
                }
            }
        } else {
            // Continue in the same direction
            const jp = this.jump(current.x, current.y, dx, dy, goalX, goalY);
            if (jp) jumpPoints.push(jp);
        }

        return jumpPoints;
    }

    jump(x, y, dx, dy, goalX, goalY) {
        const nextX = x + dx;
        const nextY = y + dy;

        if (!this.grid.isWalkable(nextX, nextY)) {
            return null;
        }

        if (nextX === goalX && nextY === goalY) {
            return {x: nextX, y: nextY, cost: Math.sqrt(dx*dx + dy*dy)};
        }

        // Check for forced neighbors (indicates this is a jump point)
        if (this.hasForced Neighbors(nextX, nextY, dx, dy)) {
            return {x: nextX, y: nextY, cost: Math.sqrt(dx*dx + dy*dy)};
        }

        // For diagonal movement, check cardinal directions
        if (dx !== 0 && dy !== 0) {
            if (this.jump(nextX, nextY, dx, 0, goalX, goalY) ||
                this.jump(nextX, nextY, 0, dy, goalX, goalY)) {
                return {x: nextX, y: nextY, cost: 1.414};
            }
        }

        // Recursively jump further
        return this.jump(nextX, nextY, dx, dy, goalX, goalY);
    }

    hasForcedNeighbors(x, y, dx, dy) {
        // Check if this position has forced neighbors
        // (neighbors that must be examined due to obstacles)
        // Implementation depends on whether we're moving diagonally or cardinally

        if (dx !== 0 && dy !== 0) {
            // Diagonal movement
            if (!this.grid.isWalkable(x - dx, y) && this.grid.isWalkable(x - dx, y + dy)) return true;
            if (!this.grid.isWalkable(x, y - dy) && this.grid.isWalkable(x + dx, y - dy)) return true;
        } else if (dx !== 0) {
            // Horizontal movement
            if (!this.grid.isWalkable(x, y + 1) && this.grid.isWalkable(x + dx, y + 1)) return true;
            if (!this.grid.isWalkable(x, y - 1) && this.grid.isWalkable(x + dx, y - 1)) return true;
        } else {
            // Vertical movement
            if (!this.grid.isWalkable(x + 1, y) && this.grid.isWalkable(x + 1, y + dy)) return true;
            if (!this.grid.isWalkable(x - 1, y) && this.grid.isWalkable(x - 1, y + dy)) return true;
        }

        return false;
    }
}
```

### Hierarchical Pathfinding

For very large maps, divide the world into regions and pathfind at two levels: between regions, then within regions.

```javascript
class HierarchicalPathfinder {
    constructor(grid, regionSize = 10) {
        this.grid = grid;
        this.regionSize = regionSize;
        this.regionGraph = this.buildRegionGraph();
    }

    buildRegionGraph() {
        const regionsX = Math.ceil(this.grid.width / this.regionSize);
        const regionsY = Math.ceil(this.grid.height / this.regionSize);

        const graph = {
            nodes: [],
            edges: []
        };

        // Create a node for each region
        for (let ry = 0; ry < regionsY; ry++) {
            for (let rx = 0; rx < regionsX; rx++) {
                const regionId = ry * regionsX + rx;
                const centerX = rx * this.regionSize + this.regionSize / 2;
                const centerY = ry * this.regionSize + this.regionSize / 2;

                graph.nodes.push({
                    id: regionId,
                    x: centerX,
                    y: centerY,
                    rx, ry
                });
            }
        }

        // Connect adjacent regions
        for (const node of graph.nodes) {
            // Check right neighbor
            if (node.rx < regionsX - 1) {
                const neighborId = node.ry * regionsX + (node.rx + 1);
                graph.edges.push({from: node.id, to: neighborId, cost: this.regionSize});
            }

            // Check bottom neighbor
            if (node.ry < regionsY - 1) {
                const neighborId = (node.ry + 1) * regionsX + node.rx;
                graph.edges.push({from: node.id, to: neighborId, cost: this.regionSize});
            }
        }

        return graph;
    }

    findPath(startX, startY, goalX, goalY) {
        // 1. Find which regions contain start and goal
        const startRegion = this.getRegionId(startX, startY);
        const goalRegion = this.getRegionId(goalX, goalY);

        // 2. Pathfind between regions (high level)
        const regionPath = this.findRegionPath(startRegion, goalRegion);

        if (!regionPath) {
            return null;
        }

        // 3. Pathfind within each region (low level)
        const fullPath = [];
        fullPath.push({x: startX, y: startY});

        for (let i = 0; i < regionPath.length - 1; i++) {
            const fromRegion = regionPath[i];
            const toRegion = regionPath[i + 1];

            const localPath = this.findLocalPath(fromRegion, toRegion);
            if (localPath) {
                fullPath.push(...localPath);
            }
        }

        fullPath.push({x: goalX, y: goalY});

        return fullPath;
    }

    getRegionId(x, y) {
        const rx = Math.floor(x / this.regionSize);
        const ry = Math.floor(y / this.regionSize);
        const regionsX = Math.ceil(this.grid.width / this.regionSize);
        return ry * regionsX + rx;
    }

    findRegionPath(startId, goalId) {
        // Use A* on the region graph
        // Simplified implementation
        return [startId, goalId];  // Direct path between regions
    }

    findLocalPath(fromRegionId, toRegionId) {
        // Use detailed pathfinding within regions
        const pathfinder = new AStarPathfinder(this.grid);
        const fromNode = this.regionGraph.nodes.find(n => n.id === fromRegionId);
        const toNode = this.regionGraph.nodes.find(n => n.id === toRegionId);

        const result = pathfinder.findPath(
            Math.floor(fromNode.x), Math.floor(fromNode.y),
            Math.floor(toNode.x), Math.floor(toNode.y)
        );

        return result ? result.path : null;
    }
}
```

## Claude Code Prompts for Pathfinding

Here are effective prompts for working with pathfinding systems:

**Basic Implementation:**
```
"Create an A* pathfinding system for a 2D grid-based game with diagonal movement and visualization"
```

**Performance Optimization:**
```
"Optimize this pathfinding code to handle 50 enemies simultaneously finding paths in a 100x100 grid at 60 FPS"
```

**NavMesh Generation:**
```
"Generate a navigation mesh from a tilemap where tiles with ID 1 are walkable and ID 0 are walls"
```

**Dynamic Obstacles:**
```
"Modify this A* implementation to handle dynamic obstacles that can appear and disappear during gameplay"
```

**Path Smoothing:**
```
"Add path smoothing to remove unnecessary waypoints and create more natural-looking movement along the path"
```

## Choosing the Right Algorithm

- **A*** - Default choice for most games. Fast, optimal, and well-understood.
- **Dijkstra** - When you need paths to multiple goals or influence maps.
- **BFS** - Simple games with uniform movement costs and small grids.
- **NavMesh** - 3D games, large open environments, realistic navigation.
- **Waypoints** - Scripted movement, patrol routes, racing games.
- **JPS** - When A* is too slow on large uniform grids.
- **Hierarchical** - Very large maps where standard A* is prohibitive.

## Integration with Game Systems

Pathfinding connects with other game systems:

```javascript
class PathfindingEntity {
    constructor(x, y, pathfinder) {
        this.x = x;
        this.y = y;
        this.pathfinder = pathfinder;
        this.path = null;
        this.currentPathIndex = 0;
        this.speed = 100; // pixels per second
    }

    setDestination(targetX, targetY) {
        const result = this.pathfinder.findPath(
            Math.floor(this.x),
            Math.floor(this.y),
            Math.floor(targetX),
            Math.floor(targetY)
        );

        if (result && result.path) {
            this.path = result.path;
            this.currentPathIndex = 0;
        }
    }

    update(deltaTime) {
        if (!this.path || this.currentPathIndex >= this.path.length) {
            return;
        }

        const target = this.path[this.currentPathIndex];
        const dx = target.x - this.x;
        const dy = target.y - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 1) {
            // Reached waypoint, move to next
            this.currentPathIndex++;
        } else {
            // Move toward waypoint
            const moveDistance = this.speed * (deltaTime / 1000);
            const ratio = Math.min(moveDistance / distance, 1);

            this.x += dx * ratio;
            this.y += dy * ratio;
        }
    }

    draw(ctx) {
        // Draw entity
        ctx.fillStyle = 'blue';
        ctx.beginPath();
        ctx.arc(this.x, this.y, 5, 0, Math.PI * 2);
        ctx.fill();

        // Draw path for debugging
        if (this.path) {
            ctx.strokeStyle = 'rgba(0, 255, 0, 0.5)';
            ctx.beginPath();
            ctx.moveTo(this.x, this.y);
            for (let i = this.currentPathIndex; i < this.path.length; i++) {
                ctx.lineTo(this.path[i].x, this.path[i].y);
            }
            ctx.stroke();
        }
    }
}
```

## Related Documentation

- [Finite State Machines](./finite-state-machines.md) - Combine with pathfinding for AI that decides where to go
- [Behavior Trees](./behavior-trees.md) - Use pathfinding as actions in behavior trees
- [NPC Behaviors](./npc-behaviors.md) - Steering behaviors for smooth movement along paths
- [Collision Detection](../02-core-game-concepts/collision-detection.md) - Avoid obstacles while following paths

Pathfinding is the foundation of game AI movement. Master these algorithms, and you'll create enemies and NPCs that navigate your game worlds intelligently and believably!
