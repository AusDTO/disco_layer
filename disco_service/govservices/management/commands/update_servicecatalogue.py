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
                # inject agency into the service jsonpayload
                if 'agency' not in jsonpayload.keys():
                    jsonpayload['agency'] = agency
                out.append((jsonfilename, jsonpayload))
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
                                # mess up database comparison (bugfix)
                                for k in subservice.keys():
                                    if subservice[k] is None:
                                        del(subservice[k])
                                    # inject agency into the subservice
                                    # jsonpayload (feature)
                                    if 'agency' not in subservice.keys():
                                        subservice['agency'] = agency
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
            service['agency'] = a
            if service not in out:
                out.append(service)
        return out

    def list_service_dimensions(self):
        try:
            out = self._service_dimensions
            return out
        except:
            out = []
            for a, f, jsonpayload in self.agency_service_json():
                for dim in jsonpayload['Dimension']:
                    dim[u'agency'] = u'%s' % a
                    for k in dim.keys():
                        if dim[k] in ('', u'', None):
                            del(dim[k])
                    if 'id' in dim.keys():
                        dim['dim_id'] = dim['id']
                        del(dim['id'])
                    out.append(dim)
            self._service_dimensions = tuple(out)
            return out

    def agency_found_in_json(self, db_a):
        found = False
        for json_a in self.list_agencies():
            if json_a == db_a:
                found = True
        return found

    def subservice_found_in_json(self, ss):
        for js in self.list_subservices():
            if js['agency']==ss['agency'] and js['id']==ss['id']:
                return True
        return False

