# Quick Testing Guide for Chatbot Response Fixes

## 🧪 Test These Scenarios

### Test 1: Filter Violation Check ❌➜✅
**Before**: Bot shows ₹8299 when asked for "under ₹1000"
**Now**: Bot ONLY shows items under ₹1000

```
User: "Show me products under ₹1000"
Expected Backend Behavior:
  - extract_price_filter() extracts max_price=1000
  - extract_products_from_chunks() filters:
    * Skip if price_value > 1000
    * Skip if price_value is None (when filter applied)
Expected LLM Behavior:
  - LLM never knows about ₹1000 filter
  - LLM gives natural response like "Here are some options for you!"
Expected Frontend:
  - Carousel shows ONLY products ≤ ₹1000
  - NO "close to budget" items
```

---

### Test 2: Product Listing in Text ❌➜✅
**Before**: Bot lists "1. Product A - ₹500, 2. Product B - ₹800..."
**Now**: Bot says "Here are our products!" (carousel shows details)

```
User: "Show me watches" or "What products do you have?"
Expected LLM Response:
  - Short intro: "Here are our watches!" or "Check out our collection!"
  - 1-2 sentences max
  - NO product names
  - NO prices
  - NO enumerated lists
Expected Frontend:
  - Clean text message
  - Product carousel below with all details
```

**How to Verify**:
1. Send query asking for products
2. Check LLM text response
3. Should NOT contain specific product names/prices
4. Should NOT have numbered lists like "1. Product A..."

---

### Test 3: Suggestions Context-Aware ❌➜✅
**Before**: Same suggestions every time: "Show products", "Filter by price", "Show more"
**Now**: Suggestions adapt to conversation state

```
Scenario A - Greeting:
User: "Hi"
Expected Suggestions:
  - "What products do you offer?"
  - "Tell me about your store"
  - "Show me bestsellers"

Scenario B - Products with Price Filter:
User: "Show watches under ₹3000"
Products Returned: 5 items
Expected Suggestions:
  - "Show different styles"
  - "What colors are available?"
  - "Show me your bestsellers"

Scenario C - No Products Found:
User: "Show products under ₹100"
Products Returned: 0 items
Expected Suggestions:
  - "Show all available products"
  - "What's your price range?"
  - "Tell me about your products"

Scenario D - Color Filter Applied:
User: "Show me blue watches"
Products Returned: 3 items
Expected Suggestions:
  - "Filter by price range"
  - "Show me budget options"
  - "What's on sale?"
```

**How to Verify**:
1. Test each scenario above
2. Check suggestions array in response
3. Verify they're different for each scenario
4. Verify they're actionable (not questions)

---

### Test 4: Multiple Filters ✅
**New Capability**: Combining price + attribute filters

```
User: "Show me blue watches under ₹2000"
Expected Extraction:
  - price_filter = {max_price: 2000}
  - attribute_filter = {colors: ['blue']}
Expected Filtering:
  - Skip if price > 2000
  - Skip if 'blue' not in product_text
  - Skip if price is None (filter requested)
Expected LLM:
  - No knowledge of filters
  - Natural response
Expected Suggestions:
  - "Show different styles"
  - "What colors are available?"
  - "Show me your bestsellers"
```

---

## 🔍 What to Look For

### ✅ Good Signs
1. **LLM text is minimal** when products are shown
2. **No product names/prices in text**, only in carousel
3. **Strict filter adherence** - no items outside range
4. **Suggestions change** based on context
5. **No "close to your budget" messages**
6. **No question-style suggestions** ("What is your budget?")

### ❌ Bad Signs (Report if you see these)
1. LLM lists products with prices in text
2. Products outside filter range shown
3. "Close to budget" or similar compensating language
4. Same suggestions regardless of context
5. Suggestions that are questions ("What is...?", "How much...?")
6. Products without prices shown when filter applied

---

## 🐛 Debug Checklist

If issues occur, check:

### Backend Logs
```bash
# Look for these log messages:
"Extracted price range: {'max_price': 1000}"
"Extracted color filters: ['blue']"
"Skipping product X - price Y > max Z"
"Skipping product X - no price data, but filter requested"
```

### LLM Context (System Prompt)
Should NOT contain:
- ❌ "Price Filter: Under 1000"
- ❌ "Color Filter: blue"
- ❌ "STRICTLY only mention products..."

Should contain:
- ✅ "Background Context: {summary}{image_context}"
- ✅ General textual content
- ✅ "Keep Responses Natural"

### Product Metadata
Check chunks sent to LLM - metadata should NOT include:
- ❌ `'product': {...}`
- ❌ `'is_product': True`
- ❌ Product price/name/details

Should only include:
- ✅ `'title': "Page Title"`
- ✅ `'url': "https://..."`
- ✅ General text content

---

## 📊 Key Metrics to Monitor

1. **Filter Accuracy**: 100% of products shown must match filter
2. **Text Cleanliness**: 0 product names/prices in LLM response text
3. **Suggestion Variety**: >5 different suggestion sets across scenarios
4. **User Satisfaction**: No "close to budget" complaints

---

## 🚀 Quick Smoke Test

Run this sequence:

```
1. "Hi" → Check suggestions are intro-focused
2. "Show watches" → Check no product listing in text
3. "Show watches under ₹2000" → Check all products ≤ ₹2000
4. "Show blue watches under ₹1500" → Check blue + price filters
5. "Show watches under ₹50" → Check suggestions adapt to no-results
```

If all 5 pass ✅, the fix is working!

---

## 💡 Pro Tips

### For Product Queries
- Products should ONLY appear in carousel
- Text should be 1-2 sentences max
- NO enumeration in text

### For Filters
- Backend enforces, LLM never knows
- If filter + no price → skip product
- No "close to", "around", "near" language

### For Suggestions
- Should read like what USER would say
- NOT what bot would ask
- Actionable, specific, contextual

---

## 📝 Report Template

If you find issues, report using this format:

```
**Issue**: [Brief description]

**User Query**: "Show watches under ₹1000"

**Expected**:
- Products: Only items ≤ ₹1000
- Text: Minimal, no product listing
- Suggestions: Context-aware

**Actual**:
- Products: [What you got]
- Text: [Copy LLM response]
- Suggestions: [List suggestions]

**Backend Logs**: [Paste relevant logs]

**Screenshots**: [If applicable]
```

---

## ⚡ Fast Verification Commands

```bash
# Check if product metadata is stripped from context
grep -A5 "clean_meta = " apps/api/app/services/chat_service.py

# Check if price context is removed
grep "price_context" apps/api/app/services/chat_service.py

# Check if smart suggestions function exists
grep -A10 "_generate_smart_suggestions" apps/api/app/services/chat_service.py

# Run backend
cd apps/api
python run.py

# Watch logs for filter enforcement
tail -f logs/app.log | grep "Skipping product"
```

---

## 🎯 Success Criteria

All three issues MUST be resolved:

1. ✅ **Product carousel rules respected**
   - No product details in LLM text
   - Only in carousel component

2. ✅ **Filter rules strictly enforced**
   - 100% backend enforcement
   - No filter violations
   - No "close to budget"

3. ✅ **Suggestions are smart**
   - Context-aware
   - Not repetitive
   - Actionable

If all ✅, deployment approved! 🚀
