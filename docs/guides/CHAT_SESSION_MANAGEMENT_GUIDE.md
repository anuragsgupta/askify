# Chat Session Management Guide

## Overview

The chat interface now supports session management, allowing users to:
- Create new chat sessions
- View recent chat sessions
- Switch between sessions
- Delete old sessions
- Automatically save conversations to sessions

## Features

### 1. New Chat Session

Click the **"+"** button in the chat header to create a new chat session. This will:
- Clear the current conversation
- Create a new session in the database
- Start fresh with an empty chat

### 2. Recent Sessions

Click the **message icon** button in the chat header to view recent sessions. This shows:
- Session title (first question from the session)
- Number of messages in the session
- Last updated date
- Delete button for each session

### 3. Session Switching

Click on any session in the recent sessions list to:
- Load all messages from that session
- Restore the last response in the right sidebar
- Continue the conversation in that session

### 4. Session Deletion

Click the trash icon next to any session to delete it. This will:
- Delete the session and all its messages
- Clear the current chat if you're viewing that session
- Update the sessions list

### 5. Automatic Session Creation

When you send your first message without selecting a session:
- A new session is automatically created
- The session title is set to your first question (truncated to 50 chars)
- All subsequent messages are saved to that session

## Backend Changes

### Database Schema

**New table: `chat_sessions`**
```sql
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Updated table: `chat_history`**
```sql
-- Added column:
session_id INTEGER FOREIGN KEY REFERENCES chat_sessions(id) ON DELETE CASCADE
```

### New API Endpoints

**1. Create Session**
```
POST /api/sessions
Body: { "title": "New Chat" }
Response: { "session_id": 1, "title": "New Chat" }
```

**2. Get Recent Sessions**
```
GET /api/sessions?limit=20
Response: { 
  "sessions": [
    {
      "id": 1,
      "title": "What is our refund policy?",
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:05:00",
      "message_count": 4
    }
  ]
}
```

**3. Get Session History**
```
GET /api/sessions/{session_id}
Response: {
  "history": [
    {
      "id": 1,
      "question": "What is our refund policy?",
      "answer": "According to our policy...",
      "sources": [...],
      "conflict_analysis": {...},
      "llm_used": "ollama (qwen3:4b-instruct-2507-q4_K_M)",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
}
```

**4. Delete Session**
```
DELETE /api/sessions/{session_id}
Response: { "success": true }
```

**5. Update Session Title**
```
PATCH /api/sessions/{session_id}
Body: { "title": "Updated Title" }
Response: { "success": true }
```

**6. Updated Query Endpoint**
```
POST /api/query
Body: { 
  "question": "What is our refund policy?",
  "n_results": 10,
  "session_id": 1  // Optional - creates new session if not provided
}
Response: {
  "answer": "...",
  "sources": [...],
  "conflict_analysis": {...},
  "session_id": 1  // Returns the session ID (new or existing)
}
```

## Frontend Changes

### New State Variables

```javascript
const [currentSessionId, setCurrentSessionId] = useState(null);
const [sessions, setSessions] = useState([]);
const [showSessions, setShowSessions] = useState(false);
```

### New Functions

**1. `loadSessions()`**
- Fetches recent sessions from the API
- Updates the sessions list

**2. `createNewSession()`**
- Creates a new session via API
- Clears current chat
- Updates sessions list

**3. `loadSession(sessionId)`**
- Loads all messages from a specific session
- Sets current session ID
- Restores last response in sidebar

**4. `deleteSession(sessionId, e)`**
- Deletes a session via API
- Clears chat if viewing that session
- Updates sessions list

### UI Components

**Session Management Buttons**
```jsx
<div style={{ display: 'flex', gap: '8px' }}>
  <button onClick={() => setShowSessions(!showSessions)}>
    <MessageSquare size={18} />
  </button>
  <button onClick={createNewSession}>
    <Plus size={18} />
  </button>
</div>
```

**Sessions Dropdown**
```jsx
{showSessions && (
  <div className="sessions-dropdown">
    {sessions.map(session => (
      <div onClick={() => loadSession(session.id)}>
        <div>{session.title}</div>
        <div>{session.message_count} messages</div>
        <button onClick={(e) => deleteSession(session.id, e)}>
          <Trash2 size={14} />
        </button>
      </div>
    ))}
  </div>
)}
```

## Migration

### For Existing Databases

Run the migration script to update your database:

```bash
python3 migrate_database.py
```

This will:
1. Create the `chat_sessions` table
2. Add `session_id` column to `chat_history`
3. Create a default "Legacy Chats" session
4. Migrate all existing chats to the default session
5. Create necessary indexes

### For New Installations

The database will be automatically initialized with the correct schema when you start the backend.

## Usage Examples

### Example 1: Starting a New Conversation

1. Open the Chat page
2. Click the "+" button to create a new session
3. Type your question and press Enter
4. The session is automatically created with your question as the title

### Example 2: Viewing Recent Sessions

1. Click the message icon in the chat header
2. See a list of your recent sessions
3. Click on any session to load it
4. Continue the conversation or start a new one

### Example 3: Organizing Sessions

1. View your recent sessions
2. Delete old or irrelevant sessions using the trash icon
3. Create new sessions for different topics
4. Switch between sessions as needed

## Best Practices

### Session Organization

- **Create new sessions for different topics** - Don't mix unrelated questions in one session
- **Delete old sessions regularly** - Keep your session list clean and manageable
- **Use descriptive first questions** - The first question becomes the session title

### Performance

- **Session limit** - The UI shows the 20 most recent sessions by default
- **Message limit** - Each session can have unlimited messages
- **Database cleanup** - Deleting a session also deletes all its messages (CASCADE)

### User Experience

- **Auto-save** - All messages are automatically saved to the current session
- **Session persistence** - Sessions are stored in the database and persist across page reloads
- **Visual feedback** - Current session is highlighted in the sessions list

## Troubleshooting

### Sessions Not Loading

**Problem:** Sessions list is empty or not loading

**Solution:**
1. Check backend logs for errors
2. Verify database file exists: `server/askify.db`
3. Run migration script if upgrading from old version
4. Check browser console for API errors

### Session Not Saving Messages

**Problem:** Messages are sent but not saved to session

**Solution:**
1. Check backend logs for database errors
2. Verify `session_id` is being sent in query request
3. Check database permissions
4. Restart backend server

### Migration Errors

**Problem:** Migration script fails

**Solution:**
1. Backup your database first: `cp server/askify.db server/askify.db.backup`
2. Check database file permissions
3. Verify Python sqlite3 module is available
4. Check error message for specific issue

## Technical Details

### Database Relationships

```
chat_sessions (1) ----< (many) chat_history
```

- One session can have many messages
- Deleting a session deletes all its messages (CASCADE)
- Each message belongs to exactly one session

### Session Title Generation

```python
# Generate title from first question (truncate to 50 chars)
title = question[:50] + "..." if len(question) > 50 else question
```

### Session Timestamps

- `created_at` - When the session was created
- `updated_at` - When the last message was added to the session

### Indexes

```sql
CREATE INDEX idx_chat_history_session ON chat_history(session_id);
```

This index improves performance when:
- Loading session history
- Counting messages per session
- Deleting sessions

## Future Enhancements

Potential improvements for future versions:

1. **Session search** - Search sessions by title or content
2. **Session tags** - Categorize sessions with tags
3. **Session export** - Export session history as PDF or JSON
4. **Session sharing** - Share sessions with team members
5. **Session templates** - Create reusable session templates
6. **Session analytics** - Track session usage and patterns
7. **Session archiving** - Archive old sessions instead of deleting
8. **Session merging** - Combine multiple sessions into one

## Summary

The chat session management feature provides a complete solution for organizing conversations:

- **Easy session creation** - One click to start a new conversation
- **Quick session switching** - View and load recent sessions instantly
- **Clean organization** - Delete old sessions to keep things tidy
- **Automatic saving** - All messages are saved without user action
- **Persistent storage** - Sessions survive page reloads and server restarts

The feature is fully integrated with the existing RAG system and requires minimal user interaction while providing powerful organization capabilities.
