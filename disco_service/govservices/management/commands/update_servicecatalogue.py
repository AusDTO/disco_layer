#-*- coding: utf-8; -*-
from django.core.management.base import BaseCommand, CommandError
from spiderbucket import tasks
from django.conf import settings
import git
import git.remote
import os
import json
import govservices

class ServiceJsonRepository(object):
    def __init__(self, repo_path, remote_name):
        # Maybe this constructor is redundant.
        # what if this management command was called by jenkins :)
        # less is more...

        # error if the repo doesn't exits
        self.repo_path = repo_path
        self._repo = git.Repo(repo_path)
        assert not self._repo.is_dirty()
        self.remote_name = remote_name
        self._remote = None
        found = False
        for r in self._repo.remotes:
            if "%s" % r == remote_name:
                found = True
                self._remote = r
        if not found:
            msg = "failed to find remote (%s) in repositorty (%s)"
            raise Exception, msg % (repo_remote, repo_path)
        # DEBUG
        ### this hangs...
        #remote.pull(progress=rp)
        # fetch the repo, discover changes
        # exit if no changes
        # ### what to do if working in that repo? don't do that, use a dedicated one
        # ### which branch (new config var)        

    def agency_service_json(self):
        try:
            out = self._agency_service_json_tuples
            #print "DEBUG agency_service_json - cache hit (%s found)" % len(out)
            return out
        except:
            #print "DEBUG agency_service_json - cache miss"
            out = []
            for agency in self.list_agencies():
                for jsonfname, jsonpayload in self.list_agency_jsonfiles(agency):
                    out.append((agency, jsonfname, jsonpayload))
            self._agency_service_json_tuples = out
            return out

    def list_agency_jsonfiles(self, agency):
        if agency not in self.list_agencies():
            msg = "%s not in list of agencies: %s"
            raise Exception, msg % (agency, self.list_agencies())
        try:
            out = self._agency_service_json_tuples
            #print "DEBUG list_agency_jsonfiles - cache hit (%s found)" % len(out)
            return out
        except:
            #print "DEBUG list_agency_jsonfiles - cache miss"
            out = []
            agency_path = os.path.join(self.repo_path, agency)
            for f in os.listdir(agency_path):
                name = os.path.join(agency_path, f)
                if not os.path.isdir(name):
                    jsonfilename = f
                    jsonpayload = json.loads(open(name).read())
                    out.append((jsonfilename, jsonpayload))
            self._agency_service_json_tuples = out
            return out

    def list_agencies(self):
        try:
            out = self._agencies
            return out
        except:
            out = []
            notagencies = ('lists', 'genService', '.git')
            for d in os.listdir(self.repo_path):
                agency_path = os.path.join(self.repo_path, d)
                if d not in notagencies and os.path.isdir(agency_path):
                    out.append(d)
            self._agencies = out
            return out

    def list_subservices(self):
        try:
            out = self._subservices
            return out
        except:
            subservices = []
            for agency, filename, jsonpayload in self.agency_service_json():
                for k in jsonpayload.keys():
                    if k == u'subService':
                        list_of_subservices = jsonpayload[k]
                        if len(list_of_subservices) > 0:
                            for subservice in list_of_subservices:
                                # delete none-valued properties, they
                                # mess up database comparison (bug)
                                for k in subservice.keys():
                                    if subservice[k] is None:
                                        del(subservice[k])
                                if subservice not in subservices:
                                    subservices.append(subservice)
            self._subservices = subservices
            return subservices

    def list_service_tags(self):
        try:
            out = self._service_tags
            #print "DEBUG list_service_tags - cache hit (%s found)" % len(out)
            return out
        except:
            #print "DEBUG list_service_tags - cache miss"
            out = []
            for a, f, jsonpayload in self.agency_service_json():
                service = jsonpayload['service']
                for k in ("tags", "tags:"):
                    if k in service.keys():
                        for tag in service[k]:
                            #print "DEBUG list_service_tags: scan saw '%s'" % tag
                            if tag not in out:
                                #print "DEBUG list_service_tags: cache add '%s'" % tag
                                out.append(tag)
            self._service_tags = out
            return out

    def list_life_events(self):
        try:
            out = self._life_events
            #print "DEBUG list_life_events - cache hit (%s found)" % len(out)
            return out
        except:
            #print "DEBUG list_life_events - cache miss"
            out = []
            for a, f, jsonpayload in self.agency_service_json():
                service = jsonpayload['service']
                if 'lifeEvents' in service.keys():
                    for le in service['lifeEvents']:
                        #print "DEBUG list_life_events: scan saw '%s'" % le
                        if le not in out:
                            #print "DEBUG list_life_events: cache add '%s'" % le
                            out.append(le)
            self._life_events = out
            return out

