"""
Database Migration Script - Add Session Support

This script migrates the existing database to add session support.
It creates the chat_sessions table and adds session_id to chat_history.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "server" / "askify.db"

def migrate_database():
    """Migrate the database to add session support."""
    print("\n🔧 DATABASE MIGRATION - Adding Session Support")
    print(f"📌 DB path: {DB_PATH}")
    
    if not DB_PATH.exists():
        print("❌ Database file not found. Run the backend first to create it.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if chat_sessions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_sessions'")
        if cursor.fetchone():
            print("✅ chat_sessions table already exists")
        else:
            print("📝 Creating chat_sessions table...")
            cursor.execute("""
                CREATE TABLE chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ chat_sessions table created")
        
        # Check if session_id column exists in chat_history
        cursor.execute("PRAGMA table_info(chat_history)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'session_id' in columns:
            print("✅ session_id column already exists in chat_history")
        else:
            print("📝 Adding session_id column to chat_history...")
            cursor.execute("ALTER TABLE chat_history ADD COLUMN session_id INTEGER")
            print("✅ session_id column added")
            
            # Create a default session for existing chats
            print("📝 Creating default session for existing chats...")
            cursor.execute("INSERT INTO chat_sessions (title) VALUES (?)", ("Legacy Chats",))
            default_session_id = cursor.lastrowid
            
            # Update all existing chats to use the default session
            cursor.execute("UPDATE chat_history SET session_id = ? WHERE session_id IS NULL", (default_session_id,))
            print(f"✅ Migrated existing chats to session ID {default_session_id}")
        
        # Create indexes
        print("📝 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_session ON chat_history(session_id)")
        print("✅ Indexes created")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
