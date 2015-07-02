#from django.test import TestCase
from unittest import TestCase
import contextlib
from django.core.management import call_command
from mock import patch, MagicMock
from mock_django.models import ModelMock
from django.test import TestCase
import test_fixtures
from govservices.management.commands.update_servicecatalogue import ServiceJsonRepository
from govservices.management.commands.update_servicecatalogue import ServiceDBRepository


class UpdateCommandInterpretationTestCase(TestCase):
    '''
    ensure the update_servicecatalogue is dispatching to the appropriate functions
    '''
    def setUp(self):
        self.command_name = 'update_servicecatalogue'
        self.commandmod = 'govservices.management.commands.%s' % self.command_name


    def test_all(self):
        '''
        if update command called with no arguments, all entities are updated
        '''
        with contextlib.nested(
            patch('%s.%s' % (self.commandmod,'update_agency')),
            patch('%s.%s' % (self.commandmod,'update_subservice')),
            patch('%s.%s' % (self.commandmod,'update_servicetag')),
            patch('%s.%s' % (self.commandmod,'update_servicetype')),
            patch('%s.%s' % (self.commandmod,'update_lifeevent')),
            patch('%s.%s' % (self.commandmod,'update_service')),
            patch('%s.%s' % (self.commandmod,'update_dimension')),
        ) as (
            mock_agency_update,
            mock_subservice_update,
            mock_servicetag_update,
            mock_servicetype_update,
            mock_lifeevent_update,
            mock_service_update,
            mock_dimension_update):
            call_command(self.command_name)
            self.assertTrue(mock_agency_update.called)
            self.assertTrue(mock_subservice_update.called)
            self.assertTrue(mock_servicetag_update.called)
            self.assertTrue(mock_servicetype_update.called)
            self.assertTrue(mock_lifeevent_update.called)
            self.assertTrue(mock_service_update.called)
            self.assertTrue(mock_dimension_update.called)

    def patch_and_test_entity_dispatch(self, entity_name, function_name):
        '''
        assumes the module contains a function named after the entity
        patches it with a MagicMock
        calles the (patched) management command with --entity=$entity_name
        and makes sure the appropriate function was called
        '''
        with patch('%s.%s' % (self.commandmod, function_name)) as mock_command:
            call_command(self.command_name,entity=entity_name)
            self.assertTrue(mock_command.called)

    def test_update_agency_dispatch(self):
        self.patch_and_test_entity_dispatch('Agency', 'update_agency')

    def test_update_subservice_dispatch(self):
        self.patch_and_test_entity_dispatch('SubService', 'update_subservice')

    def test_update_servicetag_dispatch(self):
        self.patch_and_test_entity_dispatch('ServiceTag', 'update_servicetag')

    def test_update_lifeevent_dispatch(self):
        self.patch_and_test_entity_dispatch('LifeEvent', 'update_lifeevent')

    def test_update_service_dispatch(self):
        self.patch_and_test_entity_dispatch('Service', 'update_service')

    def test_update_dimension_dispatch(self):
        self.patch_and_test_entity_dispatch('Dimension', 'update_dimension')


class UpdateCommandExecutionTestCase(TestCase):
    def test_stuff(self):
        pass

