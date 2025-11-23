"""
Categorical A* and Advanced Pathfinding Algorithms
Demonstrates A*, Dijkstra, and bidirectional search in category theory form
"""

import heapq
import math
from typing import Dict, List, Set, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time
import random

# Categorical abstractions

class Morphism(ABC):
    """Abstract morphism in a category"""

    @abstractmethod
    def compose(self, other: 'Morphism') -> 'Morphism':
        """Morphism composition"""
        pass

    @abstractmethod
    def cost(self) -> float:
        """Morphism cost/weight"""
        pass

@dataclass
class PathMorphism(Morphism):
    """Path as morphism in the free category"""
    nodes: List[str]
    total_cost: float = 0.0

    def compose(self, other: 'PathMorphism') -> 'PathMorphism':
        """Path concatenation as composition"""
        if self.nodes[-1] != other.nodes[0]:
            raise ValueError("Paths don't compose")

        combined_nodes = self.nodes + other.nodes[1:]
        combined_cost = self.total_cost + other.total_cost
        return PathMorphism(combined_nodes, combined_cost)

    def cost(self) -> float:
        return self.total_cost

class Functor(ABC):
    """Abstract functor"""

    @abstractmethod
    def map_object(self, obj: Any) -> Any:
        """Map objects"""
        pass

    @abstractmethod
    def map_morphism(self, morphism: Morphism) -> Morphism:
        """Map morphisms (preserving composition)"""
        pass

class CostFunctor(Functor):
    """Functor from paths to costs"""

    def __init__(self, cost_function: Callable[[str, str], float]):
        self.cost_function = cost_function

    def map_object(self, node: str) -> str:
        """Identity on objects"""
        return node

    def map_morphism(self, path: PathMorphism) -> float:
        """Map path to its cost"""
        total = 0
        for i in range(len(path.nodes) - 1):
            total += self.cost_function(path.nodes[i], path.nodes[i+1])
        return total

# A* Implementation in Categorical Form

class CategoricalAStar:
    """A* pathfinding with categorical abstractions"""

    def __init__(self, graph: Dict[str, List[Tuple[str, float]]],
                 heuristic: Callable[[str, str], float]):
        self.graph = graph
        self.heuristic = heuristic
        self.cost_functor = CostFunctor(self._edge_cost)

    def _edge_cost(self, u: str, v: str) -> float:
        """Get edge cost from graph"""
        for neighbor, cost in self.graph.get(u, []):
            if neighbor == v:
                return cost
        return float('inf')

    def find_path(self, start: str, goal: str) -> Optional[PathMorphism]:
        """
        A* search with categorical structure
        F*(p) = g(p) + h(target(p))
        """

        # Priority queue: (f_score, g_score, node, path)
        open_set = [(0, 0, start, [start])]
        closed_set = set()

        # g_score: actual cost from start
        g_scores = {start: 0}

        # f_score: g + h (estimated total cost)
        f_scores = {start: self.heuristic(start, goal)}

        # Parent tracking for path reconstruction
        parents = {start: None}

        while open_set:
            f_score, g_score, current, path = heapq.heappop(open_set)

            if current == goal:
                # Reconstruct path as morphism
                return PathMorphism(path, g_score)

            if current in closed_set:
                continue

            closed_set.add(current)

            # Explore neighbors
            for neighbor, edge_cost in self.graph.get(current, []):
                if neighbor in closed_set:
                    continue

                tentative_g = g_score + edge_cost

                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    # Update scores
                    g_scores[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal)
                    f_scores[neighbor] = f_score

                    # Update path
                    new_path = path + [neighbor]

                    # Add to open set
                    heapq.heappush(open_set,
                                 (f_score, tentative_g, neighbor, new_path))

                    parents[neighbor] = current

        return None  # No path found

    def verify_optimality(self, path: PathMorphism, goal: str) -> bool:
        """Verify that A* found optimal path (with admissible heuristic)"""
        # Check admissibility: h(n) ≤ actual_cost(n, goal)
        for i, node in enumerate(path.nodes[:-1]):
            h_value = self.heuristic(node, goal)
            actual_remaining = sum(
                self._edge_cost(path.nodes[j], path.nodes[j+1])
                for j in range(i, len(path.nodes)-1)
            )
            if h_value > actual_remaining:
                print(f"Heuristic not admissible at {node}: {h_value} > {actual_remaining}")
                return False
        return True

# Bidirectional Search with Categorical Meet-in-the-Middle

