"""
crawler.tasks
=============

This module contains integration tasks for synchronising this DB with the metadata used in the rest of the discovery layer.

.. autofunction:: sync_from_crawler

.. autofunction:: sync_updates_from_crawler

"""
from celery import shared_task
from django.db import connection
from .models import WebDocument
from metadata.tasks import insert_resource_from_row

@shared_task
def sync_from_crawler(limit=1000):
    """dispatch metadata.Resource inserts for **new** crawler.WebDocuments"""
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
def sync_updates_from_crawler(limit=1000):
    """dispatch metadata.Resource updates for **changed** crawler.WebDocuments"""
    raw_sql = '''
        select
            url, _hash, protocol, contenttype,
            host, port, path, depth, "lastFetchDateTime"
        from
            "webDocuments" as wd,
            metadata_resource as mr
        where wd."fetchStatus" = 'downloaded'
        and wd.url = mr.url
        and wd._hash != mr._hash
        '''
    if limit is not None:
        raw_sql += ' limit = %s' % int(limit)
        cursor = connection.cursor()
        cursor.execute(raw_sql)
        for row in cursor:
            update_resource_from_row.delay(row)
