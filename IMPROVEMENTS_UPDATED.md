# 🚀 Updated Feature Improvements & Roadmap
**Last Updated:** Feb 12, 2026  
**Status:** Prioritized by impact & complexity

---

## ✅ COMPLETED IMPROVEMENTS

### 1. Query Enrichment System
- **Status:** ✅ DONE
- **Implementation:** `chat_service.py` lines 775-880
- **Details:**
  - Detects referential language (pronouns: "it", "that", "those")
  - Handles follow-up queries vs new topics
  - Short ambiguous queries enriched with conversation context
  - `_has_referential_language()`, `enrich_query_with_context()`, `_compute_topic_overlap()`

### 2. Product Carousel + IRRELEVANT Management
- **Status:** ✅ DONE
- **Implementation:** `chat_service.py` lines 1342-1752
- **Details:**
  - Products extracted BEFORE system prompt (not after LLM response)
  - LLM told: "If products exist, NEVER mark [[IRRELEVANT]]"
  - Fallback message replacement: rejection text → friendly product intro
  - Handles contradictions intelligently

### 3. Retrieval Confidence Interpretation
- **Status:** ✅ DONE
- **Implementation:** `chat_service.py` lines 1355-1373
- **Details:**
  - Product queries with products found → NOT out-of-scope (even low confidence)
  - Non-product queries apply 0.35 confidence threshold
  - Prevents false negatives on product pages

### 4. Smart Display Name Sanitization
- **Status:** ✅ DONE
- **Implementation:** `chat_service.py` lines 686-744
- **Details:**
  - Rejects literal "undefined", "null", "none"
  - Extracts brand name from URLs: `https://ramrajcotton.in/` → "Ramrajcotton"
  - Post-processing scrubs URLs from responses and suggestions
  - Handles all variations generalized (not hardcoded patterns)

### 5. Conversation Isolation Per Session
- **Status:** ✅ DONE
- **Implementation:** `chat_service.py` lines 886-963, `ChatbotWidget.tsx` line 204
- **Details:**
  - Each browser tab = new `sessionId` (React state, not persisted)
  - Backend filters all queries by `session_id`
  - No cross-user message leakage

### 6. Enhanced System Prompt
- **Status:** ✅ DONE
- **Implementation:** `chat_service.py` lines 1420-1520
- **Details:**
  - 7 critical rules with context-aware handling
  - Product carousel specific instructions
  - Filter feedback: "Price filter applied: showing products under $50 (8 match)"
  - Suggestion templates by scenario

---

## 🔄 HIGH PRIORITY IMPROVEMENTS (Ready to Implement)

### 1. **Better Embedding Model** `[MEDIUM EFFORT]`
- **Current:** `all-MiniLM-L6-v2` (384 dims, fast but limited quality)
- **Recommendation:** Upgrade to **BAAI/bge-small-en-v1.5** (384 dims, best for RAG)
- **Why:** Better retrieval for e-commerce product Q&A without speed loss
- **Implementation File:** `apps/api/app/core/config.py` line 90 + `embedding_service.py`
- **How to do it:**
  - Change `EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"`
  - Re-run all embeddings (migrations/alembic)
  - No code changes needed (same dimensions)
- **Impact:** 15-25% better retrieval accuracy for product queries

### 2. **Semantic Caching with Redis** `[MEDIUM EFFORT]`
- **Current:** No caching, every query hits Groq LLM + HuggingFace
- **Implementation File:** Create `apps/api/app/services/cache_service.py`
- **How to do it:**
  1. Add Redis config to `core/config.py`
  2. In `chat_service.py` (~line 1450), before LLM call:
     ```python
     # Hash the query embedding (already computed)
     cache_key = f"response:{chatbot_id}:{hash(query_embedding)}"
     cached_response = await cache_service.get_similar(cache_key, min_similarity=0.98)
     if cached_response:
         return cached_response  # Skip LLM call
     ```
  3. Store response in cache after LLM generation
- **Impact:** 60-70% faster responses for repeated questions, reduced LLM costs

### 3. **Distributed Rate Limiting (Redis)** `[EASY]`
- **Current:** In-memory rate limiter (`chat.py` line 19) - per-worker limits when running 4 workers
- **Issue:** User can bypass by sending requests to different workers
- **Implementation File:** `apps/api/app/core/rate_limiter.py`
- **How to do it:**
  1. Install `slowapi==0.1.8`
  2. Use Redis backend: `from slowapi.util import get_remote_address`
  3. Global counter across all workers:
     ```python
     limiter = Limiter(
         key_func=get_remote_address,
         storage_uri="redis://redis-service:6379",
         default_limits=["100 per minute"]
     )
     ```
  4. Apply to chat endpoint: `@limiter.limit("30 per minute")`
