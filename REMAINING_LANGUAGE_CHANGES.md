# Remaining Changes for Multi-Language & Personality Features

## Status: What's Done

| Area                                                                                                 | Status |
| ---------------------------------------------------------------------------------------------------- | ------ |
| Backend model fields (personality_tone, response_length, temperature, custom_instructions, language) | Done   |
| Backend schemas (appearance.py, chatbot.py)                                                          | Done   |
| Alembic migration (applied to DB)                                                                    | Done   |
| Chat service — personality/language in system prompt                                                 | Done   |
| Chat service — language-aware suggestions (Hindi/Gujarati examples)                                  | Done   |
| Chat service — language-aware product carousel instruction                                           | Done   |
| Chat service — Hindi/Gujarati product keywords                                                       | Done   |
| Chat service — Hindi/Gujarati greeting detection                                                     | Done   |
| Chat service — Hindi/Gujarati referential language patterns                                          | Done   |
| Chat service — Hindi/Gujarati price filter patterns                                                  | Done   |
| Chat service — Hindi/Gujarati gender/attribute filters                                               | Done   |
| Chat service — Hindi/Gujarati contact patterns                                                       | Done   |
| Ranker service — Hindi/Gujarati query complexity keywords                                            | Done   |
| Chatbot service — branding enforcement for free tier                                                 | Done   |
| Widget config API — returns language, personality fields                                             | Done   |
| Frontend page.tsx — appearance tab with personality/language controls                                | Done   |
| Widget — voice input (Web Speech API with hi-IN, gu-IN, en-US)                                       | Done   |
| Widget — language-aware default texts (welcome, placeholder, listening)                              | Done   |
| Widget types.ts — language field in ChatbotConfig                                                    | Done   |

---

## What Still Needs To Be Done

### 1. CRITICAL — Embedding Model is English-Only

- **File:** `apps/api/app/core/config.py` (line 92)
- **Issue:** Current model is `BAAI/bge-small-en-v1.5` — an English-only embedding model
- **Impact:** When a user types in Hindi/Gujarati, the vector search will return poor matches because the query embedding (in Hindi/Gujarati) won't match English knowledge base embeddings
- **Fix Options:**
  - **Option A (Recommended):** Switch to a multilingual embedding model like `BAAI/bge-m3` or `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Requires re-embedding all existing knowledge.
  - **Option B (Quick fix):** Add a translation step before embedding — use the LLM to translate non-English queries to English before the vector search, while keeping the original message for the LLM response. This avoids re-embedding.

### 2. WidgetPreview Missing Language Prop

- **File:** `apps/web/components/chatbot/WidgetPreview.tsx`
- **Issue:** The `WidgetPreviewProps` interface and the component do not accept `language`, `personality_tone`, `response_length`, or `temperature` props
- **Impact:** Preview widget in the dashboard won't reflect language changes (e.g., welcome message stays in English during preview)
- **Fix:** Add `language` to `WidgetPreviewProps` and pass it into the `config` object. Also update `page.tsx` line ~4065 to pass `language={watchedAppearanceValues.language}` to `<ChatbotWidgetPreview>`

### 3. Docker Rebuild Required

- **Containers that need rebuilding:**
  - `api` — All chat_service.py, ranker_service.py changes
  - `widget` — ChatbotWidget.tsx language-aware defaults
  - `web` — page.tsx already rebuilt, but WidgetPreview.tsx fix (item #2) will need another build
- **Command:** `docker-compose up -d --build api widget web`

### 4. Query Translation for RAG Retrieval (if not switching embedding model)

- **File:** `apps/api/app/services/chat_service.py` around line ~1816
- **Issue:** The `enriched_query` sent to `get_single_embedding()` is in the user's language. If knowledge base is in English and query is in Hindi, cosine similarity will be near-zero
- **Fix:** Before embedding the query, detect if `language != "en"` and use the LLM (quick lightweight call) to translate the query to English for retrieval, while keeping the original text for the response generation
- **Example flow:**
  ```
  User types: "सोने की अंगूठी दिखाओ" (Hindi for "show gold rings")
  → Translate to English for embedding: "show gold rings"
  → Vector search finds gold ring products
  → LLM responds in Hindi: "यहाँ कुछ सोने की अंगूठियां हैं!"
  ```

### 5. Initial Suggestions Language Support

- **File:** `apps/web/app/dashboard/chatbots/[chatbotId]/page.tsx`
- **Issue:** The initial suggestions (quick-reply buttons shown below welcome message) are user-configured in the dashboard and are typically in English. When language is changed to Hindi/Gujarati, these suggestions won't auto-translate
- **Fix Options:**
  - Let users manually set suggestions per language in the dashboard
  - Or auto-translate suggestions based on selected language (more complex)
  - Or add a note in the UI: "Tip: Set initial suggestions in your selected language"

### 6. Color Keywords for Hindi/Gujarati

- **File:** `apps/api/app/services/chat_service.py` — `COLOR_KEYWORDS` list (line ~180)
- **Issue:** Color keywords are only in English. If user says "लाल रंग" (red) or "લાલ રંગ" in Hindi/Gujarati, color filters won't work
- **Fix:** Add Hindi/Gujarati color words: लाल/લાલ (red), नीला/વાદળી (blue), हरा/લીલો (green), पीला/પીળો (yellow), काला/કાળો (black), सफेद/સફેદ (white), etc.

### 7. BM25 Hybrid Search Hindi/Gujarati Support

- **File:** `apps/api/app/services/chat_service.py` (hybrid search section, around line ~1850+)
- **Issue:** The tsvector/BM25 search uses PostgreSQL full-text search which is configured for English. Hindi/Gujarati text won't tokenize properly
- **Impact:** The BM25 portion (30% weight) of hybrid search will return zero results for non-English queries
- **Fix:** Either disable BM25 for non-English queries, or configure PostgreSQL with appropriate language dictionaries

### 8. Cache Key Language Awareness

- **File:** `apps/api/app/services/chat_service.py` (around line ~1733)
- **Issue:** Cache key is based on `chatbot_id + text_content`. Two identical queries in different languages could theoretically collide (unlikely but possible with translations)
- **Fix:** Include `language` in the cache key: `cache_key = f"{chatbot_id}:{language}:{text_content}"`

---

## Priority Order

1. **#3 Docker Rebuild** — Deploy existing fixes (no code change)
2. **#1 or #4 Embedding/Translation** — Without this, Hindi/Gujarati queries won't find relevant content at all
3. **#2 WidgetPreview** — Small fix, improves dashboard preview
4. **#6 Color Keywords** — Quick addition
5. **#7 BM25 for non-English** — Disable BM25 when language ≠ "en"
6. **#8 Cache Key** — Minor safeguard
7. **#5 Suggestions** — UX improvement, not blocking