class ServiceDBRepository(object):
    def __init__(self):
        self.Agency = govservices.models.Agency
        self.SubService = govservices.models.SubService

    def list_agencies(self):
        out = []
        for dba in self.Agency.objects.all():
            out.append(dba.acronym)
        return out

    def agency_in_db(self, json_a):
        found = False
        for db_a in self.list_agencies():
            if db_a == json_a:
                found = True
        return found

    def create_agency(self, json_a):
        self.Agency(acronym=json_a).save()

    def delete_agency(self, db_a):
        self.Agency.objects.get(acronym=db_a).delete()

    def list_subservices(self):
        db_subservices = []
        for ss in govservices.models.SubService.objects.all():
            ss_dict = {
                'agency': ss.agency.acronym,
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
        return db_subservices

    def json_subservice_in_db(self, ss):
        for json_a in self.list_subservices():
            if json_a['agency'] == ss['agency'] and json_a['id'] == ss['id']:
                return True
        return False

    def create_subservice(self, ss):
        if 'desc' not in ss.keys():
            ss['desc']=None
        if ss['agency'] not in self.list_agencies():
            self.create_agency(ss['agency'])
        agency = self.Agency.objects.get(acronym=ss['agency'])
        gss = self.SubService(
            cat_id=ss['id'],
            desc=ss['desc'],
            name=ss['name'],
            agency=agency)
        if 'infoUrl' in ss.keys():
            gss.info_url=ss['infoUrl']
        if 'primaryAudience' in ss.keys():
            gss.primary_audience=ss['primaryAudience']
        gss.save()

    def delete_subservice(self, ss):
        agency = self.Agency.objects.get(acronym=ss['agency'])
        gss = self.SubService.objects.get(cat_id=ss['id'],agency=agency)
        gss.delete()

    def json_subservice_same_as_db(self, ss):
        found = False
        same = False
        for dbsub in self.list_subservices():
            if dbsub['agency'] == ss['agency'] and dbsub['id'] == ss['id']:
                found = True
                if dbsub == ss:
                    return True


class Command(BaseCommand):
    help = 'source service specification (json) from Github, then update the DB as required'

    def handle(self, *args, **options):
        # the filesystem json interface is in the repo
        # at ./catalogues/serviceDocuments/<agency>/<service spec>
        repo_path = settings.SERVICE_CATALOGUE_REPOSITORY_PATH
        catalogue_path = os.path.join(repo_path, 'catalogues')
        service_docs = os.path.join(catalogue_path, 'serviceDocuments')
        sjr = ServiceJsonRepository(service_docs)
        dbr = ServiceDBRepository()

        # agencies
        json_agencies = sjr.list_agencies()
        for json_a in json_agencies:
            if not dbr.json_agency_found_in_db(json_a):
                dbr.create_agency(json_a)
        for db_a in dbr.list_agencies():
            if not jsr.agency_found_in_json(db_a):
                dbr.delete_agency(db_a)

        # sync subservices
        db_subservices = dbr.list_subservices()
        # upsert subservices
        for ss in sjr.list_subservices():
            # validation: exception if we have two non-identical subservices
            num_matched = 0
            for ss2 in sjr.list_subservices():
                if ss2['id'] == ss['id'] and ss2['agency'] == ss['agency']:
                    if ss2 != ss:
                        msg = "json corpus contains non-identical specifications"
                        msg += " of the same subservice \n\n %s\n\n %s"
                        raise Exception, msg % (ss, ss2)
            if not dbr.json_subservice_in_db(ss):
                dbr.create_subservice(ss)
            elif not dbr.json_subservice_same_as_db(ss):
                dbr.update_subservice(ss)
        for dbss in dbr.list_subservices():
            if dbss not in jsr.list_subservices():
                dbss.delete()

        # service tags
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
                'agency': dbs.agency.acronym,
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
                    sdict[k] = []
                sdict[k].append(le)
            db_services.append(sdict)

        # if found in json but not DB, insert to DB
        for s in json_services:
            found_in_db = False
            for dbs in db_services:
                if dbs['id'] == s['id']:
                    found_in_db=True
                    num_match=0
                    # is this capturing foreign key references?
                    # is this captureing M:N relationships?
                    for k in s.keys():
                        if k in dbs.keys():
                            if dbs[k] == s[k]:
                                num_match += 1
                    if num_match == len(s):
                        found_in_db_same = True
                    else:
                        found_in_db_same = False

            if not found_in_db:  # then insert it
                agency = govservices.models.Agency.objects.get(acronym=s['agency'])
                gs = govservices.models.Service(src_id = s['id'])
                gs.org_acronym = agency.acronym  #s['org_acronym']
                gs.agency = agency
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
                agency_acronym = s['agency']
                ag = govservices.models.Agency.objects.get(acronym=agency_acronym)
                u = govservices.models.Service.objects.get(src_id=s['id'], agency=ag)
                u.org_acronym = s['agency'] # this is redundant, delete from model
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
        #
        # ServiceDimensions
        #
        json_dimensions = sjr.list_service_dimensions()
        db_dimensions = []
        for dbs in govservices.models.ServiceDimension.objects.all():
            ddict = {
                'dim_id': dbs.dim_id,
                'agency': dbs.agency.acronym,
                'name': dbs.name,
                'dist': dbs.dist,
                'desc': dbs.desc,
                'info_url': dbs.info_url,}
            db_services.append(sdict)

        # if found in json but not DB, insert to DB
        for d in json_dimensions:
            found_in_db = False
            for dbs in db_dimensions:
                if dbs['id'] == d['id']:
                    found_in_db=True
                    num_match=0
                    # is this capturing foreign key references?
                    # is this captureing M:N relationships?
                    for k in d.keys():
                        if k in dbs.keys():
                            if dbs[k] == d[k]:
                                num_match += 1
                    if num_match == len(d):
                        found_in_db_same = True
                    else:
                        found_in_db_same = False

            if not found_in_db:  # then insert it
                agency = govservices.models.Agency.objects.get(acronym=d['agency'])
                gs = govservices.models.ServiceDimension(
                    dim_id = d['dim_id'], agency = agency)
                if 'name' in d.keys():
                    gs.name= d["name"]
                if 'dist' in d.keys():
                    gs.dist=d['dist']
                if 'desc' in d.keys():
                    gs.desc=d['desc']
                if 'info_url' in d.keys():
                    gs.info_url=d["info_url"]
                gs.save()
                
            if found_in_db and not found_in_db_same:  # then update it
                agency_acronym = d['agency']
                ag = govservices.models.Agency.objects.get(acronym=agency_acronym)
                u = govservices.models.ServiceDimension.objects.get(
                    dim_id=s['id'], agency=ag)
                if 'name' in d.keys():
                    u.name = d["name"]
                if 'dist' in d.keys():
                    u.dist = d["dist"]
                if 'desc' in d.keys():
                    u.desc = d["desc"]
                if 'info_url' in d.keys():
                    u.info_url = d["info_url"]
                u.save()

        for dbdim in govservices.models.ServiceDimension.objects.all():
            found = False
            for jdim in json_dimensions:
                if jdim["dim_id"]==dbdim.dim_id and jdim["agency"] == dbdim.agency:
                    found = True
            if not found:  # delete from DB
                dbdim.delete()

if __name__ == "__main__":
    # test here now,
    # but move it to tests.py later
    pass
