# Crawl Scheduling Implementation Summary

## Completed ✅

### 1. Database Schema
- **Migration**: `apps/api/alembic/versions/012_add_crawl_scheduling.py`
  - Created `crawl_schedules` table with schedule types (manual, daily, weekly, monthly)
  - Created `crawl_history` table to track crawl statistics
  - Added `is_removed` and `updated_at` columns to `crawled_pages` for soft deletes

### 2. Backend Models
- **File**: `apps/api/app/models/knowledge.py`
  - Added `ScheduleType` enum (manual, daily, weekly, monthly)
  - Added `CrawlStatus` enum (success, partial, failed)
  - Added `CrawlSchedule` model with scheduling fields
  - Added `CrawlHistory` model to track crawl runs
  - Updated `CrawledPage` model with `is_removed` and `updated_at` fields

### 3. Backend Schemas
- **File**: `apps/api/app/schemas/knowledge.py`
  - `CrawlScheduleCreate` - for creating schedules
  - `CrawlScheduleUpdate` - for updating schedules
  - `CrawlScheduleResponse` - for returning schedule data
  - `CrawlHistoryResponse` - for returning crawl history
  - `TriggerCrawlResponse` - for manual crawl triggers

### 4. Crawler Service with Diff Detection
- **File**: `apps/api/app/services/crawler_service.py`
  - Enhanced `start_crawl` method with `is_recrawl` parameter
  - Implements diff detection:
    - Compares content hashes to detect changes
    - Adds new pages
    - Updates changed pages
    - Marks removed pages (soft delete)
  - Creates crawl history entries with statistics
  - Updates schedule's `last_crawl_at` timestamp

### 5. Scheduler Service
- **File**: `apps/api/app/services/scheduler_service.py`
  - Uses APScheduler for background job scheduling
  - Runs hourly to check for due schedules
  - `calculate_next_crawl()` - calculates next run time based on schedule type
  - `create_or_update_schedule()` - manages schedule CRUD
  - Integrated into FastAPI lifespan in `main.py`

### 6. API Endpoints
- **File**: `apps/api/app/api/v1/chatbots.py`
  - `GET /knowledge-sources/{id}/schedule` - get schedule
  - `POST /knowledge-sources/{id}/schedule` - create/update schedule
  - `PATCH /knowledge-sources/{id}/schedule` - update schedule
  - `POST /knowledge-sources/{id}/crawl-now` - trigger immediate crawl
  - `GET /knowledge-sources/{id}/crawl-history` - get crawl history

### 7. ChatbotService Methods
- **File**: `apps/api/app/services/chatbot_service.py`
  - `get_crawl_schedule()` - retrieve schedule with access control
  - `create_or_update_schedule()` - create/update with validation
  - `update_schedule()` - partial update
  - `trigger_crawl_now()` - manual crawl trigger
  - `get_crawl_history()` - retrieve history with pagination

### 8. Frontend Component
- **File**: `apps/web/components/dashboard/CrawlScheduleModal.tsx`
  - Modal component for managing crawl schedules
  - Schedule frequency options (manual, daily, weekly, monthly)
  - Day of week selector for weekly schedules
  - Hour selector (UTC timezone)
  - "Sync Now" button for manual triggers
  - Crawl history display with statistics
  - Shows next scheduled sync time

### 9. Dependencies
- Added `apscheduler==3.10.4` to `requirements.txt`

## Pending 🚧

### 1. Database Migration Execution
**Action Required**: Run the migration to create the new tables
```bash
cd apps/api
# Activate virtual environment if needed
alembic upgrade head
```

### 2. Frontend Integration
**File to Modify**: `apps/web/app/dashboard/chatbots/[chatbotId]/page.tsx`

The `CrawlScheduleModal` component has been created but needs to be integrated into the chatbot detail page. Here's what needs to be added:

#### A. Import the component (add to imports section):
```typescript
import { CrawlScheduleModal } from '@/components/dashboard/CrawlScheduleModal'
```

#### B. Add state for modal (add to state declarations):
```typescript
const [scheduleModalOpen, setScheduleModalOpen] = useState(false)
const [selectedKnowledgeSource, setSelectedKnowledgeSource] = useState<KnowledgeSource | null>(null)
```

#### C. Modify the crawl tab to show sources grouped by URL:

The current implementation shows individual pages. We need to add a section above the pages list that shows the crawl sources with a "Schedule" button:

