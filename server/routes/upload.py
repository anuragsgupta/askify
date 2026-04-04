"""
Upload Routes — file upload, document listing, and deletion.
"""
import uuid
import os
import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from pydantic import BaseModel
from typing import Optional

from server.services.parser import parse_file
from server.services.embeddings import embed_texts
from server.services.vectorstore import (
    add_documents,
    get_all_documents,
    delete_document,
    get_document_count,
    get_unique_document_count,
)
from server.services.web_scraper import scrape_website, chunk_web_content

router = APIRouter()

# Simple JSON file to store document metadata (dates, upload info)
META_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "doc_metadata.json")


class URLUploadRequest(BaseModel):
    url: str


def _load_meta():
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_meta(data):
    with open(META_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None),
):
    """
    Upload and ingest a document into the vector store.
    
    API key is optional - uses .env configuration if not provided.
    """
    # Validate file type
    allowed_extensions = {"pdf", "xlsx", "xls", "txt", "eml", "text", "csv"}
    filename = file.filename or "unknown.txt"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: .{ext}. Allowed: {', '.join(allowed_extensions)}"
        )

    # Read file bytes
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # Parse the document into chunks
    try:
        chunks = parse_file(filename, file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")

    if not chunks:
        raise HTTPException(status_code=400, detail="No content could be extracted from the file")

    # Generate embeddings (Gemini primary, Ollama fallback)
    try:
        texts = [c["text"] for c in chunks]
        embeddings, provider_used = embed_texts(texts, x_api_key)
        print(f"📊 Embeddings generated using: {provider_used}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

    # Store in ChromaDB
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    try:
        chunk_count = add_documents(doc_id, chunks, embeddings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector store error: {str(e)}")

    # Save metadata
    meta = _load_meta()
    meta[doc_id] = {
        "filename": filename,
        "source_type": ext if ext in ("pdf", "xlsx", "xls") else "text",
        "upload_date": datetime.now().isoformat(),
        "chunk_count": chunk_count,
        "file_size": len(file_bytes),
        "embedding_provider": provider_used,  # Track which provider was used
    }
    _save_meta(meta)

    return {
        "success": True,
        "doc_id": doc_id,
        "filename": filename,
        "chunks_created": chunk_count,
        "embedding_provider": provider_used,
        "message": f"Successfully ingested '{filename}' — {chunk_count} chunks indexed using {provider_used} embeddings.",
    }


@router.get("/documents")
async def list_documents():
    """List all ingested documents with metadata."""
    vector_docs = get_all_documents()
    file_meta = _load_meta()

    documents = []
    for vdoc in vector_docs:
        doc_id = vdoc["doc_id"]
        fmeta = file_meta.get(doc_id, {})
        documents.append({
            "doc_id": doc_id,
            "filename": fmeta.get("filename", vdoc.get("source", "Unknown")),
            "source_type": fmeta.get("source_type", vdoc.get("source_type", "unknown")),
            "upload_date": fmeta.get("upload_date"),
            "chunk_count": vdoc.get("chunk_count", 0),
            "file_size": fmeta.get("file_size", 0),
            "status": "Indexed",
        })

    return {
        "documents": documents,
        "total_documents": len(documents),
        "total_chunks": get_document_count(),
    }


@router.delete("/documents/{doc_id}")
async def remove_document(doc_id: str):
    """Remove a document from the vector store."""
    deleted = delete_document(doc_id)

    # Remove from metadata
    meta = _load_meta()
    if doc_id in meta:
        del meta[doc_id]
        _save_meta(meta)

    return {
        "success": True,
        "deleted_chunks": deleted,
        "message": f"Document {doc_id} removed ({deleted} chunks deleted).",
    }


@router.get("/stats")
async def get_stats():
    """Get system statistics for the dashboard."""
    meta = _load_meta()
    total_docs = get_unique_document_count()
    total_chunks = get_document_count()

    # Count by type
    type_counts = {}
    for doc_info in meta.values():
        st = doc_info.get("source_type", "unknown")
        type_counts[st] = type_counts.get(st, 0) + 1

    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "type_counts": type_counts,
        "supported_formats": "PDF, Excel, TXT, EML, Web URLs",
    }


@router.post("/upload-url")
async def upload_url(
    req: URLUploadRequest,
    x_api_key: Optional[str] = Header(None),
):
    """
    Scrape a website URL and ingest its content into the vector store.
    
    API key is optional - uses .env configuration if not provided.
    """
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    # Scrape the website
    print(f"\n🌐 Starting web scrape for: {url}")
    scrape_result = scrape_website(url)
    
    if not scrape_result["success"]:
        raise HTTPException(
            status_code=400,
            detail=scrape_result.get("error", "Failed to scrape website")
        )
    
    # Check if we got content
    if not scrape_result["text"] or len(scrape_result["text"]) < 100:
        raise HTTPException(
            status_code=400,
            detail="Insufficient content extracted from website. The page may be empty or blocked."
        )
    
    # Chunk the content
    try:
        chunks = chunk_web_content(
            scrape_result["text"],
            scrape_result["title"],
            scrape_result["url"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to chunk content: {str(e)}")
    
    if not chunks:
        raise HTTPException(status_code=400, detail="No content could be extracted from the website")
    
    # Generate embeddings
    try:
        texts = [c["text"] for c in chunks]
        embeddings, provider_used = embed_texts(texts, x_api_key)
        print(f"📊 Embeddings generated using: {provider_used}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")
    
    # Store in ChromaDB
    doc_id = f"web_{uuid.uuid4().hex[:12]}"
    try:
        chunk_count = add_documents(doc_id, chunks, embeddings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector store error: {str(e)}")
    
    # Save metadata
    meta = _load_meta()
    meta[doc_id] = {
        "filename": scrape_result["title"],
        "source_type": "web",
        "url": scrape_result["url"],
        "domain": scrape_result["domain"],
        "upload_date": datetime.now().isoformat(),
        "chunk_count": chunk_count,
        "word_count": scrape_result["word_count"],
        "embedding_provider": provider_used,
    }
    _save_meta(meta)
    
    return {
        "success": True,
        "doc_id": doc_id,
        "title": scrape_result["title"],
        "url": scrape_result["url"],
        "domain": scrape_result["domain"],
        "chunks_created": chunk_count,
        "word_count": scrape_result["word_count"],
        "embedding_provider": provider_used,
        "message": f"Successfully ingested '{scrape_result['title']}' — {chunk_count} chunks indexed from {scrape_result['domain']}.",
    }

