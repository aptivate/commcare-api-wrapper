import os
import pytest
import json

from commcareapi.comm_care_data import CommCareAPI, CommCareResources, \
    CommCareResourceValidationError, CommCareSuiteXML, CommCareCase
from commcareapi.xform import XForm


@pytest.fixture(scope="session")
def apitest_credentials():
    test_dir = os.path.abspath(os.path.dirname(__file__))
    credentials = os.path.join(test_dir, 'credentials.json')
    with open(credentials, "r") as f:
        credentials = json.load(f)
    return credentials


@pytest.fixture(scope="session")
def apitest_resource(apitest_credentials):
    test_api = CommCareAPI(apitest_credentials.get('domain'),
                           apitest_credentials.get('user'),
                           apitest_credentials.get('password'))
    test_resource = CommCareResources(test_api)
    return test_resource


@pytest.fixture(scope="session")
def apitest_resource_list_cases_response(apitest_resource):
    return apitest_resource.list_cases()


class TestValidateAPIResponses():

    validator_configuration = {'a': None, 'b': None, 'c': None}

    def test_differing_keys_raises_exception(self):
        """ If the API response keys differ from those given in our validator
            an exception should be raised """

        actual = {'a': None, 'd': None, 'c': None}

        with pytest.raises(CommCareResourceValidationError):
            CommCareResources.validate(actual, self.validator_configuration)

    def test_matching_keys_passes_validation(self):
        actual = {'a': None, 'b': None, 'c': None}
        assert  CommCareResources.validate(
            actual, self.validator_configuration) is True

    def test_subset_of_keys_in_input_is_valid(self):
        actual = {'a': None, 'b': None, 'c': None, 'e': None}
        assert  CommCareResources.validate(
            actual, self.validator_configuration) is True


class TestCommCareCaseUtils():

    @pytest.mark.apitest
    def test_resource_response_contains_a_list_of_dicts_with_valid_cases(
            self, apitest_resource_list_cases_response):

        assert isinstance(apitest_resource_list_cases_response, list)
        for case in apitest_resource_list_cases_response:
            # Validate cases
            assert CommCareResources.validate(
                case.case_data,
                case.case_validator) is True
            # Validate case_properties
            assert CommCareResources.validate(
                case.case_data.get('properties'),
                case.case_properties_validator) is True

    @pytest.mark.apitest
    def test_changing_limit_changes_number_of_responses(
            self, apitest_credentials):

        limit_test = [1, 2, 3]

        for limit in limit_test:
            test_api = CommCareAPI(apitest_credentials.get('domain'),
                                   apitest_credentials.get('user'),
                                   apitest_credentials.get('password'),
                                   limit=limit)
            test_resource = CommCareResources(test_api)
            response_list = test_resource.list_cases()
            assert len(response_list) == limit

    @pytest.mark.apitest
    def test_resource_response_gives_valid_form(
            self, apitest_resource, apitest_resource_list_cases_response):

        assert isinstance(apitest_resource_list_cases_response, list)
        # Need there to be one or more cases
        assert len(apitest_resource_list_cases_response) >= 1
        xform_ids = apitest_resource_list_cases_response[0].xform_ids
        form = apitest_resource.form(xform_ids[0])
        assert CommCareResources.validate(
            form.form_data,
            form.form_validator) is True
        assert CommCareResources.validate(
            form.form_data.get('form'),
            form.form_form_validator) is True


valid_suite = """
        <suite version="25">
            <xform>
            <resource id="c9d5180df5" version="25">
              <location authority="local">./modules-0/forms-0.xml</location>
              <location authority="remote">./modules-0/forms-0.xml</location>
            </resource>
            </xform>
            <xform>
            <resource id="c9d" version="25">
              <location authority="local">./modules-0/forms-1.xml</location>
              <location authority="remote">./modules-0/forms-1.xml</location>
            </resource>
            </xform>
        </suite>"""


