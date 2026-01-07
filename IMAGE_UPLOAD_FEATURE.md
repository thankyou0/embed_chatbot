# Image Upload & Visual Search Feature

## Overview
Implemented complete image upload functionality with vision AI analysis for product search in the e-commerce chatbot.

## Features Implemented

### 1. Vision Service (Backend)
**File:** `apps/api/app/services/vision_service.py`

- Uses **Groq's free `llama-3.2-11b-vision-preview`** model for image analysis
- Extracts product attributes:
  - Product type (shoes, shirt, bag, etc.)
  - Category (footwear, clothing, accessories)
  - Color
  - Style (casual, formal, sporty)
  - Other attributes (material, pattern)
- Returns confidence score (0.0 to 1.0)
- Handles image encoding and MIME type detection

### 2. Query Building Logic
**File:** `apps/api/app/services/vision_service.py` - `build_combined_query()`

- Combines user text with image attributes
- **User text overrides image attributes**
  - Example: "show me red ones" + blue shoes image → searches for "red shoes"
- Confidence threshold: 0.4 (asks for clarification if below)

### 3. API Endpoint Updates
**File:** `apps/api/app/api/v1/chat.py`

**Endpoint:** `POST /api/v1/chat/{chatbot_id}/message`

Now accepts **multipart/form-data**:
- `message` (optional): Text message
- `session_id` (optional): Session ID for conversation continuity
- `image` (optional): Image file (max 10MB, supports JPEG, PNG, GIF, WebP)

**Response includes:**
```json
{
  "session_id": "uuid",
  "message": "Bot response",
  "sources": [...],
  "suggestions": ["Follow-up 1?", "Follow-up 2?"],
  "image_analysis": {
    "product_type": "shoes",
    "category": "footwear",
    "color": "blue",
    "style": "casual",
    "other_attributes": "leather, lace-up",
    "confidence": 0.85,
    "needs_clarification": false
  }
}
```

### 4. Chat Service Updates
**File:** `apps/api/app/services/chat_service.py`

- Processes uploaded images via `VisionService`
- Builds effective search query combining text + image
- Stores image analysis in message metadata
- **Handles empty knowledge base** - provides helpful response instead of "no answer available"

### 5. Widget Preview (Dashboard)
**File:** `apps/web/components/chatbot/WidgetPreview.tsx`

**New Features:**
- ✅ Image upload button (camera icon)
- ✅ Image preview with remove button
- ✅ Displays uploaded images in chat
- ✅ Sends FormData instead of JSON
- ✅ Clickable suggestions after bot responses
- ✅ Welcome message with initial suggestions
- ✅ Proper error handling

### 6. Standalone Widget
**File:** `apps/widget/src/components/ChatbotWidget.tsx`

**Complete rewrite with:**
- Full chat functionality with API integration
- Image upload with compression (max 1MB)
- Image preview (60x60 thumbnail)
- Clickable suggestion pills
- Welcome message from config
- Session persistence
- Loading states
- Error handling

**File:** `apps/widget/src/styles.css`
- Modern, polished UI
- Smooth animations
- Responsive design
- Mobile-friendly

## Usage Examples

### API Usage (cURL)
```bash
# With image
curl -X POST "http://localhost:8000/api/v1/chat/{chatbot_id}/message" \
  -F "message=Show me similar products in red" \
  -F "session_id=optional-session-id" \
  -F "image=@product.jpg"

# Text only
curl -X POST "http://localhost:8000/api/v1/chat/{chatbot_id}/message" \
  -F "message=What products do you have?"
```

### Widget Integration
```html
<script 
  src="widget.js" 
  data-auto-init="true"
  data-api-url="http://localhost:8000"
  data-chatbot-id="your-chatbot-uuid">
</script>
```

Or programmatically:
```javascript
ChatbotWidget.init({
  apiUrl: 'http://localhost:8000',
  chatbotId: 'your-chatbot-uuid',
  theme: {
    primaryColor: '#6366f1',
    position: 'bottom-right'
  }
})
```

## Technical Details

### Image Processing Flow
1. User uploads image (frontend validates type/size)
2. Image compressed to max 1MB (frontend)
3. Sent as multipart/form-data to API
4. Backend encodes to base64
5. Sent to Groq Vision API
6. Attributes extracted and parsed
7. Combined with user text for search query
8. Hybrid search (vector + keyword) on embeddings
9. LLM generates response with context
10. Response includes image analysis metadata

### Confidence Handling
- **≥ 0.4**: Use image attributes confidently
- **< 0.4**: Mark as `needs_clarification`, inform user

### Empty Knowledge Base Handling
- Previously: "No answer available"
- Now: Friendly message explaining knowledge base is empty
- Suggests adding knowledge sources

## Files Modified

### Backend
- `apps/api/app/services/vision_service.py` (NEW)
- `apps/api/app/services/chat_service.py`
- `apps/api/app/api/v1/chat.py`
- `apps/api/app/schemas/chat.py`
- `apps/api/app/schemas/appearance.py`
- `apps/api/app/services/chatbot_service.py`

### Frontend (Dashboard)
- `apps/web/components/chatbot/WidgetPreview.tsx`

### Widget
- `apps/widget/src/components/ChatbotWidget.tsx`
- `apps/widget/src/styles.css`
- `apps/widget/src/index.tsx`

## Testing Checklist

- [x] Image upload works in dashboard preview
- [x] Image upload works in standalone widget
- [x] FormData sent correctly to API
- [x] Vision API analyzes images
- [x] Attributes extracted correctly
- [x] User text overrides image attributes
- [x] Suggestions are clickable
- [x] Welcome message displays
- [x] Empty knowledge base handled gracefully
- [x] Session persistence works
- [x] Error states display properly

## Known Limitations

1. **Image size**: Max 10MB (compressed to 1MB on frontend)
2. **Supported formats**: JPEG, PNG, GIF, WebP
3. **Vision model**: Free tier has rate limits
4. **No brand/SKU detection**: Intentionally excluded for privacy
5. **No face detection**: Privacy-focused

## Future Enhancements

- [ ] Support multiple images per message
- [ ] Image history in chat
- [ ] Advanced image filters (crop, rotate)
- [ ] OCR for text in images
- [ ] Product matching from image embeddings
- [ ] Image-to-image similarity search

