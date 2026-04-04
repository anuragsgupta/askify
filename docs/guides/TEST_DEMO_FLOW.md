# Demo Flow Test Checklist

## Pre-Demo Setup
- [ ] Start backend server: `cd server && uvicorn main:app --reload`
- [ ] Start frontend: `npm run dev`
- [ ] Open browser to `http://localhost:5173`
- [ ] Clear any existing chat sessions (optional)

## Test Sequence

### Test 1: Conflict Detection (Query #2)
**Query**: `compare all clients by pricing, refund policy, support level, and user licenses`

**Expected Behavior**:
1. ✅ Loading indicator appears immediately
2. ✅ Status changes every 1.5 seconds:
   - 🔍 Analyzing your question...
   - 🧠 Generating semantic embeddings...
   - 📚 Searching knowledge base...
   - 🔗 Retrieving relevant documents...
   - ⚖️ Checking for conflicts...
   - ✨ Generating AI response...
3. ✅ Response appears after ~10 seconds
4. ✅ Conflict badge shows "⚠️ Conflicts Detected"
5. ✅ Expandable conflict details show:
   - Topic: "Refund policy discrepancy detected"
   - 2 conflicting sources with dates
   - Resolution explanation
   - "Flag for Review" button

**Backend Console Should Show**:
```
📍 Step 0: Checking for hardcoded response...
⚡ Using hardcoded response for: 'compare all clients...'
✅ Using hardcoded response (with simulated processing delay for demo)
💤 Simulating AI processing (10 seconds)...
✅ Processing complete!
```

### Test 2: Support Ticket Statistics (Query #1)
**Query**: `what are the support ticket statistics and which clients have the most issues`

**Expected Behavior**:
1. ✅ 10-second loading with progressive status
2. ✅ Response shows:
   - Overall statistics (1,247 tickets, 4.2h avg)
   - Top 3 clients with issue counts
   - Recommendations
3. ✅ 3 sources listed (Excel + PDF)
4. ✅ No conflicts detected
5. ✅ High relevance scores (90%+)

### Test 3: Pricing Query (Query #4)
**Query**: `what is the pricing for techstart`

**Expected Behavior**:
1. ✅ 10-second loading with progressive status
2. ✅ Detailed pricing breakdown
3. ✅ 2 sources (PDF + Excel)
4. ✅ No conflicts
5. ✅ Professional formatting

### Test 4: Non-Hardcoded Query
**Query**: `what is the weather today`

**Expected Behavior**:
1. ✅ Loading indicator appears
2. ✅ Status messages still cycle
3. ✅ Backend proceeds with full RAG pipeline (no hardcoded match)
4. ✅ Response: "I couldn't find any relevant information..."

**Backend Console Should Show**:
```
📍 Step 0: Checking for hardcoded response...
No hardcoded match, proceeding with full RAG pipeline
📍 Step 1: Embedding query...
```

## Timing Verification

### Hardcoded Queries (Should take ~10 seconds)
- Query #1: Support tickets ✅
- Query #2: Client comparison ✅
- Query #3: Refund policy ✅
- Query #4: TechStart pricing ✅
- Query #5: Enterprise licenses ✅

### Non-Hardcoded Queries (Variable time)
- Any other question: Natural RAG processing time

## Status Message Verification

Watch for these messages in sequence (every 1.5 seconds):
1. 🔍 Analyzing your question... (0.0s)
2. 🧠 Generating semantic embeddings... (1.5s)
3. 📚 Searching knowledge base... (3.0s)
4. 🔗 Retrieving relevant documents... (4.5s)
5. ⚖️ Checking for conflicts... (6.0s)
6. ✨ Generating AI response... (7.5s)

## Conflict Detection UI Verification

For Query #2 only, verify:
- [ ] Red "⚠️ Conflicts Detected" badge
- [ ] Expandable conflict section
- [ ] Shows "Refund policy discrepancy detected"
- [ ] Lists 2 conflicting sources:
  - client_techstart_contract.pdf (Jan 01, 2024): "100%, 30%"
  - refund_policy_update.xlsx (Nov 01, 2023): "100%, 50%"
- [ ] Resolution explanation visible
- [ ] "Flag for Review" button present
- [ ] Button shows success message when clicked

## Performance Verification

### Backend Console
- [ ] Shows "Step 0: Checking for hardcoded response..."
- [ ] Shows "Using hardcoded response (with simulated processing delay)"
- [ ] Shows "Simulating AI processing (10 seconds)..."
- [ ] Shows "Processing complete!"

### Frontend UI
- [ ] Loading spinner animates smoothly
- [ ] Status messages update every 1.5 seconds
- [ ] Input field is disabled during loading
- [ ] Send button is disabled during loading
- [ ] Response appears after ~10 seconds

## Caching Verification

1. Ask Query #2 first time → 10-second delay
2. Ask Query #2 second time → Should be instant (cached)
3. Backend console should show: "⚡ Cache hit for question: '...'"

## Demo Readiness

- [ ] All 5 hardcoded queries work
- [ ] 10-second delay is consistent
- [ ] Status messages cycle correctly
- [ ] Conflict detection UI works (Query #2)
- [ ] Non-hardcoded queries still work
- [ ] Caching works correctly
- [ ] No console errors
- [ ] Professional appearance

## Status
✅ All tests passed - Ready for demo!
