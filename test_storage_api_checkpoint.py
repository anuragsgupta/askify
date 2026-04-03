"""
Comprehensive checkpoint test for Task 9: Storage Layer Validation
Tests ChromaDB persistence, Google Drive integration (mocked), and API integration.
"""

import tempfile
import shutil
import os
from datetime import datetime
from storage.chroma_store import (
    DocumentChunk,
    init_chroma_collection,
    upsert_chunks,
    query_chunks,
    get_collection_stats
)


def test_chromadb_storage_and_persistence():
    """Test ChromaDB storage operations and persistence across restarts."""
    print("\n" + "="*70)
    print("TEST 1: ChromaDB Storage and Persistence")
    print("="*70)
    
    tmpdir = tempfile.mkdtemp()
    
    try:
        # Step 1: Initialize and populate collection
        print("\n[1/5] Initializing ChromaDB collection...")
        client, collection = init_chroma_collection(persist_directory=tmpdir)
        print(f"✓ Collection created: {collection.name}")
        print(f"✓ Initial count: {collection.count()}")
        
        # Step 2: Create diverse test chunks (PDF, Excel, Email)
        print("\n[2/5] Creating test chunks for all document types...")
        test_chunks = [
            # PDF chunks
            DocumentChunk(
                id="pdf_v1_refund",
                content="Refund policy: Customers can return items within 30 days for full refund.",
                embedding=[0.1] * 384,
                metadata={
                    "source": "Refund_Policy_v1_2023.pdf",
                    "doc_type": "policy",
                    "doc_date": datetime(2023, 1, 15),
                    "section_title": "Returns and Refunds",
                    "section_number": "3.2",
                    "page_number": 5
                }
            ),
            DocumentChunk(
                id="pdf_v2_refund",
                content="Refund policy: Customers can return items within 60 days for full refund.",
                embedding=[0.15] * 384,
                metadata={
                    "source": "Refund_Policy_v2_2024.pdf",
                    "doc_type": "policy",
                    "doc_date": datetime(2024, 3, 1),
                    "section_title": "Returns and Refunds",
                    "section_number": "3.2",
                    "page_number": 5
                }
            ),
            # Excel chunks
            DocumentChunk(
                id="excel_acme_pricing",
                content="Client: Acme Corp, Product: Widget Pro, Price: $500, Discount: 10%",
                embedding=[0.2] * 384,
                metadata={
                    "source": "Pricing_Q1_2024.xlsx",
                    "doc_type": "excel",
                    "doc_date": datetime(2024, 1, 1),
                    "sheet_name": "Q1 Pricing",
                    "row_number": 42,
                    "client": "Acme Corp"
                }
            ),
            DocumentChunk(
                id="excel_techco_pricing",
                content="Client: TechCo Inc, Product: Widget Basic, Price: $300, Discount: 5%",
                embedding=[0.25] * 384,
                metadata={
                    "source": "Pricing_Q1_2024.xlsx",
                    "doc_type": "excel",
                    "doc_date": datetime(2024, 1, 1),
                    "sheet_name": "Q1 Pricing",
                    "row_number": 43,
                    "client": "TechCo Inc"
                }
            ),
            # Email chunks
            DocumentChunk(
                id="email_acme_discount",
                content="Hi team, I approved a special 15% discount for Acme Corp on Widget Pro.",
                embedding=[0.3] * 384,
                metadata={
                    "source": "email_thread_acme.eml",
                    "doc_type": "email",
                    "doc_date": datetime(2023, 12, 15),
                    "sender": "sales@company.com",
                    "subject": "Acme Corp discount approval",
                    "thread_id": "thread_acme_001"
                }
            ),
        ]
        
        print(f"✓ Created {len(test_chunks)} test chunks:")
        for chunk in test_chunks:
            print(f"  - {chunk.id} ({chunk.metadata['doc_type']})")
        
        # Step 3: Upsert chunks
        print("\n[3/5] Upserting chunks to ChromaDB...")
        upsert_chunks(collection, test_chunks)
        count = collection.count()
        print(f"✓ Upserted {len(test_chunks)} chunks")
        print(f"✓ Collection count: {count}")
        assert count == len(test_chunks), f"Expected {len(test_chunks)} chunks, got {count}"
        
        # Step 4: Verify retrieval and metadata preservation
        print("\n[4/5] Verifying chunk retrieval and metadata preservation...")
        for chunk in test_chunks:
            results = collection.get(ids=[chunk.id])
            
            # Verify chunk exists
            assert len(results['ids']) == 1, f"Failed to retrieve chunk {chunk.id}"
            
            # Verify content preserved
            assert results['documents'][0] == chunk.content, f"Content mismatch for {chunk.id}"
            
            # Verify metadata preserved
            stored_metadata = results['metadatas'][0]
            assert stored_metadata['source'] == chunk.metadata['source']
            assert stored_metadata['doc_type'] == chunk.metadata['doc_type']
            assert stored_metadata['doc_date'] == chunk.metadata['doc_date'].isoformat()
            
            # Verify doc-type specific metadata
            if chunk.metadata['doc_type'] == 'policy':
                assert stored_metadata['section_title'] == chunk.metadata['section_title']
                assert stored_metadata['section_number'] == chunk.metadata['section_number']
                assert stored_metadata['page_number'] == chunk.metadata['page_number']
            elif chunk.metadata['doc_type'] == 'excel':
                assert stored_metadata['sheet_name'] == chunk.metadata['sheet_name']
                assert stored_metadata['row_number'] == chunk.metadata['row_number']
                assert stored_metadata['client'] == chunk.metadata['client']
            elif chunk.metadata['doc_type'] == 'email':
                assert stored_metadata['sender'] == chunk.metadata['sender']
                assert stored_metadata['subject'] == chunk.metadata['subject']
                assert stored_metadata['thread_id'] == chunk.metadata['thread_id']
            
            print(f"✓ Verified: {chunk.id} (type: {chunk.metadata['doc_type']})")
        
        # Step 5: Test persistence across restart
        print("\n[5/5] Testing persistence across ChromaDB restart...")
        original_count = collection.count()
        del client
        del collection
        
        # Reinitialize
        client2, collection2 = init_chroma_collection(persist_directory=tmpdir)
        new_count = collection2.count()
        
        assert new_count == original_count, f"Persistence failed: expected {original_count}, got {new_count}"
        print(f"✓ Persistence verified: {new_count} chunks after restart")
        
        # Verify data integrity after restart
        for chunk in test_chunks:
            results = collection2.get(ids=[chunk.id])
            assert len(results['ids']) == 1
            assert results['documents'][0] == chunk.content
            assert results['metadatas'][0]['doc_type'] == chunk.metadata['doc_type']
        
        print(f"✓ Data integrity verified for all {len(test_chunks)} chunks")
        
        print("\n✅ TEST 1 PASSED: ChromaDB storage and persistence working correctly!")
        
    finally:
        # Cleanup
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_query_operations():
    """Test query operations with doc_type filtering."""
    print("\n" + "="*70)
    print("TEST 2: Query Operations and Filtering")
    print("="*70)
    
    tmpdir = tempfile.mkdtemp()
    
    try:
        # Initialize and populate
        print("\n[1/3] Setting up test collection...")
        client, collection = init_chroma_collection(persist_directory=tmpdir)
        
        test_chunks = [
            DocumentChunk(
                id="query_pdf_1",
                content="This document describes our refund policy for returns.",
                embedding=[0.1] * 384,
                metadata={
                    "source": "policy.pdf",
                    "doc_type": "policy",
                    "doc_date": datetime(2024, 1, 1),
                    "section_title": "Refunds",
                    "section_number": "1",
                    "page_number": 1
                }
            ),
            DocumentChunk(
                id="query_excel_1",
                content="Client pricing information for Acme Corp.",
                embedding=[0.2] * 384,
                metadata={
                    "source": "pricing.xlsx",
                    "doc_type": "excel",
                    "doc_date": datetime(2024, 1, 1),
                    "sheet_name": "Sheet1",
                    "row_number": 1,
                    "client": "Acme"
                }
            ),
            DocumentChunk(
                id="query_email_1",
                content="Email about refund policy changes.",
                embedding=[0.15] * 384,
                metadata={
                    "source": "email.eml",
                    "doc_type": "email",
                    "doc_date": datetime(2024, 1, 1),
                    "sender": "test@test.com",
                    "subject": "Refund policy",
                    "thread_id": "thread1"
                }
            ),
        ]
        
        upsert_chunks(collection, test_chunks)
        print(f"✓ Upserted {len(test_chunks)} test chunks")
        
        # Test query without filter
        print("\n[2/3] Testing query without doc_type filter...")
        results = query_chunks(collection, "refund policy", n_results=5)
        print(f"✓ Query returned {len(results)} results")
        assert len(results) > 0, "Query should return results"
        
        # Verify results contain metadata
        for result in results:
            assert 'id' in result
            assert 'content' in result
            assert 'metadata' in result
            assert 'doc_type' in result['metadata']
            print(f"  - {result['id']} (type: {result['metadata']['doc_type']})")
        
        # Test query with doc_type filter
        print("\n[3/3] Testing query with doc_type filter...")
        policy_results = query_chunks(collection, "refund", n_results=5, doc_type_filter="policy")
        print(f"✓ Filtered query returned {len(policy_results)} policy results")
        
        # Verify all results are policy type
        for result in policy_results:
            assert result['metadata']['doc_type'] == 'policy', "Filter should only return policy docs"
            print(f"  - {result['id']} (verified: {result['metadata']['doc_type']})")
        
        print("\n✅ TEST 2 PASSED: Query operations and filtering working correctly!")
        
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_google_drive_integration_status():
    """Check Google Drive integration test status."""
    print("\n" + "="*70)
    print("TEST 3: Google Drive Integration Status")
    print("="*70)
    
    print("\n[1/2] Checking for Google Drive credentials...")
    has_credentials = os.path.exists('credentials.json')
    
    if has_credentials:
        print("✓ credentials.json found")
    else:
        print("⚠ credentials.json not found (optional for MVP)")
    
    print("\n[2/2] Checking Google Drive unit tests...")
    # Run the unit tests (not integration tests)
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'pytest', 'ingestion/test_drive_fetcher.py', '-v', '-k', 'not Integration', '--tb=short'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print("✓ Google Drive unit tests passed")
        # Count passed tests
        passed_count = result.stdout.count(' PASSED')
        print(f"✓ {passed_count} unit tests passed")
    else:
        print("✗ Google Drive unit tests failed")
        print(result.stdout)
        raise AssertionError("Google Drive unit tests failed")
    
    print("\n✅ TEST 3 PASSED: Google Drive integration layer verified!")
    print("\nNote: Integration tests with real Drive API are optional and require:")
    print("  - credentials.json file")
    print("  - DRIVE_TEST_FOLDER_ID environment variable")
    print("  - Run with: pytest -m integration")


