"""
Django settings for erp_backoffice project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$(i+u8smen#ob!^5i7o5j4*cdsm44k8e@=%j_3-vxa$t6^&3=t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["erp.nikici.com"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.sites",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django_extensions',
    'corsheaders',

    'common',
    'identities',
    'sales',
    'purchasing',
    'inventory',
    'production',
    'accounting',
    'hr',
    'crm',
    'logistics',

    'rest_framework',
    'rest_framework.authtoken',
    'leaflet',
    'drf_yasg',
    'reversion',
    'scheduler'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'libs.middleware.SetCurrentUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'erp_backoffice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'erp_backoffice.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # 'compressor.finders.CompressorFinder',
)

# Media storage
MEDIA_ROOT = os.path.join(BASE_DIR, "static/upload")
STATICFILES_DIRS = [
    # ...
    ("upload", MEDIA_ROOT),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (-2.4833, 117.8903),  # Coordinates for Indonesia
    'DEFAULT_ZOOM': 4,
    'ATTRIBUTION_PREFIX': 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    'MAX_ZOOM': 18,
    'MIN_ZOOM': 1,
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'libs.middleware.CustomTokenAuthentication',
    ],
    "COERCE_DECIMAL_TO_STRING": False,
}

# swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'ApiKeyAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Token for authentication. Format: "Token {token}"'
        },
        'LangHeader': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Accept-Language',
            'description': 'Language preference. Example: "en-us"'
        }
    },
    'SECURITY_REQUIREMENTS': [
        {"ApiKeyAuth": []}, 
        {"LangHeader": []}
    ],
    "USE_SESSION_AUTH": False
}

LANGUAGES = [
    ('en', _('English')),
    ('id', _('Indonesian')),
    # other languages
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]


# load settings based on env
from .local_settings import *
