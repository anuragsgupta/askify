# Ollama LLM Setup - Local Answer Generation

## ✅ Successfully Configured!

Your backend now uses **Ollama (local)** as the primary LLM for answer generation, with **Gemini as fallback**.

## What Changed?

### Before (Gemini Only)
```python
# Always used Gemini API
client = genai.Client(api_key=api_key)
response = client.models.generate_content(...)
```

**Problems:**
- ❌ API quota limits (429 errors)
- ❌ Costs money after free tier
- ❌ Requires internet connection
- ❌ Slower (network latency)

### After (Ollama Primary, Gemini Fallback)
```python
# Try Ollama first (local, free, fast)
answer = generate_answer_ollama(prompt)

# Fallback to Gemini if Ollama fails
if not answer and api_key:
    answer = generate_answer_gemini(prompt, api_key)
```

**Benefits:**
- ✅ No API quota limits
- ✅ Completely free
- ✅ Works offline
- ✅ Faster (no network)
- ✅ Privacy (data stays local)

## Configuration

### Models Used

#### For Embeddings (Vector Search)
```
Model: nomic-embed-text
Dimension: 768
Purpose: Convert text to vectors for semantic search
```

#### For Answer Generation (LLM)
```
Primary: qwen3:4b-instruct-2507-q4_K_M (Ollama)
Fallback: gemini-2.0-flash (Gemini API)
```

### Why Qwen3?

**Qwen3:4b-instruct** is an excellent choice because:
- ✅ 4B parameters (good quality, reasonable size)
- ✅ Instruction-tuned (follows prompts well)
- ✅ Quantized (q4_K_M = 4-bit quantization)
- ✅ Fast inference (~5-10 seconds per query)
- ✅ Good at RAG tasks (citation, reasoning)
- ✅ Size: 2.5GB (fits in memory easily)

## Verification

### Test 1: Check Models Installed
```bash
ollama list
```

Expected output:
```
NAME                              ID              SIZE
qwen3:4b-instruct-2507-q4_K_M    0edcdef34593    2.5 GB
nomic-embed-text:latest          0a109f422b47    274 MB
```

### Test 2: Test Query
```bash
python3 test_ollama_query.py
```

Expected output:
```
✅ Query successful!
LLM Used: ollama (qwen3:4b-instruct-2507-q4_K_M)
```

### Test 3: Check Backend Logs
Look for these messages in backend terminal:
```
🤖 Trying Ollama (local) for answer generation...
✅ Ollama generation successful
```

## Performance Comparison

### Ollama (Local)
- **Speed:** 5-10 seconds per query
- **Cost:** $0 (free)
- **Quota:** Unlimited
- **Privacy:** Complete (data stays local)
- **Availability:** Works offline
- **Quality:** Good (4B parameter model)

### Gemini (Cloud)
- **Speed:** 2-3 seconds per query
- **Cost:** Free tier limited, then paid
- **Quota:** 1500 requests/day (free tier)
- **Privacy:** Data sent to Google
- **Availability:** Requires internet
- **Quality:** Excellent (large model)

## Usage

### Via Frontend
1. Open http://localhost:5173
2. Ask any question
3. System automatically uses Ollama
4. No API key needed!

### Via API
```bash
# No API key needed for Ollama
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main topics?",
    "n_results": 5
  }'
```

### With Gemini Fallback
```bash
# Include API key for Gemini fallback
curl -X POST http://localhost:8000/api/query \
  -H "x-api-key: YOUR_GEMINI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main topics?",
    "n_results": 5
  }'
```

## Fallback Behavior

### Scenario 1: Ollama Working (Normal)
```
1. User asks question
2. 🤖 Try Ollama
3. ✅ Ollama succeeds
4. Return answer
```

### Scenario 2: Ollama Down, Gemini Available
```
1. User asks question
2. 🤖 Try Ollama
3. ❌ Ollama fails (not running)
4. ⚠️  Fallback to Gemini
5. 🌐 Try Gemini
6. ✅ Gemini succeeds
7. Return answer
```

### Scenario 3: Both Fail
```
1. User asks question
2. 🤖 Try Ollama
3. ❌ Ollama fails
4. 🌐 Try Gemini
5. ❌ Gemini fails (no API key or quota exceeded)
6. Return error message with instructions
```

## Response Format

The API now includes `llm_used` field:

```json
{
  "answer": "The documents cover...",
  "sources": [...],
  "conflict_analysis": {...},
  "llm_used": "ollama (qwen3:4b-instruct-2507-q4_K_M)"
}
```

Possible values:
- `"ollama (qwen3:4b-instruct-2507-q4_K_M)"` - Ollama succeeded
- `"gemini (gemini-2.0-flash)"` - Gemini fallback used
- `"none (failed)"` - Both failed

## Troubleshooting

### "Ollama generation failed"

**Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

If not running:
```bash
ollama serve
```

**Check if model is installed:**
```bash
ollama list | grep qwen3
```

If not installed:
```bash
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

### Slow Response Times

**First query is always slower:**
- Model needs to load into memory
- Expect 15-20 seconds for first query
- Subsequent queries: 5-10 seconds

**If consistently slow:**
- Check CPU usage (Ollama is CPU-intensive)
- Consider smaller model: `ollama pull qwen3:1.5b`
- Or use Gemini fallback for speed

### "Both Ollama and Gemini failed"

**Check Ollama:**
```bash
ollama serve
```

**Check Gemini API key:**
```bash
# Set in frontend Settings or via header
x-api-key: YOUR_GEMINI_KEY
```

### Memory Issues

**Qwen3:4b uses ~4GB RAM:**
- If system has <8GB RAM, use smaller model
- Alternative: `ollama pull llama3.2:1b` (1.3GB)

## Advanced Configuration

### Change LLM Model

Edit `server/services/rag.py`:

```python
# Use different Ollama model
def generate_answer_ollama(prompt, model="llama3.2:3b"):
    ...
```

Available models:
- `qwen3:4b-instruct-2507-q4_K_M` (2.5GB, recommended)
- `llama3.2:3b` (2GB, faster)
- `llama3.2:1b` (1.3GB, fastest)
- `phi3:mini` (2.2GB, good quality)

### Disable Ollama (Use Only Gemini)

```python
# In query call
result = rag_query(question, api_key, use_ollama=False)
```

### Adjust Temperature

```python
# More creative (0.7)
answer = generate_answer_ollama(prompt, temperature=0.7)

# More deterministic (0.0, default)
answer = generate_answer_ollama(prompt, temperature=0.0)
```

### Increase Max Tokens

```python
# Generate longer answers
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": model,
        "prompt": prompt,
        "options": {
            "num_predict": 4096,  # Increased from 2048
        }
    }
)
```

## Files Modified

### 1. `server/services/rag.py` ✅
- Added `generate_answer_ollama()` function
- Added `generate_answer_gemini()` function
- Modified `rag_query()` to try Ollama first
- Added `llm_used` field to response

### 2. `server/routes/query.py` ✅
- Made `x-api-key` optional (not required for Ollama)
- Updated docstring

### 3. `test_ollama_query.py` ✅
- Created test script for Ollama queries

## Summary

**Problem:** Gemini API quota exceeded (429 errors)

**Solution:** Use Ollama (local) as primary LLM, Gemini as fallback

**Benefits:**
- ✅ No quota limits
- ✅ Free forever
- ✅ Works offline
- ✅ Privacy preserved
- ✅ Fast enough for RAG

**Status:** ✅ Working! Test showed successful query with Ollama

**Next:** Use your RAG system without worrying about API quotas!
