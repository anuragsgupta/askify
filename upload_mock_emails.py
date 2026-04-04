#!/usr/bin/env python3
"""
Script to upload mock emails to the Askify RAG system.
This will parse and embed all email files in the mock_emails directory.
"""

import os
import requests
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api"
MOCK_EMAILS_DIR = "mock_emails"

def upload_email(file_path):
    """Upload a single email file to the system."""
    filename = os.path.basename(file_path)
    
    print(f"\n{'='*60}")
    print(f"📧 Uploading: {filename}")
    print(f"{'='*60}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'message/rfc822')}
            
            response = requests.post(
                f"{API_BASE_URL}/upload",
                files=files,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: {data.get('message', 'Upload successful')}")
                print(f"   Document ID: {data.get('doc_id')}")
                print(f"   Chunks created: {data.get('chunks_created')}")
                print(f"   Provider: {data.get('embedding_provider', 'unknown')}")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                print(f"❌ FAILED: {response.status_code}")
                print(f"   Error: {error_data.get('detail', response.text)}")
                return False
                
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to backend at {API_BASE_URL}")
        print(f"   Make sure the backend is running: ./start_backend.sh")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def get_documents():
    """Get list of all documents in the system."""
    try:
        response = requests.get(f"{API_BASE_URL}/documents", timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('documents', [])
        return []
    except:
        return []

def main():
    """Main function to upload all mock emails."""
    print("\n" + "="*60)
    print("📧 MOCK EMAIL UPLOAD SCRIPT")
    print("="*60)
    print(f"Backend URL: {API_BASE_URL}")
    print(f"Email directory: {MOCK_EMAILS_DIR}")
    print("="*60)
    
    # Check if mock_emails directory exists
    if not os.path.exists(MOCK_EMAILS_DIR):
        print(f"\n❌ ERROR: Directory '{MOCK_EMAILS_DIR}' not found!")
        print(f"   Please create the directory and add email files.")
        return
    
    # Get list of email files
    email_files = sorted([
        os.path.join(MOCK_EMAILS_DIR, f) 
        for f in os.listdir(MOCK_EMAILS_DIR) 
        if f.endswith('.eml')
    ])
    
    if not email_files:
        print(f"\n❌ ERROR: No .eml files found in '{MOCK_EMAILS_DIR}'")
        return
    
    print(f"\n📊 Found {len(email_files)} email files to upload")
    print("\nFiles:")
    for i, file_path in enumerate(email_files, 1):
        print(f"   {i}. {os.path.basename(file_path)}")
    
    # Check backend connectivity
    print(f"\n🔍 Checking backend connectivity...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend is running")
        else:
            print(f"⚠️  Backend responded with status {response.status_code}")
    except:
        print(f"❌ Cannot connect to backend at {API_BASE_URL}")
        print(f"   Please start the backend: ./start_backend.sh")
        return
    
    # Get current documents
    print(f"\n📋 Checking existing documents...")
    existing_docs = get_documents()
    print(f"   Current documents in system: {len(existing_docs)}")
    
    # Upload each email
    print(f"\n🚀 Starting upload process...")
    print(f"{'='*60}\n")
    
    successful = 0
    failed = 0
    
    for i, file_path in enumerate(email_files, 1):
        print(f"\n[{i}/{len(email_files)}]")
        
        if upload_email(file_path):
            successful += 1
        else:
            failed += 1
        
        # Small delay between uploads
        if i < len(email_files):
            time.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 UPLOAD SUMMARY")
    print(f"{'='*60}")
    print(f"Total files: {len(email_files)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"{'='*60}")
    
    # Get updated document count
    print(f"\n📋 Fetching updated document list...")
    updated_docs = get_documents()
    print(f"   Total documents in system: {len(updated_docs)}")
    print(f"   Total chunks: {sum(doc.get('chunk_count', 0) for doc in updated_docs)}")
    
    if successful > 0:
        print(f"\n✅ SUCCESS! {successful} email(s) have been embedded into the system.")
        print(f"\n💡 You can now query these emails in the Chat page!")
        print(f"\nExample queries:")
        print(f"   - What is the status of Project Alpha?")
        print(f"   - Tell me about the remote work policy")
        print(f"   - What security threats were reported?")
        print(f"   - What training opportunities are available?")
        print(f"   - Summarize the sales proposal for BigClient")
    
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    main()
