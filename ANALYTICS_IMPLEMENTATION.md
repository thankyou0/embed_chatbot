# Analytics Implementation Summary

## Overview
Implemented essential, client-focused analytics features for the e-commerce chatbot platform.

## Features Implemented

### 1. Backend Changes

#### Database Migration
- **File**: `apps/api/alembic/versions/011_add_analytics_fields.py`
- Added `confidence_threshold` field to `chatbots` table (default: 0.7)
- Note: `metadata_json` already existed in `chat_messages` table

#### Models Updated
- **File**: `apps/api/app/models/chatbot.py`
- Added `confidence_threshold: Float` field to Chatbot model

#### Chat Service Enhancements
- **File**: `apps/api/app/services/chat_service.py`
- Added response time tracking
- Track retrieval confidence scores
- Store analytics metadata in assistant messages:
  ```json
  {
    "retrieval_confidence": 0.75,
    "sources_count": 3,
    "response_time_ms": 450,
    "was_answered": true
  }
  ```
- `was_answered` determined by comparing confidence to chatbot's threshold

#### New Analytics Service
- **File**: `apps/api/app/services/analytics_service.py`
- `get_analytics_overview()`: Calculate deflection rate, unanswered rate, and basic metrics
- `get_unanswered_queries()`: Group and analyze queries that weren't answered confidently
- Support for period filtering: 7d, 30d, 90d

#### New Schemas
- **File**: `apps/api/app/schemas/analytics.py`
- `AnalyticsOverviewResponse`: Includes deflection_rate, unanswered_rate, period
- `UnansweredQuery`: Query details with count, confidence, samples
- `UnansweredQueriesResponse`: List of unanswered queries

#### API Endpoints
- **File**: `apps/api/app/api/v1/chatbots.py`
- Updated: `GET /api/v1/chatbots/analytics/overview?period={7d|30d|90d}&chatbot_id={id}`
- New: `GET /api/v1/chatbots/{id}/analytics/unanswered?period={7d|30d|90d}&limit={20}`

### 2. Frontend Changes

#### Enhanced Analytics Dashboard
- **File**: `apps/web/app/dashboard/analytics/page.tsx`
- **5 Metric Cards**:
  1. Total Sessions
  2. Total Messages
  3. Average Depth (messages per session)
  4. **Deflection Rate** (green badge) - % resolved without escalation
  5. **Unanswered Rate** (orange badge) - % low confidence responses

- **Date Range Picker**: Tabs for 7d, 30d, 90d
- **Deflection Rate Visualization**: Progress bar with success rate
- **Unanswered Queries Section**:
  - Shows queries grouped by exact text match
  - Displays count, last asked date, confidence score
  - Color-coded progress bars (red < 50%, yellow 50-70%)
  - Export to CSV functionality
  - Only visible when specific chatbot selected

#### New UI Components
- **File**: `apps/web/components/ui/progress.tsx`
- Progress bar component using Radix UI

## Key Metrics Explained

### Deflection Rate
- **Definition**: Percentage of sessions where ALL bot responses had high confidence (was_answered=true)
- **Calculation**: (Sessions with all queries answered / Total sessions) × 100
- **Good Target**: > 70%
- **Client Value**: Shows how well the bot handles queries without human intervention

### Unanswered Rate
- **Definition**: Percentage of user queries that received low-confidence responses
- **Calculation**: (User messages with was_answered=false / Total user messages) × 100
- **Good Target**: < 20%
- **Client Value**: Identifies knowledge gaps to improve the bot

### Confidence Threshold
- **Default**: 0.7 (70%)
- **Configurable**: Per chatbot in database
- **Usage**: Determines if a query was "answered" based on retrieval confidence

## How It Works

1. **During Chat**:
   - Chat service tracks retrieval confidence from vector search
   - Compares confidence to chatbot's threshold
   - Stores metadata in assistant message

2. **Analytics Calculation**:
   - Filters sessions by date range (period)
   - Analyzes message metadata to calculate metrics
   - Groups unanswered queries by exact text match

3. **Dashboard Display**:
   - Fetches overview metrics with period filter
   - Shows unanswered queries for selected chatbot
   - Provides export functionality

## Usage Instructions

### For Developers
1. Run migration: `alembic upgrade head` (in apps/api directory)
2. Restart API server
3. Restart web app
4. Navigate to `/dashboard/analytics`

### For Clients
1. Select a chatbot from dropdown (or "All Chatbots")
2. Choose date range: Last 7, 30, or 90 days
3. View deflection rate and unanswered rate
4. For specific chatbot: scroll to see unanswered queries
5. Export queries to CSV for knowledge base improvements

## Future Enhancements (Not Implemented)

These were intentionally left out to keep it simple:

- ❌ Query clustering with embeddings (groups similar queries)
- ❌ "Add to FAQ" button (direct integration)
- ❌ Trend charts over time
- ❌ Session-level analytics
- ❌ Analytics events table (using existing chat_messages instead)

## Technical Notes

- **No Breaking Changes**: Built on existing schema (metadata_json already existed)
- **Efficient Queries**: Uses SQLAlchemy to minimize database calls
- **Scalable**: Can handle thousands of messages efficiently
- **Type-Safe**: Full TypeScript and Python type hints
- **Responsive**: Mobile-friendly UI

## Files Changed

### Backend (7 files)
1. `apps/api/alembic/versions/011_add_analytics_fields.py` (new)
2. `apps/api/app/models/chatbot.py` (modified)
3. `apps/api/app/services/chat_service.py` (modified)
4. `apps/api/app/services/analytics_service.py` (new)
5. `apps/api/app/schemas/analytics.py` (new)
6. `apps/api/app/schemas/chatbot.py` (modified)
7. `apps/api/app/api/v1/chatbots.py` (modified)

### Frontend (2 files)
1. `apps/web/app/dashboard/analytics/page.tsx` (rewritten)
2. `apps/web/components/ui/progress.tsx` (new)

## Testing Checklist

- [ ] Run database migration
- [ ] Test chat endpoint (verify metadata is stored)
- [ ] Test analytics overview endpoint with different periods
- [ ] Test unanswered queries endpoint
- [ ] Test UI with multiple chatbots
- [ ] Test date range switching
- [ ] Test CSV export
- [ ] Verify deflection rate calculation
- [ ] Verify unanswered rate calculation

## Migration Command

```bash
cd apps/api
alembic upgrade head
```

## API Examples

### Get Analytics Overview
```bash
GET /api/v1/chatbots/analytics/overview?period=30d&chatbot_id={uuid}
```

Response:
```json
{
  "total_sessions": 150,
  "total_messages": 890,
  "avg_messages_per_session": 5.9,
  "deflection_rate": 78.5,
  "unanswered_rate": 12.3,
  "period": "30d"
}
```

### Get Unanswered Queries
```bash
GET /api/v1/chatbots/{uuid}/analytics/unanswered?period=30d&limit=20
```

Response:
```json
{
  "queries": [
    {
      "query": "Do you offer EMI?",
      "count": 23,
      "avg_confidence": 0.45,
      "first_asked": "2024-01-01T10:00:00Z",
      "last_asked": "2024-01-15T14:30:00Z",
      "sample_messages": [...]
    }
  ],
  "total_unanswered": 156
}
```

