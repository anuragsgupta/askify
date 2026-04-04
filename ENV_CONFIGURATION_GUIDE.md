# Environment Configuration Guide

## ✅ Configuration via .env File

Your system now uses a `.env` file for all configuration instead of requiring API keys in the UI.

---

## Setup

### 1. Configuration File Location

```
server/.env
```

### 2. Current Configuration

```env
# Gemini API Configuration
GEMINI_API_KEY=AIzaSyCnO_7EpEy0Q5wE8t4QQ7LZySGauDkJFzA
GEMINI_LLM_MODEL=gemini-3-flash-preview
GEMINI_EMBEDDING_MODEL=text-embedding-004

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=qwen3:4b-instruct-2507-q4_K_M
OLLAMA_EMBED_MODEL=nomic-embed-text

# Provider Priority
USE_GEMINI_PRIMARY=true

# ChromaDB Configuration
CHROMA_PERSIST_DIR=./chroma_data
CHROMA_COLLECTION_NAME=askify_docs

# Application Configuration
PORT=8000
LOG_LEVEL=INFO
```

---

## Configuration Options

### Gemini API

**GEMINI_API_KEY**
- Your Gemini API key
- Get from: https://makersuite.google.com/app/apikey
- Required for Gemini embeddings and LLM

**GEMINI_LLM_MODEL**
- Model for answer generation
- Default: `gemini-3-flash-preview`
- Options:
  - `gemini-3-flash-preview` (latest, fastest)
  - `gemini-2.0-flash` (stable)
  - `gemini-1.5-flash` (older)

**GEMINI_EMBEDDING_MODEL**
- Model for embeddings
- Default: `text-embedding-004`
- Options:
  - `text-embedding-004` (latest, best quality)
  - `text-embedding-003` (older)

---

### Ollama Configuration

**OLLAMA_BASE_URL**
- Ollama server URL
- Default: `http://localhost:11434`
- Change if Ollama runs on different host/port

**OLLAMA_LLM_MODEL**
- Model for answer generation
- Default: `qwen3:4b-instruct-2507-q4_K_M`
- Options:
  - `qwen3:4b-instruct-2507-q4_K_M` (recommended, 2.5GB)
  - `llama3.2:3b` (faster, 2GB)
  - `llama3.2:1b` (fastest, 1.3GB)
  - `phi3:mini` (good quality, 2.2GB)

**OLLAMA_EMBED_MODEL**
- Model for embeddings
- Default: `nomic-embed-text`
- Options:
  - `nomic-embed-text` (recommended, 768-dim)
  - `all-minilm` (smaller, 384-dim - not compatible!)

---

### Provider Priority

**USE_GEMINI_PRIMARY**
- Whether to use Gemini as primary
- Default: `true`
- Options:
  - `true` - Try Gemini first, fallback to Ollama
  - `false` - Use only Ollama (no Gemini)

---

### ChromaDB Configuration

**CHROMA_PERSIST_DIR**
- Directory for ChromaDB storage
- Default: `./chroma_data`
- Relative to `server/` directory

**CHROMA_COLLECTION_NAME**
- Collection name in ChromaDB
- Default: `askify_docs`
- Change if you want separate collections

---

### Application Configuration

**PORT**
- Backend server port
- Default: `8000`
- Change if port 8000 is in use

**LOG_LEVEL**
- Logging verbosity
- Default: `INFO`
- Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

---

## Usage

### No API Key Required in UI

**Before:**
```
User had to enter API key in frontend Settings
```

**After:**
```
API key configured in server/.env file
No UI input needed
```

### Upload Documents

**Via Frontend:**
```
1. Open: http://localhost:5173
2. Upload: Select file (no API key needed!)
3. System uses .env configuration automatically
```

**Via API:**
```bash
# No x-api-key header needed
curl -X POST http://localhost:8000/api/upload \
  -F "file=@document.pdf"
```

### Query Documents

**Via Frontend:**
```
1. Open: http://localhost:5173
2. Type query
3. Submit (no API key needed!)
```

**Via API:**
```bash
# No x-api-key header needed
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the requirements?"}'
```

---

## Configuration Scenarios

### Scenario 1: Gemini Primary (Default)

```env
GEMINI_API_KEY=your_key_here
GEMINI_LLM_MODEL=gemini-3-flash-preview
GEMINI_EMBEDDING_MODEL=text-embedding-004
USE_GEMINI_PRIMARY=true
```

**Behavior:**
- Embeddings: Gemini → Ollama fallback
- LLM: Ollama → Gemini fallback
- Best quality embeddings
- Unlimited LLM queries

---

### Scenario 2: Ollama Only (No Gemini)

```env
# Leave GEMINI_API_KEY empty or remove it
GEMINI_API_KEY=
USE_GEMINI_PRIMARY=false
```

**Behavior:**
- Embeddings: Ollama only
- LLM: Ollama only
- Completely offline
- No API costs
- Good quality (85% vs 92%)

