#-*- coding: utf-8; -*-
import os
import json
import govservices


class ServiceJsonRepository(object):
    '''
    Interface to the repository of json files
    which contain the service catalogue.

    These are read but never written to (from this code).
    '''

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

    def list_service_dimensions(self):
        '''
        Returns a list of service dimensions (structures), that
        occur anywhere in the service catalogue.
        '''
        try:
            out = self._service_dimensions
            return out
        except:
            out = []
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
                    out.append(dim)
            self._service_dimensions = tuple(out)
            return out

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

class ServiceDBRepository(object):
    def __init__(self):
        self.Agency = govservices.models.Agency
        self.SubService = govservices.models.SubService
        self.ServiceTag = govservices.models.ServiceTag
        # TODO:
        #  - LifeEvent
        #  - ServiceType
        #  - Service
        #  - ServiceDimension

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
        self.ServiceTag.objects.get(acronym=db_a).delete()

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
        self.Agency(acronym=json_a).save()

    def delete_agency(self, db_a):
        '''
        Deletes the agency identified by the given string.
        '''
        # Doesn't check to make sure it exists first...
        self.Agency.objects.get(acronym=db_a).delete()

    def list_subservices(self):
        '''
        Returns a list of subservices (structures).
        
        NB: nul-valued properties are removed, to make
        comparisons easier.
        '''
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
        # potential bugs!
        #  try deleting a service that doesn't exist
        #  try deleting a service attributed to an agency that doesn't exist
        agency = self.Agency.objects.get(acronym=ss['agency'])
        gss = self.SubService.objects.get(cat_id=ss['id'],agency=agency)
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
