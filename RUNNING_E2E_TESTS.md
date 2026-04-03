# Running End-to-End Integration Tests

## Quick Start

### Run All Tests
```bash
python3 -m pytest test_e2e_integration.py -v
```

### Run Specific Test Categories

**Ingestion to Query Flow:**
```bash
python3 -m pytest test_e2e_integration.py::TestE2EIngestionToQuery -v
```

**ChromaDB Persistence:**
```bash
python3 -m pytest test_e2e_integration.py::TestChromaDBPersistence -v
```

**Complete System Flow:**
```bash
python3 -m pytest test_e2e_integration.py::TestCompleteSystemFlow -v
```

**Error Handling:**
```bash
python3 -m pytest test_e2e_integration.py::TestErrorHandlingAndEdgeCases -v
```

### Run Individual Tests

**Test complete ingestion to query flow:**
```bash
python3 -m pytest test_e2e_integration.py::TestE2EIngestionToQuery::test_complete_ingestion_to_query_flow -v -s
```

**Test conflict detection:**
```bash
python3 -m pytest test_e2e_integration.py::TestE2EIngestionToQuery::test_conflict_detection_in_e2e_flow -v -s
```

**Test persistence:**
```bash
python3 -m pytest test_e2e_integration.py::TestChromaDBPersistence::test_persistence_across_restarts -v -s
```

**Test multi-document type query:**
```bash
python3 -m pytest test_e2e_integration.py::TestCompleteSystemFlow::test_multi_document_type_query -v -s
```

**Test empty collection (reliable test):**
```bash
python3 -m pytest test_e2e_integration.py::TestErrorHandlingAndEdgeCases::test_empty_collection_query -v -s
```

## Configuration

### Provider Selection

Edit `.env` file to choose LLM provider:

**Option 1: Ollama (Local, Default)**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=phi3:mini
OLLAMA_EMBED_MODEL=nomic-embed-text:latest
```

**Option 2: Gemini (Cloud, More Stable)**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

**Option 3: OpenAI (Cloud)**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

### Prerequisites

1. **For Ollama (local):**
   ```bash
   # Start Ollama service
   ollama serve
   
   # Pull required models
   ollama pull phi3:mini
   ollama pull nomic-embed-text:latest
   ```

2. **For Gemini:**
   - Set `GEMINI_API_KEY` in `.env` file

3. **For OpenAI:**
   - Set `OPENAI_API_KEY` in `.env` file

4. **Sample Data:**
   ```bash
   # Create demo data if not present
   python3 ingest_demo_data.py
   ```

## Test Output Options

### Verbose Output with Print Statements
```bash
python3 -m pytest test_e2e_integration.py -v -s
```

### Short Traceback
```bash
python3 -m pytest test_e2e_integration.py -v --tb=short
```

### Only Show Failed Tests
```bash
python3 -m pytest test_e2e_integration.py -v --tb=short -x
```

### Run Tests Matching Pattern
```bash
python3 -m pytest test_e2e_integration.py -v -k "conflict"
```

## Troubleshooting

### Issue: "llama runner process has terminated"

**Cause:** Ollama service instability or resource constraints

**Solutions:**
1. Switch to Gemini provider (more stable):
   ```bash
   # Edit .env
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_key
   ```

2. Restart Ollama:
   ```bash
   pkill ollama
   ollama serve
   ```

3. Run tests individually instead of in batch

4. Increase Ollama timeout in code (if needed)

### Issue: "Sample data files not found"

**Solution:**
```bash
python3 ingest_demo_data.py
```

### Issue: "API key not set"

**Solution:**
Add the appropriate API key to `.env` file:
```env
GEMINI_API_KEY=your_gemini_key
# or
OPENAI_API_KEY=your_openai_key
```

### Issue: Tests are skipped

**Cause:** Missing API keys or sample data

**Check:**
```bash
# Verify .env configuration
cat .env | grep -E "LLM_PROVIDER|API_KEY"

# Verify sample data exists
ls -la data/
```

## Test Coverage

The integration tests cover:

1. ✅ **Complete Flow**: Ingestion → Query → Conflict Detection → Answer
2. ✅ **Multi-Document Types**: PDF, Excel, Email
3. ✅ **Conflict Detection**: Version conflicts, cross-doc-type conflicts
4. ✅ **ChromaDB Persistence**: Data survives application restarts
5. ✅ **Error Handling**: Empty collections, malformed metadata
6. ✅ **Performance**: Query response time validation
7. ⏭️ **Google APIs**: Drive and Gmail (requires manual setup)

## CI/CD Recommendations

For continuous integration:

```yaml
# Example GitHub Actions workflow
- name: Run E2E Tests
  env:
    LLM_PROVIDER: gemini
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: |
    python3 -m pytest test_e2e_integration.py -v --tb=short
```

Use Gemini provider for CI/CD as it's more stable than local Ollama.

## Performance Expectations

| Test | Expected Duration |
|------|------------------|
| Empty collection query | ~3 seconds |
| Complete ingestion flow | ~15-30 seconds |
| Conflict detection | ~10-20 seconds |
| Persistence test | ~10-15 seconds |
| Multi-doc-type query | ~15-25 seconds |

Total test suite: ~2-5 minutes (depending on provider and system resources)
