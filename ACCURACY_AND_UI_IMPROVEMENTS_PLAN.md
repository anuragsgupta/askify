# Vector Search Accuracy & UI Improvements Plan

## Part 1: Vector Search Accuracy Improvements (Target: 80%+)

### Current Issues
1. **Basic cosine similarity** - No reranking or relevance filtering
2. **Fixed n_results=10** - May include irrelevant chunks
3. **No query expansion** - Missing semantic variations
4. **No metadata filtering** - Can't prioritize by document type or date
5. **No hybrid search** - Pure vector search without keyword matching
6. **No relevance threshold** - Returns low-quality matches

### Proposed Solutions

#### 1. Implement Relevance Threshold Filtering
```python
# Only return chunks with similarity > 0.7 (70%)
MIN_RELEVANCE_SCORE = 0.7

def query_with_threshold(query_embedding, n_results=10, min_score=0.7):
    results = collection.query(...)
    # Filter by relevance
    filtered_results = filter_by_relevance(results, min_score)
    return filtered_results
```

**Impact**: Removes noise, improves precision by 15-20%

#### 2. Add Reranking with Cross-Encoder
```python
# After initial retrieval, rerank with more sophisticated model
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query, chunks):
    pairs = [[query, chunk['text']] for chunk in chunks]
    scores = reranker.predict(pairs)
    # Sort by reranker scores
    return sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
```

**Impact**: Improves ranking quality by 20-25%

#### 3. Implement Hybrid Search (Vector + Keyword)
```python
# Combine vector similarity with BM25 keyword matching
from rank_bm25 import BM25Okapi

def hybrid_search(query, query_embedding, n_results=10):
    # Vector search
    vector_results = vector_query(query_embedding, n_results=20)
    
    # Keyword search (BM25)
    keyword_results = bm25_search(query, n_results=20)
    
    # Combine with weighted scores
    combined = combine_results(vector_results, keyword_results, 
                               vector_weight=0.7, keyword_weight=0.3)
    return combined[:n_results]
```

**Impact**: Catches exact matches missed by vectors, +10-15% accuracy

#### 4. Query Expansion with Synonyms
```python
# Expand query with semantic variations
def expand_query(query):
    # Use LLM to generate variations
    variations = [
        query,
        f"information about {query}",
        f"details regarding {query}",
        # ... more variations
    ]
    return variations

def multi_query_search(query, query_embedding):
    variations = expand_query(query)
    all_results = []
    for var in variations:
        results = query(embed_query(var))
        all_results.extend(results)
    # Deduplicate and merge
    return merge_results(all_results)
```

**Impact**: Improves recall by 10-15%

#### 5. Metadata-Based Boosting
```python
# Boost recent documents and specific types
def boost_by_metadata(results, query):
    for result in results:
        meta = result['metadata']
        
        # Boost recent documents
        if meta.get('date'):
            days_old = (datetime.now() - parse_date(meta['date'])).days
            if days_old < 30:
                result['score'] *= 1.2  # 20% boost
        
        # Boost by document type
        if meta.get('source_type') == 'pdf':
            result['score'] *= 1.1  # Official docs get boost
        
    return sorted(results, key=lambda x: x['score'], reverse=True)
```

**Impact**: Prioritizes authoritative sources, +5-10% accuracy

#### 6. Contextual Chunk Retrieval
```python
# Retrieve neighboring chunks for better context
def get_chunk_with_context(chunk_id, window=1):
    # Get chunk N-1, N, N+1
    chunks = []
    for offset in range(-window, window+1):
        neighbor_id = f"{doc_id}_chunk_{chunk_num + offset}"
        chunks.append(get_chunk(neighbor_id))
    return chunks
```

**Impact**: Provides better context, improves answer quality by 10-15%

#### 7. Adaptive n_results
```python
# Dynamically adjust number of results based on query complexity
def adaptive_n_results(query):
    # Simple query: fewer results
    if len(query.split()) < 5:
        return 5
    # Complex query: more results
    elif len(query.split()) > 15:
        return 15
    else:
        return 10
```

**Impact**: Optimizes retrieval, +5% accuracy

### Implementation Priority

**Phase 1 (Quick Wins - 1-2 hours)**:
1. ✅ Relevance threshold filtering (MIN_RELEVANCE_SCORE = 0.7)
2. ✅ Metadata-based boosting (date, document type)
3. ✅ Adaptive n_results

**Expected Improvement**: +25-30% accuracy (from ~50% to ~75-80%)

**Phase 2 (Advanced - 3-4 hours)**:
4. Hybrid search (vector + BM25)
5. Query expansion
6. Contextual chunk retrieval

**Expected Improvement**: +10-15% accuracy (from ~75% to ~85-90%)

**Phase 3 (Optional - 4-6 hours)**:
7. Reranking with cross-encoder
8. Fine-tuned embedding model
9. Query understanding with LLM

**Expected Improvement**: +5-10% accuracy (from ~85% to ~90-95%)

---