```typescript
{/* Add this before the pages list in TabsContent value="crawl" */}
{crawlSources.length > 0 && (
  <div className="space-y-2 mb-4">
    <Label className="text-sm font-semibold">Crawled Websites</Label>
    {crawlSources.map((source) => (
      <div key={source.id} className="flex items-center justify-between p-3 border rounded-lg">
        <div>
          <div className="font-medium text-sm">{source.source_url}</div>
          <div className="text-xs text-muted-foreground">
            {source.pages_found} pages • Last synced: {new Date(source.updated_at).toLocaleString()}
          </div>
        </div>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => {
            setSelectedKnowledgeSource(source)
            setScheduleModalOpen(true)
          }}
        >
          <Clock className="h-4 w-4 mr-2" />
          Schedule
        </Button>
      </div>
    ))}
  </div>
)}
```

#### D. Add the modal at the end of the component (before the closing div):
```typescript
{scheduleModalOpen && selectedKnowledgeSource && (
  <CrawlScheduleModal
    knowledgeSourceId={selectedKnowledgeSource.id}
    sourceUrl={selectedKnowledgeSource.source_url || ''}
    pagesCount={selectedKnowledgeSource.pages_found}
    lastSynced={selectedKnowledgeSource.updated_at}
    onClose={() => {
      setScheduleModalOpen(false)
      setSelectedKnowledgeSource(null)
    }}
    onSync={() => {
      // Refresh knowledge sources
      fetchKnowledgeSources()
    }}
  />
)}
```

#### E. Add Clock icon to imports:
```typescript
import { ..., Clock } from 'lucide-react'
```

### 3. Testing Checklist

Once integrated, test the following:

- [ ] Create a new crawl schedule (daily/weekly/monthly)
- [ ] Verify next_crawl_at is calculated correctly
- [ ] Trigger manual "Sync Now" and verify it works
- [ ] Check crawl history shows statistics
- [ ] Verify diff detection works (pages added/updated/removed)
- [ ] Wait for scheduled crawl to run (or adjust time for testing)
- [ ] Verify scheduler runs hourly and picks up due schedules
- [ ] Test updating an existing schedule
- [ ] Test deactivating a schedule

## Architecture Notes

### Scheduler Flow
1. APScheduler runs every hour (on the hour)
2. Checks `crawl_schedules` table for `next_crawl_at <= now` and `is_active = true`
3. For each due schedule:
   - Triggers `CrawlerService.start_crawl()` with `is_recrawl=True`
   - Calculates and updates `next_crawl_at` based on schedule type
4. Crawler performs diff detection and updates `crawl_history`

### Diff Detection Logic
1. Fetch all existing non-removed pages
2. Crawl website and compute content hashes
3. For each crawled page:
   - If URL exists and hash matches → skip (no change)
   - If URL exists and hash differs → update content and re-embed
   - If URL is new → add page and embed
4. For existing pages not found in crawl → mark as removed
5. Record statistics in `crawl_history`

### Next Crawl Calculation
- **Daily**: Next day at preferred_hour
- **Weekly**: Next occurrence of day_of_week at preferred_hour
- **Monthly**: Same day next month at preferred_hour
- **Manual**: next_crawl_at = null

## API Usage Examples

### Get Schedule
```bash
GET /api/v1/chatbots/knowledge-sources/{id}/schedule
```

### Create/Update Schedule
```bash
POST /api/v1/chatbots/knowledge-sources/{id}/schedule
Content-Type: application/json

{
  "schedule_type": "weekly",
  "day_of_week": 0,  // Monday
  "preferred_hour": 2,  // 2 AM UTC
  "is_active": true
}
```

### Trigger Manual Crawl
```bash
POST /api/v1/chatbots/knowledge-sources/{id}/crawl-now
```

### Get Crawl History
```bash
GET /api/v1/chatbots/knowledge-sources/{id}/crawl-history?limit=20
```

## Files Modified/Created

### Backend
- ✅ `apps/api/alembic/versions/012_add_crawl_scheduling.py` (new)
- ✅ `apps/api/app/models/knowledge.py` (modified)
- ✅ `apps/api/app/schemas/knowledge.py` (modified)
- ✅ `apps/api/app/services/crawler_service.py` (modified)
- ✅ `apps/api/app/services/scheduler_service.py` (new)
- ✅ `apps/api/app/services/chatbot_service.py` (modified)
- ✅ `apps/api/app/api/v1/chatbots.py` (modified)
- ✅ `apps/api/main.py` (modified)
- ✅ `apps/api/requirements.txt` (modified)

### Frontend
- ✅ `apps/web/components/dashboard/CrawlScheduleModal.tsx` (new)
- 🚧 `apps/web/app/dashboard/chatbots/[chatbotId]/page.tsx` (needs integration)

## Environment Variables

No new environment variables required. Uses existing database configuration.

## Notes

- All times are stored and calculated in UTC
- Scheduler runs every hour on the hour
- Soft deletes are used for removed pages (is_removed flag)
- Crawl history is kept indefinitely (consider adding cleanup job later)
- Only crawled_url type knowledge sources can be scheduled
- Requires EDITOR or OWNER permission level to manage schedules

