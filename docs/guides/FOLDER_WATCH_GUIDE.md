# Folder Watch Auto-Ingest Feature Guide

## Overview

The Folder Watch Auto-Ingest feature enables automatic monitoring of filesystem folders and ingestion of new documents into the Askify RAG system. The system uses SHA-256 hash-based deduplication to prevent duplicate document ingestion, ensuring efficient storage and processing.

## Key Features

- **Automatic File Monitoring**: Background watchers detect new files in real-time
- **Hash-Based Deduplication**: SHA-256 hashing prevents duplicate document ingestion
- **Manual Folder Scanning**: On-demand scanning of existing files in watched folders
- **Statistics Tracking**: Monitor ingestion success, duplicates, and errors
- **Multi-Format Support**: Supports PDF, Office documents, text files, emails, and spreadsheets

## Supported File Types

The system automatically ingests the following file types:

- **PDF Documents**: `.pdf`
- **Text Files**: `.txt`
- **Email Files**: `.eml`
- **Excel Spreadsheets**: `.xlsx`, `.xls`
- **CSV Files**: `.csv`
- **Word Documents**: `.docx`, `.doc`

Files with other extensions are automatically skipped.

## Using the UI

### Adding a Watched Folder

1. Navigate to the **Settings** page
2. Locate the **Folder Watch** section
3. Enter the full path to the folder you want to monitor
4. Click the **Add Folder** button
5. The folder will appear in the watched folders list
6. A background watcher will automatically start monitoring the folder

**Example folder paths:**
- Linux/Mac: `/home/user/documents` or `/Users/user/Documents`
- Windows: `C:\Users\user\Documents`

### Removing a Watched Folder

1. Find the folder in the watched folders list
2. Click the **Remove** button next to the folder
3. The background watcher will stop, and the folder will be removed from monitoring

**Note**: Removing a folder does NOT delete previously ingested documents from the system.

### Manual Folder Scanning

To immediately ingest all existing files in a watched folder:

1. Locate the folder in the watched folders list
2. Click the **Scan Now** button
3. Wait for the scan to complete
4. View the scan results showing:
   - Total files found
   - Files successfully ingested
   - Duplicate files detected
   - Errors encountered

**When to use manual scanning:**
- After adding a new folder with existing files
- To re-check a folder for new files
- After moving files into a watched folder

### Viewing Statistics

The **Ingestion Statistics** section displays:

- **Total Unique Files**: Number of unique documents ingested
- **Total Duplicates Detected**: Number of duplicate files skipped
- **Files by Type**: Breakdown of ingested files by format
- **Recent Ingestions**: Latest file processing activity with status

Statistics update automatically after folder operations complete.

## Deduplication Mechanism

### How It Works

The system uses **SHA-256 cryptographic hashing** to identify duplicate files:

1. When a file is detected, the system calculates its SHA-256 hash
2. The hash is checked against the `file_hashes` database table
3. If the hash exists, the file is marked as a duplicate and skipped
4. If the hash is new, the file is parsed, embedded, and stored

### What Counts as a Duplicate

Two files are considered duplicates if they have **identical content**, even if:
- They have different filenames
- They are in different folders
- They were created at different times

### Duplicate Tracking

When a duplicate is detected:
- The `ingestion_count` is incremented in the database
- The `last_seen` timestamp is updated
- The file is logged with status `skipped_duplicate`
- No additional processing or storage occurs

### Benefits

- **Storage Efficiency**: Prevents redundant vector embeddings
- **Processing Speed**: Skips unnecessary parsing and embedding
- **Cost Savings**: Reduces API calls to embedding providers
- **Data Integrity**: Maintains single source of truth for each document

## API Endpoints

### POST /api/folder-watch/add

Add a new folder to the watch list.

**Request:**
```json
{
  "folder_path": "/path/to/folder"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Folder added successfully",
  "folder_path": "/path/to/folder"
}
```

**Error Responses:**
- `400 Bad Request`: Folder does not exist or path is not a directory
- `409 Conflict`: Folder is already being watched

**Example using curl:**
```bash
curl -X POST http://localhost:8000/api/folder-watch/add \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/home/user/documents"}'
```

**Example using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/folder-watch/add",
    json={"folder_path": "/home/user/documents"}
)
print(response.json())
```

### DELETE /api/folder-watch/remove

Remove a folder from the watch list.

**Request:**
```json
{
  "folder_path": "/path/to/folder"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Folder removed successfully"
}
```

**Error Response:**
- `404 Not Found`: Folder not found in watch list

**Example using curl:**
```bash
curl -X DELETE http://localhost:8000/api/folder-watch/remove \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/home/user/documents"}'
```

### GET /api/folder-watch/list

Get all watched folders with metadata.

**Success Response (200):**
```json
{
  "folders": [
    {
      "id": 1,
      "folder_path": "/home/user/documents",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00",
      "last_scan": "2024-01-15T14:20:00"
    }
  ]
}
```

**Example using curl:**
```bash
curl http://localhost:8000/api/folder-watch/list
```

**Example using Python:**
```python
import requests