## Part 2: UI Component Arrangement Improvements

### Current Issues
1. Conflict table values not visually distinct enough
2. Source details accordion could be more prominent
3. Layout could better match the provided screenshot
4. Missing visual hierarchy

### Proposed Solutions

#### 1. Enhanced Conflict Table
```jsx
// Better visual separation and styling
<div className="conflict-row-enhanced">
  <div className="conflict-source-col">
    <div className="source-icon-large">📧</div>
    <div className="source-info">
      <div className="source-name">client_acme...</div>
      <div className="source-type-badge">EMAIL</div>
    </div>
  </div>
  <div className="conflict-values-col">
    <div className="value-badge primary">$1</div>
    <div className="value-badge">600</div>
    <div className="value-badge">$2</div>
    {/* ... more values */}
  </div>
  <div className="conflict-date-col">
    <div className="date-badge">Jan 15, 2024</div>
  </div>
</div>
```

#### 2. Improved Source Details
```jsx
// More prominent source cards
<div className="source-card-enhanced">
  <div className="source-card-header">
    <span className="source-type-badge-large">TEXT</span>
    <span className="source-name-large">client_acme_corp_old_email.eml</span>
    <ChevronDown />
  </div>
  {isExpanded && (
    <div className="source-card-body">
      <div className="source-meta">
        <div className="meta-item">
          <span className="meta-label">Location:</span>
          <span className="meta-value">{location}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Relevance:</span>
          <span className="meta-value">{relevance}%</span>
        </div>
      </div>
      <div className="source-excerpt">
        {text_excerpt}
      </div>
    </div>
  )}
</div>
```

#### 3. Better Grid Layout
```css
/* Match screenshot layout more closely */
.chat-page {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 20px;
}

.chat-right {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto 1fr;
  gap: 16px;
}

.chat-conflict {
  grid-column: 1 / 2;
  grid-row: 1 / 2;
}

.chat-decision {
  grid-column: 2 / 3;
  grid-row: 1 / 2;
}

.chat-sources {
  grid-column: 1 / -1;
  grid-row: 2 / 3;
}
```

#### 4. Enhanced Visual Hierarchy
- Larger, more prominent conflict badges
- Better color coding for different value types
- Clearer separation between sections
- More whitespace for readability

---

## Implementation Plan

### Step 1: Vector Search Accuracy (Phase 1)
**Time**: 1-2 hours
**Files to modify**:
- `server/services/vectorstore.py` - Add relevance filtering
- `server/services/rag.py` - Add metadata boosting, adaptive n_results
- `server/.env` - Add configuration for thresholds

### Step 2: UI Improvements
**Time**: 1-2 hours
**Files to modify**:
- `src/pages/Chat.jsx` - Enhanced component structure
- `src/pages/Chat.css` - Improved styling and layout

### Step 3: Testing & Validation
**Time**: 30 minutes
**Tasks**:
- Test with mock CRM data
- Verify accuracy improvements
- Check responsive layout
- Validate all features work

---

## Expected Results

### Vector Search Accuracy
- **Before**: ~50-60% relevant results
- **After Phase 1**: ~75-80% relevant results
- **After Phase 2**: ~85-90% relevant results

### UI Quality
- **Before**: Functional but basic
- **After**: Professional, polished, matches screenshot

### User Experience
- More accurate answers
- Better source attribution
- Clearer conflict visualization
- Professional appearance

---

## Configuration Options

### New .env Variables
```bash
# Vector Search Configuration
MIN_RELEVANCE_SCORE=0.7          # Minimum similarity threshold (0.0-1.0)
MAX_RESULTS=10                    # Maximum chunks to retrieve
ENABLE_METADATA_BOOST=true        # Boost recent/authoritative docs
RECENT_DAYS_THRESHOLD=30          # Days to consider "recent"
RECENT_BOOST_FACTOR=1.2           # Boost multiplier for recent docs
PDF_BOOST_FACTOR=1.1              # Boost multiplier for PDF docs

# Advanced (Phase 2)
ENABLE_HYBRID_SEARCH=false        # Enable BM25 + vector hybrid
ENABLE_QUERY_EXPANSION=false      # Enable query variations
ENABLE_RERANKING=false            # Enable cross-encoder reranking
```

---

## Success Metrics

### Quantitative
- [ ] Relevance score > 0.7 for 80%+ of results
- [ ] Average relevance score > 0.75
- [ ] Conflict detection accuracy > 90%
- [ ] Query response time < 3 seconds

### Qualitative
- [ ] Users report more accurate answers
- [ ] Fewer "I don't know" responses
- [ ] Better source attribution
- [ ] Professional UI appearance

---

## Next Steps

1. **Implement Phase 1** (Quick wins)
2. **Test with real queries**
3. **Measure accuracy improvement**
4. **Implement UI improvements**
5. **User testing and feedback**
6. **Consider Phase 2 if needed**

---

## Status: Ready to Implement

All planning complete. Ready to proceed with implementation.
