"""
Vector Search Example Implementation
====================================

Demonstrates advanced vector search capabilities for documentation
with multiple index types, optimization strategies, and performance benchmarks.
"""

import numpy as np
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import heapq


@dataclass
class VectorDocument:
    """Document with vector representation."""
    id: str
    vector: np.ndarray
    metadata: Dict
    content: str


class VectorSearchEngine:
    """
    Advanced vector search engine for documentation.

    Implements multiple indexing strategies for optimal performance
    across different dataset sizes and query patterns.
    """

    def __init__(self, dimension: int = 384):
        """
        Initialize vector search engine.

        Args:
            dimension: Vector dimension
        """
        self.dimension = dimension
        self.documents = {}

        # Different index types
        self.flat_index = FlatIndex(dimension)
        self.lsh_index = LSHIndex(dimension, num_tables=10, hash_size=8)
        self.hnsw_index = HNSWIndex(dimension, M=16, ef_construction=200)
        self.pq_index = ProductQuantizationIndex(dimension, n_subquantizers=16)

        # Statistics
        self.stats = {
            'searches': 0,
            'total_search_time': 0,
            'index_updates': 0
        }

    def add_document(self, doc: VectorDocument, index_types: List[str] = None):
        """
        Add document to specified indexes.

        Args:
            doc: Document to add
            index_types: List of index types to use (default: all)
        """
        if index_types is None:
            index_types = ['flat', 'lsh', 'hnsw', 'pq']

        # Store document
        self.documents[doc.id] = doc

        # Add to specified indexes
        if 'flat' in index_types:
            self.flat_index.add(doc)
        if 'lsh' in index_types:
            self.lsh_index.add(doc)
        if 'hnsw' in index_types:
            self.hnsw_index.add(doc)
        if 'pq' in index_types:
            self.pq_index.add(doc)

        self.stats['index_updates'] += 1

    def search(self, query_vector: np.ndarray, k: int = 10,
              index_type: str = 'auto') -> List[Tuple[str, float]]:
        """
        Search for similar documents.

        Args:
            query_vector: Query vector
            k: Number of results
            index_type: Index to use (auto selects based on data size)

        Returns:
            List of (doc_id, similarity) tuples
        """
        start_time = time.time()

        # Select index based on strategy
        if index_type == 'auto':
            index_type = self._select_index()

        # Perform search
        if index_type == 'flat':
            results = self.flat_index.search(query_vector, k)
        elif index_type == 'lsh':
            results = self.lsh_index.search(query_vector, k)
        elif index_type == 'hnsw':
            results = self.hnsw_index.search(query_vector, k)
        elif index_type == 'pq':
            results = self.pq_index.search(query_vector, k)
        else:
            raise ValueError(f"Unknown index type: {index_type}")

        # Update statistics
        search_time = time.time() - start_time
        self.stats['searches'] += 1
        self.stats['total_search_time'] += search_time

        return results

    def _select_index(self) -> str:
        """Select optimal index based on data characteristics."""
        num_docs = len(self.documents)

        if num_docs < 1000:
            # Small dataset - use exact search
            return 'flat'
        elif num_docs < 10000:
            # Medium dataset - use LSH
            return 'lsh'
        elif num_docs < 100000:
            # Large dataset - use HNSW
            return 'hnsw'
        else:
            # Very large dataset - use PQ for memory efficiency
            return 'pq'

    def hybrid_search(self, query_vector: np.ndarray, query_text: str,
                     k: int = 10, alpha: float = 0.7) -> List[Dict]:
        """
        Hybrid search combining vector and text similarity.

        Args:
            query_vector: Query vector
            query_text: Query text
            k: Number of results
            alpha: Weight for vector similarity (vs text similarity)

        Returns:
            Combined search results
        """
        # Vector search
        vector_results = self.search(query_vector, k * 2)

        # Text search (BM25-like)
        text_results = self._text_search(query_text, k * 2)

        # Combine results
        combined_scores = defaultdict(float)

        for doc_id, score in vector_results:
            combined_scores[doc_id] += alpha * score

        for doc_id, score in text_results:
            combined_scores[doc_id] += (1 - alpha) * score

        # Sort by combined score
        sorted_results = sorted(combined_scores.items(),
                               key=lambda x: x[1], reverse=True)

        # Format results
        results = []
        for doc_id, score in sorted_results[:k]:
            if doc_id in self.documents:
                results.append({
                    'id': doc_id,
                    'score': score,
                    'content': self.documents[doc_id].content[:200],
                    'metadata': self.documents[doc_id].metadata
                })

        return results

    def _text_search(self, query: str, k: int) -> List[Tuple[str, float]]:
        """Simple text search implementation."""
        query_terms = set(query.lower().split())
        results = []

        for doc_id, doc in self.documents.items():
            doc_terms = set(doc.content.lower().split())
            intersection = query_terms & doc_terms

            if intersection:
                # Simple scoring based on term overlap
                score = len(intersection) / len(query_terms)
                results.append((doc_id, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def get_statistics(self) -> Dict:
        """Get search engine statistics."""
        stats = dict(self.stats)
        stats['num_documents'] = len(self.documents)
        stats['avg_search_time'] = (
            stats['total_search_time'] / stats['searches']
            if stats['searches'] > 0 else 0
        )
        return stats


class FlatIndex:
    """Flat (brute-force) index for exact search."""

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors = []
        self.ids = []

    def add(self, doc: VectorDocument):
        """Add document to index."""
        self.vectors.append(doc.vector / np.linalg.norm(doc.vector))
        self.ids.append(doc.id)

    def search(self, query: np.ndarray, k: int) -> List[Tuple[str, float]]:
        """Search for k nearest neighbors."""
        if not self.vectors:
            return []

        # Normalize query
        query_norm = query / np.linalg.norm(query)

        # Compute similarities
        similarities = []
        for i, vec in enumerate(self.vectors):
            similarity = np.dot(query_norm, vec)
            similarities.append((self.ids[i], float(similarity)))

        # Sort and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]


class LSHIndex:
    """Locality Sensitive Hashing index for approximate search."""

    def __init__(self, dimension: int, num_tables: int = 10, hash_size: int = 8):
        self.dimension = dimension
        self.num_tables = num_tables
        self.hash_size = hash_size

        # Random projection matrices for each table
        self.projection_matrices = [
            np.random.randn(hash_size, dimension)
            for _ in range(num_tables)
        ]

        # Hash tables
        self.tables = [defaultdict(list) for _ in range(num_tables)]
        self.documents = {}

    def _hash(self, vector: np.ndarray, table_idx: int) -> str:
        """Compute hash for vector."""
        projection = self.projection_matrices[table_idx]
        hash_vec = np.sign(np.dot(projection, vector))
        return ''.join(['1' if x > 0 else '0' for x in hash_vec])

    def add(self, doc: VectorDocument):
        """Add document to LSH index."""
        self.documents[doc.id] = doc

        # Add to each hash table
        for i in range(self.num_tables):
            hash_key = self._hash(doc.vector, i)
            self.tables[i][hash_key].append(doc.id)

    def search(self, query: np.ndarray, k: int) -> List[Tuple[str, float]]:
        """Search using LSH."""
        candidates = set()

        # Get candidates from each table
        for i in range(self.num_tables):
            hash_key = self._hash(query, i)
            candidates.update(self.tables[i][hash_key])

        # Compute exact similarities for candidates
        query_norm = query / np.linalg.norm(query)
        similarities = []

        for doc_id in candidates:
            if doc_id in self.documents:
                doc_vec = self.documents[doc_id].vector
                doc_norm = doc_vec / np.linalg.norm(doc_vec)
                similarity = np.dot(query_norm, doc_norm)
                similarities.append((doc_id, float(similarity)))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]


class HNSWIndex:
    """Hierarchical Navigable Small World index for fast approximate search."""

    def __init__(self, dimension: int, M: int = 16, ef_construction: int = 200):
        self.dimension = dimension
        self.M = M  # Number of connections per node
        self.ef_construction = ef_construction  # Size of dynamic candidate list
        self.ef_search = 50  # Size of search candidate list

        self.graph = defaultdict(dict)  # level -> node -> neighbors
        self.vectors = {}
        self.entry_point = None
        self.node_levels = {}

    def _get_random_level(self) -> int:
        """Select level for new node."""
        level = 0
        while np.random.random() < 0.5:
            level += 1
        return level

    def _distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute distance between vectors."""
        # Using 1 - cosine similarity as distance
        norm1 = vec1 / np.linalg.norm(vec1)
        norm2 = vec2 / np.linalg.norm(vec2)
        return 1.0 - np.dot(norm1, norm2)

    def add(self, doc: VectorDocument):
        """Add document to HNSW index."""
        self.vectors[doc.id] = doc.vector

        # Assign level
        level = self._get_random_level()
        self.node_levels[doc.id] = level

        if self.entry_point is None:
            self.entry_point = doc.id
            for lv in range(level + 1):
                self.graph[lv][doc.id] = set()
        else:
            # Find nearest neighbors
            self._insert_node(doc.id, level)

    def _insert_node(self, node_id: str, level: int):
        """Insert node into graph."""
        # Simplified HNSW insertion
        for lv in range(level + 1):
            if lv not in self.graph:
                self.graph[lv] = {}

            # Find M nearest neighbors at this level
            candidates = self._search_layer(node_id, self.M, lv)

            # Add bidirectional edges
            self.graph[lv][node_id] = set(candidates)
            for neighbor in candidates:
                if neighbor in self.graph[lv]:
                    self.graph[lv][neighbor].add(node_id)

    def _search_layer(self, query_id: str, k: int, level: int) -> List[str]:
        """Search for nearest neighbors in a specific layer."""
        if not self.graph[level]:
            return []

        query_vec = self.vectors[query_id]
        visited = set()
        candidates = [(self._distance(query_vec, self.vectors[self.entry_point]),
                      self.entry_point)]
        w = [candidates[0]]

        while candidates:
            current_dist, current = heapq.heappop(candidates)

            if current_dist > w[0][0]:
                break

            if current in visited:
                continue

            visited.add(current)

            # Check neighbors
            if current in self.graph[level]:
                for neighbor in self.graph[level][current]:
                    if neighbor not in visited:
                        dist = self._distance(query_vec, self.vectors[neighbor])
                        heapq.heappush(candidates, (dist, neighbor))

                        if dist < w[0][0] or len(w) < k:
                            heapq.heappush(w, (-dist, neighbor))
                            if len(w) > k:
                                heapq.heappop(w)

        return [node for _, node in sorted(w, key=lambda x: -x[0])]

    def search(self, query: np.ndarray, k: int) -> List[Tuple[str, float]]:
        """Search for k nearest neighbors."""
        if not self.vectors:
            return []

        # Start from entry point
        visited = set()
        candidates = []
        w = []

        # Search from top level to bottom
        current_nearest = [self.entry_point]

        for level in range(max(self.graph.keys()), -1, -1):
            for node in current_nearest:
                if node not in visited:
                    visited.add(node)
                    dist = self._distance(query, self.vectors[node])
                    heapq.heappush(candidates, (dist, node))
                    heapq.heappush(w, (-dist, node))

                    if level in self.graph and node in self.graph[level]:
                        for neighbor in self.graph[level][node]:
                            if neighbor not in visited:
                                dist = self._distance(query, self.vectors[neighbor])
                                heapq.heappush(candidates, (dist, neighbor))

            # Keep only ef_search best candidates
            candidates = heapq.nsmallest(self.ef_search, candidates)

        # Get final results
        results = []
        for dist, node in heapq.nsmallest(k, w, key=lambda x: -x[0]):
            similarity = 1.0 - dist  # Convert distance back to similarity
            results.append((node, similarity))

        return results


class ProductQuantizationIndex:
    """Product Quantization index for memory-efficient search."""

    def __init__(self, dimension: int, n_subquantizers: int = 8):
        self.dimension = dimension
        self.n_subquantizers = n_subquantizers
        self.subvector_dim = dimension // n_subquantizers

        # Codebooks for each subquantizer
        self.codebooks = []
        self.codes = []
        self.ids = []

        # Initialize codebooks with random centroids
        for _ in range(n_subquantizers):
            centroids = np.random.randn(256, self.subvector_dim)
            self.codebooks.append(centroids)

    def add(self, doc: VectorDocument):
        """Add document to PQ index."""
        # Split vector into subvectors
        subvectors = np.array_split(doc.vector, self.n_subquantizers)

        # Quantize each subvector
        codes = []
        for i, subvec in enumerate(subvectors):
            # Find nearest centroid
            distances = np.linalg.norm(self.codebooks[i] - subvec, axis=1)
            code = np.argmin(distances)
            codes.append(code)

        self.codes.append(codes)
        self.ids.append(doc.id)

    def search(self, query: np.ndarray, k: int) -> List[Tuple[str, float]]:
        """Search using product quantization."""
        if not self.codes:
            return []

        # Split query into subvectors
        query_subvectors = np.array_split(query, self.n_subquantizers)

        # Precompute distances to all centroids
        distance_tables = []
        for i, subvec in enumerate(query_subvectors):
            distances = np.linalg.norm(self.codebooks[i] - subvec, axis=1)
            distance_tables.append(distances)

        # Compute approximate distances to all documents
        results = []
        for idx, codes in enumerate(self.codes):
            # Sum distances from lookup tables
            distance = sum(distance_tables[i][code]
                          for i, code in enumerate(codes))
            # Convert to similarity
            similarity = 1.0 / (1.0 + distance)
            results.append((self.ids[idx], similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]


# Benchmarking functions
def benchmark_indexes(n_documents: int = 1000, dimension: int = 384,
                     n_queries: int = 100):
    """
    Benchmark different index types.

    Args:
        n_documents: Number of documents
        dimension: Vector dimension
        n_queries: Number of test queries
    """
    print(f"Benchmarking with {n_documents} documents, "
          f"{dimension} dimensions, {n_queries} queries\n")

    # Generate random documents
    documents = []
    for i in range(n_documents):
        doc = VectorDocument(
            id=f"doc_{i}",
            vector=np.random.randn(dimension),
            metadata={'index': i},
            content=f"Document {i} content"
        )
        documents.append(doc)

    # Generate random queries
    queries = [np.random.randn(dimension) for _ in range(n_queries)]

    # Test each index type
    index_types = {
        'Flat (Exact)': FlatIndex(dimension),
        'LSH': LSHIndex(dimension, num_tables=10, hash_size=8),
        'HNSW': HNSWIndex(dimension, M=16, ef_construction=200),
        'PQ': ProductQuantizationIndex(dimension, n_subquantizers=16)
    }

    results = {}

    for name, index in index_types.items():
        print(f"\nTesting {name}...")

        # Build index
        start_time = time.time()
        for doc in documents:
            index.add(doc)
        build_time = time.time() - start_time

        # Search queries
        search_times = []
        for query in queries:
            start_time = time.time()
            results_list = index.search(query, k=10)
            search_time = time.time() - start_time
            search_times.append(search_time)

        # Calculate statistics
        avg_search_time = np.mean(search_times)
        std_search_time = np.std(search_times)

        results[name] = {
            'build_time': build_time,
            'avg_search_time': avg_search_time * 1000,  # Convert to ms
            'std_search_time': std_search_time * 1000,
            'queries_per_sec': 1.0 / avg_search_time if avg_search_time > 0 else 0
        }

        print(f"  Build time: {build_time:.3f}s")
        print(f"  Avg search time: {avg_search_time*1000:.2f}ms ± {std_search_time*1000:.2f}ms")
        print(f"  Queries/sec: {results[name]['queries_per_sec']:.1f}")

    return results


# Example usage
def demo_vector_search():
    """Demonstrate vector search capabilities."""

    print("="*60)
    print("Vector Search Engine Demo")
    print("="*60)

    # Initialize search engine
    engine = VectorSearchEngine(dimension=384)

    # Add sample documents
    sample_docs = [
        "Introduction to machine learning and neural networks",
        "Deep learning fundamentals and architectures",
        "Natural language processing with transformers",
        "Computer vision and convolutional networks",
        "Reinforcement learning and policy optimization",
        "Graph neural networks for structured data",
        "Time series analysis with recurrent networks",
        "Generative models and variational autoencoders",
        "Transfer learning and fine-tuning strategies",
        "Multi-modal learning and cross-domain applications"
    ]

    print("\nAdding documents to search engine...")
    for i, content in enumerate(sample_docs):
        # Generate random embedding (in practice, use actual embeddings)
        vector = np.random.randn(384)

        # Add noise to make similar documents cluster
        if "learning" in content.lower():
            vector[0:50] += 0.5
        if "network" in content.lower():
            vector[50:100] += 0.5

        doc = VectorDocument(
            id=f"doc_{i}",
            vector=vector,
            metadata={'index': i, 'category': 'ML'},
            content=content
        )

        engine.add_document(doc)

    print(f"Added {len(sample_docs)} documents")

    # Test different search strategies
    print("\n" + "="*60)
    print("Testing Search Strategies")
    print("="*60)

    # Generate query vector
    query_vector = np.random.randn(384)
    query_vector[0:50] += 0.5  # Bias towards "learning" documents

    index_types = ['flat', 'lsh', 'hnsw', 'pq']

    for index_type in index_types:
        print(f"\n{index_type.upper()} Index Search:")
        print("-" * 40)

        results = engine.search(query_vector, k=5, index_type=index_type)

        for doc_id, similarity in results:
            doc = engine.documents[doc_id]
            print(f"  [{similarity:.3f}] {doc.content[:50]}...")

    # Test hybrid search
    print("\n" + "="*60)
    print("Hybrid Search (Vector + Text)")
    print("="*60)

    query_text = "neural networks learning"
    results = engine.hybrid_search(query_vector, query_text, k=5, alpha=0.7)

    for result in results:
        print(f"  [{result['score']:.3f}] {result['content'][:50]}...")

    # Show statistics
    print("\n" + "="*60)
    print("Search Engine Statistics")
    print("="*60)

    stats = engine.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    # Run demo
    demo_vector_search()

    # Run benchmarks
    print("\n" + "="*60)
    print("Running Performance Benchmarks")
    print("="*60)

    benchmark_results = benchmark_indexes(
        n_documents=1000,
        dimension=384,
        n_queries=100
    )

    print("\n" + "="*60)
    print("Benchmark Summary")
    print("="*60)

    for index_name, metrics in benchmark_results.items():
        print(f"\n{index_name}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.3f}")