class BidirectionalSearch:
    """Bidirectional search with categorical composition"""

    def __init__(self, graph: Dict[str, List[Tuple[str, float]]]):
        self.graph = graph
        self.reverse_graph = self._build_reverse_graph()

    def _build_reverse_graph(self) -> Dict[str, List[Tuple[str, float]]]:
        """Build reverse graph for backward search"""
        reverse = {}
        for node, neighbors in self.graph.items():
            for neighbor, cost in neighbors:
                if neighbor not in reverse:
                    reverse[neighbor] = []
                reverse[neighbor].append((node, cost))
        return reverse

    def search(self, start: str, goal: str) -> Optional[PathMorphism]:
        """Bidirectional search meeting in the middle"""

        # Forward search from start
        forward_frontier = {start}
        forward_visited = {start: (0, [start])}  # node -> (cost, path)

        # Backward search from goal
        backward_frontier = {goal}
        backward_visited = {goal: (0, [goal])}  # node -> (cost, path)

        best_path = None
        best_cost = float('inf')

        while forward_frontier and backward_frontier:
            # Expand forward frontier
            if len(forward_frontier) <= len(backward_frontier):
                new_frontier = set()

                for node in forward_frontier:
                    cost, path = forward_visited[node]

                    for neighbor, edge_cost in self.graph.get(node, []):
                        new_cost = cost + edge_cost

                        if neighbor not in forward_visited or new_cost < forward_visited[neighbor][0]:
                            forward_visited[neighbor] = (new_cost, path + [neighbor])
                            new_frontier.add(neighbor)

                        # Check for meeting point
                        if neighbor in backward_visited:
                            backward_cost, backward_path = backward_visited[neighbor]
                            total_cost = new_cost + backward_cost

                            if total_cost < best_cost:
                                # Compose paths
                                full_path = path + [neighbor] + backward_path[1:][::-1]
                                best_path = PathMorphism(full_path, total_cost)
                                best_cost = total_cost

                forward_frontier = new_frontier

            # Expand backward frontier
            else:
                new_frontier = set()

                for node in backward_frontier:
                    cost, path = backward_visited[node]

                    for neighbor, edge_cost in self.reverse_graph.get(node, []):
                        new_cost = cost + edge_cost

                        if neighbor not in backward_visited or new_cost < backward_visited[neighbor][0]:
                            backward_visited[neighbor] = (new_cost, [neighbor] + path)
                            new_frontier.add(neighbor)

                        # Check for meeting point
                        if neighbor in forward_visited:
                            forward_cost, forward_path = forward_visited[neighbor]
                            total_cost = forward_cost + new_cost

                            if total_cost < best_cost:
                                # Compose paths
                                full_path = forward_path + path[::-1]
                                best_path = PathMorphism(full_path, total_cost)
                                best_cost = total_cost

                backward_frontier = new_frontier

            # Early termination if we found a path
            if best_path and not forward_frontier and not backward_frontier:
                break

        return best_path

# Dijkstra with Categorical Priority Queue

class CategoricalDijkstra:
    """Dijkstra's algorithm with categorical abstractions"""

    def __init__(self, graph: Dict[str, List[Tuple[str, float]]]):
        self.graph = graph

    def find_shortest_paths(self, start: str) -> Dict[str, PathMorphism]:
        """Find shortest paths from start to all reachable nodes"""

        # Priority queue: (distance, node, path)
        pq = [(0, start, [start])]
        distances = {start: 0}
        paths = {}

        while pq:
            dist, node, path = heapq.heappop(pq)

            if node in paths:
                continue

            paths[node] = PathMorphism(path, dist)

            for neighbor, edge_cost in self.graph.get(node, []):
                new_dist = dist + edge_cost

                if neighbor not in distances or new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor, path + [neighbor]))

        return paths

    def find_path(self, start: str, goal: str) -> Optional[PathMorphism]:
        """Find shortest path from start to goal"""
        all_paths = self.find_shortest_paths(start)
        return all_paths.get(goal)

# Hierarchical Pathfinding

