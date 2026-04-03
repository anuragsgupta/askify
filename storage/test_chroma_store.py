"""Unit tests for ChromaDB storage layer."""

import tempfile
from datetime import datetime

import pytest

from storage.chroma_store import (
    DocumentChunk,
    init_chroma_collection,
    upsert_chunks,
    query_chunks,
    get_collection_stats
)


@pytest.fixture
def temp_chroma_dir():
    """Creates a temporary directory for ChromaDB persistence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_pdf_chunk():
    """Creates a sample PDF chunk for testing."""
    return DocumentChunk(
        id="pdf_refund_policy_section_3_2",
        content="Refund Policy Section 3.2: Customers may request refunds within 60 days of purchase.",
        embedding=[0.1] * 384,  # Mock embedding
        metadata={
            "source": "Refund_Policy_v2_2024.pdf",
            "doc_type": "policy",
            "doc_date": datetime(2024, 3, 15),
            "section_title": "Returns and Refunds",
            "section_number": "3.2",
            "page_number": 5
        }
    )


@pytest.fixture
def sample_excel_chunk():
    """Creates a sample Excel chunk for testing."""
    return DocumentChunk(
        id="excel_pricing_q1_row_42",
        content="Client: Acme Corp, Product: Widget Pro, Price: $500.00, Discount: 10%",
        embedding=[0.2] * 384,  # Mock embedding
        metadata={
            "source": "Pricing_2024.xlsx",
            "doc_type": "excel",
            "doc_date": datetime(2024, 1, 1),
            "sheet_name": "Q1",
            "row_number": 42,
            "client": "Acme Corp"
        }
    )


@pytest.fixture
def sample_email_chunk():
    """Creates a sample Email chunk for testing."""
    return DocumentChunk(
        id="email_thread_abc123_msg_1",
        content="Hi team, please note that our refund policy has been updated to 60 days.",
        embedding=[0.3] * 384,  # Mock embedding
        metadata={
            "source": "policy_update.eml",
            "doc_type": "email",
            "doc_date": datetime(2024, 2, 1),
            "sender": "john@company.com",
            "subject": "Policy Update - Refunds",
            "thread_id": "abc123",
            "client_keyword": None
        }
    )


class TestInitialization:
    """Tests for ChromaDB initialization."""
    
    def test_init_creates_directory(self, temp_chroma_dir):
        """Initialization creates persist directory if it doesn't exist."""
        import os
        persist_path = os.path.join(temp_chroma_dir, "new_db")
        
        client, collection = init_chroma_collection(persist_directory=persist_path)
        
        assert os.path.exists(persist_path)
        assert collection is not None
    
    def test_init_returns_same_collection_on_reopen(self, temp_chroma_dir):
        """Reopening same directory returns existing collection."""
        # Create collection
        client1, collection1 = init_chroma_collection(persist_directory=temp_chroma_dir)
        name1 = collection1.name
        
        # Reopen
        client2, collection2 = init_chroma_collection(persist_directory=temp_chroma_dir)
        name2 = collection2.name
        
        assert name1 == name2
    
    def test_init_with_custom_collection_name(self, temp_chroma_dir):
        """Initialization with custom collection name works."""
        client, collection = init_chroma_collection(
            persist_directory=temp_chroma_dir,
            collection_name="custom_collection"
        )
        
        assert collection.name == "custom_collection"


class TestUpsertOperations:
    """Tests for upsert operations."""
    
    def test_upsert_single_pdf_chunk(self, temp_chroma_dir, sample_pdf_chunk):
        """Upserting single PDF chunk works correctly."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        upsert_chunks(collection, [sample_pdf_chunk])
        
        assert collection.count() == 1
        results = collection.get(ids=[sample_pdf_chunk.id])
        assert results['documents'][0] == sample_pdf_chunk.content
    
    def test_upsert_multiple_chunks_different_types(
        self, temp_chroma_dir, sample_pdf_chunk, sample_excel_chunk, sample_email_chunk
    ):
        """Upserting multiple chunks of different types works."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        chunks = [sample_pdf_chunk, sample_excel_chunk, sample_email_chunk]
        upsert_chunks(collection, chunks)
        
        assert collection.count() == 3
        
        # Verify each chunk
        for chunk in chunks:
            results = collection.get(ids=[chunk.id])
            assert len(results['ids']) == 1
            assert results['metadatas'][0]['doc_type'] == chunk.metadata['doc_type']
    
    def test_upsert_with_duplicate_id_updates_content(self, temp_chroma_dir, sample_pdf_chunk):
        """Upserting with duplicate ID updates existing chunk."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        # Insert original
        upsert_chunks(collection, [sample_pdf_chunk])
        
        # Update with same ID
        updated_chunk = DocumentChunk(
            id=sample_pdf_chunk.id,
            content="Updated refund policy: 90 days now!",
            embedding=sample_pdf_chunk.embedding,
            metadata=sample_pdf_chunk.metadata
        )
        upsert_chunks(collection, [updated_chunk])
        
        # Verify only one chunk exists with updated content
        assert collection.count() == 1
        results = collection.get(ids=[sample_pdf_chunk.id])
        assert results['documents'][0] == "Updated refund policy: 90 days now!"
    
    def test_upsert_with_none_metadata_values_skipped(self, temp_chroma_dir):
        """Upserting chunk with None metadata values skips them."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        chunk = DocumentChunk(
            id="test_chunk",
            content="Test content",
            embedding=[0.1] * 384,
            metadata={
                "source": "test.pdf",
                "doc_type": "policy",
                "doc_date": datetime(2024, 1, 1),
                "optional_field": None  # Should be skipped
            }
        )
        
        upsert_chunks(collection, [chunk])
        
        results = collection.get(ids=["test_chunk"])
        stored_metadata = results['metadatas'][0]
        
        # Verify None value was skipped
        assert "optional_field" not in stored_metadata
    
    def test_upsert_without_embeddings_works(self, temp_chroma_dir, sample_pdf_chunk):
        """Upserting without pre-computed embeddings works (ChromaDB generates them)."""
        pytest.skip("Skipping test that requires embedding generation - too slow for unit tests")


