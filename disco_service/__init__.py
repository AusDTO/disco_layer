"""
Package: disco_service
======================

This is a django project, containing the usual settings.py, urls.py and wsgi.py 

.. note::

   Also contains `celery.py`, which is configuration for async worker nodes

"""

from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_ap

