# Multi-Model Comparison Report — Final

**Date:** 2026-02-21  
**Test Runs:** 3 rounds (Run 1 + Run 2 via direct API, Run 3 via OpenRouter multi-key)  
**Total Evaluations:** 200+ individual query-model evaluations  
**Queries Tested:** 21 diverse queries — product browsing (en/hi/gu), price filtering (en/hi/gu), irrelevant detection (en/hi/gu), missing info (en/hi), greetings (en/hi/gu), romanized input (hi-Latn/gu-Latn), non-product (en/hi), ambiguous, edge cases, unsupported language (French)

---

## Final Rankings — All Data Combined

### Call 1 — Query Analysis (JSON output)

| Rank | Model | Tested | Score | Latency | JSON% | Lang% | Product% |
|------|-------|--------|-------|---------|-------|-------|----------|
| 🥇 1 | **gemini-2.5-flash-lite** (direct API) | 19/21 | **3.84/4** | 1604ms | 100% | **84%** | **100%** |
| 🥈 2 | **OR-gemini-2.5-flash** (OpenRouter) | 14/21 | **3.79/4** | **959ms** | 100% | **86%** | **100%** |
| 🥉 3 | OR-gemini-2.5-flash-lite (OpenRouter) | 14/21 | 3.64/4 | **743ms** | 100% | 71% | **100%** |
| 4 | OR-gemini-2.0-flash (OpenRouter) | 21/21 | 3.62/4 | 1820ms | 100% | 71% | 95% |
| 5 | llama-3.1-8b (Groq) | 21/21 | 3.33/4 | 699ms | 100% | 43% | 90% |

### Call 2 — Response Generation

| Rank | Model | Tested | Score | Latency | Lang% | Irrel% | Sugg% | NoLeak% |
|------|-------|--------|-------|---------|-------|--------|-------|---------|
| 🥇 1 | **OR-gemini-2.5-flash-lite** (OpenRouter) | 14/21 | **5.00/5** ⭐ | **1035ms** | 100% | **100%** | **100%** | 100% |
| 🥈 2 | OR-gemini-2.5-flash (OpenRouter) | 14/21 | 4.86/5 | 1383ms | 100% | 86% | 100% | 100% |
| 🥉 3 | OR-gemini-2.0-flash (OpenRouter) | 14/21 | 4.79/5 | 1310ms | 100% | 86% | 93% | 100% |
| 4 | llama-3.3-70b (Groq) | 21/21 | 4.76/5 | 1578ms | 100% | 100% | 76% | 100% |

---

## Key Insight: gemini-2.5-flash-lite is the Star

**OR-gemini-2.5-flash-lite achieved a PERFECT 5.00/5 score on Call 2** — the only model to do so across all 14 tested queries. It also:
- Had **100% suggestion generation** (always adds `---SUGGESTIONS---` block correctly)
- Had **100% irrelevant query detection** (correctly used `[IRRELEVANT_QUERY]` marker every time)
- Was the **fastest Gemini model** at both Call 1 (743ms) and Call 2 (1035ms)

---

## Recommended Configuration

### Option A — Best Quality (Recommended)

```
Call 1: google/gemini-2.5-flash      (OpenRouter, ~960ms)  →  fallback: llama-3.1-8b (Groq, ~700ms)
Call 2: google/gemini-2.5-flash-lite (OpenRouter, ~1035ms) →  fallback: llama-3.3-70b (Groq, ~1578ms)
```

**Rationale:**
- `gemini-2.5-flash` for Call 1 — best language detection among OR models (86%) + strong score (3.79/4)
- `gemini-2.5-flash-lite` for Call 2 — perfect score (5.00/5), fastest (1035ms), 100% in every metric
- OR key rotation with 4 keys ensures no single-key credit exhaustion
- Groq fallback guarantees 100% uptime even if OR has issues

**Expected end-to-end latency:** ~2000ms (vs ~3130ms current) — **36% faster**

### Option B — Simplest Upgrade (Same model everywhere)

```
Call 1: google/gemini-2.5-flash-lite (OpenRouter, ~743ms)  →  fallback: llama-3.1-8b
Call 2: google/gemini-2.5-flash-lite (OpenRouter, ~1035ms) →  fallback: llama-3.3-70b
```

**One model for everything** — simpler config, scores 3.64/4 Call 1 + 5.00/5 Call 2.  
**E2E latency:** ~1800ms — **42% faster than current setup.**

