# Requirements Document

## Introduction

The Folder Watch Auto-Ingest feature enables users to monitor filesystem folders for new documents and automatically ingest them into the Askify RAG system with hash-based deduplication. This feature completes the existing backend service implementation by adding API endpoints, UI components, and background watcher management.

## Glossary

- **Folder_Watcher_Service**: The backend service that monitors folders and ingests files (already implemented in `server/services/folder_watcher.py`)
- **API_Router**: FastAPI router that exposes folder watch endpoints
- **Settings_UI**: React component in Settings page that provides folder watch management interface
- **Background_Watcher**: Observer process that monitors folders for file system events
- **File_Hash**: SHA-256 hash used for deduplication
- **Watched_Folder**: A folder path registered in the system for monitoring
- **Ingestion**: The process of parsing, embedding, and storing a document in the vector database

## Requirements

### Requirement 1: API Endpoints

**User Story:** As a developer, I want REST API endpoints for folder watch operations, so that the UI can manage watched folders and view statistics.

#### Acceptance Criteria

1. THE API_Router SHALL expose a POST endpoint at `/api/folder-watch/add` that accepts a folder path and returns success status
2. THE API_Router SHALL expose a DELETE endpoint at `/api/folder-watch/remove` that accepts a folder path and returns success status
3. THE API_Router SHALL expose a GET endpoint at `/api/folder-watch/list` that returns all watched folders with their metadata
4. THE API_Router SHALL expose a POST endpoint at `/api/folder-watch/scan` that accepts a folder path and returns scan results
5. THE API_Router SHALL expose a GET endpoint at `/api/folder-watch/statistics` that returns file ingestion statistics
6. WHEN an API endpoint receives an invalid folder path, THE API_Router SHALL return an HTTP 400 error with a descriptive message
7. WHEN an API operation fails, THE API_Router SHALL return an appropriate HTTP error code with error details

### Requirement 2: API Router Registration

**User Story:** As a system administrator, I want the folder watch router registered in the main application, so that the endpoints are accessible.

#### Acceptance Criteria

1. THE Main_Application SHALL import the folder watch router module
2. THE Main_Application SHALL register the folder watch router with the `/api` prefix
3. WHEN the server starts, THE Main_Application SHALL make folder watch endpoints available

### Requirement 3: Dependency Management

**User Story:** As a developer, I want the watchdog library included in requirements, so that the folder watcher service can function.

#### Acceptance Criteria

1. THE Requirements_File SHALL include the `watchdog` library
2. WHEN dependencies are installed, THE Requirements_File SHALL ensure watchdog is available for import

### Requirement 4: Folder Management UI

**User Story:** As a user, I want to add and remove watched folders through the Settings page, so that I can control which folders are monitored.

#### Acceptance Criteria

1. THE Settings_UI SHALL display an input field for entering folder paths
2. THE Settings_UI SHALL display an "Add Folder" button that calls the add endpoint
3. THE Settings_UI SHALL display a list of currently watched folders
4. THE Settings_UI SHALL display a "Remove" button for each watched folder that calls the remove endpoint
5. WHEN a folder is added successfully, THE Settings_UI SHALL refresh the folder list
6. WHEN a folder operation fails, THE Settings_UI SHALL display an error message to the user
7. THE Settings_UI SHALL display each folder's creation date and last scan timestamp

### Requirement 5: Manual Folder Scanning

**User Story:** As a user, I want to manually trigger a folder scan, so that I can immediately ingest existing files without waiting for new file events.

#### Acceptance Criteria

1. THE Settings_UI SHALL display a "Scan Now" button for each watched folder
2. WHEN the scan button is clicked, THE Settings_UI SHALL call the scan endpoint and display progress
3. WHEN a scan completes, THE Settings_UI SHALL display scan results including files ingested, duplicates detected, and errors
4. THE Settings_UI SHALL update the folder's last scan timestamp after a successful scan

### Requirement 6: Statistics Display

**User Story:** As a user, I want to view file ingestion statistics, so that I can monitor the system's deduplication effectiveness.

#### Acceptance Criteria

1. THE Settings_UI SHALL display total unique files ingested
2. THE Settings_UI SHALL display total duplicate files detected
3. THE Settings_UI SHALL display a breakdown of files by type
4. WHEN the Settings page loads, THE Settings_UI SHALL fetch and display current statistics
5. THE Settings_UI SHALL refresh statistics after folder operations complete

### Requirement 7: Background Watcher Management

**User Story:** As a system administrator, I want watchers to start automatically for active folders on server startup, so that monitoring continues after restarts.

#### Acceptance Criteria

1. WHEN the server starts, THE Main_Application SHALL retrieve all active watched folders from the database
2. FOR ALL active watched folders, THE Main_Application SHALL start a Background_Watcher
3. THE Background_Watcher SHALL monitor the folder for file creation events
4. WHEN a new file is created in a watched folder, THE Background_Watcher SHALL automatically ingest the file
5. THE Background_Watcher SHALL use the existing Folder_Watcher_Service deduplication logic

### Requirement 8: Deduplication Verification

**User Story:** As a quality assurance tester, I want to verify that duplicate files are properly detected, so that I can confirm the deduplication feature works correctly.

#### Acceptance Criteria

1. WHEN a file with an existing File_Hash is ingested, THE Folder_Watcher_Service SHALL skip ingestion and log it as a duplicate
2. WHEN a duplicate is detected, THE Folder_Watcher_Service SHALL increment the ingestion_count in the database
3. WHEN a duplicate is detected, THE Folder_Watcher_Service SHALL update the last_seen timestamp
4. THE Statistics endpoint SHALL accurately report the count of duplicate files detected

### Requirement 9: Feature Documentation

**User Story:** As a developer or user, I want documentation for the folder watch feature, so that I understand how to use and maintain it.

#### Acceptance Criteria

1. THE Documentation SHALL describe how to add and remove watched folders
2. THE Documentation SHALL explain the deduplication mechanism using File_Hash
3. THE Documentation SHALL list supported file types
4. THE Documentation SHALL provide examples of API endpoint usage
5. THE Documentation SHALL explain how background watchers are managed on server startup
