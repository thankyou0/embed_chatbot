# Setup Guide

## Prerequisites

- Node.js 18+ and pnpm 8+
- Python 3.11+
- Docker & Docker Compose

## Initial Setup

### 1. Install pnpm (if not already installed)

```bash
npm install -g pnpm
```

### 2. Install Dependencies

```bash
# Install all workspace dependencies
pnpm install
```

### 3. Set Up Environment Variables

Create `.env` files in the root and each app directory:

**Root `.env`** (or copy from root):
```env
DATABASE_URL=postgresql+asyncpg://postgres:post@localhost:5432/embed_chatbot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=post
POSTGRES_DB=embed_chatbot
API_PORT=8000
API_HOST=0.0.0.0
SECRET_KEY=your-secret-key-change-in-production
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**apps/api/.env**:
```env
DATABASE_URL=postgresql+asyncpg://postgres:post@localhost:5432/embed_chatbot
API_PORT=8000
API_HOST=0.0.0.0
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```

**apps/web/.env.local**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Start PostgreSQL

```bash
docker-compose up -d
```

Wait a few seconds for PostgreSQL to be ready.

### 5. Set Up Python Environment (API)

```bash
cd apps/api
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 6. Run Database Migrations

```bash
cd apps/api
alembic upgrade head
```

### 7. Start Development Servers

From the root directory:

```bash
pnpm dev
```

This will start:
- Next.js dashboard at http://localhost:3000
- FastAPI at http://localhost:8000

Or start individually:

```bash
# Terminal 1 - API
cd apps/api
python run.py

# Terminal 2 - Web Dashboard
cd apps/web
pnpm dev

# Terminal 3 - Widget (optional)
cd apps/widget
pnpm dev
```

## Project Structure

```
.
├── apps/
│   ├── api/          # FastAPI backend
│   ├── web/          # Next.js dashboard
│   └── widget/       # Preact embeddable widget
├── packages/
│   ├── shared/       # Shared TypeScript types/utils
│   └── ui/           # Shared UI components
└── docker-compose.yml
```

## Next Steps

- Implement authentication
- Add chat functionality
- Set up vector embeddings with pgvector
- Configure widget deployment
