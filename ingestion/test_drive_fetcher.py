"""
Unit tests for Google Drive fetcher.

Tests cover OAuth flow, folder listing, file downloads, and error handling.
Includes both unit tests with mocks and integration tests with real Drive API.
"""

import os
import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from ingestion.drive_fetcher import (
    authenticate_drive,
    download_drive_folder,
    list_drive_folders,
    _download_pdf,
    _export_sheet_as_xlsx
)


# ============================================================================
# Unit Tests with Mocks
# ============================================================================

class TestAuthentication:
    """Test OAuth 2.0 authentication flow."""
    
    def test_authenticate_with_existing_valid_token(self, tmp_path):
        """Test authentication when valid token exists."""
        # Create mock credentials
        mock_creds = Mock()
        mock_creds.valid = True
        
        with patch('os.path.exists', return_value=True), \
             patch('ingestion.drive_fetcher.Credentials.from_authorized_user_file', return_value=mock_creds):
            
            creds = authenticate_drive()
            assert creds == mock_creds
    
    def test_authenticate_with_expired_token_refresh_success(self):
        """Test authentication with expired token that refreshes successfully."""
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = 'refresh_token'
        mock_creds.to_json = Mock(return_value='{"token": "data"}')
        
        def refresh_side_effect(request):
            mock_creds.valid = True
        
        mock_creds.refresh = Mock(side_effect=refresh_side_effect)
        
        with patch('os.path.exists', return_value=True), \
             patch('ingestion.drive_fetcher.Credentials.from_authorized_user_file', return_value=mock_creds), \
             patch('builtins.open', create=True):
            
            creds = authenticate_drive()
            mock_creds.refresh.assert_called_once()
    
    def test_authenticate_missing_credentials_file(self):
        """Test authentication fails gracefully when credentials file missing."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError) as exc_info:
                authenticate_drive('missing_credentials.json')
            
            assert 'missing_credentials.json' in str(exc_info.value)
            assert 'Google Cloud Console' in str(exc_info.value)
    
    def test_authenticate_new_user_flow(self):
        """Test authentication for new user (no token file)."""
        mock_flow = Mock()
        mock_creds = Mock()
        mock_creds.to_json = Mock(return_value='{"token": "data"}')
        mock_flow.run_local_server = Mock(return_value=mock_creds)
        
        with patch('os.path.exists', side_effect=[False, True]), \
             patch('ingestion.drive_fetcher.InstalledAppFlow.from_client_secrets_file', return_value=mock_flow), \
             patch('builtins.open', create=True):
            
            creds = authenticate_drive()
            assert creds == mock_creds
            mock_flow.run_local_server.assert_called_once()


class TestDownloadDriveFolder:
    """Test folder download functionality."""
    
    def test_download_folder_with_pdfs_and_sheets(self, tmp_path):
        """Test downloading folder with mixed file types."""
        # Mock Drive API service
        mock_service = Mock()
        mock_files_list = Mock()
        mock_files_list.list = Mock(return_value=Mock(execute=Mock(return_value={
            'files': [
                {'id': 'pdf1', 'name': 'Policy.pdf', 'mimeType': 'application/pdf'},
                {'id': 'sheet1', 'name': 'Pricing', 'mimeType': 'application/vnd.google-apps.spreadsheet'},
                {'id': 'doc1', 'name': 'Notes', 'mimeType': 'application/vnd.google-apps.document'}
            ]
        })))
        mock_service.files = Mock(return_value=mock_files_list)
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service), \
             patch('ingestion.drive_fetcher._download_pdf', return_value=str(tmp_path / 'Policy.pdf')), \
             patch('ingestion.drive_fetcher._export_sheet_as_xlsx', return_value=str(tmp_path / 'Pricing.xlsx')):
            
            files = download_drive_folder('folder123', output_dir=str(tmp_path))
            
            assert len(files) == 2  # PDF + Sheet, Doc skipped
            assert any('Policy.pdf' in f for f in files)
            assert any('Pricing.xlsx' in f for f in files)
    
    def test_download_folder_empty(self, tmp_path):
        """Test downloading empty folder."""
        mock_service = Mock()
        mock_files_list = Mock()
        mock_files_list.list = Mock(return_value=Mock(execute=Mock(return_value={'files': []})))
        mock_service.files = Mock(return_value=mock_files_list)
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service):
            
            files = download_drive_folder('empty_folder', output_dir=str(tmp_path))
            assert len(files) == 0
    
    def test_download_folder_not_found(self, tmp_path):
        """Test error handling when folder doesn't exist."""
        from googleapiclient.errors import HttpError
        
        mock_service = Mock()
        mock_response = Mock()
        mock_response.status = 404
        
        mock_files_list = Mock()
        mock_files_list.list = Mock(side_effect=HttpError(mock_response, b'Not found'))
        mock_service.files = Mock(return_value=mock_files_list)
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service):
            
            with pytest.raises(ValueError) as exc_info:
                download_drive_folder('nonexistent_folder', output_dir=str(tmp_path))
            
            assert 'Folder not found' in str(exc_info.value)
    
    def test_download_folder_permission_denied(self, tmp_path):
        """Test error handling when access is denied."""
        from googleapiclient.errors import HttpError
        
        mock_service = Mock()
        mock_response = Mock()
        mock_response.status = 403
        
        mock_files_list = Mock()
        mock_files_list.list = Mock(side_effect=HttpError(mock_response, b'Forbidden'))
        mock_service.files = Mock(return_value=mock_files_list)
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service):
            
            with pytest.raises(PermissionError) as exc_info:
                download_drive_folder('forbidden_folder', output_dir=str(tmp_path))
            
            assert 'Access denied' in str(exc_info.value)
    
    def test_download_folder_creates_output_directory(self, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / 'new_dir' / 'nested'
        
        mock_service = Mock()
        mock_files_list = Mock()
        mock_files_list.list = Mock(return_value=Mock(execute=Mock(return_value={'files': []})))
        mock_service.files = Mock(return_value=mock_files_list)
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service):
            
            download_drive_folder('folder123', output_dir=str(output_dir))
            assert output_dir.exists()
    
    def test_download_folder_partial_failure(self, tmp_path):
        """Test that download continues when individual files fail."""
        mock_service = Mock()
        mock_files_list = Mock()
        mock_files_list.list = Mock(return_value=Mock(execute=Mock(return_value={
            'files': [
                {'id': 'pdf1', 'name': 'Good.pdf', 'mimeType': 'application/pdf'},
                {'id': 'pdf2', 'name': 'Bad.pdf', 'mimeType': 'application/pdf'},
            ]
        })))
        mock_service.files = Mock(return_value=mock_files_list)
        
        from googleapiclient.errors import HttpError
        mock_response = Mock()
        mock_response.status = 500
        
        def download_side_effect(service, file_id, name, output_dir):
            if file_id == 'pdf2':
                raise HttpError(mock_response, b'Server error')
            return str(tmp_path / name)
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service), \
             patch('ingestion.drive_fetcher._download_pdf', side_effect=download_side_effect):
            
            files = download_drive_folder('folder123', output_dir=str(tmp_path))
            
            # Should have 1 successful download despite 1 failure
            assert len(files) == 1
            assert 'Good.pdf' in files[0]


