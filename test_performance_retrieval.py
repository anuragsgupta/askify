"""
Performance tests for retrieval layer (without LLM).

Tests vector search and metadata retrieval performance with varying
collection sizes to identify bottlenecks and optimization opportunities.
"""

import os
import time
import tempfile
import shutil
from typing import List, Dict, Any

import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from storage.chroma_store import init_chroma_collection, upsert_chunks, DocumentChunk, query_chunks


def get_embed_model():
    """Get embedding model based on configured provider."""
    provider = os.getenv('LLM_PROVIDER', 'gemini')
    
    if provider == 'ollama':
        from llama_index.embeddings.ollama import OllamaEmbedding
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        model = os.getenv('OLLAMA_EMBED_MODEL', 'nomic-embed-text:latest')
        return OllamaEmbedding(model_name=model, base_url=base_url)
    
    elif provider == 'gemini':
        from llama_index.embeddings.gemini import GeminiEmbedding
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            pytest.skip("GEMINI_API_KEY not set")
        # Use embedding-001 which is supported
        return GeminiEmbedding(model_name="models/embedding-001", api_key=api_key)
    
    else:
        pytest.skip(f"Unknown provider: {provider}")


def generate_test_chunks(count: int, embed_model) -> List[DocumentChunk]:
    """
    Generate test document chunks with embeddings.
    
    Args:
        count: Number of chunks to generate
        embed_model: Embedding model to use
        
    Returns:
        List of DocumentChunk objects with embeddings
    """
    chunks = []
    
    # Create diverse content to simulate real documents
    doc_types = ['policy', 'excel', 'email']
    topics = [
        'refund policy', 'shipping policy', 'pricing information',
        'customer support', 'product specifications', 'discount approval',
        'return window', 'warranty terms', 'payment methods'
    ]
    
    for i in range(count):
        doc_type = doc_types[i % len(doc_types)]
        topic = topics[i % len(topics)]
        
        # Generate content
        content = f"Document {i}: This is information about {topic}. "
        content += f"It contains important details for employees to reference. "
        content += f"The policy states that customers should follow standard procedures. "
        content += f"For more information, contact the relevant department."
        
        # Create metadata based on doc_type
        metadata = {
            'source': f'doc_{i}.pdf',
            'doc_type': doc_type,
            'doc_date': f'2024-01-{(i % 28) + 1:02d}T00:00:00'
        }
        
        if doc_type == 'policy':
            metadata.update({
                'section_title': f'Section {topic}',
                'section_number': f'{(i % 10) + 1}.{(i % 5) + 1}',
                'page_number': (i % 50) + 1
            })
        elif doc_type == 'excel':
            metadata.update({
                'sheet_name': f'Sheet{(i % 4) + 1}',
                'row_number': (i % 100) + 1,
                'client': f'Client_{i % 20}'
            })
        elif doc_type == 'email':
            metadata.update({
                'sender': f'user{i % 10}@company.com',
                'subject': f'RE: {topic}',
                'thread_id': f'thread_{i % 30}'
            })
        
        # Generate embedding
        embedding = embed_model.get_text_embedding(content)
        
        chunk = DocumentChunk(
            id=f'perf_chunk_{i}',
            content=content,
            embedding=embedding,
            metadata=metadata
        )
        chunks.append(chunk)
    
    return chunks


