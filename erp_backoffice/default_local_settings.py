# Copy this file to local_settings.py and configure it

import os
import datetime
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from '.env' file


BASE_URL = os.getenv('BASE_URL')
DEBUG = True
PRODUCTION = False
SITE_ID = 1
CORS_ORIGIN_ALLOW_ALL = True



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', False)

# Assuming your ALLOWED_HOSTS is defined as "host1.example.com,host2.example.com"
allowed_hosts_str = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = allowed_hosts_str.split(',') if allowed_hosts_str else []

csrf_str = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = csrf_str.split(',') if csrf_str else []


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# S3 Configuration
USE_S3 = True
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_SIGNATURE_VERSION = "s3v4"