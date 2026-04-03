# Implementation Plan: SME Knowledge Agent

## Overview

This implementation plan breaks down the SME Knowledge Agent into discrete coding tasks following the 5-sprint structure: Foundation (parsers), Storage & Indexing (ChromaDB), Intelligence (conflict detection, query engine), Interface (Streamlit UI), and Polish. Each task builds incrementally, with property-based tests for universal correctness properties and unit tests for specific examples.


## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure: `ingestion/`, `storage/`, `retrieval/`, `data/`, `chroma_db/`
  - Create `requirements.txt` with: PyMuPDF, openpyxl, chromadb, llama-index, openai, streamlit, streamlit-authenticator, google-api-python-client, google-auth-oauthlib, hypothesis, pytest
  - Create `.env.example` with placeholders for OPENAI_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
  - Create `__init__.py` files in each module directory
  - _Requirements: All (foundation for entire system)_

- [x] 2. Implement PDF parser with section extraction
  - [x] 2.1 Create `ingestion/pdf_parser.py` with `extract_pdf_sections()` function
    - Use PyMuPDF to extract text and identify TOC structure
    - Parse hierarchical section numbering (e.g., "2.3.1")
    - Extract page numbers for each section
    - Return list of PDFSection dataclass objects with metadata
    - _Requirements: 1.1_
  
  - [x] 2.2 Implement `parse_date_from_filename()` function
    - Support patterns: "Policy_March2024.pdf", "Doc_2024-03-15.pdf"
    - Use regex to extract date components
    - Fall back to file modification timestamp if parsing fails
    - _Requirements: 1.3_
  
  - [x] 2.3 Write property test for PDF TOC extraction completeness
    - **Property 1: PDF TOC extraction completeness**
    - **Validates: Requirements 1.1**
    - Generate PDFs with varying TOC structures using Hypothesis
    - Verify all sections are extracted with hierarchy preserved
  
  - [x] 2.4 Write property test for filename date extraction accuracy
    - **Property 3: Filename date extraction accuracy**
    - **Validates: Requirements 1.3**
    - Generate random filenames with date patterns
    - Verify extracted dates match expected values
  
  - [x] 2.5 Write unit tests for PDF parser edge cases
    - Test PDFs without TOC (fallback to page-by-page)
    - Test nested sections with special characters
    - Test corrupted/password-protected PDFs (error handling)
    - _Requirements: 1.1, 1.3_

- [x] 3. Implement Excel parser with row serialization
  - [x] 3.1 Create `ingestion/excel_parser.py` with `extract_excel_rows()` function
    - Use openpyxl with `data_only=True` to get computed formula values
    - Convert each row to natural language string preserving column names and values
    - Extract client name from "Client" column if present
    - Extract date from "Date" column or file metadata
    - Return list of ExcelRow dataclass objects with metadata
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 3.2 Implement `row_to_natural_language()` helper function
    - Convert row dict to readable string: "Client: Acme, Price: $500"
    - Handle empty cells and special characters
    - _Requirements: 2.1_
  
  - [x] 3.3 Write property test for Excel row serialization
    - **Property 4: Excel row serialization preserves data**
    - **Validates: Requirements 2.1**
    - Generate random Excel rows with multiple columns
    - Verify all column names and values appear in output string
  
  - [x] 3.4 Write property test for Excel formula evaluation
    - **Property 5: Excel formula evaluation**
    - **Validates: Requirements 2.3**
    - Generate Excel files with various formulas
    - Verify computed values are stored, not raw formulas
  
  - [x] 3.5 Write unit tests for Excel parser edge cases
    - Test empty sheets and missing columns
    - Test merged cells and special formatting
    - Test formula cells that return None
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 4. Implement email parser with EML support
  - [x] 4.1 Create `ingestion/email_parser.py` with `parse_eml_file()` function
    - Use Python email stdlib to parse EML files
    - Extract sender, date, subject, body from each message
    - Extract thread_id from email headers
    - Handle multipart messages (prefer plain text over HTML)
    - Return list of EmailMessage dataclass objects with metadata
    - _Requirements: 3.1, 3.3_
  
  - [x] 4.2 Write property test for EML parsing completeness
    - **Property 6: EML parsing completeness**
    - **Validates: Requirements 3.1**
    - Generate random EML files with varying structures
    - Verify all required fields are extracted without missing data
  
  - [x] 4.3 Write unit tests for email parser edge cases
    - Test malformed EML files (error handling)
    - Test missing required fields (sender, date, subject)
    - Test multipart messages with attachments
    - _Requirements: 3.1_

- [x] 5. Checkpoint - Ensure parser tests pass
  - Run all parser unit tests and property tests
  - Verify parsers handle edge cases gracefully
  - Ask the user if questions arise

