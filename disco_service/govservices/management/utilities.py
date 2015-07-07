#-*- coding: utf-8; -*-
import os
import json
import govservices
from django.conf import settings


class ServiceJsonRepository(object):
    '''
    Interface to the repository of json files
    which contain the service catalogue.

    These are read but never written to (from this code).
    '''
    # global caches to reduce DB hits
    # (singleton class attributes)
    _agency_jsonfiles = {}
    _subservices = []
    _dimensions = []

    def __init__(self, json_path):
        '''
        Simple constructor needs a path to the json repository.

        For example. this may be the path to your working copy
        of a git repository.
        '''
        self.json_path = json_path

    def agency_service_json(self):
        '''
        Returns the entire json repository in the form of a big
        list, where each item is a 3-tuple of:
         * agency
         * filename
         * json payload

        Caches the whole thing in memory so it's cheap to call
        lots of times.
        '''
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
        '''
        For a given agency, returns a list of filename/json
        payload tuples. This is the low-level method that actually
        parses the json file.

        It also injects an 'agency' attribute (if absent), which
        is (currently) not part of the (json) sources however can
        be inferred from the directory structure.
        '''
        try:
            out = self._agency_jsonfiles
        except:
            self._agency_jsonfiles = {}
        if agency in self._agency_jsonfiles.keys():
            return self._agency_jsonfiles[agency]
        if agency not in self.list_agencies():
            msg = "%s not in list of agencies: %s"
            raise Exception, msg % (agency, self.list_agencies())
        self._agency_jsonfiles[agency] = []
        agency_path = os.path.join(self.json_path, agency)
        for f in os.listdir(agency_path):
            name = os.path.join(agency_path, f)
            if not os.path.isdir(name):
                jsonpayload = json.loads(open(name).read())
                # inject agency into the service jsonpayload
                if 'agency' not in jsonpayload.keys():
                    jsonpayload['agency'] = agency
                self._agency_jsonfiles[agency].append((f, jsonpayload))
        return self._agency_jsonfiles[agency]

    def list_agencies(self):
        '''
        Returns a list of (strings) agency acronyms.
        '''
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
        '''
        Returns the entire list of subservices that occur
        in any agency in the json repository.

        Injects 'agency' property into the returned structures.
        Note that without agency property, agencies can not be 
        uniquely defined (ids can be reused between agencies,
        names "should be" unique but are mutable).
        '''
        if len(self._subservices) > 0:
            return self._subservices
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
                            if subservice not in self._subservices:
                                self._subservices.append(subservice)
        return self._subservices

    def list_service_tags(self):
        '''
        Return a list of tags (strings) that have been applied
        to at least one of the services.
        '''
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
        '''
        Return a list of life events (structures) that have
        been related to at least one of the services.
        
        The json payloads sometimes contain 'lifeEvents' or
        'LifeEvents' (different capitalisation). Both forms
        are included in the results.
        '''
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
        '''
        Returns a list of service_types (structures) that occur
        in at least on service description. Two spellings have
        been seen in the wild ('serviceType', 'ServiceType'),
        both are included.
        '''
        out = []
        for a, f, jsonpayload in self.agency_service_json():
            service = jsonpayload['service']
            for k in (u'serviceTypes', u'ServiceTypes'):
                if k in service.keys():
                    #print "DEBUG: %s" % service
                    for st in service[k]:
                        if st not in out:
                            out.append(st)
        return out

    def list_services(self):
        '''
        Returns a list of parsed json payloads, each representing
        a service. The agency and json_filename are injected (not
        present in origional file payloads, but available from the
        file system).
        '''
        out = []
        for a, f, jsonpayload in self.agency_service_json():
            service = jsonpayload['service']
            service['json_filename'] = f
            service['agency'] = a
            if service not in out:
                out.append(service)
        return out

    def list_dimensions(self):
        '''
        Returns a list of service dimensions (structures), that
        occur anywhere in the service catalogue.
        '''
        if len(self._dimensions) > 0:
            return self._dimensions
        for a, f, jsonpayload in self.agency_service_json():
            for dim in jsonpayload['Dimension']:
                # downcast unicode to assci
                # I forget why I did that
                dim[u'agency'] = u'%s' % a
                for k in dim.keys():
                    if dim[k] in ('', u'', None):
                        del(dim[k])
                # rename 'id' attribute to 'dim_id'
                if 'id' in dim.keys():
                    dim['dim_id'] = dim['id']
                    del(dim['id'])
                self._dimensions.append(dim)
        return self._dimensions


    def agency_found_in_json(self, db_a):
        '''
        Returns True if an agency (string) exists in the
        json repository.
        '''
        for json_a in self.list_agencies():
            if json_a == db_a:
                return True
        return False

    def subservice_found_in_json(self, ss):
        '''
        Returns True if a subservice (structure) exists in
        the json repository.

        NB: If a subservice exists with the same 'id' and
        'agency', it is taken to be the same subservice (albeit
        potentially a different or changed version).
        '''
        for js in self.list_subservices():
            if js['agency']==ss['agency'] and js['id']==ss['id']:
                return True
        return False

    def service_in_json(self, s):
        '''
        Returns True if a service (structure) exists in
        the json repository.
        '''
        for js in self.list_services():
            if js['id']==s['id'] and js['agency']==s['agency']:
                return True
        return False

