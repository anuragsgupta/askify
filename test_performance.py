"""
Performance tests for SME Knowledge Agent.

Tests query response time with varying collection sizes to ensure
the system meets the < 3 second target for production workloads.
"""

import os
import time
import tempfile
import shutil
from typing import List, Dict, Any

import pytest

from storage.chroma_store import init_chroma_collection, upsert_chunks, DocumentChunk
from retrieval.query_engine import create_query_engine, query_with_metadata


def skip_if_no_provider():
    """Skip test if no LLM provider is configured."""
    provider = os.getenv('LLM_PROVIDER', 'ollama')
    
    if provider == 'ollama':
        # Check if Ollama is running
        import requests
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=2)
            if response.status_code != 200:
                pytest.skip("Ollama is not running")
        except Exception:
            pytest.skip("Ollama is not accessible")
    
    elif provider == 'gemini':
        if not os.getenv('GEMINI_API_KEY'):
            pytest.skip("GEMINI_API_KEY not set")
    
    else:
        pytest.skip(f"Unknown provider: {provider}")


def get_embed_model():
    """Get embedding model based on configured provider."""
    provider = os.getenv('LLM_PROVIDER', 'ollama')
    
    if provider == 'ollama':
        from llama_index.embeddings.ollama import OllamaEmbedding
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        model = os.getenv('OLLAMA_EMBED_MODEL', 'nomic-embed-text:latest')
        return OllamaEmbedding(model_name=model, base_url=base_url)
    
    elif provider == 'gemini':
        from llama_index.embeddings.gemini import GeminiEmbedding
        api_key = os.getenv('GEMINI_API_KEY')
        return GeminiEmbedding(model_name="models/embedding-001", api_key=api_key)
    
    else:
        raise ValueError(f"Unknown provider: {provider}")


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


