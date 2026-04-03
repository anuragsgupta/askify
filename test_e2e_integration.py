"""
End-to-end integration tests for SME Knowledge Agent.

Tests complete flow: ingestion → query → conflict detection → answer
Tests Google Drive/Gmail API integration (if implemented)
Tests ChromaDB persistence across application restarts
"""

import os
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TestE2EIngestionToQuery:
    """Test complete flow from document ingestion to query answering."""
    
    @pytest.fixture
    def test_chroma_dir(self):
        """Create temporary ChromaDB directory for testing."""
        test_dir = tempfile.mkdtemp(prefix="test_chroma_e2e_")
        yield test_dir
        # Cleanup after test
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Return path to sample PDF for testing."""
        return "data/Refund_Policy_v2_March2024.pdf"
    
    @pytest.fixture
    def sample_excel_path(self):
        """Return path to sample Excel for testing."""
        return "data/Pricing_Q1_2024.xlsx"
    
    @pytest.fixture
    def sample_eml_path(self):
        """Return path to sample EML for testing."""
        return "data/Refund_Inquiry_AcmeCorp_Jan2023.eml"
    
    def test_complete_ingestion_to_query_flow(
        self, test_chroma_dir, sample_pdf_path, sample_excel_path, sample_eml_path
    ):
        """
        Test complete flow: ingest documents → query → get answer with citations.
        
        Flow:
        1. Ingest PDF, Excel, and Email documents
        2. Submit natural language query
        3. Verify answer is generated
        4. Verify citations are present
        5. Verify metadata is preserved
        """
        # Skip if OpenAI API key not available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set - skipping integration test")
        
        # Skip if sample files don't exist
        if not all([
            Path(sample_pdf_path).exists(),
            Path(sample_excel_path).exists(),
            Path(sample_eml_path).exists()
        ]):
            pytest.skip("Sample data files not found - run create_demo_data.py first")
        
        from ingestion.pdf_parser import extract_pdf_sections
        from ingestion.excel_parser import extract_excel_rows
        from ingestion.email_parser import parse_eml_file
        from storage.chroma_store import init_chroma_collection, upsert_chunks, DocumentChunk
        from retrieval.query_engine import create_query_engine, query_with_metadata
        from llama_index.embeddings.openai import OpenAIEmbedding
        
        # Step 1: Ingest documents
        print("\n[Step 1] Ingesting documents...")
        
        # Initialize ChromaDB
        client, collection = init_chroma_collection(persist_directory=test_chroma_dir)
        
        # Initialize embedding model
        embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        
        all_chunks = []
        
        # Ingest PDF
        pdf_sections = extract_pdf_sections(sample_pdf_path)
        for section in pdf_sections:
            embedding = embed_model.get_text_embedding(section.content)
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
            all_chunks.append(chunk)
        
        # Ingest Excel
        excel_rows = extract_excel_rows(sample_excel_path)
        for row in excel_rows:
            embedding = embed_model.get_text_embedding(row.content)
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
            all_chunks.append(chunk)
        
        # Ingest Email
        email_messages = parse_eml_file(sample_eml_path)
        for message in email_messages:
            embedding = embed_model.get_text_embedding(message.content)
            chunk = DocumentChunk(
                id=f"email_{message.thread_id}_{message.doc_date.isoformat()}".replace(" ", "_").replace("/", "_").replace(":", "_"),
                content=message.content,
                embedding=embedding,
                metadata={
                    'source': Path(sample_eml_path).name,
                    'doc_type': message.doc_type,
                    'doc_date': message.doc_date,
                    'sender': message.sender,
                    'subject': message.subject,
                    'thread_id': message.thread_id,
                    'client_keyword': message.client_keyword
                }
            )
            all_chunks.append(chunk)
        
        # Upsert all chunks
        upsert_chunks(collection, all_chunks)
        
        print(f"✓ Ingested {len(all_chunks)} chunks")
        assert len(all_chunks) > 0, "Should have ingested at least one chunk"
        
        # Step 2: Submit query
        print("\n[Step 2] Submitting query...")
        
        query_engine = create_query_engine(collection)
        query = "What is the refund policy?"
        
        result = query_with_metadata(query_engine, query)
        
        print(f"✓ Query executed: {query}")
        print(f"  Answer length: {len(result.answer)} characters")
        print(f"  Retrieved chunks: {len(result.source_chunks)}")
        
        # Step 3: Verify answer is generated
        assert result.answer, "Answer should not be empty"
        assert len(result.answer) > 50, "Answer should be substantial"
        
        # Step 4: Verify citations are present
        assert len(result.source_chunks) > 0, "Should have retrieved source chunks"
        
        # Step 5: Verify metadata is preserved
        for chunk in result.source_chunks:
            assert 'metadata' in chunk, "Chunk should have metadata"
            metadata = chunk['metadata']
            assert 'source' in metadata, "Metadata should have source"
            assert 'doc_type' in metadata, "Metadata should have doc_type"
            assert 'doc_date' in metadata, "Metadata should have doc_date"
            
            # Verify doc_type-specific metadata
            if metadata['doc_type'] == 'policy':
                assert 'section_title' in metadata or 'page_number' in metadata
            elif metadata['doc_type'] == 'excel':
                assert 'sheet_name' in metadata or 'row_number' in metadata
            elif metadata['doc_type'] == 'email':
                assert 'sender' in metadata or 'subject' in metadata
        
        print("✓ All metadata preserved correctly")
    
    def test_conflict_detection_in_e2e_flow(self, test_chroma_dir):
        """
        Test conflict detection in complete flow.
        
        Flow:
        1. Ingest two versions of same policy (v1 and v2)
        2. Query about the policy
        3. Verify conflict is detected
        4. Verify most recent version wins
        5. Verify diff explanation is generated
        """
        # Skip if OpenAI API key not available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set - skipping integration test")
        
        from storage.chroma_store import init_chroma_collection, upsert_chunks, DocumentChunk
        from retrieval.query_engine import create_query_engine, query_with_metadata
        from retrieval.conflict_detector import detect_conflicts
        from llama_index.embeddings.openai import OpenAIEmbedding
        
        # Initialize ChromaDB
        client, collection = init_chroma_collection(persist_directory=test_chroma_dir)
        
        # Initialize embedding model
        embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        
        # Create conflicting policy versions
        chunks = [
            {
                "id": "policy_v1_refund",
                "content": "Refund Policy: Customers can request refunds within 30 days of purchase. All refunds require manager approval.",
                "metadata": {
                    "source": "Refund_Policy_v1_2023.pdf",
                    "doc_type": "policy",
                    "doc_date": "2023-01-15T00:00:00",
                    "section_title": "Refund Policy",
                    "section_number": "3.2",
                    "page_number": 5
                }
            },
            {
                "id": "policy_v2_refund",
                "content": "Refund Policy: Customers can request refunds within 60 days of purchase. Refunds under $100 are automatically approved.",
                "metadata": {
                    "source": "Refund_Policy_v2_2024.pdf",
                    "doc_type": "policy",
                    "doc_date": "2024-03-01T00:00:00",
                    "section_title": "Refund Policy",
                    "section_number": "3.2",
                    "page_number": 5
                }
            }
        ]
        
        # Generate embeddings and create DocumentChunk objects
        doc_chunks = []
        for chunk_data in chunks:
            embedding = embed_model.get_text_embedding(chunk_data["content"])
            chunk = DocumentChunk(
                id=chunk_data["id"],
                content=chunk_data["content"],
                embedding=embedding,
                metadata=chunk_data["metadata"]
            )
            doc_chunks.append(chunk)
        
        # Upsert chunks
        upsert_chunks(collection, doc_chunks)
        
        # Query about refund policy
        query_engine = create_query_engine(collection)
        result = query_with_metadata(query_engine, "What is the refund policy?")
        
        # Detect conflicts
        conflicts = detect_conflicts(result.source_chunks)
        
        # Verify conflict detected
        assert len(conflicts) > 0, "Should detect conflict between policy versions"
        
        conflict = conflicts[0]
        
        # Verify most recent version wins
        winner_date = conflict.winner['metadata']['doc_date']
        assert "2024" in winner_date, "Most recent version (2024) should win"
        
        # Verify diff explanation generated
        assert conflict.diff_explanation, "Diff explanation should be generated"
        assert len(conflict.diff_explanation) > 0, "Diff explanation should not be empty"
        
        print(f"✓ Conflict detected and resolved correctly")
        print(f"  Winner: {conflict.winner['metadata']['source']}")
        print(f"  Explanation: {conflict.diff_explanation[:100]}...")


class TestChromaDBPersistence:
    """Test ChromaDB persistence across application restarts."""
    
    def test_persistence_across_restarts(self):
        """
        Test that embeddings persist and reload correctly.
        
        Flow:
        1. Create ChromaDB collection and add chunks
        2. Close connection
        3. Reinitialize ChromaDB with same directory
        4. Verify chunks are still present
        5. Verify metadata is preserved
        """
        # Skip if OpenAI API key not available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set - skipping integration test")
        
        from storage.chroma_store import init_chroma_collection, upsert_chunks, DocumentChunk
        from llama_index.embeddings.openai import OpenAIEmbedding
        
        # Create temporary directory
        test_dir = tempfile.mkdtemp(prefix="test_persistence_")
        
        try:
            # Step 1: Create collection and add chunks
            print("\n[Step 1] Creating collection and adding chunks...")
            
            client1, collection1 = init_chroma_collection(persist_directory=test_dir)
            
            embed_model = OpenAIEmbedding(model="text-embedding-3-small")
            
            test_chunks = [
                {
                    "id": "test_chunk_1",
                    "content": "This is a test document about refund policies.",
                    "metadata": {
                        "source": "test_doc.pdf",
                        "doc_type": "policy",
                        "doc_date": "2024-01-01T00:00:00",
                        "section_title": "Test Section"
                    }
                },
                {
                    "id": "test_chunk_2",
                    "content": "This is another test document about pricing.",
                    "metadata": {
                        "source": "test_pricing.xlsx",
                        "doc_type": "excel",
                        "doc_date": "2024-01-01T00:00:00",
                        "sheet_name": "Q1",
                        "row_number": 1
                    }
                }
            ]
            
            doc_chunks = []
            for chunk_data in test_chunks:
                embedding = embed_model.get_text_embedding(chunk_data["content"])
                chunk = DocumentChunk(
                    id=chunk_data["id"],
                    content=chunk_data["content"],
                    embedding=embedding,
                    metadata=chunk_data["metadata"]
                )
                doc_chunks.append(chunk)
            
            upsert_chunks(collection1, doc_chunks)
            
            initial_count = collection1.count()
            print(f"✓ Added {initial_count} chunks")
            
            # Step 2: Close connection (simulate restart)
            print("\n[Step 2] Closing connection...")
            del collection1
            del client1
            
            # Step 3: Reinitialize with same directory
            print("\n[Step 3] Reinitializing ChromaDB...")
            
            client2, collection2 = init_chroma_collection(persist_directory=test_dir)
            
            # Step 4: Verify chunks are still present
            reloaded_count = collection2.count()
            print(f"✓ Reloaded {reloaded_count} chunks")
            
            assert reloaded_count == initial_count, "Chunk count should match after reload"
            
            # Step 5: Verify metadata is preserved
            results = collection2.get(ids=["test_chunk_1", "test_chunk_2"])
            
            assert len(results['ids']) == 2, "Should retrieve both chunks"
            
            for metadata in results['metadatas']:
                assert 'source' in metadata, "Metadata should have source"
                assert 'doc_type' in metadata, "Metadata should have doc_type"
                assert 'doc_date' in metadata, "Metadata should have doc_date"
            
            print("✓ All metadata preserved after restart")
            
        finally:
            # Cleanup
            if Path(test_dir).exists():
                shutil.rmtree(test_dir)


class TestGoogleAPIIntegration:
    """Test Google Drive and Gmail API integration (if implemented)."""
    
    def test_google_drive_integration(self):
        """
        Test Google Drive folder download and ingestion.
        
        Note: This test requires valid Google credentials and is skipped
        if credentials are not available.
        """
        # Check if Google credentials exist
        if not Path("credentials.json").exists():
            pytest.skip("Google credentials not found - skipping Drive integration test")
        
        # Check if token exists (user has authenticated)
        if not Path("token.json").exists():
            pytest.skip("Google token not found - user needs to authenticate first")
        
        from ingestion.drive_fetcher import download_drive_folder
        
        # This is a placeholder - actual implementation would require:
        # 1. Test Drive folder ID
        # 2. Valid credentials
        # 3. Network access
        
        pytest.skip("Google Drive integration test requires manual setup")
    
    def test_gmail_integration(self):
        """
        Test Gmail API email search and ingestion.
        
        Note: This test requires valid Google credentials and is skipped
        if credentials are not available.
        """
        # Check if Google credentials exist
        if not Path("credentials.json").exists():
            pytest.skip("Google credentials not found - skipping Gmail integration test")
        
        # Check if token exists (user has authenticated)
        if not Path("token.json").exists():
            pytest.skip("Google token not found - user needs to authenticate first")
        
        # This is a placeholder - actual implementation would require:
        # 1. Test Gmail account
        # 2. Valid credentials
        # 3. Network access
        
        pytest.skip("Gmail integration test requires manual setup")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