class ServiceDBRepository(object):
    _subservices = []
    _services = []
    _dimensions = []

    def __init__(self):
        self.Agency = govservices.models.Agency
        self.SubService = govservices.models.SubService
        self.ServiceTag = govservices.models.ServiceTag
        self.LifeEvent = govservices.models.LifeEvent
        self.ServiceType = govservices.models.ServiceType
        self.Service = govservices.models.Service
        self.Dimension = govservices.models.Dimension
 
    # service
    def list_services(self):
        if len(self._services) > 0:
            return self._services
        for s in self.Service.objects.all():
            # DEBUG
            #print s
            #for x in dir(s):
            #    try:
            #        if x[0] != '_':
            #            if u"<bound " != str(eval("s.%s" % x))[0:6]:
            #                print "    %s: %s" % (x, eval("s.%s" % x))
            #            else:
            #                print "XXX: %s" % str(eval("s.%s" % x))
            #    except:
            #        print "won't eval %s" % x
            # /DEBUG
            x = {
                'id': s.src_id,
                'agency': s.agency.acronym,
            }
            if s.old_src_id is not None:
                x['old_id'] = s.old_src_id
            if s.json_filename:
                x['json_filename'] = s.json_filename
            if s.info_url:
                x['info_url'] = s.info_url
            if s.name:
                x['name'] = s.name
            if s.acronym:
                x['acronym'] = s.acronym
            if s.tagline:
                x['tagline'] = s.tagline
            if s.primary_audience:
                x['primary_audience'] = s.primary+audience
            if s.analytics_available:
                x['analytics_available'] = s.analytics_available
            if s.incidental:
                x['incidental'] = s.incidental
            if s.secondary:
                x['secondary'] = s.secondary
            if s.src_type:
                x['src_type'] = s.src_type
            if s.description:
                x['description'] = s.description
            if s.comment:
                x['comment'] = s.comment
            if s.current:
                x['current'] = s.current
            if s.org_acronym:
                x['org_acronym'] = s.org_acronym
            #
            if s.service_types.count() > 0:
                x['service_types'] = []
                for st in s.service_types.all():
                    x['service_types'].append(str(st))
            if s.service_tags.count() > 0:
                x['service_tags'] = []
                for st in s.service_tags.all():
                    x['service_tags'].append(str(st))
            if s.life_events.count() > 0:
                x['life_events'] = []
                for le in s.life_events.all():
                    x['life_events'].append(str(le))
            self._services.append(x)
        return self._services

    def create_service(self, s):
        self._services = []
        try:
            a = self.get_ORM_agency(s['agency'])
        except:
            self.create_agency(s['agency'])
            a = self.get_ORM_agency(s['agency'])
        new = self.Service(
            agency=a,
            src_id=s['id']
        )
        if 'name' in s.keys():
            new.name  = s['name']
        new.save() # debug
        if 'old_id' in s.keys():
            new.old_src_id = s['old_id']
        if 'json_filename' in s.keys():
            new.json_filename = s['json_filename']
        if 'info_url' in s.keys():
            new.info_url = s['info_url']
        if 'acronym' in s.keys():
            new.acronym = s['acronym']
        if 'tagline' in s.keys():
            new.tagline = s['tagline']
        if 'primary_audience' in s.keys():
            new.primary_audience = s['primary_audience']
        if 'analytics_available' in s.keys():
            new.analytics_available = s['analytics_available']
        if 'incidental' in s.keys():
            new.incidental = s['incidental']
        if 'secondary' in s.keys():
            new.secondary = s['secondary']
        if 'src_type' in s.keys():
            new.src_type = s['src_type']
        if 'description' in s.keys():
            new.description = s['description']
        if 'comment' in s.keys():
            new.comment = s['comment']
        if 'current' in s.keys():
            new.current = s['current']
        if 'org_acronym' in s.keys(): #CRUFT! TODO: fixme
            new.org_acronym = s['org_acronym']
        new.save()
        if 'service_type' in s.keys():
            for st in s['service_types']:
                if st not in self.list_service_types():
                    self.create_service_type(st)
                stdb = self.ServiceType.objects.get(label=st)
                new.service_types.add(stdb)
                #print "relating %s to %s" % (s, stdb)  # DEBUG
                new.save()
        if 'service_tags' in s.keys():
            for st in s['service_tags']:
                if st not in self.list_service_tags():
                    self.create_service_tag(st)
                stdb = self.ServiceTag.objects.get(label=st)
                new.life_events.add(srdb)
                #print "relating %s to %s" % (s, stdb)  # DEBUG
                new.save()
        if 'life_events' in s.keys():
            for le in s['life_events']:
                if le not in self.list_events():
                    self.create_event(le)
                ledb = self.LifeEvent.objects.get(label=le)
                new.life_events.add(ledb) 
                #print "relating %s to %s" % (s, stdb)  # DEBUG
                new.save()

    def delete_service(self, s):
        self._services = []
        a = self.get_ORM_agency(s['agency'])
        s = self.Service.objects.get(agency=a, src_id=s['id'])
        s.delete()

    def service_in_db(self, s):
        '''
        by definition, when two services have the same agency and
        the same id, they are the same service.

        This means when services change agency (e.g. MOG), they
        are replaced with new services. We obviously will want to
        link the old and new. Those requirements are not understood
        at the moment, more work will be required...
        '''
        for dbs in self.list_services():
            if dbs['agency'] == s['agency'] and dbs['id'] == s['id']:
                return True
        return False

    def service_same_as_db(self, s):
        '''
        Returns True if the service not only exists in the DB, but is also
        identical to the record in the DB.
        '''
        for db in self.list_services():
            if db == s:
                return True
            #if db['id']==s['id'] and db['agency']==s['agency']:
            #    print "service mistmatch:"
            #    print "DB: %s" % db
            #    print "param: %s" % s
            #    raise Exception, 'DEBUG'
        return False

    def update_service(self, s):
        self._services=[]
        agency_acronym = s['agency']
        ag = self.get_ORM_agency(agency_acronym)
        u = govservices.models.Service.objects.get(src_id=s['id'], agency=ag)
        u.org_acronym = s['agency'] # this is redundant, delete from model                
        u.json_filename = s['json_filename']
        if 'oldId' in s.keys():
            u.old_src_id = s['oldId'] # old_id?
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
        # TODO: tests that fail because we are not managing these M:N fields here
        #if 'serviceTypes' in s.keys():
        #    s.'serviceTypes': s.service_types, # M:N
        #if '' in s.keys():
        #    s.'tags': s.service_tags, # M:N
        #if '' in s.keys():
        #    s.'lifeEvents': s.life_events:
        u.save()

    # service types
    def list_service_types(self):
        '''
        returns list of service types (strings)
        '''
        out = []
        for x in self.ServiceType.objects.all():
            out.append(x.label)
        return out

    def create_service_type(self, label):
        '''
        Given an label (string), creates a new life event.
        '''
        self.ServiceType(label=label).save()

    def delete_service_type(self, label):
        '''
        Deletes the service_type with the given label.
        '''
        self.ServiceType.objects.get(label=label).delete()

    def service_type_in_db(self, label):
        '''
        Returns True if there is a service type in the DB
        with the given label.
        '''
        for dbl in self.list_service_types():
            if dbl == label:
                return True
        return False

    # life events
    def list_life_events(self):
        '''
        return list of life events (strings)
        '''
        out = []
        for x in self.LifeEvent.objects.all():
            out.append(x.label)
        return out

    def life_event_in_db(self, label):
        '''
        Returns True if there is a life event in the DB
        with the given label.
        '''
        for dbl in self.list_life_events():
            if dbl == label:
                return True
        return False

    def create_life_event(self, label):
        '''
        Given an label (string), creates a new life event.
        '''
        self.LifeEvent(label=label).save()

    def delete_life_event(self, label):
        '''
        Deletes the life event with the given label.
        '''
        self.LifeEvent.objects.get(label=label).delete()

    # service tags
    def list_service_tags(self):
        '''
        return list of service tags (strings)
        '''
        out = []
        for st in self.ServiceTag.objects.all():
            out.append(st.label)
        return out

    def service_tag_in_db(self, label):
        '''
        Returns True if there is a service tag in the DB
        with the given label.
        '''
        for dbl in self.list_service_tags():
            if dbl == label:
                return True
        return False

    def create_service_tag(self, label):
        '''
        Given an label (string), creates a new service tag.
        '''
        self.ServiceTag(label=label).save()

    def delete_service_tag(self, label):
        '''
        Deletes the service tag with the given label.
        '''
        self.ServiceTag.objects.get(label=label).delete()

    # agencies
    def list_agencies(self):
        '''
        Return list of agency acronyms (strings).

        Note, there seems to be a more sophistocated agency structure
        within the serviceCatalogue internal database, but the only thing
        exposed through the json interface is the acronym. In the future,
        if those other details came out, this method would probably be
        renamed to 'list_agency_acronyms' (if it's still needed at all).
        '''
        out = []
        for dba in self.Agency.objects.all():
            out.append(dba.acronym)
        return out

    def get_ORM_agency(self, label):
        if label == None:
            raise Exception, 'label must not be None'
        try:
            cache = self._agency_ormcache
        except:
            self._agency_ormcache = {}
        if label in self._agency_ormcache.keys():
            agency = self._agency_ormcache[label]
            if agency == None:
                msg = 'something wicked: agency %s found in cache with type %s'
                raise Exception, msg % (label, type(agency))
        else:
            agency = self.Agency.objects.get(acronym=label)
            self._agency_ormcache[label] = agency
        return agency

    def agency_in_db(self, json_a):
        '''
        Returns True if there is an agency in the DB that is labeled 
        with the given acronym.
        '''
        found = False
        for db_a in self.list_agencies():
            if db_a == json_a:
                found = True
        return found

    def create_agency(self, json_a):
        '''
        Given an acronym (string), creates a new agency.
        '''
        # Doesn't check to see if the acronym is already in use, which
        # it probably should. However, this aparent deficiency is not
        # causing any tests to fail so I guess it isn't a big problem.
        agency = self.Agency(acronym=json_a)
        agency.save()
        return agency

    def delete_agency(self, label):
        '''
        Deletes the agency identified by the given string.
        '''
        # Doesn't check to make sure it exists first...
        agency = self.get_ORM_agency(label)
        agency.delete()
        del(self._agency_ormcache[label])

    # subservices
    def list_subservices(self):
        '''
        Returns a list of subservices (structures).
        
        NB: nul-valued properties are removed, to make
        comparisons easier.
        '''
        if len(self._subservices) > 0:
            return self._subservices
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
            self._subservices.append(ss_dict)
        return self._subservices

    def subservice_in_db(self, ss):
        '''
        Returns True if there is a subservice in the DB matching
        the one passed in.

        NB: 'matching' means agency and id only, because everything
        else is mutable. The lack of companion  "exact match" method
        smells like a bug...
        '''
        for json_a in self.list_subservices():
            if json_a['agency'] == ss['agency'] and json_a['id'] == ss['id']:
                return True
        return False

    def create_subservice(self, ss):
        '''
        Like it says on the box...
        '''
        self._subservices = []
        if 'desc' not in ss.keys():
            ss['desc']=None
        if ss['agency'] not in self.list_agencies():
            self.create_agency(ss['agency'])
        agency = self.get_ORM_agency(ss['agency'])
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
        # potential bugs!
        #  try deleting a service that doesn't exist
        #  try deleting a service attributed to an agency that doesn't exist
        self._subservices = []
        agency = self.get_ORM_agency(ss['agency'])
        gss = self.SubService.objects.get(
            cat_id=ss['id'],
            agency=agency)
        gss.delete()

    def json_subservice_same_as_db(self, ss):
        '''
        Returns True if the subservice not only exists in the DB, but is also
        identical to the record in the DB.
        '''
        found = False
        same = False
        for dbsub in self.list_subservices():
            if dbsub['agency'] == ss['agency'] and dbsub['id'] == ss['id']:
                found = True
                if dbsub == ss:
                    return True
                return False
        msg = 'unable to compare with a subservice that does not exist in the DB'
        raise Exception, msg

    #dimension
    def create_dimension(self, d):
        try:
            a = self.get_ORM_agency(d['agency'])
        except:
            self.create_agency(d['agency'])
            a = self.get_ORM_agency(d['agency'])
        dd = self.Dimension(
            dim_id = d['dim_id'],
            agency = a)
        if 'name' in d.keys():
            dd.name = d['name']
        if 'dist' in d.keys():
            dd.dist = d['dist']
        if 'desc' in d.keys():
            dd.desc = d['desc']
        if 'info_url' in d.keys():
            dd.info_url = d['info_url']
        dd.save()
        self._dimensions = []

    def delete_dimension(self, d):
        a = self.get_ORM_agency(d['agency'])
        self.Dimension.objects.get(
            dim_id=d['dim_id'],agency=a).delete()
        self._dimensions = []

    def dimension_in_db(self, d):
        for dbd in self.list_dimensions():
            if dbd['agency']==d['agency'] and dbd['dim_id']==d['dim_id']:
                return True
        return False

    def update_dimension(self, d):
        agency_acronym = d['agency']
        ag = self.get_ORM_agency(agency_acronym)
        u = govservices.models.Dimension.objects.get(
            dim_id=d['dim_id'], agency=ag)
        if 'name' in d.keys():
            u.name = d["name"]
        if 'dist' in d.keys():
            u.dist = d["dist"]
        if 'desc' in d.keys():
            u.desc = d["desc"]
        if 'info_url' in d.keys():
            u.info_url = d["info_url"]
        u.save()
        self._dimensions = []

    def dimension_same_as_db(self, d):
        for dbd in self.list_dimensions():
            ok = True
            for k in d.keys():
                if k in dbd.keys():
                    if dbd[k] != d[k]:
                        ok=False
                else:
                    ok=False
            for k in dbd.keys():
                if k in d.keys():
                    if dbd[k] != d[k]:
                        ok=False
                else:
                    ok=False
            if ok:
                return True
        return False

    def list_dimensions(self):
        if len(self._dimensions) > 0:
            return self._dimensions
        for d in self.Dimension.objects.all():
            dim = {
                'dim_id':d.dim_id,
                'agency':d.agency.acronym}
            if d.name:
                dim['name'] = d.name
            if d.dist:
                dim['dist'] = d.dist
            if d.desc:
                dim['desc'] = d.desc
            if d.info_url:
                dim['info_url'] = d.info_url
            self._dimensions.append(dim)
        return self._dimensions


