# Embeddable AI Chatbot SaaS

A monorepo for an embeddable AI chatbot SaaS platform.

## Structure

- `/apps/web` - Next.js 14 tenant dashboard
- `/apps/widget` - Preact embeddable chat widget
- `/apps/api` - FastAPI backend
- `/packages/shared` - Shared TypeScript types and utilities
- `/packages/ui` - Shared UI components

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

### Setup

1. Install dependencies:
   ```bash
   pnpm install
   ```

2. Start PostgreSQL:
   ```bash
   docker-compose up -d
   ```

3. Copy environment variables:
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

## Development

- Web dashboard: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

