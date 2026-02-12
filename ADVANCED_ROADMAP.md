# 🏗️ Advanced Architecture & Feature Roadmap
**Companion to:** PRIORITY_IMPROVEMENTS.md  
**Focus:** Long-term scalability, advanced AI features, enterprise capabilities

---

## 🧠 **Advanced RAG & AI Improvements**

### 1. Dynamic Context Window Sizing
**Current State:** Fixed 8 chunks × 500 chars = ~4000 tokens (wasteful for simple queries)  
**Problem:** Greeting uses same context as complex product comparison  
**Implementation:**
- Calculate query complexity score:
  ```python
  def get_query_complexity(query: str, is_product_query: bool) -> str:
      word_count = len(query.split())
      has_comparatives = bool(re.search(r'vs|versus|compare|difference', query))
      
      if word_count <= 5 and not has_comparatives:
          return 'simple'  # 2-3 chunks
      elif is_product_query or has_comparatives:
          return 'complex'  # 10-12 chunks
      else:
          return 'medium'  # 6-8 chunks (current)
  ```
- Apply in `apps/api/app/services/chat_service.py:get_response_stream()`:
  ```python
  complexity = get_query_complexity(text_content, is_product_query(text_content))
  chunk_limits = {'simple': 3, 'medium': 8, 'complex': 12}
  top_chunks = combined_results[:chunk_limits[complexity]]
  ```
- **Files:** `apps/api/app/services/chat_service.py`
- **Impact:** 30% token savings, faster responses for simple queries

### 2. Hierarchical Chunk Embedding
**Current State:** Only paragraph-level chunks (512 tokens)  
**Problem:** Miss big-picture context from full page  
**Implementation:**
- Store TWO types of embeddings per page:
  - **Document-level:** Full page summary (1 embedding)
  - **Chunk-level:** Paragraph splits (N embeddings)
- Add `embedding_level` enum to `embeddings` table:
  ```python
  embedding_level = Column(Enum('document', 'chunk'), default='chunk')
  parent_id = Column(UUID, ForeignKey('embeddings.id'), nullable=True)
  ```
- Search strategy:
  1. First pass: Find relevant documents (document-level search)
  2. Second pass: Get chunks from top documents (chunk-level search)
- **Files:** `apps/api/app/models/knowledge.py`, `apps/api/app/services/embedding_service.py`, `apps/api/app/services/chat_service.py`
- **Impact:** 20% better retrieval for broad questions ("Tell me about your company")

### 3. Metadata-Enhanced Embeddings
**Current State:** Embedding contains only text content  
**Problem:** Product metadata (price, category, brand) not influencing search  
**Implementation:**
- Prepend structured metadata to chunk text before embedding:
  ```python
  def enhance_chunk_with_metadata(chunk: str, metadata: dict) -> str:
      prefix = []
      if metadata.get('is_product'):
          prefix.append(f"Product: {metadata.get('product', {}).get('name', '')}")
          prefix.append(f"Category: {metadata.get('category', '')}")
          prefix.append(f"Price: {metadata.get('product', {}).get('price', '')}")
          prefix.append(f"Brand: {metadata.get('product', {}).get('brand', '')}")
      prefix.append(f"Title: {metadata.get('title', '')}")
      
      return "\n".join(prefix) + "\n\n" + chunk
  ```
- Apply in `apps/api/app/services/embedding_service.py:generate_embeddings()` before calling HuggingFace
- **Files:** `apps/api/app/services/embedding_service.py`
- **Impact:** Better product discovery ("show me Nike shoes under $100")

### 4. ColBERT-Style Late Interaction (Advanced)
**Current State:** Single embedding per chunk (bi-encoder)  
**Limitation:** Can't capture fine-grained token-level matching  
**Implementation:**
- Store token-level embeddings (384 dims × N tokens per chunk)
- Use MaxSim scoring: `score = max(query_token · chunk_token)` for each query token
- Requires custom storage (JSONB array in embeddings table)
- **Note:** This is expensive (500MB → 5GB storage), only for enterprise tier
- **Files:** `apps/api/app/models/knowledge.py`, `apps/api/app/services/embedding_service.py`
- **Impact:** 10-15% better accuracy, 10x storage increase

