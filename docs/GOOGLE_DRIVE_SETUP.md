# Google Drive Integration Setup

This guide explains how to set up Google Drive integration for automatic document fetching.

## Prerequisites

- Google Cloud Platform account
- Google Drive with documents to ingest
- Python 3.11+ with project dependencies installed

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

## Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure the OAuth consent screen if prompted:
   - User Type: External (for testing) or Internal (for organization)
   - App name: "SME Knowledge Agent"
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `https://www.googleapis.com/auth/drive.readonly`
4. Create OAuth client ID:
   - Application type: "Desktop app"
   - Name: "SME Knowledge Agent Desktop"
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place it in the project root

## Step 3: Configure Environment

Add your Google Drive folder ID to `.env`:

```bash
# Find your folder ID from the Drive URL:
# https://drive.google.com/drive/folders/FOLDER_ID_HERE
DRIVE_TEST_FOLDER_ID=1ypx6NLgIAUEwmGQ2XPoyX6xZMTnpZKRm
```

## Step 4: First-Time Authentication

Run the authentication flow:

```python
from ingestion.drive_fetcher import authenticate_drive

# This will open a browser window for OAuth consent
creds = authenticate_drive()
```

The first time you run this:
1. A browser window will open
2. Sign in with your Google account
3. Grant permission to access Drive (read-only)
4. The credentials will be saved to `token.json` for future use

## Step 5: Download Documents

```python
from ingestion.drive_fetcher import download_drive_folder

# Download all PDFs and Sheets from a folder
folder_id = "your_folder_id_here"
files = download_drive_folder(folder_id, output_dir="./data")

print(f"Downloaded {len(files)} files:")
for file_path in files:
    print(f"  - {file_path}")
```

## Supported File Types

- **PDFs**: Downloaded directly as `.pdf` files
- **Google Sheets**: Exported as `.xlsx` files with computed formula values
- **Other types**: Skipped (Google Docs, Slides, etc.)

## Finding Folder IDs

Use the utility function to list all accessible folders:

```python
from ingestion.drive_fetcher import list_drive_folders

folders = list_drive_folders()
for folder in folders:
    print(f"{folder['name']}: {folder['id']}")
```

Or extract the folder ID from the Drive URL:
```
https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
                                          ^^^^^^^^^^^^^^^^^^^^
                                          This is the folder ID
```

## Error Handling

### Authentication Timeout
If OAuth flow times out (default: 45 minutes), the system will raise an exception and fall back to manual file upload.

### Folder Not Found
```python
ValueError: Folder not found: folder_id. Please check the folder ID.
```
- Verify the folder ID is correct
- Ensure the folder is shared with your Google account

### Permission Denied
```python
PermissionError: Access denied to folder: folder_id. Please check sharing permissions.
```
- Ensure the folder is shared with your Google account
- Check that you granted Drive read permissions during OAuth

### Rate Limiting
The Drive API has rate limits. If you hit them:
- The system will retry with exponential backoff (up to 3 times)
- Consider reducing the number of files or spreading requests over time

## Security Notes

- `credentials.json` contains your OAuth client credentials (add to `.gitignore`)
- `token.json` contains your access token (add to `.gitignore`)
- Never commit these files to version control
- The system only requests read-only access to Drive

## Testing

Run the integration tests (requires real Drive access):

```bash
# Set up test folder ID
export DRIVE_TEST_FOLDER_ID=your_test_folder_id

# Run integration tests
pytest ingestion/test_drive_fetcher.py -m integration -v
```

Run unit tests (no Drive access required):

```bash
pytest ingestion/test_drive_fetcher.py -v
```

## Troubleshooting

### "credentials.json not found"
- Download OAuth credentials from Google Cloud Console
- Place the file in the project root directory

### "Token has been expired or revoked"
- Delete `token.json`
- Re-run authentication to generate a new token

### "API has not been enabled"
- Go to Google Cloud Console
- Enable the Google Drive API for your project

### Browser doesn't open for OAuth
- Check firewall settings
- Try running on a machine with a GUI browser
- Use the manual OAuth flow if needed

## Manual Fallback

If Drive integration fails, you can always fall back to manual file upload:
1. Download files from Drive manually
2. Place them in the `./data` directory
3. Run the ingestion pipeline directly on local files

The system is designed to work with or without Drive integration.
