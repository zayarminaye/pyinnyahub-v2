"""
Django settings for Pyinnya Hub LMS project.
Configured for scalability and easy transition from development to production.
"""
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv
import dj_database_url
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'cloudinary_storage',  # Must be before django.contrib.staticfiles
    'cloudinary',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'django_apscheduler',

    # Local apps (order matters for migrations)
    'core.apps.CoreConfig',
    'users.apps.UsersConfig',
    'courses.apps.CoursesConfig',
    'subscriptions.apps.SubscriptionsConfig',
    'payments.apps.PaymentsConfig',
    'payouts.apps.PayoutsConfig',
    'notifications.apps.NotificationsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files efficiently in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS must be before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==============================================================================
# MESSAGES CONFIGURATION
# ==============================================================================
# Map Django message levels to Bootstrap alert classes
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',  # Map error to danger for Bootstrap red alerts
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Global templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',  # For media files in templates
                'core.context_processors.system_settings',  # Custom: System-wide settings
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# Production: Use DATABASE_URL from Render/Railway/Heroku
# Development: Use SQLite
if 'DATABASE_URL' in os.environ:
    # Production database (Render, Railway, Heroku provide this)
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ['DATABASE_URL'],
            conn_max_age=600,  # Connection pooling - keep connections alive for 10 minutes
            conn_health_checks=True,  # Verify connections are healthy before using
        )
    }
else:
    # Development database
    DATABASE_ENGINE = config('DATABASE_ENGINE', default='django.db.backends.sqlite3')

    if DATABASE_ENGINE == 'django.db.backends.sqlite3':
        DATABASES = {
            'default': {
                'ENGINE': DATABASE_ENGINE,
                'NAME': BASE_DIR / config('DATABASE_NAME', default='db.sqlite3'),
            }
        }
    else:
        # PostgreSQL configuration (for local development with PostgreSQL)
        DATABASES = {
            'default': {
                'ENGINE': DATABASE_ENGINE,
                'NAME': config('DATABASE_NAME'),
                'USER': config('DATABASE_USER'),
            'PASSWORD': config('DATABASE_PASSWORD'),
            'HOST': config('DATABASE_HOST', default='localhost'),
            'PORT': config('DATABASE_PORT', default='5432'),
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Yangon'  # Myanmar timezone
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# ==============================================================================
# CLOUD STORAGE CONFIGURATION
# ==============================================================================

# Determine which storage backend to use
USE_CLOUDINARY = config('USE_CLOUDINARY', default=False, cast=bool)
USE_AWS_S3 = config('USE_AWS_S3', default=False, cast=bool)

# Cloudinary Configuration (MVP - Free tier: 25GB storage, 25GB bandwidth/month)
if USE_CLOUDINARY:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
        'API_KEY': config('CLOUDINARY_API_KEY', default=''),
        'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
    }
    MEDIA_URL = '/media/'  # Cloudinary will handle the actual URL
    DEFAULT_STORAGE_BACKEND = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# AWS S3 Configuration (For Scaling - Prepared but not active yet)
elif USE_AWS_S3:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='ap-southeast-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'public-read'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
    DEFAULT_STORAGE_BACKEND = 'storages.backends.s3boto3.S3Boto3Storage'

# Local Storage (Development fallback)
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    DEFAULT_STORAGE_BACKEND = 'django.core.files.storage.FileSystemStorage'

# Django 4.2+ STORAGES configuration (replaces DEFAULT_FILE_STORAGE)
STORAGES = {
    "default": {
        "BACKEND": DEFAULT_STORAGE_BACKEND,
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# REST FRAMEWORK CONFIGURATION
# ==============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # For browsable API
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# ==============================================================================
# JWT CONFIGURATION
# ==============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=config('JWT_REFRESH_TOKEN_LIFETIME', default=1440, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ==============================================================================
# CORS CONFIGURATION (For future React frontend)
# ==============================================================================
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True

# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=10, cast=int)  # 10 second timeout
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Pyinnya Hub LMS <noreply@pyinnyahub.com>')

# ==============================================================================
# SITE CONFIGURATION
# ==============================================================================
SITE_NAME = config('SITE_NAME', default='Pyinnya Hub LMS')
SITE_URL = config('SITE_URL', default='http://localhost:8000')
SUPPORT_EMAIL = config('SUPPORT_EMAIL', default='support@pyinnyahub.com')

# ==============================================================================
# FILE UPLOAD CONFIGURATION
# ==============================================================================
MAX_UPLOAD_SIZE = config('MAX_UPLOAD_SIZE', default=10485760, cast=int)  # 10MB
ALLOWED_RECEIPT_TYPES = config(
    'ALLOWED_RECEIPT_TYPES',
    default='image/jpeg,image/png,application/pdf',
    cast=Csv()
)
ALLOWED_COURSE_FILE_TYPES = config(
    'ALLOWED_COURSE_FILE_TYPES',
    default='video/mp4,application/pdf,image/jpeg,image/png',
    cast=Csv()
)

# ==============================================================================
# SUBSCRIPTION CONFIGURATION
# ==============================================================================
MONTHLY_DAYS = config('MONTHLY_DAYS', default=30, cast=int)
YEARLY_DAYS = config('YEARLY_DAYS', default=365, cast=int)
EXPIRY_REMINDER_DAYS = config('EXPIRY_REMINDER_DAYS', default=3, cast=int)

# ==============================================================================
# FEATURE FLAGS (Admin can toggle these)
# ==============================================================================
ENABLE_REGISTRATION = config('ENABLE_REGISTRATION', default=True, cast=bool)
ENABLE_INSTRUCTOR_APPLICATIONS = config('ENABLE_INSTRUCTOR_APPLICATIONS', default=True, cast=bool)
ENABLE_PAYMENT_UPLOADS = config('ENABLE_PAYMENT_UPLOADS', default=True, cast=bool)

# ==============================================================================
# APSCHEDULER CONFIGURATION
# ==============================================================================
SCHEDULER_AUTOSTART = config('SCHEDULER_AUTOSTART', default=True, cast=bool)
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25  # Seconds

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'pyinnyahub': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# ==============================================================================
# SECURITY SETTINGS (For production)
# ==============================================================================
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
