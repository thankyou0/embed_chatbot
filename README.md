# Embed Chatbot

A fully embeddable AI chatbot SaaS platform with multi-tenant support, real-time streaming responses, and comprehensive knowledge management.

## Features

### Core Capabilities

- **AI-Powered Chat**: HTTP streaming responses using Google Gemini models with RAG (Retrieval Augmented Generation)
- **Multi-tenant Architecture**: Organization-based isolation with role-based access control
- **Embeddable Widget**: Lightweight Preact widget for embedding on any website
- **Knowledge Management**:
  - Website crawling with intelligent content extraction
  - File uploads (PDF, DOCX, TXT, CSV, XML, etc.)
  - Q&A pair management
  - Product detection and structured metadata extraction

### Advanced Features

- **Smart Crawler**: DFS-based crawling with JS-heavy site detection, automatic sitemap discovery, and quota management
- **Vector Search**: PostgreSQL with pgvector for semantic similarity search
- **Subscription Tiers**: Free, Pro, and Enterprise plans with page/message quotas
- **Team Collaboration**: Invite team members with granular permissions (owner/admin/editor/viewer)
- **Scheduled Crawls**: Automatic re-sync with daily/weekly/monthly options
- **Stop Crawl**: Cancel crawls mid-progress while preserving already crawled pages
- **Analytics**: Usage tracking, conversation history, and performance metrics
- **Rate Limiting**: Redis-based rate limiting and caching

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Docker Compose Stack                           │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Web UI    │  │   Widget    │  │   FastAPI   │  │  PostgreSQL │    │
│  │  (Next.js)  │  │  (Preact)   │  │   Backend   │  │  (pgvector) │    │
│  │  Port 3000  │  │  Port 3001  │  │  Port 8000  │  │  Port 5432  │    │
│  └─────────────┘  └─────────────┘  └──────┬──────┘  └─────────────┘    │
│                                           │                              │
│                                    ┌──────┴──────┐                      │
│                                    │    Redis    │                      │
│                                    │  Port 6379  │                      │
│                                    └─────────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Google Gemini API key
- HuggingFace API token (for embeddings)

### 1. Clone and Configure

```bash
git clone https://github.com/thankyou0/embed_chatbot.git
cd embed_chatbot
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/chatbot_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
HUGGINGFACE_API_TOKEN=your-hf-token

# Optional
SENTRY_DSN=your-sentry-dsn
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Start the Stack

```bash
docker-compose up -d
```

Services will be available at:

- **Web Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Chatbot Widget**: http://localhost:3001

### 3. Create Your First Chatbot

1. Sign up at http://localhost:3000/signup
2. Create a new chatbot from the dashboard
3. Add knowledge sources (URL, files, or Q&A pairs)
4. Copy the embed code and add it to your website

## Embedding the Widget

```html
<script>
  window.chatbotConfig = {
    chatbotId: "your-chatbot-id",
    apiUrl: "https://your-api-domain.com",
  };
</script>
<script src="https://your-widget-domain.com/widget.js"></script>
```

## Project Structure

```
embed_chatbot/
├── apps/
│   ├── api/                 # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/v1/      # API routes
│   │   │   ├── core/        # Config, security, database
│   │   │   ├── models/      # SQLAlchemy models
│   │   │   ├── schemas/     # Pydantic schemas
│   │   │   └── services/    # Business logic
│   │   ├── alembic/         # Database migrations
│   │   └── Dockerfile
│   │
│   ├── web/                 # Next.js dashboard
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   └── Dockerfile
│   │
│   └── widget/              # Preact embeddable widget
│       ├── src/
│       └── Dockerfile
│
├── packages/                # Shared monorepo packages
├── docker-compose.yml       # Development stack
└── docker-compose.prod.yml  # Production stack
```

## Key Services

### Crawler Service

- Intelligent website crawling with content extraction via Trafilatura
- JS-heavy site detection with graceful fallback options
- Automatic sitemap.xml discovery and parsing
- Page quota enforcement per subscription tier
- Cooperative cancellation support (stop crawl mid-progress)

### Embedding Service

- HuggingFace API integration for text embeddings
- Batch processing with automatic retries
- PostgreSQL pgvector storage with HNSW indexing

### Chat Service

- Google Gemini integration with streaming responses
- RAG-based context retrieval from knowledge base
- Conversation history tracking
- Vision support for image-based queries

### Billing Service

- Subscription tier management (Free/Pro/Enterprise)
- Usage tracking (pages crawled, messages sent)
- Quota enforcement and overage handling

## API Endpoints

| Endpoint                                       | Method   | Description                   |
| ---------------------------------------------- | -------- | ----------------------------- |
| `/api/v1/auth/signup`                          | POST     | User registration             |
| `/api/v1/auth/login`                           | POST     | User authentication           |
| `/api/v1/chatbots`                             | GET/POST | List/create chatbots          |
| `/api/v1/chatbots/{id}/crawl`                  | POST     | Start website crawl           |
| `/api/v1/chatbots/knowledge-sources/{id}/stop` | POST     | Stop active crawl             |
| `/api/v1/chat/{chatbot_id}/message`            | POST     | Send chat message (streaming) |
| `/api/v1/members`                              | GET/POST | Team member management        |
| `/api/v1/usage`                                | GET      | Usage statistics              |

Full API documentation available at `/docs` when running.

## Environment Variables

| Variable                | Required | Description                            |
| ----------------------- | -------- | -------------------------------------- |
| `DATABASE_URL`          | Yes      | PostgreSQL connection string           |
| `REDIS_URL`             | Yes      | Redis connection string                |
| `SECRET_KEY`            | Yes      | JWT signing key                        |
| `GEMINI_API_KEY`        | Yes      | Google Gemini API key                  |
| `HUGGINGFACE_API_TOKEN` | Yes      | HuggingFace embeddings token           |
| `SENTRY_DSN`            | No       | Sentry error tracking                  |
| `SMTP_*`                | No       | Email configuration for password reset |

## Database Migrations

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"
```

## Development

### Local API Development

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Local Web Development

```bash
cd apps/web
pnpm install
pnpm dev
```

### Local Widget Development

```bash
cd apps/widget
pnpm install
pnpm dev
```

## Production Deployment

Use `docker-compose.prod.yml` for production:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Key differences from development:

- Multi-stage builds for smaller images
- Production-optimized Node.js builds
- Gunicorn with Uvicorn workers for API
- Health checks enabled
- No volume mounts for source code

## Subscription Tiers

| Feature          | Free | Pro   | Enterprise |
| ---------------- | ---- | ----- | ---------- |
| Chatbots         | 1    | 5     | Unlimited  |
| Pages/Month      | 50   | 500   | 10,000     |
| Messages/Month   | 100  | 5,000 | Unlimited  |
| Team Members     | 1    | 10    | Unlimited  |
| File Uploads     | 5MB  | 50MB  | 500MB      |
| Scheduled Crawls | ❌   | ✅    | ✅         |
| Custom Branding  | ❌   | ✅    | ✅         |
| Priority Support | ❌   | ❌    | ✅         |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
