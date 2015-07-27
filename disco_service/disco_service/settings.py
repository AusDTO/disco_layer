"""
https://docs.djangoproject.com/en/1.8/topics/settings/
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
import os
import os.path
from envparse import env

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
    'spiderbucket',
    'govservices',
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

'''
### CRAZY IDEA DEPARTMENT ###
Use multiple haystack connections for A/B (ANOVA) split testing i.e:
 * create multiple indexes, each with a different "treatment"
 * create a connection per index, and randomly assign them to sessions
 * analyse "scorecard performance" of each treatment condition
 * iterate:
    - drop poorly performing treatments
    - innovate new treatments...
    - innovate scorecard evaluations
 * stream experimental results into an event pipeline:
    - perform scorecard evaluation in near-real time.
    - use rules (statistical significance, sampling heuristics, etc.)
      to drive automatic blue/green deployment and rollback.

In other words, standardise on how we measure performance of the whole
discovery ecosystem (scorecard evaluation - like a headless dashboard),
and create a way to continuously monitor performance. Use this to
automatically manage the 'survival of the fittest' search index
treatments (in the extringic+intrinsic contexts, userland+codebase).
Then hack with inquisitive creativity, continuously trying to improve
the codebase, indexing treatment and instrumentation in concert.
'''
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
