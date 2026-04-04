# Debugging Guide - Gemini Primary System

## Issue Fixed: .env File Not Loading

### Problem
The backend was showing "Gemini API Key: ❌ NOT SET" even though the API key was in `server/.env`.

### Root Cause
The backend runs from the project root directory, but `load_dotenv()` was looking for `.env` in the current working directory instead of the `server/` directory.

### Solution
Updated all services to use explicit path to `server/.env`:

```python
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'  # or Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
```

### Files Updated
1. `server/main.py` - Added explicit .env path loading
2. `server/services/embeddings.py` - Added explicit .env path loading
3. `server/services/rag.py` - Added explicit .env path loading

---

## Debugging Features Added

### 1. Startup Configuration Display

When the backend starts, you'll now see:

```
============================================================
🚀 ASKIFY RAG BACKEND STARTING
============================================================
📌 Working Directory: /path/to/project
📌 .env path: /path/to/project/server/.env
📌 .env file exists: True
📌 GEMINI_API_KEY loaded: ✅ YES
📌 GEMINI_API_KEY value: AIzaSyCnO_7EpEy0Q5wE...
📌 USE_GEMINI_PRIMARY: true
📌 USE_GEMINI_LLM_PRIMARY: true
📌 GEMINI_LLM_MODEL: gemini-3-flash-preview
📌 GEMINI_EMBEDDING_MODEL: text-embedding-004
============================================================
```

### 2. Service Configuration Display

Each service (embeddings, RAG) shows its configuration:

```
============================================================
🔧 EMBEDDINGS SERVICE CONFIGURATION
============================================================
📌 .env path: /path/to/project/server/.env
📌 .env exists: True
📌 Gemini API Key: ✅ SET
📌 Gemini API Key (first 20 chars): AIzaSyCnO_7EpEy0Q5wE...
📌 Gemini Embedding Model: text-embedding-004
📌 Ollama Embed Model: nomic-embed-text
📌 USE_GEMINI_PRIMARY: True
📌 Provider Priority: Gemini → Ollama
============================================================
```

### 3. Upload Process Debugging

When uploading a file, you'll see detailed logs:

```
============================================================
📊 EMBEDDING REQUEST
============================================================
Chunks to process: 5
Use Gemini Primary: True
Provider Priority: Gemini → Ollama
============================================================

🌐 GEMINI EMBEDDINGS - Starting
   Model: text-embedding-004
   Chunks to embed: 5
   Chunk 1/5: 1234 tokens, 4936 chars
   ✅ Chunk 1 embedded successfully (768-dim)
   Chunk 2/5: 987 tokens, 3948 chars
   ✅ Chunk 2 embedded successfully (768-dim)
   ...
✅ GEMINI EMBEDDINGS - Success (5 vectors)

============================================================
📊 EMBEDDING COMPLETE
============================================================
Provider used: GEMINI
Vectors generated: 5
============================================================
```

### 4. Query Process Debugging

When asking a question, you'll see:

```
============================================================
🤖 RAG QUERY PIPELINE
============================================================
Question: What courses are available?
Use Gemini LLM Primary: True
Provider Priority: Gemini → Ollama
============================================================

📍 Step 1: Embedding query...
✅ Query embedded with Gemini

📍 Step 2: Retrieving relevant chunks from ChromaDB...
   Retrieved 10 chunks

📍 Step 3: Running conflict detection...
   ✅ No conflicts detected

📍 Step 4: Building prompt and generating answer...
   Prompt built: 5432 chars (~1358 tokens)
   Context chunks: 10

============================================================
🤖 LLM GENERATION
============================================================
Use Gemini Primary: True
============================================================

🌐 GEMINI LLM - Starting generation
   Model: gemini-3-flash-preview
   Prompt length: 5432 chars (~1358 tokens)
✅ GEMINI LLM - Success (generated 456 chars)

============================================================
✅ RAG QUERY COMPLETE
============================================================
LLM used: gemini (gemini-3-flash-preview)
Sources: 3
Conflicts: False
============================================================
```

### 5. File Parsing Debugging

When parsing files, you'll see:

```
📄 PARSING EXCEL: BCA MCA list.xlsx
   Max tokens per chunk: 6000

   📊 Processing sheet: Sheet1
      Columns: 5
      Data rows: 150
      ✅ Chunk 1: Rows 1-50 (4523 tokens)
      ✅ Chunk 2: Rows 51-100 (4789 tokens)
      ✅ Chunk 3: Rows 101-150 (3456 tokens)

   🔍 Validating chunks...
   ✅ Excel parsing complete: 3 chunks created
```

### 6. Error Detection

If chunks are too large:

```
⚠️  CHUNK TOO LARGE: 8500 tokens (max: 8000)
   Text length: 34000 chars
   First 100 chars: Sheet: Sheet1
Columns: Name, Email, Phone...
```

If Gemini fails:

```
❌ GEMINI EMBEDDINGS - Failed: 401 Unauthorized
   Falling back to Ollama...

🤖 OLLAMA EMBEDDINGS - Starting
   Model: nomic-embed-text
   ...
✅ OLLAMA EMBEDDINGS - Success (5 vectors)
```

---

## How to Use Debugging Output

### 1. Verify Configuration on Startup

Look for these lines when backend starts:

```
✅ GOOD:
📌 GEMINI_API_KEY loaded: ✅ YES
📌 USE_GEMINI_PRIMARY: true
📌 USE_GEMINI_LLM_PRIMARY: true

❌ BAD:
📌 GEMINI_API_KEY loaded: ❌ NO
📌 .env file exists: False
```

