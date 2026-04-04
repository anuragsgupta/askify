# CRM Auto-Fill & Conflict Detection - Complete Workflow

## Visual Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT SEARCHES FOR CLIENT                    │
│                                                                 │
│  Agent Query: "What is current pricing for Acme Corp?"         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RAG SYSTEM RETRIEVES DOCS                    │
│                                                                 │
│  📄 client_acme_corp_old_email.eml (Nov 2023)                  │
│     - Price: $2,500/month                                      │
│     - Discount: 15%                                            │
│                                                                 │
│  📄 client_acme_corp_new_policy.txt (Jan 2024)                 │
│     - Price: $3,200/month                                      │
│     - Discount: 20%                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CONFLICT DETECTION MODULE                     │
│                                                                 │
│  Step 1: Group by source document                              │
│  Step 2: Extract dates (Nov 2023 vs Jan 2024)                  │
│  Step 3: Extract values ($2,500 vs $3,200, 15% vs 20%)         │
│  Step 4: Compare values → CONFLICT DETECTED!                   │
│  Step 5: Prioritize by date → Jan 2024 wins                    │
│  Step 6: Generate explanation                                  │
│  Step 7: Calculate confidence → 85%                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LLM GENERATES ANSWER                         │
│                                                                 │
│  "According to our updated policy from January 2024, the       │
│   Enterprise Plan is priced at $3,200/month with a 20%         │
│   annual discount. This pricing supersedes the previous        │
│   $2,500/month rate from November 2023."                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DISPLAY IN CHAT UI                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Chat Answer                                             │   │
│  │ According to our updated policy from January 2024...    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Conflict Analysis                                       │   │
│  │ ┌─────────────────────────────────────────────────────┐ │   │
│  │ │ Source              Value        Date               │ │   │
│  │ ├─────────────────────────────────────────────────────┤ │   │
│  │ │ 📄 new_policy.txt  $3,200, 20%  Jan 15, 2024       │ │   │
│  │ │ 📄 old_email.eml   $2,500, 15%  Nov 15, 2023       │ │   │
│  │ └─────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Final Decision                                          │   │
│  │ ✓ Trusted: client_acme_corp_new_policy.txt             │   │
│  │                                                         │   │
│  │ Reasoning: The system prioritized                      │   │
│  │ 'client_acme_corp_new_policy.txt' (dated Jan 15,       │   │
│  │ 2024) as the most recent document. Newer documents     │   │
│  │ are given higher trust weight...                       │   │
│  │                                                         │   │
│  │ Confidence: ████████░░ 85%                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  STORE CONTEXT GLOBALLY                         │
│                                                                 │
│  window.__lastRagResponse = {                                  │
│    answer: "According to our updated policy...",               │
│    sources: [...],                                             │
│    conflict_analysis: {...}                                    │
│  }                                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENT CLICKS "CREATE SUPPORT TICKET"               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CRM TICKET AUTO-POPULATION                     │
│                                                                 │
│  Step 1: Read window.__lastRagResponse                         │
│  Step 2: Extract answer (first 60 chars for subject)           │
│  Step 3: Extract sources                                       │
│  Step 4: Extract conflict information                          │
│  Step 5: Format description                                    │
│  Step 6: Populate modal fields                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DISPLAY CRM MODAL                            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Create Support Ticket                                   │   │
│  │                                                         │   │
│  │ Auto-populated from your last RAG query.               │   │
│  │                                                         │   │
│  │ Subject:                                               │   │
│  │ ┌─────────────────────────────────────────────────────┐ │   │
│  │ │ Query: According to our updated policy from...      │ │   │
│  │ └─────────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │ Description:                                           │   │
│  │ ┌─────────────────────────────────────────────────────┐ │   │
│  │ │ AI Response Summary:                                │ │   │
│  │ │ According to our updated policy from January        │ │   │
│  │ │ 2024, the Enterprise Plan is priced at             │ │   │
│  │ │ $3,200/month with a 20% annual discount...         │ │   │
│  │ │                                                     │ │   │
│  │ │ Sources referenced: client_acme_corp_new_          │ │   │
│  │ │ policy.txt, client_acme_corp_old_email.eml         │ │   │
│  │ │                                                     │ │   │
│  │ │ ⚠️ Conflicts detected: The system prioritized       │ │   │
│  │ │ 'client_acme_corp_new_policy.txt' (dated           │ │   │
│  │ │ Jan 15, 2024) as the most recent document...       │ │   │
│  │ └─────────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │              [Cancel]  [Submit Ticket]                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AGENT REVIEWS & EDITS                         │
│                                                                 │
│  ✓ Subject looks good                                          │
│  ✓ Description has full context                                │
│  ✓ Sources are referenced                                      │
│  ✓ Conflict explanation included                               │
│  + Agent adds: "Customer satisfied with explanation"           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT SUBMITS TICKET                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUCCESS CONFIRMATION                         │
│                                                                 │
│  ✅ Support Ticket Created Successfully!                        │
└─────────────────────────────────────────────────────────────────┘
```

## Key Decision Points

### Conflict Detection Decision Tree

```
Document Retrieved
       │
       ▼
   Has Date?
       │
       ├─ YES ──┐
       │        ▼
       │   Extract Date
       │        │
       │        ▼
       │   Compare Dates
       │        │
       │        ├─ Newer ──> Prioritize (85% confidence)
       │        │
       │        └─ Older ──> Deprioritize
       │
       └─ NO ───┐
                ▼
           Use Retrieval Order
                │
                ▼
           First Retrieved
                │
                ▼
           Medium Confidence (60%)
