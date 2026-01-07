
# 🚀 Sprint Structure: E-Commerce Embeddable AI Chatbot SaaS

Here's your complete sprint roadmap with prompts for each step. Each sprint delivers a **working, testable feature**.

---

## 📊 Overview

| Sprint | Duration | Focus | Deliverable |
|--------|----------|-------|-------------|
| 0 | 1 day | Project Setup | Monorepo, DB, basic config |
| 1 | 3-4 days | Auth + Tenant Foundation | Login, signup, tenant isolation |
| 2 | 4-5 days | Knowledge Base - Core | URL crawling + embedding pipeline |
| 3 | 2-3 days | Knowledge Base - Extended | File upload + QA pairs |
| 4 | 3-4 days | Chatbot Widget - Basic | Embeddable chat UI + basic responses |
| 5 | 3-4 days | Chatbot Widget - Advanced | Image input, suggestions, conversation memory |
| 6 | 2-3 days | Bot Customization | Appearance editor, embed code generator |
| 7 | 2-3 days | Human Fallback | Fallback config + contact form |
| 8 | 3-4 days | Analytics | Deflection rate, unanswered queries |
| 9 | 2-3 days | Auto-Recrawl | Scheduling + diff detection |
| 10 | 2-3 days | Polish & Deploy | Testing, optimization, deployment |

**Total: ~30-35 days**

---

## 🏃 Sprint 0: Project Foundation

### Goal
Set up monorepo structure, database, and development environment.

### Prompt to Use

```
Create a monorepo project structure for an embeddable AI chatbot SaaS with:

STRUCTURE:
/apps
  /web - Next.js 14 (App Router) tenant dashboard
  /widget - Preact/vanilla JS embeddable chat widget (tiny bundle)
  /api - FastAPI backend

/packages
  /shared - Shared types/utilities
  /ui - Shared UI components (for dashboard)

TECH STACK:
- Frontend: Next.js 14, Tailwind CSS, shadcn/ui
- Widget: Preact or vanilla JS (must be <50KB gzipped)
- Backend: FastAPI (Python 3.11+)
- Database: PostgreSQL with pgvector extension
- ORM: SQLAlchemy 2.0 with async support

SETUP:
1. Create docker-compose.yml with PostgreSQL + pgvector
2. Create .env.example with required variables
3. Set up basic FastAPI app with health check endpoint
4. Set up basic Next.js app with Tailwind configured
5. Create initial database migration with these tables:
   - tenants (id, name, email, created_at)
   - users (id, tenant_id, email, password_hash, role, created_at)

Use pnpm for JS packages. Include proper .gitignore.
Do NOT implement authentication yet - just the structure.
```

### Deliverable Checklist
- [ ] Monorepo running locally
- [ ] PostgreSQL + pgvector in Docker
- [ ] FastAPI `/health` endpoint working
- [ ] Next.js homepage rendering
- [ ] Database tables created

---

## 🏃 Sprint 1: Authentication + Tenant Foundation

### Goal
Multi-tenant authentication system with proper isolation.

### Prompt 1.1 - Backend Auth

```
Add authentication to the FastAPI backend:

REQUIREMENTS:
1. JWT-based authentication with access + refresh tokens
2. Password hashing with bcrypt
3. Multi-tenant user model (users belong to tenants)

ENDPOINTS:
POST /api/auth/signup
  - Creates new tenant + admin user
  - Input: { tenant_name, email, password }
  - Returns: { access_token, refresh_token, user, tenant }

POST /api/auth/login
  - Input: { email, password }
  - Returns: { access_token, refresh_token, user, tenant }

POST /api/auth/refresh
  - Input: { refresh_token }
  - Returns: { access_token }

GET /api/auth/me
  - Protected route
  - Returns current user + tenant info

SECURITY:
- Access token: 15 min expiry
- Refresh token: 7 days expiry
- All routes except auth should require valid JWT
- Add tenant_id to JWT payload for isolation

Create proper Pydantic schemas for request/response validation.
Add dependency injection for getting current user/tenant.
```

### Prompt 1.2 - Frontend Auth Pages

```
Create authentication pages in the Next.js dashboard:

PAGES:
1. /login - Login form
2. /signup - Signup form (creates tenant + user)
3. /dashboard - Protected page (redirect if not logged in)

REQUIREMENTS:
- Use React Hook Form + Zod for validation
- Store tokens in httpOnly cookies (not localStorage)
- Create auth context/provider for global auth state
- Add middleware to protect /dashboard/* routes
- Show loading states during auth operations
- Display error messages from API

UI STYLE:
- Clean, modern SaaS aesthetic
- Use shadcn/ui components
- Mobile responsive
- Dark mode support

After login, redirect to /dashboard.
After logout, redirect to /login.
```

### Prompt 1.3 - Dashboard Layout

```
Create the main dashboard layout with navigation:

LAYOUT:
- Sidebar navigation (collapsible on mobile)
- Top header with user menu
- Main content area

NAVIGATION ITEMS:
1. Chatbots (list of tenant's chatbots)
2. Analytics (placeholder for now)
3. Usage & Billing (placeholder)
4. Settings

USER MENU (top right):
- User name + avatar
- Tenant name
- Logout button

Create a basic /dashboard/chatbots page that shows:
- "No chatbots yet" empty state
- "Create Chatbot" button

Do NOT implement chatbot creation yet - just the UI structure.
```

