---
inclusion: always
---

# Project structure

sme-knowledge-agent/
├── .kiro/
│   ├── steering/          # product.md, tech.md, structure.md
│   ├── specs/
│   │   └── sme-knowledge-agent/
│   │       ├── requirements.md
│   │       ├── design.md
│   │       └── tasks.md
│   └── hooks/             # test-sync, doc-update
├── ingestion/
│   ├── pdf_parser.py      # PyMuPDF section extractor
│   ├── excel_parser.py    # openpyxl row-as-document
│   ├── email_parser.py    # EML + Gmail API
│   └── drive_fetcher.py   # Google Drive folder download
├── storage/
│   └── chroma_store.py    # ChromaDB init + upsert helpers
├── retrieval/
│   ├── query_engine.py    # LlamaIndex RAG chain
│   └── conflict_detector.py # post-retrieval conflict logic
├── app.py                 # Streamlit entry point
├── data/                  # demo docs (committed)
├── chroma_db/             # persisted embeddings (committed)
└── .env.example