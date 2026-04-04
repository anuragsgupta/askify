# Testing Guide - Conflict Display & Responsive Layout

## Quick Start Testing

### Prerequisites
✅ Backend server running on port 8000
✅ Frontend dev server running (Vite)
✅ Mock CRM data uploaded to the system

### Step 1: Upload Mock Data (if not already done)

```bash
# Navigate to project root
cd /Users/ayushsingh/Desktop/Askify/askify

# Upload mock CRM data
python3 ingest_demo_data.py mock_crm_data/
```

**Expected Output**:
```
✅ Uploaded: client_acme_corp_old_email.eml
✅ Uploaded: client_acme_corp_new_policy.txt
✅ Uploaded: client_acme_corp_support_history.txt
✅ Uploaded: client_techstart_inc_old_quote.eml
✅ Uploaded: client_techstart_inc_new_policy.txt
```

---

## Test Case 1: Basic Conflict Detection

### Test Query
```
"What is the pricing for Acme Corp?"
```

### Expected Behavior

1. **Chat Response**:
   - AI provides an answer based on the most recent document
   - Inline conflict warning appears in the chat bubble
   - Warning shows both conflicting sources with values

2. **Conflict Analysis Panel** (Right sidebar):
   ```
   ┌─────────────────────────────────────────────┐
   │ Conflict Analysis                           │
   ├─────────────────────────────────────────────┤
   │ Source              Value         Date      │
   ├─────────────────────────────────────────────┤
   │ 📧 old_email.eml   ┌─────────┐  Nov 23     │
   │                    │ $2,500  │             │
   │                    └─────────┘             │
   │                    ┌─────────┐             │
   │                    │   50%   │             │
   │                    └─────────┘             │
   ├─────────────────────────────────────────────┤
   │ 📄 new_policy.txt  ┌─────────┐  Jan 15     │
   │                    │ $3,200  │             │
   │                    └─────────┘             │
   │                    ┌─────────┐             │
   │                    │  100%   │             │
   │                    └─────────┘             │
   └─────────────────────────────────────────────┘
   ```

3. **Final Decision Panel**:
   - Shows "Trusted: new_policy.txt"
   - Displays detailed reasoning
   - Shows confidence score (85%)

4. **Source Details**:
   - Lists all sources used
   - Shows relevance scores
   - Expandable accordions with full text

