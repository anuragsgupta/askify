"""
Google Drive integration for automatic document fetching.

This module provides OAuth 2.0 authentication and file download capabilities
for fetching PDFs and Google Sheets from a specified Drive folder.
"""

import os
import io
from typing import List, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError


# OAuth 2.0 scopes required for Drive access
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Token file for storing OAuth credentials
TOKEN_FILE = 'token.json'


def authenticate_drive(credentials_file: str = 'credentials.json') -> Credentials:
    """
    Authenticate with Google Drive using OAuth 2.0.
    
    Args:
        credentials_file: Path to OAuth 2.0 client credentials JSON file
        
    Returns:
        Authenticated credentials object
        
    Raises:
        FileNotFoundError: If credentials file doesn't exist
        Exception: If authentication fails
    """
    creds = None
    
    # Check if we have stored credentials
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If credentials are invalid or don't exist, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                # If refresh fails, re-authenticate
                print(f"Token refresh failed: {e}. Re-authenticating...")
                creds = None
        
        if not creds:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"Credentials file '{credentials_file}' not found. "
                    "Please download OAuth 2.0 credentials from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds


def download_drive_folder(
    folder_id: str,
    output_dir: str = './data',
    credentials_file: str = 'credentials.json',
    timeout_seconds: int = 2700  # 45 minutes
) -> List[str]:
    """
    Download all PDFs and export Google Sheets from a Drive folder.
    
    Args:
        folder_id: Google Drive folder ID (from folder URL)
        output_dir: Local directory to save downloaded files
        credentials_file: Path to OAuth 2.0 credentials JSON
        timeout_seconds: Maximum time to wait for authentication (default: 45 min)
        
    Returns:
        List of local file paths for downloaded documents
        
    Raises:
        TimeoutError: If OAuth flow exceeds timeout
        HttpError: If Drive API request fails
        Exception: For other authentication or download errors
    """
    downloaded_files = []
    
    try:
        # Authenticate with Drive API
        creds = authenticate_drive(credentials_file)
        service = build('drive', 'v3', credentials=creds)
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # List all files in the specified folder
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType)",
            pageSize=1000
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print(f"No files found in folder {folder_id}")
            return downloaded_files
        
        print(f"Found {len(files)} files in Drive folder")
        
        for file in files:
            file_id = file['id']
            file_name = file['name']
            mime_type = file['mimeType']
            
            try:
                # Handle PDFs
                if mime_type == 'application/pdf':
                    local_path = _download_pdf(service, file_id, file_name, output_dir)
                    downloaded_files.append(local_path)
                    print(f"Downloaded PDF: {file_name}")
                
                # Handle Google Sheets - export as Excel
                elif mime_type == 'application/vnd.google-apps.spreadsheet':
                    local_path = _export_sheet_as_xlsx(service, file_id, file_name, output_dir)
                    downloaded_files.append(local_path)
                    print(f"Exported Google Sheet: {file_name}")
                
                else:
                    print(f"Skipping unsupported file type: {file_name} ({mime_type})")
            
            except HttpError as e:
                print(f"Error downloading {file_name}: {e}")
                continue
        
        print(f"Successfully downloaded {len(downloaded_files)} files")
        return downloaded_files
    
    except FileNotFoundError as e:
        print(f"Authentication error: {e}")
        print("Falling back to manual file upload")
        raise
    
    except HttpError as e:
        if e.resp.status == 404:
            raise ValueError(f"Folder not found: {folder_id}. Please check the folder ID.")
        elif e.resp.status == 403:
            raise PermissionError(f"Access denied to folder: {folder_id}. Please check sharing permissions.")
        else:
            raise
    
    except Exception as e:
        print(f"Unexpected error during Drive sync: {e}")
        print("Falling back to manual file upload")
        raise


def _download_pdf(
    service,
    file_id: str,
    file_name: str,
    output_dir: str
) -> str:
    """
    Download a PDF file from Google Drive.
    
    Args:
        service: Authenticated Drive API service
        file_id: Google Drive file ID
        file_name: Original filename
        output_dir: Local directory to save file
        
    Returns:
        Local file path
    """
    request = service.files().get_media(fileId=file_id)
    
    # Ensure filename ends with .pdf
    if not file_name.lower().endswith('.pdf'):
        file_name = f"{file_name}.pdf"
    
    local_path = os.path.join(output_dir, file_name)
    
    with io.FileIO(local_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
    
    return local_path


def _export_sheet_as_xlsx(
    service,
    file_id: str,
    file_name: str,
    output_dir: str
) -> str:
    """
    Export a Google Sheet as Excel (.xlsx) file.
    
    Args:
        service: Authenticated Drive API service
        file_id: Google Drive file ID
        file_name: Original filename
        output_dir: Local directory to save file
        
    Returns:
        Local file path
    """
    # Export as Excel format
    request = service.files().export_media(
        fileId=file_id,
        mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Ensure filename ends with .xlsx
    if not file_name.lower().endswith('.xlsx'):
        file_name = f"{file_name}.xlsx"
    
    local_path = os.path.join(output_dir, file_name)
    
    with io.FileIO(local_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
    
    return local_path


def list_drive_folders(credentials_file: str = 'credentials.json') -> List[dict]:
    """
    List all folders accessible to the authenticated user.
    
    Utility function for discovering folder IDs.
    
    Args:
        credentials_file: Path to OAuth 2.0 credentials JSON
        
    Returns:
        List of dicts with 'id' and 'name' keys
    """
    creds = authenticate_drive(credentials_file)
    service = build('drive', 'v3', credentials=creds)
    
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query,
        fields="files(id, name)",
        pageSize=100
    ).execute()
    
    folders = results.get('files', [])
    return [{'id': f['id'], 'name': f['name']} for f in folders]
