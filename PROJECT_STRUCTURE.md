# Project Structure

> **💡 New to this codebase?** Check out [CODE_EXPLANATION.md](./CODE_EXPLANATION.md) for a comprehensive guide explaining the entire architecture, data flow, and implementation details!

```
embed_chatbot/
├── .env                        # Shared environment configuration
├── .env.example                # Environment template for new developers
├── requirements.txt            # Consolidated Python dependencies
├── docker-compose.yml          # PostgreSQL + pgvector
├── package.json                # Root workspace config
├── pnpm-workspace.yaml         # pnpm workspace
│
├── apps/
│   ├── api/                    # FastAPI Backend
│   │   ├── alembic/            # Database migrations
│   │   │   ├── versions/       # Migration files
│   │   │   ├── env.py          # Alembic environment
│   │   │   └── script.py.mako  # Migration template
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── v1/         # API v1 routes
│   │   │   ├── core/           # Core configuration
│   │   │   │   ├── config.py   # Settings (loads from root .env)
│   │   │   │   ├── database.py # Database connection
│   │   │   │   ├── security.py # JWT authentication
│   │   │   │   └── dependencies.py
│   │   │   ├── models/         # SQLAlchemy models
│   │   │   ├── schemas/        # Pydantic schemas
│   │   │   └── services/       # Business logic
│   │   ├── main.py             # FastAPI app entry
│   │   ├── run.py              # Development server
│   │   ├── requirements.txt    # References root requirements.txt
│   │   └── alembic.ini         # Alembic config
│   │
│   ├── web/                    # Next.js 14 Dashboard
│   │   ├── app/                # App Router
│   │   │   ├── layout.tsx      # Root layout
│   │   │   ├── page.tsx        # Home page
│   │   │   ├── dashboard/      # Dashboard pages
│   │   │   ├── chatbots/       # Chatbot management
│   │   │   └── settings/       # Settings pages
│   │   ├── components/         # React components
│   │   ├── contexts/           # React context providers
│   │   ├── lib/                # Utilities
│   │   ├── .env.local          # Frontend-specific env (NEXT_PUBLIC_*)
│   │   ├── package.json
│   │   ├── next.config.js
│   │   ├── tailwind.config.ts
│   │   └── tsconfig.json
│   │
│   └── widget/                 # Preact Embeddable Widget
│       ├── src/
│       │   ├── components/
│       │   ├── index.tsx       # Widget entry point
│       │   └── styles.css
│       ├── .env                # Widget-specific env (VITE_*)
│       ├── index.html
│       ├── vite.config.ts      # Vite build config
│       └── package.json
│
├── packages/
│   ├── shared/                 # Shared TypeScript
│   │   ├── src/
│   │   │   └── index.ts        # Types & utilities
│   │   └── package.json
│   │
│   └── ui/                     # Shared UI Components
│       ├── src/
│       │   ├── components/
│       │   │   ├── Button.tsx
│       │   │   └── Card.tsx
│       │   └── index.ts
│       └── package.json
│
├── .gitignore
├── README.md
├── SETUP.md                    # Setup instructions
└── PROJECT_STRUCTURE.md        # This file
```

## Key Features

### Backend (FastAPI)
- Async SQLAlchemy 2.0
- Alembic migrations (17 versions)
- JWT authentication with refresh tokens
- Multi-tenant architecture
- Vector embeddings with pgvector
- Document processing (PDF, DOCX, XLSX)
- Web crawling for knowledge ingestion
- Background job scheduling (APScheduler)

### Frontend (Next.js)
- Next.js 14 with App Router
- Tailwind CSS configured
- TypeScript support
- shadcn/ui components
- Authentication flows

### Widget (Preact)
- Preact for minimal bundle size (<50KB gzipped)
- Vite build configuration
- Customizable appearance
- Auto-initialization support

### Shared Packages
- TypeScript types and utilities
- Reusable UI components

## Database Schema

Key tables:
- `tenants` - Organizations/workspaces
- `users` - User accounts with roles
- `chatbots` - AI chatbot configurations
- `chatbot_appearance` - UI customization
- `knowledge_sources` - Training data
- `embeddings` - Vector embeddings
- `chat_history` - Conversation logs

## Environment Configuration

All environment variables are centralized in the root `.env` file:

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL connection string |
| SECRET_KEY | JWT signing key |
| CORS_ORIGINS | Allowed CORS origins (JSON array) |
| GROQ_API_KEY | LLM API key |

Frontend apps may have their own env files for public variables:
- `apps/web/.env.local` - NEXT_PUBLIC_* variables
- `apps/widget/.env` - VITE_* variables
