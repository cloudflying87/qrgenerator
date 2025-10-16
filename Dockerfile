# Multi-stage build for production optimization
FROM python:3.13.1-slim as builder

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /build
COPY requirements/ requirements/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt

# Production stage
FROM python:3.13.1-slim

# Security: Create non-root user early
RUN groupadd -r app && \
    useradd -r -g app -d /app -s /bin/bash -c "App user" app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.local/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    netcat-traditional \
    curl \
    gettext \
    gosu \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create app directory with proper structure
WORKDIR /app
RUN mkdir -p /app/{staticfiles,media,logs,persistent_media} && \
    chmod 755 /app/{staticfiles,media,logs,persistent_media} && \
    chown -R app:app /app

# Copy application code
COPY --chown=app:app . /app/

# Copy and set permissions for entrypoint
COPY --chown=root:root ./docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Note: We stay as root for entrypoint, then switch to app user via gosu
# This allows fixing volume permissions at runtime

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--worker-class", "gevent", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "100", "--timeout", "30", "--keep-alive", "5"]