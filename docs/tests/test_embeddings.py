#!/usr/bin/env python3
"""
Test script to verify embeddings are working correctly.
"""

import sys
sys.path.insert(0, '.')

from server.services.embeddings import embed_texts, embed_query

def test_embeddings():
    print("=" * 60)
    print("Testing Ollama Embeddings with nomic-embed-text")
    print("=" * 60)
    print()
    
    # Test 1: Single text embedding
    print("Test 1: Embedding single text...")
    try:
        test_text = "This is a test document about refund policies."
        embedding = embed_query(test_text)
        
        if embedding:
            print(f"✅ Success!")
            print(f"   Embedding dimension: {len(embedding)}")
            print(f"   First 5 values: {embedding[:5]}")
            print(f"   Expected dimension: 768 (nomic-embed-text)")
            
            if len(embedding) == 768:
                print("   ✅ Correct dimension!")
            else:
                print(f"   ❌ Wrong dimension! Expected 768, got {len(embedding)}")
        else:
            print("❌ Failed: No embedding returned")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    print()
    
    # Test 2: Batch embeddings
    print("Test 2: Embedding multiple texts...")
    try:
        test_texts = [
            "Refund policy for customers",
            "Pricing information for products",
            "Shipping and delivery guidelines"
        ]
        embeddings = embed_texts(test_texts)
        
        if embeddings and len(embeddings) == len(test_texts):
            print(f"✅ Success!")
            print(f"   Number of embeddings: {len(embeddings)}")
            print(f"   Each embedding dimension: {len(embeddings[0])}")
            
            # Check all have correct dimension
            all_correct = all(len(emb) == 768 for emb in embeddings)
            if all_correct:
                print("   ✅ All embeddings have correct dimension!")
            else:
                print("   ❌ Some embeddings have wrong dimension!")
                return False
        else:
            print(f"❌ Failed: Expected {len(test_texts)} embeddings, got {len(embeddings) if embeddings else 0}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    print()
    print("=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print()
    print("Your embeddings are working correctly.")
    print("You can now upload documents to the backend.")
    print()
    return True


if __name__ == "__main__":
    success = test_embeddings()
    sys.exit(0 if success else 1)