```

### CRM Auto-Fill Decision Tree

```
Agent Clicks "Create Support Ticket"
       │
       ▼
   Check window.__lastRagResponse
       │
       ├─ EXISTS ──┐
       │           ▼
       │      Extract Data
       │           │
       │           ├─ Answer → Subject (60 chars)
       │           ├─ Answer → Description (300 chars)
       │           ├─ Sources → Description
       │           └─ Conflicts → Description
       │           │
       │           ▼
       │      Auto-Populate Fields
       │           │
       │           ▼
       │      Show "Auto-populated" Message
       │
       └─ NOT EXISTS ──┐
                       ▼
                  Show Empty Fields
                       │
                       ▼
                  Show "No RAG context" Message
```

## Data Flow

### Information Flow Through System

```
┌──────────────┐
│   Documents  │
│  (Old & New) │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Parsing    │
│  & Chunking  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Embeddings  │
│  Generation  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Vector DB   │
│   Storage    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ User Query   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Retrieval  │
│  (Top 10)    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Conflict   │
│  Detection   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     LLM      │
│  Generation  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  UI Display  │
│  + Storage   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ CRM Ticket   │
│  Auto-Fill   │
└──────────────┘
```

## Timeline View

### Complete Workflow Timeline

```
Time    Action                          System Component
────────────────────────────────────────────────────────────
0:00    Agent asks question             Frontend (Chat)
0:01    Query sent to backend           API (/api/query)
0:02    Embed query                     Embeddings Service
0:03    Search vector DB                ChromaDB
0:04    Retrieve top 10 chunks          Vector Store
0:05    Group by source                 Conflict Detection
0:06    Extract dates                   Conflict Detection
0:07    Extract values                  Conflict Detection
0:08    Compare values                  Conflict Detection
0:09    Detect conflicts                Conflict Detection
0:10    Prioritize by date              Conflict Detection
0:11    Generate explanation            Conflict Detection
0:12    Build prompt                    RAG Service
0:13    Call LLM                        Ollama/Gemini
0:14    Generate answer                 LLM
0:15    Format response                 RAG Service
0:16    Return to frontend              API Response
0:17    Display answer                  Chat UI
0:18    Display conflicts               Conflict Panel
0:19    Display decision                Decision Panel
0:20    Store context                   window.__lastRagResponse
────────────────────────────────────────────────────────────
        [Agent clicks "Create Support Ticket"]
────────────────────────────────────────────────────────────
0:21    Read stored context             TopBar Component
0:22    Extract answer                  Auto-Fill Logic
0:23    Extract sources                 Auto-Fill Logic
0:24    Extract conflicts               Auto-Fill Logic
0:25    Format subject                  Auto-Fill Logic
0:26    Format description              Auto-Fill Logic
0:27    Populate fields                 Modal Component
0:28    Display modal                   UI
────────────────────────────────────────────────────────────
        [Agent reviews and submits]
────────────────────────────────────────────────────────────
0:29    Submit ticket                   Frontend
0:30    Show success                    UI
────────────────────────────────────────────────────────────
Total Time: 30 seconds (fully autonomous)
```

## Summary

**Complete autonomous workflow:**

1. ✅ Agent searches (1 action)
2. ✅ System retrieves documents (automatic)
3. ✅ System detects conflicts (automatic)
4. ✅ System prioritizes by date (automatic)
5. ✅ System explains reasoning (automatic)
6. ✅ System displays results (automatic)
7. ✅ Agent clicks ticket button (1 action)
8. ✅ System auto-fills ticket (automatic)
9. ✅ Agent reviews and submits (1 action)

**Total agent actions: 3**  
**Total system actions: 20+**  
**Manual data entry: 0**  
**Time saved: 10+ minutes per query**

🎉 **Fully autonomous CRM workflow!**
