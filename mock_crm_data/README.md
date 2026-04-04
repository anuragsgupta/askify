# Mock CRM Data - Conflict Detection & Auto-Fill Demo

## Overview

This directory contains realistic mock data designed to demonstrate:

1. **Autonomous CRM Ticket Auto-Fill** - System automatically populates support tickets with relevant context
2. **Conflict Detection** - System identifies contradictions between old and new documents
3. **Date-Based Prioritization** - System prioritizes newer documents and explains reasoning

## Mock Data Files

### Scenario 1: Acme Corp - Pricing Conflict

**Client:** Acme Corporation  
**Issue:** Pricing discrepancy between old email and new policy

#### Files:

1. **`client_acme_corp_old_email.eml`** (November 15, 2023)
   - Old pricing: $2,500/month
   - Old discount: 15% annual
   - Old setup fee: $1,000
   - Old refund: 50%, 30 days
   - Old support: 9-5 EST, email only

2. **`client_acme_corp_new_policy.txt`** (January 15, 2024)
   - New pricing: $3,200/month
   - New discount: 20% annual
   - New setup fee: WAIVED
   - New refund: 100%, 60 days
   - New support: 24/7, phone/email/chat

3. **`client_acme_corp_support_history.txt`** (February 10, 2024)
   - Recent support tickets
   - Account health metrics
   - Resolution history

#### Expected Conflicts:

| Metric | Old Value (Nov 2023) | New Value (Jan 2024) | Conflict? |
|--------|---------------------|---------------------|-----------|
| Monthly Price | $2,500 | $3,200 | ✅ YES |
| Annual Discount | 15% | 20% | ✅ YES |
| Setup Fee | $1,000 | $0 (waived) | ✅ YES |
| Refund % | 50% | 100% | ✅ YES |
| Refund Period | 30 days | 60 days | ✅ YES |

#### Test Query:

```
"What is the current pricing for Acme Corp's Enterprise Plan?"
```

#### Expected System Behavior:

1. **Detect Conflict:** System finds different prices ($2,500 vs $3,200)
2. **Extract Dates:** Nov 15, 2023 vs Jan 15, 2024
3. **Prioritize:** Choose Jan 2024 document (newer)
4. **Explain:** "The system prioritized 'client_acme_corp_new_policy.txt' (dated Jan 15, 2024) as the most recent document..."
5. **Confidence:** 85% (date-based resolution)
6. **Auto-Fill Ticket:**
   - Subject: "Query: According to our updated policy from January 2024..."
   - Description: Full answer + sources + conflict explanation

---

### Scenario 2: TechStart Inc - Refund Policy Conflict

**Client:** TechStart Inc  
**Issue:** Refund policy discrepancy between old email and new policy

#### Files:

1. **`client_techstart_inc_old_quote.eml`** (October 5, 2023)
   - Old refund: 50% of subscription
   - Old period: 30 days
   - Old processing: 10-15 business days
   - Setup fee: Non-refundable

2. **`client_techstart_inc_new_policy.txt`** (January 20, 2024)
   - New refund: 100% full refund
   - New period: 60 days
   - New processing: 5-7 business days
   - Setup fee: Fully refundable

#### Expected Conflicts:

| Metric | Old Value (Oct 2023) | New Value (Jan 2024) | Conflict? |
|--------|---------------------|---------------------|-----------|
| Refund Amount | 50% | 100% | ✅ YES |
| Refund Period | 30 days | 60 days | ✅ YES |
| Processing Time | 10-15 days | 5-7 days | ✅ YES |
| Setup Fee Refund | Non-refundable | Refundable | ✅ YES |

#### Test Query:

```
"What is our current refund policy and refund amount percentage?"
```

#### Expected System Behavior:

1. **Detect Conflict:** System finds different refund percentages (50% vs 100%)
2. **Extract Dates:** Oct 5, 2023 vs Jan 20, 2024
3. **Prioritize:** Choose Jan 2024 document (newer)
4. **Explain:** Clear reasoning about date-based prioritization
5. **Confidence:** 85% (date-based resolution)
6. **Auto-Fill Ticket:** Complete context with conflict explanation

---

## How to Use This Mock Data

### Step 1: Upload Documents