def main():
    """Run all checkpoint tests."""
    print("\n" + "="*70)
    print("TASK 9 CHECKPOINT: Storage Layer Validation")
    print("="*70)
    print("\nThis checkpoint validates:")
    print("  1. ChromaDB storage and persistence")
    print("  2. Query operations and filtering")
    print("  3. Google Drive integration (unit tests)")
    
    try:
        # Run all tests
        test_chromadb_storage_and_persistence()
        test_query_operations()
        test_google_drive_integration_status()
        
        # Final summary
        print("\n" + "="*70)
        print("✅ ALL CHECKPOINT TESTS PASSED!")
        print("="*70)
        print("\nStorage layer is ready for retrieval layer implementation.")
        print("\nSummary:")
        print("  ✓ ChromaDB initialization and persistence working")
        print("  ✓ Multi-document type storage (PDF, Excel, Email) working")
        print("  ✓ Metadata preservation across storage/retrieval working")
        print("  ✓ Query operations and doc_type filtering working")
        print("  ✓ Google Drive integration unit tests passing")
        print("\nNext steps:")
        print("  - Proceed to Task 10: Implement query engine with LlamaIndex")
        print("  - Implement conflict detection middleware")
        print("  - Build Streamlit UI")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ CHECKPOINT FAILED!")
        print("="*70)
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
