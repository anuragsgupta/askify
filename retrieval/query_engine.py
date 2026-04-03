"""
Query engine for SME Knowledge Agent using LlamaIndex.

This module provides RAG (Retrieval-Augmented Generation) capabilities
using ChromaDB as the vector store and OpenAI for embeddings and LLM.
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import chromadb
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.schema import NodeWithScore, TextNode


@dataclass
class QueryResult:
    """Result from a query execution."""
    answer: str
    source_chunks: List[Dict[str, Any]]
    response_time_ms: int = 0


def create_query_engine(
    collection: chromadb.Collection,
    llm_model: str = "gpt-4o-mini",
    embed_model: str = "text-embedding-3-small",
    temperature: float = 0.0
):
    """
    Create LlamaIndex query engine with ChromaDB backend.
    
    Args:
        collection: ChromaDB collection containing document chunks
        llm_model: OpenAI model name for text generation
        embed_model: OpenAI model name for embeddings
        temperature: LLM temperature (0.0 for deterministic)
        
    Returns:
        VectorStoreIndex configured for RAG queries
    """
    # Initialize OpenAI LLM
    llm = OpenAI(
        model=llm_model,
        temperature=temperature,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Initialize OpenAI embedding model
    embed_model_obj = OpenAIEmbedding(
        model=embed_model,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
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