class Command(BaseCommand):
    help = 'source service specification (json) from Github, then update the DB as required'

    def handle(self, *args, **options):
        #raise CommandError('Eek!')
        repo_path = settings.SERVICE_CATALOGUE_REPOSITORY_PATH
        repo_remote = settings.SERVICE_CATALOGUE_REPOSITORY_REMOTE


        # OK, we have change to process
        # 1. load all of the json into RAM
        sjr = ServiceJsonRepository(repo_path, repo_remote)
        '''
        notagencies = ('lists', 'genService', '.git')
        agencies = {}
        for d in os.listdir(repo_path):
            agency_path = os.path.join(repo_path, d)
            if d not in notagencies and os.path.isdir(agency_path):
                agencies[d] = {}
                for f in os.listdir(agency_path):
                    name = os.path.join(agency_path, f)
                    if not os.path.isdir(name):
                        agencies[d][f] = json.loads(open(name).read())
        '''

        #
        # now we inspect it to design the ORM class
        #
        tld = []
        dim_keys = []
        services = []
        service_keys = []
        service_keys_count = {}
        service_keys_examples = {}
        service_types = [] # todo
        doctypes = []
        subservices=[]
        subservice_keys = []
        subservice_keys_count = {}
        subservice_examples = {}
        service_tags = []
        #for ak in agencies.keys():
            #for s in agencies[ak]:
        counter = 0
        for a, s, jsonpayload in sjr.agency_service_json():
            counter += 1
            for k in jsonpayload.keys():
                if k not in tld:
                    tld.append(k)
                if k == 'Subs':
                    # subs seem always empty?
                    if jsonpayload[k] != []:
                        msg = "DISCOVERY! (%s: %s: %s)"
                        print msg % (ak, s[:-5], jsonpayload[k])
                elif k == 'todo':
                    pass  # not interesting
                elif k == u'Dimension':
                    dim_list = jsonpayload[k]
                    for dim in dim_list:
                        for dk in dim.keys():
                            if dk not in dim_keys:
                                dim_keys.append(dk)
                elif k == u'service':
                    srv = jsonpayload[k]
                    for sk in srv.keys():
                        if sk not in service_keys:
                            service_keys.append(sk)
                            service_keys_count[sk] = 1
                            service_keys_examples[sk] = srv[sk]
                        else:
                            service_keys_count[sk] += 1
                        if srv[sk] not in (None, [], ''):
                            try:
                                service_keys_example[sk] = srv[sk]
                            except:
                                pass
                        # service tags
                        if sk in ("tags", "tags:"):
                            for st in srv[sk]:
                                if st not in service_tags:
                                    service_tags.append(st)
                elif k == u'documentType':
                    dt = jsonpayload[k]
                    if dt not in doctypes:
                        doctypes.append(dt)
                if k == u'subService':
                    sss = jsonpayload[k]
                    if len(sss) > 0:
                        for ss in sss:
                            if ss not in subservices:
                                subservices.append(ss)
                                for k in ss.keys():
                                    if k not in subservice_keys:
                                        subservice_keys.append(k)
                                        subservice_keys_count[k]=1
                                        subservice_examples[k] = ss[k]
                                    else:
                                        subservice_keys_count[k] += 1
                                    if '%s' % ss[k] != '':
                                        subservice_examples[k] = ss[k]
        #
        #
        print "DEBUG counter: %s" % counter
        print "top level: %s" % tld
        print ''
        # dimmension
        '''
        print "dim_keys: %s" % dim_keys
        print "dim example:"
        for dk in dim.keys():
            try:
                if len(dim[dk]) > 50:
                    dim[dk] = dim[dk][:50] + '...'
            except:
                pass
            print "  %s: %s" % (dk, dim[dk])
        print ''
        '''
        # service (analysis)
        #
        # the purpose of this next blck of code is to reveal (print to screen)
        # those parts of the service json structure that is yet to be bound
        # to the ORM (and synched with it, etc).
        #
        print 'service_keys'
        print "service example:"
        ignore = ('tags', 'tags:', 'TODO', 'TODO:')
        for sk in service_keys:
            if sk not in ignore:
                val = None
                val = service_keys_examples[sk]
                if type(val) == type('') and len(val) > 50:
                    val = val[:50] + '...' 
                print "    %s (%s)" % (sk, service_keys_count[sk]),
                if val:
                    print "type: %s, example: %s" % (type(val), val)
                else:
                    print ''
        
        # a. generate text analysis from json
        # b. generate dot, visualise...
        # c. generate Model.model subclasses
        # d. break it into separate commands
        # e. separate service catalogue app!
        # f. build script (bootstrap self from repo).
        # g. generate haystack index

        #
        # sync subservices
        #
        db_subservices = []
        for ss in govservices.models.SubService.objects.all():
            ss_dict = { 
                'name': ss.name,
                'id': ss.cat_id,
                'desc': ss.desc,
                'infoUrl': ss.info_url,
                'primaryAudience': ss.primary_audience}
            # delete None-valued elements
            for k in ss_dict.keys():
                if ss_dict[k] is None:
                    del(ss_dict[k])
            db_subservices.append(ss_dict)

        # upsert subservices
        for ss in sjr.list_subservices():
            # validation: exception if we have two non-identical subservices
            num_matched = 0
            for ss2 in sjr.list_subservices():
                if ss2['id'] == ss['id']:
                    if ss2 != ss:
                        msg = "json corpus contains non-identical specifications"
                        msg += " of the same subservice \n\n %s\n\n %s"
                        raise Exception, msg % (ss, ss2)
            # compare this json object with the DB object
            found_in_db = False
            for dbss in db_subservices:
                if dbss['id'] == ss['id']:
                    found_in_db=True
                    num_match=0
                    for k in ('name', 'id', 'desc', 'infoUrl', 'primaryAudience'):
                        try:
                            if dbss[k] == ss[k]:
                                num_match += 1
                        except:
                            pass
                    if num_match == len(ss):
                        found_in_db_same = True
                    else:
                        found_in_db_same = False

            if not found_in_db:  # then insert it
                if 'desc' not in ss.keys():
                    ss['desc']='no description'
                gss = govservices.models.SubService(
                    cat_id=ss['id'],
                    desc=ss['desc'],
                    name=ss['name'])
                if 'infoUrl' in ss.keys():
                    gss.info_url=ss['infoUrl']
                if 'primaryAudience' in ss.keys():
                    gss.primary_audience=ss['primaryAudience']
                gss.save()

            if found_in_db and not found_in_db_same:  # then update it
                u = govservices.models.SubService.objects.get(cat_id=ss['id'])
                u.desc = ss['desc']
                u.name=ss['name']
                if 'infoUrl' in ss.keys():
                    u.info_url=ss['infoUrl']
                if 'primaryAudience' in ss.keys():
                    u.primary_audience=ss['primaryAudience']
                u.save()
        
        # if it's in the DB but NOT in the json, then delete it
        for dbss in govservices.models.SubService.objects.all():
            found_in_json = False
            for ss in sjr.list_subservices():
                if ss['id'] == dbss.cat_id:
                    found_in_json = True
            if not found_in_json:
                dbss.delete()

        #
        # service tags
        #
        # tags are only labels with identifiers, they can not change
        # (by definition; that's a new tag)
        service_tags = sjr.list_service_tags()
        db_servicetags = []
        for st in govservices.models.ServiceTag.objects.all():
            db_servicetags.append(st.label)
        # if found in json but not in DB, insert into DB 
        for st in service_tags:
            found_in_db = False
            for st2 in db_servicetags:
                if st2 == st:
                    found_in_db = True
            if not found_in_db:
                govservices.models.ServiceTag(label=st).save()
        # if found in DB but absent from json, delete from DB
        for st in db_servicetags:
            found_in_json = False
            for st2 in service_tags:
                if st2 == st:
                    found_in_json = True
            if not found_in_json:
                govservices.models.ServiceTag.objects.get(label=st).delete()

        #
        # life events
        #
        # like tags, only inserted/deleted (not updated)
        json_life_events = sjr.list_life_events()
        db_life_events = []
        for dble in govservices.models.LifeEvent.objects.all():
            db_life_events.append(dble.label)
        # if found in json but not DB, insert to DB
        for json_le in json_life_events:
            found_in_db = False
            for db_le in db_life_events:
                if json_le == db_le:
                    found_in_db = True
            if not found_in_db:
                govservices.models.LifeEvent(label=json_le).save()
        # if found in DB but not in JSON, delete from DB
        for db_le in db_life_events:
            found_in_json = False
            for json_le in json_life_events:
                if json_le == db_le:
                    found_in_json = True
            if not found_in_json:
                govservices.models.LifeEvent.objects.get(label=st).delete()


if __name__ == "__main__":
    # test here now,
    # but move it to tests.py later
    pass
