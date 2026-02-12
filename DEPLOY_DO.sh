#!/bin/bash
# Deploy to DigitalOcean - Complete Guide

# This guide walks through deploying the embed_chatbot application to DigitalOcean
# Using Docker Compose for multi-container orchestration

# ==============================================================================
# STEP 1: Prerequisites
# ==============================================================================
# - DigitalOcean account
# - SSH access to your Droplet
# - Docker and Docker Compose installed on Droplet
# - Domain name configured (optional but recommended)

# ==============================================================================
# STEP 2: Clone Repository and Setup
# ==============================================================================

# SSH into your DigitalOcean Droplet
# ssh root@your_droplet_ip

# Clone repository
git clone https://github.com/yourusername/embed_chatbot.git
cd embed_chatbot

# ==============================================================================
# STEP 3: Configure Environment
# ==============================================================================

# Copy environment template
cp .env.example .env

# Edit with your settings
nano .env

# ===== REQUIRED VARIABLES TO SET =====
# DATABASE_URL=postgresql://postgres:YOUR_SECURE_PASSWORD@postgres:5432/embed_chatbot
# POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD
# SECRET_KEY=generate-a-random-secure-key
# API_URL=https://your-api-domain.com
# WEB_URL=https://your-web-domain.com
# GROQ_API_KEY=your_groq_api_key (for LLM)

# ==============================================================================
# STEP 4: Start Services with Docker Compose
# ==============================================================================

# Build images (first time only, or after code changes)
docker-compose -f docker-compose.prod.yml build

# Start all services (database, API, web, widget)
docker-compose -f docker-compose.prod.yml up -d

# Verify all services are running
docker-compose -f docker-compose.prod.yml ps

# ==============================================================================
# STEP 5: Verify Database Migrations
# ==============================================================================

# Check API logs to verify migrations ran successfully
docker-compose -f docker-compose.prod.yml logs api

# Should see output like:
# api      | INFO: Alembic migration starting...
# api      | INFO: Database migration completed successfully

# Optionally connect to database and verify tables
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d embed_chatbot -c "\dt"

# ==============================================================================
# STEP 6: Setup Reverse Proxy with Nginx (Optional but Recommended)
# ==============================================================================

# Install Nginx
apt-get update
apt-get install -y nginx

# Create Nginx config
cat > /etc/nginx/sites-available/default << 'EOF'
# API Upstream
upstream api {
    server api:8000;
}

# Web Upstream
upstream web {
    server web:3000;
}

# Widget Upstream
upstream widget {
    server widget:80;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# HTTPS API Server
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/your-cert.crt;
    ssl_certificate_key /etc/ssl/private/your-key.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # SSE support for chat streaming
    location /chat {
        proxy_pass http://api;
        proxy_buffering off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTPS Web Server
server {
    listen 443 ssl http2;
    server_name app.yourdomain.com;

    ssl_certificate /etc/ssl/certs/your-cert.crt;
    ssl_certificate_key /etc/ssl/private/your-key.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://web;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTPS Widget Server
server {
    listen 443 ssl http2;
    server_name widget.yourdomain.com;

    ssl_certificate /etc/ssl/certs/your-cert.crt;
    ssl_certificate_key /etc/ssl/private/your-key.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://widget;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Restart Nginx
systemctl restart nginx

# ==============================================================================
# STEP 7: Setup SSL Certificates (Let's Encrypt)
# ==============================================================================

# Install Certbot
apt-get install -y certbot python3-certbot-nginx

# Generate certificates
certbot certonly --standalone \
    -d api.yourdomain.com \
    -d app.yourdomain.com \
    -d widget.yourdomain.com

# Auto-renewal is configured automatically

# ==============================================================================
# STEP 8: Database Backup Setup
# ==============================================================================

# Create backup script
cat > /root/backup_database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker-compose -f /root/embed_chatbot/docker-compose.prod.yml exec -T postgres \
    pg_dump -U postgres embed_chatbot | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /root/backup_database.sh

# Add to crontab for daily backups
echo "0 2 * * * /root/backup_database.sh" | crontab -

# ==============================================================================
# STEP 9: Monitoring and Logs
# ==============================================================================

# View real-time logs
docker-compose -f docker-compose.prod.yml logs -f

# View logs for specific service
docker-compose -f docker-compose.prod.yml logs -f api

# Monitor resource usage
docker stats

# ==============================================================================
# STEP 10: Health Checks
# ==============================================================================

# Check API health
curl https://api.yourdomain.com/health

# Check web app
curl https://app.yourdomain.com

# Check widget
curl https://widget.yourdomain.com/widget.umd.js

# Check database
docker-compose -f docker-compose.prod.yml exec postgres psql -U postgres -d embed_chatbot -c "SELECT NOW();"

# ==============================================================================
# STEP 11: Troubleshooting
# ==============================================================================

# If services fail to start:
docker-compose -f docker-compose.prod.yml logs

# If database connection fails:
# 1. Verify DATABASE_URL in .env
# 2. Check POSTGRES_PASSWORD matches
# 3. Ensure postgres container is running: docker-compose -f docker-compose.prod.yml ps

# If migrations fail:
# 1. Check database is accessible
# 2. Check .env DATABASE_URL is correct
# 3. View API logs: docker-compose -f docker-compose.prod.yml logs api

# ==============================================================================
# STEP 12: Production Checklist
# ==============================================================================

# Before going live, verify:
# [ ] All environment variables set in .env
# [ ] SSL certificates installed and working
# [ ] Database backups configured
# [ ] Firewall configured (open ports 80, 443)
# [ ] DNS records configured
# [ ] Monitoring setup (optional)
# [ ] Logging configured
# [ ] Team notified and tested
# [ ] Support documentation ready

# ==============================================================================
# STEP 13: Scaling Considerations
# ==============================================================================

# If you need more capacity:

# 1. Scale API workers:
# Edit docker-compose.prod.yml - increase replicas in api service

# 2. Increase database connections:
# Edit .env - DATABASE_POOL_SIZE

# 3. Add caching layer (optional):
# Add Redis to docker-compose.prod.yml for session/cache storage

# 4. Setup load balancing:
# Use DigitalOcean Load Balancer pointing to multiple droplets

# ==============================================================================
# COMMON COMMANDS FOR MANAGEMENT
# ==============================================================================

# Stop all services gracefully
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose -f docker-compose.prod.yml down -v

# Restart a service
docker-compose -f docker-compose.prod.yml restart api

# View service status
docker-compose -f docker-compose.prod.yml ps

# Update images and restart
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Execute command in container
docker-compose -f docker-compose.prod.yml exec api python -c "print('test')"

# Access container shell
docker-compose -f docker-compose.prod.yml exec api bash

# ==============================================================================
# SUPPORT & UPDATES
# ==============================================================================

# To update code:
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# To view new releases/changelogs:
git log --oneline

# For issues:
# Check CLEANUP_SUMMARY.md and DEPLOYMENT_CHECKLIST.md in project root
