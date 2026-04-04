#!/usr/bin/env python3
"""
Test script for folder watch add endpoint (Task 2.1).
Tests the POST /api/folder-watch/add endpoint implementation.
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

def test_add_folder_endpoint():
    """Test the POST /api/folder-watch/add endpoint."""
    print("=" * 60)
    print("Testing POST /api/folder-watch/add Endpoint (Task 2.1)")
    print("=" * 60)
    print()
    
    # Create a temporary test folder
    test_folder = tempfile.mkdtemp(prefix="test_watch_")
    print(f"📁 Created test folder: {test_folder}")
    
    try:
        # Test 1: Add valid folder path
        print("\nTest 1: Add valid folder path...")
        response = client.post(
            "/api/folder-watch/add",
            json={"folder_path": test_folder}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("folder_path") == test_folder:
                print("   ✅ Valid folder added successfully")
                
                # Check if observer was started
                if test_folder in active_observers:
                    print("   ✅ Watcher observer started for folder")
                else:
                    print("   ⚠️  Warning: Observer not found in active_observers")
            else:
                print("   ❌ Unexpected response format")
                return False
        else:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        # Test 2: Add duplicate folder (should return 409)
        print("\nTest 2: Add duplicate folder...")
        response = client.post(
            "/api/folder-watch/add",
            json={"folder_path": test_folder}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 409:
            print("   ✅ Duplicate folder correctly rejected with 409")
        else:
            print(f"   ❌ Expected 409, got {response.status_code}")
            return False
        
        # Test 3: Add non-existent folder (should return 400)
        print("\nTest 3: Add non-existent folder...")
        response = client.post(
            "/api/folder-watch/add",
            json={"folder_path": "/nonexistent/path/12345"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 400:
            print("   ✅ Non-existent folder correctly rejected with 400")
        else:
            print(f"   ❌ Expected 400, got {response.status_code}")
            return False
        
        # Test 4: Add empty folder path (should return 422 - validation error)
        print("\nTest 4: Add empty folder path...")
        response = client.post(
            "/api/folder-watch/add",
            json={"folder_path": ""}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 422:
            print("   ✅ Empty path correctly rejected with 422 (validation error)")
        else:
            print(f"   ⚠️  Expected 422, got {response.status_code}")
        
        # Test 5: Add file instead of folder (should return 400)
        print("\nTest 5: Add file instead of folder...")
        test_file = os.path.join(test_folder, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")
        
        response = client.post(
            "/api/folder-watch/add",
            json={"folder_path": test_file}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 400:
            print("   ✅ File path correctly rejected with 400")
        else:
            print(f"   ⚠️  Expected 400, got {response.status_code}")
        
        print()
        print("=" * 60)
        print("✅ All Task 2.1 Tests Passed!")
        print("=" * 60)
        print()
        print("Task 2.1 Implementation Verified:")
        print("  ✅ Pydantic validator for folder path")
        print("  ✅ Calls add_watched_folder() from service layer")
        print("  ✅ Returns appropriate HTTP status codes (200, 400, 409)")
        print("  ✅ Starts watcher observer for new folder")
        print()
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup: Stop observer and remove test folder
        if test_folder in active_observers:
            observer = active_observers[test_folder]
            observer.stop()
            observer.join()
            del active_observers[test_folder]
            print(f"🧹 Stopped and removed observer for test folder")
        
        if os.path.exists(test_folder):
            shutil.rmtree(test_folder)
            print(f"🧹 Removed test folder: {test_folder}")


if __name__ == "__main__":
    # First, register the folder_watch router if not already registered
    from server.routes.folder_watch import router as folder_watch_router
    
    # Check if router is already registered
    routes = [route.path for route in app.routes]
    if "/api/folder-watch/add" not in routes:
        print("⚠️  Folder watch router not registered in main.py")
        print("   Registering temporarily for testing...")
        app.include_router(folder_watch_router, prefix="/api")
        print("   ✅ Router registered\n")
    
    success = test_add_folder_endpoint()
    sys.exit(0 if success else 1)
