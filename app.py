"""
SME Knowledge Agent - Streamlit Application

Main entry point for the web application with role-based authentication.
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
from pathlib import Path
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="SME Knowledge Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load authentication configuration
def load_auth_config():
    """Load authentication configuration from config.yaml."""
    config_path = Path("config.yaml")
    
    if not config_path.exists():
        # Create default config if it doesn't exist
        create_default_config()
    
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    return config


def create_default_config():
    """Create default authentication configuration."""
    # Hash passwords using the correct API
    passwords = ['password123', 'manager123', 'admin123', 'sysadmin123']
    hasher = stauth.Hasher()
    hashed_passwords = [hasher.hash(pwd) for pwd in passwords]
    
    default_config = {
        'credentials': {
            'usernames': {
                'employee1': {
                    'name': 'John Doe',
                    'password': hashed_passwords[0],
                    'role': 'employee'
                },
                'manager1': {
                    'name': 'Jane Smith',
                    'password': hashed_passwords[1],
                    'role': 'team_lead'
                },
                'admin1': {
                    'name': 'Admin User',
                    'password': hashed_passwords[2],
                    'role': 'knowledge_manager'
                },
                'sysadmin': {
                    'name': 'System Admin',
                    'password': hashed_passwords[3],
                    'role': 'system_admin'
                }
            }
        },
        'cookie': {
            'name': 'sme_knowledge_agent',
            'key': 'sme_secret_key_12345',
            'expiry_days': 30
        },
        'preauthorized': {
            'emails': []
        }
    }
    
    with open('config.yaml', 'w') as file:
        yaml.dump(default_config, file, default_flow_style=False)
    
    return default_config


# Initialize authentication
def init_authentication():
    """Initialize Streamlit authenticator."""
    config = load_auth_config()
    
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    return authenticator, config


# Main application
def main():
    """Main application entry point."""
    
    # Initialize authentication
    authenticator, config = init_authentication()
    
    # Login widget - new API returns dict
    try:
        authenticator.login()
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return
    
    # Check authentication status from session state
    if st.session_state.get("authentication_status") == False:
        st.error('Username/password is incorrect')
        st.info("**Demo Credentials:**")
        st.info("Employee: `employee1` / `password123`")
        st.info("Team Lead: `manager1` / `manager123`")
        st.info("Knowledge Manager: `admin1` / `admin123`")
        st.info("System Admin: `sysadmin` / `sysadmin123`")
    
    elif st.session_state.get("authentication_status") == None:
        st.warning('Please enter your username and password')
        st.info("**Demo Credentials:**")
        st.info("Employee: `employee1` / `password123`")
        st.info("Team Lead: `manager1` / `manager123`")
        st.info("Knowledge Manager: `admin1` / `admin123`")
        st.info("System Admin: `sysadmin` / `sysadmin123`")
    
    elif st.session_state.get("authentication_status"):
        # Get user info from session state
        name = st.session_state.get("name")
        username = st.session_state.get("username")
        
        # Get user role from config
        role = config['credentials']['usernames'][username]['role']
        
        # Store role in session state
        st.session_state['role'] = role
        
        # Sidebar with user info and logout
        with st.sidebar:
            st.write(f'Welcome *{name}*')
            st.write(f'Role: **{role.replace("_", " ").title()}**')
            authenticator.logout(location='sidebar')
            st.divider()
        
        # Route to appropriate dashboard based on role
        route_dashboard(role)


def route_dashboard(role: str):
    """Route to appropriate dashboard based on user role."""
    
    if role == 'employee':
        render_employee_dashboard()
    
    elif role == 'team_lead':
        render_team_lead_dashboard()
    
    elif role == 'knowledge_manager':
        render_knowledge_manager_dashboard()
    
    elif role == 'system_admin':
        render_system_admin_dashboard()
    
    else:
        st.error(f"Unknown role: {role}")
        st.info("Defaulting to employee dashboard")
        render_employee_dashboard()


def render_citation(chunk: dict) -> str:
    """
    Format citation based on doc_type.
    
    Args:
        chunk: Document chunk with metadata
        
    Returns:
        Formatted citation string:
        - PDF: "Refund Policy v2 (Section 3.2: Returns, Page 5)"
        - Excel: "Pricing_2024.xlsx (Sheet: Q1, Row 42)"
        - Email: "From: john@acme.com (2024-01-15, Subject: Discount approval)"
    """
    metadata = chunk.get('metadata', {})
    doc_type = metadata.get('doc_type', '')
    source = metadata.get('source', 'Unknown')
    
    if doc_type == 'policy':
        # PDF citation format
        section_title = metadata.get('section_title', '')
        section_number = metadata.get('section_number', '')
        page_number = metadata.get('page_number', '')
        
        parts = [source]
        if section_number and section_title:
            parts.append(f"Section {section_number}: {section_title}")
        elif section_title:
            parts.append(f"Section: {section_title}")
        elif section_number:
            parts.append(f"Section {section_number}")
        
        if page_number:
            parts.append(f"Page {page_number}")
        
        return f"{parts[0]} ({', '.join(parts[1:])})" if len(parts) > 1 else parts[0]
    
    elif doc_type == 'excel':
        # Excel citation format
        sheet_name = metadata.get('sheet_name', '')
        row_number = metadata.get('row_number', '')
        
        parts = []
        if sheet_name:
            parts.append(f"Sheet: {sheet_name}")
        if row_number:
            parts.append(f"Row {row_number}")
        
        return f"{source} ({', '.join(parts)})" if parts else source
    
    elif doc_type == 'email':
        # Email citation format
        sender = metadata.get('sender', '')
        doc_date = metadata.get('doc_date', '')
        subject = metadata.get('subject', '')
        
        parts = []
        if sender:
            parts.append(f"From: {sender}")
        if doc_date:
            # Format date if it's a datetime object or ISO string
            if isinstance(doc_date, str):
                # Extract just the date part if it's ISO format
                date_str = doc_date.split('T')[0] if 'T' in doc_date else doc_date
                parts.append(date_str)
            else:
                parts.append(str(doc_date))
        if subject:
            parts.append(f"Subject: {subject}")
        
        return f"Email ({', '.join(parts)})" if parts else f"Email from {source}"
    
    else:
        # Fallback for unknown doc types
        return source


def render_conflict_warning(conflicts):
    """
    Display red warning banner when conflicts detected.
    Shows "View side-by-side" button to expand conflict details.
    
    Args:
        conflicts: List of Conflict objects from conflict_detector
    """
    if not conflicts:
        return
    
    # Display warning banner
    st.error(f"⚠️ **Conflict Detected**: {len(conflicts)} contradiction(s) found and resolved using date-priority rule.")
    
    # Show side-by-side view button
    if st.button("🔍 View side-by-side comparison", key="view_conflicts"):
        st.session_state['show_conflict_details'] = True
    
    # Display side-by-side view if requested
    if st.session_state.get('show_conflict_details', False):
        render_side_by_side_conflict_view(conflicts)


def render_side_by_side_conflict_view(conflicts):
    """
    Display winner and rejected chunks side-by-side with differences highlighted.
    Shows diff explanation for each conflict.
    
    Args:
        conflicts: List of Conflict objects
    """
    st.divider()
    st.subheader("📊 Conflict Resolution Details")
    
    for i, conflict in enumerate(conflicts, 1):
        st.markdown(f"### Conflict {i}: {conflict.conflict_type.replace('_', ' ').title()}")
        
        # Display diff explanation
        st.info(f"**What changed:** {conflict.diff_explanation}")
        
        # Create two columns for side-by-side comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ✅ Winner (Most Recent)")
            winner_meta = conflict.winner.get('metadata', {})
            st.markdown(f"**Source:** {winner_meta.get('source', 'Unknown')}")
            st.markdown(f"**Date:** {winner_meta.get('doc_date', 'Unknown')}")
            st.markdown(f"**Type:** {winner_meta.get('doc_type', 'Unknown')}")
            
            # Display additional metadata based on doc_type
            if winner_meta.get('doc_type') == 'policy':
                if winner_meta.get('section_title'):
                    st.markdown(f"**Section:** {winner_meta.get('section_title')}")
                if winner_meta.get('page_number'):
                    st.markdown(f"**Page:** {winner_meta.get('page_number')}")
            elif winner_meta.get('doc_type') == 'excel':
                if winner_meta.get('sheet_name'):
                    st.markdown(f"**Sheet:** {winner_meta.get('sheet_name')}")
                if winner_meta.get('row_number'):
                    st.markdown(f"**Row:** {winner_meta.get('row_number')}")
            elif winner_meta.get('doc_type') == 'email':
                if winner_meta.get('sender'):
                    st.markdown(f"**From:** {winner_meta.get('sender')}")
                if winner_meta.get('subject'):
                    st.markdown(f"**Subject:** {winner_meta.get('subject')}")
            
            # Display content in success container
            with st.container():
                st.success(conflict.winner.get('content', ''))
        
        with col2:
            st.markdown("#### ❌ Rejected (Outdated)")
            
            # Display all rejected chunks
            for j, rejected in enumerate(conflict.rejected, 1):
                rejected_meta = rejected.get('metadata', {})
                
                if len(conflict.rejected) > 1:
                    st.markdown(f"**Rejected version {j}:**")
                
                st.markdown(f"**Source:** {rejected_meta.get('source', 'Unknown')}")
                st.markdown(f"**Date:** {rejected_meta.get('doc_date', 'Unknown')}")
                st.markdown(f"**Type:** {rejected_meta.get('doc_type', 'Unknown')}")
                
                # Display additional metadata based on doc_type
                if rejected_meta.get('doc_type') == 'policy':
                    if rejected_meta.get('section_title'):
                        st.markdown(f"**Section:** {rejected_meta.get('section_title')}")
                    if rejected_meta.get('page_number'):
                        st.markdown(f"**Page:** {rejected_meta.get('page_number')}")
                elif rejected_meta.get('doc_type') == 'excel':
                    if rejected_meta.get('sheet_name'):
                        st.markdown(f"**Sheet:** {rejected_meta.get('sheet_name')}")
                    if rejected_meta.get('row_number'):
                        st.markdown(f"**Row:** {rejected_meta.get('row_number')}")
                elif rejected_meta.get('doc_type') == 'email':
                    if rejected_meta.get('sender'):
                        st.markdown(f"**From:** {rejected_meta.get('sender')}")
                    if rejected_meta.get('subject'):
                        st.markdown(f"**Subject:** {rejected_meta.get('subject')}")
                
                # Display content in warning container
                with st.container():
                    st.warning(rejected.get('content', ''))
                
                if j < len(conflict.rejected):
                    st.markdown("---")
        
        # Add separator between conflicts
        if i < len(conflicts):
            st.divider()


def render_ticket_creation(query_context: dict):
    """
    Display "Create Ticket" button and pre-populate form with query context.
    
    Args:
        query_context: Dictionary containing:
            - query_text: User's original query
            - ai_answer: Generated response
            - source_citations: List of formatted citation strings
            - conflicts: List of Conflict objects (empty if none)
            - source_chunks: List of retrieved chunks with metadata
    """
    st.divider()
    st.subheader("📝 Create Support Ticket")
    
    # Extract client name from Excel metadata if available
    client_name = None
    for chunk in query_context.get('source_chunks', []):
        metadata = chunk.get('metadata', {})
        if metadata.get('doc_type') == 'excel' and metadata.get('client'):
            client_name = metadata['client']
            break
    
    # Determine conflict flag and resolution reasoning
    conflicts = query_context.get('conflicts', [])
    conflict_flag = len(conflicts) > 0
    resolution_reasoning = ""
    
    if conflict_flag:
        # Combine all diff explanations
        resolution_reasoning = "\n\n".join([
            f"Conflict {i+1}: {conflict.diff_explanation}"
            for i, conflict in enumerate(conflicts)
        ])
    
    # Create ticket button
    if st.button("🎫 Create Ticket", type="primary"):
        st.session_state['show_ticket_form'] = True
    
    # Display ticket form if button clicked
    if st.session_state.get('show_ticket_form', False):
        with st.form("ticket_form"):
            st.write("**Ticket Details**")
            
            # Client name field
            ticket_client = st.text_input(
                "Client Name",
                value=client_name if client_name else "",
                placeholder="Enter client name" if not client_name else ""
            )
            
            # Query text field (pre-populated, read-only display)
            st.text_area(
                "Query",
                value=query_context.get('query_text', ''),
                height=80,
                disabled=True
            )
            
            # AI answer field (pre-populated, read-only display)
            st.text_area(
                "AI Answer",
                value=query_context.get('ai_answer', ''),
                height=150,
                disabled=True
            )
            
            # Source citations field (pre-populated, read-only display)
            citations_text = "\n".join([
                f"{i+1}. {citation}"
                for i, citation in enumerate(query_context.get('source_citations', []))
            ])
            st.text_area(
                "Source Citations",
                value=citations_text,
                height=100,
                disabled=True
            )
            
            # Conflict flag display
            if conflict_flag:
                st.warning(f"⚠️ Conflict Detected: {len(conflicts)} contradiction(s) resolved")
                
                # Resolution reasoning field (pre-populated, read-only display)
                st.text_area(
                    "Conflict Resolution Reasoning",
                    value=resolution_reasoning,
                    height=120,
                    disabled=True
                )
            else:
                st.info("✓ No conflicts detected")
            
            # Additional notes field (editable)
            additional_notes = st.text_area(
                "Additional Notes (optional)",
                placeholder="Add any additional context or notes...",
                height=80
            )
            
            # Form submission buttons
            col1, col2 = st.columns([1, 5])
            with col1:
                submitted = st.form_submit_button("Submit Ticket", type="primary")
            with col2:
                cancelled = st.form_submit_button("Cancel")
            
            if submitted:
                # Validate required fields
                if not ticket_client:
                    st.error("Client name is required")
                else:
                    # Create ticket data structure
                    ticket_data = {
                        'client_name': ticket_client,
                        'query_text': query_context.get('query_text', ''),
                        'ai_answer': query_context.get('ai_answer', ''),
                        'source_citations': query_context.get('source_citations', []),
                        'conflict_flag': conflict_flag,
                        'resolution_reasoning': resolution_reasoning if conflict_flag else None,
                        'additional_notes': additional_notes,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # Store ticket in session state (in real app, would send to CRM)
                    if 'tickets' not in st.session_state:
                        st.session_state['tickets'] = []
                    st.session_state['tickets'].append(ticket_data)
                    
                    st.success("✓ Ticket created successfully!")
                    st.session_state['show_ticket_form'] = False
                    st.rerun()
            
            if cancelled:
                st.session_state['show_ticket_form'] = False
                st.rerun()


def render_query_interface():
    """
    Display text input for natural language query.
    Call query engine on submission and display AI-generated answer.
    """
    st.write("Ask questions about company policies, pricing, and procedures.")
    
    # Text input for query
    query = st.text_input(
        "Enter your question:",
        placeholder="e.g., What is our refund policy?",
        key="query_input"
    )
    
    # Search button
    if st.button("Search", type="primary"):
        if query:
            # Reset conflict details view on new search
            st.session_state['show_conflict_details'] = False
            st.session_state['show_ticket_form'] = False
            
            with st.spinner("Searching knowledge base..."):
                try:
                    # Import query engine components
                    from storage.chroma_store import init_chroma_collection
                    from retrieval.query_engine import create_query_engine, query_with_metadata
                    from retrieval.conflict_detector import detect_conflicts
                    from dotenv import load_dotenv
                    
                    # Load environment variables
                    load_dotenv()
                    
                    # Check for API key
                    if not os.getenv('OPENAI_API_KEY'):
                        st.error("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file.")
                        return
                    
                    # Initialize ChromaDB
                    client, collection = init_chroma_collection(persist_directory="./chroma_db")
                    
                    # Check if collection has data
                    if collection.count() == 0:
                        st.warning("No documents in knowledge base. Please upload documents first.")
                        return
                    
                    # Create query engine
                    query_engine = create_query_engine(collection)
                    
                    # Execute query
                    result = query_with_metadata(query_engine, query)
                    
                    # Detect conflicts in retrieved chunks
                    conflicts = detect_conflicts(result.source_chunks)
                    
                    # Display conflict warning if conflicts detected
                    render_conflict_warning(conflicts)
                    
                    # Display answer
                    st.success("Answer:")
                    st.write(result.answer)
                    
                    # Display citations
                    source_citations = []
                    if result.source_chunks:
                        st.divider()
                        st.subheader("Sources:")
                        for i, chunk in enumerate(result.source_chunks, 1):
                            citation = render_citation(chunk)
                            source_citations.append(citation)
                            with st.expander(f"📄 Source {i}: {citation}"):
                                st.write(chunk.get('content', ''))
                                if chunk.get('score'):
                                    st.caption(f"Relevance score: {chunk['score']:.2f}")
                    
                    # Display response time
                    st.caption(f"Response time: {result.response_time_ms}ms")
                    
                    # Store query context for ticket creation
                    query_context = {
                        'query_text': query,
                        'ai_answer': result.answer,
                        'source_citations': source_citations,
                        'conflicts': conflicts,
                        'source_chunks': result.source_chunks
                    }
                    
                    # Render ticket creation interface
                    render_ticket_creation(query_context)
                    
                except ImportError as e:
                    st.error(f"Missing dependencies: {e}")
                    st.info("Please ensure all required packages are installed.")
                except Exception as e:
                    st.error(f"Error processing query: {e}")
                    st.info("Please check your configuration and try again.")
        else:
            st.warning("Please enter a question")


# Dashboard implementations
def render_employee_dashboard():
    """Render employee dashboard with query interface."""
    st.title("🔍 Knowledge Search")
    render_query_interface()


def render_team_lead_dashboard():
    """Render team lead dashboard with query interface and conflict audit."""
    st.title("🔍 Knowledge Search (Team Lead)")
    
    # Tab layout
    tab1, tab2 = st.tabs(["Search", "Conflict Audit"])
    
    with tab1:
        render_query_interface()
    
    with tab2:
        st.write("Review detected conflicts and resolution decisions.")
        st.info("Conflict audit dashboard will be implemented in Task 18")


def render_document_upload():
    """
    Display file uploader for PDF, Excel, EML files.
    Call appropriate parser on upload, generate embeddings using OpenAI,
    store chunks in ChromaDB.
    """
    st.write("Upload policy PDFs, pricing Excel files, and email threads.")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'xlsx', 'xls', 'eml'],
        accept_multiple_files=True,
        help="Supported formats: PDF (policies), Excel (pricing), EML (emails)"
    )
    
    if st.button("Process Documents", type="primary"):
        if not uploaded_files:
            st.warning("Please upload at least one file")
            return
        
        # Check for OpenAI API key
        if not os.getenv('OPENAI_API_KEY'):
            st.error("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file.")
            return
        
        with st.spinner("Processing documents..."):
            try:
                from ingestion.pdf_parser import extract_pdf_sections
                from ingestion.excel_parser import extract_excel_rows
                from ingestion.email_parser import parse_eml_file
                from storage.chroma_store import init_chroma_collection, upsert_chunks, DocumentChunk
                from llama_index.embeddings.openai import OpenAIEmbedding
                import tempfile
                
                # Initialize ChromaDB
                client, collection = init_chroma_collection(persist_directory="./chroma_db")
                
                # Initialize embedding model
                embed_model = OpenAIEmbedding(
                    model="text-embedding-3-small",
                    api_key=os.getenv('OPENAI_API_KEY')
                )
                
                # Track ingestion statistics
                stats = {
                    'total_documents': 0,
                    'total_sections': 0,
                    'total_excel_rows': 0,
                    'total_email_messages': 0,
                    'processed_files': []
                }
                
                # Process each uploaded file
                for uploaded_file in uploaded_files:
                    file_ext = Path(uploaded_file.name).suffix.lower()
                    
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name
                    
                    try:
                        chunks_to_upsert = []
                        
                        if file_ext == '.pdf':
                            # Parse PDF sections
                            sections = extract_pdf_sections(tmp_path)
                            stats['total_sections'] += len(sections)
                            
                            # Convert to DocumentChunk objects
                            for section in sections:
                                # Generate embedding
                                embedding = embed_model.get_text_embedding(section.content)
                                
                                # Create chunk
                                chunk = DocumentChunk(
                                    id=f"pdf_{section.source}_{section.section_number}".replace(" ", "_").replace("/", "_"),
                                    content=section.content,
                                    embedding=embedding,
                                    metadata={
                                        'source': section.source,
                                        'doc_type': section.doc_type,
                                        'doc_date': section.doc_date,
                                        'section_title': section.section_title,
                                        'section_number': section.section_number,
                                        'page_number': section.page_number
                                    }
                                )
                                chunks_to_upsert.append(chunk)
                        
                        elif file_ext in ['.xlsx', '.xls']:
                            # Parse Excel rows
                            rows = extract_excel_rows(tmp_path)
                            stats['total_excel_rows'] += len(rows)
                            
                            # Convert to DocumentChunk objects
                            for row in rows:
                                # Generate embedding
                                embedding = embed_model.get_text_embedding(row.content)
                                
                                # Create chunk
                                chunk = DocumentChunk(
                                    id=f"excel_{row.source}_{row.sheet_name}_{row.row_number}".replace(" ", "_").replace("/", "_"),
                                    content=row.content,
                                    embedding=embedding,
                                    metadata={
                                        'source': row.source,
                                        'doc_type': row.doc_type,
                                        'doc_date': row.doc_date,
                                        'sheet_name': row.sheet_name,
                                        'row_number': row.row_number,
                                        'client': row.client
                                    }
                                )
                                chunks_to_upsert.append(chunk)
                        
                        elif file_ext == '.eml':
                            # Parse email messages
                            messages = parse_eml_file(tmp_path)
                            stats['total_email_messages'] += len(messages)
                            
                            # Convert to DocumentChunk objects
                            for message in messages:
                                # Generate embedding
                                embedding = embed_model.get_text_embedding(message.content)
                                
                                # Create chunk
                                chunk = DocumentChunk(
                                    id=f"email_{message.thread_id}_{message.doc_date.isoformat()}".replace(" ", "_").replace("/", "_").replace(":", "_"),
                                    content=message.content,
                                    embedding=embedding,
                                    metadata={
                                        'source': uploaded_file.name,
                                        'doc_type': message.doc_type,
                                        'doc_date': message.doc_date,
                                        'sender': message.sender,
                                        'subject': message.subject,
                                        'thread_id': message.thread_id,
                                        'client_keyword': message.client_keyword
                                    }
                                )
                                chunks_to_upsert.append(chunk)
                        
                        # Upsert chunks to ChromaDB
                        if chunks_to_upsert:
                            upsert_chunks(collection, chunks_to_upsert)
                            stats['total_documents'] += 1
                            stats['processed_files'].append({
                                'name': uploaded_file.name,
                                'type': file_ext,
                                'chunks': len(chunks_to_upsert)
                            })
                    
                    finally:
                        # Clean up temporary file
                        Path(tmp_path).unlink(missing_ok=True)
                
                # Store stats in session state for dashboard
                st.session_state['ingestion_stats'] = stats
                
                # Display success message
                st.success(f"✓ Successfully processed {stats['total_documents']} document(s)!")
                
                # Display summary
                st.info(f"""
                **Ingestion Summary:**
                - PDF sections: {stats['total_sections']}
                - Excel rows: {stats['total_excel_rows']}
                - Email messages: {stats['total_email_messages']}
                """)
                
            except Exception as e:
                st.error(f"Error processing documents: {e}")
                import traceback
                st.code(traceback.format_exc())


def render_ingestion_dashboard():
    """
    Display summary statistics (total_documents, total_sections, total_excel_rows, total_email_messages).
    Allow clicking on document to preview extracted sections/rows.
    """
    st.write("View ingestion statistics and document previews.")
    
    # Get stats from session state or ChromaDB
    if 'ingestion_stats' in st.session_state:
        stats = st.session_state['ingestion_stats']
    else:
        # Load stats from ChromaDB
        try:
            from storage.chroma_store import init_chroma_collection
            
            client, collection = init_chroma_collection(persist_directory="./chroma_db")
            
            # Get all chunks and compute stats
            all_chunks = collection.get()
            
            stats = {
                'total_documents': 0,
                'total_sections': 0,
                'total_excel_rows': 0,
                'total_email_messages': 0,
                'processed_files': []
            }
            
            # Count by doc_type
            doc_sources = set()
            for metadata in all_chunks.get('metadatas', []):
                doc_type = metadata.get('doc_type', '')
                source = metadata.get('source', '')
                
                doc_sources.add(source)
                
                if doc_type == 'policy':
                    stats['total_sections'] += 1
                elif doc_type == 'excel':
                    stats['total_excel_rows'] += 1
                elif doc_type == 'email':
                    stats['total_email_messages'] += 1
            
            stats['total_documents'] = len(doc_sources)
            
        except Exception as e:
            st.error(f"Error loading ingestion statistics: {e}")
            stats = {
                'total_documents': 0,
                'total_sections': 0,
                'total_excel_rows': 0,
                'total_email_messages': 0,
                'processed_files': []
            }
    
    # Display summary statistics
    st.subheader("📊 Ingestion Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", stats['total_documents'])
    
    with col2:
        st.metric("PDF Sections", stats['total_sections'])
    
    with col3:
        st.metric("Excel Rows", stats['total_excel_rows'])
    
    with col4:
        st.metric("Email Messages", stats['total_email_messages'])
    
    # Display processed files with preview
    if stats.get('processed_files'):
        st.divider()
        st.subheader("📁 Processed Files")
        
        for file_info in stats['processed_files']:
            with st.expander(f"📄 {file_info['name']} ({file_info['chunks']} chunks)"):
                st.write(f"**File type:** {file_info['type']}")
                st.write(f"**Chunks extracted:** {file_info['chunks']}")
                
                # Load and display preview of chunks
                try:
                    from storage.chroma_store import init_chroma_collection
                    
                    client, collection = init_chroma_collection(persist_directory="./chroma_db")
                    
                    # Query chunks for this file
                    results = collection.get(
                        where={"source": file_info['name']},
                        limit=5
                    )
                    
                    if results['ids']:
                        st.write("**Preview (first 5 chunks):**")
                        for i, (chunk_id, content, metadata) in enumerate(zip(
                            results['ids'],
                            results['documents'],
                            results['metadatas']
                        ), 1):
                            with st.container():
                                st.markdown(f"**Chunk {i}:**")
                                
                                # Display metadata based on doc_type
                                doc_type = metadata.get('doc_type', '')
                                if doc_type == 'policy':
                                    st.caption(f"Section {metadata.get('section_number', '')}: {metadata.get('section_title', '')} (Page {metadata.get('page_number', '')})")
                                elif doc_type == 'excel':
                                    st.caption(f"Sheet: {metadata.get('sheet_name', '')}, Row: {metadata.get('row_number', '')}")
                                elif doc_type == 'email':
                                    st.caption(f"From: {metadata.get('sender', '')}, Subject: {metadata.get('subject', '')}")
                                
                                # Display content (truncated)
                                content_preview = content[:200] + "..." if len(content) > 200 else content
                                st.text(content_preview)
                                
                                if i < len(results['ids']):
                                    st.markdown("---")
                    
                except Exception as e:
                    st.error(f"Error loading preview: {e}")
    else:
        st.info("No documents processed yet. Upload documents in the 'Upload Documents' tab.")


def render_knowledge_manager_dashboard():
    """Render knowledge manager dashboard with document upload."""
    st.title("📚 Document Management")
    
    # Tab layout
    tab1, tab2 = st.tabs(["Upload Documents", "Ingestion Dashboard"])
    
    with tab1:
        render_document_upload()
    
    with tab2:
        render_ingestion_dashboard()


def render_system_admin_dashboard():
    """Render system admin dashboard with configuration options."""
    st.title("⚙️ System Administration")
    
    st.write("Configure workspace settings and governance rules.")
    
    # Placeholder for admin features
    st.info("System admin features will be implemented later")
    
    with st.expander("User Management"):
        st.write("Manage users and roles")
    
    with st.expander("Governance Rules"):
        st.write("Configure conflict resolution rules")
    
    with st.expander("API Configuration"):
        st.write("Configure OpenAI and Google API settings")


if __name__ == "__main__":
    main()
