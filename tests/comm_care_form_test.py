import os
import pytest
import json
import pprint
from commcareapi.comm_care_data import CommCareForm
from commcareapi.xform import XForm


def form_data(fixture):
    test_dir = os.path.abspath(os.path.dirname(__file__))
    fixture = os.path.join(test_dir, 'test_fixtures', fixture)
    with open(fixture, 'r') as f:
        form_data = json.load(f)
    return form_data


@pytest.fixture()
def comm_care_form_initial():
    return CommCareForm(form_data('form_response.json'))


@pytest.fixture()
def comm_care_form_corrupt():
    return CommCareForm(form_data('form_response_corrupt.json'))


@pytest.fixture()
def comm_care_form_update():
    return CommCareForm(form_data('form_response_2.json'))


@pytest.fixture(params=['form_response.json',
                        'form_response_2.json'])
def comm_care_forms_create_and_update(request):
    return CommCareForm(form_data(request.param))


class TestCommCareForm():

    def test_form_has_case(self, comm_care_form_initial):
        assert comm_care_form_initial.has_case is True

    def test_form_created_case(self, comm_care_form_initial):
        assert comm_care_form_initial.created is True

    def test_update_form_not_created(self, comm_care_form_update):
        assert comm_care_form_update.created is False

    def test_update_form_is_updated(self, comm_care_form_update):
        assert comm_care_form_update.updated is True

    def test_create_and_update_forms_have_date_modified(self,
            comm_care_forms_create_and_update):
        assert comm_care_forms_create_and_update.date_modified is not None

    def test_get_xmlns_id_returns_correct_id(self):
        xmlns = "http://openrosa.org/formdesigner/6B10FA6F-DBCB-4DAA-A310-646E"

        form_data = {"form": {"@xmlns": xmlns}}

        form = CommCareForm(form_data)
        expected_xmlns_id = xmlns
        assert form.xmlns_id, expected_xmlns_id

    def test_get_xmlns_unique_id_returns_correct_id(self):
        xmlns = "http://openrosa.org/formdesigner/6B10FA6F-DBCB-4DAA-A310-646E"
        version = "22"

        form_data = {"form": {"@xmlns": xmlns,
                              "@version": version}}

        form = CommCareForm(form_data)
        expected_xmlns_unique_id = xmlns + "v" + version
        assert form.xmlns_unique_id, expected_xmlns_unique_id

    def test_form_case_id_returns_case_id(self):
        form_data = {"form": {"case": {"@caseid": "bananas"}}}
        form = CommCareForm(form_data)
        assert form.form_case_id == "bananas"

    def test_is_form_valid_passes_with_good_data(self,
                                                 comm_care_form_initial):
        assert comm_care_form_initial.is_form_valid()

    def test_is_form_valid_returns_false_with_corrupt_data(self,
                                                           comm_care_form_corrupt):
        assert comm_care_form_corrupt.is_form_valid() is False


