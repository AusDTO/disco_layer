#!/usr/bin/env python
import pyorient
import json
#from StringIO import StringIO
import base64
from goose import Goose

DBHOST='52.64.24.77'
DBPORT=2424
DBUSR='root'
DBPSX='developmentpassword'

client = pyorient.OrientDB(DBHOST, DBPORT)
session_id = client.connect(DBUSR, DBPSX)

#raw_dblist =client.db_list()
dbname = 'webContent'
client.db_open(dbname, DBUSR, DBPSX)

def _process_webdocument(wdc):
    '''for k in wdc.oRecordData.keys():
        if k != 'document':  # ugly binary, don't print
            print "%s: %s" % (k, wdc.oRecordData[k])
    print ''
    '''
    g = Goose()
    if 'url' in wdc.oRecordData.keys():
        if 'document' in wdc.oRecordData.keys():
            url = wdc.oRecordData['url'],
            content = base64.b64decode(wdc.oRecordData['document'])
            a = g.extract(raw_html = content)
            # push to DB - ASYNCRONOUSLY
            print url
            print a.cleaned_text
            print '-'*128
            print ''

# this should be a periodic task
result = client.query_async("select from webDocumentContainer", 6000, '*:0', _process_webdocument)
