# Demo: Conflict Detection & CRM Integration

## Quick Demo Guide

### Demo 1: Conflict Detection

**Scenario:** Two pricing documents with different values

#### Step 1: Create Test Documents

**File 1:** `pricing_old.txt`
```
Date: December 1, 2023
Product Pricing Update

Our standard enterprise plan is priced at $100 per month.
This includes a 15% discount for annual subscriptions.
Refund policy: 30-day money-back guarantee.
```

**File 2:** `pricing_new.txt`
```
Date: January 15, 2024
Updated Pricing Policy

New enterprise plan pricing: $150 per month.
Annual subscription discount increased to 20%.
Extended refund policy: 45-day money-back guarantee.
```

#### Step 2: Upload Documents

1. Go to **Documents** page
2. Upload both `pricing_old.txt` and `pricing_new.txt`
3. Wait for processing to complete

#### Step 3: Ask Conflicting Question

Go to **Chat** page and ask:
```
What is our enterprise plan pricing and discount percentage?
```

#### Step 4: Observe Conflict Detection

**Expected Response:**

**Chat Answer:**
```
Based on our most recent pricing document from January 2024, our enterprise 
plan is priced at $150 per month with a 20% discount for annual subscriptions.
```

**Conflict Analysis Panel (Right Sidebar):**
```
┌─────────────────────────────────────┐
│ Conflict Analysis                   │
├─────────────────────────────────────┤
│ Source          Value      Date     │
├─────────────────────────────────────┤
│ 📄 pricing_new  $150, 20%  Jan 2024│
│ 📄 pricing_old  $100, 15%  Dec 2023│
└─────────────────────────────────────┘
```

**Final Decision Panel:**
```
┌─────────────────────────────────────┐
│ Final Decision                      │
├─────────────────────────────────────┤
│ ✓ Trusted: pricing_new.txt          │
│                                     │
│ Detailed Reason:                    │
│ The system prioritized              │
│ 'pricing_new.txt' (dated Jan 15,    │
│ 2024) as the most recent document.  │
│ Newer documents are given higher    │
│ trust weight because they are more  │
│ likely to reflect current policies. │
│                                     │
│ Confidence: ████████░░ 85%          │
└─────────────────────────────────────┘
```

---

### Demo 2: CRM Integration

**Scenario:** Create support ticket from RAG response

#### Step 1: Ask a Question

In **Chat** page, ask:
```
What is our refund policy for enterprise customers?
```

#### Step 2: Wait for Response

System responds with:
```
According to our updated policy from January 2024, enterprise customers 
have a 45-day money-back guarantee. Refunds can be requested through our 
customer service portal with proof of purchase. The refund amount is 20% 
of the subscription fee for annual plans.

[Sources: pricing_new.txt, refund_policy.pdf]
```

#### Step 3: Create Support Ticket

1. Click **"Create Support Ticket"** button (top-right corner)
2. Modal opens with auto-populated fields

#### Step 4: Review Auto-Populated Content

**Subject Field:**
```
Query: According to our updated policy from January 2024, en...
```

**Description Field:**
```
AI Response Summary:
According to our updated policy from January 2024, enterprise customers 
have a 45-day money-back guarantee. Refunds can be requested through our 
customer service portal with proof of purchase. The refund amount is 20% 
of the subscription fee for annual plans.

Sources referenced: pricing_new.txt, refund_policy.pdf

⚠️ Conflicts detected: The system prioritized 'pricing_new.txt' (dated 
Jan 15, 2024) as the most recent document. Newer documents are given 
higher trust weight because they are more likely to reflect current 
policies, pricing, or decisions.
```

#### Step 5: Edit and Submit

1. Edit subject/description if needed
2. Click **"Submit Ticket"**
3. See success message: `✅ Support Ticket Created Successfully!`

---

### Demo 3: Combined Workflow

**Scenario:** Customer service agent handling pricing inquiry

#### Complete Workflow:

1. **Customer asks:** "What's the current pricing?"

2. **Agent opens Chat** and asks:
   ```
   What is our current enterprise plan pricing?
   ```

3. **System detects conflict:**
   - Old doc: $100/month
   - New doc: $150/month
   - Trusts new doc (Jan 2024)

4. **Agent sees:**
   - Answer: "$150/month"
   - Conflict panel: Both sources with dates
   - Decision: Why $150 was chosen (85% confidence)

5. **Agent needs to escalate:**
   - Clicks "Create Support Ticket"
   - Reviews auto-populated content
   - Adds note: "Customer confused about pricing change"
   - Submits ticket

6. **Support team receives:**
   - Full context from RAG
   - Conflict information
   - Source references
   - Agent's additional notes

---

## Visual Flow Diagrams

### Conflict Detection Flow

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ RAG Retrieves Docs  │
└──────┬──────────────┘
       │
       ▼
┌──────────────────────┐
│ Conflict Detection   │
│ - Group by source    │
│ - Extract dates      │
│ - Extract values     │
│ - Compare values     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Conflicts Found?     │
└──────┬───────────────┘
       │
       ├─ Yes ──┐
       │        ▼
       │   ┌────────────────────┐
       │   │ Prioritize by Date │
       │   └────────┬───────────┘
       │            │
       │            ▼
       │   ┌────────────────────┐
       │   │ Generate Resolution│
       │   │ - Chosen source    │
       │   │ - Reason           │
       │   │ - Confidence       │
       │   └────────┬───────────┘
       │            │
       └─ No ───────┤
                    │
                    ▼
           ┌────────────────┐
           │ Display Result │
           │ - Answer       │
           │ - Conflicts    │
           │ - Decision     │
           └────────────────┘
