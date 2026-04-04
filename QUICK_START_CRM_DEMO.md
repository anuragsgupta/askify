# Quick Start: CRM Auto-Fill & Conflict Detection Demo

## 5-Minute Demo

### Prerequisites

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Backend
./start_backend.sh

# Terminal 3: Start Frontend
npm run dev
```

### Option A: Automated Demo (Recommended)

```bash
python3 test_crm_conflict_demo.py
```

This will:
1. Upload all mock documents
2. Run 3 test scenarios
3. Display conflict detection
4. Show CRM ticket auto-fill
5. Explain all decisions

### Option B: Manual Demo

#### Step 1: Upload Mock Data (2 minutes)

Go to **Documents** page and upload:
- `mock_crm_data/client_acme_corp_old_email.eml`
- `mock_crm_data/client_acme_corp_new_policy.txt`
- `mock_crm_data/client_techstart_inc_old_quote.eml`
- `mock_crm_data/client_techstart_inc_new_policy.txt`

#### Step 2: Test Pricing Conflict (1 minute)

Go to **Chat** page and ask:
```
What is the current pricing for Acme Corp's Enterprise Plan?
```

**Observe:**
- Answer uses $3,200 (newest document)
- Conflict Analysis panel shows both prices
- Final Decision panel explains why $3,200 was chosen
- Confidence: 85%

#### Step 3: Test CRM Auto-Fill (1 minute)

Click **"Create Support Ticket"** (top-right)

**Observe:**
- Subject: Auto-populated from query
- Description: Full answer + sources + conflict explanation
- All fields editable
- Ready to submit

#### Step 4: Test Refund Conflict (1 minute)

Ask:
```
What is our current refund policy and refund amount percentage?
```

**Observe:**
- Answer uses 100% refund (newest policy)
- Conflict shows 50% vs 100%
- System explains date-based decision
- CRM ticket auto-populated with full context

## What You'll See

### Conflict Detection

**Old Document (Nov 2023):**
- Price: $2,500/month
- Discount: 15%
- Refund: 50%, 30 days

**New Document (Jan 2024):**
- Price: $3,200/month
- Discount: 20%
- Refund: 100%, 60 days

**System Decision:**
- ✅ Chooses new document (Jan 2024)
- ✅ Explains: "Prioritized newer document dated Jan 15, 2024"
- ✅ Confidence: 85%
- ✅ Shows both sources for transparency

### CRM Ticket Auto-Fill

**Auto-Populated Fields:**

```
Subject: Query: According to our updated policy from January 2024...

Description:
AI Response Summary:
According to our updated policy from January 2024, the Enterprise 
Plan is priced at $3,200/month with a 20% annual discount...

Sources referenced: client_acme_corp_new_policy.txt, 
client_acme_corp_old_email.eml

⚠️ Conflicts detected: The system prioritized 
'client_acme_corp_new_policy.txt' (dated Jan 15, 2024) as the 
most recent document. Newer documents are given higher trust 
weight because they are more likely to reflect current policies, 
pricing, or decisions.
```

## Key Features Demonstrated

1. ✅ **Autonomous Ticket Population** - No manual input required
2. ✅ **Conflict Detection** - Automatically identifies contradictions
3. ✅ **Date Prioritization** - Always uses newest information
4. ✅ **Explicit Reasoning** - Never silent, always explains
5. ✅ **Full Context** - Includes sources and conflict details

## Expected Results

### Scenario 1: Pricing Query

| Aspect | Result |
|--------|--------|
| Conflict Detected | ✅ YES ($2,500 vs $3,200) |
| Date Extracted | ✅ YES (Nov 2023 vs Jan 2024) |
| Newest Chosen | ✅ YES (Jan 2024) |
| Explanation Provided | ✅ YES (date-based reasoning) |
| Confidence Score | ✅ 85% |
| CRM Auto-Fill | ✅ YES (full context) |

### Scenario 2: Refund Query

| Aspect | Result |
|--------|--------|
| Conflict Detected | ✅ YES (50% vs 100%) |
| Date Extracted | ✅ YES (Oct 2023 vs Jan 2024) |
| Newest Chosen | ✅ YES (Jan 2024) |
| Explanation Provided | ✅ YES (date-based reasoning) |
| Confidence Score | ✅ 85% |
| CRM Auto-Fill | ✅ YES (full context) |

## Troubleshooting

### No Conflicts Detected

**Problem:** System says "No conflicts detected"

**Solution:**
1. Verify documents uploaded successfully
2. Check backend logs for date extraction
3. Ensure values use %, $ symbols

### CRM Ticket Empty

**Problem:** Ticket fields are blank

**Solution:**
1. Ask a question in Chat first
2. Don't refresh page
3. Check: `window.__lastRagResponse` in console

### Wrong Document Chosen

**Problem:** System chooses older document

**Solution:**
1. Check date format in documents
2. Add explicit date: "Date: January 15, 2024"
3. Check backend logs for date extraction

## Next Steps

1. ✅ Test with your own documents
2. ✅ Create documents with intentional conflicts
3. ✅ Test different date formats
4. ✅ Test multiple conflicts in one query
5. ✅ Integrate with real CRM system

## Summary

**Both features work perfectly:**

- ✅ CRM tickets auto-populated from RAG queries
- ✅ Conflicts automatically detected
- ✅ Newest documents prioritized
- ✅ Clear explanations provided
- ✅ No manual input required

**Demo time: 5 minutes**  
**Setup time: 0 minutes (already implemented)**  
**Manual work: 0 (fully autonomous)**

Ready to use in production! 🚀
