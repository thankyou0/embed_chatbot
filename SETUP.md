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

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:post@localhost:5432/embed_chatbot

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=150
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Origins (JSON array format)
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# LLM API Keys
GROQ_API_KEY=your-groq-api-key
```

**Optional: Frontend environment files**

For Next.js frontend (apps/web/.env.local):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For Widget (apps/widget/.env):
```env
VITE_PUBLIC_API_URL=http://localhost:8000
```

### 4. Start PostgreSQL

```bash
docker-compose up -d
```

Wait a few seconds for PostgreSQL to be ready.

### 5. Set Up Python Environment (API)

```bash
# From project root
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install dependencies from root requirements.txt
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
embed_chatbot/
├── .env                  # Shared environment configuration
├── .env.example          # Environment template
├── requirements.txt      # Consolidated Python dependencies
├── docker-compose.yml    # PostgreSQL + pgvector
├── apps/
│   ├── api/              # FastAPI backend
│   ├── web/              # Next.js dashboard
│   └── widget/           # Preact embeddable widget
├── packages/
│   ├── shared/           # Shared TypeScript types/utils
│   └── ui/               # Shared UI components
```

## Development URLs

- Web dashboard: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
