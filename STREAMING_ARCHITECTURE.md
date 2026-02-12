# SSE Streaming - Implementation Diagram

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                                     │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Preact Widget (ChatbotWidget.tsx)                             │    │
│  │                                                                 │    │
│  │  1. User types message                                         │    │
│  │  2. Click send button                                          │    │
│  │  3. Create placeholder message with isTyping: true             │    │
│  │  4. Call: POST /api/v1/chat/{id}/message/stream                │    │
│  └────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ HTTP POST (multipart/form-data)
                                │ with ReadableStream processing
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                                     │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  chat.py: send_message_stream()                                │    │
│  │                                                                 │    │
│  │  1. Rate limit check                                           │    │
│  │  2. Validate image (if provided)                               │    │
│  │  3. Call ChatService.get_response_stream()                     │    │
│  │  4. Return StreamingResponse(event_generator())                │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                ▼                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  chat_service.py: get_response_stream()                        │    │
│  │                                                                 │    │
│  │  1. Get/Create session                                         │    │
│  │     → yield {"type": "session", "session_id": "..."}          │    │
│  │                                                                 │    │
│  │  2. Check if chatbot is paused                                 │    │
│  │                                                                 │    │
│  │  3. Process image (if provided)                                │    │
│  │     → Vision AI analysis                                       │    │
│  │                                                                 │    │
│  │  4. Get chat history & summary                                 │    │
│  │                                                                 │    │
│  │  5. RAG: Retrieve relevant context                             │    │
│  │     → Generate embeddings                                      │    │
│  │     → Vector similarity search (pgvector)                      │    │
│  │     → Extract price/color filters                             │    │
│  │     → Combine text + vision results                           │    │
│  │                                                                 │    │
│  │  6. Build system prompt with context                           │    │
│  │                                                                 │    │
│  │  7. Call Groq API with stream=True                             │    │
│  └────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                │ HTTPS POST with stream=True
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        GROQ API                                          │
│                                                                          │
│  Model: llama-3.3-70b-versatile                                         │
│  Stream: True                                                            │
│                                                                          │
│  Returns: SSE stream of tokens                                          │
│  Format: data: {"choices": [{"delta": {"content": "token"}}]}          │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                │ SSE chunks
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   BACKEND PROCESSING                                     │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  chat_service.py: Stream Processing                            │    │
│  │                                                                 │    │
│  │  For each chunk from Groq:                                     │    │
│  │    1. Parse SSE line                                           │    │
│  │    2. Extract content from delta                               │    │
│  │    3. Accumulate full_content                                  │    │
│  │    4. yield {"type": "content", "content": "chunk"}           │    │
│  │       ↓                                                         │    │
│  │       Sent to browser immediately                              │    │
│  │                                                                 │    │
│  │  After stream completes:                                       │    │
│  │    1. Clean content (remove tags)                              │    │
│  │    2. Extract suggestions                                      │    │
│  │    3. Extract products from context                            │    │
│  │    4. Save to database                                         │    │
│  │    5. yield {"type": "done", ...}                             │    │
│  └────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                │ SSE Events Stream
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      USER BROWSER                                        │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  Widget: ReadableStream Processing                             │    │
│  │                                                                 │    │
│  │  On "session" event:                                           │    │
│  │    → Update sessionId state                                    │    │
│  │                                                                 │    │
│  │  On "content" event:                                           │    │
│  │    → Append to streamedContent                                 │    │
│  │    → Update message in messages array                          │    │
│  │    → React re-renders with new content                         │    │
│  │    → User sees text appearing character by character           │    │
│  │                                                                 │    │
│  │  On "done" event:                                              │    │
│  │    → Set isTyping: false                                       │    │
│  │    → Add suggestions array                                     │    │
│  │    → Add products array                                        │    │
│  │    → Display suggestion buttons                                │    │
│  │    → Display product carousel (if products exist)              │    │
│  │                                                                 │    │
│  │  On "error" event:                                             │    │
│  │    → Display error message                                     │    │
│  │    → Set isTyping: false                                       │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Timeline

```
Time  │  Backend                          │  Frontend
──────┼───────────────────────────────────┼────────────────────────────────
0ms   │  Request received                 │  Placeholder message created
      │  Rate limit check                 │  isTyping: true
      │                                   │
50ms  │  Session created/retrieved        │
      │  → SSE: {"type": "session"}      │  → sessionId updated
      │                                   │
200ms │  Vision analysis (if image)       │
      │  RAG search starts                │
      │                                   │
500ms │  Context retrieved                │
      │  Groq streaming starts            │
      │                                   │
520ms │  First token received             │
      │  → SSE: {"type": "content"}      │  → "Hello" displayed ✨
      │                                   │
540ms │  Next token                       │
      │  → SSE: {"type": "content"}      │  → "Hello there" displayed
      │                                   │
...   │  ... streaming continues ...      │  ... text keeps appearing ...
      │                                   │
4.5s  │  Stream complete                  │
      │  Save to database                 │
      │  Extract metadata                 │
      │  → SSE: {"type": "done"}         │  → isTyping: false
      │                                   │  → Suggestions appear
      │                                   │  → Products appear
```

## SSE Event Types

### 1. Session Event

```json
{
  "type": "session",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Purpose**: Establish/update session identifier  
**Timing**: First event sent immediately

### 2. Content Event

```json
{
  "type": "content",
  "content": "Hello"
}
```

**Purpose**: Stream text chunks  
**Timing**: Multiple events as tokens arrive from Groq  
**Frequency**: 10-50 events per response

### 3. Done Event

```json
{
  "type": "done",
  "sources": [{ "title": "FAQ", "url": "https://..." }],
  "suggestions": [
    "How do I return a product?",
    "What are your shipping options?"
  ],
  "products": [
    {
      "name": "Gold Ring",
      "url": "https://...",
      "price": "5000",
      "currency": "₹",
      "image": "https://...",
      "rating": 4.5
    }
  ],
  "image_analysis": null
}
```

**Purpose**: Send final metadata  
**Timing**: After stream completes

### 4. Error Event

```json
{
  "type": "error",
  "error": "Service temporarily unavailable"
}
```

**Purpose**: Handle errors gracefully  
**Timing**: On exception

## Performance Comparison

### Non-Streaming Flow

```
User clicks send
      ↓
[====== 3-5 second wait ======]
      ↓
Full response appears
```

### Streaming Flow

```
User clicks send
      ↓
[0.2s] First word appears
      ↓
[0.5s] More text...
      ↓
[1.0s] Even more...
      ↓
[3.0s] Complete
```

## Error Handling

```
┌─────────────────────┐
│  Groq API Error     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Backend catches    │
│  Exception          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  yield error event  │
│  {"type": "error"}  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Widget displays    │
│  error message      │
│  to user            │
└─────────────────────┘
```

## Key Benefits

### Technical

- ✅ Memory efficient (streams, not buffers)
- ✅ Lower server load (progressive response)
- ✅ Better error recovery
- ✅ Maintains RAG quality

### User Experience

- ✅ 90% faster perceived response time
- ✅ No "frozen" UI during generation
- ✅ Modern, engaging interaction
- ✅ Clear progress indication

### Business

- ✅ Competitive with ChatGPT/Claude
- ✅ Improved user engagement
- ✅ Lower bounce rate on slow responses
- ✅ Professional appearance
