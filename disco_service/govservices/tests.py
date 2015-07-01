#from django.test import TestCase
from unittest import TestCase
from govservices.management.commands.update_servicecatalogue import ServiceJsonRepository
from govservices.management.commands.update_servicecatalogue import ServiceDBRepository
import test_fixtures
from mock import patch, MagicMock
from mock_django.models import ModelMock
from django.test import TestCase


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

    def test_delete_life_event(self):
        pass

    def test_create_service_tag(self):
        pass

    def test_life_event_in_db(self):
        pass

    def test_list_life_event(sel):
        pass

    def test_list_service_tags(self):
        self.assertEqual([], self.dbr.list_service_tags())
        for l in self.randomWords:
            self.dbr.create_service_tag(l)
        for l in self.dbr.list_service_tags():
            self.assertIn(l, self.randomWords)

    def test_service_tag_in_db(self):
        pass

    def test_create_service_tag(self):
        pass

    def test_delete_service_tag(self):
        pass

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
