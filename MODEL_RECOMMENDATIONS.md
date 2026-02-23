# MODEL & ARCHITECTURE RECOMMENDATIONS

> Generated based on comprehensive research of Google Gemini, OpenRouter, Groq, and DeepSeek pricing/capabilities.
> Current setup: OpenRouter (Gemini 2.0 Flash) PRIMARY → Groq (Llama 3.3 70B) FALLBACK

---

## 1. BEST FREE MODEL RECOMMENDATIONS

### WINNER: Google Gemini Direct API (FREE Standard Tier)

Google provides **completely free** access to their best models directly (not via OpenRouter). This is the single biggest upgrade you can make — **zero cost, better quality**.

| Model | Cost | Context | Best For | Notes |
|---|---|---|---|---|
| **Gemini 2.5 Flash** | FREE | 1M tokens | Call 2 (main response) | Hybrid reasoning, much smarter than 2.0 Flash |
| **Gemini 2.5 Flash-Lite** | FREE | 1M tokens | Call 1 + Translation | Fastest, cheapest — perfect for structured tasks |
| **Gemini 2.5 Pro** | FREE | 1M tokens | Premium quality option | Best quality but lower rate limits |
| **Gemini 2.0 Flash** | FREE | 1M tokens | Current model | What you're using now via OpenRouter |
| **Gemini 3 Flash Preview** | FREE | 1M tokens | Experimental | Newest, still in preview |

**How to use:**
- Endpoint: `https://generativelanguage.googleapis.com/v1beta/openai/` (OpenAI-compatible!)
- Get API key from: https://aistudio.google.com/apikey
- Works with your existing OpenAI client code — just change `base_url` and `api_key`

**Rate Limits (Free Standard Tier):**
- Gemini 2.5 Flash: 500 RPM, 250K TPM
- Gemini 2.5 Flash-Lite: 500 RPM, 250K TPM
- Gemini 2.5 Pro: 150 RPM, 100K TPM

### Recommended Setup (ALL FREE):

```
Call 1 (language detection + enrichment):
  PRIMARY:  Gemini 2.5 Flash-Lite  (Google Direct API) — FREE, super fast
  FALLBACK: Llama 3.1 8B           (Groq) — FREE tier

Call 2 (main streaming response):
  PRIMARY:  Gemini 2.5 Flash       (Google Direct API) — FREE, hybrid reasoning
  FALLBACK: Llama 3.3 70B          (Groq) — FREE tier

Translation:
  PRIMARY:  Gemini 2.5 Flash-Lite  (Google Direct API) — FREE, fast
  FALLBACK: Llama 3.1 8B           (Groq) — FREE tier
```

### Why Gemini 2.5 Flash > 2.0 Flash (current):
- **Hybrid reasoning**: Can "think" before answering for complex queries
- **Better instruction following**: Less likely to ignore language rules or delimiter requirements
- **Better multilingual**: Significantly improved Hindi/Gujarati quality
- **Same cost**: Both are FREE on Google's direct API
- **1M context**: Same as 2.0 Flash

---

## 2. ALTERNATIVE FREE OPTIONS (OpenRouter)

These 27 models are free on OpenRouter (with aggressive rate limits):

| Model | Context | Quality | Speed | Best For |
|---|---|---|---|---|
| **DeepSeek R1 0528** | 164K | Excellent reasoning | Slow | Complex queries (not for streaming) |
| **OpenAI GPT-OSS 120B** | 131K | Very good | Medium | General purpose alternative |
| **StepFun Step 3.5 Flash** | 256K | Good | Fast | Quick tasks |
| **GLM 4.5 Air** | 131K | Good | Fast | Chinese/multilingual |
| **NVIDIA Nemotron 3 Nano** | 256K | Decent | Very fast | Lightweight tasks |
| **Arcee Trinity Large** | 131K | Good | Medium | General purpose |
| **Arcee Trinity Mini** | 131K | OK | Fast | Simple tasks |

**Note:** OpenRouter free models have very low rate limits (~20 RPM). Not recommended as primary — use as emergency fallback only.

---

## 3. GROQ FREE TIER (Current Fallback — KEEP)

| Model | Input Cost | TPM | RPM | Notes |
|---|---|---|---|---|
| **Llama 3.1 8B** | $0.05/M | 250K | 1,000 | Fast, good for Call 1 |
| **Llama 3.3 70B** | $0.59/M | 300K | 1,000 | Good quality for Call 2 fallback |
| **Qwen3-32B** | $0.29/M | 300K | 1,000 | Good multilingual alternative |
| **GPT-OSS 120B** | $0.15/M | 250K | 1,000 | Largest free model |

Groq has generous free tier with high RPM (1,000). **Keep as fallback** — it's excellent for that role.

---

## 4. DEEPSEEK V3 EVALUATION

**Model:** deepseek-chat (V3.2)  
**Endpoint:** `https://api.deepseek.com/v1`

| Metric | Cost |
|---|---|
| Input (cache hit) | $0.028/M tokens |
| Input (cache miss) | $0.28/M tokens |
| Output | $0.42/M tokens |

**Prompt Caching:** DeepSeek automatically caches system prompts. Since your system prompt is ~2000 tokens and identical across requests for the same bot, you'd get ~90% cache hits after warmup. Effective cost: ~$0.03/M input for most requests.

**Verdict:**
- NOT free, but extremely cheap (~10x cheaper than GPT-4o)
- Excellent multilingual (Hindi, Gujarati work well)
- Good instruction following
- **Recommendation:** Consider for production scale later. For now, Google Gemini Direct (FREE) is better since you want free.

