# 🎯 Untouched Improvements - Priority List

**Generated:** February 13, 2026  
**Purpose:** Improvements that have NOT been implemented yet, prioritized by impact

---

## ✅ ALREADY IMPLEMENTED (Skip these)

The following improvements have been completed:

| #   | Improvement                            | Evidence                                     |
| --- | -------------------------------------- | -------------------------------------------- |
| 1   | Better Embedding Model                 | `config.py:92` uses `BAAI/bge-small-en-v1.5` |
| 2   | HNSW Vector Indexing                   | Migration `025_enable_hnsw_index.py` exists  |
| 3   | Redis-Based Rate Limiting              | `chat.py:47` has distributed rate limiting   |
| 4   | Semantic Caching (Redis)               | `cache_service.py` fully implemented         |
| 5   | Sentry Error Tracking                  | `monitoring.py` with Sentry integration      |
| 6   | Query Enrichment System                | `chat_service.py` lines 775-880              |
| 7   | Product Carousel + IRRELEVANT Handling | `chat_service.py` lines 1342-1752            |
| 8   | Retrieval Confidence Interpretation    | `chat_service.py` lines 1355-1373            |
| 9   | Smart Display Name Sanitization        | `chat_service.py` lines 686-744              |
| 10  | Conversation Isolation Per Session     | `chat_service.py` lines 886-963              |
| 11  | Enhanced System Prompt                 | `chat_service.py` lines 1420-1520            |
| 12  | Database Performance Indexes           | Migration `026_add_performance_indexes.py`   |

---

## 🔴 PRIORITY 1: HIGH IMPACT + LOW EFFORT (Do First)

### 1. Query Expansion with Synonyms

**Effort:** 1-2 hours | **Impact:** 10-15% better recall  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** "Sneakers" query misses "shoes", "footwear" results  
**Files to modify:** `apps/api/app/services/chat_service.py` (~line 900)  
**Implementation:**

```python
PRODUCT_SYNONYMS = {
    "shirt": ["top", "tee", "t-shirt", "kurta"],
    "pants": ["trousers", "jeans", "slacks"],
    "sneakers": ["shoes", "footwear", "kicks"],
    "buy": ["purchase", "order", "get", "want"],
}

def expand_query(query: str) -> str:
    words = query.lower().split()
    expanded = []
    for word in words:
        if word in PRODUCT_SYNONYMS:
            expanded.extend(PRODUCT_SYNONYMS[word])
    return f"{query} {' '.join(expanded)}"
```

---

### 2. Dynamic Context Window Sizing

**Effort:** 1.5 hours | **Impact:** ~15% cost reduction, faster responses  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** Simple greetings use same 8 chunks as complex queries (wasteful)  
**Files to modify:** `apps/api/app/services/chat_service.py` (~line 1375)  
**Implementation:**

```python
def get_context_limit(query: str, is_product_query: bool) -> int:
    if len(query.split()) <= 5 and not is_product_query:
        return 3   # Simple queries
    elif "compare" in query or "vs" in query or len(query.split()) > 20:
        return 12  # Complex queries
    return 8       # Default
```

---

## 🟠 PRIORITY 2: HIGH IMPACT + MEDIUM EFFORT (Next Week)

### 3. Hybrid Search (BM25 + Vector)

**Effort:** 3-4 hours | **Impact:** 100% exact match for SKUs, product names  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** Vector search MISSES exact matches (SKU codes, model numbers)  
**Files to modify:**

- `apps/api/alembic/versions/` - new migration for `tsvector` column
- `apps/api/app/services/chat_service.py` (~line 1240)

**Implementation:**

```sql
-- Migration
ALTER TABLE embeddings ADD COLUMN content_tsvector tsvector
GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
CREATE INDEX idx_embeddings_tsvector ON embeddings USING GIN(content_tsvector);
```

```python
# In chat_service.py - combine scores
final_score = 0.6 * vector_similarity + 0.4 * bm25_score
```

---

### 4. Cross-Encoder Re-Ranking

**Effort:** 3-4 hours | **Impact:** 20-30% better relevance  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** Better context quality → Better LLM responses  
**Files to modify:** Create `apps/api/app/services/ranker_service.py` + modify `chat_service.py`  
**Implementation:**

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

