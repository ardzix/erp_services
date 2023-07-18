# Copy this file to local_settings.py and configure it

import os
import datetime

BASE_URL = "http://127.0.0.1:8000/"
DEBUG = True
PRODUCTION = False
SITE_ID = 1
CORS_ORIGIN_ALLOW_ALL = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'erp_db',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'erp_db_test'
        }
    }
}