### 5. Query Expansion with Synonyms
**Current State:** Direct embedding of user query  
**Problem:** "sneakers" query misses "shoes", "footwear" results  
**Implementation:**
- Create synonym dictionary or use WordNet:
  ```python
  from nltk.corpus import wordnet
  
  def expand_query(query: str) -> str:
      words = query.split()
      expanded = []
      for word in words:
          synonyms = wordnet.synsets(word)
          if synonyms:
              # Add top 2 synonyms
              expanded.extend([l.name() for l in synonyms[0].lemmas()[:2]])
      return f"{query} {' '.join(expanded)}"
  ```
- Apply before embedding: `enriched_query = expand_query(text_content)`
- **Files:** `apps/api/app/services/chat_service.py`
- **Impact:** 15% recall improvement for broad queries

---

## 🕷️ **Advanced Crawling Features**

### 6. Smart Crawl Frequency Detection
**Current State:** Manual schedule configuration (daily/weekly/monthly)  
**Problem:** Product pages change frequently, About page doesn't  
**Implementation:**
- Track content hash changes:
  ```python
  class CrawledPage(Base):
      content_hash = Column(String(64))  # SHA256 of content
      change_frequency = Column(Float, default=7.0)  # days
      last_changed_at = Column(DateTime)
  ```
- Calculate adaptive frequency:
  ```python
  def calculate_crawl_frequency(page: CrawledPage) -> float:
      if page.last_changed_at:
          days_since_change = (datetime.now() - page.last_changed_at).days
          # If page changed recently, crawl more often
          return max(1.0, days_since_change * 0.5)
      return 7.0  # default weekly
  ```
- **Files:** `apps/api/app/models/knowledge.py`, `apps/api/app/services/crawler_service.py`
- **Impact:** 50% reduction in unnecessary crawls

### 7. Incremental Crawling (Only Changed Pages)
**Current State:** Re-crawl entire site on schedule  
**Problem:** Wastes resources, hits rate limits  
**Implementation:**
- Use HTTP `If-Modified-Since` and `ETag` headers:
  ```python
  async def should_recrawl(url: str, last_etag: str, last_modified: datetime) -> bool:
      headers = {}
      if last_etag:
          headers['If-None-Match'] = last_etag
      if last_modified:
          headers['If-Modified-Since'] = last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
      
      response = await client.head(url, headers=headers)
      return response.status_code != 304  # 304 = Not Modified
  ```
- Store `etag` and `last_modified` in `crawled_pages` table
- **Files:** `apps/api/app/models/knowledge.py`, `apps/api/app/services/crawler_service.py`
- **Impact:** 70% faster re-crawls

### 8. Content Quality Scoring
**Current State:** All crawled pages treated equally  
**Problem:** Some pages have minimal useful content  
**Implementation:**
- Score pages during crawl:
  ```python
  def calculate_quality_score(page: CrawledPage) -> float:
      score = 0.0
      
      # Content length (0-30 points)
      score += min(30, len(page.text_content) / 100)
      
      # Has product data (20 points)
      if page.is_product:
          score += 20
      
      # Has images (10 points)
      if page.metadata_json.get('images'):
          score += 10
      
      # Semantic coherence (0-20 points)
      sentences = page.text_content.split('.')
      if len(sentences) > 3:
          score += 20
      
      # Keyword density (0-20 points)
      # Penalize keyword stuffing
      
      return min(100, score)
  ```
- Boost high-quality chunks in search:
  ```python
  score = (1.0 - float(dist)) * quality_weight
  ```
- **Files:** `apps/api/app/services/crawler_service.py`, `apps/api/app/services/chat_service.py`
- **Impact:** Better signal-to-noise ratio in search results

### 9. Deduplication Detection
**Current State:** Duplicate content may exist across pages  
**Problem:** Wastes embedding space, confuses LLM  
**Implementation:**
- Calculate MinHash signatures during crawl:
  ```python
  from datasketch import MinHash, MinHashLSH
  
  def get_minhash(text: str) -> MinHash:
      m = MinHash(num_perm=128)
      for word in text.lower().split():
          m.update(word.encode('utf8'))
      return m
  ```
- Build LSH index to find duplicates (>90% similarity)
- Mark duplicates, only embed one copy:
  ```python
  is_duplicate = Column(Boolean, default=False)
  canonical_page_id = Column(UUID, ForeignKey('crawled_pages.id'))
  ```
- **Files:** `apps/api/app/services/crawler_service.py`, `requirements.txt` (add `datasketch`)
- **Impact:** 20-30% reduction in embedding costs

---

## 📊 **Advanced Analytics & Insights**

