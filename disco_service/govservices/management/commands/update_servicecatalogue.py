#-*- coding: utf-8; -*-
"""
It would be highly preferable to refactor this to use a REST API to interrogate
the service catalogue, rather than messing about with the ServiceJsonRepository.
"""
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from govservices.management.utilities import ServiceJsonRepository
from govservices.management.utilities import ServiceDBRepository
from govservices.management.utilities import Json2DBMigrator

class Command(BaseCommand):
    help = 'update the service catalogue in the DB, from the json files'
    # the filesystem json interface is in the repo
    # at ./catalogues/serviceDocuments/<agency>/<service spec>
    _repo_path = settings.SERVICE_CATALOGUE_REPOSITORY_PATH
    _default_catalogue_path = os.path.join(
        _repo_path,
        'catalogues')
    _default_service_docs = os.path.join(
        _default_catalogue_path,
        'serviceDocuments')

    entity_funcs = {
        'Agency': 'update_agency',
        'SubService': 'update_subservice',
        'ServiceTag': 'update_servicetag',
        'LifeEvent': 'update_lifeevent',
        'ServiceType': 'update_servicetype',
        'Service': 'update_service',
        'Dimension': 'update_dimension'}

    def add_arguments(self, parser):
        help_msg = 'Limit sync to specific relational entity %s'
        help_msg = help_msg % str(self.entity_funcs.keys())
        parser.add_argument(
            '--entity',
            action='store',
            dest='entity',
            default=None,
            help=help_msg)
        help_msg = "Access JSON files from non-default location"
        parser.add_argument(
            '--json',
            action='store',
            dest='service_docs',
            default=self._default_service_docs,
            help=help_msg)

    def handle(self, *args, **options):
        j2db = Json2DBMigrator(options['service_docs'])
        if options['entity']:
            if options['entity'] not in self.entity_funcs.keys():
                e = options['entity']
                l = tuple(self.entity_funcs.keys())
                msg = '%s is not one of the entities we can update %s' % (e, l)
                raise CommandError, msg
            else:
                cmd = self.entity_funcs[options['entity']]
                eval("j2db.%s()" % cmd)
        else:  # do everything
            for k in self.entity_funcs.keys():
                cmd = self.entity_funcs[k]
                eval("j2db.%s()" % cmd)