class ServiceDBRepoTestCase(TestCase):
    def setUp(self):
        self.dbr = ServiceDBRepository()
        self.fixture = (
            {
                'agency':'FOO',
                'name':'BAR',
                'id':'FOOBAR',
                'desc': 'once upon a time, thingy thing and thing did thing',
                'infoUrl': 'http://website.gov.au/',
                'primaryAudience':'one legged turkey wranglers that get arested overseas'
            },{
                'agency':'FOO',
                'name':'BAZ',
                'id':'FOOBAZ',
                'desc': '... and the pirate treasure is still there today!',
                'infoUrl': 'http://clickhere.gov.au/',
                'primaryAudience':'sentient domestic appliances'})
        self.randomWords = ('aSTROkitteN', u'bellybutton lint')
        self.service_fixtures = (
            {'agency':'blah', 'id':'123ABC'},
        )
        self.dimension_fixture = (
            {'foo': 'bar'},
        )

    # services
    def test_list_services(self):
        self.assertEqual([], self.dbr.list_services())
        for l in self.randomWords:
            self.dbr.create_service_type(l)
        for l in self.dbr.list_service_types():
            self.assertIn(l, self.randomWords)

    def test_service_in_db(self):
        for s in self.service_fixtures:
            self.dbr.create_service(s)
            self.assertTrue(self.dbr.service_in_db(s))

    def test_create_service(self):
        with patch('govservices.models.Service.save') as mock_save:
            for s in self.service_fixtures:
                self.dbr.create_service(s)
                self.assertTrue(mock_save.called)

    def test_delete_service(self):
        with patch('govservices.models.Service.delete') as mock_delete:
            for s in self.service_fixtures:
                self.dbr.create_service(s)
                self.dbr.delete_service(s)
                self.assertTrue(mock_delete.called)

    def test_service_same_as_db(self):
        '''
        return true if both the unique identifiers and optional ones match
        '''
        optional_fields = (
            'old_id', 'info_url', 'name', 'tagline', 'primary_audience',
            'analytics_available', 'incidental', 'secondary', 'src_type',
            'description', 'comment', 'current', 'org_acronym',
            'service_types', 'service_tags', 'life_events')
        for s in self.service_fixtures:
            self.dbr.create_service(s)
            for word in self.randomWords:
                s2 = s
                for k in optional_fields:
                    s2[k] = word
                    self.assertFalse(self.dbr.service_same_as_db(s2))

    # life events
    def test_delete_life_event(self):
        self.dbr.create_life_event('foo')
        with patch('govservices.models.LifeEvent.delete') as mock_delete:
            self.dbr.delete_life_event('foo')
            self.assertTrue(mock_delete.called)

    def test_create_life_event(self):
        with patch('govservices.models.LifeEvent.save') as mock_save:
            self.dbr.create_life_event('foo')
            self.assertTrue(mock_save.called)

    def test_life_event_in_db(self):
        label = "foo"
        self.assertFalse(self.dbr.life_event_in_db(label))
        self.dbr.create_life_event(label)
        self.assertTrue(self.dbr.life_event_in_db(label))

    def test_list_life_event(self):
        self.assertEqual([], self.dbr.list_life_events())
        for l in self.randomWords:
            self.dbr.create_life_event(l)
        for l in self.dbr.list_life_events():
            self.assertIn(l, self.randomWords)

    # service tags
    def test_service_tag_in_db(self):
        label = "foo"
        self.assertFalse(self.dbr.agency_in_db(label))
        self.dbr.create_agency(label)
        self.assertTrue(self.dbr.agency_in_db(label))

    def test_create_service_tag(self):
        with patch('govservices.models.ServiceTag.save') as mock_save:
            self.dbr.create_service_tag('foo')
            self.assertTrue(mock_save.called)

    def test_delete_service_tag(self):
        self.dbr.create_service_tag('foo')
        with patch('govservices.models.ServiceTag.delete') as mock_delete:
            self.dbr.delete_service_tag('foo')
            self.assertTrue(mock_delete.called)

    def test_list_service_tags(self):
        self.assertEqual([], self.dbr.list_service_tags())
        for l in self.randomWords:
            self.dbr.create_service_tag(l)
        for l in self.dbr.list_service_tags():
            self.assertIn(l, self.randomWords)

    # service types
    def test_list_service_types(self):
        self.assertEqual([], self.dbr.list_service_types())
        for l in self.randomWords:
            self.dbr.create_service_type(l)
        for l in self.dbr.list_service_types():
            self.assertIn(l, self.randomWords)

    def test_service_type_in_db(self):
        label = "foo"
        self.assertFalse(self.dbr.service_type_in_db(label))
        self.dbr.create_service_type(label)
        self.assertTrue(self.dbr.service_type_in_db(label))


    def test_create_service_type(self):
        with patch('govservices.models.ServiceType.save') as mock_save:
            self.dbr.create_service_type('foo')
            self.assertTrue(mock_save.called)


    def test_delete_service_type(self):
        self.dbr.create_service_type('foo')
        with patch('govservices.models.ServiceType.delete') as mock_delete:
            self.dbr.delete_service_type('foo')
            self.assertTrue(mock_delete.called)

    # agencies
    def test_list_agencies(self):
        dummy_agencies = ['foo', 'bar', 'baz']
        self.assertEqual([], self.dbr.list_agencies()) 
        for a in dummy_agencies:
            self.dbr.create_agency(a)
        found = self.dbr.list_agencies()
        for a in dummy_agencies:
            self.assertIn(a, found)

    def test_json_agency_in_db(self):
        label = "foo"
        found = self.dbr.agency_in_db(label)
        self.assertFalse(found)
        self.dbr.create_agency(label)
        found = self.dbr.agency_in_db(label)
        self.assertTrue(found)

    def test_create_agency(self):
        # if I was doing input validation, test that here too.
        # <tich tich>
        with patch('govservices.models.Agency.save') as mock_save:
            self.dbr.create_agency('foo')
            self.assertTrue(mock_save.called)

    def test_delete_agency(self):
        self.dbr.create_agency('foo')
        with patch('govservices.models.Agency.delete') as mock_delete:
            self.dbr.delete_agency('foo')
            self.assertTrue(mock_delete.called)

    # subservices
    def test_list_subservices(self):
        for ss in self.fixture:
            self.assertFalse(ss in self.dbr.list_subservices())
            self.dbr.create_subservice(ss)
            self.assertTrue(ss in self.dbr.list_subservices())

    def test_json_subservice_in_db(self):
        '''
        return true if the unique identifiers match
        even if the optional properties do not
        '''
        for ss in self.fixture:
            self.dbr.create_subservice(ss)
            self.assertTrue(self.dbr.json_subservice_in_db(ss))
            for word in self.randomWords:
                ss['desc'] = word
                self.assertTrue(self.dbr.json_subservice_in_db(ss))
                ss['infoUrl'] = word
                self.assertTrue(self.dbr.json_subservice_in_db(ss))
                ss['primaryAudience']
                self.assertTrue(self.dbr.json_subservice_in_db(ss))

    def test_json_subservice_same_as_db(self):
        '''
        return true if the unique identifiers and optional ones match
        '''
        for ss in self.fixture:
            self.dbr.create_subservice(ss)
            self.assertTrue(self.dbr.json_subservice_in_db(ss))
            for word in self.randomWords:
                s2 = ss
                for k in ('desc', 'infoUrl', 'primaryAudience'):
                    s2[k] = word
                    self.assertFalse(self.dbr.json_subservice_same_as_db(s2))

    def test_create_subservice(self):
        for ss in self.fixture:
            self.assertFalse(self.dbr.json_subservice_in_db(ss))
            self.dbr.create_subservice(ss)
            self.assertTrue(self.dbr.json_subservice_in_db(ss))
        
    def test_delete_subservice(self):
        for ss in self.fixture:
            self.dbr.create_subservice(ss)
            self.dbr.delete_subservice(ss)
            self.assertFalse(self.dbr.json_subservice_in_db(ss))

    # Dimensions
    def test_list_dimensions(self):
        for ss in self.dimension_fixture:
            self.assertFalse(ss in self.dbr.list_dimensions())
            self.dbr.create_dimension(ss)
            self.assertTrue(ss in self.dbr.list_dimensionS())

    def test_dimension_in_db(self):
        '''
        return true if the unique identifiers match
        even if the optional properties do not
        '''
        volatile_fieldss = ('name', 'dist', 'desc', 'info_url')
        for d in self.dimension_fixture:
            self.dbr.create_dimension(d)
            self.assertTrue(self.dbr.dimension_in_db(d))
            d2 = d
            for word in self.randomWords:
                for k in volatile_fields:
                    d[k] = word
                    self.assertTrue(self.dbr.dimension_in_db(d))

    def test_dimension_same_as_db(self):
        '''
        return true if the unique identifiers and optional ones match
        '''
        volatile_fieldss = ('name', 'dist', 'desc', 'info_url')
        for d in self.dimension_fixture:
            self.dbr.create_dimension(d)
            self.assertTrue(self.dbr.dimension_in_db(d))
            for word in self.randomWords:
                d2 = d
                for k in volatile_fields:
                    d2[k] = word
                    self.assertFalse(self.dbr.dimension_same_as_db(d2))

    def test_create_dimension(self):
        for d in self.dimension_fixture:
            self.assertFalse(self.dbr.dimension_in_db(d))
            self.dbr.create_dimension(d)
            self.assertTrue(self.dbr.dimension_in_db(d))
        
    def test_delete_dimension(self):
        for d in self.dimension_fixture:
            self.dbr.create_dimension(d)
            self.dbr.delete_dimension(d)
            self.assertFalse(self.dbr.dimension_in_db(d))


