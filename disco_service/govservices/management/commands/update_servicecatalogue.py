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
    def __init__(self, json_path):
        self.json_path = json_path

    def agency_service_json(self):
        try:
            out = self._agency_service_json_tuples
            return out
        except:
            out = []
            for agency in self.list_agencies():
                agency_jsonfiles = self.list_agency_jsonfiles(agency)
                #for j, p in agency_jsonfiles:
                #    #print "DEBUG agency_service_json: %s, %s" % (agency, j) 
                for jsonfname, jsonpayload in agency_jsonfiles:
                    out.append((agency, jsonfname, jsonpayload))
            self._agency_service_json_tuples = out
            return out

    def list_agency_jsonfiles(self, agency):
        if agency not in self.list_agencies():
            msg = "%s not in list of agencies: %s"
            raise Exception, msg % (agency, self.list_agencies())
        out = []
        agency_path = os.path.join(self.json_path, agency)
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
            for d in os.listdir(self.json_path):
                agency_path = os.path.join(self.json_path, d)
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
            return out
        except:
            out = []
            for a, f, jsonpayload in self.agency_service_json():
                service = jsonpayload['service']
                for k in ("tags", "tags:"):
                    if k in service.keys():
                        for tag in service[k]:
                            if tag not in out:
                                out.append(tag)
            self._service_tags = out
            return out

    def list_life_events(self):
        try:
            out = self._life_events
            return out
        except:
            out = []
            for a, f, jsonpayload in self.agency_service_json():
                service = jsonpayload['service']
                if 'lifeEvents' in service.keys():
                    for le in service['lifeEvents']:
                        if le not in out:
                            out.append(le)
                if 'LifeEvents' in service.keys(): # alternate spelling
                    for le in service['LifeEvents']:
                        if le not in out:
                            out.append(le)
                
            self._life_events = out
            return out

    def list_service_types(self):
        try:
            out = self._service_types
            return out
        except:
            out = []
            for a, f, jsonpayload in self.agency_service_json():
                service = jsonpayload['service']
                for k in ('serviceTypes', 'ServiceTypes'):
                    if k in service.keys():
                        for st in service[k]:
                            if st not in out:
                                out.append(st)
            self._service_types = out
            return out

    def list_services(self):
        out = []
        for a, f, jsonpayload in self.agency_service_json():
            service = jsonpayload['service']
            service['json_filename'] = f
            service['org_acronym'] = a
            if service not in out:
                out.append(service)
            # else - why are there duplicates?
            # DEBUG
            #if 'serviceTypes' in service.keys():
            #    print service['serviceTypes']
        return out

