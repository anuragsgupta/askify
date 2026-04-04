# Running the Backend Server

## Architecture Overview

Your project has a **modern full-stack architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - Vite dev server (port 5173)                          │
│  - React Router for navigation                          │
│  - Lucide icons                                         │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  - FastAPI server (port 8000)                           │
│  - Routes: /api/upload, /api/query, /api/share         │
│  - Services: conflict detection, embeddings             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Vector Database (ChromaDB)                  │
│  - Local persistence: server/chroma_data/               │
│  - Embeddings: Google Gemini or Ollama                 │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Option 1: Run Both Frontend and Backend (Recommended)

```bash
# Terminal 1: Start Backend
cd server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
npm run dev
```

Then open: http://localhost:5173

### Option 2: Run Backend Only (API Testing)

```bash
cd server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

## Step-by-Step Setup

### 1. Install Backend Dependencies

```bash
cd server
pip3 install -r requirements.txt
```

Required packages:
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `python-multipart` - File upload support
- `google-genai` - Gemini embeddings
- `chromadb` - Vector database
- `PyPDF2` - PDF parsing
- `openpyxl` - Excel parsing
- `python-dateutil` - Date handling

### 2. Install Frontend Dependencies

```bash
# From project root
npm install
```

### 3. Configure Environment

Create `server/.env` file:

```env
# LLM Provider
LLM_PROVIDER=gemini

# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Or use Ollama (local)
# LLM_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_EMBED_MODEL=nomic-embed-text:latest
```

### 4. Start Backend Server

```bash
cd server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5. Start Frontend Dev Server

```bash
# From project root
npm run dev
```

Expected output:
```
  VITE v8.0.1  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### 6. Verify Setup

Open browser to http://localhost:5173

Test the health endpoint:
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"ok","service":"askify-rag"}
```

## Backend API Endpoints

### Health Check
```bash
GET /api/health
```

### Upload Documents
```bash
POST /api/upload
Content-Type: multipart/form-data

# Upload PDF, Excel, or EML files
```

### Query Documents
```bash
POST /api/query
Content-Type: application/json

{
  "query": "What is the refund policy?",
  "top_k": 5
}
```

### Share Results
```bash
POST /api/share
Content-Type: application/json

{
  "query": "...",
  "answer": "...",
  "sources": [...]
}
```

## Testing the Backend

### 1. Using FastAPI Docs (Swagger UI)

Open http://localhost:8000/docs

- Interactive API documentation
- Try out endpoints directly
- See request/response schemas

### 2. Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Upload a document
curl -X POST http://localhost:8000/api/upload \
  -F "file=@data/Refund_Policy_v1_January2023.pdf"

# Query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the refund policy?", "top_k": 5}'
```

### 3. Using the Frontend

1. Open http://localhost:5173
2. Upload documents via UI
3. Submit queries
4. View results with conflict detection

## Project Structure

```
server/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── __init__.py
├── routes/
│   ├── upload.py          # Document upload endpoint
│   ├── query.py           # Query endpoint
│   └── share.py           # Share results endpoint
├── services/
│   ├── conflict.py        # Conflict detection logic
│   ├── embeddings.py      # Embedding generation
│   └── parser.py          # Document parsing
├── chroma_data/           # ChromaDB persistence
├── doc_metadata.json      # Document metadata cache
└── share_tokens.json      # Shared result tokens
```

## Configuration Options

### Backend Server Options

```bash
# Development (auto-reload on code changes)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production (no reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Custom port
uvicorn main:app --reload --port 8080

# Verbose logging
uvicorn main:app --reload --log-level debug
```

### Frontend Dev Server Options

```bash
# Default (port 5173)
npm run dev

# Custom port
npm run dev -- --port 3000

# Expose to network
npm run dev -- --host
```

## Troubleshooting

### Backend Issues

#### "Module not found" errors
```bash
cd server
pip3 install -r requirements.txt
```

#### "Address already in use" (port 8000)
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or use a different port
uvicorn main:app --reload --port 8001
```

#### CORS errors in browser
- Check that frontend is running on http://localhost:5173
- Backend allows this origin in `main.py` CORS config
- If using different port, update `allow_origins` in `main.py`

#### ChromaDB errors
```bash
# Delete and recreate database
rm -rf server/chroma_data
# Upload documents again via UI
```

### Frontend Issues

#### "Cannot connect to backend"
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify API URL in frontend code

#### "npm: command not found"
```bash
# Install Node.js
brew install node

# Verify installation
node --version
npm --version
```

#### Build errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Development Workflow

### Making Backend Changes

1. Edit files in `server/`
2. Server auto-reloads (if using `--reload` flag)
3. Test changes via http://localhost:8000/docs

### Making Frontend Changes

1. Edit files in `src/`
2. Vite hot-reloads automatically
3. See changes instantly in browser

### Adding New API Endpoints

1. Create route in `server/routes/`
2. Add service logic in `server/services/`
3. Register router in `server/main.py`
4. Update frontend to call new endpoint

## Production Deployment

### Backend

```bash
# Install production dependencies
pip3 install -r requirements.txt

# Run with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
# Build for production
npm run build

# Serve static files (output in dist/)
npm run preview
```

## Comparison: FastAPI Backend vs Streamlit App

You have TWO different implementations:

| Feature | FastAPI + React | Streamlit |
|---------|----------------|-----------|
| **Location** | `server/` + `src/` | `app.py` |
| **Backend** | FastAPI (REST API) | Streamlit (all-in-one) |
| **Frontend** | React + Vite | Streamlit components |
| **Architecture** | Separate frontend/backend | Monolithic |
| **Deployment** | More complex | Simpler |
| **Customization** | Full control | Limited |
| **Development** | Modern stack | Rapid prototyping |

### When to Use Each

**Use FastAPI + React** when:
- Building production application
- Need custom UI/UX
- Want API for mobile apps
- Require scalability

**Use Streamlit** when:
- Quick demos/prototypes
- Internal tools
- Data science workflows
- Minimal UI requirements

## Next Steps

1. ✅ Start backend server
2. ✅ Start frontend dev server
3. 📤 Upload test documents
4. 🔍 Test queries
5. 🎨 Customize UI in `src/`
6. 🔧 Add features in `server/`

For more details, see:
- FastAPI docs: https://fastapi.tiangolo.com
- Vite docs: https://vitejs.dev
- React Router: https://reactrouter.com