### Deliverable Checklist
- [ ] Can signup and create tenant
- [ ] Can login and receive tokens
- [ ] Protected routes working
- [ ] Dashboard layout with navigation
- [ ] Logout functionality

---

## 🏃 Sprint 2: Knowledge Base - URL Crawling

### Goal
Tenants can create chatbots and add knowledge via URL crawling.

### Prompt 2.1 - Chatbot CRUD Backend

```
Add chatbot management to FastAPI:

DATABASE:
Table: chatbots
- id (UUID)
- tenant_id (FK)
- name (string)
- welcome_message (text)
- status (enum: draft, active, paused)
- created_at, updated_at

ENDPOINTS:
GET /api/chatbots
  - List all chatbots for current tenant
  
POST /api/chatbots
  - Create new chatbot
  - Input: { name, welcome_message? }
  
GET /api/chatbots/{id}
  - Get chatbot details (verify tenant ownership)
  
PATCH /api/chatbots/{id}
  - Update chatbot
  
DELETE /api/chatbots/{id}
  - Soft delete chatbot

All endpoints must filter by tenant_id from JWT.
Return 404 if chatbot doesn't belong to current tenant.
```

### Prompt 2.2 - Crawling Service

```
Create URL crawling service in FastAPI:

DATABASE:
Table: knowledge_sources
- id (UUID)
- chatbot_id (FK)
- source_type (enum: crawled_url, uploaded_file, qa_pair)
- source_url (nullable)
- status (enum: pending, crawling, completed, failed)
- pages_found (int)
- created_at, updated_at

Table: crawled_pages
- id (UUID)
- knowledge_source_id (FK)
- url (string)
- title (string)
- content (text) - cleaned by trafilatura
- content_hash (string) - for diff detection
- created_at

CRAWLING LOGIC:
1. Use httpx + asyncio for async crawling
2. Use urllib.robotparser to respect robots.txt
3. Use trafilatura with favor_precision=True for content extraction
4. Crawl same domain only, max 500 pages
5. Follow links within same path prefix

ENDPOINTS:
POST /api/chatbots/{id}/crawl
  - Input: { base_url, max_pages? }
  - Starts background crawl job
  - Returns: { knowledge_source_id, status: "pending" }

GET /api/chatbots/{id}/knowledge-sources
  - List all knowledge sources for chatbot

GET /api/knowledge-sources/{id}/status
  - Get crawl progress (pages found, status)

Use BackgroundTasks or create a simple task queue for crawling.
Log progress so frontend can poll for updates.
```

### Prompt 2.3 - Embedding Pipeline

```
Create embedding pipeline that processes crawled content:

DATABASE:
Enable pgvector extension.

Table: embeddings
- id (UUID)
- chatbot_id (FK)
- knowledge_source_id (FK)
- source_type (enum: crawled, uploaded, qa_pair)
- content (text) - the chunk
- embedding (vector(384)) - for MiniLM or vector(768) for BGE
- metadata (JSONB) - source_url, title, etc.
- priority_weight (float) - for reranking
- created_at

CHUNKING STRATEGY:
1. Split by structure (headings, paragraphs)
2. Token-aware chunking (max 512 tokens per chunk)
3. Keep minimum 100 tokens per chunk
4. Add overlap of 50 tokens between chunks

EMBEDDING:
Use sentence-transformers with 'all-MiniLM-L6-v2' (free, fast)
- pip install sentence-transformers

PIPELINE:
After crawl completes:
1. Get all crawled_pages for knowledge_source
2. Chunk each page's content
3. Generate embeddings for each chunk
4. Store in embeddings table with metadata

Create async function: process_knowledge_source(knowledge_source_id)
Call this after crawl completes.
```

### Prompt 2.4 - Frontend Crawling UI

```
Create chatbot creation wizard in Next.js:

FLOW:
/dashboard/chatbots/new - Multi-step wizard

Step 1: Basic Info
- Chatbot name (required)
- Welcome message (optional, with default)
- [Next]

Step 2: Add Knowledge - URL Crawling
- URL input field
- "Start Crawling" button
- Progress indicator showing:
  - Status (pending → crawling → completed)
  - Pages found count (updates via polling)
- After complete: Show list of crawled pages
- [Skip] [Next]

Step 3: Review
- Summary of chatbot config
- Knowledge sources added
- [Create Chatbot]

After creation, redirect to /dashboard/chatbots/{id}

CHATBOT DETAIL PAGE:
/dashboard/chatbots/{id}
- Show chatbot info
- List knowledge sources with status
- "Add More Knowledge" button
- "Crawl New URL" action

Poll /api/knowledge-sources/{id}/status every 2 seconds during crawling.
Show toast notifications for success/error.
```

### Deliverable Checklist
- [ ] Can create chatbot with name
- [ ] Can submit URL for crawling
- [ ] Crawling respects robots.txt
- [ ] Content extracted with Trafilatura
- [ ] Content chunked and embedded
- [ ] Progress shown in UI

---

## 🏃 Sprint 3: Knowledge Base - Files & QA

