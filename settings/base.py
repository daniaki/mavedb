# settings/base.py

import os
import json

from django.core.exceptions import ImproperlyConfigured

# Read the secrets file
with open('secrets.json') as handle:
    secrets = json.load(handle)


def get_secret(setting, secrets=secrets):
    """
    Retrieve a named setting from the secrets dictionary read from the JSON.

    Adapted from Two Scoops of Django, Example 5.21
    """
    try:
        return secrets[setting]
    except KeyError:
        error_message = "Unable to retrieve setting: '{}'".format(setting)
        raise ImproperlyConfigured(error_message)


SECRET_KEY = get_secret('secret_key')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LICENCE_DIR = BASE_DIR + '/licences/'

# Social auth settings for ORCID authentication
SOCIAL_AUTH_ORCID_KEY = get_secret('orcid_key')
SOCIAL_AUTH_ORCID_SECRET = get_secret('orcid_secret')
SOCIAL_AUTH_USER_MODEL = 'auth.User'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/accounts/profile/"
SOCIAL_AUTH_LOGIN_ERROR_URL = "/accounts/error/"
SOCIAL_AUTH_URL_NAMESPACE = 'accounts:social'
SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'social_core.pipeline.social_auth.associate_by_email',
]

# Application definition
INSTALLED_APPS = [
    'main',
    'api',
    'accounts',
    'experiment',
    'scoreset',
    'search',
    'guardian',
    'reversion',
    'social_django',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mod_wsgi.server',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # this is default
    'guardian.backends.ObjectPermissionBackend',
    'social_core.backends.orcid.ORCIDOAuth2'
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Social-auth middleware
    'social_django.middleware.SocialAuthExceptionMiddleware'
]

ROOT_URLCONF = 'mavedb.urls'

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

                # Social-auth context_processors
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'mavedb.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'static'))
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400

# Redirect to home URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGOUT_REDIRECT_URL = '/accounts/profile/'

# DEBUG email server, set to something proper when DEBUG = FALSE
DEFAULT_FROM_EMAIL = "mavedb@mavedb.org"
SERVER_EMAIL = "admin@mavedb.org"
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Host for sending e-mail
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

# Optional SMTP authentication information for EMAIL_HOST
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

# Reply-to email for user emails
# REPLY_TO_EMAIL = os.environ.get("MAVEDB_REPLY_TO_EMAIL", '')
REPLY_TO_EMAIL = "alan.rubin@wehi.edu.au"

