# 🎯 Implementation Quick Reference

## What's Already Done ✅
- Query enrichment (context for follow-ups)
- Product carousel + IRRELEVANT handling
- Conversation isolation per user
- Smart display name sanitization
- Retrieval confidence interpretation
- Enhanced system prompt with context

---

## Next 5 Actions (by effort/impact)

### 1️⃣ Better Embedding Model `[30 min]`
**File:** `apps/api/app/core/config.py:90`  
**Change:** `"sentence-transformers/all-MiniLM-L6-v2"` → `"BAAI/bge-small-en-v1.5"`  
**Why:** 15-25% better RAG quality, same speed  
**Then:** Re-embed all knowledge base  

---

### 2️⃣ Semantic Caching `[2 hours]`
**Files:** Create `apps/api/app/services/cache_service.py` + modify `chat_service.py:1450`  
**Logic:**
```python
# Before LLM call
cache_key = f"qa:{embedding_hash}"
if similar_response_cached(cache_key, min_sim=0.98):
    return cached_response
# After LLM call
cache.set(cache_key, response)
```
**Why:** 60-70% faster for repeated questions, cut LLM costs  

---

### 3️⃣ Query Expansion `[1 hour]`
**File:** `apps/api/app/services/chat_service.py:~900`  
**Logic:**
```python
SYNONYMS = {
    "shirt": ["top", "tee", "t-shirt"],
    "buy": ["purchase", "order", "get"]
}
expanded = query + " " + " ".join(get_synonyms(query))
embedding = await get_single_embedding(expanded)
```
**Why:** 10-15% better recall for product queries  

---

### 4️⃣ Hybrid Search (BM25 + Vector) `[3 hours]`
**File:** `apps/api/app/services/chat_service.py:1240`  
**Logic:**
```python
# 1. Vector search (existing)
vector_results = top_20_by_cosine_distance()
# 2. BM25 keyword search (new)
bm25_results = db.execute(ts_rank_query(query))
# 3. Combine scores: 60% vector + 40% BM25
combined = [(vec + 0.67 * bm25) for vec, bm25 in merge()]
```
**Why:** Catch exact product names, SKUs, model numbers  

---

### 5️⃣ Enable HNSW Indexing ⚠️ CRITICAL `[10 min]`
**File:** `apps/api/alembic/versions/006_add_embeddings.py`  
**Action:** Uncomment HNSW index creation  
**Then:** `alembic upgrade head`  
**Why:** 50-70% faster queries (O(log n) vs O(n))  
**Impact:** Immediate performance gain for 10k+ documents  

---

## Advanced (Next Month)

| # | Feature | File | Effort | Impact |
|---|---------|------|--------|--------|
| 6 | Cross-encoder re-ranking | `chat_service.py:1240` | 🔴 3h | 20-30% better relevance |
| 7 | Playwright JS crawler | `crawler_service.py:345` | 🔴 4h | Support React/Vue sites |
| 8 | Dynamic context window | `chat_service.py:1375` | 🟡 1.5h | 15% cost reduction |
| 9 | Distributed rate limiting | `core/rate_limiter.py` | 🟢 1h | Prevent abuse |
| 10 | Metadata embeddings | `chat_service.py` | 🟡 2h | 12-18% product relevance |

---

## File Reference
- **Main chat logic:** `apps/api/app/services/chat_service.py` (1812 lines)
- **Embedding model:** `apps/api/app/core/config.py:90`
- **Embedding service:** `apps/api/app/services/embedding_service.py`
- **RAG retrieval:** `chat_service.py:1240-1330`
- **Crawler:** `apps/api/app/services/crawler_service.py`

---

## Testing Checklist

- [ ] Embedding model swapped → re-embed test data → verify quality
- [ ] Cache enabled → test repeated queries → measure latency
- [ ] Query expansion → longer query strings → verify embedding dimensions unchanged
- [ ] BM25 added → search for exact product names → should rank high
- [ ] HNSW index → query time on 10k+ documents → should be <100ms
- [ ] Cross-encoder → compare relevance scores before/after re-ranking

