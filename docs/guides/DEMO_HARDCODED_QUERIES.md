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

## 💡 Demo Tips

### For Speed Demo
Use any of the 5 questions above to show instant responses (no LLM wait time).

### For Conflict Detection Demo
**Use question #2** (client comparison) to demonstrate:
1. Conflict detection system
2. Source citation with conflicting values
3. "Flag for Review" button
4. Expandable source details
5. Resolution explanation (newer document chosen)

### For Source Citation Demo
All 5 questions show proper source citations with:
- Source name and type (PDF, Excel)
- Location (page, sheet, row)
- Relevance scores
- Text excerpts

---

## 🔧 Technical Details

- **Response Time**: Instant (< 50ms)
- **Caching**: Responses are cached after first query
- **Fallback**: If no match, proceeds with normal RAG pipeline
- **Matching**: Case-insensitive exact match + 60% fuzzy match

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
