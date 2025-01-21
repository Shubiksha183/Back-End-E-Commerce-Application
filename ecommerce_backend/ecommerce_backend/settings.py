import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "default-secret-key")

DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

if not DEBUG and SECRET_KEY == "default-secret-key":
    raise ValueError("Please set a valid SECRET_KEY in your environment variables.")

ALLOWED_HOSTS = ['0.0.0.0','localhost','127.0.0.1']

INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'corsheaders',
    'rest_framework_simplejwt',
    'debug_toolbar',
    'django_extensions',
]
AUTH_USER_MODEL = 'api.CustomUser'

CORS_ALLOW_ALL_ORIGINS = True



MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     'debug_toolbar.middleware.DebugToolbarMiddleware'
]


ROOT_URLCONF = 'ecommerce_backend.urls'
WSGI_APPLICATION = 'ecommerce_backend.wsgi.application'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:9200",
    "http://127.0.0.1:3000"
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME", "ecommerce_db"),
        'USER': os.getenv("DB_USER", "postgres"),
        'PASSWORD': os.getenv("DB_PASSWORD", "root123"),
        'HOST': os.getenv("DB_HOST", "localhost"),
        'PORT': os.getenv("DB_PORT", "5432"),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'ecommerce_db',
#         'USER': 'postgres',
#         'PASSWORD': 'root123',
#         'HOST': 'db',
#         'PORT': 5432,
#     }
# }


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from elasticsearch import Elasticsearch

# Create Elasticsearch client
es = Elasticsearch(
    hosts=["http://localhost:9200"],  # Connects to Elasticsearch on localhost
)

# ELASTICSEARCH_DSL configuration
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://localhost:9200',  # No security, plain HTTP
    }
}


# es = Elasticsearch(
#     hosts=["http://elasticsearch:9200"],  # Connects to Elasticsearch via Docker service name
# )

# # ELASTICSEARCH_DSL configuration
# ELASTICSEARCH_DSL = {
#     'default': {
#         'hosts': 'http://elasticsearch:9200',  # Using service name defined in docker-compose.yml
#     }
# }


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'SIGNING_KEY': SECRET_KEY,
    'ALGORITHM': 'HS256',
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