### Goal
Support file uploads and QA pair management.

### Prompt 3.1 - File Upload Backend

```
Add file upload support to knowledge base:

SUPPORTED FILES:
- PDF (.pdf)
- Text (.txt)
- Word (.docx)
- Markdown (.md)

EXTRACTION:
- PDF: Use pypdf or pdfplumber
- DOCX: Use python-docx
- TXT/MD: Direct read

STORAGE:
- Store files in /uploads/{tenant_id}/{chatbot_id}/
- Or use S3-compatible storage (make configurable)

DATABASE:
Table: uploaded_files
- id (UUID)
- knowledge_source_id (FK)
- filename (string)
- file_path (string)
- file_size (int)
- mime_type (string)
- created_at

ENDPOINTS:
POST /api/chatbots/{id}/upload
  - Multipart file upload
  - Extract text content
  - Create knowledge_source with source_type='uploaded_file'
  - Chunk and embed content
  - Returns: { knowledge_source_id, filename, status }

GET /api/chatbots/{id}/files
  - List uploaded files

DELETE /api/knowledge-sources/{id}
  - Delete knowledge source + associated embeddings

Max file size: 10MB
Validate file types on backend.
```

### Prompt 3.2 - QA Pairs Backend

```
Add QA pair management:

DATABASE:
Table: qa_pairs
- id (UUID)
- knowledge_source_id (FK)
- question (text)
- answer (text)
- created_at, updated_at

EMBEDDING STRATEGY:
- Combine Q+A as single text: "Q: {question}\nA: {answer}"
- Do NOT chunk QA pairs - keep them whole
- Set priority_weight = 1.0 (highest priority)

ENDPOINTS:
POST /api/chatbots/{id}/qa
  - Single QA: { question, answer }
  - Creates knowledge_source with source_type='qa_pair'
  
POST /api/chatbots/{id}/qa/bulk
  - Bulk upload: { qa_pairs: [{ question, answer }, ...] }
  - Or accept .xlsx file upload
  
GET /api/chatbots/{id}/qa
  - List all QA pairs for chatbot
  
PATCH /api/qa/{id}
  - Update QA pair (re-embed after update)
  
DELETE /api/qa/{id}
  - Delete QA pair + embedding

For XLSX upload:
- Expect columns: question, answer
- Use openpyxl to parse
- Validate all rows have both fields
```

### Prompt 3.3 - Frontend Knowledge Management

```
Create knowledge management UI for chatbot detail page:

/dashboard/chatbots/{id}/knowledge

TAB LAYOUT:
1. URL Sources
2. Uploaded Files  
3. QA Pairs

TAB 1 - URL SOURCES:
- List of crawled URLs with status
- "Crawl New URL" button → modal with URL input
- Each source shows: URL, pages count, status, date
- Delete button for each source

TAB 2 - UPLOADED FILES:
- Drag-and-drop upload zone
- List of uploaded files
- Each shows: filename, size, date
- Delete button

TAB 3 - QA PAIRS:
- "Add QA Pair" button → modal form
- "Bulk Upload" button → accepts .xlsx
- Table view of all QA pairs
- Inline edit capability
- Delete button
- Show count: "23 QA pairs"

DOWNLOAD TEMPLATE:
- "Download Template" button for QA xlsx
- Template has headers: question, answer
- Include 2 example rows

Add success/error toasts for all operations.
Confirm dialog before delete.
```

### Deliverable Checklist
- [ ] Can upload PDF, TXT, DOCX files
- [ ] Files extracted and embedded
- [ ] Can add individual QA pairs
- [ ] Can bulk upload QA via XLSX
- [ ] Can edit/delete QA pairs
- [ ] All knowledge sources visible in UI

---

## 🏃 Sprint 4: Chatbot Widget - Basic

### Goal
Create embeddable chat widget with basic RAG responses.

### Prompt 4.1 - Chat API Backend

```
Create chat API with hybrid search:

ENDPOINT:
POST /api/chat/{chatbot_id}/message
- Input: { message, session_id? }
- NO authentication (public endpoint for embedded widget)
- Rate limit by IP: 30 requests/minute

HYBRID SEARCH:
1. Keyword search (exact matches)
   - Search embeddings.content for exact phrases
   - Use PostgreSQL full-text search

2. Vector similarity search
   - Embed the user message
   - Search pgvector with cosine similarity
   - Get top 10 results

3. Combine and rerank
   - Merge results, deduplicate
   - Apply priority_weight boost
   - QA pairs get +0.15 to similarity score
   - Take top 5 chunks

LLM RESPONSE:
Use groq api:

System prompt:
"You are a helpful assistant for {chatbot.name}. 
Answer questions based ONLY on the provided context.
If the context doesn't contain the answer, say you don't have that information.
Be concise and helpful."

User prompt:
"Context:
{retrieved_chunks}

User question: {message}

Answer:"

RESPONSE:
{
  session_id: "...",
  message: "Bot response here",
  sources: [{ title, url }],  // Optional: cite sources
  suggestions: ["Related question 1", "Related question 2"]
}

Generate 2 follow-up suggestions based on the context.
```

### Prompt 4.2 - Widget Core