- [x] 6. Implement ChromaDB storage layer
  - [x] 6.1 Create `storage/chroma_store.py` with `init_chroma_collection()` function
    - Initialize ChromaDB client with local persistence to `./chroma_db`
    - Create single collection for all doc types
    - Configure collection with OpenAI embedding function
    - _Requirements: 4.1_
  
  - [x] 6.2 Implement `upsert_chunks()` function
    - Accept chunks with content, metadata, and pre-computed embeddings
    - Upsert to ChromaDB collection with full metadata schema
    - Handle duplicate IDs gracefully (update existing)
    - _Requirements: 1.2, 2.2, 3.3, 4.1_
  
  - [x] 6.3 Write property test for metadata preservation
    - **Property 2: Metadata preservation across storage**
    - **Validates: Requirements 1.2, 2.2, 3.3**
    - Generate random chunks with complete metadata
    - Store in ChromaDB and retrieve
    - Verify all metadata fields preserved without loss
  
  - [x] 6.4 Write unit tests for ChromaDB operations
    - Test upsert with duplicate IDs
    - Test upsert with missing metadata fields
    - Test collection initialization with existing data
    - _Requirements: 4.1_

- [x] 7. Implement Google Drive fetcher (optional enhancement)
  - [x] 7.1 Create `ingestion/drive_fetcher.py` with `download_drive_folder()` function
    - Authenticate using OAuth 2.0 with google-auth-oauthlib
    - List all files in specified Drive folder
    - Download PDFs and export Google Sheets as .xlsx
    - Return list of local file paths
    - _Requirements: 9.1, 9.2_
  
  - [x] 7.2 Write unit tests for Drive API integration
    - Test folder listing with real Drive folder (integration test)
    - Test OAuth flow and error handling
    - Test fallback to manual upload on timeout
    - _Requirements: 9.1, 9.3_

- [ ] 8. Implement Gmail API integration (optional enhancement)
  - [ ] 8.1 Add `search_gmail_by_keyword()` function to `email_parser.py`
    - Authenticate using OAuth 2.0
    - Search emails by client keyword
    - Download matching threads and parse as EML
    - _Requirements: 3.2, 9.2_
  
  - [ ] 8.2 Write unit tests for Gmail API integration
    - Test email search with real Gmail account (integration test)
    - Test rate limiting and exponential backoff
    - Test authentication error handling
    - _Requirements: 3.2, 9.2, 9.3_

- [x] 9. Checkpoint - Ensure storage layer tests pass
  - Run all storage and API integration tests
  - Verify ChromaDB persistence works across restarts
  - Ask the user if questions arise

- [x] 10. Implement query engine with LlamaIndex
  - [x] 10.1 Create `retrieval/query_engine.py` with `create_query_engine()` function
    - Initialize OpenAI GPT-4o-mini LLM
    - Initialize OpenAI text-embedding-3-small embedding model
    - Create ChromaVectorStore from ChromaDB collection
    - Create VectorStoreIndex with LlamaIndex
    - _Requirements: 4.1_
  
  - [x] 10.2 Implement `query_with_metadata()` function
    - Execute vector similarity search with top_k=5
    - Apply optional doc_type filter to restrict results
    - Return QueryResult with answer and source chunks with full metadata
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 10.3 Write property test for multi-doc-type retrieval
    - **Property 8: Multi-doc-type retrieval**
    - **Validates: Requirements 4.1**
    - Generate queries against mixed doc types
    - Verify retrieval can return chunks from all types
  
  - [x] 10.4 Write property test for retrieval metadata preservation
    - **Property 9: Retrieval metadata preservation**
    - **Validates: Requirements 4.2**
    - Generate random chunks and store in ChromaDB
    - Retrieve and verify complete metadata is preserved
  
  - [x] 10.5 Write property test for doc type filtering accuracy
    - **Property 10: Doc type filtering accuracy**
    - **Validates: Requirements 4.3**
    - Generate queries with doc_type filters
    - Verify all returned chunks match specified filter
  
  - [x] 10.6 Write unit tests for query engine
    - Test specific queries with known expected results
    - Test empty results handling
    - Test OpenAI API error handling and retries
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 11. Implement conflict detection middleware
  - [x] 11.1 Create `retrieval/conflict_detector.py` with `detect_conflicts()` function
    - Analyze retrieved chunks for same section_title or client field
    - Check for different doc_dates and semantically different content
    - Use semantic similarity threshold < 0.9 to identify conflicts
    - Return list of Conflict objects
    - _Requirements: 6.1_
  
  - [x] 11.2 Implement `apply_date_priority_rule()` function
    - Select chunk with most recent doc_date as winner
    - Return winner and list of rejected chunks
    - _Requirements: 6.2_
  
  - [x] 11.3 Implement `generate_diff_explanation()` function
    - Compare winner and rejected chunk content
    - Generate plain-language description of changes
    - Example: "Refund window changed from 30 to 60 days"
    - _Requirements: 6.3_
  
  - [x] 11.4 Implement `flag_outdated_email()` function
    - Check if email chunk predates PDF chunk on same topic
    - Match topics using section_title or client field
    - Return True if email contains outdated advice
    - _Requirements: 6.4_
  
  - [x] 11.5 Write property test for conflict detection and resolution
    - **Property 11: Conflict detection and date-priority resolution**
    - **Validates: Requirements 6.1, 6.2**
    - Generate pairs of chunks with varying attributes
    - Verify conflicts are detected and most recent wins
  
  - [x] 11.6 Write property test for diff explanation generation
    - **Property 12: Diff explanation generation**
    - **Validates: Requirements 6.3**
    - Generate detected conflicts
    - Verify non-empty diff explanation is generated
  
  - [x] 11.7 Write property test for cross-doc-type outdated flagging
    - **Property 13: Cross-doc-type outdated flagging**
    - **Validates: Requirements 6.4**
    - Generate email/PDF pairs with varying dates
    - Verify outdated flagging logic is correct
  
  - [x] 11.8 Write unit tests for conflict detector
    - Test specific conflict scenarios (version updates, policy changes)
    - Test edge cases (same date, missing metadata)
    - Test diff generation quality
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 12. Checkpoint - Ensure retrieval layer tests pass
  - Run all query engine and conflict detector tests
  - Verify end-to-end query flow works correctly
  - Ask the user if questions arise

