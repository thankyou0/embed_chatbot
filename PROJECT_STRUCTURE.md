# Project Structure

```
e_com_Chatbot/
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
│   │   │   │   ├── config.py   # Settings
│   │   │   │   └── database.py # Database connection
│   │   │   └── models/         # SQLAlchemy models
│   │   │       ├── tenant.py
│   │   │       └── user.py
│   │   ├── main.py             # FastAPI app entry
│   │   ├── run.py              # Development server
│   │   ├── requirements.txt    # Python dependencies
│   │   └── alembic.ini         # Alembic config
│   │
│   ├── web/                    # Next.js 14 Dashboard
│   │   ├── app/                # App Router
│   │   │   ├── layout.tsx      # Root layout
│   │   │   ├── page.tsx        # Home page
│   │   │   └── globals.css     # Global styles
│   │   ├── package.json
│   │   ├── next.config.js
│   │   ├── tailwind.config.ts  # Tailwind config
│   │   └── tsconfig.json
│   │
│   └── widget/                 # Preact Embeddable Widget
│       ├── src/
│       │   ├── components/
│       │   │   └── ChatbotWidget.tsx
│       │   ├── index.tsx       # Widget entry point
│       │   └── styles.css
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
├── docker-compose.yml          # PostgreSQL + pgvector
├── package.json                # Root workspace config
├── pnpm-workspace.yaml         # pnpm workspace
├── .gitignore
├── README.md
└── SETUP.md                    # Setup instructions
```

## Key Features

### Backend (FastAPI)
- ✅ Async SQLAlchemy 2.0
- ✅ Alembic migrations
- ✅ Database models: `tenants`, `users`
- ✅ Health check endpoint
- ✅ CORS configured

### Frontend (Next.js)
- ✅ Next.js 14 with App Router
- ✅ Tailwind CSS configured
- ✅ TypeScript support
- ✅ Ready for shadcn/ui integration

### Widget (Preact)
- ✅ Preact for minimal bundle size
- ✅ Vite build configuration
- ✅ Auto-initialization support
- ✅ Customizable theme

### Shared Packages
- ✅ TypeScript types and utilities
- ✅ Reusable UI components

## Database Schema

### tenants
- `id` (Integer, PK)
- `name` (String)
- `email` (String, unique)
- `created_at` (DateTime)

### users
- `id` (Integer, PK)
- `tenant_id` (Integer, FK → tenants.id)
- `email` (String, unique)
- `password_hash` (String)
- `role` (Enum: ADMIN, USER)
- `created_at` (DateTime)

