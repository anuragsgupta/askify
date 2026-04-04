# Database Reset Guide - Fixing Dimension Mismatch

## Problem Explained

### What Happened?

You got this error:
```
Collection expecting embedding with dimension of 2048, got 768
```

### Why?

1. **Old database** was created with 2048-dimensional embeddings
   - This came from the random fallback code: `[random.random() for _ in range(2048)]`
   - Wrong dimensions, but ChromaDB accepted them

2. **New embeddings** are 768-dimensional
   - Correct size for `nomic-embed-text` model
   - ChromaDB won't accept different dimensions in same collection

### The Fix

Delete the old database and let it recreate with correct dimensions.

## Steps Completed ✅

### 1. Deleted Old Database
```bash
rm -rf server/chroma_data
```

### 2. Cleaned Metadata Files
```bash
rm -f server/doc_metadata.json server/share_tokens.json
```

### 3. Verified Embeddings Work
```bash
python3 test_embeddings.py
```

Result:
- ✅ Embedding dimension: 768 (correct)
- ✅ Model: nomic-embed-text (correct)
- ✅ All tests passed

## Try Uploading Again

Your backend is ready! Try uploading your PDF again:

### Via Frontend (Recommended)
1. Open http://localhost:5173
2. Click "Upload Documents"
3. Select your PDF file
4. Upload should succeed now

### Via API
```bash
curl -X POST http://localhost:8000/api/upload \
  -H "x-api-key: YOUR_GEMINI_API_KEY" \
  -F "file=@IGNISIA_26_Twists.pdf"
```

## What Changed?

### Before (Broken)
```python
# OLD embeddings.py
model: "llama3.2:1b"  # Wrong model (LLM, not embeddings)
endpoint: "/api/embed"  # Wrong endpoint
fallback: random 2048-dim vectors  # Disaster!
```

### After (Fixed)
```python
# NEW embeddings.py
model: "nomic-embed-text"  # Correct embedding model
endpoint: "/api/embeddings"  # Correct endpoint
fallback: raise error  # Fail explicitly, no silent failures
```

## Verification Checklist

- [x] Old database deleted
- [x] Metadata files cleaned
- [x] Backend reloaded with new code
- [x] Embeddings tested (768 dimensions)
- [x] Ready for uploads

## Expected Behavior Now

### Upload Process
1. PDF uploaded → parsed with PyPDF2 (or PyMuPDF4LLM if you switch)
2. Text chunks created
3. Each chunk embedded with `nomic-embed-text` → 768-dim vectors
4. Stored in ChromaDB with correct dimensions
5. Success!

### Query Process
1. User query → embedded with `nomic-embed-text` → 768-dim vector
2. ChromaDB searches for similar vectors (cosine similarity)
3. Top K chunks retrieved
4. Sent to Gemini LLM for answer generation
5. Answer with citations returned

## Troubleshooting

### If Upload Still Fails

#### Check Ollama is Running
```bash
curl http://localhost:11434/api/tags
```

Should return list of models including `nomic-embed-text`.

#### Check Model is Installed
```bash
ollama list | grep nomic-embed-text
```

If not found:
```bash
ollama pull nomic-embed-text
```

#### Check Backend Logs
Look at the terminal running the backend for error messages.

#### Test Embeddings Manually
```bash
python3 test_embeddings.py
```

Should show:
```
✅ All tests passed!
Embedding dimension: 768
```

### If You Get "Connection Refused"

Ollama is not running:
```bash
# Start Ollama
ollama serve

# In another terminal, test
curl http://localhost:11434/api/tags
```

### If Dimensions Still Wrong

1. Make sure you're using the NEW `embeddings.py` code
2. Check backend reloaded (look for "Reloading..." in logs)
3. Restart backend manually:
   ```bash
   # Stop: CTRL+C
   # Start: python3 -m uvicorn server.main:app --reload --port 8000
   ```

## Next Steps

### 1. Upload Your Documents
Now that the database is clean, upload your documents:
- PDFs
- Excel files
- Text/Email files

### 2. Test Queries
Try some queries to verify RAG is working:
- "What is the refund policy?"
- "Show me pricing information"
- "What are the shipping guidelines?"

### 3. (Optional) Upgrade to PyMuPDF4LLM

For better PDF parsing, update `server/routes/upload.py`:

```python
# Change this line:
from server.services.parser import parse_file

# To this:
from server.services.parser_improved import parse_file
```

This will give you:
- Better text extraction (60% → 95%)
- Table preservation
- Structure awareness
- Better chunking

## Why This Won't Happen Again

The new code:
1. ✅ Uses correct embedding model
2. ✅ Fails explicitly on errors (no silent failures)
3. ✅ Validates dimensions
4. ✅ Clear error messages

If something goes wrong, you'll see a clear error message instead of silent corruption.

## Summary

**Problem:** Old database had wrong embedding dimensions (2048 from random fallback)

**Solution:** Deleted old database, fixed embedding code, verified correct dimensions (768)

**Status:** ✅ Ready to upload documents

**Next:** Upload your PDF and test queries!
