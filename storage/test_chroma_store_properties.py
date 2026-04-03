"""Property-based tests for ChromaDB storage layer using Hypothesis."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from storage.chroma_store import (
    DocumentChunk,
    init_chroma_collection,
    upsert_chunks,
    query_chunks,
    get_collection_stats
)


# Custom strategies for generating test data
@st.composite
def pdf_metadata(draw):
    """Generates valid PDF metadata."""
    return {
        "source": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='._-'))),
        "doc_type": "policy",
        "doc_date": draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2025, 12, 31))),
        "section_title": draw(st.text(min_size=3, max_size=100)),
        "section_number": draw(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',), whitelist_characters='.'))),
        "page_number": draw(st.integers(min_value=1, max_value=1000))
    }


@st.composite
def excel_metadata(draw):
    """Generates valid Excel metadata."""
    metadata = {
        "source": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='._-'))),
        "doc_type": "excel",
        "doc_date": draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2025, 12, 31))),
        "sheet_name": draw(st.text(min_size=1, max_size=50)),
        "row_number": draw(st.integers(min_value=1, max_value=10000))
    }
    # Client is optional
    if draw(st.booleans()):
        metadata["client"] = draw(st.text(min_size=3, max_size=50))
    return metadata


@st.composite
def email_metadata(draw):
    """Generates valid Email metadata."""
    metadata = {
        "source": draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='._-'))),
        "doc_type": "email",
        "doc_date": draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2025, 12, 31))),
        "sender": draw(st.emails()),
        "subject": draw(st.text(min_size=1, max_size=200)),
        "thread_id": draw(st.text(min_size=10, max_size=100))
    }
    # Client keyword is optional
    if draw(st.booleans()):
        metadata["client_keyword"] = draw(st.text(min_size=3, max_size=50))
    return metadata


@st.composite
def document_chunk(draw, metadata_strategy):
    """Generates a DocumentChunk with specified metadata strategy."""
    chunk_id = draw(st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-')))
    content = draw(st.text(min_size=10, max_size=500))
    metadata = draw(metadata_strategy)
    
    # Generate random embedding vector (384 dimensions for text-embedding-3-small)
    embedding = draw(st.lists(st.floats(min_value=-1.0, max_value=1.0), min_size=384, max_size=384))
    
    return DocumentChunk(
        id=chunk_id,
        content=content,
        embedding=embedding,
        metadata=metadata
    )


class TestMetadataPreservation:
    """
    Property 2: Metadata preservation across storage
    Validates: Requirements 1.2, 2.2, 3.3
    
    Verifies that all metadata fields are preserved when storing and retrieving
    chunks from ChromaDB, regardless of document type.
    """
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    @given(chunk=document_chunk(pdf_metadata()))
    def test_pdf_metadata_preserved(self, chunk):
        """PDF metadata is fully preserved through storage and retrieval."""
        # Create temporary directory for this test
        with tempfile.TemporaryDirectory() as temp_chroma_dir:
            # Initialize collection
            client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
            # Upsert chunk
            upsert_chunks(collection, [chunk])
            
            # Retrieve chunk by ID
            results = collection.get(ids=[chunk.id])
            
            # Verify chunk was stored
            assert len(results['ids']) == 1
            assert results['ids'][0] == chunk.id
            
            # Verify content preserved
            assert results['documents'][0] == chunk.content
            
            # Verify metadata preserved (datetime converted to ISO string)
            stored_metadata = results['metadatas'][0]
            assert stored_metadata['source'] == chunk.metadata['source']
            assert stored_metadata['doc_type'] == chunk.metadata['doc_type']
            assert stored_metadata['doc_date'] == chunk.metadata['doc_date'].isoformat()
            assert stored_metadata['section_title'] == chunk.metadata['section_title']
            assert stored_metadata['section_number'] == chunk.metadata['section_number']
            assert stored_metadata['page_number'] == chunk.metadata['page_number']
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    @given(chunk=document_chunk(excel_metadata()))
    def test_excel_metadata_preserved(self, chunk):
        """Excel metadata is fully preserved through storage and retrieval."""
        with tempfile.TemporaryDirectory() as temp_chroma_dir:
            # Initialize collection
            client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
            # Upsert chunk
            upsert_chunks(collection, [chunk])
            
            # Retrieve chunk by ID
            results = collection.get(ids=[chunk.id])
            
            # Verify chunk was stored
            assert len(results['ids']) == 1
            assert results['ids'][0] == chunk.id
            
            # Verify content preserved
            assert results['documents'][0] == chunk.content
            
            # Verify metadata preserved
            stored_metadata = results['metadatas'][0]
            assert stored_metadata['source'] == chunk.metadata['source']
            assert stored_metadata['doc_type'] == chunk.metadata['doc_type']
            assert stored_metadata['doc_date'] == chunk.metadata['doc_date'].isoformat()
            assert stored_metadata['sheet_name'] == chunk.metadata['sheet_name']
            assert stored_metadata['row_number'] == chunk.metadata['row_number']
            
            # Client is optional
            if 'client' in chunk.metadata:
                assert stored_metadata['client'] == chunk.metadata['client']
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    @given(chunk=document_chunk(email_metadata()))
    def test_email_metadata_preserved(self, chunk):
        """Email metadata is fully preserved through storage and retrieval."""
        with tempfile.TemporaryDirectory() as temp_chroma_dir:
            # Initialize collection
            client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
            # Upsert chunk
            upsert_chunks(collection, [chunk])
            
            # Retrieve chunk by ID
            results = collection.get(ids=[chunk.id])
            
            # Verify chunk was stored
            assert len(results['ids']) == 1
            assert results['ids'][0] == chunk.id
            
            # Verify content preserved
            assert results['documents'][0] == chunk.content
            
            # Verify metadata preserved
            stored_metadata = results['metadatas'][0]
            assert stored_metadata['source'] == chunk.metadata['source']
            assert stored_metadata['doc_type'] == chunk.metadata['doc_type']
            assert stored_metadata['doc_date'] == chunk.metadata['doc_date'].isoformat()
            assert stored_metadata['sender'] == chunk.metadata['sender']
            assert stored_metadata['subject'] == chunk.metadata['subject']
            assert stored_metadata['thread_id'] == chunk.metadata['thread_id']
            
            # Client keyword is optional
            if 'client_keyword' in chunk.metadata:
                assert stored_metadata['client_keyword'] == chunk.metadata['client_keyword']
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=5)
    @given(chunks=st.lists(
        st.one_of(
            document_chunk(pdf_metadata()),
            document_chunk(excel_metadata()),
            document_chunk(email_metadata())
        ),
        min_size=1,
        max_size=10,
        unique_by=lambda c: c.id
    ))
    def test_mixed_doc_types_metadata_preserved(self, chunks):
        """Metadata is preserved for mixed document types in same collection."""
        with tempfile.TemporaryDirectory() as temp_chroma_dir:
            # Initialize collection
            client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
            # Upsert all chunks
            upsert_chunks(collection, chunks)
            
            # Verify all chunks stored
            assert collection.count() == len(chunks)
            
            # Retrieve and verify each chunk
            for chunk in chunks:
                results = collection.get(ids=[chunk.id])
                assert len(results['ids']) == 1
                assert results['documents'][0] == chunk.content
                
                # Verify doc_type preserved
                stored_metadata = results['metadatas'][0]
                assert stored_metadata['doc_type'] == chunk.metadata['doc_type']


class TestUpsertBehavior:
    """Tests for upsert behavior with duplicates and edge cases."""
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    @given(chunk=document_chunk(pdf_metadata()))
    def test_upsert_duplicate_id_updates(self, chunk):
        """Upserting with duplicate ID updates existing chunk."""
        with tempfile.TemporaryDirectory() as temp_chroma_dir:
            # Initialize collection
            client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
        
            # Upsert original chunk
            upsert_chunks(collection, [chunk])
            
            # Create updated chunk with same ID but different content
            updated_chunk = DocumentChunk(
                id=chunk.id,
                content="Updated content",
                embedding=chunk.embedding,
                metadata=chunk.metadata
            )
            
            # Upsert updated chunk
            upsert_chunks(collection, [updated_chunk])
            
            # Verify only one chunk exists
            assert collection.count() == 1
            
            # Verify content was updated
            results = collection.get(ids=[chunk.id])
            assert results['documents'][0] == "Updated content"
    
    def test_upsert_empty_list_raises_error(self):
        """Upserting empty list raises ValueError."""
        with tempfile.TemporaryDirectory() as temp_chroma_dir:
            client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
            
            with pytest.raises(ValueError, match="Cannot upsert empty chunks list"):
                upsert_chunks(collection, [])
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    @given(chunk=document_chunk(pdf_metadata()))
    def test_upsert_empty_id_raises_error(self, chunk):
        """Upserting chunk with empty ID raises ValueError."""
        with tempfile.TemporaryDirectory() as temp_chroma_dir:
            client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
            
            chunk.id = ""
            
            with pytest.raises(ValueError, match="Chunk ID cannot be empty"):
                upsert_chunks(collection, [chunk])
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10)
    @given(chunk=document_chunk(pdf_metadata()))
    def test_upsert_empty_content_raises_error(self, chunk):
        """Upserting chunk with empty content raises ValueError."""
        with tempfile.TemporaryDirectory() as temp_chroma_dir:
            client, collection = init_chroma_collection(persist_directory=temp_chroma_dir)
            
            chunk.content = ""
            
            with pytest.raises(ValueError, match="Chunk content cannot be empty"):
                upsert_chunks(collection, [chunk])


class TestPersistence:
    """Tests for ChromaDB persistence across client restarts."""
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=5)
    @given(chunks=st.lists(
        document_chunk(pdf_metadata()),
        min_size=1,
        max_size=5,
        unique_by=lambda c: c.id
    ))
    def test_data_persists_across_restarts(self, chunks):
        """Data persists when client is reinitialized."""
        with tempfile.TemporaryDirectory() as temp_chroma_dir:
            # Initialize collection and upsert chunks
            client1, collection1 = init_chroma_collection(persist_directory=temp_chroma_dir)
            upsert_chunks(collection1, chunks)
            
            # Close client (simulate restart)
            del client1
            del collection1
            
            # Reinitialize client
            client2, collection2 = init_chroma_collection(persist_directory=temp_chroma_dir)
            
            # Verify all chunks still exist
            assert collection2.count() == len(chunks)
            
            # Verify each chunk can be retrieved
            for chunk in chunks:
                results = collection2.get(ids=[chunk.id])
                assert len(results['ids']) == 1
                assert results['documents'][0] == chunk.content
