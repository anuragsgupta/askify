"""
SQLite Database service for chat history and answer caching.
"""
import os
import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

# DB path located inside the server directory
DB_PATH = Path(__file__).parent.parent / "askify.db"

def get_db_connection():
    """Establish and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database tables if they don't exist."""
    print("\n🔧 INITIALIZING SQLITE DATABASE")
    print(f"📌 DB path: {DB_PATH}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Chat sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if chat_history table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Create new table with session_id
            print("📝 Creating chat_history table with session support...")
            cursor.execute("""
                CREATE TABLE chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    sources TEXT NOT NULL,
                    conflict_analysis TEXT NOT NULL,
                    llm_used TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                )
            """)
        else:
            # Check if session_id column exists
            cursor.execute("PRAGMA table_info(chat_history)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'session_id' not in columns:
                print("⚠️  Old database schema detected - session_id column missing")
                print("📝 Please run: python3 migrate_database.py")
                print("📝 Then restart the backend")
                # Don't create the index yet - it will fail
                conn.commit()
                conn.close()
                return
        
        # Create indexes (only if session_id column exists)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_question ON chat_history(question collate nocase)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_session ON chat_history(session_id)")
        
        conn.commit()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        conn.rollback()
    finally:
        conn.close()

def save_chat(question: str, rag_result: Dict[str, Any], session_id: Optional[int] = None):
    """
    Save the user question and the LLM response to the database.
    If session_id is None, creates a new session.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # If no session_id provided, create a new session
        if session_id is None:
            # Generate title from first question (truncate to 50 chars)
            title = question[:50] + "..." if len(question) > 50 else question
            cursor.execute(
                "INSERT INTO chat_sessions (title) VALUES (?)",
                (title,)
            )
            session_id = cursor.lastrowid
        else:
            # Update session's updated_at timestamp
            cursor.execute(
                "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,)
            )
        
        cursor.execute(
            """
            INSERT INTO chat_history 
            (session_id, question, answer, sources, conflict_analysis, llm_used) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                question,
                rag_result.get("answer", ""),
                json.dumps(rag_result.get("sources", [])),
                json.dumps(rag_result.get("conflict_analysis", {})),
                rag_result.get("llm_used", "unknown")
            )
        )
        
        conn.commit()
        conn.close()
        
        return session_id
    except Exception as e:
        print(f"⚠️ Failed to save chat history: {e}")
        return None

def get_cached_answer(question: str) -> Optional[Dict[str, Any]]:
    """
    Look for an exact case-insensitive match for the question to serve as cache.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT answer, sources, conflict_analysis, llm_used 
            FROM chat_history 
            WHERE lower(question) = lower(?)
            ORDER BY created_at DESC 
            LIMIT 1
            """,
            (question.strip(),)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "answer": row["answer"],
                "sources": json.loads(row["sources"]),
                "conflict_analysis": json.loads(row["conflict_analysis"]),
                "llm_used": row["llm_used"],
                "cached": True
            }
    except Exception as e:
        print(f"⚠️ Failed to check cache: {e}")
        
    return None

def get_recent_history(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve the most recent chat history for the dashboard.
    """
    history = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, session_id, question, answer, sources, conflict_analysis, llm_used, created_at
            FROM chat_history 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (limit,)
        )
        
        rows = cursor.fetchall()
        for row in rows:
            history.append({
                "id": row["id"],
                "session_id": row["session_id"],
                "question": row["question"],
                "answer": row["answer"],
                "sources": json.loads(row["sources"]),
                "conflict_analysis": json.loads(row["conflict_analysis"]),
                "llm_used": row["llm_used"],
                "created_at": row["created_at"]
            })
            
        conn.close()
    except Exception as e:
        print(f"⚠️ Failed to retrieve chat history: {e}")
        
    return history


def create_session(title: str = "New Chat") -> Optional[int]:
    """
    Create a new chat session.
    Returns the session ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO chat_sessions (title) VALUES (?)",
            (title,)
        )
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    except Exception as e:
        print(f"⚠️ Failed to create session: {e}")
        return None


def get_recent_sessions(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Retrieve the most recent chat sessions.
    """
    sessions = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT 
                s.id, 
                s.title, 
                s.created_at, 
                s.updated_at,
                COUNT(h.id) as message_count
            FROM chat_sessions s
            LEFT JOIN chat_history h ON s.id = h.session_id
            GROUP BY s.id
            ORDER BY s.updated_at DESC 
            LIMIT ?
            """,
            (limit,)
        )
        
        rows = cursor.fetchall()
        for row in rows:
            sessions.append({
                "id": row["id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "message_count": row["message_count"]
            })
            
        conn.close()
    except Exception as e:
        print(f"⚠️ Failed to retrieve sessions: {e}")
        
    return sessions


def get_session_history(session_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all chat history for a specific session.
    """
    history = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, question, answer, sources, conflict_analysis, llm_used, created_at
            FROM chat_history 
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (session_id,)
        )
        
        rows = cursor.fetchall()
        for row in rows:
            history.append({
                "id": row["id"],
                "question": row["question"],
                "answer": row["answer"],
                "sources": json.loads(row["sources"]),
                "conflict_analysis": json.loads(row["conflict_analysis"]),
                "llm_used": row["llm_used"],
                "created_at": row["created_at"]
            })
            
        conn.close()
    except Exception as e:
        print(f"⚠️ Failed to retrieve session history: {e}")
        
    return history


def delete_session(session_id: int) -> bool:
    """
    Delete a chat session and all its history.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"⚠️ Failed to delete session: {e}")
        return False


def update_session_title(session_id: int, title: str) -> bool:
    """
    Update a session's title.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE chat_sessions SET title = ? WHERE id = ?",
            (title, session_id)
        )
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"⚠️ Failed to update session title: {e}")
        return False

# Initialize the DB immediately when the package is loaded
init_db()
