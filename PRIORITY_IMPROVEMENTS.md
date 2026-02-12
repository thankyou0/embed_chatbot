# 🎯 Priority Improvements - Embed Chatbot
**Last Updated:** February 12, 2026  
**Status:** Organized by implementation priority and impact

---

## 🔴 **CRITICAL - Production Stability** (Do First)

# FUTURE
### 1. Enable HNSW Vector Indexing
**Current State:** Index is commented out in `006_add_embeddings.py:48`  
**Impact:** 10-50x faster similarity search for >10k embeddings  
**Implementation:**
- Uncomment: `op.execute('CREATE INDEX idx_embeddings_vector ON embeddings USING hnsw (embedding vector_cosine_ops)')`
- Run migration: `alembic revision -m "enable_hnsw_index"`
- Add to new migration file, then: `alembic upgrade head`
- **Files:** `apps/api/alembic/versions/006_add_embeddings.py`


### 2. Redis-Based Distributed Rate Limiting
**Current State:** In-memory rate limiting in `apps/api/app/api/v1/chat.py:20` (won't work with multiple workers)  
**Impact:** Prevents rate limit bypass in production (you're running 4 workers per docker-compose)  
**Implementation:**
- Install: `pip install redis aioredis`
- Create `apps/api/app/core/redis_client.py`:
  ```python
  import aioredis
  from app.core.config import settings
  
  _redis = None
  async def get_redis():
      global _redis
      if not _redis:
          _redis = await aioredis.create_redis_pool(settings.REDIS_URL)
      return _redis
  ```
- Update `chat.py:check_rate_limit()` to use Redis:
  ```python
  async def check_rate_limit(request: Request, db: AsyncSession):
      redis = await get_redis()
      ip = request.client.host
      key = f"rate_limit:{ip}"
      count = await redis.incr(key)
      if count == 1:
          await redis.expire(key, 60)
      if count > 30:
          raise HTTPException(429, "Too many requests")
  ```
- Add `REDIS_URL` to `apps/api/app/core/config.py:Settings`
- Update `docker-compose.yml` to add Redis service
- **Files:** `apps/api/app/api/v1/chat.py`, `apps/api/app/core/config.py`, `docker-compose.yml`


### 3. Sentry Integration for Error Tracking
**Current State:** Custom logging only (logs get lost across containers)  
**Impact:** Catch production errors, get alerts on failures  
**Implementation:**
- Install: `pip install sentry-sdk[fastapi]`
- Initialize in `apps/api/main.py:create_app()`:
  ```python
  import sentry_sdk
  from sentry_sdk.integrations.fastapi import FastApiIntegration
  
  sentry_sdk.init(
      dsn=settings.SENTRY_DSN,
      integrations=[FastApiIntegration()],
      traces_sample_rate=0.1,
      environment=settings.ENVIRONMENT
  )
  ```
- Add `SENTRY_DSN` to config
- **Files:** `apps/api/main.py`, `apps/api/app/core/config.py`, `requirements.txt`

---

## 🟡 **HIGH PRIORITY - Performance & UX**

### 4. Semantic Query Caching with Redis
**Current State:** Every query hits HuggingFace API + Groq (~500-800ms per request)  
**Impact:** 10x faster responses for common queries, 50% cost reduction  
**Implementation:**
- Create `apps/api/app/services/cache_service.py`:
  ```python
  import hashlib
  import json
  from typing import Optional
  
  class CacheService:
      @staticmethod
      async def get_cached_response(query_embedding: list, threshold=0.98):
          redis = await get_redis()
          # Store embeddings in Redis with HNSW-like search
          # Check if similar query exists (cosine similarity > 0.98)
          # Return cached response if found
  
      @staticmethod
      async def cache_response(query_embedding: list, response: dict, ttl=3600):
          # Cache the response for 1 hour
  ```
- Integrate before calling Groq in `apps/api/app/services/chat_service.py:get_response_stream()`:
  ```python
  cached = await CacheService.get_cached_response(query_embedding)
  if cached:
      yield cached
      return
  ```
- **Files:** `apps/api/app/services/cache_service.py`, `apps/api/app/services/chat_service.py`

### 5. Upgrade Embedding Model
**Current State:** `all-MiniLM-L6-v2` (384 dims, decent quality)  
**Impact:** 15-25% better retrieval accuracy for e-commerce queries  
**Recommended:** `BAAI/bge-small-en-v1.5` (384 dims, optimized for RAG, same speed)  
**Implementation:**
- Update `apps/api/app/core/config.py:Settings.EMBEDDING_MODEL`
  ```python
  EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
  ```
- Add migration to re-embed all existing chunks:
  ```python
  # apps/api/app/services/embedding_service.py
  async def migrate_embeddings(chatbot_id: UUID):
      # Re-generate all embeddings with new model
  ```
- **Note:** Requires re-embedding all data (can run as background job)
- **Files:** `apps/api/app/core/config.py`, `apps/api/app/services/embedding_service.py`

### 6. Playwright Integration for JS-Heavy Sites
**Current State:** `trafilatura` can't crawl React/Vue/Next.js sites (marked as JS_HEAVY_DOMAINS but no handling)  
**Impact:** Support 90% more e-commerce sites (most are now SPA)  
**Implementation:**
- Install: `pip install playwright` and `playwright install chromium`
- Update `apps/api/app/services/crawler_service.py`:
  ```python
  from playwright.async_api import async_playwright
  
  async def crawl_with_browser(url: str) -> str:
      async with async_playwright() as p:
          browser = await p.chromium.launch(headless=True)
          page = await browser.new_page()
          await page.goto(url, wait_until='networkidle')
          content = await page.content()
          await browser.close()
          return content
  
  # In crawl_single_page(), check is_js_heavy_site() first:
  if is_js_heavy_site(url):
      html_content = await crawl_with_browser(url)
  else:
      # Use existing httpx + trafilatura
  ```
- Add `PLAYWRIGHT_ENABLED` config flag (disable in dev to save resources)
- **Files:** `apps/api/app/services/crawler_service.py`, `requirements.txt`, `Dockerfile`

---

## 🟢 **MEDIUM PRIORITY - Feature Enhancements**

### 7. Hybrid Search (BM25 + Vector Similarity)
**Current State:** Only vector search (fails on exact SKU codes, model numbers)  
**Impact:** Better accuracy for exact product name searches  
**Implementation:**
- Add `tsvector` column to `embeddings` table:
  ```sql
  ALTER TABLE embeddings ADD COLUMN content_tsvector tsvector 
  GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
  CREATE INDEX idx_embeddings_tsvector ON embeddings USING GIN(content_tsvector);
  ```
- Update `apps/api/app/services/chat_service.py:get_response_stream()`:
  ```python
  # Get top 20 from BM25
  bm25_stmt = select(Embedding).where(
      Embedding.content_tsvector.match(enriched_query)
  ).order_by(func.ts_rank(Embedding.content_tsvector, enriched_query).desc()).limit(20)
  
  # Get top 20 from vector search (existing)
  # Merge results with score fusion: final_score = 0.3*bm25 + 0.7*vector
  ```
- **Files:** `apps/api/alembic/versions/`, `apps/api/app/services/chat_service.py`

### 8. Query Clustering for Analytics
**Current State:** Unanswered queries listed individually (line 307: "simple grouping, no clustering yet")  
**Impact:** Identify common knowledge gaps faster  
**Implementation:**
- Install: `pip install scikit-learn`
- Create `apps/api/app/services/clustering_service.py`:
  ```python
  from sklearn.cluster import DBSCAN
  import numpy as np
  
  async def cluster_queries(queries: List[str], embeddings: List[list]):
      X = np.array(embeddings)
      clustering = DBSCAN(eps=0.15, min_samples=2, metric='cosine').fit(X)
      # Group queries by cluster label
      return clusters
  ```
- Update `apps/api/app/services/analytics_service.py:get_unanswered_queries()`:
  ```python
  embeddings = await get_batch_embeddings([q.content for q in queries])
  clusters = await cluster_queries(queries, embeddings)
  # Return clustered format instead of individual queries
  ```
- **Files:** `apps/api/app/services/clustering_service.py`, `apps/api/app/services/analytics_service.py`

### 9. Cross-Encoder Re-Ranking
**Current State:** Top 8 chunks sent to LLM based only on cosine similarity  
**Impact:** 10-15% better context relevance (cross-encoder is more accurate than bi-encoder)  
**Implementation:**
- Use HuggingFace Inference API for cross-encoder:
  ```python
  async def rerank_chunks(query: str, chunks: List[Dict], top_k=8):
      pairs = [(query, chunk['content']) for chunk in chunks]
      scores = await hf_client.post(
          model="cross-encoder/ms-marco-MiniLM-L-6-v2",
          inputs=pairs
      )
      # Re-sort chunks by cross-encoder scores
      return sorted(chunks, key=lambda x: scores[x['idx']], reverse=True)[:top_k]
  ```
- Apply in `apps/api/app/services/chat_service.py` after getting top 20 vector results:
  ```python
  top_chunks = await rerank_chunks(enriched_query, combined_results[:20], top_k=8)
  ```
- **Files:** `apps/api/app/services/chat_service.py`

### 10. Chatbot Personality Customization
**Current State:** Hardcoded system prompt, no personality options  
**Impact:** Let clients customize tone (formal/casual), response length, emoji usage  
**Implementation:**
- Add to `apps/api/app/models/chatbot.py:Chatbot`:
  ```python
  tone = Column(String(50), default='friendly')  # 'formal', 'casual', 'friendly'
  response_style = Column(String(50), default='balanced')  # 'concise', 'balanced', 'detailed'
  use_emojis = Column(Boolean, default=False)
  ```
- Update system prompt builder in `apps/api/app/services/chat_service.py`:
  ```python
  tone_instructions = {
      'formal': "Use professional language, avoid contractions...",
      'casual': "Be conversational and friendly...",
      'friendly': "Be warm and helpful..."
  }
  system_prompt = f"{tone_instructions[chatbot.tone]} {base_prompt}"
  ```
- Add UI in `apps/web/app/dashboard/chatbots/[chatbotId]/page.tsx` Settings tab
- **Files:** `apps/api/app/models/chatbot.py`, `apps/api/app/services/chat_service.py`, `apps/web/app/dashboard/chatbots/[chatbotId]/page.tsx`

---

## 🔵 **LOW PRIORITY - Nice to Have**

### 11. Celery Task Queue (Replace APScheduler)
**Current State:** `apscheduler` runs in API process (not scalable, crashes if API restarts)  
**Impact:** Better reliability for background tasks  
**Implementation:**
- Install: `pip install celery[redis]`
- Create `apps/api/celery_app.py`:
  ```python
  from celery import Celery
  app = Celery('embed_chatbot', broker=settings.REDIS_URL)
  
  @app.task
  def crawl_scheduled_source(source_id: str):
      # Move crawling logic here
  ```
- Replace scheduler in `apps/api/app/services/scheduler_service.py` with Celery Beat
- Add separate worker container in `docker-compose.yml`
- **Files:** `apps/api/celery_app.py`, `docker-compose.yml`, `requirements.txt`

### 12. Human Handoff System
**Current State:** Bot has no escalation path when it can't answer  
**Impact:** Better user experience for complex queries  
**Implementation:**
- Add to system prompt: "If user asks to speak to human, respond with [[HANDOFF]]"
- Create `apps/api/app/models/handoff.py`:
  ```python
  class HandoffRequest(Base):
      id = Column(UUID, primary_key=True)
      session_id = Column(UUID, ForeignKey('chat_sessions.id'))
      user_email = Column(String)
      user_phone = Column(String)
      status = Column(Enum('pending', 'claimed', 'resolved'))
  ```
- Add "Talk to Human" button in widget when [[HANDOFF]] detected
- Notify chatbot owner via email/webhook
- **Files:** `apps/api/app/models/handoff.py`, `packages/chatbot-widget/src/ChatbotWidget.tsx`

### 13. Multi-Language Support
**Current State:** English only  
**Impact:** Expand market to non-English users  
**Implementation:**
- Detect language in widget: `const lang = navigator.language`
- Add to system prompt: `"Respond in {detected_language}"`
- Store `preferred_language` in ChatSession
- Use Groq's multilingual model (llama-3.3 supports 10+ languages already)
- **Files:** `packages/chatbot-widget/src/ChatbotWidget.tsx`, `apps/api/app/services/chat_service.py`

### 14. Voice Input (Web Speech API)
**Current State:** Text input only  
**Impact:** Mobile accessibility  
**Implementation:**
- Add microphone button in widget:
  ```typescript
  const startVoiceInput = () => {
    const recognition = new webkitSpeechRecognition();
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      setInputValue(transcript);
    };
    recognition.start();
  };
  ```
- No backend changes needed (sends text as usual)
- **Files:** `packages/chatbot-widget/src/ChatbotWidget.tsx`

### 15. A/B Testing Framework
**Current State:** No experimentation capability  
**Impact:** Optimize prompts and response styles  
**Implementation:**
- Add `experiment_variant` field to ChatSession
- Create multiple system prompt templates
- Randomly assign variant on session creation
- Track success metrics by variant
- **Files:** `apps/api/app/models/chat.py`, `apps/api/app/services/chat_service.py`, `apps/api/app/services/analytics_service.py`

---

## 📊 **Current Architecture Status**

### ✅ Already Implemented (Strong Foundation)
- Streaming SSE responses
- Markdown rendering in widget
- S3/object storage for files
- Smart query enrichment with context
- Product extraction with metadata
- Vision/image analysis
- Analytics with LLM-classified unanswered queries
- Sitemap parsing
- Crawl scheduling
- Price/attribute/gender filters

### ❌ Not Yet Implemented
- Redis (caching + rate limiting)
- HNSW vector indexing
- Better embedding model
- Hybrid BM25+Vector search
- Playwright for JS-heavy sites
- Celery distributed tasks
- Query clustering
- Cross-encoder re-ranking
- Personality customization
- Human handoff
- Multi-language
- Voice input
- A/B testing

---

## 🎯 **Recommended Implementation Order**

**Week 1-2:** Critical production stability  
1. Enable HNSW indexing (30 min)
2. Redis rate limiting (4 hours)
3. Sentry error tracking (1 hour)

**Week 3-4:** Performance wins  
4. Semantic caching (8 hours)
5. Upgrade embedding model (2 hours + re-embedding time)
6. Playwright for SPA sites (6 hours)

**Month 2:** Feature enhancements  
7. Hybrid BM25+Vector search (12 hours)
8. Query clustering (6 hours)
9. Cross-encoder re-ranking (4 hours)
10. Personality customization (8 hours)

**Month 3+:** Advanced features  
11. Celery migration (16 hours)
12. Human handoff (20 hours)
13. Multi-language (8 hours)
14. Voice input (4 hours)
15. A/B testing (12 hours)

---

**Total Estimated Effort:** ~120 hours (3 months of focused work)