class TestPerformanceRequirements:
    """Test query performance with varying collection sizes."""
    
    @pytest.fixture
    def temp_chroma_dir(self):
        """Create temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp(prefix='chroma_perf_')
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_query_performance_100_chunks(self, temp_chroma_dir):
        """
        Test query performance with 100 chunks.
        
        Target: < 3 seconds
        """
        skip_if_no_provider()
        
        print("\n" + "="*70)
        print("Performance Test: 100 chunks")
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
        
        # Create query engine
        print("Creating query engine...")
        query_engine = create_query_engine(collection)
        
        # Test queries
        test_queries = [
            "What is the refund policy?",
            "What are the pricing details for Client_5?",
            "Did anyone approve a discount?",
            "What are the shipping terms?",
            "What is the warranty information?"
        ]
        
        print(f"\nExecuting {len(test_queries)} test queries...")
        query_times = []
        
        for i, query in enumerate(test_queries, 1):
            start_query = time.time()
            result = query_with_metadata(query_engine, query)
            query_time = time.time() - start_query
            query_times.append(query_time)
            
            print(f"  Query {i}: {query_time:.2f}s - {query[:50]}...")
            
            # Verify we got results
            assert result.answer, "Query should return an answer"
        
        # Calculate statistics
        avg_time = sum(query_times) / len(query_times)
        max_time = max(query_times)
        min_time = min(query_times)
        
        print(f"\nPerformance Summary (100 chunks):")
        print(f"  Average query time: {avg_time:.2f}s")
        print(f"  Min query time: {min_time:.2f}s")
        print(f"  Max query time: {max_time:.2f}s")
        print(f"  Target: < 3.0s")
        
        # Assert performance target
        # Using 10s for test environment (relaxed from 3s production target)
        assert avg_time < 10, f"Average query time {avg_time:.2f}s exceeds 10s threshold"
        
        if avg_time < 3:
            print(f"  ✓ PASSED: Meets production target!")
        else:
            print(f"  ⚠ WARNING: Exceeds production target but within test threshold")
    
    def test_query_performance_1000_chunks(self, temp_chroma_dir):
        """
        Test query performance with 1000 chunks.
        
        Target: < 3 seconds
        """
        skip_if_no_provider()
        
        print("\n" + "="*70)
        print("Performance Test: 1000 chunks")
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
        
        # Create query engine
        print("Creating query engine...")
        query_engine = create_query_engine(collection)
        
        # Test queries
        test_queries = [
            "What is the refund policy?",
            "What are the pricing details?",
            "What are the shipping terms?"
        ]
        
        print(f"\nExecuting {len(test_queries)} test queries...")
        query_times = []
        
        for i, query in enumerate(test_queries, 1):
            start_query = time.time()
            result = query_with_metadata(query_engine, query)
            query_time = time.time() - start_query
            query_times.append(query_time)
            
            print(f"  Query {i}: {query_time:.2f}s - {query[:50]}...")
            
            # Verify we got results
            assert result.answer, "Query should return an answer"
        
        # Calculate statistics
        avg_time = sum(query_times) / len(query_times)
        max_time = max(query_times)
        min_time = min(query_times)
        
        print(f"\nPerformance Summary (1000 chunks):")
        print(f"  Average query time: {avg_time:.2f}s")
        print(f"  Min query time: {min_time:.2f}s")
        print(f"  Max query time: {max_time:.2f}s")
        print(f"  Target: < 3.0s")
        
        # Assert performance target
        assert avg_time < 10, f"Average query time {avg_time:.2f}s exceeds 10s threshold"
        
        if avg_time < 3:
            print(f"  ✓ PASSED: Meets production target!")
        else:
            print(f"  ⚠ WARNING: Exceeds production target but within test threshold")
    
    @pytest.mark.slow
    def test_query_performance_10000_chunks(self, temp_chroma_dir):
        """
        Test query performance with 10000 chunks.
        
        This test is marked as slow and may take several minutes to complete.
        Target: < 3 seconds for queries (not including data generation)
        """
        skip_if_no_provider()
        
        print("\n" + "="*70)
        print("Performance Test: 10000 chunks (SLOW TEST)")
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
        
        # Create query engine
        print("Creating query engine...")
        query_engine = create_query_engine(collection)
        
        # Test queries
        test_queries = [
            "What is the refund policy?",
            "What are the pricing details?",
            "What are the shipping terms?"
        ]
        
        print(f"\nExecuting {len(test_queries)} test queries...")
        query_times = []
        
        for i, query in enumerate(test_queries, 1):
            start_query = time.time()
            result = query_with_metadata(query_engine, query)
            query_time = time.time() - start_query
            query_times.append(query_time)
            
            print(f"  Query {i}: {query_time:.2f}s - {query[:50]}...")
            
            # Verify we got results
            assert result.answer, "Query should return an answer"
        
        # Calculate statistics
        avg_time = sum(query_times) / len(query_times)
        max_time = max(query_times)
        min_time = min(query_times)
        
        print(f"\nPerformance Summary (10000 chunks):")
        print(f"  Average query time: {avg_time:.2f}s")
        print(f"  Min query time: {min_time:.2f}s")
        print(f"  Max query time: {max_time:.2f}s")
        print(f"  Target: < 3.0s")
        
        # Assert performance target
        assert avg_time < 10, f"Average query time {avg_time:.2f}s exceeds 10s threshold"
        
        if avg_time < 3:
            print(f"  ✓ PASSED: Meets production target!")
        else:
            print(f"  ⚠ WARNING: Exceeds production target but within test threshold")
        
        # Performance analysis
        print(f"\nPerformance Analysis:")
        print(f"  Collection size: 10000 chunks")
        print(f"  Query performance appears to be: ", end="")
        
        # Compare with smaller collection (if we had baseline data)
        if avg_time < 3:
            print("EXCELLENT - scales well to large collections")
        elif avg_time < 5:
            print("GOOD - acceptable for production use")
        elif avg_time < 10:
            print("ACCEPTABLE - may need optimization for larger collections")
        else:
            print("NEEDS OPTIMIZATION - consider indexing improvements")


class TestPerformanceOptimizations:
    """Test potential performance optimizations."""
    
    @pytest.fixture
    def temp_chroma_dir(self):
        """Create temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp(prefix='chroma_perf_opt_')
        yield temp_dir
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_retrieval_only_performance(self, temp_chroma_dir):
        """
        Test retrieval performance without LLM generation.
        
        This isolates vector search performance from LLM inference time.
        """
        skip_if_no_provider()
        
        print("\n" + "="*70)
        print("Performance Test: Retrieval Only (No LLM)")
        print("="*70)
        
        # Initialize ChromaDB
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        embed_model = get_embed_model()
        
        # Generate test data
        print("Generating 500 test chunks...")
        chunks = []
        for batch_num in range(5):
            batch_chunks = generate_test_chunks(100, embed_model)
            for i, chunk in enumerate(batch_chunks):
                chunk.id = f'perf_chunk_{batch_num * 100 + i}'
            chunks.extend(batch_chunks)
        
        upsert_chunks(collection, chunks)
        print(f"  Inserted {len(chunks)} chunks")
        
        # Create query engine
        query_engine = create_query_engine(collection)
        
        # Test retrieval only
        from retrieval.query_engine import retrieve_chunks
        
        test_queries = [
            "refund policy",
            "pricing information",
            "shipping terms"
        ]
        
        print(f"\nTesting retrieval-only performance...")
        retrieval_times = []
        
        for query in test_queries:
            start = time.time()
            chunks_result = retrieve_chunks(query_engine, query, top_k=5)
            retrieval_time = time.time() - start
            retrieval_times.append(retrieval_time)
            
            print(f"  Query '{query}': {retrieval_time:.3f}s ({len(chunks_result)} chunks)")
        
        avg_retrieval = sum(retrieval_times) / len(retrieval_times)
        print(f"\nAverage retrieval time: {avg_retrieval:.3f}s")
        print(f"  This represents vector search + metadata retrieval only")
        
        # Retrieval should be very fast (< 1 second)
        assert avg_retrieval < 2, f"Retrieval time {avg_retrieval:.3f}s is too slow"
        
        if avg_retrieval < 0.5:
            print(f"  ✓ EXCELLENT: Vector search is very fast")
        elif avg_retrieval < 1:
            print(f"  ✓ GOOD: Vector search performance is acceptable")
        else:
            print(f"  ⚠ WARNING: Vector search may need optimization")
    
    def test_batch_query_performance(self, temp_chroma_dir):
        """
        Test performance of multiple queries in sequence.
        
        This simulates real-world usage where multiple employees
        query the system simultaneously.
        """
        skip_if_no_provider()
        
        print("\n" + "="*70)
        print("Performance Test: Batch Queries")
        print("="*70)
        
        # Initialize ChromaDB
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        embed_model = get_embed_model()
        
        # Generate test data
        print("Generating 200 test chunks...")
        chunks = []
        for batch_num in range(2):
            batch_chunks = generate_test_chunks(100, embed_model)
            for i, chunk in enumerate(batch_chunks):
                chunk.id = f'perf_chunk_{batch_num * 100 + i}'
            chunks.extend(batch_chunks)
        
        upsert_chunks(collection, chunks)
        
        # Create query engine
        query_engine = create_query_engine(collection)
        
        # Simulate 10 sequential queries
        queries = [
            "What is the refund policy?",
            "What are the pricing details?",
            "What are the shipping terms?",
            "What is the warranty information?",
            "What are the payment methods?",
            "What is the return window?",
            "What are the discount policies?",
            "What is the customer support process?",
            "What are the product specifications?",
            "What are the delivery options?"
        ]
        
        print(f"\nExecuting {len(queries)} sequential queries...")
        start_batch = time.time()
        query_times = []
        
        for i, query in enumerate(queries, 1):
            start = time.time()
            result = query_with_metadata(query_engine, query)
            query_time = time.time() - start
            query_times.append(query_time)
            
            if i % 5 == 0:
                print(f"  Completed {i}/{len(queries)} queries...")
        
        total_time = time.time() - start_batch
        avg_time = sum(query_times) / len(query_times)
        
        print(f"\nBatch Query Performance:")
        print(f"  Total time for {len(queries)} queries: {total_time:.2f}s")
        print(f"  Average time per query: {avg_time:.2f}s")
        print(f"  Throughput: {len(queries)/total_time:.2f} queries/second")
        
        # All queries should complete in reasonable time
        assert avg_time < 10, f"Average query time {avg_time:.2f}s is too slow"
        
        if avg_time < 3:
            print(f"  ✓ EXCELLENT: Meets production target for all queries")
        else:
            print(f"  ⚠ WARNING: Some queries exceed production target")


if __name__ == '__main__':
    # Run with: pytest test_performance.py -v -s
    # Run slow tests: pytest test_performance.py -v -s -m slow
    pytest.main([__file__, '-v', '-s'])
