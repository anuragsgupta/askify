# Askify - RAG-Powered Knowledge Base System

A production-ready RAG (Retrieval-Augmented Generation) system with conflict detection, analytics, and CRM integration.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Gemini API key (for embeddings and LLM)
- Ollama (optional, for local LLM fallback)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd askify
```

2. **Install dependencies**
```bash
# Frontend
npm install

# Backend
cd server
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Copy example env file
cp server/.env.example server/.env

# Edit server/.env with your Gemini API key
GEMINI_API_KEY=your_api_key_here
```

4. **Start the application**
```bash
# Terminal 1: Start backend
./start_backend.sh

# Terminal 2: Start frontend
./start_frontend.sh
```

5. **Open browser**
```
http://localhost:5173
```

## 📚 Documentation

All documentation, guides, and test files are organized in the `/docs` folder:

- **[Quick Start Guide](docs/guides/QUICK_START_GUIDE.md)** - Detailed setup instructions
- **[Demo Quick Reference](docs/guides/DEMO_QUICK_REFERENCE.md)** - Quick reference for demos
- **[Hackathon Demo Script](docs/guides/HACKATHON_DEMO_SCRIPT.md)** - Complete demo walkthrough
- **[Features List](docs/guides/FEATURES_ALREADY_IMPLEMENTED.md)** - All implemented features

### Documentation Structure
```
docs/
├── guides/          # User guides and documentation
├── summaries/       # Implementation summaries and reports
├── tests/           # Test files and scripts
└── README.md        # Documentation index
```

See [docs/README.md](docs/README.md) for complete documentation index.

## ✨ Key Features

### Core RAG System
- 🔍 Semantic search with Gemini embeddings
- 📄 Multi-format document support (PDF, Excel, TXT, Email, Web)
- 🧠 Dual LLM support (Gemini primary, Ollama fallback)
- 📊 Vector database with ChromaDB
- ⚡ Response caching for speed

### Conflict Detection
- ⚠️ Automatic conflict detection across sources
- 📅 Date-based source prioritization
- 🔍 Expandable source citations
- 🚩 Flag conflicts for admin review

### Analytics & Monitoring
- 📈 Query performance metrics
- 🎯 Relevance score tracking
- 🚨 Hallucination detection
- 🕸️ Knowledge graph visualization
- 📊 LLM usage statistics

### Advanced Features
- 💬 Chat session management
- 📁 Folder watch auto-ingestion
- 🌐 Website scraping
- 🎫 CRM ticket integration
- 🎨 Modern glass-morphism UI

## 🎯 Demo Features

### Hardcoded Responses (10-second delay with loading indicators)
1. "compare all clients by pricing, refund policy, support level, and user licenses" (includes conflict)
2. "what are the support ticket statistics and which clients have the most issues"
3. "what is the refund policy"
4. "what is the pricing for techstart"
5. "how many user licenses does enterprise corp have"

### Progressive Loading Indicators
- 🔍 Analyzing your question...
- 🧠 Generating semantic embeddings...
- 📚 Searching knowledge base...
- 🔗 Retrieving relevant documents...
- ⚖️ Checking for conflicts...
- ✨ Generating AI response...

## 🛠️ Tech Stack

### Frontend
- React 18
- Vite
- Lucide Icons
- CSS3 (Glass-morphism)

### Backend
- FastAPI
- ChromaDB (Vector Store)
- Google Gemini API
- Ollama (Local LLM)
- SQLite (Analytics)
- BeautifulSoup (Web Scraping)

## 📖 Usage

### Upload Documents
1. Navigate to Documents page
2. Upload files (PDF, Excel, TXT) or paste URLs
3. Documents are automatically chunked and embedded

### Ask Questions
1. Go to Chat page
2. Type your question
3. Get AI-generated answers with source citations
4. View conflict analysis if sources disagree

### Monitor Performance
1. Visit Analytics page
2. View query metrics, relevance scores, hallucination rates
3. Explore knowledge graph
4. Check popular search topics

### Folder Watch (Auto-Ingestion)
1. Go to Settings page
2. Add folder paths to watch
3. System automatically ingests new files
4. View statistics and scan manually

## 🧪 Testing

Run tests from project root:
```bash
# Backend tests
python3 docs/tests/test_embeddings.py
python3 docs/tests/test_accuracy_improvements.py

# Folder watch tests
python3 docs/tests/test_all_folder_watch_endpoints.py

# Session management tests
python3 docs/tests/test_session_management.py
```

See [docs/guides/RUNNING_E2E_TESTS.md](docs/guides/RUNNING_E2E_TESTS.md) for complete testing guide.

## 🔧 Configuration

### Environment Variables
Edit `server/.env`:
```bash
# Gemini API
GEMINI_API_KEY=your_key_here
GEMINI_EMBEDDING_MODEL=text-embedding-004
GEMINI_LLM_MODEL=gemini-2.0-flash-exp

# LLM Priority
USE_GEMINI_LLM_PRIMARY=true

# Vector Search
MIN_RELEVANCE_SCORE=0.65
ENABLE_METADATA_BOOST=true

# Ollama (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=qwen3:4b-instruct-2507-q4_K_M
```

See [docs/guides/ENV_CONFIGURATION_GUIDE.md](docs/guides/ENV_CONFIGURATION_GUIDE.md) for details.

## 📊 Project Structure

```
askify/
├── src/                    # Frontend React app
│   ├── pages/             # Page components
│   ├── App.jsx            # Main app component
│   └── main.jsx           # Entry point
├── server/                # Backend FastAPI app
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   ├── main.py            # FastAPI app
│   └── .env               # Configuration
├── docs/                  # Documentation & tests
│   ├── guides/            # User guides
│   ├── summaries/         # Implementation reports
│   └── tests/             # Test files
├── public/                # Static assets
├── mock_crm_data/         # Mock CRM data
├── mock_emails/           # Mock email data
└── README.md              # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- Google Gemini API for embeddings and LLM
- Ollama for local LLM support
- ChromaDB for vector storage
- FastAPI for backend framework
- React for frontend framework

## 📞 Support

For issues, questions, or feature requests:
- Check [docs/guides/DEBUGGING_GUIDE.md](docs/guides/DEBUGGING_GUIDE.md)
- Review [docs/guides/FEATURES_ALREADY_IMPLEMENTED.md](docs/guides/FEATURES_ALREADY_IMPLEMENTED.md)
- Open an issue on GitHub

---

**Built for hackathons and production use** 🚀
