"""
Development settings for qrgenerator
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Development hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Database - always use sqlite for development unless explicitly configured
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development-only apps
INSTALLED_APPS += [
    'django_extensions',
]

# Development middleware
if DEBUG:
    # Browser reload (only if installed)
    try:
        import django_browser_reload
        INSTALLED_APPS += ['django_browser_reload']
        MIDDLEWARE = ['django_browser_reload.middleware.BrowserReloadMiddleware'] + MIDDLEWARE
    except ImportError:
        pass

    # Debug toolbar (only if installed)
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
        INTERNAL_IPS = ['127.0.0.1', 'localhost']

        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        }
    except ImportError:
        pass

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache settings for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable security settings for development
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Development logging - more verbose
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers'] = {
    'django': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },
    'apps': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    },
}