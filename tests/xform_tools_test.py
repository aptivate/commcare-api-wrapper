import os
import pytest

from commcareapi.xform import XForm


class TestGetQuestions:

    @pytest.fixture
    def xform_questionlist(self):
        test_dir = os.path.abspath(os.path.dirname(__file__))
        raw_xform_file = os.path.join(test_dir, 'test_fixtures', 'test_xform_definition.xml')
        raw_xform = open(raw_xform_file, 'r').read()
        xform_test = XForm(raw_xform)
        return xform_test.get_questions(['en'])

    def test_options_list_produced_when_tag_is_select1(self, xform_questionlist):
        for question_dict in xform_questionlist:
            if question_dict['tag'] == 'select1':
                assert 'options' in question_dict, \
                    "The question dictionary does not have options entry"

    def test_options_list_produced_when_tag_is_select(self, xform_questionlist):
        for question_dict in xform_questionlist:
            if question_dict['tag'] == 'select':
                assert 'options' in question_dict, \
                    "The question dictionary does not have options entry"

    def get_groups(self, questionlist):
        groups = [question for question in questionlist
                  if question['tag'] == 'group']
        return groups

    # The following three tests are all VERY dependent on the specific data
    # in test_xform_definition including the order which the data appears.

    def test_group_node_creates_group_tag(self, xform_questionlist):
        groups = self.get_groups(xform_questionlist)
        assert len(groups) == 2, "Wrong number of group tags found"

    def test_group_node_has_children_list(self, xform_questionlist):
        group = self.get_groups(xform_questionlist)[1]
        assert 'children' in group
        children_list = group['children']
        assert isinstance(children_list, list)
        assert len(children_list) == 3, "Expected 3 child questions"

    def test_repeat_questions_are_in_a_group(self, xform_questionlist):
        group = self.get_groups(xform_questionlist)[0]
        assert 'children' in group
        children_list = group['children']
        assert children_list[0]['value'] == \
            "/data/repeat/testmodule1_form_createcase_repeat_question1"
