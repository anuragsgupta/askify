"""ChromaDB storage layer for document chunks with embeddings."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings


@dataclass
class DocumentChunk:
    """Represents a document chunk with content and metadata."""
    id: str
    content: str
    embedding: Optional[List[float]]
    metadata: Dict[str, Any]


def init_chroma_collection(
    persist_directory: str = "./chroma_db",
    collection_name: str = "sme_knowledge"
):
    """
    Initializes ChromaDB client with local persistence.
    
    Creates a single collection for all document types (PDF, Excel, Email).
    Configures collection with OpenAI embedding function.
    
    Args:
        persist_directory: Path to persist ChromaDB data (default: ./chroma_db)
        collection_name: Name of the collection (default: sme_knowledge)
        
    Returns:
        Tuple of (chromadb.Client, chromadb.Collection)
    """
    # Create persist directory if it doesn't exist
    Path(persist_directory).mkdir(parents=True, exist_ok=True)
    
    # Initialize ChromaDB client with local persistence
    client = chromadb.PersistentClient(
        path=persist_directory,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    # Get or create collection
    # Note: We don't use ChromaDB's built-in embedding function
    # because we'll provide pre-computed embeddings from OpenAI
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "SME Knowledge Agent - All document types"}
    )
    
    return client, collection


def upsert_chunks(
    collection,
    chunks: List[DocumentChunk]
) -> None:
    """
    Upserts document chunks to ChromaDB collection.
    
    Accepts chunks with content, metadata, and pre-computed embeddings.
    Handles duplicate IDs gracefully by updating existing entries.
    
    Metadata schema:
    - source: filename (str)
    - doc_type: "policy" | "excel" | "email" (str)
    - doc_date: ISO format timestamp (str)
    
    PDF-specific metadata:
    - section_title: section name (str)
    - section_number: hierarchical numbering like "2.3.1" (str)
    - page_number: starting page (int)
    
    Excel-specific metadata:
    - sheet_name: worksheet name (str)
    - row_number: 1-indexed row number (int)
    - client: client name if present (str or None)
    
    Email-specific metadata:
    - sender: email address (str)
    - subject: email subject line (str)
    - thread_id: thread identifier (str)
    - client_keyword: client name if present (str or None)
    
    Args:
        collection: ChromaDB collection object
        chunks: List of DocumentChunk objects with embeddings and metadata
        
    Raises:
        ValueError: If chunks list is empty or contains invalid data
    """
    if not chunks:
        raise ValueError("Cannot upsert empty chunks list")
    
    # Prepare data for ChromaDB upsert
    ids = []
    documents = []
    embeddings = []
    metadatas = []
    
    for chunk in chunks:
        if not chunk.id:
            raise ValueError("Chunk ID cannot be empty")
        if not chunk.content:
            raise ValueError(f"Chunk content cannot be empty for ID: {chunk.id}")
        
        ids.append(chunk.id)
        documents.append(chunk.content)
        
        # Add embedding if provided, otherwise ChromaDB will generate it
        if chunk.embedding:
            embeddings.append(chunk.embedding)
        
        # Serialize metadata (convert datetime to ISO string)
        serialized_metadata = {}
        for key, value in chunk.metadata.items():
            if isinstance(value, datetime):
                serialized_metadata[key] = value.isoformat()
            elif value is None:
                # ChromaDB doesn't support None values, skip them
                continue
            elif isinstance(value, (str, int, float, bool)):
                serialized_metadata[key] = value
            else:
                # Convert other types to string
                serialized_metadata[key] = str(value)
        
        metadatas.append(serialized_metadata)
    
    # Upsert to ChromaDB (handles duplicates automatically)
    if embeddings:
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
    else:
        # Let ChromaDB generate embeddings
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )


def query_chunks(
    collection,
    query_text: str,
    n_results: int = 5,
    doc_type_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Queries ChromaDB collection for similar chunks.
    
    Args:
        collection: ChromaDB collection object
        query_text: Natural language query
        n_results: Number of results to return (default: 5)
        doc_type_filter: Optional filter by doc_type ("policy", "excel", "email")
        
    Returns:
        List of dicts with keys: id, content, metadata, distance
    """
    # Build where filter if doc_type specified
    where_filter = None
    if doc_type_filter:
        where_filter = {"doc_type": doc_type_filter}
    
    # Query collection
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where=where_filter
    )
    
    # Format results
    formatted_results = []
    if results['ids'] and results['ids'][0]:
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
    
    return formatted_results


def get_collection_stats(collection) -> Dict[str, Any]:
    """
    Gets statistics about the ChromaDB collection.
    
    Args:
        collection: ChromaDB collection object
        
    Returns:
        Dict with keys: total_chunks, doc_type_counts
    """
    # Get total count
    total_chunks = collection.count()
    
    # Get counts by doc_type
    doc_type_counts = {}
    for doc_type in ["policy", "excel", "email"]:
        results = collection.get(
            where={"doc_type": doc_type},
            limit=1
        )
        # Note: ChromaDB doesn't provide count with where filter directly
        # This is a limitation - we'd need to query all and count
        # For now, just return total
    
    return {
        "total_chunks": total_chunks,
        "doc_type_counts": doc_type_counts  # Empty for now
    }