```bash
# Option A: Use the demo script (recommended)
python3 test_crm_conflict_demo.py

# Option B: Upload manually via UI
# 1. Go to Documents page
# 2. Upload all files from mock_crm_data/
# 3. Wait for processing to complete
```

### Step 2: Test Queries

**Query 1: Pricing Conflict**
```
What is the current pricing for Acme Corp's Enterprise Plan?
```

**Query 2: Refund Conflict**
```
What is our current refund policy and refund amount percentage?
```

**Query 3: Complex Multi-Conflict**
```
What are our current Enterprise Plan pricing, refund policy, and refund percentage? 
Include setup fees and processing time.
```

### Step 3: Observe Results

**In Chat UI:**
1. **Answer** - System provides answer based on newest document
2. **Conflict Analysis Panel** - Shows conflicting sources with dates
3. **Final Decision Panel** - Explains why newest document was chosen
4. **Confidence Score** - Shows 85% confidence (date-based)

**In CRM Ticket:**
1. Click "Create Support Ticket" button
2. See auto-populated subject and description
3. Review conflict explanation in description
4. Edit if needed and submit

---

## Expected Conflict Detection Output

### Console Output (Backend):

```
📍 Step 3: Running conflict detection...
   ⚠️  Conflicts detected: 1 conflict(s)

Conflict Details:
- Topic: Value discrepancy detected across sources
- Sources involved: 2
  1. client_acme_corp_new_policy.txt (Jan 15, 2024): $3,200, 20%
  2. client_acme_corp_old_email.eml (Nov 15, 2023): $2,500, 15%
- Resolution: Trusted client_acme_corp_new_policy.txt (newest)
- Confidence: 85%
```

### UI Output (Chat Page):

**Conflict Analysis Panel:**
```
┌─────────────────────────────────────────────────┐
│ Conflict Analysis                               │
├─────────────────────────────────────────────────┤
│ Source                    Value        Date     │
├─────────────────────────────────────────────────┤
│ 📄 new_policy.txt        $3,200, 20%  Jan 2024 │
│ 📄 old_email.eml         $2,500, 15%  Nov 2023 │
└─────────────────────────────────────────────────┘
```

**Final Decision Panel:**
```
┌─────────────────────────────────────────────────┐
│ Final Decision                                  │
├─────────────────────────────────────────────────┤
│ ✓ Trusted: client_acme_corp_new_policy.txt      │
│                                                 │
│ Detailed Reason:                                │
│ The system prioritized                          │
│ 'client_acme_corp_new_policy.txt' (dated       │
│ Jan 15, 2024) as the most recent document.     │
│ Newer documents are given higher trust weight  │
│ because they are more likely to reflect        │
│ current policies, pricing, or decisions.       │
│                                                 │
│ Confidence: ████████░░ 85%                      │
└─────────────────────────────────────────────────┘
```

### CRM Ticket Output:

```
┌─────────────────────────────────────────────────┐
│ Create Support Ticket                           │
├─────────────────────────────────────────────────┤
│ Auto-populated from your last RAG query.        │
│                                                 │
│ Subject:                                        │
│ Query: According to our updated policy from...  │
│                                                 │
│ Description:                                    │
│ AI Response Summary:                            │
│ According to our updated policy from January    │
│ 2024, the Enterprise Plan is priced at         │
│ $3,200/month with a 20% annual discount...     │
│                                                 │
│ Sources referenced: client_acme_corp_new_       │
│ policy.txt, client_acme_corp_old_email.eml     │
│                                                 │
│ ⚠️ Conflicts detected: The system prioritized   │
│ 'client_acme_corp_new_policy.txt' (dated       │
│ Jan 15, 2024) as the most recent document...   │
│                                                 │
│              [Cancel]  [Submit Ticket]          │
└─────────────────────────────────────────────────┘
```

---

## Key Features Demonstrated

### 1. Autonomous CRM Ticket Auto-Fill ✅

- **No manual input required**
- Subject auto-populated from query
- Description includes full context
- Sources automatically referenced
- Conflict information included
- Editable before submission

### 2. Conflict Detection ✅

- **Automatic identification** of contradictions
- Extracts numerical values (%, $)
- Compares across sources
- Flags discrepancies
- Visual display in UI