- **Impact:** Prevents abuse across distributed workers

### 4. **Query Expansion with Synonyms** `[MEDIUM EFFORT]`
- **Current:** Query used as-is for embedding
- **Problem:** "shirt" vs "top" vs "garment" are synonyms but different embeddings
- **Implementation File:** `chat_service.py` (~line 900, before embedding)
- **How to do it:**
  1. Create synonym dict in config:
     ```python
     PRODUCT_SYNONYMS = {
         "shirt": ["top", "tee", "t-shirt", "kurta"],
         "pants": ["trousers", "jeans", "slacks"],
         "buy": ["purchase", "order", "get", "want"],
     }
     ```
  2. Expand query before embedding:
     ```python
     expanded_query = query + " " + " ".join(synonyms_for_query)
     embedding = await get_single_embedding(expanded_query)
     ```
  3. Limit to 50 extra tokens to avoid noise
- **Impact:** 10-15% better recall for product queries with different terminology

### 5. **Hybrid Search: BM25 + Vector** `[HIGH EFFORT]`
- **Current:** Vector similarity only (cosine distance on embeddings)
- **Problem:** Misses exact product names, SKUs, model numbers
- **Implementation File:** `chat_service.py` (~line 1240, retrieval section)
- **How to do it:**
  1. Use PostgreSQL `tsvector` + `ts_rank` for keyword search:
     ```sql
     SELECT embedding_id, ts_rank(content_tsv, to_tsquery('simple', 'iPhone 15')) as bm25_score
     FROM embeddings 
     WHERE content_tsv @@ to_tsquery('simple', 'iPhone 15')
     ```
  2. Combine with vector scores (60% vector + 40% BM25):
     ```python
     final_score = 0.6 * vector_similarity + 0.4 * bm25_score
     ```
  3. Re-rank top 20 by combined score
- **Impact:** Perfect recall for exact matches (SKUs, product names)

---

## 🎯 MEDIUM PRIORITY IMPROVEMENTS (Next Quarter)

### 1. **Re-ranking with Cross-Encoder** `[HIGH EFFORT]`
- **Current:** Top 20 vector results → Top 8 sent to LLM
- **Better:** Top 20 → Cross-encoder re-rank → Top 8
- **Implementation File:** Create `apps/api/app/services/ranker_service.py`
- **How to do it:**
  1. Use model: `cross-encoder/ms-marco-MiniLM-L-12-v2` (small, fast)
  2. Score all top 20 results against query:
     ```python
     scores = cross_encoder.predict([(query, chunk_text) for chunk in top_20])
     ranked = sorted(zip(top_20, scores), key=lambda x: x[1], reverse=True)[:8]
     ```
  3. Insert before LLM: `chat_service.py` line 1240
- **Impact:** 20-30% better relevance (LLM gets only truly relevant chunks)

