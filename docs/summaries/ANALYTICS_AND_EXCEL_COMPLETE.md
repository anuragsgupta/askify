# Analytics System & Excel Mock Data - Complete ✅

## Summary
Successfully implemented:
1. ✅ Mock Excel files with conflicting data
2. ✅ System Analytics module with RAG performance tracking
3. ✅ Knowledge Graph visualization showing document connections

---

## Part 1: Mock Excel Files ✅

### Files Created

**1. client_pricing_sheet.xlsx**
- Contains pricing data for 4 clients
- Includes old vs new pricing (conflicts)
- Sheets: "Pricing", "Summary"
- Conflicts: Acme Corp ($2,500 → $3,200), TechStart Inc ($1,200 → $1,500)

**2. support_tickets_database.xlsx**
- 20 realistic support tickets
- Ticket tracking with response/resolution times
- Sheets: "Tickets", "Statistics"
- Includes priority levels, status, customer satisfaction

**3. product_features_matrix.xlsx**
- Feature comparison across 4 plans (Basic, Standard, Premium, Enterprise)
- 12 features with availability matrix
- Sheets: "Features", "Pricing"
- Shows feature availability and pricing tiers

**4. refund_policy_details.xlsx**
- Refund policies for all clients
- Old vs new policies (conflicts)
- Sheets: "Refund Policies", "Notes"
- Conflicts: Acme Corp (50% → 100%), TechStart Inc (30% → 75%)

### How to Upload

```bash
# Upload all Excel files
python3 ingest_demo_data.py mock_crm_data/
```

### Expected Behavior

When you query:
- **"What is the pricing for Acme Corp?"**
  - Returns data from BOTH email and Excel
  - Detects conflict: $2,500 (old) vs $3,200 (new)
  - Prioritizes Excel data (more recent)

- **"What is the refund policy?"**
  - Returns data from BOTH text files and Excel
  - Detects conflict: 50% vs 100%
  - Shows all sources with badges

- **"Show me support ticket statistics"**
  - Returns data from Excel sheets
  - Shows ticket counts, response times, satisfaction scores

---

## Part 2: System Analytics Module ✅

### Features Implemented

#### 1. Query Analytics Tracking
- **What**: Tracks every RAG query with performance metrics
- **Metrics**:
  - Query text
  - Response time (ms)
  - Number of sources retrieved
  - Average relevance score
  - Conflict detection (yes/no)
  - LLM provider used (Gemini/Ollama)
  - Timestamp

#### 2. Hallucination Detection
- **What**: Automatically detects potential hallucinations
- **Indicators**:
  - Missing citations ([Source N])
  - Low citation count (< 2)
  - Low confidence score (< 0.6)
- **Flagging**: Automatically flags suspicious responses

#### 3. Search Topics Tracking
- **What**: Tracks popular search topics
- **Features**:
  - Extracts key topics from queries
  - Counts frequency
  - Shows trending topics
  - Last searched timestamp

#### 4. Knowledge Graph
- **What**: Tracks document co-occurrence
- **Features**:
  - Documents that appear together in queries
  - Connection strength (co-occurrence count)
  - Shared topics
  - Visual graph representation

### Database Schema

**query_analytics table**:
```sql
- id (PRIMARY KEY)
- query_text
- response_time_ms
- num_sources
- avg_relevance
- has_conflicts
- llm_used
- timestamp
```

**hallucination_checks table**:
```sql
- id (PRIMARY KEY)
- query_id (FOREIGN KEY)
- has_citations
- citation_count
- confidence_score
- flagged_as_hallucination
- timestamp
```

**search_topics table**:
```sql
- id (PRIMARY KEY)
- topic
- query_count
- last_searched
```

**document_connections table**:
```sql
- id (PRIMARY KEY)
- source_doc
- target_doc
- connection_strength
- shared_topics
- co_occurrence_count
- last_connected
```

### API Endpoints

**GET /api/analytics/summary?days=7**
- Returns analytics summary for specified time period
- Metrics: total queries, avg response time, avg relevance, conflict rate, hallucination rate
- Charts: queries over time, LLM usage distribution
- Topics: top 10 search topics

