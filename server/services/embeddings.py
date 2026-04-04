"""
Embeddings Service — Gemini (primary) with Ollama (fallback).

Uses Gemini text-embedding-004 for higher quality embeddings,
falls back to Ollama nomic-embed-text if Gemini fails.

Configuration via .env file.
"""
import os
from pathlib import Path
import requests
from google import genai
from dotenv import load_dotenv

# Load environment variables from server/.env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get configuration from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2-preview")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
USE_GEMINI_PRIMARY = os.getenv("USE_GEMINI_PRIMARY", "true").lower() == "true"

# Debug: Print configuration on module load
print("\n" + "="*60)
print("🔧 EMBEDDINGS SERVICE CONFIGURATION")
print("="*60)
print(f"📌 .env path: {env_path}")
print(f"📌 .env exists: {env_path.exists()}")
print(f"📌 Gemini API Key: {'✅ SET' if GEMINI_API_KEY else '❌ NOT SET'}")
if GEMINI_API_KEY:
    print(f"📌 Gemini API Key (first 20 chars): {GEMINI_API_KEY[:20]}...")
print(f"📌 Gemini Embedding Model: {GEMINI_EMBEDDING_MODEL}")
print(f"📌 Ollama Embed Model: {OLLAMA_EMBED_MODEL}")
print(f"📌 USE_GEMINI_PRIMARY: {USE_GEMINI_PRIMARY}")
print(f"📌 Provider Priority: {'Gemini → Ollama' if USE_GEMINI_PRIMARY else 'Ollama → Gemini'}")
print("="*60 + "\n")


def estimate_tokens(text):
    """Estimate token count (1 token ≈ 4 chars)."""
    return len(text) // 4


def validate_chunk_size(text, max_tokens=8000):
    """
    Validate that text fits within embedding model context limit.
    
    Args:
        text: Text to validate
        max_tokens: Maximum tokens allowed
        
    Returns:
        True if valid, raises ValueError if too large
    """
    tokens = estimate_tokens(text)
    if tokens > max_tokens:
        print(f"⚠️  CHUNK TOO LARGE: {tokens} tokens (max: {max_tokens})")
        print(f"   Text length: {len(text)} chars")
        print(f"   First 100 chars: {text[:100]}...")
        raise ValueError(
            f"Text too large for embedding: {tokens} tokens (max: {max_tokens}). "
            f"Text length: {len(text)} chars. "
            f"Please ensure document parser is chunking properly."
        )
    return True


def embed_texts_gemini(texts, api_key=None):
    """
    Generate embeddings using Gemini text-embedding-004.
    
    Args:
        texts: List of text strings to embed
        api_key: Gemini API key (optional, uses .env if not provided)
        
    Returns:
        List of embedding vectors (768-dim)
    """
    if not texts:
        return []
    
    # Use provided API key or fall back to environment variable
    api_key = api_key or GEMINI_API_KEY
    
    if not api_key:
        raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in server/.env file")
    
    print(f"\n🌐 GEMINI EMBEDDINGS - Starting")
    print(f"   Model: {GEMINI_EMBEDDING_MODEL}")
    print(f"   Chunks to embed: {len(texts)}")
    
    try:
        client = genai.Client(api_key=api_key)
        embeddings = []
        
        # Gemini can batch, but we'll do one at a time for consistency
        for i, text in enumerate(texts):
            tokens = estimate_tokens(text)
            print(f"   Chunk {i+1}/{len(texts)}: {tokens} tokens, {len(text)} chars")
            
            # Validate chunk size (Gemini supports up to 2048 tokens)
            validate_chunk_size(text, max_tokens=2000)
            
            # Generate embedding
            result = client.models.embed_content(
                model=GEMINI_EMBEDDING_MODEL,
                contents=text
            )
            
            if hasattr(result, 'embeddings') and result.embeddings:
                embeddings.append(result.embeddings[0].values)
                print(f"   ✅ Chunk {i+1} embedded successfully (768-dim)")
            else:
                raise ValueError(f"Unexpected Gemini response format for chunk {i+1}")
        
        print(f"✅ GEMINI EMBEDDINGS - Success ({len(embeddings)} vectors)")
        return embeddings
        
    except Exception as e:
        print(f"❌ GEMINI EMBEDDINGS - Failed: {e}")
        raise


def embed_texts_ollama(texts):
    """
    Generate embeddings using Ollama nomic-embed-text (fallback).
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors (768-dim)
    """
    if not texts:
        return []
    
    print(f"\n🤖 OLLAMA EMBEDDINGS - Starting")
    print(f"   Model: {OLLAMA_EMBED_MODEL}")
    print(f"   Chunks to embed: {len(texts)}")
    
    try:
        embeddings = []
        
        for i, text in enumerate(texts):
            tokens = estimate_tokens(text)
            print(f"   Chunk {i+1}/{len(texts)}: {tokens} tokens, {len(text)} chars")
            
            # Validate chunk size (Ollama supports up to 8192 tokens)
            validate_chunk_size(text, max_tokens=8000)
            
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": OLLAMA_EMBED_MODEL,
                    "prompt": text,
                },
                timeout=180
            )
            response.raise_for_status()
            data = response.json()
            
            if "embedding" in data:
                embeddings.append(data["embedding"])
                print(f"   ✅ Chunk {i+1} embedded successfully (768-dim)")
            else:
                raise ValueError(f"Unexpected Ollama response format for chunk {i+1}")
        
        print(f"✅ OLLAMA EMBEDDINGS - Success ({len(embeddings)} vectors)")
        return embeddings
        
    except Exception as e:
        print(f"❌ OLLAMA EMBEDDINGS - Failed: {e}")
        raise


