---
inclusion: always
---

# Tech stack

## Languages & frameworks
- Backend: Python 3.11+
- Frontend: Streamlit (single-file UI, no separate React build)
- No TypeScript, no Next.js — keep it simple for hackathon scope

## Core libraries
- Document parsing: PyMuPDF (PDF), openpyxl data_only=True (Excel), Python email stdlib (EML)
- Vector store: ChromaDB (local persistence, no cloud setup required)
- Embeddings: Ollama nomic-embed-text (local) OR Gemini embedding-001
- RAG orchestration: LlamaIndex (ChromaVectorStore + VectorStoreIndex)
- LLM inference: Ollama phi3:mini (local) OR Gemini 1.5 Flash
- Google APIs: google-api-python-client + google-auth-oauthlib

## Architecture decisions
- ALL document types (PDF, Excel, email) stored in ONE ChromaDB collection
- Each chunk carries full metadata: source, doc_type, doc_date, section/row/subject
- Conflict detection runs POST-retrieval as custom middleware — not inside the LLM
- Embeddings pre-generated and persisted to disk before demo

## What NOT to use
- No LangChain (LlamaIndex is sufficient and simpler)
- No Pinecone/Weaviate (ChromaDB local is sufficient)
- No LlamaSheet, LiteLLM, LlamaClassify (unnecessary abstraction)
- No Quivr fork (full ownership required)
- No separate SQLite for Excel (same ChromaDB, different doc_type)