class Command(BaseCommand):
    help = 'source service specification (json) from Github, then update the DB as required'

    def handle(self, *args, **options):
        #raise CommandError('Eek!')
        repo_path = settings.SERVICE_CATALOGUE_REPOSITORY_PATH
        repo_remote = settings.SERVICE_CATALOGUE_REPOSITORY_REMOTE

        # 1. load all of the json into RAM
        sjr = ServiceJsonRepository(repo_path, repo_remote)

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
                govservices.models.LifeEvent.objects.get(label=db_le).delete()

        #
        # servce types
        #
        # another tag-like property
        json_service_types = sjr.list_service_types()
        db_service_types = []
        for dbst in govservices.models.ServiceType.objects.all():
            db_service_types.append(dbst.label)
        # if found in json but not DB, insert to DB
        for json_st in json_service_types:
            found_in_db = False
            for db_st in db_service_types:
                if json_st == db_st:
                    found_in_db = True
            if not found_in_db:
                govservices.models.ServiceType(label=json_st).save()
        # if found in DB but not in JSON, delete from DB
        for db_st in db_service_types:
            found_in_json = False
            for json_st in json_service_types:
                if json_st == db_st:
                    found_in_json = True
            if not found_in_json:
                govservices.models.ServiceType.objects.get(label=db_st).delete()

        #
        # services themselves
        #
        json_services = sjr.list_services()
        db_services = []
        for dbs in govservices.models.Service.objects.all():
            sdict = {
                'oldID': dbs.old_src_id,
                'org_acronym': dbs.org_acronym,
                'json_filename': dbs.json_filename,
                'infoUrl': dbs.info_url,
                'name': dbs.name,
                'acronym': dbs.acronym,
                'tagline': dbs.tagline,
                'primaryAudience': dbs.primary_audience,
                'analyticsAvailable': dbs.analytics_available,
                'incidental': dbs.incidental,
                'secondary': dbs.secondary,
                'type': dbs.src_type,
                'description': dbs.description,
                'id': dbs.src_id,
            }
            
            for st in dbs.service_types.all():
                k = 'serviceTypes'
                if k not in sdict.keys():
                    sdict[k] = []
                sdict[k].append("%s" % st)
            for tg in dbs.service_tags.all():
                k = 'tags'
                if k not in sdict.keys():
                    sdict[k] = []
                sdict[k].append(tg)
            for le in dbs.life_events.all():
                k = 'lifeEvents'
                if k not in sdict.keys():
                    sdictp[k] = []
                sdict[k].append(le)
            db_services.append(sdict)

        # if found in json but not DB, insert to DB
        for s in json_services:
            found_in_db = False
            for dbs in db_services:
                if dbs['id'] == s['id']:
                    found_in_db=True
                    num_match=0
                    for k in s.keys():
                        if k in dbs.keys():
                            if dbs[k] == s[k]:
                                num_match += 1
                    if num_match == len(s):
                        found_in_db_same = True
                    else:
                        found_in_db_same = False

            if not found_in_db:  # then insert it
                gs = govservices.models.Service(src_id = s['id'])
                gs.org_acronym = s['org_acronym']
                gs.json_filename = s['json_filename']
                if 'oldID' in s.keys():
                    gs.old_src_id = s['oldID']
                if 'infoUrl' in s.keys():
                    if s['infoUrl'] != '':
                        gs.info_url = s['infoUrl']
                if 'name' in s.keys():
                    gs.name = s['name']
                if 'acronym' in s.keys():
                    gs.acronym = s['acronym']
                if 'tagline' in s.keys():
                    gs.tagline = s['tagline']
                if 'primaryAudience' in s.keys():
                    gs.primaryAudience = s['primaryAudience']
                if 'analyticsAvailable' in s.keys():
                    gs.analyticsAvailable = s['analyticsAvailable']
                if 'incidental' in s.keys():
                    gs.incidental = s['incidental']
                if 'secondary' in s.keys():
                    gs.secondary = s['secondary']
                if 'type' in s.keys():
                    gs.src_type = s['type']
                if 'description' in s.keys():
                    gs.description = s['description']
                if 'id' in s.keys():
                    gs.src_id = s['id']
                gs.save()
                # service types
                if 'serviceTypes' in s.keys():
                    for st in s['serviceTypes']:
                        dbst = govservices.models.ServiceType.objects.get(label=st)
                        gs.service_types.add(dbst)
                    gs.save()
                # service tags
                alternate_tag_spellings = ('tags', 'tags:')
                for k in alternate_tag_spellings:
                    if k in s.keys():
                        for st in s[k]:
                            dbst = govservices.models.ServiceTag.objects.get(label=st)
                            gs.service_tags.add(dbst)
                        gs.save()
                # life events
                alternate_life_event_spellings = ('lifeEvents', 'LifeEvents')
                for k in alternate_life_event_spellings:
                    if k in s.keys():
                        for le in s[k]:
                            dble = t = govservices.models.LifeEvent.objects.get(label=le)
                            gs.life_events.add(dble)
                        gs.save()
                
            if found_in_db and not found_in_db_same:  # then update it
                u = govservices.models.Service.objects.get(src_id=s['id'])
                u.org_acronym = s['org_acronym']
                u.json_filename = s['json_filename']
                if 'oldID' in s.keys():
                    u.old_src_id = s['oldID']
                if 'infoUrl' in s.keys():
                    if s['infoUrl'] != '':
                        u.info_url = s['infoUrl']
                if 'name' in s.keys():
                    u.name = s['name']
                if 'acronym' in s.keys():
                    u.acronym = s['acronym']
                if 'tagline' in s.keys():
                    u.tagline = s['tagline']
                if 'primaryAudience' in s.keys():
                    u.primary_audience = s['primaryAudience']
                if 'analyticsAvailable' in s.keys():
                    u.analytics_available = s['analyticsAvailable']
                if 'incidental' in s.keys():
                    u.indicental = s['incidental']
                if 'secondary' in s.keys():
                    u.secondary = s['secondary']
                if 'type' in s.keys():
                    u.src_type = s['type']
                if 'description' in s.keys():
                    u.description = s['description']
                if 'id' in s.keys():
                    u.src_id = s['id']
                #if 'serviceTypes' in s.keys():
                #    s.'serviceTypes': s.service_types, # M:N
                #if '' in s.keys():
                #    s.'tags': s.service_tags, # M:N
                #if '' in s.keys():
                #    s.'lifeEvents': s.life_events:
                
                u.save()
            '''
            # if it's in the DB but NOT in the json, then delete it
            for dbss in govservices.models.SubService.objects.all():
            found_in_json = False
            for ss in sjr.list_subservices():
                if ss['id'] == dbss.cat_id:
                    found_in_json = True
            if not found_in_json:
                dbss.delete()
            '''




if __name__ == "__main__":
    # test here now,
    # but move it to tests.py later
    pass
