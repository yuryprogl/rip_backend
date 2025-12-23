from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for elemention
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in elemention secret!
SECRET_KEY = 'django-insecure-ak@ou_29q#pmjez&&8z%o9z%$b4#-!8)y9n%8xu=%q#dbx%5c$'

# SECURITY WARNING: don't run with debug turned on in elemention!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# --- CORS & CSRF SETTINGS ---
# Разрешаем запросы с любого источника (важно для Tauri/Frontend)
CORS_ALLOW_ALL_ORIGINS = True 
# Разрешаем передачу кук (session_id)
CORS_ALLOW_CREDENTIALS = True

# Важно: Django проверяет Origin при POST запросах. 
# Для Tauri и локальной разработки нужно добавить эти хосты в доверенные.
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "tauri://localhost",      # Для Tauri на macOS/Linux
    "https://tauri.localhost" # Для Tauri на Windows
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'app',
    'rest_framework',
    'drf_yasg',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware", # Должен быть как можно выше
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lab4.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'lab4.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'pgdb',
        'PORT': '5432'
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MINIO_ENDPOINT = 'minio:9000'
MINIO_ACCESS_KEY = 'minio'
MINIO_SECRET_KEY = 'minio123'
MINIO_USE_HTTPS = False
MINIO_MEDIA_FILES_BUCKET = "images"
MINIO_EXTERNAL_ENDPOINT = '192.168.105.1:9000' 

STORAGES = {
    "default": {
        "BACKEND": "django_minio_backend.models.MinioBackend",
        "OPTIONS": {
            # Важно: Ключи должны быть UPPERCASE (большими буквами)
            "MINIO_ENDPOINT": "minio:9000",
            "MINIO_ACCESS_KEY": "minio",
            "MINIO_SECRET_KEY": "minio123",
            "MINIO_USE_HTTPS": False,
            "MINIO_MEDIA_FILES_BUCKET": "images",
            "MINIO_PUBLIC_BUCKETS": ['images'],
            
            # Настройки для внешнего доступа
            "MINIO_EXTERNAL_ENDPOINT_USE_HTTPS": False,
            "MINIO_EXTERNAL_ENDPOINT": "192.168.105.1:9000",
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
    }
}

MINIO_ENDPOINT = 'minio:9000'
MINIO_USE_HTTPS = False
MINIO_EXTERNAL_ENDPOINT = 'localhost:9000'
MINIO_EXTERNAL_ENDPOINT_USE_HTTPS = False
MINIO_ACCESS_KEY = 'minio'
MINIO_SECRET_KEY = 'minio123'
MINIO_PUBLIC_BUCKETS = [
    'images'
]
MINIO_MEDIA_FILES_BUCKET = "images"

REDIS_HOST = "redis"
REDIS_PORT = 6379