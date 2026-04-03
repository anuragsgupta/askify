"""
Quick test script to verify Ollama/Gemini setup.

Run this to ensure your local LLM configuration is working.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_ollama_connection():
    """Test Ollama service connectivity."""
    print("Testing Ollama connection...")
    
    try:
        import requests
        response = requests.get(f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✓ Ollama is running with {len(models)} models")
            for model in models:
                print(f"  - {model['name']}")
            return True
        else:
            print(f"✗ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return False


def test_embedding_generation():
    """Test embedding generation."""
    print("\nTesting embedding generation...")
    
    try:
        from storage.embeddings import get_embedding_function
        
        provider = os.getenv('LLM_PROVIDER', 'ollama')
        print(f"Using provider: {provider}")
        
        embed_fn = get_embedding_function(provider)
        embedding = embed_fn("This is a test document.")
        
        print(f"✓ Generated embedding with {len(embedding)} dimensions")
        print(f"  First 5 values: {embedding[:5]}")
        return True
        
    except Exception as e:
        print(f"✗ Embedding generation failed: {e}")
        return False


def test_query_engine():
    """Test query engine initialization."""
    print("\nTesting query engine...")
    
    try:
        from storage.chroma_store import init_chroma_collection
        from retrieval.query_engine import create_query_engine
        
        # Initialize ChromaDB
        client, collection = init_chroma_collection(
            persist_directory="./test_chroma_e2e"
        )
        
        # Create query engine
        provider = os.getenv('LLM_PROVIDER', 'ollama')
        query_engine = create_query_engine(collection, provider=provider)
        
        print(f"✓ Query engine created successfully")
        print(f"  Provider: {provider}")
        print(f"  Collection: {collection.name}")
        print(f"  Document count: {collection.count()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Query engine initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Local LLM Setup Test")
    print("=" * 60)
    
    provider = os.getenv('LLM_PROVIDER', 'ollama')
    print(f"\nConfigured provider: {provider}")
    
    if provider == 'ollama':
        print(f"LLM model: {os.getenv('OLLAMA_LLM_MODEL', 'phi3:mini')}")
        print(f"Embed model: {os.getenv('OLLAMA_EMBED_MODEL', 'nomic-embed-text:latest')}")
        print(f"Base URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
    elif provider == 'gemini':
        print(f"Model: {os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')}")
        api_key = os.getenv('GEMINI_API_KEY', '')
        print(f"API Key: {'*' * 10 + api_key[-4:] if len(api_key) > 4 else 'NOT SET'}")
    
    print("\n" + "=" * 60)
    
    results = []
    
    # Test Ollama connection (only if using Ollama)
    if provider == 'ollama':
        results.append(("Ollama Connection", test_ollama_connection()))
    
    # Test embedding generation
    results.append(("Embedding Generation", test_embedding_generation()))
    
    # Test query engine
    results.append(("Query Engine", test_query_engine()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python ingest_demo_data.py")
        print("2. Run: streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        if provider == 'ollama':
            print("- Ensure Ollama is running: ollama serve")
            print("- Check models are installed: ollama list")
            print("- Pull missing models: ollama pull phi3:mini")
        elif provider == 'gemini':
            print("- Check GEMINI_API_KEY in .env file")
            print("- Verify API key at: https://makersuite.google.com/app/apikey")


if __name__ == "__main__":
    main()