```
Create embeddable chat widget (separate /apps/widget):

REQUIREMENTS:
- Vanilla JS or Preact (tiny bundle, <50KB gzipped)
- Single script tag embed
- Works on any website
- No external CSS dependencies (styles bundled)

EMBED CODE:
<script 
  src="https://yourapp.com/widget.js"
  data-chatbot-id="xxx"
  data-position="bottom-right"
></script>

WIDGET UI:
1. Floating button (chat bubble icon)
   - Position: bottom-right (configurable)
   - Click to open chat

2. Chat window (modal/popup)
   - Header: Chatbot name + minimize button
   - Messages area (scrollable)
   - Input field + send button
   - "Powered by YourBrand" footer

3. Message types:
   - User message (right aligned)
   - Bot message (left aligned, with avatar)
   - Loading indicator (typing dots)

FUNCTIONALITY:
- Generate session_id on first open (store in sessionStorage)
- Send message to POST /api/chat/{chatbot_id}/message
- Display response
- Auto-scroll to new messages
- Show welcome message on first open

BUILD:
- Bundle with Vite or esbuild
- Output single widget.js file
- Minimize bundle size

Make CORS work for widget API calls.
```

### Prompt 4.3 - Widget Styling

```
Style the chat widget with modern, professional design:

DESIGN REQUIREMENTS:
- Clean, minimal aesthetic
- Smooth animations (open/close, messages appearing)
- Mobile responsive (full screen on mobile)
- Accessible (keyboard navigation, ARIA labels)

COLOR SCHEME (default, will be customizable later):
- Primary: #2563eb (blue)
- Background: #ffffff
- Text: #1f2937
- User bubble: #2563eb
- Bot bubble: #f3f4f6
- Border: #e5e7eb

ANIMATIONS:
- Widget open: slide up + fade in (200ms)
- Widget close: slide down + fade out (150ms)
- New message: fade in + slight slide up (150ms)
- Typing indicator: pulsing dots

RESPONSIVE:
- Desktop: 380px wide, 500px tall, bottom-right corner
- Mobile (<768px): Full screen overlay

CSS ISOLATION:
- Use CSS-in-JS or scoped styles
- Prefix all classes to avoid conflicts
- Don't inherit styles from host page

Include subtle shadow on widget for depth.
```

### Deliverable Checklist
- [ ] Chat API returns RAG-powered responses
- [ ] Hybrid search working (keyword + vector)
- [ ] Widget embeds with single script tag
- [ ] Messages send and receive
- [ ] Typing indicator during loading
- [ ] Mobile responsive

---

## 🏃 Sprint 5: Chatbot Widget - Advanced

### Goal  ---
Add image input, conversation memory, and clickable suggestions.

### Prompt 5.1 - Conversation Memory Backend

```
Add conversation memory to chat API:

DATABASE:
Table: chat_sessions
- id (UUID)
- chatbot_id (FK)
- started_at, last_message_at
- conversation_summary (text) - compressed memory

Table: chat_messages
- id (UUID)
- session_id (FK)
- role (enum: user, assistant)
- content (text)
- metadata (JSONB) - sources, suggestions, etc.
- created_at

MEMORY STRATEGY:
1. Sliding Window: Keep last 6 messages in context
2. Conversation Summary: Update every 4 turns

Summary generation prompt:
"Summarize this conversation in 1-2 sentences, focusing on what the user is looking for:
{last_messages}

Previous summary: {existing_summary}

Updated summary:"

ENHANCED CHAT FLOW:
1. Get/create session
2. Get last 6 messages from DB
3. Get conversation_summary
4. Hybrid search with query: "{message} | Context: {summary}"
5. Build LLM prompt with:
   - Retrieved chunks
   - Last 3-4 messages for immediate context
   - Summary for background context
6. Generate response
7. Save message to DB
8. Update summary if needed (every 4 turns)

Return session_id in response for session continuity.
```

### Prompt 5.2 - Image Input Backend

```
Add image processing to chat API:

ENDPOINT MODIFICATION:
POST /api/chat/{chatbot_id}/message
- Accept multipart form data
- Fields: message (text), image (file, optional), session_id

IMAGE PROCESSING:
Use OpenAI Vision API (gpt-4o-mini with vision) or Claude:

Prompt for image analysis:
"Extract product attributes from this image. Return JSON:
{
  \"product_type\": \"...\",
  \"category\": \"...\",
  \"color\": \"...\",
  \"style\": \"...\",
  \"other_attributes\": \"...\"
}

Only extract what you can clearly see. Leave fields empty if uncertain.
Do NOT identify specific brands or SKUs.
Do NOT identify people or faces."

QUERY BUILDING:
1. Get image attributes from vision model
2. Parse user text for overrides (text > image)
3. Build effective query:
   - User: "show me red ones" + image of blue shoes
   - Image attrs: { product_type: "shoes", color: "blue" }
   - Override: color → "red"
   - Final query: "red shoes similar to casual shoes"

4. Use this query for hybrid search

Add image to chat_messages as base64 or store and reference URL.
Set confidence threshold - if vision confidence < 0.4, ask for clarification.
```

### Prompt 5.3 - Suggestions & Widget Updates

