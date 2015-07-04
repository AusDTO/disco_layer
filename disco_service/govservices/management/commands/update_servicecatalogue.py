#-*- coding: utf-8; -*-
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from govservices.management.utilities import ServiceJsonRepository
from govservices.management.utilities import ServiceDBRepository
from govservices.management.utilities import Json2DBMigrator

class Command(BaseCommand):
    help = 'update the service catalogue in the DB, from the json files'
    j2db = Json2DBMigrator()
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

    def handle(self, *args, **options):
        if options['entity']:
            if options['entity'] not in self.entity_funcs.keys():
                e = options['entity']
                l = tuple(self.entity_funcs.keys())
                msg = '%s is not one of the entities we can update %s' % (e, l)
                raise CommandError, msg
            else:
                cmd = self.entity_funcs[options['entity']]
                eval("self.j2db.%s()" % cmd)
        else:  # do everything
            for k in self.entity_funcs.keys():
                cmd = self.entity_funcs[k]
                eval("self.j2db.%s()" % cmd)
