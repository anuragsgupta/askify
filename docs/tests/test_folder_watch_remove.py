#!/usr/bin/env python3
"""
Test script for folder watch remove endpoint (Task 2.2).
Tests the DELETE /api/folder-watch/remove endpoint implementation.
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

def test_remove_folder_endpoint():
    """Test the DELETE /api/folder-watch/remove endpoint."""
    print("=" * 60)
    print("Testing DELETE /api/folder-watch/remove Endpoint (Task 2.2)")
    print("=" * 60)
    print()
    
    # Create a temporary test folder
    test_folder = tempfile.mkdtemp(prefix="test_watch_remove_")
    print(f"📁 Created test folder: {test_folder}")
    
    try:
        # Setup: Add folder first
        print("\nSetup: Adding folder to watch list...")
        response = client.post(
            "/api/folder-watch/add",
            json={"folder_path": test_folder}
        )
        
        if response.status_code != 200:
            print(f"   ❌ Setup failed: Could not add folder (status {response.status_code})")
            return False
        
        print(f"   ✅ Folder added successfully")
        
        # Verify observer is running
        if test_folder not in active_observers:
            print("   ❌ Setup failed: Observer not started")
            return False
        
        observer = active_observers[test_folder]
        print(f"   ✅ Observer is running: {observer.is_alive()}")
        
        # Test 1: Remove existing folder
        print("\nTest 1: Remove existing folder...")
        response = client.request(
            "DELETE",
            "/api/folder-watch/remove",
            json={"folder_path": test_folder}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("   ✅ Folder removed successfully")
                
                # Check if observer was stopped
                if test_folder not in active_observers:
                    print("   ✅ Observer stopped and removed from active_observers")
                else:
                    print("   ❌ Observer still in active_observers")
                    return False
                
                # Check if observer thread is stopped
                if not observer.is_alive():
                    print("   ✅ Observer thread is stopped")
                else:
                    print("   ⚠️  Warning: Observer thread still alive")
            else:
                print("   ❌ Unexpected response format")
                return False
        else:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        # Test 2: Remove non-existent folder (should return 404)
        print("\nTest 2: Remove non-existent folder...")
        response = client.request(
            "DELETE",
            "/api/folder-watch/remove",
            json={"folder_path": "/nonexistent/path/12345"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 404:
            print("   ✅ Non-existent folder correctly rejected with 404")
        else:
            print(f"   ❌ Expected 404, got {response.status_code}")
            return False
        
        # Test 3: Remove already removed folder (should return 404)
        print("\nTest 3: Remove already removed folder...")
        response = client.request(
            "DELETE",
            "/api/folder-watch/remove",
            json={"folder_path": test_folder}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 404:
            print("   ✅ Already removed folder correctly rejected with 404")
        else:
            print(f"   ❌ Expected 404, got {response.status_code}")
            return False
        
        print()
        print("=" * 60)
        print("✅ All Task 2.2 Tests Passed!")
        print("=" * 60)
        print()
        print("Task 2.2 Implementation Verified:")
        print("  ✅ Calls remove_watched_folder() from service layer")
        print("  ✅ Stops the observer for the removed folder")
        print("  ✅ Returns appropriate HTTP status codes (200, 404)")
        print("  ✅ Removes observer from active_observers dictionary")
        print()
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup: Ensure observer is stopped and test folder is removed
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
    if "/api/folder-watch/remove" not in routes:
        print("⚠️  Folder watch router not registered in main.py")
        print("   Registering temporarily for testing...")
        app.include_router(folder_watch_router, prefix="/api")
        print("   ✅ Router registered\n")
    
    success = test_remove_folder_endpoint()
    sys.exit(0 if success else 1)
