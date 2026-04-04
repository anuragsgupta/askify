# Demo Hardcoded Queries - Quick Reference

## 🚀 Instant Response Questions

These questions return **instant responses** without waiting for LLM processing. Perfect for demos!

### 1. Support Ticket Statistics
```
what are the support ticket statistics and which clients have the most issues
```
**Shows**: 
- Overall ticket statistics (1,247 tickets, 4.2h avg resolution)
- Top 3 clients with most issues (TechStart: 127, Enterprise: 89, StartupHub: 76)
- Recommendations for each client

**Conflict**: None

---

### 2. Client Comparison (WITH CONFLICT DEMO) ⚠️
```
compare all clients by pricing, refund policy, support level, and user licenses
```
**Shows**:
- Complete comparison table (TechStart, Enterprise Corp, StartupHub)
- Pricing, refund policy, support level, user licenses
- Best value recommendation

**Conflict**: ✅ YES - Refund policy discrepancy
- TechStart contract shows "100%, 30%" (Jan 2024)
- Policy update shows "100%, 50%" (Nov 2023)
- System chose newer document
- **Perfect for demonstrating conflict detection UI!**

---

### 3. Refund Policy
```
what is the refund policy
```
**Shows**:
- Refund policies by tier (Standard, Enterprise, Starter)
- General terms and processing time
- Best refund protection recommendation

**Conflict**: None

---

### 4. TechStart Pricing
```
what is the pricing for techstart
```
**Shows**:
- Monthly subscription ($1,000/month)
- What's included (50 users, Premium support, API access)
- Additional costs (extra users, API calls, storage)
- Setup fees and contract terms

**Conflict**: None

---

### 5. Enterprise Corp Licenses
```
how many user licenses does enterprise corp have
```
**Shows**:
- Current license count (200 users)
- Active users (187, 93.5% utilization)
- Usage trends and recommendations
- Upgrade suggestions

**Conflict**: None

---

### 6. TechStart Contract Renewal (WITH CONFLICT DEMO) ⚠️
```
what is the contract renewal date for techstart solutions
```
**Shows**:
- Current contract renewal date (Jan 1, 2025)
- Contract type and auto-renewal settings
- Renewal options and important dates
- Cancellation terms

**Conflict**: ✅ YES - Renewal date discrepancy
- Original contract shows "January 15, 2025" (Jan 2024)
- Contract amendment shows "January 1, 2025" (Dec 2024)
- System chose amendment (supersedes original)
- **Demonstrates temporal authority scoring!**

---

### 7. Enterprise Corp Support SLA (WITH CONFLICT DEMO) ⚠️
```
what is the support response time for enterprise corp
```
**Shows**:
- Current SLA response times (P1: 15 min, P2: 2 hrs, P3: 8 hrs, P4: 24 hrs)
- Support coverage (24/7, dedicated team)
- Actual performance vs SLA (98.5% compliance)
- Resolution times by priority

**Conflict**: ✅ YES - P1 response time discrepancy
- Original agreement shows "30 minutes" (Dec 2023)
- Service upgrade shows "15 minutes" (Nov 2024)
- System chose upgrade (service improvements override)
- **Shows how upgrades supersede original terms!**

---

### 8. StartupHub API Limits (WITH CONFLICT DEMO) ⚠️
```
what are the api rate limits for startuphub
```
**Shows**:
- Current API limits (5,000 calls/month, 100 req/min)
- Usage breakdown (3,847 calls, 77% utilization)
- Overage pricing and upgrade options
- Rate limit handling

**Conflict**: ✅ YES - Monthly API call limit discrepancy
- Original terms show "3,000 calls/month" (Mar 2024)
- Capacity increase shows "5,000 calls/month" (Oct 2024)
- System chose capacity increase (permanent enhancement)
- **Demonstrates capacity upgrade handling!**

---

## 💡 Demo Tips

### For Speed Demo
Use any of the 8 questions above to show instant responses (no LLM wait time).

### For Conflict Detection Demo
**Use questions #2, #6, #7, or #8** to demonstrate:
1. **Question #2** (Client Comparison) - Refund policy conflict
2. **Question #6** (TechStart Renewal) - Contract amendment superseding original
3. **Question #7** (Enterprise SLA) - Service upgrade improving response time
4. **Question #8** (StartupHub API) - Capacity increase overriding original limit

All show:
- Conflict detection system
- Source citation with conflicting values
- "Flag for Review" button
- Expandable source details
- Resolution explanation with temporal authority scoring

### For Source Citation Demo
All 8 questions show proper source citations with:
- Source name and type (PDF, Excel)
- Location (page, sheet, row)
- Relevance scores
- Text excerpts

---

## 🔧 Technical Details

- **Response Time**: Instant (< 50ms)
- **Caching**: Responses are cached after first query
- **Fallback**: If no match, proceeds with normal RAG pipeline
- **Matching**: Case-insensitive exact match + 50% fuzzy match threshold
- **Total Hardcoded Queries**: 8 (4 with conflicts, 4 without)

---

## 📝 Adding More Hardcoded Responses

Edit `server/services/hardcoded_responses.py` and add to `HARDCODED_RESPONSES` dict:

```python
"your question here": {
    "answer": "...",
    "sources": [...],
    "conflict_analysis": {...},
    "llm_used": "gemini",
    "avg_relevance": 0.95
}
```

Restart server to apply changes.
