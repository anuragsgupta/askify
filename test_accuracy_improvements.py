#!/usr/bin/env python3
"""
Test script for vector search accuracy improvements.
Tests relevance filtering, metadata boosting, and adaptive n_results.
"""
import sys
sys.path.insert(0, '.')

from server.services.rag import rag_query, adaptive_n_results
from server.services.embeddings import embed_query

def test_adaptive_n_results():
    """Test adaptive n_results function."""
    print("\n" + "="*60)
    print("TEST 1: Adaptive n_results")
    print("="*60)
    
    test_cases = [
        ("pricing", 5),  # Simple query
        ("What is the pricing?", 10),  # Medium query
        ("What are the detailed pricing, refund policy, and support terms for enterprise customers?", 15),  # Complex query
    ]
    
    for query, expected in test_cases:
        result = adaptive_n_results(query)
        status = "✅" if result == expected else "❌"
        print(f"{status} Query: '{query}'")
        print(f"   Word count: {len(query.split())}")
        print(f"   Expected n_results: {expected}")
        print(f"   Actual n_results: {result}")
        print()


def test_relevance_filtering():
    """Test relevance filtering with a real query."""
    print("\n" + "="*60)
    print("TEST 2: Relevance Filtering")
    print("="*60)
    
    query = "What is the pricing for Acme Corp?"
    print(f"Query: {query}")
    print()
    
    try:
        # Run query with relevance filtering
        result = rag_query(query, n_results=10)
        
        print(f"\n📊 Results:")
        print(f"   Sources returned: {len(result['sources'])}")
        print(f"   Average relevance: {result.get('avg_relevance', 0):.1%}")
        print(f"   Conflicts detected: {result['conflict_analysis']['has_conflicts']}")
        print()
        
        print(f"📄 Source Details:")
        for i, source in enumerate(result['sources'], 1):
            print(f"   {i}. {source['source']}")
            print(f"      Type: {source['source_type']}")
            print(f"      Relevance: {source['relevance_score']:.1%}")
            print()
        
        # Check if average relevance is above threshold
        avg_rel = result.get('avg_relevance', 0)
        if avg_rel >= 0.65:
            print(f"✅ PASS: Average relevance ({avg_rel:.1%}) >= 65%")
        else:
            print(f"⚠️  WARNING: Average relevance ({avg_rel:.1%}) < 65%")
            print(f"   Consider uploading more relevant documents or lowering MIN_RELEVANCE_SCORE")
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()


def test_metadata_boosting():
    """Test metadata boosting with conflict detection."""
    print("\n" + "="*60)
    print("TEST 3: Metadata Boosting (Conflict Detection)")
    print("="*60)
    
    query = "What is the refund policy for Acme Corp?"
    print(f"Query: {query}")
    print()
    
    try:
        result = rag_query(query, n_results=10)
        
        print(f"\n📊 Results:")
        print(f"   Sources returned: {len(result['sources'])}")
        print(f"   Average relevance: {result.get('avg_relevance', 0):.1%}")
        print(f"   Conflicts detected: {result['conflict_analysis']['has_conflicts']}")
        print()
        
        if result['conflict_analysis']['has_conflicts']:
            print(f"⚠️  Conflict Details:")
            conflict = result['conflict_analysis']['conflicts'][0]
            print(f"   Topic: {conflict['topic']}")
            print(f"   Conflicting sources: {len(conflict['sources'])}")
            print()
            
            for i, src in enumerate(conflict['sources'], 1):
                print(f"   Source {i}: {src['source']}")
                print(f"      Value: {src['value']}")
                print(f"      Date: {src['date'] or 'No date'}")
                print()
            
            print(f"   Resolution:")
            print(f"      Chosen: {conflict['resolution']['chosen_source']}")
            print(f"      Reason: {conflict['resolution']['reason'][:100]}...")
            print(f"      Confidence: {conflict['resolution']['confidence']:.1%}")
            print()
            
            print(f"✅ PASS: Conflict detection and metadata boosting working")
        else:
            print(f"ℹ️  INFO: No conflicts detected (this is normal if sources agree)")
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 VECTOR SEARCH ACCURACY IMPROVEMENTS - TEST SUITE")
    print("="*60)
    
    # Test 1: Adaptive n_results
    test_adaptive_n_results()
    
    # Test 2: Relevance filtering
    test_relevance_filtering()
    
    # Test 3: Metadata boosting
    test_metadata_boosting()
    
    print("\n" + "="*60)
    print("✅ TEST SUITE COMPLETE")
    print("="*60)
    print()
    print("Next steps:")
    print("1. Review the test results above")
    print("2. Check average relevance scores (target: 75-80%+)")
    print("3. Verify conflict detection is working")
    print("4. Adjust MIN_RELEVANCE_SCORE in server/.env if needed")
    print()


if __name__ == "__main__":
    main()