```
Enhance widget with suggestions and image upload:

NEW FEATURES:

1. CLICKABLE SUGGESTIONS:
- Show 2 suggestions after each bot response
- Show 2 initial suggestions based on welcome context
- Clicking suggestion sends it as user message
- Style as pill buttons below bot message

2. IMAGE UPLOAD:
- Add image icon button next to text input
- Click to open file picker (accept: image/*)
- Show image preview before sending
- "X" button to remove selected image
- Send image + text together

3. WELCOME MESSAGE:
- On first open, show welcome message from chatbot config
- Show 2 initial suggestions (generic or from config):
  - "What products do you have?"
  - "Tell me about your return policy"

UI UPDATES:
- Suggestions container below bot messages
- Image preview thumbnail (60x60) with remove button
- Image icon in input area
- Loading state for image processing (may take longer)

Widget should handle:
- Image compression before upload (max 1MB)
- Error state if image upload fails
- Fallback if image processing fails
```

### Deliverable Checklist
- [ ] Conversation persists across messages
- [ ] Summary generated and used for context
- [ ] Can upload image with message
- [ ] Image attributes extracted
- [ ] Text overrides image attributes
- [ ] Clickable suggestions working
- [ ] Welcome message with initial suggestions

---

## 🏃 Sprint 6: Bot Customization

### Goal
Let tenants customize bot appearance and generate embed code.

### Prompt 6.1 - Appearance Settings Backend

```
Add appearance customization:

DATABASE:
Table: chatbot_appearance
- id (UUID)
- chatbot_id (FK, unique)
- primary_color (string, hex)
- header_text (string) - shown in widget header
- avatar_url (string, nullable)
- position (enum: bottom-right, bottom-left)
- welcome_message (text)
- initial_suggestions (JSONB array of strings)
- show_branding (boolean, default true)
- created_at, updated_at

ENDPOINTS:
GET /api/chatbots/{id}/appearance
- Returns appearance settings (with defaults if not set)

PATCH /api/chatbots/{id}/appearance
- Update appearance settings

POST /api/chatbots/{id}/avatar
- Upload custom avatar image
- Store in uploads, return URL

GET /api/widget/{chatbot_id}/config (PUBLIC, no auth)
- Returns appearance config for widget to fetch
- Include: colors, header_text, avatar_url, position, welcome_message, initial_suggestions
```

### Prompt 6.2 - Appearance Editor UI

```
Create appearance customization page:

/dashboard/chatbots/{id}/appearance

TWO-COLUMN LAYOUT:
- Left: Settings form
- Right: Live preview (actual widget)

SETTINGS FORM:
1. Basic
   - Header text (what shows in widget header)
   - Welcome message (first bot message)
   
2. Colors
   - Primary color picker
   - Show preset color swatches
   
3. Avatar
   - Upload custom image
   - Or choose from defaults
   - Preview thumbnail
   
4. Position
   - Radio: Bottom Left / Bottom Right
   
5. Initial Suggestions
   - Two text inputs for default suggestions
   - Help text: "Shown when chat opens"
   
6. Branding
   - Toggle: Show "Powered by YourBrand"

[Save Changes] button (disabled until changes made)

LIVE PREVIEW:
- Render actual widget component in iframe
- Pass current settings as config
- Updates in real-time as form changes
- "Open Preview" button to test interaction
```

### Prompt 6.3 - Embed Code Generator

```
Create embed code page:

/dashboard/chatbots/{id}/embed

DISPLAY:
1. Status indicator
   - Green: "Ready to embed" (has knowledge sources)
   - Yellow: "No knowledge added" (still works but warn)
   
2. Embed Code Box
   - Syntax highlighted code block
   - One-click copy button
   
3. Code:
<script 
  src="https://yourapp.com/widget.js"
  data-chatbot-id="{chatbot.id}"
  async
></script>


5. Test Section:
   - "Test Your Bot" button
   - Opens modal with widget preview
   - Can send test messages

6. Domain Restrictions (optional, future):
   - List allowed domains
   - "Any domain" or specify whitelist
```

### Deliverable Checklist
- [ ] Can customize colors
- [ ] Can set custom welcome message
- [ ] Can upload avatar
- [ ] Live preview shows changes
- [ ] Embed code generated correctly
- [ ] Widget fetches config on load
- [ ] Installation instructions clear

---

## 🏃 Sprint 7: Human Fallback

### Goal
Configure what happens when bot can't answer.

### Prompt 7.1 - Fallback Backend

```
Add human fallback system:

DATABASE:
Table: fallback_settings
- id (UUID)
- chatbot_id (FK, unique)
- enabled (boolean)
- method (enum: show_contact, contact_form, external_link)
- contact_email (string, nullable)
- contact_phone (string, nullable)
- contact_hours (string, nullable)
- external_url (string, nullable) - for Zendesk etc.
- fallback_message (text)
- created_at, updated_at

Table: contact_submissions
- id (UUID)
- chatbot_id (FK)
- session_id (FK, nullable)
- user_email (string)
- user_message (text)
- conversation_context (text) - last few messages
- status (enum: new, read, resolved)
- created_at

FALLBACK TRIGGER LOGIC:
Add to chat response:
{
  ...response,
  triggered_fallback: boolean,
  fallback_reason: "low_confidence" | "user_requested" | null
}

Trigger when:
- retrieval_confidence < 0.4
- user says "talk to human", "support", "agent"
- 2+ consecutive low-confidence responses

ENDPOINTS:
GET/PATCH /api/chatbots/{id}/fallback
- Get/update fallback settings

POST /api/chat/{chatbot_id}/contact
- Submit contact form
- Input: { email, message, session_id }
- Stores in contact_submissions

GET /api/chatbots/{id}/contact-submissions
- List contact form submissions (paginated)

PATCH /api/contact-submissions/{id}
- Mark as read/resolved
```

