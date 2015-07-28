"""
TODO:
    we do need to go the other way as well,
    delete from SOLR and the DB when page is "absent" from OrientDB
    and by absent, I mean flagged as missing (not available)
    or whatever (ask Nigel about business logic)

#def purge_url_rdbms(url):
"""
from celery import shared_task
from django.test import TestCase
from .models import Resource
from celery.utils.log import get_task_logger
import logging

class MultiplePagesWithSameURLError(Exception): pass
class InvalidPageDataError(Exception): pass
class InvalidPageIDError(Exception): pass

logger = logging.getLogger(__file__)
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(console)

class PageDictValidator(object):
    '''
    This captures/encapsulates our assumptions about the
    webDocumentContainer data in OrientDB
    '''
    REQUIRED_PROPERTIES = (
        'orient_rid', 'orient_version',
        'orient_class', 'url')
    ALLOWED_PROPERTIES = (
        'protocol', 'host', 'port',
        'depth', 'fetched', 'path',
        'status', 'lastFetchDateTime',
        'nextFetchDateTime', 'document')

    def valid(self, page):
        logger.debug('PageDictValidator: %s' % page)
        if type(page) != type ({}):
            return False
        for k in self.REQUIRED_PROPERTIES:
            if k not in page.keys():
                return False
        return True

    def invalid_reasons(self, page):
        if self.valid(page):
            return None
        else:
            out = []
            expected_properties = self.REQUIRED_PROPERTIES + self.ALLOWED_PROPERTIES
            for k in page.keys():
                if k not in expected_properties:
                    out.append('key "%s" found but not expected' % k)
            for k in self.REQUIRED_PROPERTIES:
                if k not in page.keys():
                    out.append('key "%s" REQUIRED but not found' % k)
            return out


@shared_task
def push_page_dict(page):
    '''
    Idempotently sync one page in RDBMS/Solr,
    
    presumably sourced from OrientDB following insert/update
    but we have rendered the data to a dict
    so there is no trace of pyorient anymore.
    '''
    pvd = PageDictValidator()
    if not pvd.valid(page):
        if 'document' in page.keys():
            if len(page['document']) > 100:
                page['document'] = page['document'][:100] + "... 8< chomped."
        raise InvalidPageDataError, page
    num_found = Page.objects.filter(url=page['url']).count()
    if num_found == 1:
        update_page_in_db.delay(page)
    elif num_found == 0:
        insert_page_in_db.delay(page)
    else:
        raise MultiplePagesWithSameURLError, page['url']

@shared_task
def update_page_in_db(page):
    pvd = PageDictValidator()
    if not pvd.valid(page):
        raise InvalidPageDataError, page
    p = Page.objects.get(url=page['url'])  # url is imutable
    dirty = False
    for prop in pvd.REQUIRED_PROPERTIES + pvd.ALLOWED_PROPERTIES:
        exec("m = p.%s" % prop)
        if prop in page.keys():
            if m != page[prop]:
                m = page[prop]
                dirty = True
        elif m is not None:
            m = None
            dirty = True
    if dirty:
        p.save()
    sync_page_sinks.delay(p.id)

@shared_task
def insert_page_in_db(page):
    pvd = PageDictValidator()
    if not pvd.valid(page):
        raise InvalidPageDataError, page
    p = Page(
        url = page['url'],
        orient_rid = page['orient_rid'],
        orient_version = page['orient_version'],
        orient_class = page['orient_class'],
    )
    if 'protocol' in page.keys():
        p.protocol = page['protocol']
    if 'host' in page.keys():
        p.host = page['host']
    if 'port' in page.keys():
        p.port = int(page['port'])
    if 'depth' in page.keys():
        p.depth = int(page['depth'])
    if 'fetched' in page.keys():
        p.fetched = page['fetched']
    if 'status' in page.keys():
        p.status = page['status']
    if 'lastFetchDateTime' in page.keys():
        p.lastFetchDateTime = page['lastFetchDateTime']
    if 'nextFetchDateTime' in page.keys():
        p.nectFetchDateTime = page['nextFetchDateTime']
    if 'document' in page.keys():
        p.document = page['document']
    p.save()
    pid = p.id
    sync_page_sinks.delay(pid)


class NulTask:
    '''
    like a @shared_task except won't burden the queue with a useless message 
    '''
    def init(self, page=None):
        pass
    @classmethod
    def delay(self, page):
        pass


class PageSyncSubscribers(object):
    '''
    This is a bit of a white elephant.

    I was synchronising Solr from here until I discovered this:
    https://github.com/django-haystack/celery-haystack/

    Now I'm just keeping this here in case I want to push/purge
    each delta to other sinks (e.g. tripplestore, event log,
    semantic agents). Or if I get cranky with celery-haystack.
    '''
    # this might be better in settings.py
    HARDCODED_CONFIG = (
        {
            'name':'solr',
            'push': 'NulTask',
            'delete': 'NulTask'
        },
    )

    def list_push_task_names(self):
        out = []
        for c in self.HARDCODED_CONFIG:
            out.append(c['push'])
        return out

    def list_push_tasks(self):
        out = []
        for taskname in self.list_push_task_names():
            eval("out.append(%s)" % taskname)
        return out

    def list_delete_task_names(self):
        out = []
        for c in self.HARDCODED_CONFIG:
            out.append(c['delete'])
        return out

    def list_delete_tasks(self):
        out = []
        for taskname in self.list_delete_task_names():
            eval("out.append(%s)" % taskname)
        return out

    def list_subscriber_names(self):
        out = []
        for c in self.HARDCODED_CONFIG:
            out.append(c['name'])
        return out

@shared_task
def sync_page_sinks(page_id):
    '''
    after updating a pages, dispatching a call to sync_page_sinks.
    
    This task provides indirection between database wrtites and consequent
    updates to downstream data sources. i.e. extensability pattern.

    PageSyncSubscribers is responsible for knowing who to dispatch to.

    As with harvest_celery, it might be better to drive this from signals.
    '''
    if type(page_id) != type(1):
        raise InvalidPageIDError, page_id
    pss = PageSyncSubscribers()
    if Page.objects.filter(pk=page_id).count() == 0:
        for t in pss.list_delete_tasks():
            t.delay(page_id)
    else:
        for t in pss.list_push_tasks():
            page = Page.objects.get(pk=page_id)
            t.delay(page)
