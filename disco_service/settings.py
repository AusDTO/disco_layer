"""
settings module
===============

Standard django project configuration file

https://docs.djangoproject.com/en/1.8/topics/settings/
https://docs.djangoproject.com/en/1.8/ref/settings/

.. note::

   envparse.env used to create default values that are overriden by
   environment variables (where present). This is how settings are
   managed in Docker containers, http://12factor.net style.

"""
import os
import os.path
from envparse import env
import sys
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = env(
    'SECRET_KEY',
    default='this_is_not_a_real_secret_key_234db#1k2l#GfnGqn')
DEBUG = env('DEBUG', default=False)
ALLOWED_HOSTS = [
    '127.0.0.1', 'localhost',
    env('DJANGO_ALLOWED_HOST', default='presidentbusiness.com')]

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'celery',
    'haystack',
    'celery_haystack',
    'metadata',
    'govservices',
    'crawler',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'disco_service.urls'
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
WSGI_APPLICATION = 'disco_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': env(
            'DATABASE_DEFAULT_ENGINE',
            default='django.db.backends.sqlite3'),
        'NAME': env(
            'DATABASE_DEFAULT_NAME',
            default=os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': env('DATABASE_DEFAULT_USER', default=''),
        'PASSWORD': env('DATABASE_DEFAULT_PASSWORD', default=''),
        'HOST': env('DATABASE_DEFAULT_HOST', default=''),
        'PORT': env('DATABASE_DEFAULT_PORT', default=''),
    }
}
# use sqlite for testing
if 'test' in sys.argv or 'test_coverage' in sys.argv:
        DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

# default haystack is elasticsearch on localhost
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': env(
            'HAYSTACK_DEFAULT_ENGINE',
            default='haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine'),
        'URL': env(
            'HAYSTACK_DEFAULT_URL',
            default='http://127.0.0.1:9200/'),
        'INDEX_NAME': env(   # required by elasticsearch, ignored by solr
            'HAYSTACK_INDEX_NAME',
            default='haystack')
    },
}
BROKER_URL = env(
    'BROKER_URL',
    default='amqp://guest:guest@127.0.0.1/spiderbucket')

CRAWLER_HEARTBEAT_SECONDS = 300
# not working as expected
#CRAWLER_HEARTBEAT_SIZE = 100 # make it a large number when it's working OK
CELERYBEAT_SCHEDULE = {
    "periodically_insert_new_resources": {
        "task": "crawler.tasks.sync_from_crawler",
        "schedule": timedelta(seconds=CRAWLER_HEARTBEAT_SECONDS), 
        "args": ()  # CRAWLER_HEARTBEAT_SIZE,)
     },
    "periodically_update_changed_resources": {
        "task": "crawler.tasks.sync_updates_from_crawler",
        "schedule": timedelta(seconds=CRAWLER_HEARTBEAT_SECONDS), 
        "args": ()  # CRAWLER_HEARTBEAT_SIZE,) 
     },
}

CELERY_RESULT_BACKEND = env(
    'CELERY_RESULT_BACKEND',
    default='djcelery.backends.database:DatabaseBackend')
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']

### FIXME
#CELERY_TIMEZONE = 'Au/'
#CELERY_ENABLE_UTC = True
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

SERVICE_CATALOGUE_REPOSITORY_PATH = env(
    'SERVICE_CATALOGUE_REPOSITORY_PATH',
    default=os.path.join(BASE_DIR, '../../serviceCatalogue/'))
SERVICE_CATALOGUE_REPOSITORY_REMOTE = env(
    'SERVICE_CATALOGUE_REPOSITORY_REMOTE', default='origin')

HAYSTACK_SIGNAL_PROCESSOR = 'celery_haystack.signals.CelerySignalProcessor'