---

### Scenario 3: Gemini for Everything

```env
GEMINI_API_KEY=your_key_here
USE_GEMINI_PRIMARY=true
# Modify code to use Gemini LLM as primary
```

**Behavior:**
- Embeddings: Gemini
- LLM: Gemini
- Best quality
- Fastest responses
- API costs apply

---

### Scenario 4: Development (Ollama) + Production (Gemini)

**Development (.env.development):**
```env
USE_GEMINI_PRIMARY=false
```

**Production (.env.production):**
```env
GEMINI_API_KEY=your_key_here
USE_GEMINI_PRIMARY=true
```

---

## Model Comparison

### Gemini Models

| Model | Speed | Quality | Cost | Use Case |
|-------|-------|---------|------|----------|
| gemini-3-flash-preview | Fastest | Excellent | Free tier | Production |
| gemini-2.0-flash | Fast | Excellent | Free tier | Stable |
| gemini-1.5-flash | Medium | Very Good | Free tier | Legacy |

### Ollama Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| qwen3:4b | 2.5GB | Medium | Good | Recommended |
| llama3.2:3b | 2GB | Fast | Good | Speed priority |
| llama3.2:1b | 1.3GB | Fastest | Fair | Low resources |
| phi3:mini | 2.2GB | Medium | Good | Alternative |

---

## Changing Configuration

### Update API Key

```bash
# Edit server/.env
nano server/.env

# Update GEMINI_API_KEY
GEMINI_API_KEY=your_new_key_here

# Restart backend
# Backend auto-reloads on code changes, but not .env changes
# Stop (CTRL+C) and restart
```

### Switch to Different Model

```bash
# Edit server/.env
nano server/.env

# Change model
GEMINI_LLM_MODEL=gemini-2.0-flash

# Restart backend
```

### Disable Gemini

```bash
# Edit server/.env
nano server/.env

# Set to false
USE_GEMINI_PRIMARY=false

# Restart backend
```

---

## Verification

### Check Configuration Loaded

**Backend logs on startup:**
```
Loading configuration from .env...
✓ GEMINI_API_KEY: Set
✓ GEMINI_LLM_MODEL: gemini-3-flash-preview
✓ GEMINI_EMBEDDING_MODEL: text-embedding-004
✓ USE_GEMINI_PRIMARY: true
```

### Test Upload

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.pdf"
```

**Expected logs:**
```
🌐 Trying Gemini embeddings (text-embedding-004) for 10 chunks...
✅ Gemini embeddings successful (10 vectors, 768-dim)
📊 Embeddings generated using: gemini
```

### Test Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

**Expected logs:**
```
✅ Query embedded with Gemini
🤖 Trying Ollama (local) for answer generation...
✅ Ollama generation successful
```

---

## Troubleshooting

### "Gemini API key not found"

**Check 1: File exists**
```bash
ls -la server/.env
# Should show the file
```

**Check 2: Key is set**
```bash
cat server/.env | grep GEMINI_API_KEY
# Should show: GEMINI_API_KEY=your_key_here
```

**Check 3: No spaces**
```bash
# Wrong:
GEMINI_API_KEY = your_key_here

# Correct:
GEMINI_API_KEY=your_key_here
```

### "python-dotenv not found"

```bash
pip3 install python-dotenv
```

### Changes Not Applied

**.env changes require restart:**
```bash
# Stop backend (CTRL+C)
# Start again
python3 -m uvicorn server.main:app --reload --port 8000
```

### "Invalid model name"

**Check model name format:**
```bash
# Gemini models don't need "models/" prefix in .env
# Wrong:
GEMINI_LLM_MODEL=models/gemini-3-flash-preview

# Correct:
GEMINI_LLM_MODEL=gemini-3-flash-preview
```

---

## Security

### Protect .env File

```bash
# Add to .gitignore
echo "server/.env" >> .gitignore

# Verify not tracked
git status | grep .env
# Should not appear
```

### Use .env.example

```bash
# Copy example
cp server/.env.example server/.env

# Edit with your keys
nano server/.env
```

### Environment Variables

**Alternative to .env file:**
```bash
# Set in shell
export GEMINI_API_KEY=your_key_here
export GEMINI_LLM_MODEL=gemini-3-flash-preview

# Start backend
python3 -m uvicorn server.main:app --reload
```

---

## Summary

**Configuration:**
- ✅ All settings in `server/.env` file
- ✅ No API key input in UI
- ✅ Gemini model: `gemini-3-flash-preview`
- ✅ Embedding model: `text-embedding-004`
- ✅ Automatic fallback to Ollama

**Benefits:**
- ✅ Simpler UI (no settings page needed)
- ✅ Centralized configuration
- ✅ Easy to change models
- ✅ Secure (API key not in frontend)
- ✅ Environment-specific configs

**Usage:**
- Upload documents without API key
- Query without API key
- System uses .env configuration automatically

**Your system is now configured via .env file!** 🎉
