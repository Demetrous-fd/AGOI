"""
Django settings for AGOI project.

Generated by 'django-admin startproject' using Django 3.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from os import getenv

import dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

dotenv.read_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if getenv("DEBUG", "").lower() != "true" else True

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost", getenv("APP_DOMAIN", "localhost")]
    USE_X_FORWARDED_PORT = True

# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'AGOI.apps.MyAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'more_admin_filters',
    'admin_auto_filters',
    'rangefilter',
    'simple_history',
    'qr_code',
    "inventory",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'AGOI.urls'

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

WSGI_APPLICATION = 'AGOI.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DB_ENGINE = getenv("DB_ENGINE", "sqlite")
DB_OPTIONS = {
    "sqlite": {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    "postgres": {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv("DB_NAME", "postgres"),
        'USER': getenv("DB_USER", "postgres"),
        'PASSWORD': getenv("DB_PASSWORD", "postgres"),
        'HOST': getenv("DB_HOST", "localhost"),
        'PORT': getenv("DB_PORT", "5432"),
    }
}

DATABASES = {
    'default': DB_OPTIONS[DB_ENGINE]
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Irkutsk'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

LOGIN_URL = 'admin/login'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

USE_QR_FULL_URI = False if getenv("USE_QR_FULL_URI", "").lower() != "true" else True
APP_DOMAIN = getenv("APP_DOMAIN", None)
_APP_EXTERNAL_PORT = getenv("APP_EXTERNAL_PORT", "")
APP_EXTERNAL_PORT = _APP_EXTERNAL_PORT if _APP_EXTERNAL_PORT not in ("80", "443", "") \
                                          and _APP_EXTERNAL_PORT.isdigit() else ""

CSRF_TRUSTED_ORIGINS = [f"http://{APP_DOMAIN}:{APP_EXTERNAL_PORT}", f"https://{APP_DOMAIN}:{APP_EXTERNAL_PORT}"]
