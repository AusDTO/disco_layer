"""
crawler.models
==============

An ORM interface to the DB which is shared with the disco_crawler node.js app. 

.. autoclass:: WebDocument
"""
from __future__ import unicode_literals
from django.db import models


class WebDocument(models.Model):
    """
    Resource downloaded by the disco_crawler node.js app.

    The document attribute is a copy of the resource which was downloaded.

    url uniquely defines the resource (there is no numeric primary key). 
    host, path, port and protocol are attributes about the HTTP request
    used to retrieve the resource. lastfetchdatetime and nextfetchdatetime
    are heuristically determined and drive the behavior of the crawler. _hash
    is indexed and has a coresponding attribute in the metadata.Resource class
    (these are compared to determine if the metadata is dirty).

    The rest of the attributes are derived from the content of the document.
    """
    url = models.TextField(primary_key=True)
    host = models.CharField(max_length=255, blank=True, null=True)
    document = models.BinaryField(blank=True, null=True)
    lastfetchdatetime = models.DateTimeField(db_column='lastFetchDateTime', blank=True, null=True)  # Field name made lowercase.
    nextfetchdatetime = models.DateTimeField(db_column='nextFetchDateTime', blank=True, null=True)  # Field name made lowercase.
    path = models.TextField(blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    protocol = models.CharField(max_length=255, blank=True, null=True)
    httpcode = models.IntegerField(db_column='httpCode', blank=True, null=True)  # Field name made lowercase.
    contenttype = models.CharField(db_column='contentType', max_length=255, blank=True, null=True)  # Field name made lowercase.
    statedata = models.TextField(db_column='stateData', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    fetchstatus = models.CharField(db_column='fetchStatus', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fetched = models.NullBooleanField()
    outlinks = models.TextField(blank=True, null=True)  # This field type is a guess.
    _hash = models.CharField(db_column='hash', max_length=255, blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'webDocuments'
