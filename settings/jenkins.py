# settings/staging.py
from .staging import *

import logging

# Disable logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}
logging.disable(logging.CRITICAL)

# ------ CELERY CONFIG ------------------- #
# Celery needs these in each settings file
DATASET_TASK_SOFT_TIME_LIMIT =  10 * 60  # In seconds
broker_url = 'amqp://localhost:5672//'
accept_content = ('json',)
result_serializer = 'json'

task_ignore_result = True
task_serializer = 'json'
worker_hijack_root_logger = False
task_soft_time_limit = 60  # seconds
task_always_eager = False
task_create_missing_queues = True

# Celery needs this for autodiscover to work
INSTALLED_APPS = [
    'metadata',
    'main',
    'genome',
    'urn',
    'variant',
    'dataset',
    'search',
    'api',
    'accounts',
    'core',

    'guardian',
    'reversion',
    'social_django',
    'django_extensions',
    'widget_tweaks',
    'rest_framework',
    'django_filters',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]