```

### CRM Integration Flow

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ RAG Generates Answer│
└──────┬──────────────┘
       │
       ▼
┌──────────────────────────┐
│ Store in Global Variable │
│ window.__lastRagResponse │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────┐
│ User Clicks "Create  │
│ Support Ticket"      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Check Global Variable│
└──────┬───────────────┘
       │
       ├─ Has Context ──┐
       │                ▼
       │   ┌────────────────────┐
       │   │ Auto-Populate:     │
       │   │ - Subject (60ch)   │
       │   │ - Description      │
       │   │ - Sources          │
       │   │ - Conflicts        │
       │   └────────┬───────────┘
       │            │
       └─ No Context┤
                    │
                    ▼
           ┌────────────────┐
           │ Show Modal     │
           │ - Editable     │
           │ - Submit       │
           └────────────────┘
```

---

## Expected Outputs

### Conflict Detection Output

**Console Log (Backend):**
```
📍 Step 3: Running conflict detection...
   ⚠️  Conflicts detected: 1 conflict(s)
   
Conflict Details:
- Topic: Value discrepancy detected across sources
- Sources involved: 2
  1. pricing_new.txt (Jan 15, 2024): $150, 20%
  2. pricing_old.txt (Dec 1, 2023): $100, 15%
- Resolution: Trusted pricing_new.txt (newest)
- Confidence: 85%
```

**UI Display:**
- Red badges for conflicting values
- Green badge for trusted source
- Progress bar showing confidence
- Detailed explanation text

### CRM Integration Output

**Modal Content:**
```
┌────────────────────────────────────────────┐
│ Create Support Ticket                      │
├────────────────────────────────────────────┤
│ Auto-populated from your last RAG query.   │
│                                            │
│ Subject:                                   │
│ ┌────────────────────────────────────────┐ │
│ │ Query: According to our updated poli...│ │
│ └────────────────────────────────────────┘ │
│                                            │
│ Description:                               │
│ ┌────────────────────────────────────────┐ │
│ │ AI Response Summary:                   │ │
│ │ According to our updated policy from   │ │
│ │ January 2024, enterprise customers...  │ │
│ │                                        │ │
│ │ Sources referenced: pricing_new.txt,   │ │
│ │ refund_policy.pdf                      │ │
│ │                                        │ │
│ │ ⚠️ Conflicts detected: The system...   │ │
│ └────────────────────────────────────────┘ │
│                                            │
│              [Cancel]  [Submit Ticket]     │
└────────────────────────────────────────────┘
```

**Success Alert:**
```
┌────────────────────────────────────┐
│ ✅ Support Ticket Created          │
│    Successfully!                   │
└────────────────────────────────────┘
```

---

## Testing Checklist

### Conflict Detection Tests

- [ ] Upload two documents with different dates
- [ ] Upload two documents with different percentages
- [ ] Upload two documents with different dollar amounts
- [ ] Ask question that triggers both documents
- [ ] Verify conflict panel shows both sources
- [ ] Verify decision panel shows newest source
- [ ] Verify confidence score is displayed
- [ ] Verify explanation mentions date prioritization

### CRM Integration Tests

- [ ] Ask a question in Chat
- [ ] Wait for RAG response
- [ ] Click "Create Support Ticket"
- [ ] Verify subject is auto-populated
- [ ] Verify description includes answer summary
- [ ] Verify description includes source references
- [ ] Verify description includes conflict info (if any)
- [ ] Edit fields manually
- [ ] Submit ticket
- [ ] Verify success message appears

### Edge Cases

- [ ] No RAG context (empty ticket form)
- [ ] No conflicts (clean resolution)
- [ ] No dates in documents (medium confidence)
- [ ] Multiple conflicts (shows all)
- [ ] Very long answers (truncated properly)

---

## Common Issues

### Issue 1: No Conflicts Detected

**Symptoms:** Conflict panel says "No conflicts detected" when there should be

**Causes:**
- Documents don't have extractable dates
- Values are in different formats
- Values are not numerical (%, $)

**Solutions:**
- Add dates to documents: "Date: Jan 15, 2024"
- Use standard formats: "15%", "$100"
- Check backend logs for extraction errors

### Issue 2: CRM Fields Empty

**Symptoms:** Modal opens but fields are blank

**Causes:**
- No RAG query was made
- Global variable not set
- Page was refreshed

**Solutions:**
- Ask a question in Chat first
- Check console: `window.__lastRagResponse`
- Don't refresh page between query and ticket creation

### Issue 3: Wrong Source Trusted

**Symptoms:** System trusts older document instead of newer

**Causes:**
- Date extraction failed
- Newer document has no date
- Date format not recognized

**Solutions:**
- Use standard date formats
- Add explicit date field
- Check date extraction patterns in code

---

## Summary

Both features work seamlessly together:

1. **Conflict Detection** provides transparency about contradictions
2. **CRM Integration** captures full context for support teams
3. **Combined** they create a complete workflow for handling complex queries

**Key Benefits:**
- ✅ Automatic conflict detection
- ✅ Date-based prioritization
- ✅ Clear explanations
- ✅ One-click ticket creation
- ✅ Full context preservation
- ✅ Editable before submission

**Ready to demo!** 🎉

Follow the steps above to see both features in action.
