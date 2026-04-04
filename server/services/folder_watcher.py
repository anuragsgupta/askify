"""
Folder Watcher Service - Monitor folders for new files and auto-ingest with deduplication.
"""
import os
import hashlib
import sqlite3
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from server.services.parser import parse_file
from server.services.embeddings import embed_texts
from server.services.vectorstore import add_documents

DB_PATH = Path(__file__).parent.parent / "askify.db"


def init_folder_watch_tables():
    """Initialize folder watch tables in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Watched folders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watched_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_path TEXT UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_scan DATETIME
        )
    """)
    
    # File hashes table (for deduplication)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_hashes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE NOT NULL,
            original_filename TEXT NOT NULL,
            file_size INTEGER,
            file_type TEXT,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            ingestion_count INTEGER DEFAULT 1,
            doc_id TEXT,
            metadata TEXT
        )
    """)
    
    # File ingestion log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_ingestion_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT,
            chunks_created INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Folder watch tables initialized")


def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"❌ Error calculating hash for {file_path}: {e}")
        return None


def is_duplicate_file(file_hash):
    """Check if file hash already exists in database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, original_filename, first_seen, ingestion_count
        FROM file_hashes
        WHERE file_hash = ?
    """, (file_hash,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result is not None, result


def register_file_hash(file_hash, filename, file_size, file_type, doc_id, metadata):
    """Register a new file hash in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    import json
    
    try:
        cursor.execute("""
            INSERT INTO file_hashes 
            (file_hash, original_filename, file_size, file_type, doc_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (file_hash, filename, file_size, file_type, doc_id, json.dumps(metadata)))
        
        conn.commit()
        print(f"✅ Registered file hash: {filename}")
    except sqlite3.IntegrityError:
        # Hash already exists, update last_seen and increment count
        cursor.execute("""
            UPDATE file_hashes
            SET last_seen = CURRENT_TIMESTAMP,
                ingestion_count = ingestion_count + 1
            WHERE file_hash = ?
        """, (file_hash,))
        conn.commit()
        print(f"⚠️  Duplicate file detected: {filename}")
    finally:
        conn.close()


def log_file_ingestion(file_path, file_hash, status, error_message=None, chunks_created=0):
    """Log file ingestion attempt."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO file_ingestion_log
        (file_path, file_hash, status, error_message, chunks_created)
        VALUES (?, ?, ?, ?, ?)
    """, (file_path, file_hash, status, error_message, chunks_created))
    
    conn.commit()
    conn.close()


def ingest_file(file_path):
    """
    Ingest a single file with deduplication.
    
    Returns:
        (success: bool, message: str, is_duplicate: bool)
    """
    try:
        # Calculate file hash
        file_hash = calculate_file_hash(file_path)
        if not file_hash:
            return False, "Failed to calculate file hash", False
        
        # Check for duplicates
        is_dup, dup_info = is_duplicate_file(file_hash)
        if is_dup:
            message = f"Duplicate file skipped: {os.path.basename(file_path)} (original: {dup_info[1]}, first seen: {dup_info[2]})"
            log_file_ingestion(file_path, file_hash, "skipped_duplicate")
            print(f"⏭️  {message}")
            return True, message, True
        
        # Parse document
        print(f"\n📄 Processing: {os.path.basename(file_path)}")
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        chunks = parse_file(os.path.basename(file_path), file_bytes)
        
        if not chunks:
            error_msg = "No chunks extracted from document"
            log_file_ingestion(file_path, file_hash, "failed", error_msg)
            return False, error_msg, False
        
        # Generate embeddings
        texts = [c["text"] for c in chunks]
        embeddings, provider = embed_texts(texts)
        
        if not embeddings:
            error_msg = "Failed to generate embeddings"
            log_file_ingestion(file_path, file_hash, "failed", error_msg)
            return False, error_msg, False
        
        # Store in vector database
        doc_id = os.path.basename(file_path)
        num_chunks = add_documents(doc_id, chunks, embeddings)
        
        # Register file hash
        file_size = os.path.getsize(file_path)
        file_type = chunks[0]["metadata"].get("source_type", "unknown")
        metadata = {
            "source": doc_id,
            "source_type": file_type,
            "upload_date": datetime.now().isoformat(),
            "chunk_count": num_chunks,
            "embedding_provider": provider
        }
        
        register_file_hash(file_hash, os.path.basename(file_path), file_size, file_type, doc_id, metadata)
        log_file_ingestion(file_path, file_hash, "success", chunks_created=num_chunks)
        
        message = f"Successfully ingested: {os.path.basename(file_path)} ({num_chunks} chunks)"
        print(f"✅ {message}")
        return True, message, False
        
    except Exception as e:
        error_msg = str(e)
        log_file_ingestion(file_path, file_hash if 'file_hash' in locals() else "unknown", "failed", error_msg)
        print(f"❌ Error ingesting {file_path}: {e}")
        return False, error_msg, False


class FolderWatchHandler(FileSystemEventHandler):
    """Handle file system events for watched folders."""
    
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.supported_extensions = {'.pdf', '.txt', '.eml', '.xlsx', '.xls', '.csv', '.docx', '.doc'}
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        file_path = event.src_path
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Check if file type is supported
        if file_ext not in self.supported_extensions:
            print(f"⏭️  Skipping unsupported file type: {os.path.basename(file_path)}")
            return
        
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        # Ingest the file
        print(f"\n🔔 New file detected: {os.path.basename(file_path)}")
        success, message, is_duplicate = ingest_file(file_path)
        
        if success and not is_duplicate:
            print(f"✅ Auto-ingestion successful: {os.path.basename(file_path)}")
        elif is_duplicate:
            print(f"⏭️  Duplicate skipped: {os.path.basename(file_path)}")
        else:
            print(f"❌ Auto-ingestion failed: {os.path.basename(file_path)}")


def add_watched_folder(folder_path):
    """Add a folder to the watch list."""
    if not os.path.exists(folder_path):
        return False, "Folder does not exist"
    
    if not os.path.isdir(folder_path):
        return False, "Path is not a directory"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO watched_folders (folder_path, is_active)
            VALUES (?, 1)
        """, (folder_path,))
        conn.commit()
        print(f"✅ Added watched folder: {folder_path}")
        return True, "Folder added successfully"
    except sqlite3.IntegrityError:
        print(f"⚠️  Folder already being watched: {folder_path}")
        return False, "Folder is already being watched"
    finally:
        conn.close()


