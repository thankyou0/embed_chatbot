# ============================================
# FastAPI Backend Dockerfile
# Lightweight build - uses HuggingFace API for embeddings
# No heavy PyTorch/sentence-transformers!
# ============================================

# ---- Base Stage ----
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies (no cache to save space)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# ---- Dependencies Stage ----
FROM base AS dependencies

# Copy requirements (using root requirements.txt)
COPY requirements.txt /app/requirements.txt

# Install Python dependencies WITHOUT cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    rm -rf /root/.cache /tmp/*

# ---- Development Stage ----
FROM dependencies AS development

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
# Restrict watcher to /app/app to avoid memory issues with watching root /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "app", "--reload-include", "*.py"]

# ---- Production Stage ----
FROM dependencies AS production

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
