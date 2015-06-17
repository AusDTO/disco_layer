from __future__ import absolute_import
import pyorient
import json
import base64
from celery import shared_task
from .models import Page

class ODBWrapper:
    # this should be coming from settings!
    DBHOST='52.64.24.77'
    DBPORT=2424
    DBUSR='root'
    DBPSX='developmentpassword'
    DBNAME = 'webContent'
    client = pyorient.OrientDB(DBHOST, DBPORT)
    client.db_open(DBNAME, DBUSR, DBPSX)
    
    def __init__(self):
        self.client = ODBWrapper.client
    
    def all_webDocumentContainers_callback(self, count, callback):
        self.client.query_async("select from webDocumentContainer", count, '*:0', callback)    
    
    def count_webdocumentContainers(self, url):
        query = "select count(*) from webDocumentContainer where url=\"http://google.com/\""# % url
        result = self.client.query(query, 1, '*:0')
        return result[0].oRecordData['count']

    def count_all_records(self):
        return self.client.db_count_records()

class RDBMSWrapper:
    def __init__(self):
        self.foo = 'BAR'
    def page_with_url_exists(self, page_url):
        num_found = Page.objects.filter(url=page_url).count()
        if num_found > 0:
            return True
        else:
            return False
    
@shared_task
def sync_url_from_orient(url):
    ''' Idempotently sync one page in RDBMS/Solr from OrientDB
    
        e.g. following document insert/update in OrientDB
    '''
    ow = ODBWrapper()
    if ow.count_webdocumentContainers(url) == 0:
        # corner-case: page absent from OrientDB
        purge_url_rdbms.delay(url)
        purge_url_solr.delay(url)
    else:
        rdb = RDBMSWrapper()
        if rdb.page_with_url_exists(url):
            rdbms_id = rdb.update_page('foo')
        else:
            rdbms_id = rdb.insert_page('foo')
        sync_solr_from_rdbms.delay(rdbms_id)


@shared_task
def purge_url_rdbms(url):
    ''' Delete document from RDBMS after deletion from OrientDB '''
    ## GUARD CONDITION
    # if a document exists in OrientDB with that url:
    #   fail! dispatch sync_url_from_orient(url)
    ## LAZY is good
    # else if the document does not exist in the RDBMS:
    #   do nothing
    # else:
    #   delete it
    #   purge_solr_url(url)
    print "TODO: purge_url_rdbms(%s)" % url
    pass

@shared_task
def sync_solr_from_rdbms(rdbms_document_id):
    ''' Ensure solr is up to date with the RDBMS, for the given document'''
    print "TODO: sync_solr_from_rdbms(%s)" % rdbms_document_id

@shared_task
def purge_url_solr(url):
    ''' remove the document with given url from solr '''
    print "TODO: purge_url_solr(%s)" % url


@shared_task
def sync_the_db(limit=None):
    ''' A periodic task that syncs the RDBMS from OrientDB

    Obsolete when we have OriendDB making a callback to a web method.

    Intended to be called on a schedule (e.g. by celerybeat)
    '''
    ### do this bit now
    # for each document in OrientDB that should be in the database:
    #    dispatch a job to ensure it is valid in the DB

    ### do this bit later
    # for each service in the catalogue (?)
    #    dispatch a job to ensure it is valid in the DB
    def _process_webdocument(wdc):
        ''' this is stupid. I'm given an object,
            I pick it's ID, and dispatch that to an async
            task that uses the ID to retrieve the same object again.

            would be smarter to pass this guy an ID only
        '''
        if 'url' in wdc.oRecordData.keys():
            if 'document' in wdc.oRecordData.keys():
                url = wdc.oRecordData['url']
                doc_sync_orient_cru.delay(url)
    ow = ODBWrapper()
    if not limit:
        limit = 2+ow.count_all_records()
    ow.all_webDocumentContainers_callback(limit, _process_webdocument)

