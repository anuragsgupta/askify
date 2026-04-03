"""
Query engine for SME Knowledge Agent using LlamaIndex.

This module provides RAG (Retrieval-Augmented Generation) capabilities
using ChromaDB as the vector store with support for Ollama and Gemini.
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import chromadb
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.schema import NodeWithScore, TextNode


@dataclass
class QueryResult:
    """Result from a query execution."""
    answer: str
    source_chunks: List[Dict[str, Any]]
    response_time_ms: int = 0


def create_query_engine(
    collection: chromadb.Collection,
    provider: str = None,
    llm_model: str = None,
    embed_model: str = None,
    temperature: float = 0.0
):
    """
    Create LlamaIndex query engine with ChromaDB backend.
    
    Supports Ollama (local) and Gemini providers.
    
    Args:
        collection: ChromaDB collection containing document chunks
        provider: "ollama" or "gemini" (defaults to LLM_PROVIDER env var)
        llm_model: Model name for text generation (provider-specific)
        embed_model: Model name for embeddings (provider-specific)
        temperature: LLM temperature (0.0 for deterministic)
        
    Returns:
        VectorStoreIndex configured for RAG queries
    """
    # Get provider from env if not specified
    if provider is None:
        provider = os.getenv('LLM_PROVIDER', 'ollama').lower()
    
    # Initialize LLM and embedding model based on provider
    if provider == 'ollama':
        from llama_index.llms.ollama import Ollama
        from llama_index.embeddings.ollama import OllamaEmbedding
        
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        llm_model = llm_model or os.getenv('OLLAMA_LLM_MODEL', 'phi3:mini')
        embed_model_name = embed_model or os.getenv('OLLAMA_EMBED_MODEL', 'nomic-embed-text:latest')
        
        llm = Ollama(
            model=llm_model,
            base_url=base_url,
            temperature=temperature,
            request_timeout=120.0
        )
        
        embed_model_obj = OllamaEmbedding(
            model_name=embed_model_name,
            base_url=base_url
        )
        
    elif provider == 'gemini':
        from llama_index.llms.gemini import Gemini
        from llama_index.embeddings.gemini import GeminiEmbedding
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        llm_model = llm_model or os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        
        llm = Gemini(
            model=llm_model,
            api_key=api_key,
            temperature=temperature
        )
        
        embed_model_obj = GeminiEmbedding(
            model_name="models/embedding-001",
            api_key=api_key
        )
        
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'ollama' or 'gemini'")
    
    # Create ChromaDB vector store
    vector_store = ChromaVectorStore(chroma_collection=collection)
    
    # Create storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create vector store index
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
        embed_model=embed_model_obj
    )
    
    # Create query engine
    query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=5,
        response_mode="compact"
    )
    
    return query_engine


def query_with_metadata(
    query_engine,
    query: str,
    doc_type_filter: Optional[str] = None,
    top_k: int = 5
) -> QueryResult:
    """
    Execute query and return results with full metadata.
    
    Args:
        query_engine: LlamaIndex query engine
        query: Natural language query
        doc_type_filter: Optional filter for "policy", "excel", or "email"
        top_k: Number of chunks to retrieve
        
    Returns:
        QueryResult with answer and source chunks with metadata
    """
    import time
    start_time = time.time()
    
    # Build metadata filters if doc_type specified
    filters = None
    if doc_type_filter:
        from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
        filters = MetadataFilters(
            filters=[ExactMatchFilter(key="doc_type", value=doc_type_filter)]
        )
    
    # Execute query
    if filters:
        response = query_engine.query(query, filters=filters)
    else:
        response = query_engine.query(query)
    
    # Extract source chunks with metadata
    source_chunks = []
    if hasattr(response, 'source_nodes'):
        for node in response.source_nodes:
            chunk = {
                'content': node.node.text,
                'metadata': node.node.metadata,
                'score': node.score if hasattr(node, 'score') else None
            }
            source_chunks.append(chunk)
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    return QueryResult(
        answer=str(response),
        source_chunks=source_chunks,
        response_time_ms=response_time_ms
    )


def retrieve_chunks(
    query_engine,
    query: str,
    doc_type_filter: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant chunks without generating an answer.
    
    Useful for conflict detection and analysis without LLM generation.
    
    Args:
        query_engine: LlamaIndex query engine
        query: Natural language query
        doc_type_filter: Optional filter for "policy", "excel", or "email"
        top_k: Number of chunks to retrieve
        
    Returns:
        List of chunks with content and metadata
    """
    # Get the retriever from the query engine
    retriever = query_engine.retriever
    
    # Build metadata filters if doc_type specified
    if doc_type_filter:
        from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
        filters = MetadataFilters(
            filters=[ExactMatchFilter(key="doc_type", value=doc_type_filter)]
        )
        retriever.filters = filters
    
    # Retrieve nodes
    nodes = retriever.retrieve(query)
    
    # Convert to chunk format
    chunks = []
    for node in nodes:
        chunk = {
            'content': node.node.text,
            'metadata': node.node.metadata,
            'score': node.score if hasattr(node, 'score') else None
        }
        chunks.append(chunk)
    
    return chunks