class TestCommCareSuiteXML():

    @pytest.fixture(scope="session")
    def ccfd(self, apitest_credentials):
        ccfd = CommCareSuiteXML(
            apitest_credentials.get('domain'),
            apitest_credentials.get('app_id'))
        ccfd.suite_xml = ccfd.get_suite_xml()
        ccfd.xform_dict = CommCareSuiteXML.get_xform_locations(ccfd.get_suite_xml())
        return ccfd

    @pytest.mark.apitest
    def test_suite_xml_gives_xml_with_valid_suite(self, ccfd):
        assert ccfd.validate_suite_xml(ccfd.suite_xml)

    def test_get_xform_definition_location_dictionary(self):
        xform_dict = CommCareSuiteXML.get_xform_locations(valid_suite)
        expected_dict = {"c9d5180df5v25":"./modules-0/forms-0.xml",
                         "c9dv25":"./modules-0/forms-1.xml"}
        assert xform_dict == expected_dict

    @pytest.mark.apitest
    def test_get_xform_gives_a_correct_xform(self, ccfd):
        """
        If this test fails, one of the following has changed:
        - the url to download the xform has changed
        - data_node's tag_xmlns no longer exists (used for matching to forms)
        Note:
        - confirming that tag_xmlns matches a form in the app is outside the
        scope of this test.
        - asserting the len(xmlns) > 20 is arbitrary, but it should be a
        relatively long string.
        """
        resource_snippet = ccfd.xform_dict.popitem()
        xform = ccfd.get_xform_definition(resource_snippet[1]) # Test download
        xform = XForm(xform)
        xmlns = xform.data_node.tag_xmlns
        assert len(xmlns) > 20

    def test_get_suite_version_returns_version_from_xml(self):
        test_dir = os.path.abspath(os.path.dirname(__file__))
        fixture = os.path.join(test_dir, 'test_fixtures', 'suite.xml')
        with open(fixture, 'r') as f:
            suite_xml = f.read()
        assert CommCareSuiteXML.get_suite_version(suite_xml) == "25"

class TestCommCareSuiteValidation():
    def test_passes_correct_suite_markup(self):
        assert CommCareSuiteXML.validate_suite_xml(valid_suite) is True

    def test_rejects_missing_suite_tags(self):
        invalid_suite = "<foo></foo>"
        with pytest.raises(CommCareResourceValidationError) as error:
            CommCareSuiteXML.validate_suite_xml(invalid_suite)
        expectederror = 'Suite tag not at root'
        assert str(error.value).find(expectederror) >= 0, \
            "Did not find correct error message: %s" % expectederror

    def test_rejects_missing_version_attribute(self):
        invalid_suite = "<suite></suite>"
        with pytest.raises(CommCareResourceValidationError) as error:
            CommCareSuiteXML.validate_suite_xml(invalid_suite)
        expectederror = 'Missing version attribute on suite'
        assert str(error.value).find(expectederror) >= 0, \
            "Did not find correct error message: %s" % expectederror

    def test_rejects_missing_xform_tags(self):
        invalid_suite = "<suite></suite>"
        with pytest.raises(CommCareResourceValidationError) as error:
            CommCareSuiteXML.validate_suite_xml(invalid_suite)
        expectederror = 'Suite does not contain one or more xforms'
        assert str(error.value).find(expectederror) >= 0, \
            "Did not find correct error message: %s" % expectederror

    def test_rejects_missing_resource_tags(self):
        invalid_suite = "<suite><xform></xform></suite>"
        with pytest.raises(CommCareResourceValidationError) as error:
            CommCareSuiteXML.validate_suite_xml(invalid_suite)
        expectederror = 'Missing resource tags in xform'
        assert str(error.value).find(expectederror) >= 0, \
            "Did not find correct error message: %s" % expectederror

    def test_rejects_missing_resource_tags_in_one(self):
        invalid_suite = """<suite>
                            <xform>
                                <resource id="" version=""></resource>
                            </xform>
                            <xform></xform>
                        </suite>"""
        with pytest.raises(CommCareResourceValidationError) as error:
            CommCareSuiteXML.validate_suite_xml(invalid_suite)
        expectederror = 'Missing resource tags in xform'
        assert str(error.value).find(expectederror) >= 0, \
            "Did not find correct error message: %s" % expectederror

    def test_rejects_missing_id_attrib_in_resource(self):
        invalid_suite = "<suite><xform><resource></resource></xform></suite>"
        with pytest.raises(CommCareResourceValidationError) as error:
            CommCareSuiteXML.validate_suite_xml(invalid_suite)
        expectederror = 'Missing id attribute in resource'
        assert str(error.value).find(expectederror) >= 0, \
            "Did not find correct error message: %s" % expectederror

    def test_rejects_missing_version_attrib_in_resource(self):
        invalid_suite = """<suite>
                            <xform><resource id=""></resource></xform>
                        </suite>"""
        with pytest.raises(CommCareResourceValidationError) as error:
            CommCareSuiteXML.validate_suite_xml(invalid_suite)
        expectederror = 'Missing version attribute in resource'
        assert str(error.value).find(expectederror) >= 0, \
            "Did not find correct error message: %s" % expectederror

    def test_rejects_missing_location_tags(self):
        invalid_suite = """<suite>
                            <xform>
                                <resource id="" version=""></resource>
                            </xform>
                        </suite>"""
        with pytest.raises(CommCareResourceValidationError) as error:
            CommCareSuiteXML.validate_suite_xml(invalid_suite)
        expectederror = 'Missing remote location tags in resource'
        assert str(error.value).find(expectederror) >= 0, \
            "Did not find correct error message: %s" % expectederror

    def test_rejects_missing_remote_location_attrib(self):
        invalid_suite = """<suite>
                            <xform>
                                <resource id="" version="">
                                    <location></location>
                                </resource>
                            </xform>
                        </suite>"""
        with pytest.raises(CommCareResourceValidationError) as error:
            CommCareSuiteXML.validate_suite_xml(invalid_suite)
        expectederror = 'Missing authority attribute in location'
        assert str(error.value).find(expectederror) >= 0, \
            "Did not find correct error message: %s" % expectederror

