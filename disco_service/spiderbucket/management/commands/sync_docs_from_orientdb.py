#-*- coding: utf-8; -*-
import logging
import pyorient
from django.core.management.base import BaseCommand, CommandError
from spiderbucket import tasks


class Command(BaseCommand):
    help = 'source documents from OrientDB, sink them into the RDBMS'

    def handle(self, *args, **options):
        #raise CommandError('Eek!')

        logger = logging.getLogger(__file__)
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(console)

        verbosity = int(options['verbosity'])
        #console.setLevel(logging.CRITICAL)
        if verbosity == 0:
            console.setLevel(logging.ERROR)
        elif verbosity == 1:
            console.setLevel(logging.WARNING)
        elif verbosity == 2:
            console.setLevel(logging.INFO)
        else:
            console.setLevel(logging.DEBUG)

        logger.debug("DEBUG sync_docs_from_orientdb command called with verbosity %s" % options['verbosity'])     
        logger.info("INFO sync_docs_from_orientdb command called with verbosity %s" % options['verbosity'])     
        logger.warning("WARNING sync_docs_from_orientdb command called with verbosity %s" % options['verbosity'])     
        logger.error("ERROR sync_docs_from_orientdb command called with verbosity %s" % options['verbosity'])     
        logger.critical("CRITICAL sync_docs_from_orientdb command called with verbosity %s" % options['verbosity'])     


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

        def _callback_sync_page_to_rdbms(wdc):
            # objects dispatched to workers must be serialisable
            # pyorient doesn't play nice with celery workers either,
            # so this command is the only place we interface OrientDB
            pd = {}
            expected_keys = (
                'url', 'protocol', 'host', 'port',
                'path', 'depth', 'fetched', 'status',
                'stateData', 'lastFetchDateTime',
                'nextFetchDateTime', 'document')
            for k in expected_keys:
                if k in wdc.oRecordData.keys():
                    pd[k] = "%s" % wdc.oRecordData[k]
                if set(expected_keys) == set(pd.keys()):
                    sync_page_dict_to_rdbms.delay(pd)
                    #tasks.sync_page_dict_to_rdbms(pd)  # DEBUG

        sql = 'select count(*) from webDocumentContainer where status="downloaded"'
        count = client.query(sql,1,'*:0')[0].oRecordData['count']
        self.stdout.write('%s docs to sync' % count)
        sql = 'select url, orient_rid, orient_version, orient_class protocol, host, port, path, depth, fetched, status, lastFetchDateTime, nextFetchDateTime, document from webDocumentContainer where status="downloaded"'
        client.query_async(sql, int(count), '*:0', _callback_sync_page_to_rdbms)
        # Dispatch war rocket AJAX to bring back his body.
        self.stdout.write('doc sync fully dispatched')
        

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
