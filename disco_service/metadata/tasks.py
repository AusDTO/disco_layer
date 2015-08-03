from celery import shared_task
from .models import Resource

@shared_task
def insert_resource_from_row(row):
    r = Resource()
    r.url = row[0]
    r._hash = row[1]
    r.protocol = row[2]
    r.contenttype = row[3]
    r.host = row[4]
    r.port = row[5]
    r.path = row[6]
    r.depth = row[7]
    r.lastFetchDateTime = row[8]
    r.save()

