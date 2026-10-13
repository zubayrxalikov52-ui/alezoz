"""
Al Ezoz — Django Settings
Configured for Local Development and Production Deployment on Railway.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.getenv('SECRET_KEY', 'allon-cafe-django-secret-key-change-in-production-2026')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['*']

# CSRF Trusted Origins for Railway and local development
csrf_origins_env = os.getenv(
    'CSRF_TRUSTED_ORIGINS',
    'https://*.railway.app,https://*.up.railway.app,http://127.0.0.1,http://localhost'
)
CSRF_TRUSTED_ORIGINS = [orig.strip() for orig in csrf_origins_env.split(',') if orig.strip()]

# APPLICATIONS
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.menu',
    'apps.orders',
    'apps.dashboard',
    'apps.telegram_bot',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.menu.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# DATABASE (Automatic PostgreSQL detection on Railway or SQLite fallback)
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
        }
    except Exception:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# AUTH
AUTH_USER_MODEL = 'accounts.CustomUser'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# STATIC & WHITENOISE
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True

# MEDIA
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SESSION
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# TELEGRAM BOT
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME', 'alezozmilliycafebot')
ADMIN_TELEGRAM_ID = os.getenv('ADMIN_TELEGRAM_ID', '')
CHEF_TELEGRAM_IDS = os.getenv('CHEF_TELEGRAM_IDS', os.getenv('CHEF_TELEGRAM_ID', ''))

# 2FA Verification
VERIFICATION_CODE_EXPIRE_SECONDS = int(os.getenv('VERIFICATION_CODE_EXPIRE_SECONDS', '180'))
MAX_VERIFICATION_ATTEMPTS = int(os.getenv('MAX_VERIFICATION_ATTEMPTS', '3'))

# Restaurant Info
RESTAURANT_NAME = os.getenv('RESTAURANT_NAME', 'Al Ezoz')
RESTAURANT_PHONE = os.getenv('RESTAURANT_PHONE', '+998 90 911 52 52, +998 90 138 18 23')
RESTAURANT_ADDRESS = os.getenv('RESTAURANT_ADDRESS', "Toshkent shahri, Amir Temur shoh ko'chasi, 42-uy")
RESTAURANT_HOURS = os.getenv('RESTAURANT_HOURS', '09:00 - 23:00')

# Custom admin/chef URLs
ADMIN_PANEL_URL = os.getenv('ADMIN_PANEL_URL', 'secure-admin')
CHEF_PANEL_URL = os.getenv('CHEF_PANEL_URL', 'chef-panel')

# Django LoginRequiredMixin redirect URL
LOGIN_URL = f'/{os.getenv("ADMIN_PANEL_URL", "secure-admin")}/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'WARNING'},
        'apps': {'handlers': ['console'], 'level': 'DEBUG' if DEBUG else 'INFO'},
    },
}
