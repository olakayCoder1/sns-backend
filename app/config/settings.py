from pathlib import Path
from datetime import timedelta
import os
import environ
import cloudinary

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    ON_SERVER=(bool, True), LOGGING_LEVEL=(str, "INFO"), DEBUG=(bool, False)
)

IGNORE_DOT_ENV_FILE = env.bool("IGNORE_DOT_ENV_FILE", default=False)
if not IGNORE_DOT_ENV_FILE:
    # reading .env file
    environ.Env.read_env(env_file=os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!

ON_SERVER = env("ON_SERVER", default=True)

if ON_SERVER:
    DEBUG = False
    CORS_ORIGIN_REGEX_WHITELIST = env.list(
        "CORS_ORIGIN_REGEX_WHITELIST", default=[]
    )
    ALLOWED_HOSTS = ["localhost", "api.socialfeed.jp", "socialfeed.jp"]
    CORS_ALLOWED_ORIGINS = [
        "https://api.socialfeed.jp",
        "https://socialfeed.jp",
    ]
    CSRF_TRUSTED_ORIGINS = [
        "https://api.socialfeed.jp",
        "https://socialfeed.jp",
    ]
else:
    DEBUG = True
    CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles"
]
THIRD_PARTY_APPS = [
    "corsheaders",
    "django_extensions",
    "rest_framework",
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework_swagger',       # Swagger 
    'drf_yasg',                     # Yet Another Swagger generator
    'django_crontab',
    'dbbackup'
]
OUR_APPS = [
    "jwt_auth",
    "api.v0.owner",
    "api.v0.customer.member",
    "api.v0.customer.admin_user",
    "api.v0.shared",
    "db_schema",
    'django_mailbox'
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + OUR_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if not ON_SERVER:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(9, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = [
        '127.0.0.1',
    ]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        BASE_DIR / 'templates',
    ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
},]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# Database
if ON_SERVER:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env("DB_NAME"),
            'USER':  env("DB_USER"),
            'PASSWORD':  env("DB_PASSWORD"),
            'HOST':'localhost',
            'PORT':'3306',
        }
    }
    DBBACKUP_CONNECTORS = {
        'default': {
            'USER': env("DB_USER"),
            'PASSWORD': env("DB_PASSWORD"),
            'HOST': 'localhost'
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': "auto_posting_tool",
            'USER':  "root",
            'PASSWORD':  "",
            'HOST':'localhost',
            'PORT':'3306',
        }
    }
    DBBACKUP_CONNECTORS = {
        'default': {
            'USER': 'root',
            'PASSWORD': '',
            'HOST': 'localhost'
        }
    }
    
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': f'{BASE_DIR}/backup/' }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

password_validators = [
    "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    "django.contrib.auth.password_validation.MinimumLengthValidator",
    "django.contrib.auth.password_validation.CommonPasswordValidator",
    "django.contrib.auth.password_validation.NumericPasswordValidator",
]
AUTH_PASSWORD_VALIDATORS = [{"NAME": v} for v in password_validators]
AUTH_USER_MODEL = "jwt_auth.User"

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tokyo"

USE_I18N = True

USE_L10N = True

USE_TZ = False

STORAGE_ROOT = os.path.join(BASE_DIR, 'storage')


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

cloudinary.config(
    cloud_name='drbjh9df5',  # Replace with your Cloudinary cloud name
    api_key='975346332749118',        # Replace with your Cloudinary API key
    api_secret='pE0hNc2eTxYdn0g6muN5qD2TK00',  # Replace with your Cloudinary API secret
    secure=True
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'drbjh9df5',
    'API_KEY': '975346332749118',
    'API_SECRET': 'pE0hNc2eTxYdn0g6muN5qD2TK00'
}

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'

DJANGO_CSS_INLINE_ENABLE = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema' 
}

# CRON Jobs Settings
# run cron.mail.py every 5 s
CRONJOBS = [
    
]

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}


#Email
# DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
DEFAULT_FROM_EMAIL = "info@socialfeed.jp"
# EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST = "hit-mail2.jp"
EMAIL_PORT = 587                  
EMAIL_HOST_USER = "info@socialfeed.jp"
# EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True 
if ON_SERVER:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'jwt_auth.backend.LoggingEmailBackend'

# In your Django project's settings.py, configure Celery to use the chosen message broker. Here's an example configuration for Redis:
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
    

# Maximum size in bytes allowed for uploaded files.
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
# Maximum size in bytes allowed for a single file uploaded via a multipart/form-data request.
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
# Maximum size in bytes allowed for an uploaded file.
FILE_UPLOAD_MAX_SIZE = 100 * 1024 * 1024  # 100MB