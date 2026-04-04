"""
Query Route — RAG query endpoint.
"""
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional

from server.services.rag import rag_query
from server.services.database import (
    get_cached_answer, 
    save_chat, 
    get_recent_history,
    create_session,
    get_recent_sessions,
    get_session_history,
    delete_session,
    update_session_title
)

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    n_results: int = 10
    session_id: Optional[int] = None


class SessionCreateRequest(BaseModel):
    title: str = "New Chat"


class SessionUpdateRequest(BaseModel):
    title: str


@router.post("/query")
async def query_knowledge_base(
    req: QueryRequest,
    x_api_key: Optional[str] = Header(None),
):
    """
    Ask a natural language question against the ingested knowledge base.
    Returns an AI-generated answer with source citations and conflict analysis.
    
    Uses Gemini (cloud) as primary LLM, Ollama (local) as fallback.
    API key is optional - uses .env configuration if not provided.
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # 1. Check for exact cached answer
    cached_result = get_cached_answer(req.question)
    if cached_result:
        print(f"⚡ Cache hit for question: '{req.question}'")
        return cached_result

    try:
        # API key is optional now - Ollama doesn't need it
        result = rag_query(req.question, x_api_key, n_results=req.n_results)
        
        # 2. Save the AI response and sources to the database
        session_id = save_chat(req.question, result, req.session_id)
        result["session_id"] = session_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

    return result


@router.get("/history")
async def fetch_recent_history(limit: int = 50):
    """
    Retrieve the most recent chat history for the dashboard.
    """
    try:
        history = get_recent_history(limit=limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")


@router.post("/sessions")
async def create_new_session(req: SessionCreateRequest):
    """
    Create a new chat session.
    """
    try:
        session_id = create_session(req.title)
        if session_id is None:
            raise HTTPException(status_code=500, detail="Failed to create session")
        return {"session_id": session_id, "title": req.title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/sessions")
async def fetch_recent_sessions(limit: int = 20):
    """
    Retrieve the most recent chat sessions.
    """
    try:
        sessions = get_recent_sessions(limit=limit)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")


@router.get("/sessions/{session_id}")
async def fetch_session_history(session_id: int):
    """
    Retrieve all chat history for a specific session.
    """
    try:
        history = get_session_history(session_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session history: {str(e)}")


@router.delete("/sessions/{session_id}")
async def remove_session(session_id: int):
    """
    Delete a chat session and all its history.
    """
    try:
        success = delete_session(session_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete session")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@router.patch("/sessions/{session_id}")
async def update_session(session_id: int, req: SessionUpdateRequest):
    """
    Update a session's title.
    """
    try:
        success = update_session_title(session_id, req.title)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update session")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")