---

## 5. EMBEDDINGS ADVICE (bge-m3)

### Current: `sentence-transformers/all-MiniLM-L6-v2`
- 384 dimensions
- English-only
- Fast, lightweight
- Requires translation to English before retrieval (your Call 1 does this)

### Recommended Upgrade: `BAAI/bge-m3`
- 1024 dimensions
- **100+ languages natively** (Hindi, Gujarati, English, all work)
- Maps all languages into the **same vector space**
- Supports dense, sparse, and ColBERT retrieval

### Key Benefits:
1. **Hindi/Gujarati queries can directly search English product data** — no translation needed for retrieval
2. **"સસ્તા shirts છે?" would match "affordable shirts" in English** embeddings
3. **Eliminates translation as a retrieval bottleneck** — Translation would only be needed for the LLM prompt, not for vector search
4. **Better semantic matching overall** — bge-m3 is a much larger, more capable model

### Migration Impact:
- **ALL existing embeddings must be regenerated** — MiniLM (384d) and bge-m3 (1024d) are incompatible vector spaces
- Database vector column needs resizing: 384 → 1024 dimensions
- Embedding generation is ~3x slower (larger model)
- Vector index needs rebuilding
- **One-time migration, permanent benefit**

### Can bge-m3 search existing MiniLM embeddings?
**NO.** You cannot mix embedding models. All data must be re-embedded with bge-m3. But this is a one-time operation — run a migration script on all stored product/page data.

### Should You Do It Now?
- If you have < 10K products across all bots: **Yes, easy migration** (minutes)
- If you have > 100K products: Plan a migration window
- **Recommendation:** Do it when you're ready. It's a clear upgrade but not urgent since your translation step handles multilingual retrieval adequately today.

---

## 6. ARCHITECTURE SUGGESTIONS

### Current Architecture (Good):
```
User Query → Call 1 (language detect + translate + enrich)
           → Vector Search (MiniLM, English)
           → Call 2 (stream response with context)
           → SSE to client
```

### Suggested Improvements:

#### A. Switch to Google Gemini Direct API (HIGH PRIORITY, EASY)
- Replace OpenRouter with direct Google Generative AI endpoint
- Same OpenAI-compatible format — minimal code change
- Upgrade from Gemini 2.0 Flash → 2.5 Flash
- **Impact:** Better quality, still free, less dependency on OpenRouter

#### B. Use Gemini's Native JSON Mode for Call 1 (MEDIUM PRIORITY)
- Gemini supports `response_format={"type": "json_object"}` natively
- More reliable structured output for language detection + query enrichment
- Fewer parsing failures on the JSON response from Call 1
- **Impact:** More robust Call 1 parsing

#### C. Replace Embeddings with bge-m3 (MEDIUM PRIORITY)
- Enables cross-lingual retrieval without translation
- Could potentially simplify Call 1 (no need to translate for retrieval)
- Call 1 still needed for: language detection, query enrichment, intent classification
- **Impact:** Better retrieval quality, especially for non-English queries

#### D. Add Provider Health Monitoring (LOW PRIORITY)
- Track response times, error rates, and token usage per provider
- Auto-switch to fallback if primary latency exceeds threshold (e.g., 5s)
- Store metrics in Redis for dashboard display
- **Impact:** Better reliability, visibility

#### E. Implement Prompt Caching Strategy (LOW PRIORITY, FOR PAID MODELS)
- If you switch to DeepSeek later, their automatic prompt caching would save ~90% on input costs
- For Gemini, context caching is available on paid tier
- Not relevant while using free tier
- **Impact:** Major cost savings when you scale to paid

### What NOT to Change:
- **2-call architecture is solid** — Don't merge Call 1 and Call 2. The separation gives you translation, intent classification, AND streaming, which a single call can't do efficiently.
- **SSE streaming** — This is the right approach for real-time chat UX.
- **Groq as fallback** — Keep it. Groq's high RPM and low latency make it an excellent safety net.

---

## 7. IMPLEMENTATION PRIORITY

| Priority | Action | Effort | Impact |
|---|---|---|---|
| 1 | Switch to Google Gemini Direct API | Low (1-2 hrs) | Better quality, independent of OpenRouter |
| 2 | Upgrade to Gemini 2.5 Flash | None (model name change) | Significantly better responses |
| 3 | Use Gemini 2.5 Flash-Lite for Call 1 | None (model name change) | Faster, still free |
| 4 | Add JSON mode to Call 1 | Low (add response_format param) | More reliable parsing |
| 5 | Migrate to bge-m3 embeddings | Medium (migration script) | Better multilingual search |
| 6 | Add provider health monitoring | Medium | Better reliability |
| 7 | Evaluate DeepSeek for production | Low (testing) | Future cost optimization |

---

## 8. QUICK START: Switching to Google Gemini Direct

In your `.env`:
```env
# Replace OpenRouter with Google Direct
GOOGLE_AI_API_KEY=your-key-from-aistudio.google.com

# Model names for Google Direct API
GEMINI_CALL1_MODEL=gemini-2.5-flash-lite
GEMINI_CALL2_MODEL=gemini-2.5-flash
GEMINI_TRANSLATION_MODEL=gemini-2.5-flash-lite
```

In your code (client initialization):
```python
from openai import AsyncOpenAI

google_client = AsyncOpenAI(
    api_key=settings.GOOGLE_AI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
```

That's it — same `chat.completions.create()` calls, same streaming, everything works.