class TestQueryOperations:
    """Tests for query operations."""
    
    def test_query_returns_relevant_chunks(
        self, temp_chroma_dir, sample_pdf_chunk, sample_excel_chunk
    ):
        """Querying returns relevant chunks."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        upsert_chunks(collection, [sample_pdf_chunk, sample_excel_chunk])
        
        # Query for refund-related content
        results = query_chunks(collection, "refund policy", n_results=2)
        
        assert len(results) > 0
        assert all('content' in r for r in results)
        assert all('metadata' in r for r in results)
    
    def test_query_with_doc_type_filter(
        self, temp_chroma_dir, sample_pdf_chunk, sample_excel_chunk, sample_email_chunk
    ):
        """Querying with doc_type filter returns only matching types."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        chunks = [sample_pdf_chunk, sample_excel_chunk, sample_email_chunk]
        upsert_chunks(collection, chunks)
        
        # Query with filter for only Excel
        results = query_chunks(collection, "pricing", n_results=5, doc_type_filter="excel")
        
        # Verify all results are Excel type
        for result in results:
            assert result['metadata']['doc_type'] == "excel"
    
    def test_query_empty_collection_returns_empty(self, temp_chroma_dir):
        """Querying empty collection returns empty list."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        results = query_chunks(collection, "test query", n_results=5)
        
        assert results == []
    
    def test_query_respects_n_results_limit(
        self, temp_chroma_dir, sample_pdf_chunk, sample_excel_chunk, sample_email_chunk
    ):
        """Query respects n_results parameter."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        chunks = [sample_pdf_chunk, sample_excel_chunk, sample_email_chunk]
        upsert_chunks(collection, chunks)
        
        # Query with limit of 2
        results = query_chunks(collection, "policy", n_results=2)
        
        assert len(results) <= 2


class TestCollectionStats:
    """Tests for collection statistics."""
    
    def test_stats_empty_collection(self, temp_chroma_dir):
        """Stats for empty collection returns zero counts."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        stats = get_collection_stats(collection)
        
        assert stats['total_chunks'] == 0
    
    def test_stats_with_chunks(
        self, temp_chroma_dir, sample_pdf_chunk, sample_excel_chunk, sample_email_chunk
    ):
        """Stats returns correct total count."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        chunks = [sample_pdf_chunk, sample_excel_chunk, sample_email_chunk]
        upsert_chunks(collection, chunks)
        
        stats = get_collection_stats(collection)
        
        assert stats['total_chunks'] == 3


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_upsert_chunk_with_special_characters_in_metadata(self, temp_chroma_dir):
        """Upserting chunk with special characters in metadata works."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        chunk = DocumentChunk(
            id="special_chars_test",
            content="Test content with special chars: @#$%",
            embedding=[0.1] * 384,
            metadata={
                "source": "file_with_special_chars_@#$.pdf",
                "doc_type": "policy",
                "doc_date": datetime(2024, 1, 1),
                "section_title": "Section with émojis 🎉 and ñ"
            }
        )
        
        upsert_chunks(collection, [chunk])
        
        results = collection.get(ids=["special_chars_test"])
        assert len(results['ids']) == 1
    
    def test_upsert_chunk_with_very_long_content(self, temp_chroma_dir):
        """Upserting chunk with very long content works."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        long_content = "A" * 10000  # 10k characters
        
        chunk = DocumentChunk(
            id="long_content_test",
            content=long_content,
            embedding=[0.1] * 384,
            metadata={
                "source": "long_doc.pdf",
                "doc_type": "policy",
                "doc_date": datetime(2024, 1, 1)
            }
        )
        
        upsert_chunks(collection, [chunk])
        
        results = collection.get(ids=["long_content_test"])
        assert results['documents'][0] == long_content
    
    def test_query_with_invalid_doc_type_filter_returns_empty(self, temp_chroma_dir, sample_pdf_chunk):
        """Querying with invalid doc_type filter returns empty results."""
        client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
        upsert_chunks(collection, [sample_pdf_chunk])
        
        # Query with non-existent doc_type
        results = query_chunks(collection, "test", n_results=5, doc_type_filter="invalid_type")
        
        assert results == []
