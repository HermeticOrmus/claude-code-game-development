"""
RAG System Example Implementation
=================================

Complete example of a RAG (Retrieval-Augmented Generation) system
for documentation with vector search, semantic chunking, and query optimization.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

# For demonstration - in production, use actual libraries
# import faiss
# from sentence_transformers import SentenceTransformer
# import openai


@dataclass
class Document:
    """Document with metadata and embeddings."""
    id: str
    content: str
    embedding: np.ndarray
    metadata: Dict
    chunks: List[Dict] = None


class DocumentationRAGSystem:
    """
    Complete RAG system for documentation.

    This implements Level 4 (RAG-Based Documentation) with
    advanced vector search and semantic retrieval capabilities.
    """

    def __init__(self, embedding_dim: int = 384):
        """
        Initialize RAG system.

        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedding_dim = embedding_dim
        self.documents = {}
        self.embeddings = []
        self.index = None  # Would be FAISS index
        self.model = None  # Would be SentenceTransformer

        # Initialize components
        self._initialize_embedding_model()
        self._initialize_vector_index()

    def _initialize_embedding_model(self):
        """Initialize the embedding model."""
        # In production:
        # self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # For demonstration, simulate with random embeddings
        self.model = lambda text: np.random.randn(self.embedding_dim)

    def _initialize_vector_index(self):
        """Initialize vector search index."""
        # In production:
        # self.index = faiss.IndexFlatIP(self.embedding_dim)

        # For demonstration, use simple list
        self.index = []

    def add_documentation(self, doc_path: str, doc_type: str = "markdown"):
        """
        Add documentation to RAG system.

        Args:
            doc_path: Path to documentation file
            doc_type: Type of documentation (markdown, rst, html)

        Returns:
            Document ID
        """
        # Read document
        with open(doc_path, 'r') as f:
            content = f.read()

        # Generate document ID
        doc_id = hashlib.md5(content.encode()).hexdigest()[:16]

        # Chunk document
        chunks = self._chunk_document(content, doc_type)

        # Generate embeddings
        doc_embedding = self._generate_embedding(content)
        chunk_embeddings = [self._generate_embedding(c['content']) for c in chunks]

        # Create document object
        document = Document(
            id=doc_id,
            content=content,
            embedding=doc_embedding,
            metadata={
                'path': doc_path,
                'type': doc_type,
                'chunks': len(chunks),
                'length': len(content)
            },
            chunks=chunks
        )

        # Store document
        self.documents[doc_id] = document

        # Add to index
        self._add_to_index(doc_embedding, doc_id)

        # Add chunk embeddings
        for i, chunk_emb in enumerate(chunk_embeddings):
            chunk_id = f"{doc_id}_chunk_{i}"
            self._add_to_index(chunk_emb, chunk_id)

        return doc_id

    def _chunk_document(self, content: str, doc_type: str) -> List[Dict]:
        """
        Chunk document into semantic segments.

        Args:
            content: Document content
            doc_type: Document type

        Returns:
            List of chunks with metadata
        """
        chunks = []

        if doc_type == "markdown":
            # Split by headers
            lines = content.split('\n')
            current_chunk = []
            current_header = ""

            for line in lines:
                if line.startswith('#'):
                    # New section
                    if current_chunk:
                        chunks.append({
                            'content': '\n'.join(current_chunk),
                            'header': current_header,
                            'type': 'section'
                        })
                    current_header = line
                    current_chunk = [line]
                else:
                    current_chunk.append(line)

            # Add last chunk
            if current_chunk:
                chunks.append({
                    'content': '\n'.join(current_chunk),
                    'header': current_header,
                    'type': 'section'
                })

        elif doc_type == "code":
            # Split by functions/classes
            chunks = self._chunk_code(content)

        else:
            # Default: split by paragraphs
            paragraphs = content.split('\n\n')
            for i, para in enumerate(paragraphs):
                if para.strip():
                    chunks.append({
                        'content': para,
                        'type': 'paragraph',
                        'index': i
                    })

        return chunks

    def _chunk_code(self, content: str) -> List[Dict]:
        """Chunk code into logical segments."""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_type = None

        for line in lines:
            if line.strip().startswith('def '):
                if current_chunk:
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'type': current_type or 'code'
                    })
                current_chunk = [line]
                current_type = 'function'
            elif line.strip().startswith('class '):
                if current_chunk:
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'type': current_type or 'code'
                    })
                current_chunk = [line]
                current_type = 'class'
            else:
                current_chunk.append(line)

        # Add last chunk
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'type': current_type or 'code'
            })

        return chunks

    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        # In production: return self.model.encode(text)
        # For demonstration:
        return self.model(text)

    def _add_to_index(self, embedding: np.ndarray, doc_id: str):
        """Add embedding to vector index."""
        # Normalize for cosine similarity
        norm_embedding = embedding / np.linalg.norm(embedding)

        # In production: self.index.add(norm_embedding.reshape(1, -1))
        # For demonstration:
        self.index.append((doc_id, norm_embedding))
        self.embeddings.append(norm_embedding)

    def search(self, query: str, k: int = 5, search_type: str = "hybrid") -> List[Dict]:
        """
        Search documentation using RAG.

        Args:
            query: Search query
            k: Number of results
            search_type: Type of search (vector, keyword, hybrid)

        Returns:
            List of search results with scores
        """
        results = []

        if search_type == "vector" or search_type == "hybrid":
            vector_results = self._vector_search(query, k * 2)
            results.extend(vector_results)

        if search_type == "keyword" or search_type == "hybrid":
            keyword_results = self._keyword_search(query, k)
            results.extend(keyword_results)

        # Deduplicate and rank
        unique_results = self._deduplicate_results(results)
        ranked_results = self._rerank_results(unique_results, query)

        return ranked_results[:k]

    def _vector_search(self, query: str, k: int) -> List[Dict]:
        """Perform vector similarity search."""
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # Calculate similarities
        similarities = []
        for doc_id, embedding in self.index:
            similarity = np.dot(query_embedding, embedding)
            similarities.append({
                'doc_id': doc_id,
                'score': float(similarity),
                'type': 'vector'
            })

        # Sort by similarity
        similarities.sort(key=lambda x: x['score'], reverse=True)

        return similarities[:k]

    def _keyword_search(self, query: str, k: int) -> List[Dict]:
        """Perform keyword-based search."""
        query_terms = query.lower().split()
        results = []

        for doc_id, doc in self.documents.items():
            content_lower = doc.content.lower()

            # Calculate BM25-like score
            score = 0
            for term in query_terms:
                term_count = content_lower.count(term)
                if term_count > 0:
                    # Simplified BM25 formula
                    doc_len = len(content_lower.split())
                    avg_doc_len = 1000  # Average document length
                    k1 = 1.2
                    b = 0.75

                    tf = (term_count * (k1 + 1)) / (
                        term_count + k1 * (1 - b + b * doc_len / avg_doc_len)
                    )

                    # Simplified IDF
                    idf = np.log((len(self.documents) + 1) / (term_count + 0.5))

                    score += tf * idf

            if score > 0:
                results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'type': 'keyword'
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results."""
        seen = {}
        for result in results:
            doc_id = result['doc_id'].split('_chunk_')[0]  # Get base doc ID
            if doc_id not in seen or result['score'] > seen[doc_id]['score']:
                seen[doc_id] = result

        return list(seen.values())

    def _rerank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Rerank results using advanced scoring."""
        reranked = []

        for result in results:
            doc_id = result['doc_id'].split('_chunk_')[0]
            if doc_id in self.documents:
                doc = self.documents[doc_id]

                # Calculate additional features
                features = {
                    'base_score': result['score'],
                    'length_penalty': 1.0 / (1 + np.log(len(doc.content) + 1)),
                    'type_boost': 1.2 if result['type'] == 'vector' else 1.0,
                    'freshness': self._calculate_freshness(doc),
                    'relevance': self._calculate_relevance(doc, query)
                }

                # Combine features
                final_score = (
                    features['base_score'] * features['type_boost'] *
                    features['freshness'] * features['relevance']
                )

                reranked.append({
                    **result,
                    'final_score': final_score,
                    'features': features
                })

        reranked.sort(key=lambda x: x['final_score'], reverse=True)
        return reranked

    def _calculate_freshness(self, doc: Document) -> float:
        """Calculate document freshness score."""
        # Simplified - would use actual timestamps
        return 0.9

    def _calculate_relevance(self, doc: Document, query: str) -> float:
        """Calculate query-document relevance."""
        query_terms = set(query.lower().split())
        doc_terms = set(doc.content.lower().split())
        intersection = query_terms & doc_terms

        if not query_terms:
            return 0.0

        return len(intersection) / len(query_terms)

    def generate_response(self, query: str, context: List[Dict]) -> str:
        """
        Generate response using retrieved context.

        Args:
            query: User query
            context: Retrieved documents

        Returns:
            Generated response
        """
        if not context:
            return "No relevant documentation found for your query."

        # Prepare context for generation
        context_text = "\n\n".join([
            f"Source {i+1}:\n{self.documents[r['doc_id'].split('_chunk_')[0]].content[:500]}"
            for i, r in enumerate(context[:3])
        ])

        # In production, use LLM for generation
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[
        #         {"role": "system", "content": "You are a documentation assistant."},
        #         {"role": "user", "content": f"Context:\n{context_text}\n\nQuery: {query}"}
        #     ]
        # )

        # For demonstration, create structured response
        response = f"""Based on the documentation:

**Query:** {query}

**Answer:**
The relevant documentation sections have been found. Here's a summary:

{context_text[:300]}...

**Related Sections:**"""

        for i, result in enumerate(context[:3]):
            doc_id = result['doc_id'].split('_chunk_')[0]
            doc = self.documents.get(doc_id)
            if doc:
                response += f"\n{i+1}. {doc.metadata.get('path', 'Unknown')} (Score: {result['score']:.2f})"

        return response

    def update_document(self, doc_id: str, new_content: str):
        """
        Update existing document.

        Args:
            doc_id: Document ID
            new_content: New content
        """
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")

        # Update document
        old_doc = self.documents[doc_id]
        new_embedding = self._generate_embedding(new_content)

        # Create updated document
        updated_doc = Document(
            id=doc_id,
            content=new_content,
            embedding=new_embedding,
            metadata={**old_doc.metadata, 'updated': True}
        )

        self.documents[doc_id] = updated_doc

        # Update index
        self._update_index(doc_id, new_embedding)

    def _update_index(self, doc_id: str, new_embedding: np.ndarray):
        """Update embedding in index."""
        # Find and update in index
        for i, (idx_id, _) in enumerate(self.index):
            if idx_id == doc_id:
                norm_embedding = new_embedding / np.linalg.norm(new_embedding)
                self.index[i] = (doc_id, norm_embedding)
                self.embeddings[i] = norm_embedding
                break

    def export_index(self, path: str):
        """Export index for backup or sharing."""
        export_data = {
            'documents': {
                doc_id: {
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'embedding': doc.embedding.tolist()
                }
                for doc_id, doc in self.documents.items()
            },
            'index': [(doc_id, emb.tolist()) for doc_id, emb in self.index],
            'config': {
                'embedding_dim': self.embedding_dim
            }
        }

        with open(path, 'w') as f:
            json.dump(export_data, f, indent=2)

    def import_index(self, path: str):
        """Import previously exported index."""
        with open(path, 'r') as f:
            export_data = json.load(f)

        # Restore documents
        self.documents = {}
        for doc_id, doc_data in export_data['documents'].items():
            self.documents[doc_id] = Document(
                id=doc_id,
                content=doc_data['content'],
                embedding=np.array(doc_data['embedding']),
                metadata=doc_data['metadata']
            )

        # Restore index
        self.index = [
            (doc_id, np.array(emb))
            for doc_id, emb in export_data['index']
        ]
        self.embeddings = [emb for _, emb in self.index]

        # Restore config
        self.embedding_dim = export_data['config']['embedding_dim']


# Example usage and testing
def demo_rag_system():
    """Demonstrate RAG system capabilities."""

    # Initialize RAG system
    rag = DocumentationRAGSystem(embedding_dim=384)

    # Create sample documentation
    sample_docs = [
        {
            'path': 'api_reference.md',
            'content': """# API Reference

## Authentication

### Getting Started
To use the API, you need to authenticate using an API key.

```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY'
}
```

### Endpoints

#### GET /api/users
Retrieve list of users.

**Parameters:**
- limit: Maximum number of users (default: 100)
- offset: Pagination offset (default: 0)

**Response:**
```json
{
    "users": [...],
    "total": 1000
}
```
"""
        },
        {
            'path': 'tutorial.md',
            'content': """# Tutorial: Getting Started

## Installation

Install the framework using pip:

```bash
pip install doc-framework
```

## Quick Start

Here's a simple example:

```python
from doc_framework import DocumentationSystem

# Initialize the system
doc_sys = DocumentationSystem()

# Generate documentation
result = doc_sys.generate('my_module.py')
print(result)
```

## Advanced Usage

For advanced features, configure the system:

```python
config = {
    'rag_enabled': True,
    'vector_dim': 768
}

doc_sys = DocumentationSystem(config=config)
```
"""
        }
    ]

    # Add documents to RAG system
    print("Adding documents to RAG system...")
    for doc_info in sample_docs:
        # Save to temporary file
        temp_path = Path(f"/tmp/{doc_info['path']}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, 'w') as f:
            f.write(doc_info['content'])

        # Add to RAG
        doc_id = rag.add_documentation(str(temp_path), doc_type="markdown")
        print(f"Added {doc_info['path']} with ID: {doc_id}")

    # Test queries
    test_queries = [
        "How do I authenticate with the API?",
        "What are the installation steps?",
        "Show me the user endpoint",
        "How to configure advanced features?"
    ]

    print("\n" + "="*60)
    print("Testing RAG queries:")
    print("="*60)

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)

        # Search
        results = rag.search(query, k=3, search_type="hybrid")

        # Generate response
        response = rag.generate_response(query, results)
        print(response)

    # Export index
    export_path = "/tmp/rag_index.json"
    rag.export_index(export_path)
    print(f"\n\nIndex exported to: {export_path}")

    return rag


if __name__ == "__main__":
    # Run demonstration
    rag_system = demo_rag_system()

    # Additional testing
    print("\n" + "="*60)
    print("Additional RAG Features:")
    print("="*60)

    # Test document update
    doc_ids = list(rag_system.documents.keys())
    if doc_ids:
        doc_id = doc_ids[0]
        print(f"\nUpdating document {doc_id}...")
        rag_system.update_document(doc_id, "Updated content for testing.")
        print("Document updated successfully!")

    # Show statistics
    print(f"\nRAG System Statistics:")
    print(f"- Total documents: {len(rag_system.documents)}")
    print(f"- Index size: {len(rag_system.index)}")
    print(f"- Embedding dimension: {rag_system.embedding_dim}")