**GET /api/analytics/knowledge-graph**
- Returns knowledge graph data
- Nodes: documents
- Edges: connections with strength and count

---

## Part 3: Analytics Dashboard UI ✅

### Features

#### Overview Tab
- **Key Metrics Cards**:
  - Total Queries
  - Average Relevance (with quality indicator)
  - Average Response Time
  - Hallucination Rate (with risk indicator)

- **Charts**:
  - Queries Over Time (bar chart)
  - LLM Provider Usage (pie chart)

- **Performance Indicators**:
  - Conflict Detection Rate (progress bar)
  - Citation Quality (progress bar)
  - Average Relevance Score (progress bar)

#### Search Topics Tab
- **Popular Topics List**:
  - Ranked by frequency
  - Visual bar chart
  - Search count for each topic
  - Hover effects

#### Knowledge Graph Tab
- **Visual Graph**:
  - Document nodes (circles)
  - Connection lines
  - Node labels
  - Connection counts

- **Graph Statistics**:
  - Total documents
  - Total connections
  - Average co-occurrence

### Time Range Selector
- 7 Days (default)
- 30 Days
- 90 Days

### Navigation
- Added "Analytics" to sidebar
- Icon: TrendingUp
- Route: `/analytics`

---

## How It Works

### 1. Query Tracking Flow

```
User asks question
    ↓
RAG pipeline processes query
    ↓
Analytics service logs:
  - Query text
  - Response time
  - Sources retrieved
  - Relevance scores
  - Conflicts detected
  - LLM used
    ↓
Hallucination check:
  - Count citations
  - Check confidence
  - Flag if suspicious
    ↓
Document connections:
  - Track co-occurrence
  - Update graph
    ↓
Dashboard displays metrics
```

### 2. Hallucination Detection Logic

```python
# Flag as potential hallucination if:
flagged = (
    not has_citations OR
    (citation_count < 2 AND confidence_score < 0.6)
)
```

**Examples**:
- ✅ Good: "According to [Source 1], the pricing is $3,200 [Source 2]."
- ❌ Flagged: "The pricing is $3,200." (no citations)
- ❌ Flagged: "Based on [Source 1], the pricing is $3,200." (only 1 citation, low confidence)

### 3. Knowledge Graph Building

```python
# When documents appear together in a query:
for each pair of documents:
    if connection exists:
        increment co_occurrence_count
        increase connection_strength
    else:
        create new connection
        set initial strength = 0.5
```

**Example**:
- Query: "Acme Corp pricing and refund policy"
- Documents retrieved:
  - client_acme_corp_old_email.eml
  - client_acme_corp_new_policy.txt
  - client_pricing_sheet.xlsx
  - refund_policy_details.xlsx
- Connections created:
  - old_email ↔ new_policy
  - old_email ↔ pricing_sheet
  - old_email ↔ refund_policy
  - new_policy ↔ pricing_sheet
  - new_policy ↔ refund_policy
  - pricing_sheet ↔ refund_policy

---

## Testing

### 1. Upload Mock Excel Files

```bash
python3 create_mock_excel.py
python3 ingest_demo_data.py mock_crm_data/
```

### 2. Ask Test Queries

**Query 1**: "What is the pricing for Acme Corp?"
- **Expected**: Data from email + Excel
- **Expected**: Conflict detected ($2,500 vs $3,200)
- **Expected**: Analytics logged

**Query 2**: "What is the refund policy?"
- **Expected**: Data from text + Excel
- **Expected**: Conflict detected (50% vs 100%)
- **Expected**: Analytics logged

**Query 3**: "Show me support ticket statistics"
- **Expected**: Data from Excel only
- **Expected**: Ticket counts and metrics
- **Expected**: Analytics logged

### 3. Check Analytics Dashboard

1. Navigate to `/analytics`
2. Verify metrics are displayed:
   - Total queries > 0
   - Average relevance > 0
   - Charts populated
3. Check Search Topics tab
4. Check Knowledge Graph tab

### 4. Verify Database

