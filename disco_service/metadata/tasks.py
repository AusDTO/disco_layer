from celery import shared_task
from django.db import connection # not often needed
from .models import Resource
from crawler.models import WebDocument
#from celery.utils.log import get_task_logger
#import logging

@shared_task
def sync_from_crawler(limit=1000):
    raw_sql = '''
        select
            url, _hash, protocol, contenttype,
            host, port, path, depth, "lastFetchDateTime"
        from "webDocuments"
        where "fetchStatus" = 'downloaded'
        and url not in (
            select url
            from metadata_resource
        )'''
    if limit is not None:
        raw_sql += ' limit = %s' % int(limit)
    cursor = connection.cursor()
    cursor.execute(raw_sql)
    for row in cursor:
        insert_resource_from_row.delay(row)

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

