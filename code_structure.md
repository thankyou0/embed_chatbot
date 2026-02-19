# Embed Chatbot - Code Structure

## Repository Overview

```
embed_chatbot/
├── apps/                    # Main applications
│   ├── api/                 # FastAPI backend
│   ├── web/                 # Next.js dashboard
│   └── widget/              # Preact embeddable widget
├── packages/                # Shared monorepo packages
├── docker-compose.yml       # Development stack
└── docker-compose.prod.yml  # Production stack
```

---

## Backend API (`apps/api/`)

### Core Structure

```
apps/api/
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container build
├── alembic.ini              # Database migration config
│
├── alembic/                 # Database migrations
│   ├── env.py               # Migration environment
│   └── versions/            # Migration scripts (001-026+)
│
└── app/
    ├── __init__.py
    ├── api/                 # API layer
    ├── core/                # Core utilities
    ├── models/              # Database models
    ├── schemas/             # Pydantic schemas
    └── services/            # Business logic
```

### API Routes (`app/api/v1/`)

| File                         | Purpose                                        |
| ---------------------------- | ---------------------------------------------- |
| `router.py`                  | Main router aggregating all endpoints          |
| `auth.py`                    | Authentication (signup, login, password reset) |
| `chatbots.py`                | Chatbot CRUD, knowledge sources, crawling      |
| `chat.py`                    | Chat messaging with streaming support          |
| `members.py`                 | Team member management                         |
| `billing.py`                 | Subscription and billing                       |
| `usage.py`                   | Usage statistics and quotas                    |
| `endpoints/crawl_preview.py` | Crawl preview endpoint                         |

### Core Utilities (`app/core/`)

| File                 | Purpose                                    |
| -------------------- | ------------------------------------------ |
| `config.py`          | Environment configuration (Settings class) |
| `database.py`        | SQLAlchemy async engine setup              |
| `dependencies.py`    | FastAPI dependency injection               |
| `security.py`        | JWT, password hashing, authentication      |
| `exceptions.py`      | Custom exception classes                   |
| `error_sanitizer.py` | User-friendly error messages               |
| `logging.py`         | Structured logging with Loguru             |
| `monitoring.py`      | Sentry integration                         |
| `rate_limiter.py`    | Redis-based rate limiting                  |
| `redis_client.py`    | Redis connection management                |
| `tier_limits.py`     | Subscription tier definitions              |

### Database Models (`app/models/`)

| File                      | Purpose                                                       |
| ------------------------- | ------------------------------------------------------------- |
| `user.py`                 | User model with authentication                                |
| `tenant.py`               | Organization/tenant model                                     |
| `chatbot.py`              | Chatbot and activity models                                   |
| `chatbot_appearance.py`   | Widget appearance settings                                    |
| `chatbot_permission.py`   | Team permissions                                              |
| `knowledge.py`            | KnowledgeSource, CrawledPage, Embedding, QAPair, UploadedFile |
| `chat.py`                 | ChatSession and ChatMessage                                   |
| `subscription.py`         | Subscription plans and billing                                |
| `password_reset_token.py` | Password reset tokens                                         |

### Services (`app/services/`)

| File                   | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| `auth_service.py`      | User authentication logic                  |
| `chatbot_service.py`   | Chatbot CRUD and management                |
| `chat_service.py`      | Chat message handling with RAG             |
| `chat_streaming.py`    | HTTP streaming response utilities          |
| `crawler_service.py`   | Website crawling with cancellation support |
| `embedding_service.py` | Vector embeddings via HuggingFace          |
| `file_service.py`      | File upload processing                     |
| `member_service.py`    | Team member management                     |
| `billing_service.py`   | Subscription and quota management          |
| `analytics_service.py` | Usage analytics                            |
| `email_service.py`     | Email notifications                        |
| `scheduler_service.py` | Scheduled crawl jobs                       |
| `product_extractor.py` | E-commerce product detection               |
| `vision_service.py`    | Image/vision processing                    |
| `cache_service.py`     | Redis caching utilities                    |

### Schemas (`app/schemas/`)

Pydantic models for request/response validation:

- `auth.py`, `user.py`, `tenant.py`
- `chatbot.py`, `appearance.py`, `knowledge.py`
- `chat.py`, `member.py`, `billing.py`, `analytics.py`

---

## Frontend Dashboard (`apps/web/`)

### Structure

