# Vision Service - Setup & Testing Guide

## Quick Fix Applied

✅ **Updated Groq model** from `llama-3.2-11b-vision-preview` (decommissioned) to `llama-3.2-90b-vision-preview`

✅ **Priority order**: Gemini first (better free tier), then Groq as fallback

✅ **Enhanced error handling** with detailed error messages

## Setup Instructions

### 1. Get API Keys (at least one required)

#### Option A: Google Gemini (Recommended - Free)

- Go to: https://makersuite.google.com/app/apikey
- Click "Create API Key"
- Copy your API key
- **Free tier**: 1,500 requests/day

#### Option B: Groq (Alternative - Free)

- Go to: https://console.groq.com/keys
- Create an account and generate API key
- **Free tier**: 30 requests/minute

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# Vision Model Configuration
VISION_MODEL_PROVIDER=gemini

# Gemini API Key (Recommended)
GEMINI_API_KEY=your-gemini-api-key-here

# Groq API Key (Optional fallback)
GROQ_API_KEY=your-groq-api-key-here
```

### 3. Test the Setup

Run the test script:

```bash
cd apps/api
python test_vision.py
```

Expected output:

```
🚀 Starting Vision Service Tests...

============================================================
VISION SERVICE TEST
============================================================

📋 Configuration:
  - VISION_MODEL_PROVIDER: gemini
  - GEMINI_API_KEY: ✅ Set
  - GROQ_API_KEY: ✅ Set

🔍 Testing with sample image...
  - Image downloaded: 12345 bytes

⏳ Running vision analysis...

✅ Analysis Results:
  - Confidence: 0.85
  - Product Type: shoes
  - Category: footwear
  - Primary Color: red
  ...

✅ All tests passed!
```

## How It Works

### 1. **Multi-Provider Support**

```python
# Automatically uses best available provider
result = await VisionService.analyze_image(image_bytes)
```

The service will:

- Try Gemini first (if API key exists)
- Fallback to Groq if Gemini fails
- Return error if both fail

### 2. **Smart Query Building**

```python
primary, detailed = VisionService.build_combined_query(
    user_message="show me red ones",  # User text overrides
    image_attrs=result                 # Image provides base info
)
# Result: "red shoes" (color from user, product from image)
```

### 3. **Context-Aware Analysis**

```python
result = await VisionService.analyze_image(
    image_bytes=image_bytes,
    user_context="I'm looking for jewelry",  # Helps focus the analysis
    quick_mode=False  # Full detailed analysis
)
```

## Configuration Options

### VISION_MODEL_PROVIDER

Set which provider to use first:

```env
# Use Gemini first (recommended)
VISION_MODEL_PROVIDER=gemini

# Or use Groq first
VISION_MODEL_PROVIDER=groq
```

### Model Details

| Provider   | Model                        | Free Tier     | Best For       |
| ---------- | ---------------------------- | ------------- | -------------- |
| **Gemini** | gemini-1.5-flash             | 1,500 req/day | Production use |
| **Groq**   | llama-3.2-90b-vision-preview | 30 req/min    | High accuracy  |

## Troubleshooting

### Error: "No API keys configured"

**Solution**: Add at least one API key (GEMINI_API_KEY or GROQ_API_KEY) to your `.env` file

### Error: "Groq model decommissioned"

**Solution**: Already fixed! The code now uses `llama-3.2-90b-vision-preview`

### Error: "Gemini API error: 400"

**Possible causes**:

1. Invalid API key - check your key is correct
2. API quota exceeded - wait or switch to Groq
3. Invalid image format - ensure image is PNG/JPEG/WEBP

### Low confidence results

**Tips**:

- Use clear, well-lit product images
- Avoid blurry or low-resolution images
- Include user text context for better results

## API Response Format

```python
ImageAttributes(
    product_type="sneakers",
    category="footwear",
    subcategory="running shoes",
    primary_color="navy blue",
    secondary_colors=["white", "orange"],
    pattern="solid",
    material="synthetic leather",
    style="sporty",
    occasion="casual",
    gender_target="unisex",
    notable_features=["cushioned sole", "breathable mesh"],
    confidence=0.87,
    needs_clarification=False
)
```

## Integration in Chat

The vision service is automatically integrated in the chat endpoint:

```python
# POST /api/v1/chatbots/{chatbot_id}/chat
# with multipart/form-data:
# - message: "show me similar ones"
# - image: [uploaded file]

# The system will:
# 1. Analyze the image
# 2. Combine with user text
# 3. Generate optimized search query
# 4. Return relevant products
```

## Performance Tips

1. **Use quick_mode** for faster responses:

   ```python
   result = await VisionService.analyze_image(image_bytes, quick_mode=True)
   ```

2. **Provide user context** for better results:

   ```python
   result = await VisionService.analyze_image(
       image_bytes,
       user_context="looking for wedding jewelry"
   )
   ```

3. **Cache results** (optional) to avoid redundant API calls for the same image

## What Changed

1. ✅ Fixed Groq model (90b instead of decommissioned 11b)
2. ✅ Gemini tried first (better free tier)
3. ✅ Enhanced error messages with details
4. ✅ Better fallback logic
5. ✅ Improved logging for debugging

## Support

If you encounter issues:

1. Check logs for detailed error messages
2. Run `python test_vision.py` to diagnose
3. Verify API keys are valid and active
4. Check rate limits haven't been exceeded
