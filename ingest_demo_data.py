"""
Script to ingest demo data into ChromaDB with OpenAI embeddings.

Processes all documents in data/ directory:
- Parses PDFs, Excel files, and EML files
- Generates embeddings using OpenAI
- Stores in ChromaDB with persistence to ./chroma_db
"""

import os
from pathlib import Path
from typing import List
import uuid

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from ingestion.pdf_parser import extract_pdf_sections
from ingestion.excel_parser import extract_excel_rows
from ingestion.email_parser import parse_eml_file
from storage.chroma_store import init_chroma_collection, upsert_chunks, DocumentChunk


# Load environment variables
load_dotenv()

# Initialize embedding model (using local sentence-transformers)
embedding_model = None


def generate_embeddings(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]]:
    """
    Generate embeddings for a list of texts using sentence-transformers (local).
    
    Args:
        texts: List of text strings to embed
        model_name: Sentence-transformers model name (default: all-MiniLM-L6-v2)
        
    Returns:
        List of embedding vectors
    """
    global embedding_model
    
    if embedding_model is None:
        print(f"Loading embedding model: {model_name}...")
        embedding_model = SentenceTransformer(model_name)
        print("✓ Model loaded")
    
    # Generate embeddings in batches
    batch_size = 32
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = embedding_model.encode(batch, show_progress_bar=False)
        all_embeddings.extend(batch_embeddings.tolist())
    
    return all_embeddings


def ingest_pdfs(data_dir: Path) -> List[DocumentChunk]:
    """
    Ingest all PDF files from data directory.
    
    Returns:
        List of DocumentChunk objects ready for ChromaDB
    """
    pdf_files = list(data_dir.glob("*.pdf"))
    all_chunks = []
    
    print(f"\n📄 Processing {len(pdf_files)} PDF files...")
    
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
        sections = extract_pdf_sections(str(pdf_file))
        
        for section in sections:
            chunk_id = f"pdf_{pdf_file.stem}_{section.section_number}_{uuid.uuid4().hex[:8]}"
            
            chunk = DocumentChunk(
                id=chunk_id,
                content=section.content,
                embedding=None,  # Will be generated in batch
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
        
        print(f"    ✓ Extracted {len(sections)} sections")
    
    return all_chunks


def ingest_excel_files(data_dir: Path) -> List[DocumentChunk]:
    """
    Ingest all Excel files from data directory.
    
    Returns:
        List of DocumentChunk objects ready for ChromaDB
    """
    excel_files = list(data_dir.glob("*.xlsx"))
    all_chunks = []
    
    print(f"\n📊 Processing {len(excel_files)} Excel files...")
    
    for excel_file in excel_files:
        print(f"  - {excel_file.name}")
        rows = extract_excel_rows(str(excel_file))
        
        for row in rows:
            chunk_id = f"excel_{excel_file.stem}_{row.sheet_name}_{row.row_number}_{uuid.uuid4().hex[:8]}"
            
            chunk = DocumentChunk(
                id=chunk_id,
                content=row.content,
                embedding=None,  # Will be generated in batch
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
        
        print(f"    ✓ Extracted {len(rows)} rows")
    
    return all_chunks


def ingest_email_files(data_dir: Path) -> List[DocumentChunk]:
    """
    Ingest all EML files from data directory.
    
    Returns:
        List of DocumentChunk objects ready for ChromaDB
    """
    eml_files = list(data_dir.glob("*.eml"))
    all_chunks = []
    
    print(f"\n📧 Processing {len(eml_files)} EML files...")
    
    for eml_file in eml_files:
        print(f"  - {eml_file.name}")
        messages = parse_eml_file(str(eml_file))
        
        for message in messages:
            chunk_id = f"email_{eml_file.stem}_{uuid.uuid4().hex[:8]}"
            
            chunk = DocumentChunk(
                id=chunk_id,
                content=message.content,
                embedding=None,  # Will be generated in batch
                metadata={
                    'source': eml_file.name,
                    'doc_type': message.doc_type,
                    'doc_date': message.doc_date,
                    'sender': message.sender,
                    'subject': message.subject,
                    'thread_id': message.thread_id,
                    'client_keyword': message.client_keyword
                }
            )
            all_chunks.append(chunk)
        
        print(f"    ✓ Extracted {len(messages)} messages")
    
    return all_chunks


def main():
    """Main ingestion pipeline."""
    print("=" * 60)
    print("SME Knowledge Agent - Demo Data Ingestion")
    print("=" * 60)
    
    data_dir = Path("data")
    
    if not data_dir.exists():
        print(f"\n❌ Error: {data_dir} directory not found")
        return
    
    # Step 1: Parse all documents
    print("\n" + "=" * 60)
    print("STEP 1: Parsing Documents")
    print("=" * 60)
    
    pdf_chunks = ingest_pdfs(data_dir)
    excel_chunks = ingest_excel_files(data_dir)
    email_chunks = ingest_email_files(data_dir)
    
    all_chunks = pdf_chunks + excel_chunks + email_chunks
    
    print(f"\n✓ Total chunks extracted: {len(all_chunks)}")
    print(f"  - PDF sections: {len(pdf_chunks)}")
    print(f"  - Excel rows: {len(excel_chunks)}")
    print(f"  - Email messages: {len(email_chunks)}")
    
    # Step 2: Generate embeddings
    print("\n" + "=" * 60)
    print("STEP 2: Generating Embeddings")
    print("=" * 60)
    print("\nGenerating embeddings using sentence-transformers (local)...")
    
    texts = [chunk.content for chunk in all_chunks]
    embeddings = generate_embeddings(texts)
    
    # Attach embeddings to chunks
    for chunk, embedding in zip(all_chunks, embeddings):
        chunk.embedding = embedding
    
    print(f"✓ Generated {len(embeddings)} embeddings")
    
    # Step 3: Store in ChromaDB
    print("\n" + "=" * 60)
    print("STEP 3: Storing in ChromaDB")
    print("=" * 60)
    print("\nInitializing ChromaDB with persistence to ./chroma_db...")
    
    client, collection = init_chroma_collection(persist_directory="./chroma_db")
    
    print(f"Upserting {len(all_chunks)} chunks to collection...")
    upsert_chunks(collection, all_chunks)
    
    print(f"✓ Successfully stored {len(all_chunks)} chunks in ChromaDB")
    
    # Verify storage
    count = collection.count()
    print(f"✓ Verified: Collection contains {count} chunks")
    
    # Summary
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  Total documents processed: {len(pdf_chunks) + len(excel_chunks) + len(email_chunks)}")
    print(f"  Total chunks stored: {count}")
    print(f"  ChromaDB location: ./chroma_db")
    print(f"\n✅ Demo data is ready for queries!")
    print(f"\nNote: Using local sentence-transformers model (all-MiniLM-L6-v2)")
    print(f"      For production, consider using OpenAI embeddings for better quality.")


if __name__ == "__main__":
    main()
