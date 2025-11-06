import sys
from dotenv import load_dotenv
from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load the environment variables 
load_dotenv()

# Security

SECRET_KEY = os.environ.get("SECRET_KEY")

# Uncomment on production
# SECURE_HSTS_SECONDS = 31536000  
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True  
# SECURE_HSTS_PRELOAD = True  

# # Additional security settings
# SECURE_SSL_REDIRECT = True  
# SESSION_COOKIE_SECURE = True  
# CSRF_COOKIE_SECURE = True 

DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'service',
    'django_celery_results',
    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',  
]

# CORS settings for FastAPI
CORS_ORIGIN_ALLOW_ALL = True

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',  
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'blogging_system',  
    }
}

# Cache Timeouts
CACHE_TTL = 60 * 15  # Cache timeout in seconds (e.g., 15 minutes)

# Use Redis for session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Celery Configuration Options
CELERY_BROKER_URL = 'redis://redis:6379/0'  
CELERY_RESULT_BACKEND = 'django-db'  
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# User Authentication
AUTH_USER_MODEL = 'service.CustomUser'

ROOT_URLCONF = 'bloggin_system.urls'





MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'Media') 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

WSGI_APPLICATION = 'bloggin_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'HOST': 'db',
        'PORT': 5432,
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Logging Configuration
LOGS_DIR = os.path.join(BASE_DIR, 'Logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '[%(asctime)s] [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',  
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'Logs/log.txt'),
            'maxBytes': 1024 * 1024 * 15,  
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO', 
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO', 
            'propagate': True,
        },
        'service': {
            'handlers': ['file', 'console'],
            'level': 'INFO', 
            'propagate': False,
        },
    },
}

# Test-specific configuration
if 'test' in sys.argv or 'pytest' in sys.modules:
    # Test-specific database configuration
    # Use keepdb to reuse database between test runs for speed
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db_for_pytest',
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'HOST': 'db',
        'PORT': 5432,
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'TEST': {
            'NAME': 'test_db_for_pytest',
        },
        'CONN_MAX_AGE': 0,  # Disable persistent connections for tests
    }
    
    # Disable password validators for faster tests
    AUTH_PASSWORD_VALIDATORS = []
    
    # Use dummy cache backend for tests (no Redis needed)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    
    # Use database sessions instead of cache for tests
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    
    # Disable Celery for tests (use eager mode)
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
    
    # Reduce logging in tests
    LOGGING['loggers']['django']['level'] = 'WARNING'
    LOGGING['loggers']['service']['level'] = 'WARNING'