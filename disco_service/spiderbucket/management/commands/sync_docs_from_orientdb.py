#-*- coding: utf-8; -*-
import logging
import pyorient
from django.core.management.base import BaseCommand, CommandError
from spiderbucket import tasks
import datetime

# logLevel set in handler, but logger defined 
# out here so other things can use it
logger = logging.getLogger(__file__)
console = logging.StreamHandler()
console.setFormatter(
    logging.Formatter('%(message)s'))
logger.addHandler(console)

'''
def callback_sync_page_to_rdbms(wdc):
    # objects dispatched to workers must be serialisable
    # pyorient doesn't play nice with celery workers either,
    # so this command is the only place we interface OrientDB
    pd = {}
    expected_keys = (
        'url', 'protocol', 'host', 'port',
        'path', 'depth', 'fetched', 'status',
        #'stateData',
        'lastFetchDateTime',
        'nextFetchDateTime', 'document')
    for k in expected_keys:
        if k in wdc.oRecordData.keys():
            pd[k] = "%s" % wdc.oRecordData[k]

    # validate keys
    if set(expected_keys) != set(pd.keys()):
        logger.warn('refuse to sync page, pd.keys() != expected_keys')
        for k in pd.keys():
            if k not in expected_keys:
                msg = '%s in pd.keys() but not in expected_keys'
                logger.debug(msg % k)
            for k in expected_keys:
                if k not in pd.keys():
                    msg = '%s in expected_keys but not in pd.keys()'
                    logger.debug(msg % k)
    else:
        msg = 'about to try and sync_page_dict_to_rdbms for %s'
        logger.debug(msg % pd['url'])
        #sync_page_dict_to_rdbms.delay(pd)
        tasks.sync_page_dict_to_rdbms(pd)
'''

def process_wdc(wdc):
    out = {}
    for k in wdc.oRecordData.keys():
        out[k] = "%s" % wdc.oRecordData[k]
    logger.debug('about to dispatch push_page_dict("%s")' % out['url'])
    return tasks.push_page_dict(out)


class Command(BaseCommand):
    help = 'source documents from OrientDB, sink them into the RDBMS'

    def handle(self, *args, **options):
        #raise CommandError('Eek!')
        verbosity = int(options['verbosity'])
        if verbosity == 0:
            loglevel =logging.ERROR
        elif verbosity == 1:
            loglevel = logging.WARNING
        elif verbosity == 2:
            loglevel = logging.INFO
        else:
            loglevel = logging.DEBUG
    
        console.setLevel(loglevel)
        logger.setLevel(loglevel)

        ### TODO: get from environment variables
        DBHOST = "52.64.24.77"
        DBPORT = 2424
        DBUSR =  "root"
        DBPSX = "developmentpassword"
        DBNAME = "webContent"

        # orient client
        client = pyorient.OrientDB(DBHOST, DBPORT)
        client.connect(DBUSR, DBPSX)
        client.db_open(DBNAME, DBUSR, DBPSX, pyorient.DB_TYPE_DOCUMENT, "")

        sql = '''select count(*) from webDocumentContainer where status="downloaded"'''
        result = client.query(sql,1,'*:0')
        count = result[0].oRecordData['count']
        logger.info('%s docs to sync' % count)
        sql = 'select url, @rid as orient_rid, @version as orient_version, @class as orient_class, protocol, host, port, path, depth, fetched, status, lastFetchDateTime, nextFetchDateTime, document from webDocumentContainer where status="downloaded"'
        #if hasattr(process_wdc, '__call__'):
        #    client.query_async(sql, int(count), '*:0', process_wdc)
        #else:
        #    raise Exception, dir(process_wdc)
        client.query_async(sql, int(count), '*:0', process_wdc)

'''
        if '__call__' in dir(_callback_sync_page_to_rdbms):
            logger.debug('about to dispatch query: %s' % sql)
            client.query_async(
                sql, int(count), '*:0',
                callback_sync_page_to_rdbms)
        else:
            msg = 'unable to dispatch query, callback is uncallable'
            logger.critical(msg)
        logger.info('finished dispatching sync_docs_from_orientdb')
'''

if __name__ == "__main__":
    urls = (
        "http://2commando.gov.au/",
        "http://aao.gov.au/",
        "http://aat.gov.au/",
        "http://aa.gov.au/",
        "http://abcb.gov.au/",
        )
    # mock
    def f(x):
        print "DEBUG: %s" % x
    # monkey patch
    #tasks.sync_page_to_rdbms_from_orient = f
    for u in urls:
        page = {'url': u}
        tasks.sync_page_to_rdbms_from_orient(page)
