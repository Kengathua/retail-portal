"""
Django settings for elites_retail_portal project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
import psycopg2
from pathlib import Path
from datetime import timedelta
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-^pa2=6*-vo@hne3@l26&&v(9__@rx!a4m28xy#2-+gf!$zd7lp')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"

NGROK_BASE_URL = 'http://2028-197-237-137-119.ngrok.io'
# ALLOWED_HOSTS = [
#     'kengathua.pythonanywhere.com', '127.0.0.1', 'localhost', '.ngrok.io',
#     NGROK_BASE_URL, 'chrome-extension://fhbjgbiflinjbdggehcddcbncdddomop',
#     'http://retail-portal.eba-uk5xvhjm.eu-west-2.elasticbeanstalk.com',
#     'http://localhost:3000/']

# CSRF_TRUSTED_ORIGINS = ['chrome-extension://fhbjgbiflinjbdggehcddcbncdddomop',
#                         'chrome-extension://gighmmpiobklfepjocnamgkkbiglidom/browser-polyfill.js.map',
#                         'http://retail-portal.eba-uk5xvhjm.eu-west-2.elasticbeanstalk.com']

CORS_ORIGIN_ALLOW_ALL = True

ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = [
    'localhost', '127.0.0.1', '68.183.33.98', 'kengathua.pythonanywhere.com',
    '.uat-elites-retail-portal.com', '.staging.uat-elites-retail-portal.com',]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django_filters',
    'rest_framework',
    'rest_framework_simplejwt',
]

LOCAL_APPS = [
    'elites_retail_portal.users',
    'elites_retail_portal.debit',
    'elites_retail_portal.items',
    'elites_retail_portal.orders',
    'elites_retail_portal.credit',
    'elites_retail_portal.wallet',
    'elites_retail_portal.catalog',
    'elites_retail_portal.adapters',
    'elites_retail_portal.customers',
    'elites_retail_portal.warehouses',
    'elites_retail_portal.enterprises',
    'elites_retail_portal.encounters',
    'elites_retail_portal.transactions',
    'elites_retail_portal.enterprise_mgt',
    'elites_retail_portal.adapters.mobile_money.mpesa',
]

INSTALLED_APPS += LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'elites_retail_portal.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'elites_retail_portal.config.wsgi.application'

"""
This is a helper variable that you will use to determine when to connect to Postgres database
and when to connect to a local SQLite database for testing."""

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"
# ENVIRONMENTS = ['DEVELOPMENT', 'STAGING', 'UAT-TEST', 'PRODUCTION']

ENVIRONMENT = os.getenv("ENVIRONMENT", "DEVELOPMENT")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
DEBUG = True

if not ENVIRONMENT == 'DEVELOPMENT':
    DATABASES = {
        "default": dj_database_url.parse(
            os.environ.get(
                "DATABASE_URL",
                "postgres://elites_user:elites_pass@localhost:5432/elites_franchises"
            )
        ),
    }

    # Keep connections alive for 10 minutes in production
    DATABASES['default']['CONN_MAX_AGE'] = 0 if DEBUG else 600

    # set transaction isolation level
    isolation_level = os.getenv('PG_TRANSACTION_ISOLATION_LEVEL', 'READ_COMMITTED')
    isolation_level_choices = {
        'READ_COMMITTED': psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED,
        'REPEATABLE_READ': psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ,
        'SERIALIZABLE': psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
    }
    options = DATABASES['default'].get('OPTIONS', {})
    options.update({
        'isolation_level': isolation_level_choices.get(isolation_level, 'READ_COMMITTED'),
    })
    DATABASES['default']['OPTIONS'] = options

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.getenv("POSTGRES_DB_NAME", 'elites_franchise'),
#         'USER': os.getenv("POSTGRES_DB_USER", 'elites_user'),
#         'PASSWORD': os.getenv("POSTGRES_DB_PASSWORD", 'elites_pass'),
#         'HOST': os.getenv("POSTGRES_DB_HOST", 'localhost'),
#         'PORT': os.getenv("POSTGRES_DB_PORT", '5432'),
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_MODEL_SERIALIZER_CLASS': [
        'rest_framework.ModelSerializer',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'elites_retail_portal.common.filters.EnterpriseFilterBackend',
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'elites_retail_portal.common.permissions.DRFScreenPermission',
    ],

    # Throttling settings
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/second',
        'anon': '4/minute'
    },
    'DEFAULT_PAGINATION_CLASS': 'elites_retail_portal.common.pagination.EnhancedPagination',
    'EXCEPTION_HANDLER': 'elites_retail_portal.common.exception_handlers.custom_exception_handler',
    # 'PAGE_SIZE': 50,    # Default paginated page size
    'PAGE_SIZE': 10,    # Default paginated page size
    'DATETIME_FORMAT': 'iso-8601',
    'DATE_FORMAT': 'iso-8601',
    'TIME_FORMAT': 'iso-8601',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10000),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('JWT',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

DATE_INPUT_FORMATS = ['%Y-%m-%d']

# Media files
DEFAULT_MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles/')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', DEFAULT_MEDIA_ROOT)
MEDIA_URL = '/media/'
SECURE_MEDIA_URL = '/secure_media/'

if DEBUG:
    SENDFILE_BACKEND = 'sendfile.backends.development'
else:
    SENDFILE_BACKEND = 'sendfile.backends.nginx'
    SENDFILE_ROOT = MEDIA_ROOT
    SENDFILE_URL = SECURE_MEDIA_URL

SOCIAL_AUTH_RAISE_EXCEPTIONS = False
LOGIN_ERROR_URL = '/'
LOGIN_REDIRECT_URL = '/v1/errors/'
LOGIN_URL = '/auth/login/'

MPESA_C2B_URL = F'{NGROK_BASE_URL}/v1/adapters/mobile_money/safaricom/c2b/callback/'
MPESA_CHECKOUT_URL = 'https://sandbox.safaricom.co.ke/safaricom/stkpush/v1/processrequest'
MPESA_ACCESS_TOKEN_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'  # noqa


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True


# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CACHE_TTL = 60 * 1
# @method_decorator(cache_page(CACHE_TTL))

CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_TASK_RESULT_EXPIRES = 30  # in seconds
# CELERY_TASK_RESULT_EXPIRES = 300  # in seconds
CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_TIME_LIMIT = int(60 * 60 * 12)  # 12 hours in seconds
CELERY_TASK_IGNORE_RESULT = True

# Email address: adminuser@email.com
# First name: Admin
# Last name: User
# Password: Hu46!YftP6^l$
