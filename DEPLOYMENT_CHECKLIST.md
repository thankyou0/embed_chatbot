# Deployment Checklist for DigitalOcean

## ✅ Pre-Deployment Verification (Completed)

### Database Migrations
- [x] All migrations verified and properly linked
- [x] Migration chain: 001 → ... → 024 (latest)
- [x] Billing/Subscription migrations included (022-024)
- [x] Permission migrations included (002, 013, 2ce1fa, 8ddec7)
- [x] Migration environment configured to load .env from `/app/.env` (Docker)

### Backend Integration
- [x] BillingService integrated and used in ChatbotService, ChatService, UsageService
- [x] Permission system fully integrated
- [x] Analytics counting fixed (preview sessions excluded)
- [x] Welcome message sync implemented in update_appearance

### Frontend Integration
- [x] Analytics dashboard functional
- [x] Usage/Billing pages functional
- [x] Team permissions UI cleaned up (shows role only)
- [x] Widget properly displays welcome messages

### Docker Configuration
- [x] docker-compose.yml (development) - verified
- [x] docker-compose.prod.yml (production) - verified
- [x] Dockerfiles - NOT modified (as requested)
- [x] Environment variables properly configured

---

## 🚀 Deployment Steps for DigitalOcean

### 1. Environment Setup
```bash
# Copy env template
cp .env.example .env

# Configure production variables in .env:
DATABASE_URL=postgresql://user:password@postgres:5432/embed_chatbot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=embed_chatbot
SECRET_KEY=your_production_secret_key
API_URL=https://your-api-domain.com
WEB_URL=https://your-web-domain.com
```

### 2. Deploy with Docker Compose
```bash
# Pull latest images and start services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Verify services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs for any errors
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Database Migrations
Migrations run automatically on API startup via alembic in `app/main.py`.

Verify migration ran:
```bash
# Check API logs
docker-compose -f docker-compose.prod.yml logs api

# Should see: "Database migration completed successfully"
```

### 4. Verify Database Connection
```bash
# Connect to database
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d embed_chatbot

# Check tables exist
\dt

# Exit
\q
```

### 5. Health Check
```bash
# Check API health
curl https://your-api-domain.com/health

# Check web app
curl https://your-web-domain.com

# Check widget endpoint
curl https://your-widget-domain.com/widget.umd.js
```

---

## 📋 Files Removed for Cleanup

The following development/documentation files have been removed:
- `error.txt` - Issue tracking
- `feat.impr.txt` - Feature ideas
- `improvements.txt` - Improvement suggestions
- `PERMISSION_AUDIT.md` - Permission documentation
- `PROJECT_STRUCTURE.md` - Project structure documentation
- `PRODUCTION_IMPROVEMENTS_REPORT.md` - Production suggestions
- `prompts.md` - LLM prompt examples

**Retained**: README.md (user-facing documentation)

---

## 🔒 Security Checklist

- [ ] Environment variables set securely (not in git)
- [ ] Database password changed from default
- [ ] SECRET_KEY changed from default
- [ ] CORS configured for your domains (not "*" in production)
- [ ] SSL/TLS certificates installed
- [ ] Database backups configured
- [ ] Regular security updates scheduled

---

## 📊 System Architecture Verified

### Backend (FastAPI)
- JWT authentication working
- Billing service active
- Permission system active
- Analytics tracking (excluding previews)
- Database connection pooling configured

### Frontend (Next.js)
- Authentication context working
- API integration verified
- Dashboard fully functional
- Team management working

### Widget (Preact)
- Embeddable script loading correctly
- Welcome message displays from chatbot.welcome_message
- Analytics tracking sending data

### Database (PostgreSQL + pgvector)
- All 24 migrations applied in sequence
- Foreign key constraints in place
- Indexes created for performance
- pgvector extension loaded

---

## 🐛 Monitoring After Deployment

Monitor these metrics:
1. API response times (should be < 500ms)
2. Database query performance
3. Memory usage
4. Message count growth (should only count non-preview)
5. Widget script loading times

---

## ✨ Known Working Features

✅ User authentication and tenant isolation
✅ Chatbot creation and management
✅ Knowledge base upload and crawling
✅ Vector embeddings and RAG
✅ Chat streaming with SSE
✅ Analytics dashboard
✅ Team member management with granular permissions
✅ Subscription/Billing tracking
✅ Embeddable widget with custom styling
✅ Preview mode (doesn't count in analytics)

---

## 📞 Support

For issues during deployment:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Verify DATABASE_URL is correct
3. Ensure port 5432 is accessible for database
4. Check .env file has all required variables

---

Generated: 2026-02-04
Last Updated: After cleanup and verification
