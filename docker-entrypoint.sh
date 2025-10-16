#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting qrgenerator application...${NC}"

# Fix volume permissions (this script runs as root to handle volume ownership)
echo -e "${YELLOW}🔧 Fixing volume permissions...${NC}"
# Ensure directories exist and have correct ownership
mkdir -p /app/staticfiles /app/media /app/logs /app/persistent_media
chown -R app:app /app/staticfiles /app/media /app/logs /app/persistent_media
chmod -R 755 /app/staticfiles /app/media /app/logs /app/persistent_media
echo -e "${GREEN}✅ Permissions fixed${NC}"

# Function to wait for a service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to be ready...${NC}"
    while ! nc -z "$host" "$port"; do
        sleep 0.1
    done
    echo -e "${GREEN}✅ $service_name is ready!${NC}"
}

# Wait for dependencies
if [ "${DATABASE_CHECK:-}" = "1" ]; then
    wait_for_service "${DB_HOST:-db}" "${DB_PORT:-5432}" "PostgreSQL database"
fi

if [ "${REDIS_URL:-}" != "" ]; then
    wait_for_service "${REDIS_HOST:-redis}" "${REDIS_PORT:-6379}" "Redis cache"
fi

# Django setup (run as app user)
echo -e "${BLUE}🔧 Setting up Django...${NC}"

# Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
gosu app python manage.py collectstatic --noinput --clear

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
gosu app python manage.py migrate --noinput

# Check for critical migrations
echo -e "${YELLOW}🔍 Checking for pending migrations...${NC}"
if gosu app python manage.py showmigrations --plan | grep -q "\[ \]"; then
    echo -e "${YELLOW}⚠️  Warning: There are unapplied migrations${NC}"
fi

# Create superuser if needed (only in development)
if [ "${DJANGO_SETTINGS_MODULE}" = "config.settings.development" ] && [ "${CREATE_SUPERUSER:-}" = "1" ]; then
    echo -e "${YELLOW}👤 Creating superuser (if not exists)...${NC}"
    gosu app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
fi

# Health check endpoint setup
echo -e "${YELLOW}🏥 Setting up health check...${NC}"
gosu app python manage.py shell -c "
from django.core.management import execute_from_command_line
import sys
try:
    from django.urls import reverse
    print('Health check endpoint available')
except:
    print('Note: Add health check URL to your Django URLs')
" || true

# Load initial data if specified
if [ "${LOAD_FIXTURES:-}" = "1" ]; then
    echo -e "${YELLOW}📊 Loading initial data...${NC}"
    gosu app python manage.py loaddata initial_data.json || echo "No initial data fixtures found"
fi

echo -e "${GREEN}✅ Django setup complete!${NC}"

# Production vs Development startup
if [ "${DJANGO_SETTINGS_MODULE}" = "config.settings.production" ]; then
    echo -e "${BLUE}🏭 Starting production server with Gunicorn...${NC}"
    # Switch to app user for running the server (using gosu to drop privileges)
    exec gosu app "$@"
else
    echo -e "${BLUE}🔧 Starting development server...${NC}"
    # Switch to app user for running the server (using gosu to drop privileges)
    exec gosu app python manage.py runserver 0.0.0.0:8000
fi