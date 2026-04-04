"""
Folder Watch Routes - API endpoints for folder watch management.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional, List
from server.services.folder_watcher import (
    add_watched_folder,
    remove_watched_folder,
    get_watched_folders,
    scan_folder_for_new_files,
    get_file_statistics,
    start_folder_watcher
)

router = APIRouter()

# Global dictionary to track active observers
# This will be imported and used by main.py as well
active_observers = {}


# Request/Response Models

class FolderPath(BaseModel):
    """Request model for folder path operations."""
    folder_path: str
    
    @validator('folder_path')
    def validate_path(cls, v):
        if not v or not v.strip():
            raise ValueError('Folder path cannot be empty')
        return v.strip()


class WatchedFolder(BaseModel):
    """Response model for watched folder information."""
    id: int
    folder_path: str
    is_active: bool
    created_at: str
    last_scan: Optional[str]


class ScanResult(BaseModel):
    """Response model for folder scan results."""
    success: bool
    total_files: int
    ingested: int
    duplicates: int
    errors: int
    message: str


class FileTypeCount(BaseModel):
    """Model for file type statistics."""
    type: str
    count: int


class RecentIngestion(BaseModel):
    """Model for recent ingestion log entry."""
    file_path: str
    status: str
    chunks_created: int
    timestamp: str


class Statistics(BaseModel):
    """Response model for file ingestion statistics."""
    total_files: int
    total_duplicates: int
    files_by_type: List[FileTypeCount]
    recent_ingestions: List[RecentIngestion]


# API Endpoints

@router.post("/folder-watch/add")
async def add_folder(data: FolderPath):
    """
    Add a new folder to the watch list and start watching it.
    
    Returns success status and message.
    """
    success, message = add_watched_folder(data.folder_path)
    
    if not success:
        if "already being watched" in message:
            raise HTTPException(status_code=409, detail=message)
        elif "does not exist" in message or "not a directory" in message:
            raise HTTPException(status_code=400, detail=message)
        else:
            raise HTTPException(status_code=500, detail=message)
    
    # Start watcher observer for the new folder
    observer, watcher_message = start_folder_watcher(data.folder_path)
    if observer:
        active_observers[data.folder_path] = observer
        print(f"✅ Started watcher for: {data.folder_path}")
    else:
        print(f"⚠️  Failed to start watcher: {watcher_message}")
    
    return {
        "success": True,
        "message": message,
        "folder_path": data.folder_path
    }


@router.delete("/folder-watch/remove")
async def remove_folder(data: FolderPath):
    """
    Remove a folder from the watch list and stop its observer.
    
    Returns success status and message.
    """
    success, message = remove_watched_folder(data.folder_path)
    
    if not success:
        raise HTTPException(status_code=404, detail=message)
    
    # Stop the observer for the removed folder
    if data.folder_path in active_observers:
        observer = active_observers[data.folder_path]
        observer.stop()
        observer.join()
        del active_observers[data.folder_path]
        print(f"✅ Stopped watcher for: {data.folder_path}")
    
    return {
        "success": True,
        "message": message
    }


@router.get("/folder-watch/list")
async def list_folders():
    """
    Get all watched folders with metadata.
    
    Returns list of watched folders.
    """
    folders = get_watched_folders()
    
    return {
        "folders": folders
    }


@router.post("/folder-watch/scan")
async def scan_folder(data: FolderPath):
    """
    Manually scan a folder for new files.
    
    Returns scan results including files ingested, duplicates, and errors.
    """
    import os
    
    # Validate folder exists
    if not os.path.exists(data.folder_path):
        raise HTTPException(status_code=400, detail="Folder does not exist")
    
    if not os.path.isdir(data.folder_path):
        raise HTTPException(status_code=400, detail="Path is not a directory")
    
    # Call service layer to scan folder
    total_files, ingested, duplicates, errors = scan_folder_for_new_files(data.folder_path)
    
    message = f"Scanned {total_files} files: {ingested} ingested, {duplicates} duplicates, {errors} errors"
    
    return {
        "success": True,
        "total_files": total_files,
        "ingested": ingested,
        "duplicates": duplicates,
        "errors": errors,
        "message": message
    }


@router.get("/folder-watch/statistics")
async def get_statistics():
    """
    Get file ingestion statistics.
    
    Returns statistics including total files, duplicates, and breakdown by type.
    """
    stats = get_file_statistics()
    
    return stats