### 2. Verify Gemini is Being Used

During upload, look for:

```
✅ GOOD:
🌐 GEMINI EMBEDDINGS - Starting
✅ GEMINI EMBEDDINGS - Success

❌ BAD (Fallback Active):
⚠️  Gemini embeddings failed: [error]
🤖 OLLAMA EMBEDDINGS - Starting
```

During query, look for:

```
✅ GOOD:
🌐 GEMINI LLM - Starting generation
✅ GEMINI LLM - Success

❌ BAD (Fallback Active):
❌ GEMINI LLM - Failed: [error]
🤖 OLLAMA LLM - Starting generation
```

### 3. Check for Preprocessing Issues

Look for warnings about large chunks:

```
⚠️  Row 45: Truncating long value (1200 chars → 500 chars)
⚠️  Chunk 3 too large (7800 tokens), splitting further...
```

These indicate the preprocessing is working to prevent errors.

### 4. Verify Provider Used

At the end of each operation:

```
Provider used: GEMINI  ← Good!
Provider used: OLLAMA  ← Fallback was used
```

---

## Common Issues and Solutions

### Issue 1: API Key Not Loading

**Symptoms:**
```
📌 GEMINI_API_KEY loaded: ❌ NO
```

**Solutions:**
1. Check `server/.env` file exists
2. Verify API key is set: `GEMINI_API_KEY=your_key_here`
3. Restart backend to reload configuration
4. Check file permissions on `server/.env`

### Issue 2: Gemini Always Failing

**Symptoms:**
```
❌ GEMINI EMBEDDINGS - Failed: 401 Unauthorized
```

**Solutions:**
1. Verify API key is valid at https://aistudio.google.com
2. Check API key has correct permissions
3. Verify no quota limits exceeded
4. Check internet connectivity

### Issue 3: Chunks Too Large

**Symptoms:**
```
⚠️  CHUNK TOO LARGE: 8500 tokens (max: 8000)
```

**Solutions:**
1. System should automatically split chunks
2. Check preprocessing is working
3. Verify MAX_TOKENS is set correctly (6000)
4. Check if file has extremely long rows/pages

### Issue 4: Ollama Always Used Instead of Gemini

**Symptoms:**
```
Provider used: OLLAMA
```

**Solutions:**
1. Check `USE_GEMINI_PRIMARY=true` in `.env`
2. Verify Gemini API key is set
3. Check backend logs for Gemini errors
4. Restart backend to reload configuration

---

## Testing Checklist

### ✅ Configuration Test
```bash
# Start backend and check output
./start_backend.sh

# Look for:
# ✅ GEMINI_API_KEY loaded: ✅ YES
# ✅ USE_GEMINI_PRIMARY: true
# ✅ USE_GEMINI_LLM_PRIMARY: true
```

### ✅ Upload Test
```bash
# Upload a file and check logs

# Look for:
# ✅ 🌐 GEMINI EMBEDDINGS - Starting
# ✅ Provider used: GEMINI
```

### ✅ Query Test
```bash
# Ask a question and check logs

# Look for:
# ✅ 🌐 GEMINI LLM - Starting generation
# ✅ LLM used: gemini (gemini-3-flash-preview)
```

### ✅ Preprocessing Test
```bash
# Upload a large Excel file

# Look for:
# ✅ 📄 PARSING EXCEL: filename.xlsx
# ✅ Chunk 1: Rows 1-50 (4523 tokens)
# ✅ Excel parsing complete: X chunks created
```

---

## Debug Log Levels

### Startup Logs (Always Shown)
- Backend configuration
- Service configuration
- .env file loading status

### Operation Logs (Always Shown)
- Embedding requests
- Query pipeline steps
- File parsing progress
- Provider selection

### Detailed Logs (Always Shown)
- Individual chunk processing
- Token counts
- Chunk validation
- Error messages

### Success Indicators
- ✅ Green checkmarks for success
- 🌐 Globe for Gemini operations
- 🤖 Robot for Ollama operations
- 📊 Chart for statistics
- 📄 Document for file operations

### Warning Indicators
- ⚠️  Yellow warning for non-critical issues
- Preprocessing warnings
- Fallback activation

### Error Indicators
- ❌ Red X for failures
- API errors
- Configuration errors
- Processing errors

---

## Quick Debug Commands

### Check .env File
```bash
cat server/.env
```

### Verify API Key
```bash
python3 -c "from dotenv import load_dotenv; import os; from pathlib import Path; load_dotenv(Path('server/.env')); print('API Key:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

### Test Gemini API
```bash
python3 -c "from google import genai; from dotenv import load_dotenv; import os; from pathlib import Path; load_dotenv(Path('server/.env')); client = genai.Client(api_key=os.getenv('GEMINI_API_KEY')); print('Gemini API:', 'OK' if client else 'FAIL')"
```

### Check Ollama Status
```bash
ollama list
```

---

## Status: READY FOR TESTING

All debugging features are now active. When you restart the backend, you'll see:

1. ✅ Configuration display on startup
2. ✅ Detailed embedding logs
3. ✅ Detailed query logs
4. ✅ File parsing progress
5. ✅ Provider selection logs
6. ✅ Error detection and warnings
7. ✅ Preprocessing logs for long files

**Next Action**: Restart backend and test upload to see the new debugging output!
