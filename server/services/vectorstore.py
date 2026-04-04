"""
ChromaDB Vector Store Service — persistent local storage.
"""
import os
import chromadb

_chroma_client = None
_collection = None

CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_data")


def _get_collection():
    global _chroma_client, _collection
    if _collection is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = _chroma_client.get_or_create_collection(
            name="askify_docs",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_documents(doc_id, chunks, embeddings):
    """
    Add document chunks with embeddings and metadata to ChromaDB.
    
    Args:
        doc_id: Unique document identifier
        chunks: List of {"text": str, "metadata": dict}
        embeddings: List of embedding vectors matching chunks
    """
    collection = _get_collection()

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    metadatas = []
    for c in chunks:
        meta = dict(c["metadata"])
        meta["doc_id"] = doc_id
        # ChromaDB only supports str/int/float/bool in metadata
        for k, v in meta.items():
            if v is None:
                meta[k] = ""
            elif not isinstance(v, (str, int, float, bool)):
                meta[k] = str(v)
        metadatas.append(meta)

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    return len(ids)


def query(query_embedding, n_results=10):
    """
    Semantic search against the vector store.
    Returns matched documents with metadata and distances.
    """
    collection = _get_collection()

    if collection.count() == 0:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    return results


def delete_document(doc_id):
    """Remove all chunks belonging to a specific document."""
    collection = _get_collection()
    # Get all IDs matching this doc_id
    results = collection.get(
        where={"doc_id": doc_id},
        include=[],
    )
    if results["ids"]:
        collection.delete(ids=results["ids"])
    return len(results["ids"])


def get_all_documents():
    """Get metadata summary of all documents in the store."""
    collection = _get_collection()
    if collection.count() == 0:
        return []

    results = collection.get(include=["metadatas"])

    # Group by doc_id to get unique documents
    docs = {}
    for meta in results["metadatas"]:
        doc_id = meta.get("doc_id", "unknown")
        if doc_id not in docs:
            docs[doc_id] = {
                "doc_id": doc_id,
                "source": meta.get("source", "Unknown"),
                "source_type": meta.get("source_type", "unknown"),
                "chunk_count": 0,
            }
        docs[doc_id]["chunk_count"] += 1

    return list(docs.values())


def get_document_count():
    """Get the total number of chunks in the store."""
    collection = _get_collection()
    return collection.count()


def get_unique_document_count():
    """Get the number of unique documents."""
    return len(get_all_documents())
