# Quick Start Guide

Get the SME Knowledge Agent running with your local Ollama setup in 5 minutes.

## Prerequisites

You already have:
- ✓ Ollama installed
- ✓ `phi3:mini` model (2.2 GB)
- ✓ `nomic-embed-text:latest` model (274 MB)

## Setup Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- LlamaIndex with Ollama support
- ChromaDB for vector storage
- Streamlit for the UI
- Document parsers (PDF, Excel, Email)

### 2. Verify Your Configuration

The `.env` file is already configured for Ollama:

```bash
cat .env
```

Should show:
```
LLM_PROVIDER=ollama
OLLAMA_LLM_MODEL=phi3:mini
OLLAMA_EMBED_MODEL=nomic-embed-text:latest
```

### 3. Test Your Setup

```bash
python test_local_llm.py
```

This verifies:
- Ollama is running and accessible
- Embedding generation works
- Query engine initializes correctly

Expected output:
```
✓ Ollama is running with 2 models
✓ Generated embedding with 768 dimensions
✓ Query engine created successfully
🎉 All tests passed!
```

### 4. Ingest Demo Data

```bash
python ingest_demo_data.py
```

This processes the demo documents in `data/`:
- Refund policies (PDF)
- Pricing spreadsheets (Excel)
- Customer emails (EML)

And stores them in ChromaDB with embeddings.

### 5. Launch the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

## Using the App

### Login Credentials

Default users (from `config.yaml`):

| Username | Password | Role |
|----------|----------|------|
| employee1 | password123 | Employee |
| admin1 | admin123 | Knowledge Manager |
| manager1 | manager123 | Team Lead |
| sysadmin | sysadmin123 | System Admin |

### Try These Queries

1. "What is the refund policy for defective products?"
2. "What was the pricing for TechStart in Q1 2024?"
3. "Show me emails about refund requests"
4. "Are there any conflicts in the refund policies?"

## Troubleshooting

### Ollama Not Running

```bash
# Check status
ollama list

# Start Ollama
ollama serve
```

### Models Missing

```bash
# Pull required models
ollama pull phi3:mini
ollama pull nomic-embed-text
```

### Slow Performance

Ollama runs locally, so speed depends on your hardware:
- First query: ~5-10 seconds (model loading)
- Subsequent queries: ~2-3 seconds
- Embeddings: ~1 second per document

For faster performance, consider:
- Using Gemini instead (see `LOCAL_LLM_SETUP.md`)
- Upgrading to a larger model like `phi3:medium`
- Running on a machine with more RAM/CPU

### Port Already in Use

If port 8501 is busy:

```bash
streamlit run app.py --server.port 8502
```

## Next Steps

- Read `LOCAL_LLM_SETUP.md` for Gemini setup
- Check `docs/GOOGLE_DRIVE_SETUP.md` for Drive integration
- Explore the codebase structure in `.kiro/steering/structure.md`

## Architecture Overview

```
User Query
    ↓
Streamlit UI (app.py)
    ↓
Query Engine (retrieval/query_engine.py)
    ↓
ChromaDB Vector Search (storage/chroma_store.py)
    ↓
Ollama Embeddings (nomic-embed-text)
    ↓
Retrieved Chunks + Metadata
    ↓
Ollama LLM (phi3:mini)
    ↓
Answer with Citations
```

## Performance Expectations

With Ollama on a typical laptop:
- Embedding generation: ~100 docs/minute
- Query response: 2-5 seconds
- Memory usage: ~3-4 GB
- Disk space: ~3 GB (models + ChromaDB)

Enjoy building with local LLMs! 🚀