### 10. Conversation Flow Analysis
**Current State:** Track individual messages, no flow analysis  
**Problem:** Don't know where users drop off  
**Implementation:**
- Create conversation flow states:
  ```python
  class ConversationState(Enum):
      GREETING = 'greeting'
      BROWSING = 'browsing'
      PRODUCT_INQUIRY = 'product_inquiry'
      SUPPORT = 'support'
      ABANDONED = 'abandoned'
  ```
- Track state transitions:
  ```python
  class ConversationTransition(Base):
      session_id = Column(UUID, ForeignKey('chat_sessions.id'))
      from_state = Column(Enum(ConversationState))
      to_state = Column(Enum(ConversationState))
      message_id = Column(UUID, ForeignKey('chat_messages.id'))
      timestamp = Column(DateTime)
  ```
- Build Sankey diagram showing user journeys
- **Files:** `apps/api/app/models/chat.py`, `apps/api/app/services/analytics_service.py`
- **Impact:** Identify friction points, optimize conversation design

### 11. Intent Classification & Tracking
**Current State:** Binary classification (product query vs general)  
**Problem:** Can't segment analytics by user intent  
**Implementation:**
- Expand intent taxonomy:
  ```python
  class QueryIntent(Enum):
      PRODUCT_DISCOVERY = 'product_discovery'
      PRICE_INQUIRY = 'price_inquiry'
      SHIPPING_INFO = 'shipping_info'
      RETURN_POLICY = 'return_policy'
      SIZE_GUIDE = 'size_guide'
      STORE_LOCATOR = 'store_locator'
      COMPLAINT = 'complaint'
      OTHER = 'other'
  ```
- Classify using regex + LLM:
  ```python
  async def classify_intent(query: str) -> QueryIntent:
      # Fast regex pre-classification
      if re.search(r'track|shipping|delivery', query):
          return QueryIntent.SHIPPING_INFO
      
      # LLM classifier for ambiguous cases
      prompt = f"Classify intent: {query}\nChoose: {list(QueryIntent)}"
      # ... call Groq
  ```
- Store in message metadata, aggregate in analytics
- **Files:** `apps/api/app/services/chat_service.py`, `apps/api/app/services/analytics_service.py`
- **Impact:** Better understanding of user needs

### 12. Real-Time Alerting System
**Current State:** No alerts for anomalies  
**Problem:** Don't know when chatbot is failing  
**Implementation:**
- Define alert triggers:
  ```python
  class AlertRule(Base):
      chatbot_id = Column(UUID, ForeignKey('chatbots.id'))
      metric = Column(String)  # 'unanswered_rate', 'response_time', 'error_rate'
      threshold = Column(Float)
      window_minutes = Column(Integer)
      notification_channel = Column(String)  # 'email', 'webhook', 'slack'
  ```
- Background job checks metrics every 5 minutes:
  ```python
  async def check_alert_rules():
      for rule in active_rules:
          current_value = await calculate_metric(rule.metric, rule.window_minutes)
          if current_value > rule.threshold:
              await send_alert(rule)
  ```
- Send email/Slack/webhook notification
- **Files:** `apps/api/app/models/alerts.py`, `apps/api/app/services/alert_service.py`
- **Impact:** Proactive issue detection

---

## 🎨 **Platform & Enterprise Features**

### 13. White-Label Customization
**Current State:** Fixed widget appearance (limited CSS customization)  
**Implementation:**
- Support custom domains:
  ```python
  class ChatbotDomain(Base):
      chatbot_id = Column(UUID, ForeignKey('chatbots.id'))
      custom_domain = Column(String)  # 'chat.clientsite.com'
      ssl_cert = Column(Text)
      ssl_key = Column(Text)
  ```
- Inject client branding:
  ```python
  widget_config = {
      'custom_css_url': chatbot.appearance.custom_css_url,
      'remove_branding': chatbot.tenant.plan == 'enterprise',
      'powered_by_text': chatbot.appearance.powered_by_text
  }
  ```
- **Files:** `apps/api/app/models/chatbot.py`, `packages/chatbot-widget/src/ChatbotWidget.tsx`

### 14. RBAC (Role-Based Access Control)
**Current State:** Simple tenant membership (ChatbotPermission has can_edit flag)  
**Problem:** No granular permissions  
**Implementation:**
- Define roles:
  ```python
  class Role(Enum):
      OWNER = 'owner'        # Full access
      ADMIN = 'admin'        # Manage settings, can't delete
      ANALYST = 'analyst'    # View analytics only
      SUPPORT = 'support'    # View chats, respond, no config
  ```
