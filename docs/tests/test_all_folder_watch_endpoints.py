#!/usr/bin/env python3
"""
Comprehensive test suite for all folder watch API endpoints.
Runs all endpoint tests and provides a summary report.
"""

import sys
import subprocess

def run_test(test_file, test_name):
    """Run a single test file and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            ["python3", test_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ Test timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False


def main():
    """Run all folder watch endpoint tests."""
    print("\n" + "="*60)
    print("FOLDER WATCH API ENDPOINTS - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    tests = [
        ("test_folder_watch_endpoint.py", "POST /api/folder-watch/add"),
        ("test_folder_watch_remove.py", "DELETE /api/folder-watch/remove"),
        ("test_folder_watch_list.py", "GET /api/folder-watch/list"),
        ("test_folder_watch_scan.py", "POST /api/folder-watch/scan"),
        ("test_folder_watch_statistics.py", "GET /api/folder-watch/statistics"),
    ]
    
    results = {}
    
    for test_file, test_name in tests:
        success = run_test(test_file, test_name)
        results[test_name] = success
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All API endpoint tests passed successfully!")
        print("\nVerified Endpoints:")
        print("  ✅ POST   /api/folder-watch/add")
        print("  ✅ DELETE /api/folder-watch/remove")
        print("  ✅ GET    /api/folder-watch/list")
        print("  ✅ POST   /api/folder-watch/scan")
        print("  ✅ GET    /api/folder-watch/statistics")
        print("\nAll requirements validated:")
        print("  ✅ Requirement 1.1: Add folder endpoint")
        print("  ✅ Requirement 1.2: Remove folder endpoint")
        print("  ✅ Requirement 1.3: List folders endpoint")
        print("  ✅ Requirement 1.4: Scan folder endpoint")
        print("  ✅ Requirement 1.5: Statistics endpoint")
        print("  ✅ Requirement 1.6: Invalid path error handling")
        print("  ✅ Requirement 1.7: Appropriate error codes")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
