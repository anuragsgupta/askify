# askify

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
## Configuration

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
