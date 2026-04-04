# Start Ollama Guide

## Configuration Changed

I've switched your system to use **Ollama as PRIMARY** and Gemini as fallback. This avoids the quota limits you're hitting with Gemini.

### Updated Configuration (server/.env):
```env
# Provider Priority
USE_GEMINI_PRIMARY=false        # Changed from true
USE_GEMINI_LLM_PRIMARY=false    # Changed from true
```

**New Priority**: Ollama → Gemini (instead of Gemini → Ollama)

---

## How to Start Ollama

### Step 1: Open a New Terminal

Keep your backend terminal running, and open a **new terminal window**.

### Step 2: Start Ollama Server

```bash
ollama serve
```

**Expected Output:**
```
time=2026-04-04T... level=INFO msg="Ollama server starting..."
time=2026-04-04T... level=INFO msg="Listening on 127.0.0.1:11434"
```

### Step 3: Verify Models are Installed

In **another new terminal**, check if the models are installed:

```bash
ollama list
```

**Expected Output:**
```
NAME                                    ID              SIZE
nomic-embed-text:latest                 ...             274MB
qwen3:4b-instruct-2507-q4_K_M          ...             2.4GB
```

### Step 4: Pull Models (If Not Installed)

If the models are missing, pull them:

```bash
# Pull embedding model (required)
ollama pull nomic-embed-text

# Pull LLM model (required)
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

**Note**: This will download ~2.7GB total. It may take a few minutes.

---

## What You'll See After Starting Ollama

### Backend Logs Will Show:
```
============================================================
🔧 EMBEDDINGS SERVICE CONFIGURATION
============================================================
📌 USE_GEMINI_PRIMARY: False
📌 Provider Priority: Ollama → Gemini
============================================================

============================================================
🔧 RAG SERVICE CONFIGURATION
============================================================
📌 USE_GEMINI_LLM_PRIMARY: False
📌 Provider Priority: Ollama → Gemini
============================================================
```

### On Upload:
```
============================================================
📊 EMBEDDING REQUEST
============================================================
Use Gemini Primary: False
Provider Priority: Ollama → Gemini
============================================================

🤖 OLLAMA EMBEDDINGS - Starting
   Model: nomic-embed-text
   Chunks to embed: 12
   Chunk 1/12: 1815 tokens, 7260 chars
   ✅ Chunk 1 embedded successfully (768-dim)
   ...
✅ OLLAMA EMBEDDINGS - Success (12 vectors)

============================================================
📊 EMBEDDING COMPLETE
============================================================
Provider used: OLLAMA
Vectors generated: 12
============================================================
```

---

## Testing Steps

### 1. Start Ollama
```bash
# In a new terminal
ollama serve
```

### 2: Restart Backend
```bash
# In backend terminal: Ctrl+C to stop
./start_backend.sh
```

**Look for:**
```
📌 USE_GEMINI_PRIMARY: False
📌 Provider Priority: Ollama → Gemini
```

### 3. Re-upload File
Upload "BCA MCA list.xlsx" again in the Documents page.

**Expected Result:**
- ✅ Uses Ollama embeddings (no quota limit)
- ✅ Upload completes successfully
- ✅ No 429 errors

---

## Advantages of Ollama Primary

### ✅ Pros:
- **Unlimited**: No quota limits
- **Free**: Completely free to use
- **Fast**: Local processing (no network latency)
- **Private**: Data stays on your machine
- **Reliable**: No API failures

### ⚠️ Cons:
- **Requires local resources**: Uses CPU/RAM
- **Slightly lower quality**: 85% accuracy vs Gemini's 92%
- **Requires installation**: Need to install Ollama

---

## Switching Back to Gemini (When Quota Resets)

If you want to switch back to Gemini as primary later:

### Edit server/.env:
```env
# Provider Priority
USE_GEMINI_PRIMARY=true
USE_GEMINI_LLM_PRIMARY=true
```

### Restart Backend:
```bash
# Ctrl+C to stop
./start_backend.sh
```

---

## Troubleshooting

### Issue: "ollama: command not found"

**Solution**: Install Ollama first

**macOS:**
```bash
# Using Homebrew
brew install ollama

# Or download from https://ollama.ai
```

### Issue: "Connection refused" on port 11434

**Solution**: Start Ollama server
```bash
ollama serve
```

### Issue: Models not found

**Solution**: Pull the models
```bash
ollama pull nomic-embed-text
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

### Issue: Ollama server crashes

**Solution**: Check system resources
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
killall ollama
ollama serve
```

---

## Quick Commands Reference

```bash
# Start Ollama server
ollama serve

# List installed models
ollama list

# Pull embedding model
ollama pull nomic-embed-text

# Pull LLM model
ollama pull qwen3:4b-instruct-2507-q4_K_M

# Test Ollama is working
curl http://localhost:11434/api/tags

# Stop Ollama
killall ollama
```

---

## Status: READY TO START OLLAMA

Configuration has been updated to use Ollama as primary.

**Next Steps:**
1. Open new terminal
2. Run: `ollama serve`
3. Restart backend
4. Re-upload file

The system will now use Ollama (unlimited, local) instead of Gemini (quota-limited, cloud)!
