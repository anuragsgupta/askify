# Local LLM Setup Guide

This project now supports both Ollama (local) and Gemini as alternatives to OpenAI.

## Quick Start with Ollama

You already have Ollama installed with the required models:
- `phi3:mini` - for text generation
- `nomic-embed-text:latest` - for embeddings

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Ollama is Running

```bash
# Check if Ollama service is running
ollama list

# If not running, start it (usually runs automatically)
ollama serve
```

### 3. Test Your Setup

```bash
# Test the LLM
ollama run phi3:mini "Hello, how are you?"

# Test embeddings
ollama run nomic-embed-text "Test embedding"
```

### 4. Configuration

Your `.env` file is already configured for Ollama:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=phi3:mini
OLLAMA_EMBED_MODEL=nomic-embed-text:latest
```

## Alternative: Using Gemini

If you want to use Gemini instead:

### 1. Get Gemini API Key

Visit: https://makersuite.google.com/app/apikey

### 2. Update .env

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

## Usage in Code

The system automatically uses the provider specified in `.env`:

```python
from storage.chroma_store import init_chroma_collection
from retrieval.query_engine import create_query_engine

# Initialize ChromaDB
client, collection = init_chroma_collection()

# Create query engine (automatically uses LLM_PROVIDER from .env)
query_engine = create_query_engine(collection)

# Query
result = query_engine.query("What is the refund policy?")
print(result)
```

## Generating Embeddings During Ingestion

```python
from storage.embeddings import generate_embeddings_batch

texts = ["Document chunk 1", "Document chunk 2"]
embeddings = generate_embeddings_batch(texts)  # Uses LLM_PROVIDER from .env
```

## Performance Notes

### Ollama (Local)
- Pros: Free, private, no API limits
- Cons: Slower than cloud APIs, requires local resources
- Best for: Development, testing, privacy-sensitive data

### Gemini
- Pros: Fast, high quality, generous free tier
- Cons: Requires internet, API key management
- Best for: Production, demos, when speed matters

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
killall ollama
ollama serve
```

### Model Not Found

```bash
# Pull models if needed
ollama pull phi3:mini
ollama pull nomic-embed-text
```

### Slow Performance

Ollama performance depends on your hardware:
- phi3:mini is optimized for speed (2.2 GB)
- Consider using phi3:medium for better quality (but slower)
- Embeddings with nomic-embed-text are fast (274 MB)

## Next Steps

1. Run the ingestion script to populate ChromaDB:
   ```bash
   python ingest_demo_data.py
   ```

2. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

3. Query your documents using natural language!
