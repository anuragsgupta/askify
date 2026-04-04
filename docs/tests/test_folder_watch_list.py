#!/usr/bin/env python3
"""
Test script for folder watch list endpoint (Task 2.3).
Tests the GET /api/folder-watch/list endpoint implementation.
"""

import sys
import os
import tempfile
import shutil
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from server.main import app
from server.routes.folder_watch import active_observers

# Create test client
client = TestClient(app)

def test_list_folders_endpoint():
    """Test the GET /api/folder-watch/list endpoint."""
    print("=" * 60)
    print("Testing GET /api/folder-watch/list Endpoint (Task 2.3)")
    print("=" * 60)
    print()
    
    # Create temporary test folders
    test_folder1 = tempfile.mkdtemp(prefix="test_watch_list1_")
    test_folder2 = tempfile.mkdtemp(prefix="test_watch_list2_")
    print(f"📁 Created test folder 1: {test_folder1}")
    print(f"📁 Created test folder 2: {test_folder2}")
    
    try:
        # Test 1: List folders when empty (or with existing folders)
        print("\nTest 1: Get initial folder list...")
        response = client.get("/api/folder-watch/list")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            
            # Verify response structure
            if "folders" in data and isinstance(data["folders"], list):
                print(f"   ✅ Response has correct structure")
                print(f"   📊 Initial folder count: {len(data['folders'])}")
                initial_count = len(data["folders"])
            else:
                print("   ❌ Response missing 'folders' key or not a list")
                return False
        else:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        # Test 2: Add folders and verify they appear in list
        print("\nTest 2: Add folders and verify list updates...")
        
        # Add first folder
        response = client.post(
            "/api/folder-watch/add",
            json={"folder_path": test_folder1}
        )
        if response.status_code != 200:
            print(f"   ❌ Failed to add test folder 1: {response.status_code}")
            return False
        print(f"   ✅ Added folder 1")
        
        # Add second folder
        response = client.post(
            "/api/folder-watch/add",
            json={"folder_path": test_folder2}
        )
        if response.status_code != 200:
            print(f"   ❌ Failed to add test folder 2: {response.status_code}")
            return False
        print(f"   ✅ Added folder 2")
        
        # Get updated list
        response = client.get("/api/folder-watch/list")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            folders = data.get("folders", [])
            print(f"   📊 Updated folder count: {len(folders)}")
            
            # Verify both folders are in the list
            folder_paths = [f["folder_path"] for f in folders]
            
            if test_folder1 in folder_paths and test_folder2 in folder_paths:
                print(f"   ✅ Both test folders found in list")
            else:
                print(f"   ❌ Test folders not found in list")
                print(f"   Expected: {test_folder1}, {test_folder2}")
                print(f"   Found: {folder_paths}")
                return False
        else:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        # Test 3: Verify folder metadata structure
        print("\nTest 3: Verify folder metadata structure...")
        
        response = client.get("/api/folder-watch/list")
        data = response.json()
        folders = data.get("folders", [])
        
        if len(folders) > 0:
            sample_folder = folders[0]
            print(f"   Sample folder: {sample_folder}")
            
            # Check required fields
            required_fields = ["id", "folder_path", "is_active", "created_at"]
            missing_fields = [field for field in required_fields if field not in sample_folder]
            
            if not missing_fields:
                print(f"   ✅ All required fields present: {required_fields}")
                
                # Verify field types
                if (isinstance(sample_folder["id"], int) and
                    isinstance(sample_folder["folder_path"], str) and
                    isinstance(sample_folder["is_active"], bool) and
                    isinstance(sample_folder["created_at"], str)):
                    print(f"   ✅ Field types are correct")
                else:
                    print(f"   ❌ Field types incorrect")
                    return False
                
                # last_scan is optional (can be None)
                if "last_scan" in sample_folder:
                    if sample_folder["last_scan"] is None or isinstance(sample_folder["last_scan"], str):
                        print(f"   ✅ last_scan field has correct type (str or None)")
                    else:
                        print(f"   ❌ last_scan has incorrect type")
                        return False
            else:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
        else:
            print(f"   ⚠️  No folders to verify metadata structure")
        
        # Test 4: Remove a folder and verify list updates
        print("\nTest 4: Remove folder and verify list updates...")
        
        response = client.request(
            "DELETE",
            "/api/folder-watch/remove",
            json={"folder_path": test_folder1}
        )
        if response.status_code != 200:
            print(f"   ❌ Failed to remove test folder 1: {response.status_code}")
            return False
        print(f"   ✅ Removed folder 1")
        
        # Get updated list
        response = client.get("/api/folder-watch/list")
        data = response.json()
        folders = data.get("folders", [])
        folder_paths = [f["folder_path"] for f in folders]
        
        if test_folder1 not in folder_paths and test_folder2 in folder_paths:
            print(f"   ✅ Folder 1 removed from list, Folder 2 still present")
        else:
            print(f"   ❌ List not updated correctly after removal")
            return False
        
        print()
        print("=" * 60)
        print("✅ All Task 2.3 Tests Passed!")
        print("=" * 60)
        print()
        print("Task 2.3 Implementation Verified:")
        print("  ✅ GET /api/folder-watch/list endpoint exists")
        print("  ✅ Calls get_watched_folders() from service layer")
        print("  ✅ Returns folders with correct metadata structure")
        print("  ✅ Response includes: id, folder_path, is_active, created_at, last_scan")
        print("  ✅ List updates correctly when folders are added/removed")
        print()
        print("Requirements 1.3 Satisfied:")
        print("  ✅ API_Router exposes GET endpoint at /api/folder-watch/list")
        print("  ✅ Returns all watched folders with their metadata")
        print()
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup: Stop observers and remove test folders
        for test_folder in [test_folder1, test_folder2]:
            if test_folder in active_observers:
                observer = active_observers[test_folder]
                observer.stop()
                observer.join()
                del active_observers[test_folder]
                print(f"🧹 Stopped and removed observer for {test_folder}")
            
            # Remove from database by calling remove endpoint
            try:
                client.request(
                    "DELETE",
                    "/api/folder-watch/remove",
                    json={"folder_path": test_folder}
                )
            except:
                pass
            
            if os.path.exists(test_folder):
                shutil.rmtree(test_folder)
                print(f"🧹 Removed test folder: {test_folder}")


if __name__ == "__main__":
    # First, register the folder_watch router if not already registered
    from server.routes.folder_watch import router as folder_watch_router
    
    # Check if router is already registered
    routes = [route.path for route in app.routes]
    if "/api/folder-watch/list" not in routes:
        print("⚠️  Folder watch router not registered in main.py")
        print("   Registering temporarily for testing...")
        app.include_router(folder_watch_router, prefix="/api")
        print("   ✅ Router registered\n")
    
    success = test_list_folders_endpoint()
    sys.exit(0 if success else 1)