class HierarchicalPathfinder:
    """Hierarchical pathfinding with abstraction levels"""

    def __init__(self, graph: Dict[str, List[Tuple[str, float]]]):
        self.graph = graph
        self.clusters = self._create_clusters()
        self.abstract_graph = self._create_abstract_graph()

    def _create_clusters(self) -> Dict[str, str]:
        """Create node clusters for hierarchical abstraction"""
        # Simple clustering based on node prefixes
        clusters = {}
        for node in self.graph:
            # Extract cluster from node name (e.g., "A1" -> "A")
            cluster = node[0] if node else "default"
            clusters[node] = cluster
        return clusters

    def _create_abstract_graph(self) -> Dict[str, List[Tuple[str, float]]]:
        """Create abstract graph between clusters"""
        abstract = {}

        for node, neighbors in self.graph.items():
            cluster1 = self.clusters[node]

            for neighbor, cost in neighbors:
                cluster2 = self.clusters[neighbor]

                if cluster1 != cluster2:
                    if cluster1 not in abstract:
                        abstract[cluster1] = []

                    # Add or update edge between clusters
                    existing = False
                    for i, (c, w) in enumerate(abstract[cluster1]):
                        if c == cluster2:
                            # Keep minimum cost
                            abstract[cluster1][i] = (c, min(w, cost))
                            existing = True
                            break

                    if not existing:
                        abstract[cluster1].append((cluster2, cost))

        return abstract

    def find_path(self, start: str, goal: str) -> Optional[PathMorphism]:
        """Hierarchical pathfinding"""

        start_cluster = self.clusters[start]
        goal_cluster = self.clusters[goal]

        # If in same cluster, use direct search
        if start_cluster == goal_cluster:
            return self._find_path_within_cluster(start, goal, start_cluster)

        # Find abstract path between clusters
        abstract_search = CategoricalAStar(
            self.abstract_graph,
            lambda x, y: 0  # No heuristic for abstract level
        )

        abstract_path = abstract_search.find_path(start_cluster, goal_cluster)

        if not abstract_path:
            return None

        # Refine abstract path to concrete path
        return self._refine_path(start, goal, abstract_path.nodes)

    def _find_path_within_cluster(self, start: str, goal: str, cluster: str) -> Optional[PathMorphism]:
        """Find path within a single cluster"""
        # Filter graph to cluster nodes
        cluster_graph = {}
        for node, neighbors in self.graph.items():
            if self.clusters[node] == cluster:
                cluster_neighbors = [
                    (n, c) for n, c in neighbors
                    if self.clusters[n] == cluster
                ]
                if cluster_neighbors:
                    cluster_graph[node] = cluster_neighbors

        dijkstra = CategoricalDijkstra(cluster_graph)
        return dijkstra.find_path(start, goal)

    def _refine_path(self, start: str, goal: str, abstract_path: List[str]) -> Optional[PathMorphism]:
        """Refine abstract path to concrete path"""
        concrete_path = [start]
        current = start

        for i in range(len(abstract_path) - 1):
            current_cluster = abstract_path[i]
            next_cluster = abstract_path[i + 1]

            # Find boundary nodes
            boundary = self._find_boundary(current, current_cluster, next_cluster)

            if boundary:
                # Find path to boundary
                segment = self._find_path_within_cluster(current, boundary, current_cluster)
                if segment:
                    concrete_path.extend(segment.nodes[1:])
                    current = boundary

        # Final segment to goal
        final_segment = self._find_path_within_cluster(current, goal, self.clusters[goal])
        if final_segment:
            concrete_path.extend(final_segment.nodes[1:])

            # Calculate total cost
            total_cost = 0
            for i in range(len(concrete_path) - 1):
                for neighbor, cost in self.graph.get(concrete_path[i], []):
                    if neighbor == concrete_path[i + 1]:
                        total_cost += cost
                        break

            return PathMorphism(concrete_path, total_cost)

        return None

    def _find_boundary(self, from_node: str, from_cluster: str, to_cluster: str) -> Optional[str]:
        """Find boundary node between clusters"""
        # BFS to find closest boundary node
        queue = [(from_node, 0)]
        visited = {from_node}

        while queue:
            node, dist = queue.pop(0)

            for neighbor, _ in self.graph.get(node, []):
                if self.clusters[neighbor] == to_cluster:
                    return node  # Found boundary

                if neighbor not in visited and self.clusters[neighbor] == from_cluster:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))

        return None

# Demo and Testing

def create_test_graph() -> Dict[str, List[Tuple[str, float]]]:
    """Create a test graph with multiple clusters"""
    return {
        # Cluster A
        "A1": [("A2", 1), ("A3", 4), ("B1", 10)],
        "A2": [("A1", 1), ("A3", 2), ("A4", 5)],
        "A3": [("A1", 4), ("A2", 2), ("A4", 1)],
        "A4": [("A2", 5), ("A3", 1), ("B2", 3)],

        # Cluster B
        "B1": [("A1", 10), ("B2", 2), ("B3", 3)],
        "B2": [("A4", 3), ("B1", 2), ("B3", 1), ("C1", 7)],
        "B3": [("B1", 3), ("B2", 1), ("B4", 2)],
        "B4": [("B3", 2), ("C2", 5)],

        # Cluster C
        "C1": [("B2", 7), ("C2", 1), ("C3", 2)],
        "C2": [("B4", 5), ("C1", 1), ("C3", 1), ("C4", 3)],
        "C3": [("C1", 2), ("C2", 1), ("C4", 1)],
        "C4": [("C2", 3), ("C3", 1)],
    }