def embed_texts(texts, api_key=None, use_gemini=None):
    """
    Generate embeddings with Gemini (primary) and Ollama (fallback).
    
    Args:
        texts: List of text strings to embed
        api_key: Gemini API key (optional, uses .env if not provided)
        use_gemini: Whether to try Gemini first (optional, uses .env if not provided)
        
    Returns:
        Tuple of (embeddings, provider_used)
        - embeddings: List of embedding vectors
        - provider_used: "gemini" or "ollama"
    """
    if not texts:
        return [], "none"
    
    # Use environment variable if not explicitly set
    if use_gemini is None:
        use_gemini = USE_GEMINI_PRIMARY
    
    print(f"\n{'='*60}")
    print(f"📊 EMBEDDING REQUEST")
    print(f"{'='*60}")
    print(f"Chunks to process: {len(texts)}")
    print(f"Use Gemini Primary: {use_gemini}")
    print(f"Provider Priority: {'Gemini → Ollama' if use_gemini else 'Ollama → Gemini'}")
    print(f"{'='*60}")
    
    embeddings = None
    provider_used = None
    
    # Try Gemini first (higher quality)
    if use_gemini:
        print(f"\n🌐 Trying Gemini embeddings ({GEMINI_EMBEDDING_MODEL}) for {len(texts)} chunks...")
        try:
            embeddings = embed_texts_gemini(texts, api_key)
            provider_used = "gemini"
            print(f"\n✅ Gemini embeddings successful ({len(embeddings)} vectors, 768-dim)")
        except Exception as e:
            print(f"\n⚠️  Gemini embeddings failed: {e}")
            print(f"   Falling back to Ollama...")
    
    # Fallback to Ollama (local, reliable)
    if embeddings is None:
        print(f"\n🤖 Using Ollama embeddings ({OLLAMA_EMBED_MODEL}) for {len(texts)} chunks...")
        try:
            embeddings = embed_texts_ollama(texts)
            provider_used = "ollama"
            print(f"\n✅ Ollama embeddings successful ({len(embeddings)} vectors, 768-dim)")
        except Exception as e:
            print(f"\n❌ Ollama embeddings failed: {e}")
            print(f"   Make sure Ollama is running: ollama serve")
            raise
    
    print(f"\n{'='*60}")
    print(f"📊 EMBEDDING COMPLETE")
    print(f"{'='*60}")
    print(f"Provider used: {provider_used.upper()}")
    print(f"Vectors generated: {len(embeddings)}")
    print(f"{'='*60}\n")
    
    return embeddings, provider_used


def embed_query(query_text, api_key=None, use_gemini=None):
    """
    Embed a single query string with Gemini (primary) and Ollama (fallback).
    
    Args:
        query_text: Query string to embed
        api_key: Gemini API key (optional, uses .env if not provided)
        use_gemini: Whether to try Gemini first (optional, uses .env if not provided)
        
    Returns:
        Embedding vector (768-dim)
    """
    if not query_text:
        return None
    
    # Use environment variable if not explicitly set
    if use_gemini is None:
        use_gemini = USE_GEMINI_PRIMARY
    
    # Use provided API key or fall back to environment variable
    api_key = api_key or GEMINI_API_KEY
    
    embedding = None
    
    # Try Gemini first
    if use_gemini and api_key:
        try:
            validate_chunk_size(query_text, max_tokens=2000)
            
            client = genai.Client(api_key=api_key)
            result = client.models.embed_content(
                model=GEMINI_EMBEDDING_MODEL,
                contents=query_text
            )
            
            if hasattr(result, 'embeddings') and result.embeddings:
                embedding = result.embeddings[0].values
                print(f"✅ Query embedded with Gemini")
        except Exception as e:
            print(f"⚠️  Gemini query embedding failed: {e}, falling back to Ollama...")
    
    # Fallback to Ollama
    if embedding is None:
        try:
            validate_chunk_size(query_text, max_tokens=8000)
            
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": OLLAMA_EMBED_MODEL,
                    "prompt": query_text,
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            if "embedding" in data:
                embedding = data["embedding"]
                print(f"✅ Query embedded with Ollama")
            else:
                raise ValueError(f"Unexpected Ollama response format")
                
        except Exception as e:
            print(f"❌ Query embedding failed: {e}")
            raise
    
    return embedding


# Backward compatibility - return just embeddings without provider info
def embed_texts_compat(texts, api_key=None):
    """Backward compatible version that returns only embeddings."""
    embeddings, _ = embed_texts(texts, api_key)
    return embeddings