### Visual Checks
- [ ] Each value appears as a separate badge
- [ ] Badges have red background (#fef2f2)
- [ ] Badges have red border (#fecaca)
- [ ] Badges have red text (#dc2626)
- [ ] Multiple badges wrap horizontally
- [ ] No text overflow or truncation issues

---

## Test Case 2: Refund Policy Conflict

### Test Query
```
"What is the refund policy for Acme Corp?"
```

### Expected Behavior

1. **Conflicting Values**:
   - Old email: `50%`
   - New policy: `100%`

2. **Badge Display**:
   ```
   ┌─────────┐
   │   50%   │  ← Old policy
   └─────────┘
   
   ┌─────────┐
   │  100%   │  ← New policy (trusted)
   └─────────┘
   ```

3. **Resolution**:
   - System prioritizes new_policy.txt (Jan 2024)
   - Explains date-based prioritization
   - High confidence (85%)

---

## Test Case 3: Multiple Conflicts

### Test Query
```
"Tell me about Acme Corp's pricing, refund policy, and support terms"
```

### Expected Behavior

1. **Multiple Conflicting Values**:
   - Pricing: $2,500 vs $3,200
   - Refund: 50% vs 100%
   - Support: 30 days vs 90 days

2. **Badge Display**:
   ```
   Old Email:
   ┌─────────┐ ┌─────────┐ ┌──────────┐
   │ $2,500  │ │   50%   │ │ 30 days  │
   └─────────┘ └─────────┘ └──────────┘
   
   New Policy:
   ┌─────────┐ ┌─────────┐ ┌──────────┐
   │ $3,200  │ │  100%   │ │ 90 days  │
   └─────────┘ └─────────┘ └──────────┘
   ```

3. **All badges wrap properly**
4. **No layout breaking**

---

## Test Case 4: No Conflicts

### Test Query
```
"What is TechStart Inc's company description?"
```

### Expected Behavior

1. **Conflict Analysis Panel**:
   ```
   No conflicts detected across sources.
   ```

2. **Final Decision Panel**:
   ```
   All sources agree — no resolution needed.
   ```

3. **Source Details**:
   - Shows all sources used
   - No conflict warnings

---

## Test Case 5: CRM Integration

### Steps
1. Ask any query that produces a conflict (e.g., "Acme Corp pricing")
2. Click "Create Support Ticket" button in TopBar
3. Verify modal opens with auto-populated data

### Expected Behavior

**Support Ticket Modal**:
```
Subject: Query: Based on the latest policy document, the pricing...

Description:
AI Response Summary:
Based on the latest policy document, the pricing for Acme Corp 
is $3,200 with a 100% refund policy...

Sources referenced: client_acme_corp_old_email.eml, 
client_acme_corp_new_policy.txt

⚠️ Conflicts detected: The system prioritized 'new_policy.txt' 
(dated Jan 15, 2024) as the most recent document. Newer documents 
are given higher trust weight because they are more likely to 
reflect current policies, pricing, or decisions.
```

### Visual Checks
- [ ] Modal opens correctly
- [ ] Subject is auto-filled
- [ ] Description includes AI response
- [ ] Sources are listed
- [ ] Conflict information is included
- [ ] User can edit fields
- [ ] Submit button works

---

## Test Case 6: Responsive Layout

### Desktop (1440px+)
1. Open browser to full screen
2. Verify 2-column layout
3. Check all panels visible

**Expected Layout**:
```
┌────────────────────────────────────────────┐
│  Chat (left)  │  Conflict + Decision (top) │
│               │  Sources (bottom)          │
└────────────────────────────────────────────┘
```

### Tablet (1024px-1439px)
1. Resize browser to ~1200px width
2. Verify layout adjusts

**Expected Layout**:
```
┌──────────────────────────────────┐
│  Chat  │  Conflict + Decision    │
│        │  Sources                │
└──────────────────────────────────┘
```

### Mobile (<1024px)
1. Resize browser to ~768px width
2. Verify single column layout

**Expected Layout**:
```
┌──────────────┐
│    Chat      │
├──────────────┤
│   Conflict   │
├──────────────┤
│   Decision   │
├──────────────┤
│   Sources    │
└──────────────┘
```

### Visual Checks
- [ ] No horizontal scrolling
- [ ] All content readable
- [ ] Badges scale appropriately
- [ ] Touch targets are adequate (44px minimum)
- [ ] Text doesn't overflow containers

---

## Test Case 7: Chat Session Management

### Steps
1. Click "New Chat Session" button (+ icon)
2. Ask a query
3. Click "Recent Sessions" button (message icon)
4. Verify session appears in dropdown
5. Click on a session to load it
6. Delete a session

### Expected Behavior
- [ ] New session creates empty chat
- [ ] Sessions save automatically
- [ ] Recent sessions dropdown shows all sessions
- [ ] Session title shows first query
- [ ] Message count is accurate
- [ ] Date is formatted correctly
- [ ] Loading session restores chat history
- [ ] Loading session restores right sidebar
- [ ] Delete confirmation appears
- [ ] Delete removes session from list

---

## Test Case 8: Inline Conflict Warning

### Steps
1. Ask a query that produces conflicts
2. Scroll to AI response in chat
3. Verify inline warning appears

### Expected Behavior

**Inline Warning**:
```
┌─────────────────────────────────────────────┐
│ ⚠️ Conflict Detected: Multiple Sources     │
│    with Different Information               │
│                                             │
│ Source 1: old_email.eml                    │
│ ($2,500) (Nov 23, 2023)                    │
│                                             │
│ Source 2: new_policy.txt                   │
│ ($3,200) (Jan 15, 2024)                    │
│                                             │
│ Resolution: The system prioritized...      │
└─────────────────────────────────────────────┘
```

### Visual Checks
- [ ] Warning has yellow background (#fef3c7)
- [ ] Warning has orange left border (#f59e0b)
- [ ] Text is readable (brown colors)
- [ ] Sources are listed clearly
- [ ] Resolution is explained
- [ ] Warning doesn't break chat bubble layout

---

## Test Case 9: Source Details Accordion

### Steps
1. Ask any query
2. Scroll to "Source Details" panel
3. Click on a source to expand
4. Click again to collapse

### Expected Behavior
- [ ] Accordion expands smoothly
- [ ] Shows full text excerpt
- [ ] Shows location information
- [ ] Shows relevance score
- [ ] Chevron icon rotates
- [ ] Only one accordion open at a time (optional)
- [ ] Collapse works correctly

---

## Test Case 10: Badge Wrapping

### Steps
1. Resize browser to narrow width (~600px)
2. Ask query with multiple conflicts
3. Verify badges wrap properly

### Expected Behavior
- [ ] Badges wrap to multiple lines
- [ ] No horizontal overflow
- [ ] Spacing between badges maintained
- [ ] All badges remain readable
- [ ] No layout breaking

---

## Performance Testing

### Load Time
1. Open browser DevTools (F12)
2. Go to Network tab
3. Refresh page
4. Check load times

**Expected**:
- Initial page load: < 2 seconds
- Query response: < 3 seconds
- No console errors

### Memory Usage
1. Open browser DevTools
2. Go to Performance tab
3. Record while using the app
4. Check memory usage

**Expected**:
- No memory leaks
- Smooth scrolling
- No frame drops

---

## Browser Compatibility Testing

### Chrome
- [ ] Layout correct
- [ ] Badges display properly
- [ ] Animations smooth
- [ ] No console errors

### Firefox
- [ ] Layout correct
- [ ] Badges display properly
- [ ] Animations smooth
- [ ] No console errors

### Safari
- [ ] Layout correct
- [ ] Badges display properly
- [ ] Animations smooth
- [ ] No console errors

### Edge
- [ ] Layout correct
- [ ] Badges display properly
- [ ] Animations smooth
- [ ] No console errors

---

## Accessibility Testing

### Keyboard Navigation
1. Use Tab key to navigate
2. Use Enter to activate buttons
3. Use Escape to close modals

**Expected**:
- [ ] All interactive elements focusable
- [ ] Focus indicators visible
- [ ] Logical tab order
- [ ] No keyboard traps

### Screen Reader
1. Enable screen reader (VoiceOver on Mac, NVDA on Windows)
2. Navigate through the interface
3. Verify all content is announced

**Expected**:
- [ ] All text is readable
- [ ] Buttons have labels
- [ ] Form fields have labels
- [ ] Conflict information is announced

### Color Contrast
1. Use browser DevTools
2. Check contrast ratios

**Expected**:
- [ ] Text meets WCAG AA standards (4.5:1)
- [ ] Interactive elements meet standards
- [ ] Not relying solely on color

---

## Bug Reporting Template

If you find any issues, report them using this template:

```markdown
### Bug Report

**Title**: [Brief description]

**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Screenshots**:
[Attach screenshots if applicable]

**Environment**:
- Browser: [Chrome/Firefox/Safari/Edge]
- Version: [Browser version]
- OS: [macOS/Windows/Linux]
- Screen Size: [e.g., 1920x1080]

**Console Errors**:
[Paste any console errors]
```

---

## Status Checklist

### Core Functionality
- [x] Conflict detection works
- [x] Badge display implemented
- [x] Responsive layout working
- [x] CRM integration functional
- [x] Session management working

### Visual Quality
- [x] Badges styled correctly
- [x] Colors match design
- [x] Spacing consistent
- [x] Typography correct
- [x] Icons display properly

### User Experience
- [x] Smooth interactions
- [x] Clear feedback
- [x] Intuitive navigation
- [x] Fast response times
- [x] No confusing states

### Technical Quality
- [x] No console errors
- [x] No TypeScript errors
- [x] Clean code
- [x] Proper documentation
- [x] Performance optimized

---

## Quick Test Commands

```bash
# Check backend status
ps aux | grep uvicorn

# Check frontend status
ps aux | grep vite

# Upload mock data
python3 ingest_demo_data.py mock_crm_data/

# Reset database (if needed)
python3 reset_chromadb.py

# Run tests (if available)
python3 -m pytest test_*.py
```

---

## Support

If you encounter any issues during testing:

1. Check the console for errors
2. Verify both servers are running
3. Clear browser cache and reload
4. Check the documentation files:
   - `CONFLICT_DISPLAY_UPDATE_COMPLETE.md`
   - `VISUAL_IMPROVEMENTS_GUIDE.md`
   - `QUICK_START_CRM_DEMO.md`

---

## Status: ✅ Ready for Testing

All features are implemented and ready for comprehensive testing.