class TestHumaniseFormData():

    form_definition = [{
        'label': 'Group One',
        'value': '/data/group1',
        'tag': 'group',
        'children': [{
            'label': 'APPLE',
            'value': '/data/group1/code1',
            'tag': 'input'
            }, {
            'label': 'BANANA',
            'value': '/data/group1/code2',
            'tag': 'input'
            }, {
            'label': 'Style',
            'value': '/data/group1/code3',
            'tag': 'select1',
            'options': [{
                'label': 'Juiced',
                'value': 'juice'
                }, {
                'label': 'Sliced',
                'value': 'slice'
                }],
            }, {
            'label': 'Multi Select',
            'value': '/data/group1/code4',
            'tag': 'select',
            'options': [{
                'label': 'Select 1',
                'value': 'select1'
                }, {
                'label': 'Select 2',
                'value': 'select2'
                }],
            }]
        }, {
        'label': 'PEAR',
        'value': '/data/code2',
        'tag': 'input'
        }]

    def test_form_data_nodes_are_resolved_to_fieldnames(self):
        form_data = {  'form': {
                                'group1': {
                                    'code2': 2,
                                    'code1': 1,
                                    'code3': 'slice',
                                    'code4': 'select2 select1',
                                    },
                                'code2': 0,
                                }
                                }

        expected = [(
                'Group One', [
                    ('APPLE', 1),
                    ('BANANA', 2),
                    ('Style', 'Sliced'),
                    ('Multi Select', 'Select 1, Select 2'),
                    ],
                ), 
                ('PEAR', 'No Data')]

        form = CommCareForm(form_data)
        actual = form.make_human_readable(self.form_definition)
        assert actual == expected

    def test_missing_data_form_data_nodes_display_no_data(self):
        form_data = { 'form': {
                                'group1': {
                                    'code1': 1,
                                    },
                                'code2': 0,
                                }
                               }

        expected = [
                ('Group One', [
                    ('APPLE', 1),
                    ('BANANA', 'No Data'),
                    ('Style', 'No Data'),
                    ('Multi Select', 'No Data'),
                    ],
                ),
                ('PEAR', 'No Data')]

        form = CommCareForm(form_data)
        actual = form.make_human_readable(self.form_definition)
        assert actual == expected

    def test_can_handle_select1_with_no_data_in_it(self):
        test_dir = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(test_dir, 'test_fixtures', 'form_data_with_0len_select1.json'), 'r') as f:
            form_data = f.read()
        with open(os.path.join(test_dir, 'test_fixtures', 'form_definition_for_0len.xml'), 'r') as f:
            xform = XForm(f.read())
        form = CommCareForm(json.loads(form_data))
        human_readable = form.make_human_readable(xform.get_questions(['en']))
        assert True, "If this test is broken an assertion error will be raised \
                        while .make_human_readable() is running"

    """
    Form data:
    {
        u'@uiVersion': u'1', 
        u'case': {
            u'@xmlns': u'http://commcarehq.org/case/transaction/v2',
            u'@case_id': u'8f6ebc41-5c66-47ec-9e60-bccdd7529938',
            u'@user_id': u'de6ed25cd6baf50106f146182a824a46',
            u'@date_modified': datetime.datetime(2013, 11, 18, 17, 52, 13),
            u'update': u''},
        u'@name': u'Membership', 
        u'#type': u'data', 
        u'meta': {
            u'@xmlns': u'http://openrosa.org/jr/xforms',
            u'username': u'mobile5',
            u'instanceID': u'17348205-481d-4c0c-b952-f0b552145314',
            u'userID': u'de6ed25cd6baf50106f146182a824a46',
            u'timeEnd': datetime.datetime(2013, 11, 18, 17, 52, 13),
            u'appVersion': {
                u'@xmlns': u'http://commcarehq.org/xforms',
                u'#text': u'v2.9.0 (6b1e95-e699cd-unvers-2.1.0-Nokia/S40-native-input) build 23681 App #153 b:2013-Sep-30 r:2013-Nov-18'
                },
            u'timeStart': datetime.datetime(2013, 11, 18, 17, 49, 11),
            u'deviceID': u'354146053394360'
        }, 
        u'group_membership': [{
            u'reason_left_group': u'Gtggh',
            u'group_position': [{
                u'date_left_position':
                u'', u'position':u'Fff',
                u'date_took_position': u'',
                u'reason_left_position': u'Gggg'
                },{
                u'date_left_position': u'',
                u'position': u'Ggggg', 
                u'date_took_position': datetime.date(2012, 12, 12),
                u'reason_left_position': u''
                }],
            u'date_left': datetime.date(2013, 11, 18),
            u'group_type': u'Asc',
            u'date_joined': u''
        },{
            u'reason_left_group': u'Closed',
            u'group_position': {
                u'date_left_position': u'',
                u'position': u'Boss',
                u'date_took_position': datetime.date(2013, 12, 12),
                u'reason_left_position': u'Merged'
                },
            u'date_left': u'',
            u'group_type': u'Hhhh',
            u'date_joined': u''
        }], 
            u'@xmlns': u'http://openrosa.org/formdesigner/0BB4FA46-2EB6-4765-81E0-2FC5CA072EF5',
            u'@version': u'153'
    }
    
    Form definition:
    [{
        'tag': 'group', 
        'children': [{
            'tag': 'input',
            'value': '/data/group_membership/group_type',
            'label': '6. Group name'
        },{
            'tag': 'input',
            'value': '/data/group_membership/date_joined',
            'label': '7. Date joined'
        },{
            'tag': 'input',
            'value': '/data/group_membership/date_left',
            'label': '8. Date left'
        },{
            'tag': 'input',
            'value': '/data/group_membership/reason_left_group',
            'label': '9. Reason for leaving'
        },{
            'tag': 'group',
                'children': [{
                    'tag': 'input',
                    'value': '/data/group_membership/group_position/position',
                    'label': '10. Position'
            },{
                    'tag': 'input',
                    'value': '/data/group_membership/group_position/date_took_position',
                    'label': '11. Date took position'
            },{
                    'tag': 'input',
                    'value': '/data/group_membership/group_position/date_left_position',
                    'label': '12. Date left position'
            },{
                    'tag': 'input',
                    'value': '/data/group_membership/group_position/reason_left_position',
                    'label': '13. Reason for leaving'
            }],
                'value': '/data/group_membership',
                'label': 'Positions held'}], 
            'value': '',
            'label': 'Group membership'
        },{
            'tag': 'hidden',
            'value': '/data/case/update',
            'label': '/data/case/update'
        },{
            'tag': 'hidden',
            'value': '/data/meta/deviceID',
            'label': '/data/meta/deviceID'
        },{
            'tag': 'hidden',
            'value': '/data/meta/timeStart',
            'label': '/data/meta/timeStart'
        },{
            'tag': 'hidden',
            'value': '/data/meta/timeEnd',
            'label': '/data/meta/timeEnd'
        },{
            'tag': 'hidden', 
            'value': '/data/meta/username',
            'label': '/data/meta/username'
        },{
            'tag': 'hidden',
            'value': '/data/meta/userID',
            'label': '/data/meta/userID'
        },{
            'tag': 'hidden',
            'value': '/data/meta/instanceID',
            'label': '/data/meta/instanceID'
        },{
            'tag': 'hidden',
            'value': '/data/meta/appVersion',
            'label': '/data/meta/appVersion'
        }]
    """
    def test_children_parsed(self):
        form_definition = [{
        'tag': 'group', 
        'children': [{
            'tag': 'input',
            'value': '/data/group_membership/group_name',
            'label': 'Group name'
        },{
            'tag': 'input',
            'value': '/data/group_membership/reason_left_group',
            'label': 'Reason for leaving'
        },{
            'tag': 'group',
                'children': [{
                    'tag': 'input',
                    'value': '/data/group_membership/group_position/position',
                    'label': 'Position'
            }],
                'value': '/data/group_membership/group_position',
                'label': 'Positions held'}], 
            'value': '/data/group_membership',
            'label': 'Group membership'
        }]

        form_data = \
        {
            'form':
            {
                'group_membership':
                [{
                    'reason_left_group': 'Moved to other village',
                    'group_position':
                    [{
                        'position':'Secretary',
                    },
                    {
                        'position': 'Chair', 
                    }],
                    'group_name': 'SHG',
                },
                {
                    'reason_left_group': 'Closed',
                    'group_position':
                    {
                        'position': 'Time keeper',
                    },
                    'group_name': 'SHG Grassroots Federation',
                }],
            }
        }
        
        expected = \
        [('Group membership', [
            ('Group name', 'SHG'),
            ('Reason for leaving', 'Moved to other village'),
            ('Positions held', [
                ('Position', 'Secretary'),
                ('Position', 'Chair')]),
            ('Group name', 'SHG Grassroots Federation'),
            ('Reason for leaving', 'Closed'),
                ('Positions held',  [
                    ('Position', 'Time keeper')])
            ])]
        
        form = CommCareForm(form_data)
        actual = form.make_human_readable(form_definition)
        
        assert actual == expected
