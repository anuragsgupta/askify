"""
Embedding generation utilities for document ingestion.

Supports Ollama (local) and Gemini embedding models.
"""

import os
from typing import List


def get_embedding_function(provider: str = None):
    """
    Get embedding function based on provider.
    
    Args:
        provider: "ollama" or "gemini" (defaults to LLM_PROVIDER env var)
        
    Returns:
        Callable that takes text and returns embedding vector
    """
    if provider is None:
        provider = os.getenv('LLM_PROVIDER', 'ollama').lower()
    
    if provider == 'ollama':
        from llama_index.embeddings.ollama import OllamaEmbedding
        
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        model_name = os.getenv('OLLAMA_EMBED_MODEL', 'nomic-embed-text:latest')
        
        embed_model = OllamaEmbedding(
            model_name=model_name,
            base_url=base_url
        )
        
        def embed_fn(text: str) -> List[float]:
            return embed_model.get_text_embedding(text)
        
        return embed_fn
        
    elif provider == 'gemini':
        from llama_index.embeddings.gemini import GeminiEmbedding
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        embed_model = GeminiEmbedding(
            model_name="models/embedding-001",
            api_key=api_key
        )
        
        def embed_fn(text: str) -> List[float]:
            return embed_model.get_text_embedding(text)
        
        return embed_fn
        
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'ollama' or 'gemini'")


def generate_embeddings_batch(texts: List[str], provider: str = None) -> List[List[float]]:
    """
    Generate embeddings for a batch of texts.
    
    Args:
        texts: List of text strings to embed
        provider: "ollama" or "gemini" (defaults to LLM_PROVIDER env var)
        
    Returns:
        List of embedding vectors
    """
    embed_fn = get_embedding_function(provider)
    embeddings = []
    
    for text in texts:
        embedding = embed_fn(text)
        embeddings.append(embedding)
    
    return embeddings