class TestCommCareCase():

    @pytest.fixture
    def case_fixture(self):
        test_dir = os.path.abspath(os.path.dirname(__file__))
        fixture = os.path.join(test_dir, 'test_fixtures', 'case_response.json')
        with open(fixture, 'r') as f:
            case_data = f.read()
        return CommCareCase(case_data)

    def test_xform_ids_property(self, case_fixture):
        expected_xform_ids = ["315c73e1-bc8b-40bb-8c1e-11aa94774ba2",
                              "PG25GC8U3RUKE34TYRGYA15UJ",
                              "PU2H67JR3KX99X3H4SYQG6DRJ",
                              "03df7515-c7dc-4cac-bde3-aea14c6e45a8"]
        assert case_fixture.xform_ids == expected_xform_ids

    def test_case_properties_property(self, case_fixture):
        expected_case_properties = {
        "testmodule1_form_createcase_question1": "Updated info",
        "testmodule1_form_createcase_question3": "",
        "testmodule1_form_createcase_question2": "",
        "case_type": "testmodule1_case",
        "case_name": "Test Data 1 - Question1",
        "testmodule1_form_createcase_group_question3": "",
        "testmodule1_form_createcase_group_question2": "",
        "testmodule1_form_createcase_group_question1": "",
        "testmodule1_form_createcase_question4": "",
        "date_opened": "2013-02-11T19:59:49",
        "external_id": "null",
        "owner_id": "cf0b7d3f231d2c384d3259d4f04d3978"
        }
        expected = set(expected_case_properties)
        actual = set(case_fixture.case_properties)
        assert expected == actual

    def test_case_id_property(self, case_fixture):
        expected_case_id = "d54f6068-cb66-4b99-92b1-a923afff87cb"
        assert case_fixture.case_id == expected_case_id

    def test_case_name_property(self, case_fixture):
        expected_case_name = "Test Data 1 - Question1"
        assert case_fixture.case_name == expected_case_name

    def test_case_type_property(self, case_fixture):
        expected_case_type = "testmodule1_case"
        assert case_fixture.case_type == expected_case_type