class JSONParser(TestCase):
    def setUp(self):
        fixture_path = "./test_fixtures/"
        self.jsr = ServiceJsonRepository(fixture_path)
        self.randomWords = ('aSTROkitteN', u'bellybutton lint')

    def test_agency_found_in_json(self):
        '''
        if the agency exists in the json, this should return true
        otherwise this should return false
        '''
        for a in self.jsr.list_agencies():
            self.assertTrue(
                self.jsr.agency_found_in_json(a))
        for a in ('foo', 'bar', 'baz', 'bling'):
            if a not in self.jsr.list_agencies():
                self.assertFalse(
                    self.jsr.agency_found_in_json(a))

    def test_list_service_dimensions(self):
        '''
        we expect to get a list of service dimensions
        pk (agency, dim_id) 
        and the rest...
        '''
        found_dims = self.jsr.list_service_dimensions()
        expected_dims = test_fixtures.EXPECTED_AGENCY_DIMENSIONS
        for fd in found_dims:
            for k in fd.keys():
                if fd[k] in ('', u'', None):
                    del(fd[k ])
            self.assertIn(fd, expected_dims)  # no unexpected dims
        for d in expected_dims:
            self.assertIn(d, found_dims)  # all expected dims

    def test_list_agencies(self):
        # given the fixture, all expected agencies must present
        found_agencies = self.jsr.list_agencies()
        expected_agencies = ("XYZ", "DEF", "QWERTY", "FOO")
        for a in expected_agencies:
            self.assertIn(a, found_agencies)
        # and no unexpected agencies
        for a in found_agencies:
            self.assertIn(a, expected_agencies)
        # and no duplicates
        num_found = len(found_agencies)
        num_distinct = len(set(found_agencies))
        self.assertEqual(num_found, num_distinct)

    def test_list_agency_jsonfiles(self):
        '''
        given an agency name (== top level directory in the json fixture),
        we expect this method to return a list of 2-tuples (couples)
        where the first element is the name of a json file
        and the second element is a parsed json payload.
        '''
        # TODO: move to test_fixtures.__init__.py, EXPECTED_AGENCY_JSONFILES
        expected_agency_jsonfiles = test_fixtures.EXPECTED_AGENCY_JSONFILES
        for agency in expected_agency_jsonfiles.keys():
            found_jsonfiles = self.jsr.list_agency_jsonfiles(agency)
            found_jsonfile_names = []
            for (n, p) in found_jsonfiles:
                if n not in found_jsonfile_names:
                    found_jsonfile_names.append(n)
            found_num_jsonfiles = len(found_jsonfiles)
            found_num_jsonfile_names = len(found_jsonfile_names)
            expected_num_jsonfiles = len(expected_agency_jsonfiles[agency])
            self.assertEqual(found_num_jsonfile_names, expected_num_jsonfiles)
            self.assertEqual(found_num_jsonfiles, expected_num_jsonfiles)

            for j in expected_agency_jsonfiles[agency]:
                self.assertIn(j, found_jsonfile_names)

    def test_list_subservices(self):
        '''
        we expect this method to return a list of distinct structures
        each of which represents a subservice object

        The returned structure should not should not contain None-valued
        properties or empty lists, even if they are present in the source
        JSON.

        The structure:
         * must contain an 'id' field.
         * may contain 'desc', 'name', 'infoUrl' or 'primaryAudience' fields.
         * must not contain any other fields
        
        '''
        mandatory_fields = ('id')
        optional_fields = ('desc', 'name', 'infoUrl', 'primaryAudience')
        expected_subservices = test_fixtures.EXPECTED_SUBSERVICES
        found_subservices = self.jsr.list_subservices()
        for ss in found_subservices:
            self.assertIn(ss, expected_subservices)
        for ss in expected_subservices:
            self.assertIn(ss, found_subservices)

    def test_subservice_found_in_json(self):
        '''
        true if subservice can be found in json
        '''
        for ss in self.jsr.list_subservices():
            self.assertTrue(self.jsr.subservice_found_in_json(ss))
            for word in self.randomWords:
                s2 = ss
                for k in ('desc', 'infoUrl', 'primaryAudience'):
                    s2[k] = word
                    self.assertTrue(self.jsr.subservice_found_in_json(s2))

    def test_list_service_tags(self):
        '''
        we expect to recieve a list of labels which:
         * contains no duplicates
         * contains every label in the test fixture
         * does not contain any labels that are not in the fixture
        '''
        expected_labels = ('housing', 'automatic')
        found_labels = self.jsr.list_service_tags()
        for st in found_labels:
            self.assertIn(st, expected_labels)
        for st in expected_labels:
            self.assertIn(st, found_labels)
        num_found = len(found_labels)
        num_distinct = len(set(found_labels))
        self.assertEqual(num_found, num_distinct)

    def test_list_life_events(self):
        '''
        much like service_tags, except life events
        '''
        expected_labels = test_fixtures.EXPECTED_LIFE_EVENTS
        found_labels = self.jsr.list_life_events()
        for st in found_labels:
            self.assertIn(st, expected_labels)
        for st in expected_labels:
            self.assertIn(st, found_labels)
        num_found = len(found_labels)
        num_distinct = len(set(found_labels))
        self.assertEqual(num_found, num_distinct)

    def test_list_service_types(self):
        '''
        another tag-like weak entity, per life_event and service_tag
        '''
        expected_labels = test_fixtures.EXPECTED_SERVICE_TYPES
        found_labels = self.jsr.list_service_types()
        for st in found_labels:
            self.assertIn(st, expected_labels)
        for st in expected_labels:
            self.assertIn(st, found_labels)
        num_found = len(found_labels)
        num_distinct = len(set(found_labels))
        self.assertEqual(num_found, num_distinct)
        

    def test_list_services(self):
        '''
        we expect every servce in the fixture will be found and returned
        '''
        found_services = self.jsr.list_services()
        # all the filenames in fixture are found
        expected_filenames = test_fixtures.EXPECTED_FILENAMES
        found_filenames = []
        for s in found_services:
            filename_attribute = s['json_filename']
            self.assertIn(filename_attribute, expected_filenames)
            found_filenames.append(filename_attribute)
        # including filenames in agency_jsonfiles
        expected_agency_jsonfiles = test_fixtures.EXPECTED_AGENCY_JSONFILES
        for k in expected_agency_jsonfiles.keys():
            for fn in expected_agency_jsonfiles[k]:
                self.assertIn(fn, found_filenames)
        # also, all the json payloads check out too...
        # TODO

    def test_agency_service_json(self):
        '''
        we expect every service for every agency
        '''
        expected_agencies = self.jsr.list_agencies()
        expected_filenames = test_fixtures.EXPECTED_FILENAMES
        found_agencies = []
        found_filenames = []
        found_jsonpayloads = []
        for agency, filename, jsonpayload in self.jsr.agency_service_json():
            self.assertIn(agency, expected_agencies)
            if agency not in found_agencies:
                found_agencies.append(agency)
            if filename not in found_filenames:
                found_filenames.append(filename)
            if jsonpayload not in found_jsonpayloads:
                found_jsonpayloads.append(jsonpayload)

        for agency in found_agencies:
            self.assertIn(agency, expected_agencies)
        for agency in expected_agencies:
            self.assertIn(agency, found_agencies)

        for filename in found_filenames:
            self.assertIn(filename, expected_filenames)
        for filename in expected_filenames:
            self.assertIn(filename, found_filenames)