- [x] 13. Implement Streamlit authentication and role-based routing
  - [x] 13.1 Create `app.py` with authentication setup
    - Install streamlit-authenticator
    - Create `config.yaml` with sample users and roles (employee, team_lead, knowledge_manager, system_admin)
    - Implement login page with role-based session state
    - _Requirements: All (foundation for UI)_
  
  - [x] 13.2 Implement role-based dashboard routing
    - Check `st.session_state['role']` after authentication
    - Route to appropriate dashboard based on role
    - _Requirements: All (foundation for UI)_
  
  - [x] 13.3 Write unit tests for authentication
    - Test login with valid/invalid credentials
    - Test role assignment and session state
    - Test default role fallback
    - _Requirements: All_

- [x] 14. Implement employee query interface
  - [x] 14.1 Create `render_query_interface()` function in `app.py`
    - Display text input for natural language query
    - Call query engine on submission
    - Display AI-generated answer
    - _Requirements: 4.1, 5.1, 5.2, 5.3_
  
  - [x] 14.2 Implement `render_citation()` function
    - Format citations based on doc_type
    - PDF: "Refund Policy v2 (Section 3.2: Returns, Page 5)"
    - Excel: "Pricing_2024.xlsx (Sheet: Q1, Row 42)"
    - Email: "From: john@acme.com (2024-01-15, Subject: Discount approval)"
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 14.3 Write property test for citation formatting completeness
    - **Property 7: Citation formatting completeness**
    - **Validates: Requirements 5.1, 5.2, 5.3**
    - Generate random chunks with metadata
    - Verify citation includes all required fields for doc_type
  
  - [x] 14.4 Write unit tests for query interface
    - Test query submission and answer display
    - Test citation formatting for each doc_type
    - Test empty results handling
    - _Requirements: 4.1, 5.1, 5.2, 5.3_

- [x] 15. Implement conflict warning UI
  - [x] 15.1 Create `render_conflict_warning()` function in `app.py`
    - Display red warning banner when conflicts detected
    - Show "View side-by-side" button
    - _Requirements: 7.1_
  
  - [x] 15.2 Implement side-by-side conflict view
    - Display winner and rejected chunks
    - Highlight differences in content
    - Show diff explanation
    - _Requirements: 7.2_
  
  - [x] 15.3 Ensure no conflict UI when no conflicts exist
    - Hide warning banner and side-by-side view
    - _Requirements: 7.3_
  
  - [x] 15.4 Write unit tests for conflict UI
    - Test warning banner visibility
    - Test side-by-side view rendering
    - Test UI hiding when no conflicts
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 16. Implement CRM ticket creation
  - [x] 16.1 Create `render_ticket_creation()` function in `app.py`
    - Display "Create Ticket" button after query
    - Pre-populate form with: client_name, query_text, ai_answer, source_citations, conflict_flag
    - Extract client_name from Excel metadata if available
    - Include resolution reasoning if conflict was resolved
    - _Requirements: 8.1, 8.2_
  
  - [x] 16.2 Write property test for ticket field population
    - **Property 14: Ticket field population**
    - **Validates: Requirements 8.1, 8.2**
    - Generate random query contexts
    - Verify all required fields are populated correctly
  
  - [x] 16.3 Write unit tests for ticket creation
    - Test ticket pre-population with query context
    - Test conflict_flag setting
    - Test missing client_name handling
    - _Requirements: 8.1, 8.2_

