from __future__ import absolute_import
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
# this should be pulled in from environment slightly differently (12 factors)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disco_service.settings')

from django.conf import settings
app = Celery('disco_service')

# Using a string here means the worker will not have to
# pickle the object when using Windows. (who cares)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
        print('Request: {0!r}'.format(self.request))
