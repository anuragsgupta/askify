# Implementation Plan: Folder Watch Auto-Ingest

## Overview

This implementation plan breaks down the folder watch auto-ingest feature into discrete coding tasks. The feature builds on the existing `server/services/folder_watcher.py` service by adding API endpoints, UI components, and background watcher initialization. Each task references specific requirements and builds incrementally toward a complete, working feature.

## Tasks

- [x] 1. Add watchdog dependency and create API router module
  - Add `watchdog` to `server/requirements.txt`
  - Create `server/routes/folder_watch.py` with FastAPI router and Pydantic models
  - Define request/response models: `FolderPath`, `WatchedFolder`, `ScanResult`, `Statistics`
  - _Requirements: 3.1, 3.2_

- [x] 2. Implement folder management API endpoints
  - [x] 2.1 Implement POST /api/folder-watch/add endpoint
    - Validate folder path using Pydantic validator
    - Call `add_watched_folder()` from service layer
    - Return appropriate HTTP status codes (200, 400, 409)
    - Start watcher observer for the new folder
    - _Requirements: 1.1, 1.6, 1.7_
  
  - [x] 2.2 Implement DELETE /api/folder-watch/remove endpoint
    - Call `remove_watched_folder()` from service layer
    - Stop the observer for the removed folder
    - Return appropriate HTTP status codes (200, 404)
    - _Requirements: 1.2, 1.6, 1.7_
  
  - [x] 2.3 Implement GET /api/folder-watch/list endpoint
    - Call `get_watched_folders()` from service layer
    - Format response with folder metadata
    - _Requirements: 1.3_

- [x] 3. Implement scan and statistics API endpoints
  - [x] 3.1 Implement POST /api/folder-watch/scan endpoint
    - Validate folder path exists
    - Call `scan_folder_for_new_files()` from service layer
    - Return scan results with counts (total, ingested, duplicates, errors)
    - _Requirements: 1.4, 1.6, 1.7_
  
  - [x] 3.2 Implement GET /api/folder-watch/statistics endpoint
    - Call `get_file_statistics()` from service layer
    - Format response with total files, duplicates, files by type, and recent ingestions
    - _Requirements: 1.5_

- [x] 4. Register folder watch router in main application
  - Import folder watch router in `server/main.py`
  - Register router with `/api` prefix using `app.include_router()`
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 5. Checkpoint - Test API endpoints
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement background watcher initialization on server startup
  - [x] 6.1 Create lifespan context manager in server/main.py
    - Define `lifespan()` async context manager
    - Create global `active_observers` dictionary to track watchers
    - _Requirements: 7.1, 7.2_
  
  - [x] 6.2 Initialize watchers for active folders on startup
    - Fetch all active watched folders from database
    - Start observer for each active folder using `start_folder_watcher()`
    - Store observers in `active_observers` dictionary
    - Log startup status for each watcher
    - _Requirements: 7.2, 7.3, 7.4, 7.5_
  
  - [x] 6.3 Implement watcher cleanup on shutdown
    - Stop all observers in `active_observers`
    - Join observer threads to ensure clean shutdown
    - Log shutdown status
    - _Requirements: 7.2_

- [x] 7. Implement folder watch UI in Settings page
  - [x] 7.1 Add state management for folder watch
    - Add state variables: `watchedFolders`, `statistics`, `newFolderPath`, `scanning`, `error`
    - Create `useEffect` hook to fetch folders and statistics on mount
    - _Requirements: 4.1, 6.1, 6.5_
  
  - [x] 7.2 Implement folder management functions
    - Create `addFolder()` function that calls POST /api/folder-watch/add
    - Create `removeFolder()` function that calls DELETE /api/folder-watch/remove
    - Create `scanFolder()` function that calls POST /api/folder-watch/scan
    - Create `fetchWatchedFolders()` function that calls GET /api/folder-watch/list
    - Create `fetchStatistics()` function that calls GET /api/folder-watch/statistics
    - Add error handling with user-friendly error messages
    - _Requirements: 4.2, 4.3, 4.4, 4.6, 5.2, 6.5_
  
  - [x] 7.3 Create folder management UI section
    - Add "Folder Watch" glass-panel section below shareable links
    - Add input field for folder path with label
    - Add "Add Folder" button that calls `addFolder()`
    - Display list of watched folders with metadata (path, created date, last scan)
    - Add "Remove" button for each folder that calls `removeFolder()`
    - Add "Scan Now" button for each folder that calls `scanFolder()`
    - Display error messages when operations fail
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.3, 5.4_
  
  - [x] 7.4 Create statistics display UI section
    - Add "Ingestion Statistics" glass-panel section
    - Display total unique files ingested
    - Display total duplicate files detected
    - Display files by type breakdown
    - Display recent ingestions list
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 8. Checkpoint - Test end-to-end functionality
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 9. Write unit tests for API endpoints
  - Test POST /api/folder-watch/add with valid and invalid paths
  - Test POST /api/folder-watch/add with duplicate folder
  - Test DELETE /api/folder-watch/remove with existing and non-existent folders
  - Test GET /api/folder-watch/list returns correct format
  - Test POST /api/folder-watch/scan returns correct result structure
  - Test GET /api/folder-watch/statistics returns correct format
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [ ]* 10. Write integration tests for deduplication
  - Test file ingestion creates hash record
  - Test duplicate file detection increments ingestion_count
  - Test duplicate file updates last_seen timestamp
  - Test statistics endpoint reports correct duplicate count
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ]* 11. Write integration tests for background watchers
  - Test watcher initialization on server startup
  - Test file creation triggers automatic ingestion
  - Test watcher stops when folder is removed
  - Test watchers restart after server restart
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 12. Create feature documentation
  - Document how to add and remove watched folders via UI
  - Document how to manually scan folders
  - Explain deduplication mechanism using SHA-256 hashes
  - List supported file types (.pdf, .txt, .eml, .xlsx, .xls, .csv, .docx, .doc)
  - Provide API endpoint usage examples
  - Explain background watcher management on server startup
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- The existing `server/services/folder_watcher.py` provides all core functionality
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Background watchers use the watchdog library's Observer pattern
- Deduplication uses SHA-256 file hashing with database tracking