### Prompt 7.2 - Fallback Configuration UI

```
Create fallback settings page:

/dashboard/chatbots/{id}/fallback

FORM:
1. Enable Fallback
   - Toggle switch
   
2. Fallback Method (radio):
   ○ Show contact information
     - Email input
     - Phone input (optional)
     - Business hours (optional)
     
   ○ Show contact form
     - Collects user email + message
     - You'll see submissions in dashboard
     
   ○ Redirect to external chat
     - URL input (Zendesk widget URL, etc.)

3. Fallback Message
   - Textarea with placeholder:
   "I'm not able to help with this. Please contact our support team."
   - Preview how it looks

[Save Settings]

SUBMISSIONS TAB (if contact form enabled):
- Table: Date, Email, Message preview, Status
- Click row to expand full message + conversation context
- Mark as resolved checkbox
- Export to CSV button
```

### Prompt 7.3 - Widget Fallback UI

```
Add fallback UI to widget:

WHEN FALLBACK TRIGGERS:
1. Bot sends fallback message
2. Based on settings, show appropriate UI:

METHOD: SHOW_CONTACT
┌─────────────────────────────────────────┐
│ 🤖 I'm not able to help with this.     │
│                                         │
│ 📧 Contact Support                      │
│    support@store.com                    │
│    Mon-Fri, 9AM-5PM EST                │
│                                         │
│ 📞 Call Us                              │
│    +1-800-123-4567                      │
└─────────────────────────────────────────┘

METHOD: CONTACT_FORM
┌─────────────────────────────────────────┐
│ 🤖 I'll connect you with our team.     │
│                                         │
│ 📧 Your email                           │
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ 💬 Your question                        │
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│        [ Submit ]                       │
│                                         │
│ ✓ We'll get back within 24 hours       │
└─────────────────────────────────────────┘

METHOD: EXTERNAL_LINK
┌─────────────────────────────────────────┐
│ 🤖 I'll connect you with our team.     │
│                                         │
│    [ Chat with Support → ]              │
│    Opens in new window                  │
└─────────────────────────────────────────┘

After contact form submit, show success message.
User can continue chatting after fallback.
```

### Deliverable Checklist
- [ ] Fallback triggers on low confidence
- [ ] Fallback triggers on user request
- [ ] Contact info displays in widget
- [ ] Contact form submits successfully
- [ ] Submissions visible in dashboard
- [ ] Can mark submissions as resolved

---

## 🏃 Sprint 8: Analytics

### Goal
Track and display deflection rate and unanswered queries.

### Prompt 8.1 - Analytics Tracking Backend

```
Add analytics event tracking:

DATABASE:
Table: analytics_events
- id (UUID)
- chatbot_id (FK)
- session_id (FK)
- event_type (enum: see below)
- metadata (JSONB)
- created_at

EVENT TYPES:
- session_start
- message_sent (user message)
- message_received (bot response)
- fallback_triggered
- contact_form_submitted
- suggestion_clicked
- session_end (inactivity timeout: 30 min)

AUTOMATIC TRACKING:
Modify chat endpoint to log:
- session_start (first message in session)
- message_sent + message_received (every exchange)
- fallback_triggered (when applicable)

Include in message_received metadata:
{
  retrieval_confidence: 0.75,
  sources_count: 3,
  response_time_ms: 450,
  was_answered: true  // confidence > threshold
}

AGGREGATION ENDPOINTS:
GET /api/chatbots/{id}/analytics/overview
- Period: ?period=7d|30d|90d
Returns:
{
  total_sessions: 150,
  total_messages: 890,
  deflection_rate: 78.5,  // % sessions without fallback
  avg_messages_per_session: 5.9,
  unanswered_rate: 12.3
}

GET /api/chatbots/{id}/analytics/unanswered
- Returns top unanswered queries (grouped by similarity)
- Include count of times asked
{
  queries: [
    { query: "Do you offer EMI?", count: 23, sample_messages: [...] },
    { query: "Warranty period?", count: 18, sample_messages: [...] }
  ]
}

Use PostgreSQL window functions for efficient aggregation.
```

### Prompt 8.2 - Analytics Dashboard UI