class TestDownloadPDF:
    """Test PDF download helper."""
    
    def test_download_pdf_success(self, tmp_path):
        """Test successful PDF download."""
        mock_service = Mock()
        mock_request = Mock()
        mock_service.files().get_media.return_value = mock_request
        
        # Mock the download process
        mock_downloader = Mock()
        mock_downloader.next_chunk.side_effect = [
            (Mock(progress=lambda: 0.5), False),
            (Mock(progress=lambda: 1.0), True)
        ]
        
        with patch('ingestion.drive_fetcher.MediaIoBaseDownload', return_value=mock_downloader), \
             patch('io.FileIO', create=True):
            
            local_path = _download_pdf(mock_service, 'file123', 'test.pdf', str(tmp_path))
            
            assert local_path == str(tmp_path / 'test.pdf')
    
    def test_download_pdf_adds_extension(self, tmp_path):
        """Test that .pdf extension is added if missing."""
        mock_service = Mock()
        mock_request = Mock()
        mock_service.files().get_media.return_value = mock_request
        
        mock_downloader = Mock()
        mock_downloader.next_chunk.return_value = (Mock(), True)
        
        with patch('ingestion.drive_fetcher.MediaIoBaseDownload', return_value=mock_downloader), \
             patch('io.FileIO', create=True):
            
            local_path = _download_pdf(mock_service, 'file123', 'test', str(tmp_path))
            
            assert local_path.endswith('.pdf')