class TestRetrievalPerformance:
    """Test retrieval performance without LLM generation."""
    
    @pytest.fixture
    def temp_chroma_dir(self):
        """Create temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp(prefix='chroma_perf_ret_')
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_retrieval_performance_100_chunks(self, temp_chroma_dir):
        """
        Test retrieval performance with 100 chunks.
        
        Measures vector search + metadata retrieval time.
        Target: < 1 second for retrieval only
        """
        print("\n" + "="*70)
        print("Retrieval Performance Test: 100 chunks")
        print("="*70)
        
        # Initialize ChromaDB
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        embed_model = get_embed_model()
        
        # Generate and insert test data
        print("Generating 100 test chunks...")
        start_gen = time.time()
        chunks = generate_test_chunks(100, embed_model)
        gen_time = time.time() - start_gen
        print(f"  Generation time: {gen_time:.2f}s")
        
        print("Inserting chunks into ChromaDB...")
        start_insert = time.time()
        upsert_chunks(collection, chunks)
        insert_time = time.time() - start_insert
        print(f"  Insertion time: {insert_time:.2f}s")
        
        # Test retrieval queries
        test_queries = [
            "refund policy",
            "pricing information",
            "shipping terms",
            "warranty information",
            "payment methods"
        ]
        
        print(f"\nExecuting {len(test_queries)} retrieval queries...")
        retrieval_times = []
        
        for i, query in enumerate(test_queries, 1):
            start_query = time.time()
            results = query_chunks(collection, query, n_results=5)
            query_time = time.time() - start_query
            retrieval_times.append(query_time)
            
            print(f"  Query {i}: {query_time:.3f}s - '{query}' ({len(results)} results)")
            
            # Verify we got results
            assert len(results) > 0, f"Query '{query}' should return results"
        
        # Calculate statistics
        avg_time = sum(retrieval_times) / len(retrieval_times)
        max_time = max(retrieval_times)
        min_time = min(retrieval_times)
        
        print(f"\nRetrieval Performance Summary (100 chunks):")
        print(f"  Average retrieval time: {avg_time:.3f}s")
        print(f"  Min retrieval time: {min_time:.3f}s")
        print(f"  Max retrieval time: {max_time:.3f}s")
        print(f"  Target: < 1.0s")
        
        # Assert performance target
        assert avg_time < 2, f"Average retrieval time {avg_time:.3f}s exceeds 2s threshold"
        
        if avg_time < 0.5:
            print(f"  ✓ EXCELLENT: Vector search is very fast")
        elif avg_time < 1:
            print(f"  ✓ GOOD: Vector search performance is acceptable")
        else:
            print(f"  ⚠ WARNING: Vector search may need optimization")
    
    def test_retrieval_performance_1000_chunks(self, temp_chroma_dir):
        """
        Test retrieval performance with 1000 chunks.
        
        Measures vector search + metadata retrieval time.
        Target: < 1 second for retrieval only
        """
        print("\n" + "="*70)
        print("Retrieval Performance Test: 1000 chunks")
        print("="*70)
        
        # Initialize ChromaDB
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        embed_model = get_embed_model()
        
        # Generate and insert test data in batches
        print("Generating 1000 test chunks...")
        start_gen = time.time()
        
        batch_size = 100
        for batch_num in range(10):
            start_idx = batch_num * batch_size
            chunks = generate_test_chunks(batch_size, embed_model)
            
            # Update IDs to be unique across batches
            for i, chunk in enumerate(chunks):
                chunk.id = f'perf_chunk_{start_idx + i}'
            
            upsert_chunks(collection, chunks)
            print(f"  Inserted batch {batch_num + 1}/10")
        
        gen_time = time.time() - start_gen
        print(f"  Total generation + insertion time: {gen_time:.2f}s")
        
        # Test retrieval queries
        test_queries = [
            "refund policy",
            "pricing information",
            "shipping terms"
        ]
        
        print(f"\nExecuting {len(test_queries)} retrieval queries...")
        retrieval_times = []
        
        for i, query in enumerate(test_queries, 1):
            start_query = time.time()
            results = query_chunks(collection, query, n_results=5)
            query_time = time.time() - start_query
            retrieval_times.append(query_time)
            
            print(f"  Query {i}: {query_time:.3f}s - '{query}' ({len(results)} results)")
            
            # Verify we got results
            assert len(results) > 0, f"Query '{query}' should return results"
        
        # Calculate statistics
        avg_time = sum(retrieval_times) / len(retrieval_times)
        max_time = max(retrieval_times)
        min_time = min(retrieval_times)
        
        print(f"\nRetrieval Performance Summary (1000 chunks):")
        print(f"  Average retrieval time: {avg_time:.3f}s")
        print(f"  Min retrieval time: {min_time:.3f}s")
        print(f"  Max retrieval time: {max_time:.3f}s")
        print(f"  Target: < 1.0s")
        
        # Assert performance target
        assert avg_time < 2, f"Average retrieval time {avg_time:.3f}s exceeds 2s threshold"
        
        if avg_time < 0.5:
            print(f"  ✓ EXCELLENT: Vector search scales well")
        elif avg_time < 1:
            print(f"  ✓ GOOD: Vector search performance is acceptable")
        else:
            print(f"  ⚠ WARNING: Vector search may need optimization")
    
    @pytest.mark.slow
    def test_retrieval_performance_10000_chunks(self, temp_chroma_dir):
        """
        Test retrieval performance with 10000 chunks.
        
        This test is marked as slow and may take several minutes.
        Measures vector search + metadata retrieval time.
        Target: < 1 second for retrieval only
        """
        print("\n" + "="*70)
        print("Retrieval Performance Test: 10000 chunks (SLOW TEST)")
        print("="*70)
        
        # Initialize ChromaDB
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        embed_model = get_embed_model()
        
        # Generate and insert test data in batches
        print("Generating 10000 test chunks (this will take a while)...")
        start_gen = time.time()
        
        batch_size = 100
        num_batches = 100
        
        for batch_num in range(num_batches):
            start_idx = batch_num * batch_size
            chunks = generate_test_chunks(batch_size, embed_model)
            
            # Update IDs to be unique across batches
            for i, chunk in enumerate(chunks):
                chunk.id = f'perf_chunk_{start_idx + i}'
            
            upsert_chunks(collection, chunks)
            
            if (batch_num + 1) % 10 == 0:
                print(f"  Inserted batch {batch_num + 1}/{num_batches}")
        
        gen_time = time.time() - start_gen
        print(f"  Total generation + insertion time: {gen_time:.2f}s ({gen_time/60:.1f} minutes)")
        
        # Test retrieval queries
        test_queries = [
            "refund policy",
            "pricing information",
            "shipping terms"
        ]
        
        print(f"\nExecuting {len(test_queries)} retrieval queries...")
        retrieval_times = []
        
        for i, query in enumerate(test_queries, 1):
            start_query = time.time()
            results = query_chunks(collection, query, n_results=5)
            query_time = time.time() - start_query
            retrieval_times.append(query_time)
            
            print(f"  Query {i}: {query_time:.3f}s - '{query}' ({len(results)} results)")
            
            # Verify we got results
            assert len(results) > 0, f"Query '{query}' should return results"
        
        # Calculate statistics
        avg_time = sum(retrieval_times) / len(retrieval_times)
        max_time = max(retrieval_times)
        min_time = min(retrieval_times)
        
        print(f"\nRetrieval Performance Summary (10000 chunks):")
        print(f"  Average retrieval time: {avg_time:.3f}s")
        print(f"  Min retrieval time: {min_time:.3f}s")
        print(f"  Max retrieval time: {max_time:.3f}s")
        print(f"  Target: < 1.0s")
        
        # Assert performance target
        assert avg_time < 2, f"Average retrieval time {avg_time:.3f}s exceeds 2s threshold"
        
        if avg_time < 0.5:
            print(f"  ✓ EXCELLENT: Vector search scales excellently to large collections")
        elif avg_time < 1:
            print(f"  ✓ GOOD: Vector search performance is acceptable at scale")
        else:
            print(f"  ⚠ WARNING: Vector search may need optimization for large collections")
        
        # Performance analysis
        print(f"\nPerformance Analysis:")
        print(f"  Collection size: 10000 chunks")
        print(f"  Retrieval performance: ", end="")
        
        if avg_time < 0.5:
            print("EXCELLENT - ChromaDB scales well")
        elif avg_time < 1:
            print("GOOD - acceptable for production use")
        else:
            print("NEEDS OPTIMIZATION - consider indexing improvements")


class TestPerformanceScaling:
    """Test how performance scales with collection size."""
    
    @pytest.fixture
    def temp_chroma_dir(self):
        """Create temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp(prefix='chroma_perf_scale_')
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_performance_scaling_analysis(self, temp_chroma_dir):
        """
        Analyze how retrieval performance scales with collection size.
        
        Tests multiple collection sizes and reports scaling characteristics.
        """
        print("\n" + "="*70)
        print("Performance Scaling Analysis")
        print("="*70)
        
        # Initialize ChromaDB
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        embed_model = get_embed_model()
        
        # Test different collection sizes
        test_sizes = [50, 100, 200, 500]
        results = []
        
        print(f"\nTesting retrieval performance at different scales...")
        
        for size in test_sizes:
            print(f"\n--- Testing with {size} chunks ---")
            
            # Generate and insert chunks
            chunks = []
            for batch_start in range(0, size, 50):
                batch_size = min(50, size - batch_start)
                batch_chunks = generate_test_chunks(batch_size, embed_model)
                
                # Update IDs
                for i, chunk in enumerate(batch_chunks):
                    chunk.id = f'scale_chunk_{batch_start + i}'
                
                chunks.extend(batch_chunks)
            
            upsert_chunks(collection, chunks)
            print(f"  Inserted {size} chunks")
            
            # Test retrieval
            query = "refund policy"
            start = time.time()
            query_results = query_chunks(collection, query, n_results=5)
            query_time = time.time() - start
            
            results.append({
                'size': size,
                'time': query_time,
                'results': len(query_results)
            })
            
            print(f"  Query time: {query_time:.3f}s")
        
        # Analyze scaling
        print(f"\n" + "="*70)
        print("Scaling Analysis Results")
        print("="*70)
        print(f"\n{'Size':<10} {'Time (s)':<12} {'Results':<10} {'Time/100 chunks':<15}")
        print("-" * 50)
        
        for result in results:
            time_per_100 = (result['time'] / result['size']) * 100
            print(f"{result['size']:<10} {result['time']:<12.3f} {result['results']:<10} {time_per_100:<15.3f}")
        
        # Check if performance degrades significantly
        if len(results) >= 2:
            first_time = results[0]['time']
            last_time = results[-1]['time']
            size_ratio = results[-1]['size'] / results[0]['size']
            time_ratio = last_time / first_time if first_time > 0 else 0
            
            print(f"\nScaling Characteristics:")
            print(f"  Collection size increased by: {size_ratio:.1f}x")
            print(f"  Query time increased by: {time_ratio:.1f}x")
            
            if time_ratio < size_ratio * 0.5:
                print(f"  ✓ EXCELLENT: Sub-linear scaling (very efficient)")
            elif time_ratio < size_ratio:
                print(f"  ✓ GOOD: Better than linear scaling")
            elif time_ratio < size_ratio * 1.5:
                print(f"  ⚠ ACCEPTABLE: Approximately linear scaling")
            else:
                print(f"  ⚠ WARNING: Worse than linear scaling - optimization needed")


if __name__ == '__main__':
    # Run with: pytest test_performance_retrieval.py -v -s
    # Run slow tests: pytest test_performance_retrieval.py -v -s -m slow
    pytest.main([__file__, '-v', '-s'])
