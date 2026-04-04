"""
Analytics API Routes - Provide RAG performance metrics and knowledge graph data.
"""
from fastapi import APIRouter, Query
from server.services.analytics import get_analytics_summary, get_knowledge_graph_data

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def get_summary(days: int = Query(7, ge=1, le=90)):
    """
    Get analytics summary for the specified number of days.
    
    Args:
        days: Number of days to include in summary (1-90)
    
    Returns:
        Analytics summary including:
        - Total queries
        - Average response time
        - Average relevance
        - Conflict rate
        - Hallucination rate
        - Top search topics
        - Queries over time
        - LLM usage distribution
    """
    summary = get_analytics_summary(days=days)
    return summary


@router.get("/knowledge-graph")
async def get_knowledge_graph():
    """
    Get knowledge graph data showing document connections.
    
    Returns:
        Graph data with nodes (documents) and edges (connections)
    """
    graph_data = get_knowledge_graph_data()
    return graph_data