```
Create analytics dashboard:

/dashboard/chatbots/{id}/analytics

HEADER:
- Chatbot name
- Date range picker (Last 7 days, 30 days, 90 days)

METRICS CARDS (row of 4):
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Sessions     │ │ Messages     │ │ Deflection   │ │ Unanswered   │
│    150       │ │    890       │ │   78.5%      │ │   12.3%      │
│   ↑ 12%      │ │   ↑ 8%       │ │   ↑ 5%       │ │   ↓ 3%       │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘

DEFLECTION RATE SECTION:
- Visual bar/gauge showing 78.5%
- "78 of 100 sessions resolved without human help"
- Trend line chart (optional, simple)

UNANSWERED QUERIES SECTION:
- Table:
  | Query | Times Asked | Action |
  |-------|-------------|--------|
  | "Do you offer EMI payment?" | 23 | [Add to FAQ] |
  | "What's the warranty?" | 18 | [Add to FAQ] |
  | "Store locations?" | 12 | [Add to FAQ] |

- [Add to FAQ] button opens modal:
  - Pre-filled question
  - Empty answer textarea
  - Save creates QA pair

- [Export All] button - downloads CSV
- [Mark as Addressed] - hides from list

Keep it simple - focus on actionable insights.
Use charts only if they add value (recharts library).
```

### Prompt 8.3 - Query Clustering

```
Add intelligent query clustering for unanswered queries:

PROBLEM:
Raw queries are noisy:
- "do you have emi"
- "EMI available?"
- "can i pay in installments"
- "emi option"

These should cluster together.

SOLUTION:
1. Embed all unanswered queries
2. Cluster using cosine similarity (threshold: 0.85)
3. Pick most common phrasing as representative
4. Sum counts

IMPLEMENTATION:
Background job (run daily or on-demand):

async def cluster_unanswered_queries(chatbot_id):
    # Get all messages with was_answered=false
    queries = get_unanswered_queries(chatbot_id, days=30)
    
    # Embed all queries
    embeddings = embed_texts([q.content for q in queries])
    
    # Simple clustering: group by similarity > 0.85
    clusters = []
    for i, query in enumerate(queries):
        matched = False
        for cluster in clusters:
            if cosine_sim(embeddings[i], cluster.centroid) > 0.85:
                cluster.add(query)
                matched = True
                break
        if not matched:
            clusters.append(new_cluster(query, embeddings[i]))
    
    # Return clusters sorted by count
    return sorted(clusters, key=lambda c: c.count, reverse=True)

Store cluster results in cache/DB for fast dashboard loading.
```

### Deliverable Checklist
- [ ] Events tracked automatically
- [ ] Deflection rate calculated correctly
- [ ] Unanswered queries detected
- [ ] Similar queries clustered
- [ ] "Add to FAQ" creates QA pair
- [ ] Analytics dashboard shows metrics

---

## 🏃 Sprint 9: Auto-Recrawl

### Goal
Scheduled re-crawling with change detection.

### Prompt 9.1 - Scheduling Backend

```
Add crawl scheduling:

DATABASE:
Table: crawl_schedules
- id (UUID)
- knowledge_source_id (FK)
- schedule_type (enum: manual, daily, weekly, monthly)
- day_of_week (int 0-6, nullable) - for weekly
- preferred_hour (int 0-23, default 2) - UTC
- is_active (boolean)
- last_crawl_at (timestamp)
- next_crawl_at (timestamp)
- created_at, updated_at

Table: crawl_history
- id (UUID)
- knowledge_source_id (FK)
- started_at, completed_at
- status (enum: success, partial, failed)
- pages_checked (int)
- pages_added (int)
- pages_updated (int)
- pages_removed (int)
- error_message (text, nullable)

SCHEDULER:
Create background scheduler (APScheduler or simple cron):
- Run every hour
- Find schedules where next_crawl_at <= now
- Execute crawl for each
- Update next_crawl_at based on schedule_type

DIFF DETECTION:
When re-crawling:
1. Crawl pages, compute content_hash for each
2. Compare with existing crawled_pages:
   - Hash match → skip (no change)
   - Hash differs → update content, re-embed
   - New URL → add
   - Missing URL → soft delete (mark removed)
3. Log stats in crawl_history

ENDPOINTS:
GET/POST /api/knowledge-sources/{id}/schedule
- Get or set crawl schedule

POST /api/knowledge-sources/{id}/crawl-now
- Trigger immediate re-crawl

GET /api/knowledge-sources/{id}/crawl-history
- List past crawls with stats
```

### Prompt 9.2 - Scheduling UI

```
Add scheduling UI to knowledge source management:

In /dashboard/chatbots/{id}/knowledge, for each URL source:

EXPAND ROW TO SHOW:
┌─────────────────────────────────────────────────────────────┐
│ 🌐 https://store.com                                        │
│ 156 pages • Last synced: Jan 1, 2026 2:15 AM               │
│                                                             │
│ ⚙️ Sync Settings                                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Sync Frequency:                                         │ │
│ │ ○ Manual only                                           │ │
│ │ ○ Daily                                                 │ │
│ │ ● Weekly - Every [Monday ▼] at [2 AM ▼] UTC            │ │
│ │ ○ Monthly                                               │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Next sync: Jan 8, 2026 at 2:00 AM UTC                      │
│                                                             │
│ [ Sync Now ] [ View History ]                               │
└─────────────────────────────────────────────────────────────┘

SYNC HISTORY MODAL:
Table showing:
| Date | Duration | Pages | Added | Updated | Removed | Status |
|------|----------|-------|-------|---------|---------|--------|
| Jan 1 | 45s | 156 | 0 | 3 | 0 | ✅ Success |
| Dec 25 | 52s | 153 | 5 | 2 | 1 | ✅ Success |

Show notification when scheduled sync completes (store in notifications table, show in dashboard header).
```