### 2. **JavaScript-Heavy Site Crawling (Playwright)** `[HIGH EFFORT]`
- **Current:** trafilatura + httpx (can't render React/Vue)
- **Problem:** Sites like myntra.com, ajio.com fail silently or return generic content
- **Implementation File:** Modify `crawler_service.py` line 345
- **How to do it:**
  1. Add Playwright fallback when trafilatura returns empty:
     ```python
     if not extracted:  # trafilatura returned nothing
         async with async_playwright() as p:
             browser = await p.chromium.launch(headless=True)
             page = await browser.new_page()
             await page.goto(url, wait_until="networkidle")
             html_content = await page.content()
             extracted = trafilatura.extract(html_content)
     ```
  2. Timeout: 10 seconds per page
  3. Only use for known JS-heavy domains (list already exists)
- **Impact:** Can crawl 30-40% more sites (React-based stores)

### 3. **Dynamic Context Window** `[MEDIUM EFFORT]`
- **Current:** Always send top 8 chunks × 500 chars (~4000 tokens)
- **Better:** Adjust based on query complexity
- **Implementation File:** `chat_service.py` (~line 1375)
- **How to do it:**
  ```python
  # Complexity scoring
  query_length = len(text_content.split())
  is_complex = "compare" in query or "difference" in query or query_length > 20
  
  # Dynamic window
  if is_greeting:
      context_chunks = 2  # "Hi there!" doesn't need 8 chunks
  elif is_complex:
      context_chunks = 12
  else:
      context_chunks = 8
  ```
  - Saves tokens on simple queries, keeps quality on complex ones
- **Impact:** ~15% cost reduction, faster responses

### 4. **Metadata-Enhanced Embeddings** `[MEDIUM EFFORT]`
- **Current:** Embed only content text
- **Better:** Include metadata (title, product name, price, color)
- **Implementation Files:** `chat_service.py` product extraction (+metadata to chunks)
- **How to do it:**
  1. Modify chunking to include: `f"Product: {name} | Price: {price} | Color: {color} | {content}"`
  2. Weight by importance: product name 2x, color 1.5x, price 1.5x
  3. Results in richer embeddings for product queries
- **Impact:** 12-18% better product relevance

---

## 📋 LOWER PRIORITY (Nice to Have)

### 1. Source Citation Footnotes
- Add URL footnotes to responses linking back to source
- Implementation: Append `[^source-1]: https://...` markdown during response building
- Impact: Transparency + trust for enterprise users

### 2. Crawl Quality Metrics
- Dashboard showing % of JS-blocked pages, duplicate content, freshness score
- Implementation: Track in `CrawlHistory` model
- Impact: Operational insight

### 3. Smart Crawl Scheduling
- Detect page change frequency, prioritize frequently-changing pages
- Implementation: Track `Last-Modified` headers, adjust schedule
- Impact: Keep e-commerce product prices fresh

### 4. Sitemap Support
- Parse `sitemap.xml` for faster initial crawl discovery
- Implementation: `crawler_service.py` (~line 250) add `parse_sitemap()`
- Impact: 2-3x faster initial crawls

### 5. Heading-Aware Chunking
- Split at semantic boundaries (headings) instead of fixed tokens
- Implementation: Use `trafilatura` + BeautifulSoup to detect `<h1>...<h3>` tags
- Impact: Better coherence in retrieved chunks

---

## 🚨 CRITICAL IMPROVEMENTS (Security/Stability)

### 1. **Vector Indexing (HNSW)** ⚠️ URGENT
- **Current:** pgvector with no indexing (full scan for every query)
- **Problem:** With 10k+ embeddings, query latency becomes O(n) = slow
- **Status:** Migration `006_embeddings.py` has HNSW implementation but commented out
- **How to do it:**
  1. Uncomment HNSW index in `alembic/versions/006_add_embeddings.py`
  2. Re-run migration: `alembic upgrade head`
  3. No code changes needed - pgvector handles automatically
- **Impact:** O(log n) search, 50-70% faster retrieval (10k+ documents)

### 2. **Sentry Error Tracking**
- Current: Custom traceback logic in logs
- Add: Sentry integration for aggregated error tracking + alerting
- Implementation: `pip install sentry-sdk`, init in `main.py`
- Impact: Real-time Error alerts, error trends

### 3. **Secret Rotation**
- Current: `.env` file static
- Better: Rotate `SECRET_KEY` monthly, use AWS Secrets Manager / Doppler
- Impact: Security compliance (SOC 2, ISO 27001)

---

## 📊 Priority Matrix

| Feature | Effort | Impact | Priority |
|---------|--------|--------|----------|
| Better Embedding Model | 🟢 Low | 🟡 Medium | **NOW** |
| Semantic Caching | 🟡 Medium | 🟢 High | **NOW** |
| Distributed Rate Limiting | 🟢 Low | 🟡 Medium | **THIS WEEK** |
| Query Expansion | 🟡 Medium | 🟡 Medium | **THIS WEEK** |
| Hybrid BM25 Search | 🔴 High | 🟢 High | **NEXT MONTH** |
| Playwright JS Support | 🔴 High | 🟢 High | **NEXT MONTH** |
| Cross-Encoder Re-ranking | 🔴 High | 🟢 High | **NEXT MONTH** |
| HNSW Indexing | 🟢 Low | 🟢 High | **CRITICAL** |

---

## ✨ Quick Wins (1-2 hours each)

1. Change embedding model → 15% accuracy boost
2. Add Redis rate limiting → Prevent abuse
3. Add query expansion synonyms → Better recall
4. Enable HNSW indexing → 50% faster queries
5. Add Sentry error tracking → Observability

---

## 📝 Next Steps

1. **This week:** Implement semantic caching + better embedding model
2. **Next 2 weeks:** Hybrid BM25 search + query expansion
3. **Month 2:** Playwright crawler + cross-encoder re-ranking
4. **Month 3:** Dynamic context windows + metadata-enhanced embeddings