- Expand ChatbotPermission:
  ```python
  role = Column(Enum(Role))
  permissions = Column(JSONB)  # {'can_edit_knowledge', 'can_view_analytics', ...}
  ```
- Add permission checks in API routes
- **Files:** `apps/api/app/models/chatbot.py`, all API routes

### 15. Audit Logging
**Current State:** No audit trail for configuration changes  
**Implementation:**
- Create audit log table:
  ```python
  class AuditLog(Base):
      id = Column(UUID, primary_key=True)
      tenant_id = Column(Integer, ForeignKey('tenants.id'))
      user_id = Column(Integer, ForeignKey('users.id'))
      entity_type = Column(String)  # 'chatbot', 'knowledge_source'
      entity_id = Column(UUID)
      action = Column(String)  # 'create', 'update', 'delete'
      changes = Column(JSONB)  # {'field': {'old': ..., 'new': ...}}
      ip_address = Column(String)
      timestamp = Column(DateTime, server_default=func.now())
  ```
- Add middleware to log all mutations
- Dashboard page to view audit logs
- **Files:** `apps/api/app/models/audit.py`, `apps/api/app/middleware/audit.py`

### 16. CSV/Excel Bulk Q&A Upload
**Current State:** Manual Q&A entry one-by-one  
**Implementation:**
- Add upload endpoint:
  ```python
  @router.post("/{chatbot_id}/knowledge/qa/bulk")
  async def upload_qa_bulk(
      chatbot_id: UUID,
      file: UploadFile = File(...),
      db: AsyncSession = Depends(get_db)
  ):
      # Parse CSV/Excel
      df = pd.read_excel(file.file) if file.filename.endswith('.xlsx') else pd.read_csv(file.file)
      
      # Validate columns: 'question', 'answer'
      if not {'question', 'answer'}.issubset(df.columns):
          raise HTTPException(400, "Missing required columns")
      
      # Create QAPair records
      for _, row in df.iterrows():
          qa = QAPair(chatbot_id=chatbot_id, question=row['question'], answer=row['answer'])
          db.add(qa)
      
      await db.commit()
      # Trigger embedding generation
  ```
- Add UI in Knowledge tab with file upload component
- **Files:** `apps/api/app/api/v1/knowledge.py`, `apps/web/app/dashboard/chatbots/[chatbotId]/page.tsx`

### 17. Webhook System for Integrations
**Current State:** No way to notify external systems  
**Implementation:**
- Webhook configuration:
  ```python
  class Webhook(Base):
      chatbot_id = Column(UUID, ForeignKey('chatbots.id'))
      event = Column(String)  # 'chat.started', 'chat.ended', 'handoff.requested'
      url = Column(String)
      secret = Column(String)  # HMAC signing
      is_active = Column(Boolean, default=True)
  ```
- Send webhooks on events:
  ```python
  async def trigger_webhook(event: str, payload: dict, chatbot_id: UUID):
      webhooks = await get_webhooks(chatbot_id, event)
      for webhook in webhooks:
          signature = hmac.new(webhook.secret.encode(), json.dumps(payload).encode(), 'sha256').hexdigest()
          await httpx_client.post(
              webhook.url,
              json=payload,
              headers={'X-Webhook-Signature': signature}
          )
  ```
- **Files:** `apps/api/app/models/webhook.py`, `apps/api/app/services/webhook_service.py`

---

## 🌐 **Multi-Channel Support**

### 18. WhatsApp Integration
**Implementation:**
- Use Twilio WhatsApp API
- Create adapter:
  ```python
  @router.post("/webhooks/whatsapp")
  async def whatsapp_webhook(request: Request):
      data = await request.json()
      message = data['Body']
      from_number = data['From']
      
      # Get or create session by phone number
      session = await get_or_create_session_by_phone(from_number, chatbot_id)
      
      # Forward to chat service
      response = await ChatService.get_response(db, chatbot_id, message, session.id)
      
      # Send via Twilio
      await twilio_client.messages.create(
          body=response,
          from_=twilio_whatsapp_number,
          to=from_number
      )
  ```
- **Files:** `apps/api/app/api/v1/channels.py`