### Deliverable Checklist
- [ ] Can set schedule (daily/weekly/monthly)
- [ ] Scheduler runs and triggers crawls
- [ ] Diff detection works (add/update/remove)
- [ ] Crawl history recorded
- [ ] Manual "Sync Now" works
- [ ] Next sync time displayed

---

## 🏃 Sprint 10: Polish & Deploy

### Goal
Final testing, optimization, and production deployment.

### Prompt 10.1 - Error Handling & Edge Cases

```
Add comprehensive error handling:

BACKEND:
1. Global exception handler with proper error responses
2. Validation errors return 422 with details
3. Rate limiting with clear error messages
4. Timeout handling for:
   - Crawling (max 5 min per source)
   - LLM calls (max 30s)
   - Embedding generation (max 60s)

WIDGET:
1. Graceful degradation if API unreachable
2. Retry logic (3 attempts with exponential backoff)
3. Offline message queuing
4. Clear error states:
   - "Connection lost. Retrying..."
   - "Something went wrong. Please try again."

DASHBOARD:
1. Form validation on all inputs
2. Optimistic UI updates with rollback on error
3. Toast notifications for all actions
4. Loading skeletons for data fetching

TEST CASES TO HANDLE:
- Empty knowledge base (bot should say "I don't have any information yet")
- Very long user messages (truncate at 2000 chars)
- Rapid message sending (queue and process in order)
- Session expiry mid-conversation
- Invalid chatbot_id in widget
```

### Prompt 10.2 - Performance Optimization

```
Optimize for production:

BACKEND:
1. Database indexes:
   - embeddings: (chatbot_id, source_type)
   - embeddings: HNSW index on embedding vector
   - chat_messages: (session_id, created_at)
   - analytics_events: (chatbot_id, created_at)

2. Connection pooling for PostgreSQL
3. Cache frequently accessed data:
   - Chatbot config (5 min TTL)
   - Appearance settings (5 min TTL)
   - Fallback settings (5 min TTL)
   
4. Background job queue for:
   - Crawling
   - Embedding generation
   - Analytics aggregation
   - Summary generation

WIDGET:
1. Lazy load - don't fetch config until button clicked
2. Compress messages in localStorage
3. Debounce typing indicator
4. Preconnect to API domain

FRONTEND:
1. Code splitting by route
2. Image optimization
3. Static generation where possible
4. API response caching with SWR/React Query
```

### Prompt 10.3 - Deployment Setup

```
Create production deployment configuration:

DOCKER:
- Dockerfile for FastAPI backend
- Dockerfile for Next.js frontend
- docker-compose.prod.yml with:
  - Backend service
  - Frontend service
  - PostgreSQL with pgvector
  - Redis (for caching/queues)
  - Nginx reverse proxy

ENVIRONMENT:
.env.production template with:
- DATABASE_URL
- REDIS_URL
- JWT_SECRET
- OPENAI_API_KEY
- WIDGET_BASE_URL
- CORS_ORIGINS
- SENTRY_DSN (optional)

DEPLOYMENT OPTIONS (choose one):
1. Railway/Render (easy, managed)
2. DigitalOcean App Platform
3. AWS ECS/Fargate
4. Self-hosted VPS with Docker

REQUIRED INFRASTRUCTURE:
- PostgreSQL 15+ with pgvector extension
- Redis for background jobs
- S3-compatible storage for file uploads
- CDN for widget.js (CloudFlare, etc.)

CI/CD:
- GitHub Actions workflow
- Run tests on PR
- Deploy to staging on merge to main
- Manual promotion to production

MONITORING:
- Health check endpoints
- Sentry for error tracking
- Basic logging to stdout (collect with platform tools)
```

### Deliverable Checklist
- [ ] All error cases handled gracefully
- [ ] Database indexes created
- [ ] Caching implemented
- [ ] Docker images build successfully
- [ ] Can deploy to chosen platform
- [ ] Widget served via CDN
- [ ] Health checks passing
- [ ] Basic monitoring in place

---

## 📋 Summary: Sprint Prompts Quick Reference

| Sprint | Key Prompts |
|--------|-------------|
| **0** | Project setup, Docker, DB schema |
| **1** | Auth backend, Auth frontend, Dashboard layout |
| **2** | Chatbot CRUD, Crawling service, Embedding pipeline, Crawl UI |
| **3** | File upload, QA pairs, Knowledge management UI |
| **4** | Chat API with RAG, Widget core, Widget styling |
| **5** | Conversation memory, Image input, Suggestions UI |
| **6** | Appearance backend, Appearance editor, Embed code |
| **7** | Fallback backend, Fallback settings UI, Widget fallback UI |
| **8** | Analytics tracking, Analytics dashboard, Query clustering |
| **9** | Scheduling backend, Scheduling UI |
| **10** | Error handling, Optimization, Deployment |

---

## 🚦 How to Use These Prompts

1. **Start each sprint** by reading through all prompts
2. **Run prompts sequentially** within each sprint
3. **Test after each prompt** before moving to next
4. **Modify prompts** if you need different tech/styling
5. **Switch to Agent mode** in Cursor to apply code changes

Would you like me to expand any sprint or adjust the scope?