#from django.test import TestCase
from unittest import TestCase
from govservices.management.commands.update_servicecatalogue import ServiceJsonRepository
import test_fixtures

# Create your tests here.
class JSONParser(TestCase):
    def setUp(self):
        fixture_path = "./test_fixtures/"
        self.jsr = ServiceJsonRepository(fixture_path)

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
        expected_agency_jsonfiles = {
            'DEF': (
                'bbq_tax.json',
                'birthday_tax.json',
                'christmas_tax.json',
                'register_bbq.json',),
            'FOO': (
                'space_robot_loans.json',
                'spaceship_loans.json',),
            'QWERTY': (
                'birthday_bonus.json',)}
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
        pass

    def test_list_service_types(self):
        pass

    def test_list_services(self):
        pass

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
