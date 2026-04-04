# Quick Reference Guide

## 🚀 Starting the Application

### Backend Server (FastAPI)
```bash
# Option 1: Using startup script
./start_backend.sh

# Option 2: Manual command
python3 -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend URLs:**
- API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### Frontend (React + Vite)
```bash
# Option 1: Using startup script
./start_frontend.sh

# Option 2: Manual command
npm run dev
```

**Frontend URL:**
- App: http://localhost:5173

### Streamlit App (Alternative)
```bash
streamlit run app.py
```

**Streamlit URL:**
- App: http://localhost:8501

## 📁 Project Structure

```
askify/
├── server/                    # FastAPI backend
│   ├── main.py               # API entry point
│   ├── routes/               # API endpoints
│   ├── services/             # Business logic
│   └── chroma_data/          # Vector database
├── src/                      # React frontend
│   ├── components/           # UI components
│   ├── pages/                # Page components
│   └── App.jsx               # Main app
├── app.py                    # Streamlit app (alternative)
├── app_enhanced.py           # Enhanced Streamlit UI
├── data/                     # Demo documents
├── ingestion/                # Document parsers
├── retrieval/                # Query engine
└── storage/                  # ChromaDB utilities
```

## 🔧 Common Commands

### Backend Development
```bash
# Install dependencies
pip3 install -r server/requirements.txt

# Start server
python3 -m uvicorn server.main:app --reload --port 8000

# Run from different port
python3 -m uvicorn server.main:app --reload --port 8080

# Production mode (no reload)
python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Development
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Streamlit Development
```bash
# Start Streamlit app
streamlit run app.py

# Start enhanced UI
streamlit run app_enhanced.py

# Custom port
streamlit run app.py --server.port 8502
```

## 🗄️ Database Management

### ChromaDB (FastAPI Backend)
```bash
# Reset database
rm -rf server/chroma_data

# View database location
ls -la server/chroma_data
```

### ChromaDB (Streamlit)
```bash
# Reset database
rm -rf chroma_db

# Re-ingest demo data
python3 ingest_demo_data.py
```

## 🔍 Testing

### Test Backend API
```bash
# Health check
curl http://localhost:8000/api/health

# Upload document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@data/Refund_Policy_v1_January2023.pdf"

# Query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the refund policy?", "top_k": 5}'
```

### Test Streamlit Query Engine
```bash
python3 -c "
from storage.chroma_store import init_chroma_collection
from retrieval.query_engine import create_query_engine, query_with_metadata

client, collection = init_chroma_collection()
query_engine = create_query_engine(collection)
result = query_with_metadata(query_engine, 'What is the refund policy?')
print(result.answer)
"
```

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)

# Or use different port
python3 -m uvicorn server.main:app --reload --port 8080
```

### Module Import Errors
```bash
# Backend
pip3 install -r server/requirements.txt

# Frontend
npm install

# Streamlit
pip3 install -r requirements.txt
```

### CORS Errors
- Ensure frontend is on http://localhost:5173
- Check `server/main.py` CORS configuration
- Clear browser cache

### Ollama Not Running
```bash
# Start Ollama
ollama serve

# Check status
curl http://localhost:11434/api/tags

# Pull models
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

## 📊 API Endpoints

### FastAPI Backend

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/upload` | Upload documents |
| POST | `/api/query` | Query documents |
| POST | `/api/share` | Share results |

### Interactive API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Environment Configuration

### Backend (.env or server/.env)
```env
# LLM Provider
LLM_PROVIDER=ollama

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:1b
OLLAMA_EMBED_MODEL=nomic-embed-text:latest

# Gemini (alternative)
GEMINI_API_KEY=your_key_here
```

## 📝 Development Workflow

### Adding New Features

1. **Backend API Endpoint**
   ```bash
   # Create route file
   touch server/routes/new_feature.py
   
   # Add service logic
   touch server/services/new_feature.py
   
   # Register in server/main.py
   ```

2. **Frontend Component**
   ```bash
   # Create component
   touch src/components/NewFeature.jsx
   
   # Add to page
   # Edit src/pages/YourPage.jsx
   ```

3. **Streamlit Feature**
   ```bash
   # Edit app.py or app_enhanced.py
   # Add new function or section
   ```

## 🚢 Deployment

### Backend
```bash
# Install production dependencies
pip3 install -r server/requirements.txt

# Run with gunicorn (recommended)
gunicorn server.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or with uvicorn
uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
# Build
npm run build

# Output in dist/
# Serve with nginx, Apache, or any static host
```

### Streamlit
```bash
# Deploy to Streamlit Cloud
# Or run on server:
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📚 Documentation

- [Running Backend](RUNNING_BACKEND.md) - Detailed backend setup
- [Local LLM Setup](LOCAL_LLM_SETUP.md) - Ollama configuration
- [Quick Fix](QUICK_FIX.md) - Common issues and solutions
- [Architecture](ARCHITECTURE.md) - System design
- [Usage Examples](USAGE_EXAMPLES.md) - Code examples

## 🎯 Quick Tips

1. **Always start backend before frontend** - Frontend needs API
2. **Keep Ollama running** - Faster query responses
3. **Use API docs** - http://localhost:8000/docs for testing
4. **Check logs** - Backend terminal shows errors
5. **Clear cache** - Delete chroma_data/ or chroma_db/ if issues

## 🔄 Switching Between Implementations

### Use FastAPI + React when:
- Building production app
- Need REST API
- Want custom UI
- Require scalability

### Use Streamlit when:
- Quick prototyping
- Internal tools
- Data science workflows
- Simple UI needs

Both implementations share:
- Same document parsers (`ingestion/`)
- Same query engine (`retrieval/`)
- Same vector store (`storage/`)
- Same LLM providers (Ollama/Gemini)