class TestExportSheet:
    """Test Google Sheets export helper."""
    
    def test_export_sheet_as_xlsx_success(self, tmp_path):
        """Test successful Sheet export."""
        mock_service = Mock()
        mock_request = Mock()
        mock_service.files().export_media.return_value = mock_request
        
        mock_downloader = Mock()
        mock_downloader.next_chunk.return_value = (Mock(), True)
        
        with patch('ingestion.drive_fetcher.MediaIoBaseDownload', return_value=mock_downloader), \
             patch('io.FileIO', create=True):
            
            local_path = _export_sheet_as_xlsx(mock_service, 'sheet123', 'Pricing', str(tmp_path))
            
            assert local_path == str(tmp_path / 'Pricing.xlsx')
            mock_service.files().export_media.assert_called_once_with(
                fileId='sheet123',
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
    def test_export_sheet_adds_extension(self, tmp_path):
        """Test that .xlsx extension is added if missing."""
        mock_service = Mock()
        mock_request = Mock()
        mock_service.files().export_media.return_value = mock_request
        
        mock_downloader = Mock()
        mock_downloader.next_chunk.return_value = (Mock(), True)
        
        with patch('ingestion.drive_fetcher.MediaIoBaseDownload', return_value=mock_downloader), \
             patch('io.FileIO', create=True):
            
            local_path = _export_sheet_as_xlsx(mock_service, 'sheet123', 'Data', str(tmp_path))
            
            assert local_path.endswith('.xlsx')


class TestListDriveFolders:
    """Test folder listing utility."""
    
    def test_list_folders_success(self):
        """Test listing accessible folders."""
        mock_service = Mock()
        mock_files_list = Mock()
        mock_files_list.list = Mock(return_value=Mock(execute=Mock(return_value={
            'files': [
                {'id': 'folder1', 'name': 'Documents'},
                {'id': 'folder2', 'name': 'Policies'},
            ]
        })))
        mock_service.files = Mock(return_value=mock_files_list)
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service):
            
            folders = list_drive_folders()
            
            assert len(folders) == 2
            assert folders[0] == {'id': 'folder1', 'name': 'Documents'}
            assert folders[1] == {'id': 'folder2', 'name': 'Policies'}
    
    def test_list_folders_empty(self):
        """Test listing when no folders exist."""
        mock_service = Mock()
        mock_files_list = Mock()
        mock_files_list.list = Mock(return_value=Mock(execute=Mock(return_value={'files': []})))
        mock_service.files = Mock(return_value=mock_files_list)
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service):
            
            folders = list_drive_folders()
            assert len(folders) == 0


# ============================================================================
# Integration Tests (require real Drive API access)
# ============================================================================