```
apps/web/
├── app/                     # Next.js App Router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Landing page
│   ├── login/               # Authentication pages
│   ├── signup/
│   ├── forgot-password/
│   ├── reset-password/
│   ├── change-password/
│   ├── dashboard/           # Main dashboard
│   │   ├── page.tsx         # Dashboard home
│   │   ├── layout.tsx       # Dashboard layout with sidebar
│   │   ├── chatbots/        # Chatbot management
│   │   │   ├── page.tsx     # Chatbot list
│   │   │   └── [chatbotId]/ # Individual chatbot
│   │   ├── analytics/       # Analytics page
│   │   ├── billing/         # Billing management
│   │   ├── pricing/         # Pricing plans
│   │   ├── usage/           # Usage statistics
│   │   ├── settings/        # Account settings
│   │   └── developer/       # Developer tools
│   └── embed/               # Embeddable chatbot page
│
├── components/
│   ├── ui/                  # shadcn/ui components
│   ├── dashboard/           # Dashboard-specific components
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── CrawlSourcePanel.tsx
│   │   ├── CrawlScheduleModal.tsx
│   │   ├── QABundlePanel.tsx
│   │   └── ChatbotTeamSettings.tsx
│   └── chatbot/
│       └── WidgetPreview.tsx
│
├── contexts/
│   └── AuthContext.tsx      # Authentication context
│
├── lib/
│   ├── api.ts               # API client utilities
│   ├── auth.ts              # Auth helpers
│   └── utils.ts             # General utilities
│
├── middleware.ts            # Auth middleware
└── instrumentation.ts       # Sentry instrumentation
```

### Key Pages

| Path                              | Component             | Purpose                                                           |
| --------------------------------- | --------------------- | ----------------------------------------------------------------- |
| `/dashboard/chatbots/[chatbotId]` | page.tsx (3988 lines) | Main chatbot editor with tabs for knowledge, appearance, settings |
| `/dashboard/analytics`            | page.tsx              | Usage analytics and charts                                        |
| `/dashboard/pricing`              | page.tsx              | Subscription plan selection                                       |
| `/dashboard/settings/team`        | page.tsx              | Team member management                                            |

---

## Embeddable Widget (`apps/widget/`)

### Structure

```
apps/widget/
├── src/
│   ├── index.tsx            # Widget entry point and main component
│   ├── styles.css           # Widget styles
│   ├── styles.ts            # CSS-in-JS styles
│   └── widget.css           # Additional styles
│
├── index.html               # Development HTML
├── vite.config.ts           # Vite build config
├── server.js                # Production server
├── nginx.conf               # Production nginx config
└── Dockerfile               # Container build
```

### Widget Features

- Preact-based for minimal bundle size (~30KB)
- Floating chat bubble with expand/collapse
- Real-time streaming message display
- Markdown rendering support
- Customizable appearance via API

---

## Shared Packages (`packages/`)

```
packages/
├── chatbot-widget/          # Widget as npm package
│   └── src/
├── shared/                  # Shared utilities
│   └── src/
└── ui/                      # Shared UI components
    └── src/
```

---

## Database Schema (Key Tables)

| Table                 | Purpose                      |
| --------------------- | ---------------------------- |
| `users`               | User accounts                |
| `tenants`             | Organizations                |
| `chatbots`            | Chatbot instances            |
| `chatbot_appearances` | Widget styling               |
| `chatbot_permissions` | Team access control          |
| `knowledge_sources`   | Crawled URLs, files, Q&A     |
| `crawled_pages`       | Individual crawled pages     |
| `embeddings`          | Vector embeddings (pgvector) |
| `uploaded_files`      | File uploads                 |
| `qa_pairs`            | Q&A knowledge pairs          |
| `chat_sessions`       | Conversation sessions        |
| `chat_messages`       | Individual messages          |
| `subscriptions`       | Billing subscriptions        |
| `crawl_schedules`     | Scheduled re-crawls          |
| `crawl_histories`     | Crawl run history            |

---

## Docker Services

| Service    | Image                  | Port | Purpose                      |
| ---------- | ---------------------- | ---- | ---------------------------- |
| `postgres` | pgvector/pgvector:pg16 | 5432 | Database with vector support |
| `redis`    | redis:7-alpine         | 6379 | Caching and rate limiting    |
| `api`      | Custom (Python 3.11)   | 8000 | FastAPI backend              |
| `web`      | Custom (Node 20)       | 3000 | Next.js dashboard            |
| `widget`   | Custom (Node 20)       | 3001 | Preact widget                |

---

## Key Integrations

| Integration         | Purpose                 | Config Variable         |
| ------------------- | ----------------------- | ----------------------- |
| Google Gemini       | LLM for chat responses  | `GEMINI_API_KEY`        |
| HuggingFace         | Text embeddings         | `HUGGINGFACE_API_TOKEN` |
| Sentry              | Error tracking          | `SENTRY_DSN`            |
| SMTP                | Email notifications     | `SMTP_*`                |
| Redis               | Caching, rate limiting  | `REDIS_URL`             |
| PostgreSQL/pgvector | Database, vector search | `DATABASE_URL`          |
