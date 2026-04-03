# SME Knowledge Agent

A conversational AI system that helps employees at small and medium enterprises query scattered company documents (policy PDFs, pricing Excel files, and email threads) in natural language with precise citations and autonomous conflict resolution.

## Features

- 🔍 Multi-format document ingestion (PDF, Excel, Email)
- 🤖 RAG-based query engine with OpenAI GPT-4o-mini
- 📊 ChromaDB vector storage with metadata preservation
- 🔐 Role-based authentication (Employee, Team Lead, Knowledge Manager, System Admin)
- ⚠️ Autonomous conflict detection and resolution
- 📝 Exact source citations with section/row/email metadata
- 🔄 Google Drive and Gmail integration (optional)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 4. Login

Use these demo credentials:

- **Employee**: `employee1` / `password123`
- **Team Lead**: `manager1` / `manager123`
- **Knowledge Manager**: `admin1` / `admin123`
- **System Admin**: `sysadmin` / `sysadmin123`

## Project Structure

```
sme-knowledge-agent/
├── ingestion/          # Document parsers (PDF, Excel, Email)
├── storage/            # ChromaDB storage layer
├── retrieval/          # Query engine and conflict detection
├── app.py              # Streamlit UI entry point
├── data/               # Demo documents
├── chroma_db/          # Persisted embeddings
└── docs/               # Documentation
```

## Development Status

### ✅ Completed
- Project structure and dependencies
- PDF parser with section extraction
- Excel parser with row serialization
- Email parser with EML support
- ChromaDB storage layer
- Google Drive fetcher (optional)
- Query engine with LlamaIndex
- Streamlit authentication and routing

### 🚧 In Progress
- Conflict detection middleware
- Employee query interface
- Conflict warning UI
- CRM ticket creation
- Knowledge manager ingestion dashboard

## Testing

Run all tests:
```bash
pytest -v
```

Run specific test modules:
```bash
pytest ingestion/test_pdf_parser.py -v
pytest retrieval/test_query_engine.py -v
```

Run integration tests (requires API credentials):
```bash
pytest -m integration -v
```

## Google Drive Integration

See [docs/GOOGLE_DRIVE_SETUP.md](docs/GOOGLE_DRIVE_SETUP.md) for detailed setup instructions.

## Tech Stack

- **Backend**: Python 3.11+
- **Frontend**: Streamlit
- **Vector Store**: ChromaDB (local persistence)
- **Embeddings**: OpenAI text-embedding-3-small
- **LLM**: OpenAI GPT-4o-mini
- **RAG Framework**: LlamaIndex
- **Document Parsing**: PyMuPDF, openpyxl, Python email stdlib
- **Testing**: pytest, Hypothesis (property-based testing)

## License

MIT

## SME Knowledge Agent

A conversational AI system that ingests multi-format company documents (PDF, Excel, email) and answers employee queries with precise citations and autonomous conflict resolution.

## Setup

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```
w## Configuration

Configure your environment variables in `.env`:
- `OPENAI_API_KEY` - Your OpenAI API key
- `GOOGLE_CLIENT_ID` - Google OAuth client ID (optional)
- `GOOGLE_CLIENT_SECRET` - Google OAuth secret (optional)
- ChromaDB settings (if using cloud)

## Development

### Project Structure

```
askify/
├── .kiro/              # Private submodule (specs, requirements, design)
├── ingestion/          # Document parsers (PDF, Excel, Email)
├── storage/            # ChromaDB integration
├── retrieval/          # Query engine and conflict detection
├── data/               # Demo documents
└── chroma_db/          # Vector database storage
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test suite
python -m pytest ingestion/

# Run property-based tests only
python -m pytest -k "property"
```

## For Contributors

### Accessing the Specs

The `.kiro/` folder is a Git submodule pointing to a private repository. You need:
1. Access to the private `askify-kiro` repository
2. Clone with `--recurse-submodules` flag

### Updating Specs

```bash
# Make changes in .kiro/
cd .kiro
git add .
git commit -m "Update specs"
git push

# Update main repo to point to new commit
cd ..
git add .kiro
git commit -m "Update .kiro submodule"
git push
```
