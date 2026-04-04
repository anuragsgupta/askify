# Conflict Analysis UI Improvements

## Overview

Enhanced the Conflict Analysis panel in the Chat interface to provide more detailed source information, full citations, and an admin review workflow.

## What Was Changed

### 1. Enhanced Conflict Display

**Before:**
- Simple table showing: Source | Value | Date
- Limited information about each source
- No way to see the actual text from documents
- No citation details

**After:**
- Detailed card-based layout for each conflicting source
- Full source metadata including:
  - Document name with icon
  - Location within document (page number, section, etc.)
  - Conflicting values highlighted in red badges
  - Date information in yellow badges
- Expandable citations showing actual text excerpts from each source
- Visual hierarchy with color-coded source types

### 2. Source Citation Excerpts

Each conflicting source now includes:
- **Expandable text excerpt**: Click the chevron to reveal the actual text from the document
- **Formatted citation**: Italicized quote with source-colored border
- **Context**: Shows ~200 characters of the original text where the conflict was detected

### 3. Admin Review Workflow

Added a "🚩 Flag for Review" button that:
- Appears only when conflicts are detected
- Sends conflict data to the backend API
- Includes:
  - The user's question
  - All conflicting sources with their details
  - Timestamp
  - Session ID for tracking
- Provides confirmation with a unique Review ID
- Logs to server console for admin monitoring

### 4. Conflict Summary

Added a summary box showing:
- Total number of conflicting sources
- Conflict topic/type
- Visual warning styling

## API Changes

### New Endpoint: POST /api/conflicts/flag-review

**Purpose**: Allow users to flag conflicts for manual admin verification

**Request Body:**
```json
{
  "question": "What is the refund policy?",
  "conflicts": {
    "has_conflicts": true,
    "conflicts": [...],
    "trusted_sources": [...]
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "session_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "message": "Conflict flagged for admin review",
  "review_id": "review_2024-01-15T10:30:00Z"
}
```

**Server Logging:**
The endpoint logs detailed information to the console for admin review:
```
🚩 CONFLICT FLAGGED FOR ADMIN REVIEW
   Question: What is the refund policy?
   Timestamp: 2024-01-15T10:30:00Z
   Session ID: 123
   Conflicts: {...}
   Number of conflicting sources: 3
```

## Visual Improvements

### Color Coding
- **Red badges**: Conflicting values
- **Yellow badges**: Date information
- **Source-specific colors**: PDF (orange), Excel (green), Email (blue)

### Interactive Elements
- **Expand/Collapse**: Click chevron to show/hide citations
- **Hover effects**: Cards respond to mouse interaction
- **Button states**: Flag button styled with warning colors

### Layout
- **Card-based design**: Each source in its own container
- **Responsive spacing**: Proper padding and margins
- **Scrollable content**: Long lists of conflicts scroll smoothly

## Benefits

1. **Transparency**: Users can see exactly what text caused the conflict
2. **Verification**: Admins can review flagged conflicts for accuracy
3. **Trust**: Full citations build confidence in the system's decisions
4. **Debugging**: Easier to identify why conflicts were detected
5. **Compliance**: Audit trail for conflict resolution decisions

## Future Enhancements

### Potential Additions:
1. **Admin Dashboard**: Dedicated page to review flagged conflicts
2. **Database Storage**: Store flagged conflicts in a dedicated table
3. **Resolution Override**: Allow admins to manually override AI decisions
4. **Notification System**: Email/Slack alerts when conflicts are flagged
5. **Conflict History**: Track how conflicts were resolved over time
6. **Bulk Review**: Review multiple flagged conflicts at once
7. **User Feedback**: Allow users to rate conflict resolutions
8. **Export**: Download conflict reports for compliance

## Testing

To test the improvements:

1. **Start the server**:
   ```bash
   cd server
   uvicorn main:app --reload
   ```

2. **Start the frontend**:
   ```bash
   npm run dev
   ```

3. **Create a conflict scenario**:
   - Upload documents with conflicting information (e.g., different pricing)
   - Ask a question that triggers the conflict detection
   - Example: "What is the price for TechStart package?"

4. **Verify the UI**:
   - Check that conflict cards display properly
   - Click chevrons to expand/collapse citations
   - Click "Flag for Review" button
   - Verify the confirmation message with Review ID

5. **Check server logs**:
   - Look for the "🚩 CONFLICT FLAGGED FOR ADMIN REVIEW" message
   - Verify all conflict details are logged

## Files Modified

1. **src/pages/Chat.jsx**
   - Enhanced conflict analysis panel
   - Added expandable source cards
   - Implemented flag for review button
   - Added API call to flag endpoint

2. **server/routes/query.py**
   - Added `ConflictReviewRequest` model
   - Added `POST /api/conflicts/flag-review` endpoint
   - Implemented server-side logging

## Related Documentation

- **CONFLICT_DETECTION_AND_CRM_GUIDE.md**: Original conflict detection documentation
- **DEMO_CONFLICT_AND_CRM.md**: Demo script for conflict detection
- **server/services/conflict.py**: Conflict detection algorithm

## Notes

- The current implementation logs to console; production should use a database
- Review IDs are timestamp-based; consider UUIDs for production
- No authentication on the flag endpoint; add auth for production
- Consider rate limiting to prevent abuse
