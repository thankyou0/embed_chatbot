# Embeddable AI Chatbot SaaS

A monorepo for an embeddable AI chatbot SaaS platform.

## 📚 Documentation

**NEW! Want to understand the complete codebase?**
- **[CODE_EXPLANATION.md](./CODE_EXPLANATION.md)** - Comprehensive guide explaining the entire codebase from architecture to implementation
  - Complete architecture overview
  - Detailed explanation of backend, frontend, and widget
  - Data flow diagrams and request lifecycle
  - Key features implementation
  - Perfect starting point for understanding the code!

## Structure

```
embed_chatbot/
├── .env                  # Shared environment configuration
├── .env.example          # Environment template
├── requirements.txt      # Consolidated Python dependencies
├── docker-compose.yml    # Local development
├── docker-compose.prod.yml # Production deployment
├── apps/
│   ├── api/              # FastAPI backend
│   ├── web/              # Next.js 14 tenant dashboard
│   └── widget/           # Preact embeddable chat widget
├── packages/
│   ├── shared/           # Shared TypeScript types and utilities
│   └── ui/               # Shared UI components
```

## Tech Stack

- **Frontend**: Next.js 14 (App Router), Tailwind CSS, shadcn/ui
- **Widget**: Preact (<50KB gzipped)
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with pgvector extension
- **ORM**: SQLAlchemy 2.0 (async)

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm 8+
- Python 3.11+
- Docker & Docker Compose

### Option 1: Docker (Recommended)

Run everything with Docker:

```bash
# Copy environment file
cp .env.example .env

# Start all services (database + API + web + widget)
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head
```

### Option 2: Local Development

1. Install dependencies:
   ```bash
   pnpm install
   pip install -r requirements.txt
   ```

2. Start PostgreSQL only:
   ```bash
   docker-compose up -d postgres
   ```

3. Copy and configure environment variables:
   ```bash
   cp .env.example .env
   ```

4. Run database migrations:
   ```bash
   cd apps/api
   alembic upgrade head
   ```

5. Start development servers:
   ```bash
   pnpm dev
   ```

## Docker Commands

```bash
# Local Development (with hot reload)
docker-compose up -d              # Start all services
docker-compose down               # Stop all services
docker-compose logs -f api        # View API logs
docker-compose exec api alembic upgrade head  # Run migrations

# Production Deployment
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml down
```

## Development URLs

- Web dashboard: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Widget: http://localhost:3001

## Environment Configuration

All environment variables are centralized in the root `.env` file. See `.env.example` for available options.

For frontend-specific variables:
- Next.js: Create `apps/web/.env.local` for `NEXT_PUBLIC_*` variables
- Widget: Create `apps/widget/.env` for `VITE_*` variables
