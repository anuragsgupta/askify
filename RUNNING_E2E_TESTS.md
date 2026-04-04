# End-to-End Testing Guide

## ✅ Backend Server is Running

Your FastAPI backend is now running successfully!

**Status:** ✅ Running on http://localhost:8000

**Verification:**
```bash
curl http://localhost:8000/api/health
# Response: {"status":"ok","service":"askify-rag"}
```

## 🧪 Testing the Complete Stack

### 1. Test Backend API

#### Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status":"ok","service":"askify-rag"}
```

#### Interactive API Testing
Open in browser: http://localhost:8000/docs

This gives you Swagger UI where you can:
- See all available endpoints
- Test endpoints interactively
- View request/response schemas

### 2. Test Document Upload

```bash
# Upload a PDF
curl -X POST http://localhost:8000/api/upload \
  -F "file=@data/Refund_Policy_v1_January2023.pdf"

# Upload an Excel file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@data/Pricing_Q1_2024.xlsx"

# Upload an email
curl -X POST http://localhost:8000/api/upload \
  -F "file=@data/Refund_Inquiry_AcmeCorp_Jan2023.eml"
```

### 3. Test Query Endpoint

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the refund policy?",
    "top_k": 5
  }'
```

Expected response structure:
```json
{
  "answer": "The refund policy states...",
  "sources": [
    {
      "content": "...",
      "metadata": {
        "source": "Refund_Policy_v1_January2023.pdf",
        "doc_type": "policy",
        "section_title": "Refund Policy"
      },
      "score": 0.85
    }
  ],
  "conflicts": [],
  "response_time_ms": 1500
}
```

### 4. Start Frontend

In a new terminal:

```bash
npm run dev
```

Then open: http://localhost:5173

### 5. Test Full User Flow

1. **Open Frontend** - http://localhost:5173
2. **Upload Documents** - Use the upload button
3. **Submit Query** - Type "What is the refund policy?"
4. **View Results** - See answer with sources
5. **Check Conflicts** - View conflict detection panel

## 🔍 Monitoring Backend

### View Backend Logs

The backend terminal shows real-time logs:
```
INFO:     127.0.0.1:52345 - "POST /api/query HTTP/1.1" 200 OK
INFO:     Query completed in 1523ms
```

### Check Process Status

```bash
# List running processes
ps aux | grep uvicorn

# Check port usage
lsof -i :8000
```

### Stop Backend

Press `CTRL+C` in the backend terminal, or:

```bash
# Find and kill process
kill -9 $(lsof -ti:8000)
```

## 🧪 Automated Testing

### Backend Unit Tests

```bash
# Run pytest (if tests exist)
cd server
pytest tests/

# Run with coverage
pytest --cov=server tests/
```

### Frontend Tests

```bash
# Run tests (if configured)
npm test

# Run with coverage
npm test -- --coverage
```

### Integration Tests

```bash
# Test complete flow
python3 test_e2e_integration.py
```

## 📊 Performance Testing

### Load Testing with Apache Bench

```bash
# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/api/health

# Test query endpoint (requires POST data)
ab -n 100 -c 5 -p query.json -T application/json \
  http://localhost:8000/api/query
```

### Query Performance

```bash
# Time a query
time curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the refund policy?", "top_k": 5}'
```

Expected times:
- First query: 15-20 seconds (model loading)
- Subsequent queries: 10-15 seconds
- With Gemini: 2-3 seconds

## 🐛 Debugging

### Enable Debug Logging

```bash
# Start with debug logs
python3 -m uvicorn server.main:app --reload --log-level debug
```

### Check ChromaDB

```bash
# View database files
ls -la server/chroma_data/

# Check collection size
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='server/chroma_data')
collection = client.get_or_create_collection('sme_knowledge')
print(f'Collection has {collection.count()} documents')
"
```

### Test Individual Components

```bash
# Test document parser
python3 -c "
from ingestion.pdf_parser import parse_pdf
chunks = parse_pdf('data/Refund_Policy_v1_January2023.pdf')
print(f'Extracted {len(chunks)} chunks')
"

# Test embeddings
python3 -c "
from storage.embeddings import get_embedding_function
embed_fn = get_embedding_function('ollama')
embedding = embed_fn('test text')
print(f'Embedding dimension: {len(embedding)}')
"
```

## 🔄 Restart Services

### Restart Backend
```bash
# Stop (CTRL+C in terminal)
# Then start again
python3 -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

### Restart Frontend
```bash
# Stop (CTRL+C in terminal)
# Then start again
npm run dev
```

### Restart Ollama
```bash
# Stop
pkill ollama

# Start
ollama serve
```

## 📝 Test Checklist

- [ ] Backend health check responds
- [ ] API docs accessible at /docs
- [ ] Can upload PDF document
- [ ] Can upload Excel document
- [ ] Can upload EML document
- [ ] Query returns relevant results
- [ ] Sources include metadata
- [ ] Conflict detection works
- [ ] Frontend loads successfully
- [ ] Frontend can connect to backend
- [ ] Full user flow works end-to-end

## 🎯 Next Steps

1. ✅ Backend is running
2. ⏭️ Start frontend: `npm run dev`
3. ⏭️ Test document upload
4. ⏭️ Test queries
5. ⏭️ Customize UI in `src/`
6. ⏭️ Add features in `server/`

## 📚 Related Documentation

- [Quick Reference](QUICK_REFERENCE.md) - Common commands
- [Running Backend](RUNNING_BACKEND.md) - Detailed setup
- [Local LLM Setup](LOCAL_LLM_SETUP.md) - Ollama config
- [Architecture](ARCHITECTURE.md) - System design

## 🆘 Getting Help

If you encounter issues:

1. Check backend logs in terminal
2. Check browser console (F12)
3. Verify Ollama is running: `curl http://localhost:11434/api/tags`
4. Check port availability: `lsof -i :8000`
5. Review error messages in logs
6. Restart services if needed

Your backend is ready! Start the frontend and begin testing.
