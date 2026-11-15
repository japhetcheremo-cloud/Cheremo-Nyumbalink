
"""
Django settings for nyumbalink project.
Django 6.0 configuration for local development,
Vercel, PostgreSQL, SQLite and WhiteNoise.
"""

import os
from pathlib import Path

import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
# VERCEL DETECTION
# ==========================================================

IS_VERCEL = bool(
    os.environ.get('VERCEL')
    or os.environ.get('VERCEL_ENV')
    or os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
    or str(BASE_DIR).startswith('/var/task')
)


# ==========================================================
# SECURITY CONFIGURATION
# ==========================================================

SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    if IS_VERCEL:
        raise ValueError(
            "SECRET_KEY environment variable is required on Vercel."
        )
    SECRET_KEY = 'django-insecure-local-development-only-key'

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'


# ==========================================================
# ALLOWED HOSTS
# ==========================================================

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.vercel.app',
    'cheremo-nyumbalink.vercel.app',
]

extra_hosts = os.environ.get('ALLOWED_HOSTS', '')

if extra_hosts:
    ALLOWED_HOSTS.extend(
        host.strip()
        for host in extra_hosts.split(',')
        if host.strip()
    )


# ==========================================================
# APPLICATIONS
# ==========================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'users',
    'properties',
    'chat',
    'core',
]


# ==========================================================
# MIDDLEWARE
# ==========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'nyumbalink.urls'


# ==========================================================
# TEMPLATES
# ==========================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'nyumbalink.wsgi.application'


# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================

DATABASE_URL = os.environ.get('DATABASE_URL')

if IS_VERCEL:

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is required on Vercel."
        )

    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=0,
            ssl_require=True,
        )
    }

elif DATABASE_URL:

    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=0,
        )
    }

else:

    # Local development uses SQLite.

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ==========================================================
# PASSWORD VALIDATION
# ==========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==========================================================
# INTERNATIONALIZATION
# ==========================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# ==========================================================
# STATIC FILES
# ==========================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# ==========================================================
# DJANGO 6 STORAGE CONFIGURATION
# ==========================================================

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


# ==========================================================
# MEDIA FILES
# ==========================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ==========================================================
# AUTHENTICATION
# ==========================================================

AUTH_USER_MODEL = 'users.CustomUser'

LOGIN_URL = 'login'

LOGIN_REDIRECT_URL = 'dashboard_redirect'

LOGOUT_REDIRECT_URL = 'home'


# ==========================================================
# SESSION CONFIGURATION
# ==========================================================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_COOKIE_AGE = 1209600

SESSION_SAVE_EVERY_REQUEST = True

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SAMESITE = 'Lax'


# ==========================================================
# SECURITY AND HTTPS
# ==========================================================

CSRF_TRUSTED_ORIGINS = [
    'https://cheremo-nyumbalink.vercel.app',
    'https://*.vercel.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

if IS_VERCEL:

    SECURE_PROXY_SSL_HEADER = (
        'HTTP_X_FORWARDED_PROTO',
        'https',
    )

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_SSL_REDIRECT = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = 'DENY'

else:

    SESSION_COOKIE_SECURE = False

    CSRF_COOKIE_SECURE = False


# Allow additional trusted origins through environment variables.

extra_origins = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    ''
)

if extra_origins:
    CSRF_TRUSTED_ORIGINS.extend(
        origin.strip()
        for origin in extra_origins.split(',')
        if origin.strip()
    )


# ==========================================================
# DEFAULT PRIMARY KEY
# ==========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