```bash
sqlite3 server/askify.db

# Check query analytics
SELECT * FROM query_analytics ORDER BY timestamp DESC LIMIT 5;

# Check hallucination checks
SELECT * FROM hallucination_checks ORDER BY timestamp DESC LIMIT 5;

# Check search topics
SELECT * FROM search_topics ORDER BY query_count DESC LIMIT 10;

# Check document connections
SELECT * FROM document_connections ORDER BY connection_strength DESC LIMIT 10;
```

---

## Files Created/Modified

### Backend
1. ✅ `server/services/analytics.py` - Analytics tracking service
2. ✅ `server/routes/analytics.py` - Analytics API endpoints
3. ✅ `server/services/rag.py` - Added analytics integration
4. ✅ `server/main.py` - Registered analytics router

### Frontend
1. ✅ `src/pages/Analytics.jsx` - Analytics dashboard component
2. ✅ `src/pages/Analytics.css` - Analytics styling
3. ✅ `src/App.jsx` - Added Analytics route
4. ✅ `src/components/layout/Sidebar.jsx` - Added Analytics link

### Mock Data
1. ✅ `create_mock_excel.py` - Excel file generator
2. ✅ `mock_crm_data/client_pricing_sheet.xlsx`
3. ✅ `mock_crm_data/support_tickets_database.xlsx`
4. ✅ `mock_crm_data/product_features_matrix.xlsx`
5. ✅ `mock_crm_data/refund_policy_details.xlsx`

### Documentation
1. ✅ `ANALYTICS_AND_EXCEL_COMPLETE.md` - This file

---

## Key Metrics to Monitor

### Quality Metrics
- **Average Relevance**: Target 75-80%+
- **Hallucination Rate**: Target < 10%
- **Citation Quality**: Target > 90%

### Performance Metrics
- **Response Time**: Target < 2000ms
- **Conflict Detection Rate**: Varies by data
- **LLM Usage**: Monitor Gemini vs Ollama

### Usage Metrics
- **Total Queries**: Growth indicator
- **Popular Topics**: User interests
- **Document Connections**: Knowledge coverage

---

## Troubleshooting

### Issue: No analytics data showing

**Solution**:
1. Ask some questions in the chat
2. Wait a few seconds
3. Refresh analytics page
4. Check database: `sqlite3 server/askify.db "SELECT COUNT(*) FROM query_analytics;"`

### Issue: Knowledge graph empty

**Solution**:
1. Ask questions that reference multiple documents
2. Example: "Compare Acme Corp pricing across all documents"
3. This will create document connections

### Issue: Hallucination rate too high

**Possible causes**:
1. LLM not citing sources properly
2. Low relevance scores
3. Insufficient context

**Solutions**:
1. Improve prompt engineering
2. Increase MIN_RELEVANCE_SCORE
3. Upload more relevant documents

---

## Future Enhancements (Optional)

### Phase 2 Features
1. **Advanced Visualizations**:
   - Interactive knowledge graph (D3.js, Cytoscape.js)
   - Time-series charts (Chart.js, Recharts)
   - Heatmaps for query patterns

2. **Real-time Monitoring**:
   - WebSocket updates
   - Live query feed
   - Alert system for high hallucination rate

3. **Export Functionality**:
   - Export analytics as PDF/CSV
   - Scheduled reports
   - Email notifications

4. **Advanced Analytics**:
   - Query clustering
   - Semantic similarity analysis
   - User behavior patterns
   - A/B testing for prompts

5. **Machine Learning**:
   - Anomaly detection
   - Predictive analytics
   - Auto-tuning relevance thresholds

---

## Status: ✅ COMPLETE

All features implemented and ready for use:
- ✅ Mock Excel files with conflicts
- ✅ Analytics tracking system
- ✅ Hallucination detection
- ✅ Knowledge graph
- ✅ Analytics dashboard UI
- ✅ API endpoints
- ✅ Database schema

**Ready for production use!** 🎉

### Quick Start
1. Create mock Excel files: `python3 create_mock_excel.py`
2. Upload files: `python3 ingest_demo_data.py mock_crm_data/`
3. Ask questions in chat
4. View analytics at `/analytics`
5. Monitor performance and quality metrics!
