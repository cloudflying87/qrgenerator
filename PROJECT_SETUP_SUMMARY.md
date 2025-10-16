# QRGENERATOR - Project Setup Summary

**Generated on**: 2025-10-15 22:15:56

## 🎯 Project Overview

**Name**: qrgenerator
**Description**: Building my own QR generator for fun.
**Domain**: Building QR codes
**Target Users**: QR generators
**Python Version**: 3.13.1

## 🎨 Design & Theme

**Primary Color**: #18181b
**Secondary Color**: #e5e7eb
**Accent Color**: #f97316
**Design Style**: Modern
**Border Radius**: 8px
**Shadow Style**: Medium
**Dark Mode**: Enabled
**Mobile Navigation**: Hamburger
**Share Image**: Provided ✓

## ⚙️ Technical Configuration

**Development Database**: SQLITE
**Features Enabled**:
- ❌ Celery (Background Tasks)
- ❌ Redis (Caching)
- ✅ REST API
- ❌ Sentry Error Tracking

**Remote Backup**: Not configured


## 🏗️ Architecture Details

**Development Workflow**:
- Local development with pyenv (no Docker)
- Hot reload with `python manage.py runserver`
- SQLITE database for development

**Production Stack**:
- Docker Compose orchestration
- PostgreSQL database
- Nginx web server with security headers
- Gunicorn WSGI server
- Automated build/deploy via build.sh

**CSS Architecture**:
- Custom component system (NO Bootstrap/Tailwind)
- Mobile-first responsive design
- CSS variables for consistent theming
- Component-based organization in static/css/components/

## 📁 Generated Project Structure

```
qrgenerator/
├── CLAUDE.md                    # Project memory (IMPORTANT for AI context)
├── build.sh                     # Production deployment automation
├── Makefile                     # Development commands (make help)
├── .python-version              # Auto pyenv activation
├── .pre-commit-config.yaml      # Code quality automation
├── README.md                    # Project overview
│
├── apps/                        # Django applications
│   └── core/                   # Base functionality
├── config/                      # Django settings
│   └── settings/               # Environment-specific settings
├── static/                      # Static assets
│   ├── css/                    # Custom CSS framework
│   │   ├── base.css            # Generated theme with your colors
│   │   └── components/         # Reusable components (buttons, forms, etc.)
│   ├── img/                    # Images
│   │   └── default-share.*     # Default share image (PWA/OG)
│   ├── js/                     # JavaScript
│   │   └── service-worker.js   # PWA service worker
│   └── manifest.json           # PWA manifest
├── templates/                   # Django templates
├── docs/                       # Comprehensive documentation
│   ├── SETUP_GUIDE.md         # Complete setup instructions
│   ├── BEGINNERS_GUIDE.md     # Tutorial for new developers
│   ├── STYLE_GUIDE.md         # Custom styling guidelines
│   ├── CODING_GUIDE.md        # Development standards
│   ├── FILE_HANDLING.md       # File upload & storage guide
│   └── PWA_SETUP.md           # PWA & Open Graph configuration
│
├── requirements/               # Python dependencies
├── nginx/                      # Production nginx config
├── docker-compose.yml          # Production containers
└── Dockerfile                  # Production image
```

## 🚀 Key Commands Reference

**Development**:
```bash
make run          # Start development server
make test         # Run tests
make shell        # Django shell
make migrate      # Database migrations
make format       # Auto-format code
make lint         # Check code quality
```

**Production**:
```bash
make deploy       # Deploy with backup
make backup       # Backup database
./build.sh -r -d $(date +%Y%m%d)  # Full rebuild
```

## 🎯 Domain-Specific Context

**Industry**: Building QR codes
**Compliance Requirements**: Standard security practices
**Special Features**: 

## 📋 Next Development Tasks

1. **Django Setup**:
   - Move settings.py to config/settings/ structure
   - Create base, development, and production settings
   - Add 'apps.core' to INSTALLED_APPS

2. **Model Development**:
   - Define domain models in apps/core/models.py
   - Create migrations and migrate
   - Set up admin interface

3. **Frontend**:
   - Custom CSS components are ready in static/css/
   - Mobile-first templates in templates/
   - No Bootstrap/Tailwind - use custom system

4. **Quality Setup**:
   - Pre-commit hooks configured
   - Code formatting with black/isort
   - Linting with flake8

## 🤖 AI Assistant Instructions

When helping with this project:

1. **NEVER suggest Bootstrap/Tailwind** - We have a complete custom CSS system
2. **Always think mobile-first** - Every component starts with mobile design
3. **Use the custom CSS variables** - Primary: #18181b, etc.
4. **Follow the build.sh pattern** - Production deployment via Docker
5. **Reference CLAUDE.md** - Contains living project context
6. **Domain focus**: This is a Building QR codes application for QR generators

## 🔧 Quick Context for Development

**Current Status**: Fresh project setup completed
**Ready for**: Django project creation and initial model development
**Architecture**: Same proven patterns as Keep-Logging project
**Styling**: Custom Modern theme with #18181b primary color
**Deployment**: Docker production, pyenv development

---

*This summary provides complete context for AI assistants and developers joining the project.*
