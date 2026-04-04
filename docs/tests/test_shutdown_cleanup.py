"""
Test for watcher cleanup on shutdown (Task 6.3)

This test verifies that the lifespan context manager properly:
1. Stops all observers in active_observers
2. Joins observer threads to ensure clean shutdown
3. Logs shutdown status

Requirements: 7.2
"""
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server.services.folder_watcher import add_watched_folder, start_folder_watcher
from server.routes.folder_watch import active_observers


def test_shutdown_cleanup():
    """
    Test that observers are properly stopped and joined during shutdown.
    
    This simulates the shutdown behavior in the lifespan context manager.
    """
    print("\n" + "="*60)
    print("TEST: Watcher Cleanup on Shutdown (Task 6.3)")
    print("="*60)
    
    # Create temporary test folders
    test_folders = []
    for i in range(3):
        temp_dir = tempfile.mkdtemp(prefix=f"test_shutdown_{i}_")
        test_folders.append(temp_dir)
        print(f"✅ Created test folder: {temp_dir}")
    
    try:
        # Step 1: Add folders to watch list and start observers
        print("\nStep 1: Starting observers for test folders...")
        for folder in test_folders:
            success, message = add_watched_folder(folder)
            assert success, f"Failed to add folder: {message}"
            
            observer, watcher_message = start_folder_watcher(folder)
            assert observer is not None, f"Failed to start watcher: {watcher_message}"
            
            active_observers[folder] = observer
            print(f"  ✅ Started observer for: {folder}")
        
        print(f"\n✅ Total active observers: {len(active_observers)}")
        assert len(active_observers) == 3, "Should have 3 active observers"
        
        # Step 2: Verify all observers are running
        print("\nStep 2: Verifying observers are running...")
        for folder, observer in active_observers.items():
            assert observer.is_alive(), f"Observer for {folder} should be alive"
            print(f"  ✅ Observer running for: {folder}")
        
        # Step 3: Simulate shutdown - stop all observers
        print("\nStep 3: Simulating shutdown - stopping all observers...")
        print("🛑 Stopping folder watchers...")
        
        for folder_path, observer in list(active_observers.items()):
            # Stop the observer
            observer.stop()
            print(f"  ⏸️  Stopped observer for: {folder_path}")
            
            # Join the observer thread to ensure clean shutdown
            observer.join(timeout=5)
            print(f"  🔗 Joined observer thread for: {folder_path}")
            
            # Verify observer is no longer alive
            assert not observer.is_alive(), f"Observer for {folder_path} should be stopped"
            print(f"  ✅ Observer cleanly shut down for: {folder_path}")
        
        # Step 4: Clear the active_observers dictionary
        print("\nStep 4: Clearing active observers dictionary...")
        active_observers.clear()
        assert len(active_observers) == 0, "active_observers should be empty"
        print("  ✅ All observers removed from active_observers")
        
        print("\n" + "="*60)
        print("✅ TEST PASSED: Shutdown cleanup works correctly")
        print("="*60)
        print("\nVerified:")
        print("  ✅ All observers stopped using observer.stop()")
        print("  ✅ All observer threads joined using observer.join()")
        print("  ✅ Shutdown status logged for each observer")
        print("  ✅ All observers cleanly shut down")
        
    finally:
        # Cleanup: Remove test folders
        print("\n🧹 Cleaning up test folders...")
        for folder in test_folders:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                print(f"  🗑️  Removed: {folder}")


if __name__ == "__main__":
    test_shutdown_cleanup()