async def rerank_chunks(query: str, chunks: list, top_k: int = 8):
    pairs = [(query, chunk['content']) for chunk in chunks]
    scores = reranker.predict(pairs)
    return sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)[:top_k]
```

---

## 🟡 PRIORITY 3: MEDIUM IMPACT (This Month)

### 6. Metadata-Enhanced Embeddings

**Effort:** 2-3 hours | **Impact:** 12-18% better product relevance  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** Product metadata (price, category, brand) not in embeddings  
**Files to modify:** `apps/api/app/services/embedding_service.py`  
**Implementation:**

```python
def enhance_chunk_with_metadata(chunk: str, metadata: dict) -> str:
    prefix = []
    if metadata.get('is_product'):
        prefix.append(f"Product: {metadata.get('product', {}).get('name', '')}")
        prefix.append(f"Category: {metadata.get('category', '')}")
        prefix.append(f"Price: {metadata.get('product', {}).get('price', '')}")
    return "\n".join(prefix) + "\n\n" + chunk
```

---

### 7. Query Clustering for Analytics

**Effort:** 3-4 hours | **Impact:** Better knowledge gap identification  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** Identify common unanswered topics faster  
**Files to modify:** Create `apps/api/app/services/clustering_service.py`  
**Implementation:**

```python
from sklearn.cluster import DBSCAN

async def cluster_queries(queries: list, embeddings: list):
    clustering = DBSCAN(eps=0.15, min_samples=2, metric='cosine').fit(embeddings)
    # Group queries by cluster label
    return clusters