- [x] 17. Implement knowledge manager ingestion dashboard
  - [x] 17.1 Create `render_document_upload()` function in `app.py`
    - Display file uploader for PDF, Excel, EML files
    - Call appropriate parser on upload
    - Generate embeddings using OpenAI
    - Store chunks in ChromaDB
    - _Requirements: 1.1, 2.1, 3.1, 9.1_
  
  - [x] 17.2 Create `render_ingestion_dashboard()` function
    - Display summary statistics: total_documents, total_sections, total_excel_rows, total_email_messages
    - Allow clicking on document to preview extracted sections/rows
    - _Requirements: 10.1, 10.2_
  
  - [x] 17.3 Write property test for ingestion summary accuracy
    - **Property 15: Ingestion summary accuracy**
    - **Validates: Requirements 10.1**
    - Generate ingestion runs with known quantities
    - Verify summary statistics are accurate
  
  - [x] 17.4 Write unit tests for ingestion dashboard
    - Test file upload and processing
    - Test summary statistics calculation
    - Test document preview display
    - _Requirements: 10.1, 10.2_

- [ ] 18. Implement team lead conflict audit dashboard (optional)
  - [ ] 18.1 Create `render_conflict_audit_dashboard()` function in `app.py`
    - Display list of all detected conflicts
    - Show resolution decisions and reasoning
    - Allow filtering by date range and doc_type
    - _Requirements: 7.1, 7.2_
  
  - [ ] 18.2 Write unit tests for conflict audit dashboard
    - Test conflict list display
    - Test filtering functionality
    - Test resolution reasoning display
    - _Requirements: 7.1, 7.2_

- [x] 19. Checkpoint - Ensure UI tests pass
  - Run all Streamlit UI tests
  - Manually test role-based dashboard rendering
  - Verify conflict warning and ticket creation work correctly
  - Ask the user if questions arise

- [x] 20. Create demo data and pre-generate embeddings
  - [x] 20.1 Create sample documents in `data/` directory
    - Add 2-3 policy PDFs with version conflicts (e.g., Refund_Policy_v1_2023.pdf, Refund_Policy_v2_2024.pdf)
    - Add 1-2 pricing Excel files with client data
    - Add 2-3 EML files with email threads
    - _Requirements: All (demo preparation)_
  
  - [x] 20.2 Run ingestion pipeline on demo data
    - Parse all demo documents
    - Generate embeddings using OpenAI
    - Store in ChromaDB with persistence to `./chroma_db`
    - Commit `chroma_db/` directory to repository
    - _Requirements: All (demo preparation)_
  
  - [x] 20.3 Verify demo queries work correctly
    - Test query that triggers conflict detection
    - Test query that retrieves from multiple doc types
    - Test citation formatting for all doc types
    - _Requirements: All (demo preparation)_

- [~] 21. Integration testing and polish
  - [x] 21.1 Write end-to-end integration tests
    - Test complete flow: ingestion → query → conflict detection → answer
    - Test Google Drive/Gmail API integration (if implemented)
    - Test ChromaDB persistence across application restarts
    - _Requirements: All_
  
  - [x] 21.2 Performance testing
    - Measure query response time (target: < 3 seconds)
    - Test with varying collection sizes (100, 1000, 10000 chunks)
    - Optimize if necessary
    - _Requirements: All_
  
  - [-] 21.3 Error handling and logging
    - Add comprehensive error handling for all API calls
    - Add logging for debugging and monitoring
    - Test error scenarios (API failures, malformed files, etc.)
    - _Requirements: All_
  
  - [~] 21.4 Documentation and README
    - Update README.md with setup instructions
    - Document environment variables in .env.example
    - Add usage examples and screenshots
    - _Requirements: All_

- [~] 22. Final checkpoint - Ensure all tests pass
  - Run full test suite (unit tests, property tests, integration tests)
  - Verify demo works end-to-end
  - Ensure all requirements are covered
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- Integration tests verify external service interactions
- Checkpoints ensure incremental validation at reasonable breaks
- Demo data and pre-generated embeddings are committed to repository for fast demo startup
- Focus on hackathon-ready deliverables with 5-hour timeline
