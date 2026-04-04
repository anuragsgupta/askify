"""
Analytics Service - Track RAG query performance, hallucination detection, and search patterns.
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json

DB_PATH = Path(__file__).parent.parent / "askify.db"


def init_analytics_tables():
    """Initialize analytics tables in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query analytics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_text TEXT NOT NULL,
            response_time_ms INTEGER,
            num_sources INTEGER,
            avg_relevance REAL,
            has_conflicts BOOLEAN,
            llm_used TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Search topics table (for trending queries)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            query_count INTEGER DEFAULT 1,
            last_searched DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Hallucination detection table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hallucination_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id INTEGER,
            has_citations BOOLEAN,
            citation_count INTEGER,
            confidence_score REAL,
            flagged_as_hallucination BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (query_id) REFERENCES query_analytics(id)
        )
    """)
    
    # Document connections table (for knowledge graph)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_doc TEXT NOT NULL,
            target_doc TEXT NOT NULL,
            connection_strength REAL,
            shared_topics TEXT,
            co_occurrence_count INTEGER DEFAULT 1,
            last_connected DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Analytics tables initialized")


def log_query_analytics(query_text, response_time_ms, num_sources, avg_relevance, 
                        has_conflicts, llm_used):
    """Log query analytics data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO query_analytics 
        (query_text, response_time_ms, num_sources, avg_relevance, has_conflicts, llm_used)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (query_text, response_time_ms, num_sources, avg_relevance, has_conflicts, llm_used))
    
    query_id = cursor.lastrowid
    
    # Update search topics
    # Extract key topics (simple word extraction for now)
    topics = extract_topics(query_text)
    for topic in topics:
        cursor.execute("""
            INSERT INTO search_topics (topic, query_count, last_searched)
            VALUES (?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(topic) DO UPDATE SET
                query_count = query_count + 1,
                last_searched = CURRENT_TIMESTAMP
        """, (topic,))
    
    conn.commit()
    conn.close()
    
    return query_id


def log_hallucination_check(query_id, has_citations, citation_count, confidence_score):
    """Log hallucination detection results."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Flag as potential hallucination if:
    # - No citations OR
    # - Very few citations with low confidence
    flagged = not has_citations or (citation_count < 2 and confidence_score < 0.6)
    
    cursor.execute("""
        INSERT INTO hallucination_checks 
        (query_id, has_citations, citation_count, confidence_score, flagged_as_hallucination)
        VALUES (?, ?, ?, ?, ?)
    """, (query_id, has_citations, citation_count, confidence_score, flagged))
    
    conn.commit()
    conn.close()


def log_document_connection(source_doc, target_doc, shared_topics=None):
    """Log document co-occurrence for knowledge graph."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if connection exists
    cursor.execute("""
        SELECT id, co_occurrence_count FROM document_connections
        WHERE (source_doc = ? AND target_doc = ?) OR (source_doc = ? AND target_doc = ?)
    """, (source_doc, target_doc, target_doc, source_doc))
    
    result = cursor.fetchone()
    
    if result:
        # Update existing connection
        cursor.execute("""
            UPDATE document_connections
            SET co_occurrence_count = co_occurrence_count + 1,
                connection_strength = connection_strength + 0.1,
                last_connected = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (result[0],))
    else:
        # Create new connection
        cursor.execute("""
            INSERT INTO document_connections
            (source_doc, target_doc, connection_strength, shared_topics)
            VALUES (?, ?, ?, ?)
        """, (source_doc, target_doc, 0.5, json.dumps(shared_topics or [])))
    
    conn.commit()
    conn.close()


def get_analytics_summary(days=7):
    """Get analytics summary for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate date range
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Total queries
    cursor.execute("""
        SELECT COUNT(*) FROM query_analytics
        WHERE DATE(timestamp) >= ?
    """, (start_date,))
    total_queries = cursor.fetchone()[0]
    
    # Average response time
    cursor.execute("""
        SELECT AVG(response_time_ms) FROM query_analytics
        WHERE DATE(timestamp) >= ?
    """, (start_date,))
    avg_response_time = cursor.fetchone()[0] or 0
    
    # Average relevance
    cursor.execute("""
        SELECT AVG(avg_relevance) FROM query_analytics
        WHERE DATE(timestamp) >= ?
    """, (start_date,))
    avg_relevance = cursor.fetchone()[0] or 0
    
    # Conflict rate
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN has_conflicts = 1 THEN 1 END) * 100.0 / COUNT(*) as conflict_rate
        FROM query_analytics
        WHERE DATE(timestamp) >= ?
    """, (start_date,))
    conflict_rate = cursor.fetchone()[0] or 0
    
    # Hallucination rate
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN flagged_as_hallucination = 1 THEN 1 END) * 100.0 / COUNT(*) as hallucination_rate
        FROM hallucination_checks hc
        JOIN query_analytics qa ON hc.query_id = qa.id
        WHERE DATE(qa.timestamp) >= ?
    """, (start_date,))
    hallucination_rate = cursor.fetchone()[0] or 0
    
    # Top search topics
    cursor.execute("""
        SELECT topic, query_count
        FROM search_topics
        ORDER BY query_count DESC
        LIMIT 10
    """)
    top_topics = [{"topic": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    # Queries over time (daily)
    cursor.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM query_analytics
        WHERE DATE(timestamp) >= ?
        GROUP BY DATE(timestamp)
        ORDER BY date
    """, (start_date,))
    queries_over_time = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    # LLM usage distribution
    cursor.execute("""
        SELECT llm_used, COUNT(*) as count
        FROM query_analytics
        WHERE DATE(timestamp) >= ?
        GROUP BY llm_used
    """, (start_date,))
    llm_usage = [{"llm": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_queries": total_queries,
        "avg_response_time_ms": round(avg_response_time, 2),
        "avg_relevance": round(avg_relevance, 3),
        "conflict_rate": round(conflict_rate, 2),
        "hallucination_rate": round(hallucination_rate, 2),
        "top_topics": top_topics,
        "queries_over_time": queries_over_time,
        "llm_usage": llm_usage
    }


def get_knowledge_graph_data():
    """Get document connections for knowledge graph visualization."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all document connections
    cursor.execute("""
        SELECT source_doc, target_doc, connection_strength, co_occurrence_count
        FROM document_connections
        WHERE connection_strength > 0.3
        ORDER BY connection_strength DESC
        LIMIT 100
    """)
    
    connections = []
    nodes = set()
    
    for row in cursor.fetchall():
        source, target, strength, count = row
        connections.append({
            "source": source,
            "target": target,
            "strength": strength,
            "count": count
        })
        nodes.add(source)
        nodes.add(target)
    
    conn.close()
    
    return {
        "nodes": [{"id": node, "label": node} for node in nodes],
        "edges": connections
    }


def extract_topics(query_text):
    """Extract key topics from query text (simple implementation)."""
    # Remove common words
    stop_words = {'what', 'is', 'the', 'a', 'an', 'for', 'to', 'of', 'in', 'on', 'at', 'by', 'with'}
    
    words = query_text.lower().split()
    topics = [word for word in words if word not in stop_words and len(word) > 3]
    
    return topics[:3]  # Return top 3 topics


# Initialize tables on module load
init_analytics_tables()