response = requests.get("http://localhost:8000/api/folder-watch/list")
folders = response.json()["folders"]

for folder in folders:
    print(f"Watching: {folder['folder_path']}")
    print(f"  Active: {folder['is_active']}")
    print(f"  Last Scan: {folder['last_scan']}")
```

### POST /api/folder-watch/scan

Manually scan a folder for new files.

**Request:**
```json
{
  "folder_path": "/path/to/folder"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "total_files": 25,
  "ingested": 18,
  "duplicates": 5,
  "errors": 2,
  "message": "Scanned 25 files: 18 ingested, 5 duplicates, 2 errors"
}
```

**Error Response:**
- `400 Bad Request`: Folder does not exist or path is not a directory

**Example using curl:**
```bash
curl -X POST http://localhost:8000/api/folder-watch/scan \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/home/user/documents"}'
```

**Example using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/folder-watch/scan",
    json={"folder_path": "/home/user/documents"}
)

result = response.json()
print(f"Scanned {result['total_files']} files")
print(f"  Ingested: {result['ingested']}")
print(f"  Duplicates: {result['duplicates']}")
print(f"  Errors: {result['errors']}")
```

### GET /api/folder-watch/statistics

Get file ingestion statistics.

**Success Response (200):**
```json
{
  "total_files": 150,
  "total_duplicates": 23,
  "files_by_type": [
    {"type": "pdf", "count": 85},
    {"type": "xlsx", "count": 40},
    {"type": "txt", "count": 25}
  ],
  "recent_ingestions": [
    {
      "file_path": "/path/to/document.pdf",
      "status": "success",
      "chunks_created": 12,
      "timestamp": "2024-01-15T15:45:00"
    }
  ]
}
```

**Example using curl:**
```bash
curl http://localhost:8000/api/folder-watch/statistics
```

**Example using Python:**
```python
import requests

response = requests.get("http://localhost:8000/api/folder-watch/statistics")
stats = response.json()

print(f"Total Files: {stats['total_files']}")
print(f"Duplicates: {stats['total_duplicates']}")
print("\nFiles by Type:")
for file_type in stats['files_by_type']:
    print(f"  {file_type['type']}: {file_type['count']}")
```

## Background Watcher Management

### Automatic Startup

When the server starts, the system automatically:

1. Queries the database for all active watched folders
2. Starts a background watcher (Observer) for each folder
3. Monitors folders recursively (including subdirectories)
4. Logs the initialization status to the console

**Console output example:**
```
🔍 Initializing folder watchers...
✅ Started watcher for: /home/user/documents
✅ Started watcher for: /home/user/downloads
✅ Started 2 folder watchers
```

### How Watchers Work

Each background watcher:

- Uses the **watchdog** library to monitor filesystem events
- Detects file creation events in real-time
- Waits 1 second after file creation to ensure the file is fully written
- Automatically triggers ingestion for supported file types
- Applies deduplication logic before processing
- Logs all ingestion attempts to the database

### Watcher Lifecycle

**When a folder is added:**
- A new Observer is created and started immediately
- The Observer is stored in the `active_observers` dictionary
- Monitoring begins for the folder and all subdirectories

**When a folder is removed:**
- The Observer is stopped gracefully
- The Observer thread is joined (waits for completion)
- The Observer is removed from `active_observers`
- No further file events are processed

**On server shutdown:**
- All active Observers are stopped
- Observer threads are joined to ensure clean shutdown
- Console logs confirm each watcher has stopped

### Monitoring Watcher Status

Check server logs for watcher activity:

```
🔔 New file detected: report.pdf
📄 Processing: report.pdf
✅ Auto-ingestion successful: report.pdf
```

Or for duplicates:

```
🔔 New file detected: report.pdf
⏭️  Duplicate file skipped: report.pdf (original: report.pdf, first seen: 2024-01-15 10:30:00)
```

## Database Schema

### watched_folders Table

Stores registered folders for monitoring.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| folder_path | TEXT | Full path to folder (unique) |
| is_active | BOOLEAN | Whether folder is actively monitored |
| created_at | DATETIME | When folder was added |
| last_scan | DATETIME | Last manual scan timestamp |

### file_hashes Table

Stores SHA-256 hashes for deduplication.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| file_hash | TEXT | SHA-256 hash (unique) |
| original_filename | TEXT | Original filename |
| file_size | INTEGER | File size in bytes |
| file_type | TEXT | File extension |
| first_seen | DATETIME | First ingestion timestamp |
| last_seen | DATETIME | Most recent detection |
| ingestion_count | INTEGER | Number of times detected |
| doc_id | TEXT | Document ID in vector store |
| metadata | TEXT | JSON metadata |

### file_ingestion_log Table

