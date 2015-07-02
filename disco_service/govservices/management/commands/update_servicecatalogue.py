#-*- coding: utf-8; -*-
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from govservices.management.utilities import ServiceJsonRepository
from govservices.management.utilities import ServiceDBRepository


# the filesystem json interface is in the repo
# at ./catalogues/serviceDocuments/<agency>/<service spec>
repo_path = settings.SERVICE_CATALOGUE_REPOSITORY_PATH
catalogue_path = os.path.join(repo_path, 'catalogues')
service_docs = os.path.join(catalogue_path, 'serviceDocuments')
sjr = ServiceJsonRepository(service_docs)
dbr = ServiceDBRepository()


def update_agency():
    for json_a in sjr.list_agencies():
        if not dbr.agency_in_db(json_a):
            dbr.create_agency(json_a)
    for db_a in dbr.list_agencies():
        if not sjr.agency_found_in_json(db_a):
            dbr.delete_agency(db_a)

def update_subservice():
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
        if dbss not in sjr.list_subservices():
            dbr.delete_subservice(dbss)

def update_servicetag():
    for st in sjr.list_service_tags():
        if st not in dbr.list_service_tags():
            dbr.create_service_tag(st)
    for st in dbr.list_service_tags():
        if st not in sjr.list_service_tags():
            dbr.selete_service_tag(st)

def update_servicetype():
    for st in sjr.list_service_types():
        if st not in dbr.list_service_types():
            dbr.create_service_type(st)
    for st in dbr.list_service_types():
        if st not in sjr.list_service_types():
            dbr.delete_service_type(st)

def update_lifeevent():
    for le in sjr.list_life_events():
        if le not in dbr.list_life_events():
            dbr.create_life_event(le)
    for le in dbr.list_life_events():
        if le not in sjr.list_life_events():
            dbr.delete_life_events(le)

def update_service():
    for s in sjr.list_services():
        if not dbr.service_in_db(s):
            dbr.create_service(s)
        elif not dbr.service_same_as_db(s):
            dbr.update_service(s)
    for s in dbr.list_services():
        if s not in sjr.list_services():
            dbr.delete_service(s)

def update_dimension():
    for d in sjr.list_service_dimensions():
        if not dbr.dimension_in_db(d):
            dbr.create_dimension(d)
        elif not dbr.dimension_same_as_db(d):
            dbr.update_dimension(d)
    for d in dbr.list_dervice_dimensions():
        if d not in jsr.list_service_dimensions():
            dbr.delete_dimension(d)
        #BUG? - if not identical, will delete
        # but we just synced everything...

class Command(BaseCommand):
    help = 'source service specification (json) from Github, then update the DB as required'
    entity_funcs = {
        'Agency': update_agency,
        'SubService': update_subservice,
        'ServiceTag': update_servicetag,
        'LifeEvent': update_lifeevent,
        'ServiceType': update_servicetype,
        'Service': update_service,
        'Dimension': update_dimension}

    def add_arguments(self, parser):
        parser.add_argument(
            '--entity',
            action='store',
            dest='entity',
            default=None,
            help='Limit sync to specific relational entity %s' % str(self.entity_funcs.keys()))

    def handle(self, *args, **options):

        if options['entity']:
            if options['entity'] not in self.entity_funcs.keys():
                e = options['entity']
                l = tuple(self.entity_funcs.keys())
                msg = '%s is not one of the entities we can update %s' % (e, l)
                raise CommandError, msg
            else:
                ent = self.entity_funcs[options['entity']]
                ent()
        else:
            # do everything
            for k in self.entity_funcs.keys():
                f = entity_funcs[k]
                f()