# this stuff should be here, but
# the above should be refactored into smaller classes
# packaged into modules (one for json, the other for DB).
#
# those modules should serve as models for other sources/sinks
# e.g. elasticsearch
#
# migrator could be generic (by config) if the constructor
# took (src, sink) and all had same methods

class Json2DBMigrator():
    def __init__(self, json_path):
        self.sjr = ServiceJsonRepository(json_path)
        self.dbr = ServiceDBRepository()

    def update_agency(self):
        for json_a in self.sjr.list_agencies():
            if not self.dbr.agency_in_db(json_a):
                self.dbr.create_agency(json_a)
        for db_a in self.dbr.list_agencies():
            if not self.sjr.agency_found_in_json(db_a):
                self.dbr.delete_agency(db_a)

    def update_subservice(self):
        for ss in self.sjr.list_subservices():
            # validation: exception if we have two non-identical subservices
            num_matched = 0
            for ss2 in self.sjr.list_subservices():
                if ss2['id'] == ss['id'] and ss2['agency'] == ss['agency']:
                    if ss2 != ss:
                        msg = "json corpus contains non-identical specifications"
                        msg += " of the same subservice \n\n %s\n\n %s"
                        raise Exception, msg % (ss, ss2)
            if not self.dbr.subservice_in_db(ss):
                self.dbr.create_subservice(ss)
            elif not self.dbr.json_subservice_same_as_db(ss):
                self.dbr.update_subservice(ss)
        for dbss in self.dbr.list_subservices():
            if dbss not in self.sjr.list_subservices():
                self.dbr.delete_subservice(dbss)

    def update_servicetag(self):
        for st in self.sjr.list_service_tags():
            if st not in self.dbr.list_service_tags():
                self.dbr.create_service_tag(st)
        for st in self.dbr.list_service_tags():
            if st not in self.sjr.list_service_tags():
                self.dbr.selete_service_tag(st)

    def update_servicetype(self):
        for st in self.sjr.list_service_types():
            if st not in self.dbr.list_service_types():
                self.dbr.create_service_type(st)
        for st in self.dbr.list_service_types():
            if st not in self.sjr.list_service_types():
                self.dbr.delete_service_type(st)

    def update_lifeevent(self):
        for le in self.sjr.list_life_events():
            if le not in self.dbr.list_life_events():
                self.dbr.create_life_event(le)
        for le in self.dbr.list_life_events():
            if le not in self.sjr.list_life_events():
                self.dbr.delete_life_events(le)

    def update_service(self):
        for s in self.sjr.list_services():
            if not self.dbr.service_in_db(s):
                #print "DEBUG service not in DB, inserting %s" % str((s['id'], s['agency'], s['name']))
                self.dbr.create_service(s)
            elif not self.dbr.service_same_as_db(s):
                #print "DEBUG service in DB but not same, updating %s" % str((s['id'], s['agency'], s['name']))
                self.dbr.update_service(s)
        for s in self.dbr.list_services():
            #if s not in self.sjr.list_services(): ### NOOOOO!
            if not self.sjr.service_in_json(s):
                #print "DEBUG service (%s) in DB not found Json; delete it" % str((s['id'], s['agency'], s['name']))
                self.dbr.delete_service(s)

    def update_dimension(self):
        for d in self.sjr.list_dimensions():
            if not self.dbr.dimension_in_db(d):
                self.dbr.create_dimension(d)
            elif not self.dbr.dimension_same_as_db(d):
                self.dbr.update_dimension(d)
        for d in self.dbr.list_dimensions():
            if d not in self.sjr.list_dimensions():
                self.dbr.delete_dimension(d)
            #BUG? - if not identical, will delete
            # but we just synced everything...