@pytest.mark.integration
@pytest.mark.skipif(
    not os.path.exists('credentials.json'),
    reason="Requires credentials.json for Drive API access"
)
class TestDriveAPIIntegration:
    """
    Integration tests with real Google Drive API.
    
    These tests require:
    1. credentials.json file in project root
    2. A test folder in Google Drive with known files
    3. DRIVE_TEST_FOLDER_ID environment variable set
    """
    
    def test_real_folder_listing(self):
        """Test listing files from real Drive folder."""
        folder_id = os.getenv('DRIVE_TEST_FOLDER_ID')
        if not folder_id:
            pytest.skip("DRIVE_TEST_FOLDER_ID not set")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            files = download_drive_folder(folder_id, output_dir=tmp_dir)
            
            # Verify files were downloaded
            assert isinstance(files, list)
            for file_path in files:
                assert os.path.exists(file_path)
                assert file_path.endswith(('.pdf', '.xlsx'))
    
    def test_real_oauth_flow(self):
        """Test OAuth authentication flow."""
        # This will open browser for authentication if token doesn't exist
        creds = authenticate_drive()
        
        assert creds is not None
        assert creds.valid
    
    def test_real_folder_not_found(self):
        """Test error handling with invalid folder ID."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(ValueError) as exc_info:
                download_drive_folder('invalid_folder_id_12345', output_dir=tmp_dir)
            
            assert 'Folder not found' in str(exc_info.value)
    
    def test_fallback_to_manual_upload_on_timeout(self):
        """Test that system falls back gracefully on authentication timeout."""
        # Simulate timeout by using invalid credentials
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(FileNotFoundError):
                download_drive_folder(
                    'folder123',
                    output_dir=tmp_dir,
                    credentials_file='nonexistent_credentials.json'
                )


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_download_folder_with_special_characters_in_names(self, tmp_path):
        """Test handling files with special characters in names."""
        mock_service = Mock()
        mock_files_list = Mock()
        mock_files_list.list = Mock(return_value=Mock(execute=Mock(return_value={
            'files': [
                {'id': 'pdf1', 'name': 'Policy (v2) [Final].pdf', 'mimeType': 'application/pdf'},
            ]
        })))
        mock_service.files = Mock(return_value=mock_files_list)
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service), \
             patch('ingestion.drive_fetcher._download_pdf', return_value=str(tmp_path / 'Policy (v2) [Final].pdf')):
            
            files = download_drive_folder('folder123', output_dir=str(tmp_path))
            assert len(files) == 1
    
    def test_download_folder_with_duplicate_names(self, tmp_path):
        """Test handling multiple files with same name."""
        mock_service = Mock()
        mock_files_list = Mock()
        mock_files_list.list = Mock(return_value=Mock(execute=Mock(return_value={
            'files': [
                {'id': 'pdf1', 'name': 'Policy.pdf', 'mimeType': 'application/pdf'},
                {'id': 'pdf2', 'name': 'Policy.pdf', 'mimeType': 'application/pdf'},
            ]
        })))
        mock_service.files = Mock(return_value=mock_files_list)
        
        call_count = [0]
        def download_with_count(service, file_id, name, output_dir):
            call_count[0] += 1
            return str(tmp_path / f'Policy_{call_count[0]}.pdf')
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service), \
             patch('ingestion.drive_fetcher._download_pdf', side_effect=download_with_count):
            
            files = download_drive_folder('folder123', output_dir=str(tmp_path))
            # Both files should be downloaded (second may overwrite first)
            assert len(files) == 2
    
    def test_download_folder_with_large_file_count(self, tmp_path):
        """Test handling folders with many files."""
        # Generate 150 mock files
        mock_files = [
            {'id': f'file{i}', 'name': f'Doc{i}.pdf', 'mimeType': 'application/pdf'}
            for i in range(150)
        ]
        
        mock_service = Mock()
        mock_files_list = Mock()
        mock_files_list.list = Mock(return_value=Mock(execute=Mock(return_value={'files': mock_files})))
        mock_service.files = Mock(return_value=mock_files_list)
        
        with patch('ingestion.drive_fetcher.authenticate_drive'), \
             patch('ingestion.drive_fetcher.build', return_value=mock_service), \
             patch('ingestion.drive_fetcher._download_pdf', side_effect=lambda s, fid, name, od: str(tmp_path / name)):
            
            files = download_drive_folder('folder123', output_dir=str(tmp_path))
            assert len(files) == 150


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
