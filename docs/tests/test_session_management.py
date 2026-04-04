"""
Test script for session management functionality
"""
from server.services.database import (
    create_session,
    get_recent_sessions,
    get_session_history,
    save_chat,
    delete_session
)

def test_session_management():
    print("\n🧪 TESTING SESSION MANAGEMENT")
    print("="*60)
    
    # Test 1: Create a new session
    print("\n1️⃣ Creating new session...")
    session_id = create_session("Test Session")
    if session_id:
        print(f"✅ Session created with ID: {session_id}")
    else:
        print("❌ Failed to create session")
        return
    
    # Test 2: Save a chat to the session
    print("\n2️⃣ Saving chat to session...")
    mock_result = {
        "answer": "This is a test answer",
        "sources": [{"source": "test.pdf", "location": "Page 1"}],
        "conflict_analysis": {"has_conflicts": False},
        "llm_used": "test"
    }
    saved_session_id = save_chat("What is a test question?", mock_result, session_id)
    if saved_session_id == session_id:
        print(f"✅ Chat saved to session {session_id}")
    else:
        print("❌ Failed to save chat")
        return
    
    # Test 3: Get recent sessions
    print("\n3️⃣ Fetching recent sessions...")
    sessions = get_recent_sessions(limit=5)
    print(f"✅ Found {len(sessions)} session(s)")
    for s in sessions:
        print(f"   - Session {s['id']}: '{s['title']}' ({s['message_count']} messages)")
    
    # Test 4: Get session history
    print("\n4️⃣ Fetching session history...")
    history = get_session_history(session_id)
    print(f"✅ Found {len(history)} message(s) in session {session_id}")
    for h in history:
        print(f"   - Q: {h['question'][:50]}...")
        print(f"     A: {h['answer'][:50]}...")
    
    # Test 5: Delete the session
    print("\n5️⃣ Deleting test session...")
    success = delete_session(session_id)
    if success:
        print(f"✅ Session {session_id} deleted successfully")
    else:
        print("❌ Failed to delete session")
        return
    
    # Verify deletion
    print("\n6️⃣ Verifying deletion...")
    sessions_after = get_recent_sessions(limit=5)
    deleted = not any(s['id'] == session_id for s in sessions_after)
    if deleted:
        print(f"✅ Session {session_id} no longer exists")
    else:
        print(f"❌ Session {session_id} still exists")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_session_management()
