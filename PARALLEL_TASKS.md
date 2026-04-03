# Parallel Task Execution Plan

## Currently In Progress
- **Task 6**: ChromaDB storage layer (Other laptop)
- **Task 7**: Google Drive fetcher (This laptop)

## Tasks You Can Do in Parallel (No Conflicts)

### ✅ Task 8: Gmail API Integration
**File**: `ingestion/email_parser.py` (add function to existing file)
**Dependencies**: None (uses existing email parser)
**Conflicts**: ❌ None
**Why safe**: 
- Adds function to existing `email_parser.py`
- Independent of Task 6 (storage) and Task 7 (Drive)
- Only depends on completed Task 4 (email parser)

---

### ✅ Task 20: Create Demo Data
**Files**: `data/` directory (new sample documents)
**Dependencies**: None (just creating files)
**Conflicts**: ❌ None
**Why safe**:
- Creates sample PDFs, Excel files, EML files in `data/` folder
- Completely independent - just file creation
- No code dependencies

**Sub-tasks you can do now:**
- ✅ 20.1: Create sample documents in `data/` directory
  - Add 2-3 policy PDFs with version conflicts
  - Add 1-2 pricing Excel files with client data
  - Add 2-3 EML files with email threads

---

### ✅ Task 21.4: Documentation and README
**Files**: `README.md`, `.env.example`
**Dependencies**: None
**Conflicts**: ❌ None
**Why safe**:
- Updates documentation files
- No code dependencies
- Independent of all other tasks

---

## Tasks You CANNOT Do Yet (Have Dependencies)

### ❌ Task 9: Checkpoint - Storage layer tests
**Reason**: Depends on Task 6 completion

### ❌ Task 10: Query engine with LlamaIndex
**Reason**: Depends on Task 6 (needs ChromaDB storage)
**Files**: `retrieval/query_engine.py`

### ❌ Task 11: Conflict detection middleware
**Reason**: Depends on Task 10 (needs query engine)
**Files**: `retrieval/conflict_detector.py`

### ❌ Task 12: Checkpoint - Retrieval layer tests
**Reason**: Depends on Tasks 10 and 11

### ❌ Task 13-17: Streamlit UI tasks
**Reason**: Depend on Tasks 6, 10, 11 (need storage, query engine, conflict detection)
**Files**: `app.py`

### ❌ Task 18: Team lead conflict audit dashboard
**Reason**: Depends on Task 11 (conflict detection)

### ❌ Task 19: Checkpoint - UI tests
**Reason**: Depends on Tasks 13-17

### ❌ Task 20.2: Run ingestion pipeline
**Reason**: Depends on Task 6 (needs ChromaDB to store embeddings)

### ❌ Task 20.3: Verify demo queries
**Reason**: Depends on Tasks 6, 10 (needs storage and query engine)

### ❌ Task 21.1: End-to-end integration tests
**Reason**: Depends on all previous tasks

### ❌ Task 21.2: Performance testing
**Reason**: Depends on Tasks 6, 10 (needs full system)

### ❌ Task 21.3: Error handling and logging
**Reason**: Should be done after main features are complete

### ❌ Task 22: Final checkpoint
**Reason**: Depends on all tasks

---

## Recommended Parallel Work Plan

### Laptop 1 (Other laptop)
- ✅ Task 6: ChromaDB storage layer

### Laptop 2 (This laptop)
- ✅ Task 7: Google Drive fetcher (in progress)
- ✅ Task 8: Gmail API integration (can start now)
- ✅ Task 20.1: Create demo data (can start now)
- ✅ Task 21.4: Documentation (can start now)

### After Tasks 6 & 7 Complete
**Either laptop can do:**
- Task 10: Query engine (depends on Task 6)
- Task 11: Conflict detection (depends on Task 10)
- Tasks 13-17: Streamlit UI (depends on Tasks 6, 10, 11)
- Task 20.2-20.3: Demo pipeline (depends on Task 6, 10)

---

## Summary

**Safe to do NOW on this laptop (while Task 6 & 7 are in progress):**
1. ✅ **Task 8**: Gmail API integration
2. ✅ **Task 20.1**: Create demo data files
3. ✅ **Task 21.4**: Update documentation

**Total: 3 tasks** can be done in parallel without any conflicts!

---

## Git Merge Strategy

When merging work from both laptops:

1. **No conflicts expected** because:
   - Task 6 creates: `storage/chroma_store.py`
   - Task 7 creates: `ingestion/drive_fetcher.py`
   - Task 8 modifies: `ingestion/email_parser.py` (adds function)
   - Task 20.1 creates: files in `data/` directory
   - Task 21.4 modifies: `README.md`, `.env.example`

2. **All different files/directories** - clean merge!

3. **Merge order** (recommended):
   ```bash
   # On main branch
   git merge task-6-chromadb
   git merge task-7-drive-fetcher
   git merge task-8-gmail-api
   git merge task-20-demo-data
   git merge task-21-docs
   ```
