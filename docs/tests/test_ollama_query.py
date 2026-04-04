#!/usr/bin/env python3
"""
Test RAG query with Ollama (local) instead of Gemini.
"""

import sys
import requests
import json

def test_query():
    print("=" * 60)
    print("Testing RAG Query with Ollama (Local)")
    print("=" * 60)
    print()
    
    # Test query
    query = "What are the main topics covered in the Ignisia documents?"
    
    print(f"Query: {query}")
    print()
    print("Sending request to backend...")
    print()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/query",
            headers={
                "Content-Type": "application/json"
                # x-api-key is optional now (only needed for Gemini fallback)
            },
            json={
                "question": query,  # FIXED: use "question" not "query"
                "n_results": 5
            },
            timeout=120
        )
        
        response.raise_for_status()
        data = response.json()
        
        print("✅ Query successful!")
        print()
        print("-" * 60)
        print("ANSWER:")
        print("-" * 60)
        print(data.get("answer", "No answer"))
        print()
        print("-" * 60)
        print("METADATA:")
        print("-" * 60)
        print(f"LLM Used: {data.get('llm_used', 'unknown')}")
        print(f"Sources: {len(data.get('sources', []))} documents")
        print(f"Conflicts: {data.get('conflict_analysis', {}).get('has_conflicts', False)}")
        print()
        
        # Show sources
        if data.get("sources"):
            print("-" * 60)
            print("SOURCES:")
            print("-" * 60)
            for i, source in enumerate(data["sources"][:3], 1):
                print(f"{i}. {source.get('source', 'Unknown')}")
                print(f"   Location: {source.get('location', 'N/A')}")
                print(f"   Relevance: {source.get('relevance_score', 0):.2f}")
                print(f"   Excerpt: {source.get('text_excerpt', '')[:100]}...")
                print()
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_query()
    sys.exit(0 if success else 1)
