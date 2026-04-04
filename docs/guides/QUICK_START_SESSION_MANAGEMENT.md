# Quick Start: Chat Session Management

## For Existing Users (Upgrading)

### Step 1: Run Migration

```bash
python3 migrate_database.py
```

Expected output:
```
🔧 DATABASE MIGRATION - Adding Session Support
📌 DB path: /path/to/server/askify.db
📝 Creating chat_sessions table...
✅ chat_sessions table created
📝 Adding session_id column to chat_history...
✅ session_id column added
📝 Creating default session for existing chats...
✅ Migrated existing chats to session ID 1
📝 Creating indexes...
✅ Indexes created

✅ Migration completed successfully!
```

### Step 2: Restart Backend

```bash
# Stop current backend (Ctrl+C)
./start_backend.sh
```

### Step 3: Test Features

1. Open browser to `http://localhost:5173`
2. Go to Chat page
3. Click the "+" button to create a new session
4. Click the message icon to view recent sessions

## For New Users

No migration needed! Just start the backend:

```bash
./start_backend.sh
```

The database will be automatically initialized with session support.

## Using Session Management

### Create New Session

1. Click the **"+"** button in the chat header
2. Start typing your question
3. Session is created automatically

### View Recent Sessions

1. Click the **message icon** button in the chat header
2. See list of recent sessions
3. Click any session to load it

### Delete Session

1. Open recent sessions list
2. Click the **trash icon** next to any session
3. Confirm deletion

## Troubleshooting

### Migration Failed

**Error:** "Database file not found"

**Solution:** Start the backend first to create the database:
```bash
./start_backend.sh
# Wait for it to start, then Ctrl+C
python3 migrate_database.py
./start_backend.sh
```

### Sessions Not Showing

**Problem:** Sessions list is empty

**Solution:**
1. Send a message to create a session
2. Refresh the page
3. Check backend logs for errors

### Messages Not Saving

**Problem:** Messages disappear after refresh

**Solution:**
1. Check backend is running
2. Check browser console for errors
3. Verify database file exists: `server/askify.db`

## Features Overview

| Feature | Button | Description |
|---------|--------|-------------|
| New Session | + icon | Start fresh conversation |
| Recent Sessions | Message icon | View past conversations |
| Load Session | Click session | Switch to that conversation |
| Delete Session | Trash icon | Remove conversation |

## What Gets Saved

- ✅ All messages (questions and answers)
- ✅ Session title (first question)
- ✅ Session timestamps (created, updated)
- ✅ Message count per session
- ✅ Sources and conflict analysis

## What Doesn't Get Saved

- ❌ Expanded/collapsed state of sources
- ❌ Scroll position in chat
- ❌ Sessions dropdown open/closed state

## Tips

1. **Start new sessions for different topics** - Keep conversations organized
2. **Delete old sessions regularly** - Keep the list manageable
3. **Use descriptive first questions** - They become the session title
4. **Switch sessions freely** - No data is lost when switching

## That's It!

You now have full session management for your chat conversations. Create, view, switch, and delete sessions as needed. All messages are automatically saved.

**Need help?** See `CHAT_SESSION_MANAGEMENT_GUIDE.md` for complete documentation.