def remove_watched_folder(folder_path):
    """Remove a folder from the watch list."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM watched_folders
        WHERE folder_path = ?
    """, (folder_path,))
    
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    if deleted:
        print(f"✅ Removed watched folder: {folder_path}")
        return True, "Folder removed successfully"
    else:
        return False, "Folder not found in watch list"


def get_watched_folders():
    """Get list of all watched folders."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, folder_path, is_active, created_at, last_scan
        FROM watched_folders
        ORDER BY created_at DESC
    """)
    
    folders = []
    for row in cursor.fetchall():
        folders.append({
            "id": row[0],
            "folder_path": row[1],
            "is_active": bool(row[2]),
            "created_at": row[3],
            "last_scan": row[4]
        })
    
    conn.close()
    return folders


def scan_folder_for_new_files(folder_path):
    """Scan a folder and ingest all new files.
    
    Returns:
        tuple: (total_files, ingested, duplicates, errors) - all integers
        Returns (0, 0, 0, 0) if folder doesn't exist (caller should validate path first)
    """
    if not os.path.exists(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        return 0, 0, 0, 0
    
    supported_extensions = {'.pdf', '.txt', '.eml', '.xlsx', '.xls', '.csv', '.docx', '.doc'}
    
    total_files = 0
    ingested = 0
    duplicates = 0
    errors = 0
    
    print(f"\n🔍 Scanning folder: {folder_path}")
    
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in supported_extensions:
                total_files += 1
                file_path = os.path.join(root, filename)
                
                success, message, is_duplicate = ingest_file(file_path)
                
                if success and not is_duplicate:
                    ingested += 1
                elif is_duplicate:
                    duplicates += 1
                else:
                    errors += 1
    
    # Update last_scan timestamp
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE watched_folders
        SET last_scan = CURRENT_TIMESTAMP
        WHERE folder_path = ?
    """, (folder_path,))
    conn.commit()
    conn.close()
    
    summary = f"Scanned {total_files} files: {ingested} ingested, {duplicates} duplicates, {errors} errors"
    print(f"\n📊 {summary}")
    
    return total_files, ingested, duplicates, errors


def start_folder_watcher(folder_path):
    """Start watching a folder for new files."""
    if not os.path.exists(folder_path):
        return None, "Folder does not exist"
    
    event_handler = FolderWatchHandler(folder_path)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)
    observer.start()
    
    print(f"👁️  Started watching folder: {folder_path}")
    return observer, "Folder watcher started"


def get_file_statistics():
    """Get statistics about ingested files."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total unique files
    cursor.execute("SELECT COUNT(*) FROM file_hashes")
    total_files = cursor.fetchone()[0]
    
    # Total duplicates detected
    cursor.execute("SELECT SUM(ingestion_count - 1) FROM file_hashes")
    total_duplicates = cursor.fetchone()[0] or 0
    
    # Files by type
    cursor.execute("""
        SELECT file_type, COUNT(*) as count
        FROM file_hashes
        GROUP BY file_type
        ORDER BY count DESC
    """)
    files_by_type = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    # Recent ingestions
    cursor.execute("""
        SELECT file_path, status, chunks_created, timestamp
        FROM file_ingestion_log
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    recent_ingestions = []
    for row in cursor.fetchall():
        recent_ingestions.append({
            "file_path": row[0],
            "status": row[1],
            "chunks_created": row[2],
            "timestamp": row[3]
        })
    
    conn.close()
    
    return {
        "total_files": total_files,
        "total_duplicates": total_duplicates,
        "files_by_type": files_by_type,
        "recent_ingestions": recent_ingestions
    }


# Initialize tables on module load
init_folder_watch_tables()