def euclidean_heuristic(node1: str, node2: str) -> float:
    """Simple heuristic based on node names"""
    # Extract numeric parts (assuming format like "A1", "B2", etc.)
    try:
        x1 = ord(node1[0]) - ord('A')
        y1 = int(node1[1]) - 1
        x2 = ord(node2[0]) - ord('A')
        y2 = int(node2[1]) - 1

        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    except:
        return 0  # Fallback for invalid node names

def main():
    """Demonstrate categorical pathfinding algorithms"""

    print("=" * 60)
    print("Categorical Pathfinding Demonstration")
    print("=" * 60)

    graph = create_test_graph()
    start = "A1"
    goal = "C4"

    # Test A*
    print("\n📍 A* Pathfinding")
    print("-" * 40)

    astar = CategoricalAStar(graph, euclidean_heuristic)
    start_time = time.time()
    path = astar.find_path(start, goal)
    elapsed = time.time() - start_time

    if path:
        print(f"Path found: {' → '.join(path.nodes)}")
        print(f"Total cost: {path.cost():.2f}")
        print(f"Time: {elapsed*1000:.2f}ms")
        print(f"Optimal: {astar.verify_optimality(path, goal)}")
    else:
        print("No path found")

    # Test Bidirectional Search
    print("\n🔄 Bidirectional Search")
    print("-" * 40)

    bidirectional = BidirectionalSearch(graph)
    start_time = time.time()
    path = bidirectional.search(start, goal)
    elapsed = time.time() - start_time

    if path:
        print(f"Path found: {' → '.join(path.nodes)}")
        print(f"Total cost: {path.cost():.2f}")
        print(f"Time: {elapsed*1000:.2f}ms")
    else:
        print("No path found")

    # Test Dijkstra
    print("\n📏 Dijkstra's Algorithm")
    print("-" * 40)

    dijkstra = CategoricalDijkstra(graph)
    start_time = time.time()
    path = dijkstra.find_path(start, goal)
    elapsed = time.time() - start_time

    if path:
        print(f"Path found: {' → '.join(path.nodes)}")
        print(f"Total cost: {path.cost():.2f}")
        print(f"Time: {elapsed*1000:.2f}ms")

        # Show all shortest paths from start
        all_paths = dijkstra.find_shortest_paths(start)
        print(f"\nAll shortest paths from {start}:")
        for dest, p in sorted(all_paths.items())[:5]:
            print(f"  To {dest}: cost = {p.cost():.2f}")
    else:
        print("No path found")

    # Test Hierarchical Pathfinding
    print("\n🏗️ Hierarchical Pathfinding")
    print("-" * 40)

    hierarchical = HierarchicalPathfinder(graph)
    start_time = time.time()
    path = hierarchical.find_path(start, goal)
    elapsed = time.time() - start_time

    if path:
        print(f"Path found: {' → '.join(path.nodes)}")
        print(f"Total cost: {path.cost():.2f}")
        print(f"Time: {elapsed*1000:.2f}ms")

        # Show cluster structure
        clusters = {}
        for node, cluster in hierarchical.clusters.items():
            if cluster not in clusters:
                clusters[cluster] = []
            clusters[cluster].append(node)

        print("\nCluster structure:")
        for cluster, nodes in sorted(clusters.items()):
            print(f"  {cluster}: {', '.join(sorted(nodes))}")
    else:
        print("No path found")

    # Compare all algorithms
    print("\n📊 Algorithm Comparison")
    print("-" * 40)

    algorithms = [
        ("A*", CategoricalAStar(graph, euclidean_heuristic)),
        ("Bidirectional", BidirectionalSearch(graph)),
        ("Dijkstra", CategoricalDijkstra(graph)),
        ("Hierarchical", HierarchicalPathfinder(graph))
    ]

    test_pairs = [("A1", "C4"), ("B2", "A3"), ("C1", "A4")]

    for start, goal in test_pairs:
        print(f"\nPath from {start} to {goal}:")

        for name, algo in algorithms:
            start_time = time.time()

            if hasattr(algo, 'find_path'):
                path = algo.find_path(start, goal)
            else:
                path = algo.search(start, goal)

            elapsed = time.time() - start_time

            if path:
                print(f"  {name:15} - Cost: {path.cost():6.2f}, Time: {elapsed*1000:6.2f}ms")
            else:
                print(f"  {name:15} - No path found")

    print("\n✨ Categorical Pathfinding Complete!")

if __name__ == "__main__":
    main()