### Option C — Zero Cost (Groq Only)

```
Call 1: llama-3.1-8b (Groq)   — fast (700ms) but weak Hindi/Gujarati detection (43%)
Call 2: llama-3.3-70b (Groq)  — reliable (4.76/5) but misses suggestions for irrelevant queries
```

**Free forever, works right now.** Main limitation: poor native-script language detection.

---

## Detailed Analysis

### Call 1: Language Detection

The single biggest differentiator between models is **native-script language detection**:

| Input | Expected | gemini-2.5-flash (OR) | gemini-2.5-flash-lite (OR) | gemini-2.0-flash (OR) | llama-3.1-8b |
|-------|----------|----------------------|---------------------------|----------------------|-------------|
| `मुझे ground coffee दिखाओ` (Devanagari) | `hindi` | ✅ | ⚠️ sometimes `hindi-latin` | ❌ `hindi-latin` | ❌ `hindi-latin` |
| `તમારા bracelets બતાવો` (Gujarati) | `gujarati` | ✅ | ✅ | ❌ `gujarati-latin` | ❌ `gujarati-latin` |
| `mujhe coffee dikhao` (Latin) | `hindi-latin` | ✅ | ✅ | ✅ | ✅ |
| `Bonjour...` (French) | `other` | ✅ | ✅ | ✅ | ❌ `english` |

**Impact on UX:** If Call 1 returns `hindi-latin` for a Devanagari Hindi query, the response model usually still detects the script and responds correctly. But incorrect language metadata affects response language selection logic in the chatbot backend — so better Call 1 accuracy = fewer language mismatches.

### Call 2: Why gemini-2.5-flash-lite Wins

The 2 main areas where `gemini-2.5-flash` and `gemini-2.0-flash` fall short:

**1. Irrelevant query detection (86%)**  
Failed for "missing_info" type queries — models incorrectly flagged "What are your CEO's contact details?" as `[IRRELEVANT_QUERY]` (it should be `missing_info`, answered politely). `gemini-2.5-flash-lite` handled all such nuances correctly.

**2. Suggestion generation (93% for gemini-2.0-flash)**  
`OR-gemini-2.0-flash` skipped the `---SUGGESTIONS---` block on Gujarati greetings. The lite/2.5-flash models followed the prompt instruction perfectly (100%).

**llama-3.3-70b weakness:**  
Consistently omits suggestions for irrelevant and non-product queries (return policy, delivery questions), dropping its score to 4/5 on those 5 query types. The model interprets "don't suggest products to irrelevant queries" as correct behavior — but our prompt says "EVERY response."

### Latency Comparison

| Configuration | Call 1 | Call 2 | Total |
|---------------|--------|--------|-------|
| gemini-2.5-flash + gemini-2.5-flash-lite (Rec. A) | ~959ms | ~1035ms | **~2000ms** |
| gemini-2.5-flash-lite + gemini-2.5-flash-lite (Rec. B) | ~743ms | ~1035ms | **~1780ms** |
| OR-gemini-2.0-flash for both (current prod) | ~1820ms | ~1310ms | **~3130ms** |
| Groq only | ~699ms | ~1578ms | **~2280ms** |

---

## Action Items

### To implement Recommendation A or B:

1. **Update `.env`** (already done — OPENROUTER_API_KEYS has all 4 keys)
2. **Update `OPENROUTER_CALL1_MODEL`** in `.env`:
   - Rec A: `google/gemini-2.5-flash`
   - Rec B: `google/gemini-2.5-flash-lite`
3. **Update `OPENROUTER_CALL2_MODEL`** in `.env`:
   - Both: `google/gemini-2.5-flash-lite`
4. **Add OR key rotation to `chat_service.py`** — same round-robin pattern as `GROQ_API_KEYS`
5. **Strengthen Groq Call 2 fallback prompt** (optional) — explicitly instruct to add suggestions even for irrelevant queries to get 5.00/5 from the fallback too

### Credit management:
- Each OR free account starts with ~$1 credit (~5000 lite queries, ~2000 flash queries)
- With 4 keys × $1 = ~$4 effective budget (then top-up as needed, min $5)
- Groq fallback ensures zero downtime even when OR credits deplete

---

## Raw Data Files
- `model_comparison_results.json` — Run 1 + Run 2 data
- `openrouter_retest_results.json` — Run 3 data (OR multi-key Gemini 2.5)
- Test scripts: `test_model_comparison.py`, `test_openrouter_retest.py`
