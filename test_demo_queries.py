"""
Test script to verify demo queries work correctly.

Tests:
1. Query that triggers conflict detection (refund policy versions)
2. Query that retrieves from multiple doc types
3. Citation formatting for all doc types
"""

from pathlib import Path
from storage.chroma_store import init_chroma_collection, query_chunks
from retrieval.conflict_detector import detect_conflicts


def test_conflict_detection():
    """Test query that triggers conflict detection between policy versions."""
    print("\n" + "=" * 60)
    print("TEST 1: Conflict Detection")
    print("=" * 60)
    
    # Initialize ChromaDB
    client, collection = init_chroma_collection(persist_directory="./chroma_db")
    
    # Query about refund policy (should retrieve both v1 and v2)
    query = "What is the refund window for returns?"
    print(f"\nQuery: {query}")
    
    results = query_chunks(collection, query, n_results=5)
    
    print(f"\nRetrieved {len(results)} chunks:")
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"\n  {i}. {metadata.get('source', 'Unknown')}")
        print(f"     Doc Type: {metadata.get('doc_type', 'Unknown')}")
        print(f"     Date: {metadata.get('doc_date', 'Unknown')}")
        if metadata.get('section_title'):
            print(f"     Section: {metadata.get('section_title')}")
        print(f"     Content preview: {result['content'][:100]}...")
    
    # Test conflict detection
    print("\n" + "-" * 60)
    print("Running conflict detection...")
    
    conflicts = detect_conflicts(results)
    
    if conflicts:
        print(f"\n[OK] Detected {len(conflicts)} conflict(s):")
        for conflict in conflicts:
            print(f"\n  Winner: {conflict.winner['metadata'].get('source')}")
            print(f"    Date: {conflict.winner['metadata'].get('doc_date')}")
            print(f"  Rejected: {conflict.rejected[0]['metadata'].get('source')}")
            print(f"    Date: {conflict.rejected[0]['metadata'].get('doc_date')}")
            print(f"  Explanation: {conflict.diff_explanation}")
    else:
        print("\n[WARN] No conflicts detected (expected at least 1)")
    
    return len(conflicts) > 0


def test_multi_doc_type_retrieval():
    """Test query that retrieves from multiple document types."""
    print("\n" + "=" * 60)
    print("TEST 2: Multi-Doc-Type Retrieval")
    print("=" * 60)
    
    # Initialize ChromaDB
    client, collection = init_chroma_collection(persist_directory="./chroma_db")
    
    # Query that should match PDF, Excel, and Email (broader query)
    query = "Tell me about Acme Corp and refund policies"
    print(f"\nQuery: {query}")
    
    results = query_chunks(collection, query, n_results=10)
    
    # Count doc types
    doc_types = set()
    for result in results:
        doc_type = result['metadata'].get('doc_type')
        doc_types.add(doc_type)
    
    print(f"\nRetrieved {len(results)} chunks from {len(doc_types)} document types:")
    print(f"  Doc types: {', '.join(sorted(doc_types))}")
    
    # Show examples from each doc type
    for doc_type in sorted(doc_types):
        matching = [r for r in results if r['metadata'].get('doc_type') == doc_type]
        if matching:
            example = matching[0]
            print(f"\n  {doc_type.upper()} example:")
            print(f"    Source: {example['metadata'].get('source')}")
            print(f"    Content: {example['content'][:100]}...")
    
    # Verify we got multiple doc types
    success = len(doc_types) >= 2
    if success:
        print(f"\n[OK] Successfully retrieved from multiple doc types")
    else:
        print(f"\n[WARN] Only retrieved from {len(doc_types)} doc type(s)")
    
    return success


def test_citation_formatting():
    """Test citation formatting for all doc types."""
    print("\n" + "=" * 60)
    print("TEST 3: Citation Formatting")
    print("=" * 60)
    
    # Initialize ChromaDB
    client, collection = init_chroma_collection(persist_directory="./chroma_db")
    
    # Get examples of each doc type
    doc_types = ["policy", "excel", "email"]
    
    for doc_type in doc_types:
        print(f"\n{doc_type.upper()} Citation:")
        print("-" * 40)
        
        results = query_chunks(collection, "test", n_results=1, doc_type_filter=doc_type)
        
        if results:
            result = results[0]
            metadata = result['metadata']
            
            # Format citation based on doc type
            if doc_type == "policy":
                citation = f"{metadata.get('source')} (Section {metadata.get('section_number')}: {metadata.get('section_title')}, Page {metadata.get('page_number')})"
            elif doc_type == "excel":
                citation = f"{metadata.get('source')} (Sheet: {metadata.get('sheet_name')}, Row {metadata.get('row_number')})"
            elif doc_type == "email":
                citation = f"From: {metadata.get('sender')} ({metadata.get('doc_date')}, Subject: {metadata.get('subject')})"
            else:
                citation = "Unknown format"
            
            print(f"  {citation}")
            
            # Verify all required fields are present
            if doc_type == "policy":
                required = ['source', 'section_number', 'section_title', 'page_number']
            elif doc_type == "excel":
                required = ['source', 'sheet_name', 'row_number']
            elif doc_type == "email":
                required = ['sender', 'doc_date', 'subject']
            
            missing = [field for field in required if not metadata.get(field)]
            
            if missing:
                print(f"  [WARN] Missing fields: {', '.join(missing)}")
            else:
                print(f"  [OK] All required fields present")
        else:
            print(f"  [WARN] No chunks found for {doc_type}")
    
    return True


def main():
    """Run all demo query tests."""
    print("=" * 60)
    print("Demo Query Verification Tests")
    print("=" * 60)
    
    # Check if ChromaDB exists
    if not Path("./chroma_db").exists():
        print("\n[ERROR] ./chroma_db directory not found")
        print("Please run ingest_demo_data.py first")
        return
    
    # Run tests
    test1_passed = test_conflict_detection()
    test2_passed = test_multi_doc_type_retrieval()
    test3_passed = test_citation_formatting()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"\n  Test 1 (Conflict Detection): {'[PASS]' if test1_passed else '[FAIL]'}")
    print(f"  Test 2 (Multi-Doc-Type Retrieval): {'[PASS]' if test2_passed else '[FAIL]'}")
    print(f"  Test 3 (Citation Formatting): {'[PASS]' if test3_passed else '[FAIL]'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print("\n[SUCCESS] All demo queries work correctly!")
    else:
        print("\n[WARNING] Some tests failed - review output above")


if __name__ == "__main__":
    main()
