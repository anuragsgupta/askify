"""
Quick checkpoint test for storage layer functionality.
Tests ChromaDB persistence and basic operations.
"""

import tempfile
import shutil
from datetime import datetime
from storage.chroma_store import (
    DocumentChunk,
    init_chroma_collection,
    upsert_chunks,
    get_collection_stats
)


def test_basic_storage_operations():
    """Test basic ChromaDB storage operations."""
    print("\n[1/4] Testing ChromaDB initialization...")
    tmpdir = tempfile.mkdtemp()
    
    try:
        # Initialize collection
        client, collection = init_chroma_collection(persist_directory=tmpdir)
        print(f"✓ Collection created: {collection.name}")
        print(f"✓ Initial count: {collection.count()}")
        
        # Create test chunks
        print("\n[2/4] Testing chunk upsert...")
        test_chunks = [
            DocumentChunk(
                id="pdf_chunk_1",
                content="This is a refund policy section about 30-day returns.",
                embedding=[0.1] * 384,  # Dummy embedding
                metadata={
                    "source": "Refund_Policy_v1.pdf",
                    "doc_type": "policy",
                    "doc_date": datetime(2023, 1, 15),
                    "section_title": "Returns",
                    "section_number": "3.2",
                    "page_number": 5
                }
            ),
            DocumentChunk(
                id="excel_chunk_1",
                content="Client: Acme Corp, Product: Widget, Price: $500",
                embedding=[0.2] * 384,
                metadata={
                    "source": "Pricing_2024.xlsx",
                    "doc_type": "excel",
                    "doc_date": datetime(2024, 3, 1),
                    "sheet_name": "Q1",
                    "row_number": 42,
                    "client": "Acme Corp"
                }
            ),
            DocumentChunk(
                id="email_chunk_1",
                content="Hi, regarding the discount approval for Acme Corp...",
                embedding=[0.3] * 384,
                metadata={
                    "source": "email_thread_123.eml",
                    "doc_type": "email",
                    "doc_date": datetime(2024, 1, 15),
                    "sender": "john@acme.com",
                    "subject": "Discount approval",
                    "thread_id": "thread_123"
                }
            )
        ]
        
        upsert_chunks(collection, test_chunks)
        print(f"✓ Upserted {len(test_chunks)} chunks")
        print(f"✓ Collection count: {collection.count()}")
        
        # Verify chunks can be retrieved
        print("\n[3/4] Testing chunk retrieval...")
        for chunk in test_chunks:
            results = collection.get(ids=[chunk.id])
            assert len(results['ids']) == 1, f"Failed to retrieve chunk {chunk.id}"
            assert results['documents'][0] == chunk.content
            assert results['metadatas'][0]['doc_type'] == chunk.metadata['doc_type']
            print(f"✓ Retrieved chunk: {chunk.id} (type: {chunk.metadata['doc_type']})")
        
        # Test persistence across restart
        print("\n[4/4] Testing persistence across restart...")
        del client
        del collection
        
        # Reinitialize
        client2, collection2 = init_chroma_collection(persist_directory=tmpdir)
        assert collection2.count() == len(test_chunks), "Chunks not persisted!"
        print(f"✓ Persistence verified: {collection2.count()} chunks after restart")
        
        # Verify data integrity after restart
        for chunk in test_chunks:
            results = collection2.get(ids=[chunk.id])
            assert len(results['ids']) == 1
            assert results['documents'][0] == chunk.content
            print(f"✓ Data integrity verified for: {chunk.id}")
        
        print("\n" + "="*60)
        print("✅ ALL STORAGE LAYER TESTS PASSED!")
        print("="*60)
        
    finally:
        # Cleanup
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    test_basic_storage_operations()