### 19. Slack Integration
**Implementation:**
- Slack App with Events API
- Handle `message` events:
  ```python
  @router.post("/webhooks/slack")
  async def slack_webhook(request: Request):
      data = await request.json()
      
      if data['type'] == 'url_verification':
          return {'challenge': data['challenge']}
      
      if data['type'] == 'event_callback':
          event = data['event']
          if event['type'] == 'message':
              # Process message through chat service
              # Reply in thread
  ```
- **Files:** `apps/api/app/api/v1/channels.py`

---

## 🔐 **Security Enhancements**

### 20. Rate Limiting Per Chatbot (Not Just IP)
**Current State:** Global IP rate limit (30/min)  
**Problem:** One user can exhaust entire chatbot's quota  
**Implementation:**
- Rate limit by `(chatbot_id, session_id)`:
  ```python
  async def check_chatbot_rate_limit(chatbot_id: UUID, session_id: str):
      key = f"rate:{chatbot_id}:{session_id}"
      count = await redis.incr(key)
      if count == 1:
          await redis.expire(key, 60)
      
      # Get plan limits
      plan_limits = {'free': 10, 'starter': 30, 'pro': 100, 'enterprise': 1000}
      limit = plan_limits[chatbot.tenant.plan]
      
      if count > limit:
          raise HTTPException(429, "Rate limit exceeded for your plan")
  ```
- **Files:** `apps/api/app/api/v1/chat.py`

### 21. Content Security Policy for Widget
**Current State:** Widget injects inline styles (blocked by strict CSP)  
**Implementation:**
- Host CSS file separately:
  ```typescript
  // Instead of injecting styles in head
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = `${config.apiUrl}/static/widget.css`;
  document.head.appendChild(link);
  ```
- Support CSP nonce:
  ```typescript
  if (config.cspNonce) {
      link.nonce = config.cspNonce;
  }
  ```
- **Files:** `packages/chatbot-widget/src/ChatbotWidget.tsx`

---

## 📈 **Observability Beyond Sentry**

### 22. OpenTelemetry Tracing
**Implementation:**
- Add OpenTelemetry:
  ```python
  from opentelemetry import trace
  from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
  
  tracer = trace.get_tracer(__name__)
  
  @tracer.start_as_current_span("generate_embeddings")
  async def generate_embeddings(...):
      # ...
  ```
- Export to Jaeger/Honeycomb/Datadog
- Trace full request: API → DB → HuggingFace → Groq → Response
- **Files:** `apps/api/main.py`, all service files

### 23. Business Metrics Dashboard
**Current State:** Analytics focused on chat metrics  
**Gap:** No business KPIs  
**Implementation:**
- Add business event tracking:
  ```python
  class BusinessEvent(Base):
      session_id = Column(UUID, ForeignKey('chat_sessions.id'))
      event_type = Column(String)  # 'product_viewed', 'add_to_cart', 'purchase'
      metadata = Column(JSONB)
      revenue = Column(Float, nullable=True)
  ```
- Track via postMessage from parent site:
  ```javascript
  window.addEventListener('message', (event) => {
      if (event.data.type === 'business_event') {
          trackBusinessEvent(event.data.event_type, event.data.metadata);
      }
  });
  ```
- Dashboard showing ROI: Revenue attributed to chatbot interactions
- **Files:** `apps/api/app/models/events.py`, `packages/chatbot-widget/src/ChatbotWidget.tsx`

---

## ⚡ **Performance Optimizations**

### 24. Database Connection Pooling Optimization
**Current State:** Default SQLAlchemy async pool  
**Implementation:**
- Tune pool for production:
  ```python
  engine = create_async_engine(
      DATABASE_URL,
      echo=False,
      pool_size=20,           # Higher for production
      max_overflow=10,        # Allow bursts
      pool_timeout=30,
      pool_pre_ping=True,     # Verify connections
      pool_recycle=3600       # Recycle after 1 hour
  )
  ```
- **Files:** `apps/api/app/core/database.py`

### 25. Response Streaming Optimization
**Current State:** Stream token-by-token from Groq  
**Problem:** Too many small SSE events  
**Implementation:**
- Buffer tokens before yielding:
  ```python
  buffer = ""
  async for chunk in groq_stream:
      buffer += chunk
      if len(buffer) >= 20 or chunk.endswith(('.', '!', '?')):
          yield buffer
          buffer = ""
  ```
- **Files:** `apps/api/app/services/chat_service.py`

---

**Document Version:** 1.0  
**Last Updated:** February 12, 2026  
**Estimated Total Effort:** 300+ hours (6+ months)
