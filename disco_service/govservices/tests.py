#from django.test import TestCase
from unittest import TestCase
from govservices.management.commands.update_servicecatalogue import ServiceJsonRepository

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
        # this gumpf should be hidden in a module
        expected_subservices = (
            {"id": "CMP_035", "name": "Accommodation Details"},
            {"id": "CMP_098", "name": "Accommodation"},
            {"id": "CMP_199", "name": "Activity Test"},
            {"id": "CMP_200", "name": "Activity Test Exemption"},
            {"id": "CMP_225", "name": "Activity Test Review"},
            {"id": "CMP_163", "name": "Additional Entitlements "},
            {"id": "CMP_099", "name": "Address"},
            {"id": "CMP_277", "name": "Administrative Appeals Tribunal (AAT)"},
            {"id": "CMP_150", "name": "Administrative Compensation"},
            {"id": "CMP_144", "name": "Advance Payment (FTB / MOB / Generic)"},
            {"id": "CMP_194", "name": "AMEP"},
            {"id": "CMP_226", "name": "AOS Reviews"},
            {"id": "CMP_037", "name": "Assurance of Support"},
            {"id": "CMP_145", "name": "Assurance of Support (Release of Bank Guarantee)"},
            {"id": "CMP_253", "name": "Australia Post Commission"},
            {"id": "CMP_278", "name": "Authorised Review Officer (ARO)"},
            {"id": "CMP_173", "name": "Basics Card",},
            {"id": "CMP_019", "name": "Book Appointment",},
            {"id": "CMP_100", "name": "Business Details",},
            {"id": "CMP_146", "name": "Cancellation of Entitlement",},
            {"id": "CMP_148", "name": "Centrepay",},
            {"id": "CMP_107", "name": "Change Customer Details"},
            {"id": "CMP_149", "name": "Child Support Agency Deductions"},
            {"id": "CMP_254", "name": "Collector of Public Monies"},
            {"id": "CMP_006", "name": "Claim Lodgement"},
            {"id": "CMP_007", "name": "Coding / Verification of Customers Generic Details",},
            {"id": "CMP_042", "name": "Compensation Assessment"},
            {"id": "CMP_255", "name": "Compensation Recovery"},
            {"id": "CMP_229", "name": "Compliance Reviews"},
            {"id": "CMP_222", "name": "Comprehensive Compliance Assessment"},
            {"id": "CMP_187", "name": "Concession Card Re-issue"},
            {"id": "CMP_020", "name": "Conduct Interview"},
            {"id": "CMP_008", "name": "Create Customer Record"},
            {"id": "CMP_256", "name": "Debt Raising"},
            {"id": "CMP_257", "name": "Debt Recovery"},
            {"id": "CMP_258", "name": "Debt Repayments"},
            {"id": "CMP_103", "name": "Deceased Customer"},
            {"id": "CMP_026", "name": "Deny Access Facility"},
            {"id": "CMP_230", "name": "Department of Corrective Services Reviews"},
            {"id": "CMP_269", "name": "Departure Prohibition Order"},
            {"id": "CMP_231", "name": "DHA Reviews"},
            {"id": "CMP_232", "name": "DIBP Reviews"},
            {"id": "CMP_286", "name": "Duplicate Form Issue"},
            {"id": "CMP_129", "name": "DVA Updates"},
            {"id": "CMP_287", "name": "Early Release of Superannuation (Hardship Assessment)"},
            {"id": "CMP_010", "name": "Electronic Messaging"},
            {"id": "CMP_002", "name": "Eligibility Entitlement Discussion"},
            {"id": "CMP_201", "name": "Employer Contact Certificates"},
            {"id": "CMP_044", "name": "Employment  Details / Earnings                "},
            {"id": "CMP_202", "name": "Employment Pathway / Participation Plan",},
            {"id": "CMP_203", "name": "Employment Pathway / Participation Plan Review"},
            {"id": "CMP_223", "name": "Employment Services Assessment (ESAt)"},
            {"id": "CMP_195", "name": "Employment Services Provider Referral / Connection"},
            {"id": "CMP_204", "name": "Employment Services Provider Registration"},
            {"id": "CMP_025", "name": "ESAt Liaison"},
            {"id": "CMP_196", "name": "External Programme / Assistance"},
            {"id": "CMP_220", "name": "External Programme Participation "},
            {"id": "CMP_106", "name": "Foreign Pension / Entitlement Status"},
            {"id": "CMP_234", "name": "Foreign Pension Reviews"},
            {"id": "CMP_259", "name": "Garnishee Arrangements"},
            {"id": "CMP_001", "name": "Generic Enquiry"},
            {"id": "CMP_197", "name": "Generic Referral"},
            {"id": "CMP_046", "name": "Homelessness Assessment"},
            {"id": "CMP_151", "name": "Immediate Payment / Hardship Payment"},
            {"id": "CMP_108", "name": "Immunisation / Health Check Details "},
            {"id": "CMP_235", "name": "Income and Assets Review"},
            {"id": "CMP_174", "name": "Income Management - Child Protection"},
            {"id": "CMP_175", "name": "Income Management - Compulsory"},
            {"id": "CMP_178", "name": "Income Management - Voluntary"},
            {"id": "CMP_176", "name": "Income Management Compulsory - Exemptions"},
            {"id": "CMP_177", "name": "Income Management -Deductions"},
            {"id": "CMP_292", "name": "Income Statements"},
            {"id": "CMP_236", "name": "Income Stream Reviews"},
            {"id": "CMP_111", "name": "Income Streams (Super etc - Notification)"},
            {"id": "CMP_188", "name": "Interim Concession Card Issue"},
            {"id": "CMP_021", "name": "Interpreter Requirement"},
            {"id": "CMP_022", "name": "Interview with Specialist"},
            {"id": "CMP_189", "name": "Issue Basics Card "},
            {"id": "CMP_190", "name": "Issue EBT Card"},
            {"id": "CMP_288", "name": "Issue Information"},
            {"id": "CMP_289", "name": "Issue Letter"},
            {"id": "CMP_206", "name": "Job Search Efforts"},
            {"id": "CMP_207", "name": "Job Search Support Only Registrations (JSSO)"},
            {"id": "CMP_208", "name": "Job Seeker Classification Instrument (JSCI)"},
            {"id": "CMP_209", "name": "Job Seeker Diary Issue"},
            {"id": "CMP_210", "name": "Job Seeker Diary Return"},
            {"id": "CMP_113", "name": "Managed Investments (Income & Assets)"},
            {"id": "CMP_114", "name": "Medical Certificate"},
            {"id": "CMP_067", "name": "Medical Consultation (HPAU) "},
            {"id": "CMP_260", "name": "Mercantile Agent Commission"},
            {"id": "CMP_027", "name": "Nominee Arrangements"},
            {"id": "CMP_282", "name": "Ombudsman / Ministerial / NGO"},
            {"id": "CMP_160", "name": "One Off Payment"},
            {"id": "CMP_115", "name": "Other Assets (Income & Assets)"},
            {"id": "CMP_117", "name": "Other Income (Income & Assets)"},
            {"id": "CMP_118", "name": "Overseas Absences"},
            {"id": "CMP_211", "name": "Participation Assessment (Non Serious Failure)"},
            {"id": "CMP_212", "name": "Participation Assessment (Serious Failure)"},
            {"id": "CMP_213", "name": "Participation Exemption "},
            {"id": "CMP_153", "name": "Payday Change"},
            {"id": "CMP_154", "name": "Payment Destination "},
            {"id": "CMP_155", "name": "Payment Frequency / Rate"},
            {"id": "CMP_215", "name": "Payment Stimulation (SU19)"},
            {"id": "CMP_290", "name": "Payment Summaries"},
            {"id": "CMP_221", "name": "Personal Contact Interview"},
            {"id": "CMP_240", "name": "Pilot Review"},
            {"id": "CMP_028", "name": "Power of Attorney"},
            {"id": "CMP_261", "name": "Prosecutions"},
            {"id": "CMP_029", "name": "Proof of Identification"},
            {"id": "CMP_056", "name": "Qualifying Event"},
            {"id": "CMP_241", "name": "Random Sample Review"},
            {"id": "CMP_120", "name": "Real Estate Details"},
            {"id": "CMP_262", "name": "Recovery Fee (Admin Debts)"},
            {"id": "CMP_216", "name": "Reduced Work Capacity"},
            {"id": "CMP_121", "name": "Relationship Status"},
            {"id": "CMP_242", "name": "Rent Review"},
            {"id": "CMP_219", "name": "Reporting Frequency"},
            {"id": "CMP_291", "name": "Request For Further Information"},
            {"id": "CMP_131", "name": "Residency"},
            {"id": "CMP_162", "name": "Restoration"},
            {"id": "CMP_161", "name": "Returned / Re-issue Payment"},
            {"id": "CMP_122", "name": "Savings (Income & Assets)"},
            {"id": "CMP_072", "name": "School Enrolment & Attendance"},
            {"id": "CMP_009", "name": "Self Manage Service Access"},
            {"id": "CMP_243", "name": "Service Profiling"},
            {"id": "CMP_123", "name": "Shares (Income & Assets)"},
            {"id": "CMP_280", "name": "Social Security Appeals Tribunal (SSAT)"},
            {"id": "CMP_156", "name": "Special Employment Advance"},
            {"id": "CMP_124", "name": "Study / Training Details"},
            {"id": "CMP_279", "name": "Subject Matter Expert (SME)"},
            {"id": "CMP_157", "name": "Suspension"},
            {"id": "CMP_158", "name": "Tax Deductions"},
            {"id": "CMP_030", "name": "Tax File Number"},
            {"id": "CMP_125", "name": "Telephone / Internet Details"},
            {"id": "CMP_180", "name": "Third Party Payment Destination"},
            {"id": "CMP_245", "name": "Tip Off Review"},
            {"id": "CMP_126", "name": "Trust & Companies - Notification"},
            {"id": "CMP_023", "name": "Update Appointment"},
            {"id": "CMP_217", "name": "Vulnerability Indicator"},
            {"id": "CMP_246", "name": "Vulnerability Review"},
            {"id": "CMP_198", "name": "Welfare Assistance Referral"},
            {"id": "CMP_159", "name": "Withholdings"})
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
        expected_filenames = (
            'bbq_tax.json',
            'birthday_tax.json',
            'christmas_tax.json',
            'register_bbq.json',
            'space_robot_loans.json',
            'spaceship_loans.json',
            'birthday_bonus.json',
            'aditional_christmas_tax.json',
        )
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