### 3. Date-Based Prioritization ✅

- **Automatic date extraction** from documents
- Prioritizes newest documents
- Clear explanation of reasoning
- Confidence score provided
- Transparent decision-making

### 4. Explicit Reasoning ✅

- **Never silent** - always explains decisions
- Shows which source was chosen
- Explains why (date-based)
- Shows confidence level
- Displays all conflicting sources

---

## Testing Checklist

### Conflict Detection Tests

- [ ] Upload old and new documents
- [ ] Ask query that triggers both
- [ ] Verify conflict panel shows both sources
- [ ] Verify dates are extracted correctly
- [ ] Verify newest document is chosen
- [ ] Verify explanation mentions date prioritization
- [ ] Verify confidence score is 85%

### CRM Auto-Fill Tests

- [ ] Ask a question in Chat
- [ ] Wait for RAG response
- [ ] Click "Create Support Ticket"
- [ ] Verify subject is auto-populated
- [ ] Verify description includes answer
- [ ] Verify description includes sources
- [ ] Verify description includes conflict info
- [ ] Verify fields are editable
- [ ] Submit ticket successfully

### Edge Cases

- [ ] No conflicts (both documents agree)
- [ ] No dates (medium confidence 60%)
- [ ] Multiple conflicts (all detected)
- [ ] Very old vs very new (large date gap)
- [ ] Same date (first retrieved wins)

---

## Troubleshooting

### Issue: No Conflicts Detected

**Symptoms:** System says "No conflicts detected" when there should be

**Causes:**
- Documents not uploaded correctly
- Dates not extracted properly
- Values in wrong format

**Solutions:**
- Check backend logs for upload confirmation
- Verify dates are in standard format
- Ensure values use %, $ symbols

### Issue: Wrong Document Prioritized

**Symptoms:** System chooses older document instead of newer

**Causes:**
- Date extraction failed
- Newer document has no date
- Date format not recognized

**Solutions:**
- Add explicit date: "Date: January 15, 2024"
- Use standard formats: YYYY-MM-DD, MM/DD/YYYY
- Check backend logs for date extraction

### Issue: CRM Ticket Not Auto-Populated

**Symptoms:** Ticket modal opens but fields are empty

**Causes:**
- No RAG query was made
- Page was refreshed
- Global variable not set

**Solutions:**
- Ask a question in Chat first
- Don't refresh page between query and ticket
- Check console: `window.__lastRagResponse`

---

## Real-World Use Cases

### Use Case 1: Customer Service

**Scenario:** Customer calls asking about pricing

**Agent Workflow:**
1. Search for client in system
2. Ask: "What is current pricing for [Client]?"
3. System detects old email vs new policy conflict
4. System shows newest pricing with explanation
5. Agent clicks "Create Support Ticket"
6. Ticket auto-populated with full context
7. Agent adds notes and submits
8. No manual lookup required!

### Use Case 2: Billing Disputes

**Scenario:** Customer disputes refund amount

**Agent Workflow:**
1. Search for refund policy
2. Ask: "What is our refund policy?"
3. System detects 50% vs 100% conflict
4. System shows newest policy (100%)
5. Agent sees clear explanation
6. Agent confidently informs customer
7. Ticket auto-created with evidence
8. Dispute resolved quickly!

### Use Case 3: Policy Updates

**Scenario:** Multiple policy changes over time

**Agent Workflow:**
1. Ask comprehensive question
2. System detects multiple conflicts
3. System prioritizes all newest documents
4. System explains each decision
5. Agent has complete current information
6. Ticket includes all relevant context
7. No confusion about which policy applies!

---

## Summary

This mock data demonstrates a **complete autonomous CRM workflow**:

1. ✅ **No manual data entry** - System auto-fills everything
2. ✅ **Conflict detection** - Automatically identifies contradictions
3. ✅ **Date prioritization** - Always uses newest information
4. ✅ **Explicit reasoning** - Never silent, always explains
5. ✅ **Full transparency** - Shows all sources and decisions
6. ✅ **Production-ready** - Real-world scenarios and data

**The system works exactly as requested:**
- Autonomous ticket population
- Conflict detection with date prioritization
- Explicit explanations (never silent)
- No manual input required

Ready to demo! 🎉
