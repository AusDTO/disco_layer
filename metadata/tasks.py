"""
metadata.tasks
==============

.. autofunction:: metadata.tasks.insert_resource_from_row

.. autofunction:: metadata.tasks.update_resource_from_row

"""

from celery import shared_task
from .models import Resource

@shared_task
def insert_resource_from_row(row):
    """ Wrap metadata.Resource constructor

    Stupidly, doesn't even do any input validation.
    """
    r = Resource()
    r.url = row[0]
    r._hash = row[1]
    r.protocol = row[2]
    r.contenttype = row[3]
    r.host = row[4]
    r.port = row[5]
    r.path = row[6]
    r.lastFetchDateTime = row[7]
    r.save()


@shared_task
def delete_resource_with_url(url):
    """ wrap metadata.Resource destructor.

    another one without input validation!
    """
    r = Resource(url=url)
    r.delete()


@shared_task
def update_resource_from_row(row):
    """ ORM lookup then update
    
    No input validation and foolishly assumes the lookup won't miss.
    """
    r = Resource(url=row[0])
    r._hash = row[1]
    r.protocol = row[2]
    r.contenttype = row[3]
    r.host = row[4]
    r.port = row[5]
    r.path = row[6]
    r.lastFetchDateTime = row[7]
    r.save()
    
