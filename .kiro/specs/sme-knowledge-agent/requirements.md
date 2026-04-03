# Requirements document

## Introduction
This spec defines the SME Knowledge Agent — a conversational system that ingests multi-format company documents (PDF, Excel, email) and answers employee queries with precise citations and autonomous conflict resolution.

---

## Requirement 1: Document ingestion — PDF

**User story:** As a Knowledge Manager, I want to upload policy PDFs from Google Drive so that the system understands document sections and versions natively.

**Acceptance criteria:**
WHEN a PDF is ingested
THE SYSTEM SHALL extract the table of contents and identify named sections
WHEN a PDF section is stored
THE SYSTEM SHALL attach metadata: {source filename, section_title, section_number, page_number, doc_date, doc_type: "policy"}
WHEN doc_date cannot be parsed from content
THE SYSTEM SHALL extract it from the filename (e.g. "Refund_Policy_v2_March2024.pdf" → 2024-03-01)

---

## Requirement 2: Document ingestion — Excel

**User story:** As a Knowledge Manager, I want pricing spreadsheets indexed by row so that employees can retrieve exact client data with row-level citations.

**Acceptance criteria:**
WHEN an Excel file is ingested
THE SYSTEM SHALL convert each data row into a natural language string preserving all column values
WHEN an Excel row is stored
THE SYSTEM SHALL attach metadata: {source, sheet_name, row_number, client, doc_date, doc_type: "excel"}
WHEN an Excel cell contains a formula
THE SYSTEM SHALL store the computed value, not the raw formula expression

---

## Requirement 3: Document ingestion — Email

**User story:** As a Knowledge Manager, I want email threads ingested so that the system can detect when old email advice contradicts current policy documents.

**Acceptance criteria:**
WHEN an EML file is uploaded
THE SYSTEM SHALL parse sender, date, subject, and body from each message in the thread
WHEN Gmail API is connected
THE SYSTEM SHALL search and ingest emails matching a client keyword provided by the admin
WHEN an email message is stored
THE SYSTEM SHALL attach metadata: {sender, doc_date, subject, thread_id, client_keyword, doc_type: "email"}

---

## Requirement 4: Hybrid retrieval

**User story:** As an Employee, I want to ask a natural language question and receive an answer that searches across all document types simultaneously.

**Acceptance criteria:**
WHEN a user submits a query
THE SYSTEM SHALL perform vector similarity search across PDF, Excel, and email chunks in a single ChromaDB collection
WHEN retrieval results are returned
THE SYSTEM SHALL include the full metadata dict for every retrieved chunk
WHEN doc_type filter is applied
THE SYSTEM SHALL restrict retrieval to only chunks matching the specified type

---

## Requirement 5: Exact source citation

**User story:** As an Employee, I want every answer to show exactly where the information came from so I can verify it before telling a client.

**Acceptance criteria:**
WHEN a PDF chunk is cited
THE SYSTEM SHALL display: filename, section_title, section_number, page_number
WHEN an Excel chunk is cited
THE SYSTEM SHALL display: filename, sheet_name, row_number
WHEN an email chunk is cited
THE SYSTEM SHALL display: sender, doc_date, subject line

---

## Requirement 6: Conflict detection

**User story:** As an Employee, I want the system to warn me when two documents contradict each other so I never accidentally use outdated information.

**Acceptance criteria:**
WHEN two retrieved chunks share the same section_title but have different doc_dates and different content
THE SYSTEM SHALL classify this as a conflict
WHEN a conflict is detected
THE SYSTEM SHALL apply the date-priority rule: the chunk with the most recent doc_date is the winner
WHEN a conflict is resolved
THE SYSTEM SHALL generate a plain-language diff explanation: e.g. "Refund window changed from 30 to 60 days"
WHEN an email chunk predates the winning PDF chunk on the same topic
THE SYSTEM SHALL flag the email as containing outdated advice

---

## Requirement 7: Conflict transparency UI

**User story:** As an Employee, I want to see a clear warning when a conflict was detected and resolved so I understand why a specific source was chosen.

**Acceptance criteria:**
WHEN a conflict has been resolved
THE SYSTEM SHALL display a red warning banner above the answer
WHEN the user clicks "View side-by-side"
THE SYSTEM SHALL display the winner and rejected chunks with differences highlighted
WHEN no conflict exists
THE SYSTEM SHALL NOT display any conflict UI elements

---

## Requirement 8: CRM ticket creation

**User story:** As an Employee, I want to create a support ticket pre-populated with the AI answer and sources so I don't have to copy-paste manually.

**Acceptance criteria:**
WHEN the user clicks "Create Ticket"
THE SYSTEM SHALL pre-populate: client name (from Excel metadata), query text, AI answer, source citations, conflict flag (yes/no)
WHEN a conflict was resolved in the current query
THE SYSTEM SHALL set conflict_flag = true and include the resolution reasoning in the ticket

---

## Requirement 9: Google Workspace integration

**User story:** As a Knowledge Manager, I want to connect my Google Drive folder so documents are auto-ingested without manual file uploads.

**Acceptance criteria:**
WHEN the admin provides a Drive folder ID
THE SYSTEM SHALL list and download all PDF files and export all Sheets as .xlsx automatically
WHEN Gmail API is authenticated
THE SYSTEM SHALL search emails by client keyword and ingest matching threads
WHEN OAuth setup fails or times out after 45 minutes
THE SYSTEM SHALL fall back to manual file upload without breaking other pipeline stages

---

## Requirement 10: Admin ingestion dashboard

**User story:** As a Knowledge Manager, I want to see a processing summary after ingestion so I can verify the system captured the documents correctly.

**Acceptance criteria:**
WHEN ingestion completes
THE SYSTEM SHALL display: total documents processed, total sections indexed, total Excel rows stored, total email messages parsed
WHEN the admin clicks a processed document
THE SYSTEM SHALL show a preview of the extracted sections or rows