Logs all ingestion attempts.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| file_path | TEXT | Full path to file |
| file_hash | TEXT | SHA-256 hash |
| status | TEXT | success, failed, or skipped_duplicate |
| error_message | TEXT | Error details if failed |
| chunks_created | INTEGER | Number of chunks created |
| timestamp | DATETIME | Ingestion attempt time |

## Troubleshooting

### Folder Not Being Watched

**Symptoms**: New files are not automatically ingested

**Solutions**:
1. Check that the folder exists and is accessible
2. Verify the folder appears in the watched folders list
3. Check server logs for watcher initialization errors
4. Restart the server to reinitialize watchers
5. Ensure the folder path is correct (absolute path)

### Files Not Being Ingested

**Symptoms**: Files are detected but not processed

**Solutions**:
1. Verify the file type is supported (see Supported File Types)
2. Check the file is not corrupted or empty
3. Review the `file_ingestion_log` table for error messages
4. Check server logs for parsing or embedding errors
5. Ensure embedding provider (OpenAI/Gemini) is configured correctly

### Duplicate Detection Not Working

**Symptoms**: Same file is ingested multiple times

**Solutions**:
1. Verify the file content is truly identical (not just same name)
2. Check the `file_hashes` table for the file's hash
3. Ensure the database is not being reset between ingestions
4. Review the `file_ingestion_log` for duplicate status entries

### High Memory Usage

**Symptoms**: Server memory increases over time

**Solutions**:
1. Limit the number of watched folders
2. Avoid watching folders with very large files
3. Monitor the number of active Observer threads
4. Restart the server periodically if needed

### Permission Errors

**Symptoms**: "Permission denied" errors in logs

**Solutions**:
1. Ensure the server process has read access to watched folders
2. Check folder permissions: `ls -la /path/to/folder`
3. Run the server with appropriate user permissions
4. Avoid watching system folders or restricted directories

## Best Practices

### Folder Selection

- Watch specific document folders, not entire drives
- Avoid watching temporary or cache directories
- Use dedicated folders for document ingestion
- Keep folder structures organized and shallow

### Performance Optimization

- Limit the number of simultaneously watched folders (< 10 recommended)
- Use manual scanning for one-time bulk imports
- Schedule bulk imports during off-peak hours
- Monitor ingestion statistics regularly

### Data Management

- Periodically review duplicate statistics
- Clean up old entries in `file_ingestion_log` if needed
- Back up the database before major operations
- Document your folder watching strategy

### Security Considerations

- Only watch folders with trusted content
- Validate folder paths before adding
- Restrict server access to authorized users
- Monitor ingestion logs for suspicious activity

## Advanced Usage

### Programmatic Folder Management

Create a Python script to manage multiple folders:

```python
import requests

BASE_URL = "http://localhost:8000/api/folder-watch"

def add_folders(folder_paths):
    """Add multiple folders to watch list."""
    for path in folder_paths:
        response = requests.post(
            f"{BASE_URL}/add",
            json={"folder_path": path}
        )
        result = response.json()
        print(f"{path}: {result['message']}")

def scan_all_folders():
    """Scan all watched folders."""
    response = requests.get(f"{BASE_URL}/list")
    folders = response.json()["folders"]
    
    for folder in folders:
        print(f"\nScanning: {folder['folder_path']}")
        scan_response = requests.post(
            f"{BASE_URL}/scan",
            json={"folder_path": folder['folder_path']}
        )
        result = scan_response.json()
        print(f"  {result['message']}")

# Example usage
folders_to_watch = [
    "/home/user/documents",
    "/home/user/downloads",
    "/home/user/reports"
]

add_folders(folders_to_watch)
scan_all_folders()
```

### Monitoring Script

Create a monitoring script to track ingestion activity:

```python
import requests
import time

def monitor_statistics(interval=60):
    """Monitor ingestion statistics at regular intervals."""
    while True:
        response = requests.get(
            "http://localhost:8000/api/folder-watch/statistics"
        )
        stats = response.json()
        
        print(f"\n=== Statistics at {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        print(f"Total Files: {stats['total_files']}")
        print(f"Duplicates: {stats['total_duplicates']}")
        print(f"Duplicate Rate: {stats['total_duplicates'] / max(stats['total_files'], 1) * 100:.1f}%")
        
        print("\nRecent Activity:")
        for ing in stats['recent_ingestions'][:5]:
            print(f"  {ing['status']}: {ing['file_path']}")
        
        time.sleep(interval)

# Monitor every 60 seconds
monitor_statistics(60)
```

## Related Documentation

- **QUICK_START_GUIDE.md**: General system setup and usage
- **DATABASE_RESET_GUIDE.md**: Database management and reset procedures
- **DEBUGGING_GUIDE.md**: Troubleshooting and debugging tips

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Inspect database tables for data integrity
4. Consult the design document at `.kiro/specs/folder-watch-auto-ingest/design.md`
