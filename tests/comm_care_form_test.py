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
                    # Note that CommCare does not return a list of dicts for a
                    # single repeat group value;
                    'group_position': {
                        'position': 'Time keeper',
                    },
                    'group_name': 'SHG Grassroots Federation',
                }],
            }
        }


        # repeat-group data should be contained in a list of lists when there
        # are multiple rows.
        # (treat them like tabular data, one row per loop).

        # a repeat group with a single response appears as a normal question
        # group (a list containing questions). - this is how CommCare sends the
        # data.

        expected = \
        [('Group membership',
            [
                [
                    ('Group name', 'SHG'),
                    ('Reason for leaving', 'Moved to other village'),
                    ('Positions held', [
                        [
                            ('Position', 'Secretary')
                        ],
                        [
                            ('Position', 'Chair')
                        ]
                    ]),
                ],
                [
                    ('Group name', 'SHG Grassroots Federation'),
                    ('Reason for leaving', 'Closed'),
                    ('Positions held', [
                    # Note that a single repeat is treated as a normal
                    # question, rather than a list of lists;
                            ('Position', 'Time keeper')
                    ])
                ]
            ]
        )]

        form = CommCareForm(form_data)
        actual = form.make_human_readable(form_definition)
        
        assert actual == expected