```

---

### 8. Chatbot Personality Customization

**Effort:** 2-3 hours | **Impact:** Better client customization  
**Status:** ✅ IMPLEMENTED  
**Why it matters:** Let clients customize tone (formal/casual), response length  
**Implementation:**

- Added `personality_tone`, `response_length`, `temperature`, `custom_instructions` fields to `ChatbotAppearance` model
- Added personality settings to system prompt in `chat_service.py`
- Added UI controls in appearance tab (tone, length, temperature slider, custom instructions)
- Temperature now configurable per-chatbot (0.0 - 1.0)

---

## 🔵 PRIORITY 4: LOW PRIORITY (Next Quarter)

### 9. Celery Task Queue (Replace APScheduler)

**Effort:** 8-12 hours | **Impact:** Better scalability  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** APScheduler runs in API process (not scalable, crashes if API restarts)  
**Files to create:**

- `apps/api/celery_app.py`
- Update `docker-compose.yml` with Celery worker

---

### 10. Human Handoff System

**Effort:** 10-15 hours | **Impact:** Better UX for complex queries  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** No escalation path when bot can't answer  
**Files to create:**

- `apps/api/app/models/handoff.py`
- Update widget with "Talk to Human" button

---

### 11. Multi-Language Support

**Effort:** 4-6 hours | **Impact:** Expand to non-English markets  
**Status:** ✅ IMPLEMENTED (Hindi, Gujarati)  
**Implementation:**

- Added `language` field to `ChatbotAppearance` model (en, hi, gu)
- Added language instructions to system prompt in `chat_service.py`
- Added language selector in appearance tab
- Voice recognition language auto-detects based on chatbot language setting

---

### 12. Voice Input (Web Speech API)

**Effort:** 2-3 hours | **Impact:** Mobile accessibility  
**Status:** ✅ IMPLEMENTED  
**Implementation:**

- Added Web Speech API integration to `ChatbotWidget.tsx`
- Voice input button appears next to image upload button (only on browsers that support it)
- Supports English, Hindi, and Gujarati based on chatbot language setting
- Visual feedback with pulsing animation when listening

---

### 13. A/B Testing Framework

**Effort:** 6-8 hours | **Impact:** Optimize prompts scientifically  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** No experimentation capability  
**Files to modify:**

- `apps/api/app/models/chat.py` - add experiment_variant
- `apps/api/app/services/analytics_service.py` - track by variant

---

### 14. Webhook System for Integrations

**Effort:** 4-6 hours | **Impact:** Enable Zapier/CRM integrations  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** No way to notify external systems  
**Files to create:**

- `apps/api/app/models/webhook.py`
- `apps/api/app/services/webhook_service.py`

---

### 15. CSV/Excel Bulk Q&A Upload

**Effort:** 3-4 hours | **Impact:** Faster knowledge onboarding  
**Status:** ❌ NOT IMPLEMENTED  
**Why it matters:** Manual Q&A entry is slow  
**Files to modify:**

- `apps/api/app/api/v1/knowledge.py` - add upload endpoint
- Dashboard Knowledge tab - add file upload UI

---

## 🔷 PRIORITY 5: ADVANCED/ENTERPRISE (Future)

### 16. Hierarchical Chunk Embedding

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** 20% better retrieval for broad questions

### 17. ColBERT-Style Late Interaction

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** 10-15% accuracy boost, 10x storage increase (enterprise only)

### 18. Smart Crawl Frequency Detection

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** 50% reduction in unnecessary crawls

### 19. Incremental Crawling (Only Changed Pages)

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** 70% faster re-crawls

### 20. Content Quality Scoring

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Better signal-to-noise in search

### 21. Deduplication Detection (MinHash)

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** 20-30% reduction in embedding costs

### 22. Conversation Flow Analysis

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Identify user drop-off points

### 23. Real-Time Alerting System

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Proactive issue detection

### 24. White-Label Customization

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Enterprise custom domains + branding

### 25. RBAC (Role-Based Access Control)

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Granular permissions (analyst, support, admin)

### 26. Audit Logging

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Compliance (SOC 2, ISO 27001)

### 27. WhatsApp/Slack Integration

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Multi-channel support

### 28. OpenTelemetry Tracing

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Full request tracing across services

### 29. Content Security Policy (Widget)

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Enterprise security compliance

### 30. Secret Rotation / AWS Secrets Manager

**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Production-level security

---

## 📊 Summary Table

| Priority | Item                         | Effort | Impact           | Status |
| -------- | ---------------------------- | ------ | ---------------- | ------ |
| **P1**   | Query Expansion (Synonyms)   | 1-2h   | 10-15% recall    | ❌     |
| **P1**   | Dynamic Context Window       | 1.5h   | 15% cost savings | ❌     |
| **P2**   | Hybrid BM25 + Vector Search  | 3-4h   | 100% exact match | ❌     |
| **P2**   | Cross-Encoder Re-Ranking     | 3-4h   | 20-30% relevance | ❌     |
| **P2**   | Playwright JS Crawler        | 4-6h   | 90% more sites   | ❌     |
| **P3**   | Metadata-Enhanced Embeddings | 2-3h   | 12-18% relevance | ❌     |
| **P3**   | Query Clustering             | 3-4h   | Better analytics | ❌     |
| **P3**   | Personality Customization    | 2-3h   | Client UX        | ✅     |
| **P4**   | Celery Task Queue            | 8-12h  | Scalability      | ❌     |
| **P4**   | Human Handoff                | 10-15h | UX               | ❌     |
| **P4**   | Multi-Language               | 4-6h   | Market expansion | ✅     |
| **P4**   | Voice Input                  | 2-3h   | Accessibility    | ✅     |
| **P4**   | A/B Testing                  | 6-8h   | Optimization     | ❌     |
| **P4**   | Webhooks                     | 4-6h   | Integrations     | ❌     |
| **P4**   | Bulk Q&A Upload              | 3-4h   | Onboarding       | ❌     |
| **P5**   | 15+ Advanced Features        | Varies | Enterprise       | ❌     |

---

## 🚀 Recommended Implementation Order

### Week 1 (Quick Wins - ~5 hours)

1. ✅ Query Expansion with Synonyms (1-2h)
2. ✅ Dynamic Context Window (1.5h)

### Week 2-3 (Core RAG Improvements - ~10 hours)

3. ✅ Hybrid BM25 + Vector Search (3-4h)
4. ✅ Cross-Encoder Re-Ranking (3-4h)

### Week 4 (Crawling Enhancement - ~6 hours)

5. ✅ Playwright Integration (4-6h)

### Month 2 (Feature Polish - ~10 hours)

6. ✅ Metadata-Enhanced Embeddings (2-3h)
7. ✅ Query Clustering (3-4h)
8. ✅ Personality Customization (2-3h)

### Month 3+ (Enterprise Features)

9+ Celery, Handoff, Multi-Language, etc.

---

**Total Estimated Effort for P1-P3:** ~25-35 hours  
**Total Estimated Effort for All:** ~100-120 hours
