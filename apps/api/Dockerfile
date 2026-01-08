# ============================================
# FastAPI Backend Dockerfile
# Supports both local development and production
# ============================================

# ---- Base Stage ----
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Dependencies Stage ----
FROM base as dependencies

# Copy requirements from project root
# apps/api/requirements.txt references ../../requirements.txt, so we copy root requirements.txt
# and place it where the relative path will resolve correctly
COPY requirements.txt /app/requirements.txt

# Install Python dependencies directly from root requirements.txt
# (apps/api/requirements.txt just references it anyway)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# ---- Development Stage ----
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir watchfiles

# Copy application code
COPY apps/api /app

# Note: .env file is mounted via docker-compose volumes, not copied here

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with hot reload for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---- Production Stage ----
FROM dependencies as production

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy application code
COPY apps/api /app

# Create uploads directory
RUN mkdir -p /app/uploads && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with production settings (multiple workers)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
