# Complete Code Explanation - Embeddable AI Chatbot SaaS

This document provides a comprehensive explanation of the entire codebase, from architecture to implementation details.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Backend (FastAPI) Explained](#backend-fastapi-explained)
6. [Frontend (Next.js) Explained](#frontend-nextjs-explained)
7. [Widget (Preact) Explained](#widget-preact-explained)
8. [Database Schema](#database-schema)
9. [Key Features Implementation](#key-features-implementation)
10. [Data Flow & Request Lifecycle](#data-flow--request-lifecycle)
11. [Getting Started](#getting-started)

---

## Project Overview

This is a **multi-tenant SaaS platform** that allows businesses to create and embed AI-powered chatbots on their websites. The platform consists of three main applications:

1. **API (Backend)**: FastAPI server handling authentication, chatbot management, and AI interactions
2. **Web (Dashboard)**: Next.js 14 application for managing chatbots and viewing analytics
3. **Widget**: Lightweight Preact component that can be embedded on any website

### What Problems Does It Solve?

- **For Business Owners**: Create custom AI chatbots without coding
- **For End Users**: Get instant answers to questions on websites
- **For Developers**: Easy-to-embed widget with minimal footprint

---

## Architecture

The application follows a **monorepo architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                         MONOREPO                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │     API      │  │     WEB      │  │    WIDGET    │    │
│  │  (FastAPI)   │  │  (Next.js)   │  │   (Preact)   │    │
│  │              │  │              │  │              │    │
│  │  Port: 8000  │  │  Port: 3000  │  │  Port: 3001  │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                  │             │
│         └─────────────────┼──────────────────┘             │
│                           │                                │
│                    ┌──────▼───────┐                        │
│                    │  PostgreSQL   │                       │
│                    │  + pgvector   │                       │
│                    └──────────────┘                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              SHARED PACKAGES                         │ │
│  │  • @chatbot/shared (Types & Utilities)               │ │
│  │  • @chatbot/ui (Reusable Components)                 │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Tenant Architecture

Each tenant (organization) has:
- Isolated data (chatbots, users, knowledge sources)
- JWT tokens with `tenant_id` for data isolation
- Role-based access control (admin, member, viewer)

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with pgvector extension
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: JWT (access + refresh tokens)
- **Migrations**: Alembic
- **AI/LLM**: Integration with Groq API
- **Scheduling**: APScheduler for background jobs

### Frontend (Dashboard)
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Context API

### Widget
- **Framework**: Preact (lightweight React alternative)
- **Build Tool**: Vite
- **Bundle Size**: <50KB gzipped
- **Language**: TypeScript

### DevOps
- **Containerization**: Docker & Docker Compose
- **Package Manager**: pnpm (for Node.js)
- **Monorepo**: pnpm workspaces

---

## Project Structure

```
embed_chatbot/
├── .env                      # Shared environment variables
├── docker-compose.yml        # Development environment
├── docker-compose.prod.yml   # Production environment
├── pnpm-workspace.yaml       # Monorepo workspace config
├── requirements.txt          # Python dependencies
│
├── apps/                     # Main applications
│   ├── api/                  # Backend (FastAPI)
│   ├── web/                  # Frontend Dashboard (Next.js)
│   └── widget/               # Embeddable Widget (Preact)
│
└── packages/                 # Shared packages
    ├── shared/               # TypeScript types & utilities
    └── ui/                   # Reusable UI components
```

---

## Backend (FastAPI) Explained

### Directory Structure

```
apps/api/
├── main.py                   # Application entry point
├── run.py                    # Development server runner
├── alembic/                  # Database migrations
│   └── versions/             # Migration files (21 migrations)
│
└── app/
    ├── api/
    │   └── v1/               # API version 1 routes
    │       ├── auth.py       # Authentication endpoints
    │       ├── chatbots.py   # Chatbot management
    │       ├── chat.py       # Chat interactions
    │       ├── members.py    # Team member management
    │       └── router.py     # Main router
    │
    ├── core/                 # Core functionality
    │   ├── config.py         # Settings & configuration
    │   ├── database.py       # Database connection
    │   ├── security.py       # JWT & password hashing
    │   ├── dependencies.py   # FastAPI dependencies
    │   ├── exceptions.py     # Custom exceptions
    │   └── logging.py        # Logging configuration
    │
    ├── models/               # SQLAlchemy ORM models
    │   ├── tenant.py         # Tenant/Organization model
    │   ├── user.py           # User model
    │   ├── chatbot.py        # Chatbot configuration
    │   ├── chatbot_appearance.py  # UI customization
    │   ├── chatbot_permission.py  # Access control
    │   ├── knowledge.py      # Knowledge sources & embeddings
    │   └── chat.py           # Chat history
    │
    ├── schemas/              # Pydantic schemas (validation)
    │   └── ...               # Request/response schemas
    │
    └── services/             # Business logic
        ├── auth_service.py   # Authentication logic
        ├── chatbot_service.py # Chatbot operations
        ├── chat_service.py   # AI chat processing
        ├── embedding_service.py # Vector embeddings
        ├── crawler_service.py # Web scraping
        ├── file_service.py   # Document processing
        ├── scheduler_service.py # Background jobs
        ├── member_service.py # Team management
        ├── analytics_service.py # Usage analytics
        └── vision_service.py # Image processing
```

### Application Entry Point (`main.py`)

The `main.py` file is the heart of the FastAPI application:

```python
# 1. Application initialization
app = FastAPI(
    title="Chatbot API",
    lifespan=lifespan  # Manages startup/shutdown
)

# 2. Exception handlers
# - APIException: Custom errors
# - HTTPException: Standard HTTP errors
# - ValidationError: Request validation failures
# - SQLAlchemyError: Database errors
# - Exception: Catch-all for unexpected errors

# 3. Middleware
# - CORS: Cross-origin requests
# - Request logging: Track all requests with timing

# 4. Router inclusion
app.include_router(api_router, prefix="/api/v1")
```

**Key Features:**
- **Lifespan Management**: Starts/stops scheduler, checks database connection
- **Error Handling**: Comprehensive exception handlers with source tracking
- **Request Logging**: Logs method, path, status code, and duration
- **CORS**: Allows cross-origin requests from web and widget

### Core Components

#### 1. Configuration (`core/config.py`)
- Loads environment variables using Pydantic's `BaseSettings`
- Database URL, JWT secrets, API keys, CORS origins
- Validates configuration at startup

#### 2. Database (`core/database.py`)
- Async SQLAlchemy engine and session
- Connection pooling for performance
- Session management with dependency injection

#### 3. Security (`core/security.py`)
- **Password hashing**: bcrypt for secure password storage
- **JWT tokens**: 
  - Access tokens (15 min expiry)
  - Refresh tokens (7 days expiry)
- Token payload includes: `user_id`, `tenant_id`, `email`, `type`

#### 4. Dependencies (`core/dependencies.py`)
- `get_db()`: Provides database session
- `get_current_user()`: Validates JWT and returns user
- `get_current_tenant()`: Returns tenant from token
- Used with FastAPI's `Depends()` for route protection

### Database Models

The application uses SQLAlchemy ORM models representing the database schema:

#### Core Models:
1. **Tenant**: Organizations/workspaces
2. **User**: User accounts with roles (admin, member, viewer)
3. **Chatbot**: AI chatbot configurations
4. **ChatbotAppearance**: UI customization (colors, position, messages)
5. **ChatbotPermission**: Access control for shared chatbots
6. **KnowledgeSource**: Training data sources (files, URLs)
7. **Embedding**: Vector embeddings for semantic search
8. **ChatHistory**: Conversation logs

**Relationships:**
- Tenant → Users (one-to-many)
- Tenant → Chatbots (one-to-many)
- Chatbot → KnowledgeSources (one-to-many)
- KnowledgeSource → Embeddings (one-to-many)
- Chatbot → ChatHistory (one-to-many)

### API Routes

#### Authentication (`api/v1/auth.py`)
- `POST /auth/signup` - Create tenant and admin user
- `POST /auth/login` - Authenticate user
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info
- `POST /auth/change-password` - Change password

#### Chatbots (`api/v1/chatbots.py`)
- `POST /chatbots` - Create chatbot
- `GET /chatbots` - List all chatbots
- `GET /chatbots/{id}` - Get chatbot details
- `PATCH /chatbots/{id}` - Update chatbot
- `DELETE /chatbots/{id}` - Delete chatbot
- `POST /chatbots/{id}/knowledge` - Add knowledge source
- `GET /chatbots/{id}/knowledge` - List knowledge sources
- `DELETE /knowledge/{id}` - Delete knowledge source
- `POST /chatbots/{id}/crawl` - Crawl website for knowledge

#### Chat (`api/v1/chat.py`)
- `POST /chat/{chatbot_id}` - Send message to chatbot
- `GET /chat/{chatbot_id}/history` - Get chat history

#### Members (`api/v1/members.py`)
- `POST /members` - Invite team member
- `GET /members` - List team members
- `PATCH /members/{id}` - Update member role
- `DELETE /members/{id}` - Remove member

### Services (Business Logic)

#### AuthService (`services/auth_service.py`)
- User registration and login
- Password hashing and verification
- Token generation and validation
- Multi-tenant user isolation

#### ChatbotService (`services/chatbot_service.py`)
- CRUD operations for chatbots
- Appearance customization
- Knowledge source management
- Permission management

#### ChatService (`services/chat_service.py`)
- **Core chat processing**:
  1. Receive user message
  2. Search relevant knowledge using embeddings
  3. Build context from knowledge
  4. Call LLM API (Groq) with context
  5. Stream response back to client
  6. Save conversation to history
- **LLM Configuration** (currently hardcoded):
  - Model: `llama-3.3-70b-versatile` (main chat)
  - Temperature: 0.1 (for consistent answers)
  - System prompt: Built dynamically with knowledge context

#### EmbeddingService (`services/embedding_service.py`)
- Convert text to vector embeddings
- Store embeddings with pgvector
- Semantic search using cosine similarity
- Used for retrieving relevant knowledge

#### CrawlerService (`services/crawler_service.py`)
- Web scraping for knowledge ingestion
- Extracts text from websites
- Creates embeddings from crawled content
- Scheduled crawling for updates

#### FileService (`services/file_service.py`)
- Document upload and processing
- Supports: PDF, DOCX, XLSX, TXT
- Text extraction and chunking
- Embedding generation for documents

#### SchedulerService (`services/scheduler_service.py`)
- Background job scheduling using APScheduler
- Periodic website crawling
- Cleanup tasks
- Runs in background thread

### Database Migrations

The application uses **Alembic** for database migrations:
- **21 migration files** in `alembic/versions/`
- Tracks schema changes over time
- Commands:
  - `alembic upgrade head` - Apply all migrations
  - `alembic downgrade -1` - Rollback last migration
  - `alembic revision -m "message"` - Create new migration

---

## Frontend (Next.js) Explained

### Directory Structure

```
apps/web/
├── app/                      # Next.js 14 App Router
│   ├── layout.tsx            # Root layout (applies to all pages)
│   ├── page.tsx              # Home page (/)
│   ├── login/                # Login page
│   ├── signup/               # Signup page
│   ├── dashboard/            # Dashboard pages
│   ├── chatbots/             # Chatbot management
│   ├── embed/                # Embed code page
│   ├── change-password/      # Password change
│   └── globals.css           # Global styles
│
├── components/               # React components
│   ├── ui/                   # shadcn/ui components
│   ├── ChatbotCard.tsx       # Chatbot display card
│   ├── ChatbotForm.tsx       # Create/edit chatbot form
│   ├── KnowledgeTable.tsx    # Knowledge sources table
│   └── ...                   # Other components
│
├── contexts/                 # React Context for state
│   └── AuthContext.tsx       # Authentication state
│
├── lib/                      # Utilities
│   ├── api.ts                # API client
│   └── utils.ts              # Helper functions
│
├── middleware.ts             # Next.js middleware (auth check)
└── next.config.js            # Next.js configuration
```

### How Next.js 14 App Router Works

Next.js 14 uses a **file-based routing** system:

```
app/
├── page.tsx              → Route: /
├── login/
│   └── page.tsx          → Route: /login
├── dashboard/
│   ├── page.tsx          → Route: /dashboard
│   └── [id]/
│       └── page.tsx      → Route: /dashboard/[id] (dynamic)
└── layout.tsx            → Wraps all routes
```

### Key Components

#### 1. Root Layout (`app/layout.tsx`)
- Wraps entire application
- Includes AuthProvider for authentication state
- Sets up HTML structure, metadata

#### 2. Authentication Context (`contexts/AuthContext.tsx`)
- Manages user authentication state
- Provides login/logout functions
- Stores JWT tokens in localStorage
- Checks authentication on mount

#### 3. Middleware (`middleware.ts`)
- Runs before page renders
- Checks if user is authenticated
- Redirects to login if not authenticated
- Protects dashboard routes

#### 4. API Client (`lib/api.ts`)
- Axios instance for API calls
- Automatically adds JWT token to headers
- Handles authentication errors
- Base URL: `http://localhost:8000/api/v1`

### Page Flow

#### Login Flow:
1. User enters email and password
2. Frontend calls `POST /auth/login`
3. Backend validates credentials
4. Returns access token and refresh token
5. Frontend stores tokens in localStorage
6. Redirects to dashboard

#### Dashboard Flow:
1. User navigates to `/dashboard`
2. Middleware checks authentication
3. If authenticated, fetch chatbots from API
4. Display chatbots in grid layout
5. User can create, edit, delete chatbots

#### Chatbot Creation Flow:
1. User clicks "Create Chatbot"
2. Form opens with fields:
   - Name
   - Welcome message
   - Status (draft/active)
3. User submits form
4. Frontend calls `POST /chatbots`
5. Backend creates chatbot with default settings
6. Frontend updates list

---

## Widget (Preact) Explained

### Directory Structure

```
apps/widget/
├── src/
│   ├── index.tsx             # Widget initialization
│   ├── main.tsx              # Entry point
│   ├── app.tsx               # Main App component
│   ├── components/           # Widget components
│   │   ├── ChatWindow.tsx    # Chat interface
│   │   ├── ChatButton.tsx    # Floating chat button
│   │   ├── MessageList.tsx   # Message display
│   │   └── ...
│   ├── styles.css            # Global styles
│   └── widget.css            # Widget-specific styles
│
├── vite.config.ts            # Vite build configuration
└── index.html                # Development HTML
```

### Why Preact?

Preact is a lightweight alternative to React:
- **3KB** vs React's 40KB
- Same API as React (hooks, components)
- Perfect for embeddable widgets
- Fast rendering and small bundle

### Widget Architecture

The widget is designed to be **embeddable** on any website:

#### 1. Auto-initialization
```html
<script
  src="https://your-domain.com/chatbot-widget.js"
  data-auto-init="true"
  data-api-url="https://api.your-domain.com"
  data-tenant-id="tenant-123"
  data-chatbot-id="chatbot-456"
></script>
```

#### 2. Manual initialization
```javascript
ChatbotWidget.init({
  apiUrl: 'https://api.your-domain.com',
  tenantId: 'tenant-123',
  chatbotId: 'chatbot-456',
  theme: {
    primaryColor: '#007bff',
    position: 'bottom-right'
  }
})
```

### Widget Components

#### 1. ChatButton (`components/ChatButton.tsx`)
- Floating button (default: bottom-right)
- Shows unread message count
- Toggles chat window

#### 2. ChatWindow (`components/ChatWindow.tsx`)
- Main chat interface
- Header with chatbot name
- Message list
- Input field
- Close button

#### 3. MessageList (`components/MessageList.tsx`)
- Displays conversation history
- User messages (right-aligned)
- Bot messages (left-aligned)
- Auto-scrolls to bottom
- Loading indicator

### How Widget Communicates

```
┌──────────────┐                ┌──────────────┐
│   Website    │                │  API Server  │
│   (Widget)   │                │   (FastAPI)  │
└──────┬───────┘                └──────▲───────┘
       │                               │
       │  1. User sends message        │
       ├───────────────────────────────┤
       │  POST /chat/{chatbot_id}      │
       │  { message: "Hello" }         │
       │                               │
       │  2. API processes with AI     │
       │     - Search knowledge         │
       │     - Call LLM                │
       │                               │
       │  3. Stream response           │
       │◄───────────────────────────────┤
       │  { response: "Hi there!" }    │
       │                               │
       │  4. Display in UI             │
       │                               │
```

### Widget Build Process

1. Vite bundles all components
2. Outputs single JavaScript file
3. Includes all styles inline
4. Minified and gzipped
5. Result: `chatbot-widget.js` (<50KB)

---

## Database Schema

### Entity Relationship Diagram (Text)

```
┌────────────┐
│   Tenant   │
└─────┬──────┘
      │
      ├─────────────┬─────────────┐
      │             │             │
┌─────▼──────┐ ┌───▼────────┐ ┌──▼──────────┐
│    User    │ │  Chatbot   │ │ Other Data  │
└────────────┘ └─────┬──────┘ └─────────────┘
                     │
         ┌───────────┼────────────┐
         │           │            │
   ┌─────▼────┐ ┌───▼─────────┐ ┌▼─────────────┐
   │Appearance│ │ Knowledge   │ │ ChatHistory  │
   └──────────┘ │   Source    │ └──────────────┘
                └─────┬───────┘
                      │
                ┌─────▼─────┐
                │ Embedding │
                └───────────┘
```

### Tables Explained

#### 1. `tenants`
- **Purpose**: Organizations/workspaces
- **Key Fields**: `id`, `name`, `email`, `created_at`
- **Isolation**: All data belongs to a tenant

#### 2. `users`
- **Purpose**: User accounts
- **Key Fields**: `id`, `tenant_id`, `email`, `password_hash`, `role`
- **Roles**: admin, member, viewer
- **Authentication**: JWT tokens with `user_id` and `tenant_id`

#### 3. `chatbots`
- **Purpose**: Chatbot configurations
- **Key Fields**: 
  - `id`, `tenant_id`, `name`
  - `welcome_message` - Greeting shown to users
  - `status` - draft, active, or paused
  - `confidence_threshold` - Minimum confidence for answers (default: 0.7)
  - `created_by` - User who created the chatbot
- **Note**: LLM settings (model, temperature, system prompt) are currently hardcoded in the chat service

#### 4. `chatbot_appearance`
- **Purpose**: UI customization
- **Key Fields**:
  - `chatbot_id`
  - `primary_color`, `text_color`, `bg_color`
  - `position` - Where to show widget (bottom-right, etc.)
  - `initial_message` - Welcome message
  - `bubble_style` - Button appearance

#### 5. `knowledge_sources`
- **Purpose**: Training data for chatbots
- **Key Fields**:
  - `id`, `chatbot_id`, `type` (file, url, text)
  - `content` - Original content
  - `url` - For web sources
  - `file_path` - For uploaded files
  - `status` - processing, completed, failed

#### 6. `embeddings`
- **Purpose**: Vector representations of knowledge
- **Key Fields**:
  - `id`, `knowledge_source_id`
  - `content` - Text chunk
  - `embedding` - Vector (pgvector type)
  - `metadata` - Additional info
- **Usage**: Semantic search to find relevant knowledge

#### 7. `chat_history`
- **Purpose**: Conversation logs
- **Key Fields**:
  - `id`, `chatbot_id`, `session_id`
  - `message` - User's message
  - `response` - Bot's response
  - `created_at` - Timestamp

---

## Key Features Implementation

### 1. Multi-Tenant Architecture

**How it works:**
1. User signs up → Creates tenant and admin user
2. All API calls include JWT token
3. Token contains `tenant_id`
4. All database queries filter by `tenant_id`

**Example:**
```python
# In any route
async def get_chatbots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Automatically filtered by tenant_id
    chatbots = await db.execute(
        select(Chatbot)
        .where(Chatbot.tenant_id == current_user.tenant_id)
    )
```

### 2. JWT Authentication

**Token Flow:**
```
┌─────────┐                 ┌─────────┐
│ Client  │                 │   API   │
└────┬────┘                 └────┬────┘
     │                           │
     │  1. POST /auth/login      │
     ├───────────────────────────>
     │  email + password          │
     │                           │
     │  2. Validate credentials  │
     │                           │
     │  3. Generate JWT tokens   │
     │  - Access (15 min)        │
     │  - Refresh (7 days)       │
     │                           │
     │◄───────────────────────────┤
     │  tokens + user data        │
     │                           │
     │  4. Store tokens          │
     │  (localStorage)           │
     │                           │
     │  5. Subsequent requests   │
     ├───────────────────────────>
     │  Authorization: Bearer    │
     │  <access_token>           │
```

### 3. Vector Embeddings & Semantic Search

**Purpose**: Find relevant knowledge for answering questions

**Process:**
1. **Ingestion**: 
   - Upload document or add URL
   - Extract text content
   - Split into chunks (500 words each)
   - Generate embeddings using AI model
   - Store in database with pgvector

2. **Search**:
   - User asks question
   - Generate embedding for question
   - Search embeddings using cosine similarity
   - Retrieve top 5 most relevant chunks

3. **Answer Generation**:
   - Pass relevant chunks to LLM as context
   - LLM generates answer based on context
   - Stream response to user

**Example Query:**
```sql
SELECT content, 
       1 - (embedding <=> query_embedding) as similarity
FROM embeddings
WHERE chatbot_id = ?
ORDER BY embedding <=> query_embedding
LIMIT 5
```

### 4. Web Crawling

**How it works:**
1. User provides URL to crawl
2. Crawler fetches webpage
3. Extracts main content (removes nav, footer, etc.)
4. Generates embeddings for content
5. Schedules periodic re-crawl (optional)

**Scheduler:**
- Uses APScheduler
- Runs in background thread
- Checks for scheduled crawls every hour
- Updates knowledge automatically

### 5. File Processing

**Supported formats:**
- PDF (PyPDF2)
- DOCX (python-docx)
- XLSX (openpyxl)
- TXT (plain text)

**Process:**
1. Upload file via API
2. Save to `uploads/` directory
3. Extract text based on file type
4. Generate embeddings
5. Store in database

### 6. Real-time Chat

**Streaming Response:**
```python
async def chat(message: str):
    # 1. Search knowledge
    context = await search_embeddings(message)
    
    # 2. Call LLM
    async for chunk in llm_stream(message, context):
        # 3. Stream to client
        yield chunk
```

**Benefits:**
- User sees response immediately
- Better UX for long responses
- Lower perceived latency

---

## Data Flow & Request Lifecycle

### Complete Chat Request Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. USER INTERACTION                                          │
└──────────────────────────────────────────────────────────────┘
   User types message in widget
   Widget validates input
   Shows loading indicator
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. WIDGET → API REQUEST                                      │
└──────────────────────────────────────────────────────────────┘
   POST /api/v1/chat/{chatbot_id}
   Headers: { "Authorization": "Bearer <token>" }
   Body: { "message": "What are your hours?" }
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. API - AUTHENTICATION & VALIDATION                         │
└──────────────────────────────────────────────────────────────┘
   main.py: Request logging middleware
   └→ Logs: "POST /chat/123 → ..."
   
   dependencies.py: JWT validation
   └→ Decode token
   └→ Get user and tenant
   
   chat.py: Route handler
   └→ Validate request body
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. CHAT SERVICE - PROCESS REQUEST                            │
└──────────────────────────────────────────────────────────────┘
   chat_service.py:
   
   Step 1: Get chatbot config
   └→ Query database for chatbot settings
   └→ Get system prompt, model, temperature
   
   Step 2: Search relevant knowledge
   └→ embedding_service.py
   └→ Generate embedding for user message
   └→ Query pgvector for similar embeddings
   └→ Return top 5 relevant chunks
   
   Step 3: Build context
   └→ Combine relevant knowledge
   └→ Add system prompt
   └→ Format for LLM
   
   Step 4: Call LLM
   └→ Send to Groq API
   └→ Stream response chunks
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. STREAMING RESPONSE                                        │
└──────────────────────────────────────────────────────────────┘
   FastAPI: Yield chunks as they arrive
   └→ "We"
   └→ " are"
   └→ " open"
   └→ " Monday"
   └→ "-Friday"
   └→ " 9AM-5PM"
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. WIDGET - DISPLAY RESPONSE                                 │
└──────────────────────────────────────────────────────────────┘
   Receive chunks via EventSource or fetch
   Append to message bubble
   Auto-scroll to bottom
   Hide loading indicator
              │
              ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. SAVE TO HISTORY                                           │
└──────────────────────────────────────────────────────────────┘
   Create chat_history record
   └→ Store message + response
   └→ Associate with chatbot_id
   └→ Track session_id for conversation
```

### Authentication Flow

```
┌──────────────────────────────────────────────────────────────┐
│ SIGNUP FLOW                                                  │
└──────────────────────────────────────────────────────────────┘

1. Frontend: POST /auth/signup
   { tenant_name, email, password }
        │
        ▼
2. auth.py: signup() route
        │
        ▼
3. auth_service.py: create_tenant_and_admin()
   ├→ Check if email exists
   ├→ Hash password (bcrypt)
   ├→ Create Tenant record
   ├→ Create User record (role: admin)
   └→ Commit to database
        │
        ▼
4. Generate JWT tokens
   ├→ Access token (15 min)
   └→ Refresh token (7 days)
        │
        ▼
5. Return to frontend
   { access_token, refresh_token, user, tenant }
        │
        ▼
6. Frontend stores tokens
   └→ localStorage.setItem('access_token', ...)
        │
        ▼
7. Redirect to dashboard
```

### Chatbot Creation Flow

```
┌──────────────────────────────────────────────────────────────┐
│ CREATE CHATBOT FLOW                                          │
└──────────────────────────────────────────────────────────────┘

1. User fills form in dashboard
   ├→ Name: "Support Bot"
   ├→ Welcome Message: "Hello! How can I help you?"
   └→ Status: "active"
        │
        ▼
2. Frontend: POST /chatbots
   Headers: { Authorization: Bearer <token> }
   Body: { name, welcome_message }
        │
        ▼
3. chatbots.py: create_chatbot() route
   └→ Validate JWT (get current_user)
        │
        ▼
4. chatbot_service.py: create_chatbot()
   ├→ Create Chatbot record
   │  └→ tenant_id = current_user.tenant_id
   │  └→ status = "draft" (default)
   │  └→ confidence_threshold = 0.7 (default)
   ├→ Create default ChatbotAppearance
   │  └→ primary_color = "#007bff"
   │  └→ position = "bottom-right"
   └→ Commit to database
        │
        ▼
5. Return chatbot data
   { id, name, welcome_message, status, ... }
        │
        ▼
6. Frontend updates UI
   └→ Show new chatbot in list
   └→ Show success message
```

### Knowledge Ingestion Flow

```
┌──────────────────────────────────────────────────────────────┐
│ ADD KNOWLEDGE SOURCE (FILE)                                  │
└──────────────────────────────────────────────────────────────┘

1. User uploads PDF file
        │
        ▼
2. Frontend: POST /chatbots/{id}/knowledge
   Content-Type: multipart/form-data
   { file: <pdf_file> }
        │
        ▼
3. chatbots.py: add_knowledge() route
        │
        ▼
4. file_service.py: process_file()
   ├→ Save file to uploads/ directory
   ├→ Detect file type (PDF)
   ├→ Extract text (PyPDF2)
   ├→ Create KnowledgeSource record
   └→ status = "processing"
        │
        ▼
5. embedding_service.py: create_embeddings()
   ├→ Split text into chunks (500 words)
   ├→ For each chunk:
   │  ├→ Generate embedding vector
   │  └→ Create Embedding record
   └→ Update status = "completed"
        │
        ▼
6. Knowledge ready for chat
   └→ Bot can now answer questions using this content
```

---

## Getting Started

### Prerequisites

- **Node.js** 18+ (for frontend and widget)
- **Python** 3.11+ (for backend)
- **Docker** & **Docker Compose** (for database)
- **pnpm** 8+ (package manager)

### Quick Start (Docker - Recommended)

This is the easiest way to run everything:

```bash
# 1. Clone repository
git clone <repository-url>
cd embed_chatbot

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Run database migrations
docker-compose exec api alembic upgrade head

# 5. Open in browser
# - Dashboard: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - Widget: http://localhost:3001
```

### Manual Development Setup

For development with hot-reloading:

```bash
# 1. Install dependencies
pnpm install
pip install -r requirements.txt

# 2. Start PostgreSQL
docker-compose up -d postgres

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run migrations
cd apps/api
alembic upgrade head

# 5. Start all development servers
cd ../..
pnpm dev
```

This starts:
- API server on port 8000 (with auto-reload)
- Web dashboard on port 3000 (with hot-reload)
- Widget on port 3001 (with hot-reload)

### First Steps After Setup

1. **Open Dashboard**: http://localhost:3000
2. **Sign Up**: Create your tenant and admin account
3. **Create Chatbot**: Click "New Chatbot", fill in details
4. **Add Knowledge**: Upload files or add URLs
5. **Test Chat**: Use the preview to test your chatbot
6. **Get Embed Code**: Copy widget code for your website

### Environment Variables

Key variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/chatbot_db

# JWT Authentication
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI/LLM
GROQ_API_KEY=your-groq-api-key

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# API Server
API_HOST=0.0.0.0
API_PORT=8000
```

### Testing the System

#### Test Backend:
```bash
# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

#### Test Frontend:
```bash
# Open dashboard
open http://localhost:3000

# Login with your credentials
# Create a chatbot
# Test chat functionality
```

#### Test Widget:
```html
<!-- Add to any HTML file -->
<script
  src="http://localhost:3001/chatbot-widget.js"
  data-auto-init="true"
  data-api-url="http://localhost:8000"
  data-chatbot-id="<your-chatbot-id>"
></script>
```

### Common Commands

```bash
# Start all services
pnpm dev

# Start individual services
cd apps/api && python run.py          # Backend only
cd apps/web && pnpm dev               # Dashboard only
cd apps/widget && pnpm dev            # Widget only

# Database migrations
cd apps/api
alembic revision -m "description"     # Create migration
alembic upgrade head                  # Apply migrations
alembic downgrade -1                  # Rollback last

# Build for production
pnpm build                            # Build all apps
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose logs -f api            # API logs
docker-compose logs -f web            # Web logs
docker-compose logs -f postgres       # Database logs
```

---

## Summary

This embeddable AI chatbot SaaS is a complete, production-ready platform with:

**Architecture:**
- Multi-tenant SaaS design
- Microservices-based monorepo
- JWT authentication
- Vector embeddings for knowledge

**Components:**
- **Backend**: FastAPI with async SQLAlchemy
- **Frontend**: Next.js 14 dashboard
- **Widget**: Lightweight Preact component
- **Database**: PostgreSQL with pgvector

**Key Features:**
- Create and manage multiple chatbots
- Upload documents and crawl websites for knowledge
- Semantic search using vector embeddings
- Real-time streaming chat responses
- Embeddable widget (<50KB)
- Team collaboration with roles
- Customizable appearance

**Data Flow:**
1. User signs up → Creates tenant
2. Creates chatbot → Configures settings
3. Adds knowledge → Processes and embeds
4. Embeds widget → Users can chat
5. Chat requests → Search knowledge → AI responds

The codebase is well-structured, follows best practices, and is ready for deployment and scaling.
