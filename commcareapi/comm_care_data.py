import urllib2
import string
import json
import drest
from jsonpath import jsonpath

from .xform import parse_xml

HOST = 'https://www.commcarehq.org'


class CommCareAPI(drest.api.API):

    def __init__(self, domain, user, password, limit=10000):
        baseurl = self.commcare_base(domain, 'v0.3')
        extra_params = dict(limit=limit)
        super(CommCareAPI, self).__init__(baseurl=baseurl,
                                          extra_params=extra_params,
                                          auth_mech='basic')
        super(CommCareAPI, self).auth(user, password)

    def commcare_base(self, domain, version):
        return '{host}/a/{domain}/api/{version}/'.format(
            host=HOST,
            domain=domain,
            version=version)


class CommCareForm(object):

    form_validator = {
        u"form": None,
        u"received_on": None,
        u"type": None,
        u"id": None,
        u"metadata": None,
    }

    form_form_validator = {
        u"case": None,
        u"@xmlns": None,
        u"meta": None,
        u"@version": None,
    }

    def __init__(self, form_data):
        self.form_data = form_data
        if not self.is_form_valid:
            raise CommCareResourceValidationError('Form not valid')

    @property
    def case(self):
        matches = jsonpath(self.form_data, '$.form.case')
        if len(matches) == 1:
            return matches[0]
        else:
            return None

    @property
    def has_case(self):
        return True if self.case else False

    @property
    def created(self):
        return 'create' in self.case

    @property
    def updated(self):
        return 'update' in self.case

    @property
    def date_modified(self):
        return self.case.get('@date_modified')

    @property
    def case_updated(self):
        matches = jsonpath(self.form_data, '$.form.case.@case_updated')
        return matches[0]

    @property
    def form_id(self):
        matches = jsonpath(self.form_data, '$.id')
        return matches[0]

    @property
    def xmlns_id(self):
        form_data = self.form_data
        xmlns = form_data['form'].get('@xmlns')
        return xmlns

    @property
    def xmlns_unique_id(self):
        form_data = self.form_data
        version = form_data['form'].get('@version')
        xmlns_unique_id = self.xmlns_id + "v" + version
        return xmlns_unique_id

    @property
    def form_case_id(self):
        return self.form_data['form']['case'].get('@caseid')

    def is_form_valid(self):
        try:
            CommCareResources.validate(self.form_data,
                                       self.form_validator)
            CommCareResources.validate(self.form_data.get('form'),
                                       self.form_form_validator)
            return True
        except CommCareResourceValidationError:
            return False

    def make_human_readable(self, form_definition):
        """
        form_definition is a list of dictionaries retrieved by running
        get_questions on an xform.
        """
        form_data = self.form_data['form']

        def resolve_form_values(form_def, form_data):
            data_nodes = []

            for def_node in form_def:
                path = def_node['value'].split('/')
                name = path[-1]
                tag = def_node['tag']
                value = form_data.get(name)
                label = def_node['label']

                if not value:
                    data_nodes.append((label, "No Data"))
                    continue

                if tag == 'group':
                    children = def_node.get('children', [])

                    if isinstance(value, list):
                        group_nodes = []
                        for repeat_value in value:
                            repeat_groups = resolve_form_values(children, repeat_value)
                            group_nodes.append(repeat_groups)
                    else:
                        group_nodes = resolve_form_values(children, value)
                    data_nodes.append((label, group_nodes))

                elif tag in ['select', 'select1']:
                    options = def_node.get('options', [])

                    values = value.split()
                    selected = [o for o in options if o['value'] in values]

                    if tag == 'select1':
                        assert len(selected) <= 1, \
                            "Expected only one or no options to be selected."

                    labels = [s['label'] for s in selected]
                    selected_text = string.join(labels, ', ')
                    data_nodes.append((label, selected_text))
                else:
                    data_nodes.append((label, value))

            return data_nodes
        return resolve_form_values(form_definition, form_data)


class CommCareCaseValueError(Exception):
    pass

class CommCareCase(object):

    case_validator = {
        u"id": None,
        u"case_id": None,
        u"user_id": None,
        u"date_modified": None,
        u"closed": None,
        u"date_closed": None,
        u"server_date_modified": None,
        u"server_date_opened": None,
        u"xform_ids": None,
        u"properties": None,
        u"indices": None
    }

    case_properties_validator = {
        u"case_name": None,
        u"case_type": None,
        u"date_opened": None,
    }

    # case_data can be both json or dictionary representation of a commcare case
    def __init__(self, case_data):
        if not isinstance(case_data, dict):
            try:
                self.case_data = json.loads(case_data)
            except:
                raise CommCareCaseValueError('Could not parse case_data')
        else:
            self.case_data = case_data
            
        if not self.is_case_valid:
            raise CommCareResourceValidationError('Case not valid')

    def is_case_valid(self):
        try:
            CommCareResources.validate(self.case_data,
                                       self.case_validator)
            CommCareResources.validate(self.case_data.get('properties'),
                                       self.case_properties_validator)
            return True
        except CommCareResourceValidationError:
            return False

    @property
    def case_id(self):
        return self.case_data.get('case_id', None)

    @property
    def xform_ids(self):
        return self.case_data.get('xform_ids', [])

    @property
    def case_properties(self):
        return self.case_data.get('properties', {})

    @property
    def case_name(self):
        return self.case_properties.get('case_name', {})

    @property
    def case_type(self):
        return self.case_properties.get('case_type', "")


class CommCareResourceValidationError(Exception):
    pass


class CommCareResources(object):

    def __init__(self, api):
        api.add_resource('case')
        api.add_resource('form')
        self.api = api

    @classmethod
    def validate(cls, data, rules):
        rules_keys = set(rules.keys())
        data_keys = set(data.keys())

        if rules_keys.issubset(data_keys):
            return True
        else:
            raise CommCareResourceValidationError(str(data_keys - rules_keys))

    def list_cases(self):
        """
        https://www.commcarehq.org/a/[domain]/api/v0.3/case/
        structure of resp;
        -> meta [pagination?]
        -> objects [list of cases]
        """
        resp = self.api.case.get()
        list_cases_data = resp.data.get('objects')
        list_cases = []
        for case in list_cases_data:
            list_cases.append(CommCareCase(case))
        return list_cases

    def case(self, case_id):
        """
        https://www.commcarehq.org/a/[domain]/api/v0.3/case/[case_id]/
        Case as documented:

        case_id         Case UUID   0X9OCW3JMV98EYOVN32SGN4II
        username        User name of case owner
        user_id         UUID user that owns the case 3c5a623af057e23a32ae4000cf291339
        owner_id        UUID group/user that owns the case ac9d34ff59cf6388e4f5804b12276d8a
        case_name       Name of case Rose
        external_id     External ID associated with the case 123456
        case_type       Type of case    pregnant_mother
        date_opened     Date and time case was opened 2011-11-16T14:26:15Z
        date_modified   Date and time case was last modified 2011-12-13T15:09:47Z
        closed          Case status false
        date_closed     Date and time case was closed 2011-12-20T15:09:47Z

        Case as implemented:

        v3 def: corehq/apps/api/resources/v0_3.py
        Also see 'to_json' in casexml-src/casexml/apps/case/models.py::CommCareCase

        id = fields.CharField(attribute='case_id', readonly=True, unique=True)
        case_id = id
        user_id = fields.CharField(attribute='user_id', null=True)
        date_modified = fields.CharField(attribute='date_modified')
        closed = fields.BooleanField(attribute='closed')
        date_closed = fields.CharField(attribute='date_closed', null=True)
        server_date_modified = fields.CharField(attribute='server_date_modified')
        server_date_opened = fields.CharField(attribute='server_date_opened', null=True)
        xform_ids = fields.ListField(attribute='xform_ids')
        properties = fields.DictFild('properties')
        indices = fields.DictField('indices')
        """
        resp = self.api.case.get(case_id)
        return CommCareCase(resp.data)

    def form(self, form_id):
        resp = self.api.form.get(form_id)
        return CommCareForm(resp.data)


class CommCareSuiteXML():
    """
    This is un-supported API functionality so may change.
    We need an app_id from which we can get the suite.xml.
    In this we can get the link to the form.
    """
    def __init__(self, domain, app_id):
        download_url = HOST + '/a/' + domain + '/apps/download/' + app_id
        self.download_url = download_url

    def get_suite_xml(self):
        """
        Calls Commcare to get suite.xml and adds to instance
        """
        url = self.download_url + '/suite.xml'
        suite_xml = urllib2.urlopen(url).read()
        self.validate_suite_xml(suite_xml)
        self.suite_xml = suite_xml
        return suite_xml

    @classmethod
    def validate_suite_xml(cls, suite_xml):
        failures = []

        def build_error():
            return "Suite.xml was not valid. Failures: %s" % failures

        resources = []
        locations = []
        tree = parse_xml(suite_xml)
        xforms = [child for child in tree if child.tag == 'xform']
        if xforms:
            for xform in xforms:
                resources.extend([child for child in list(xform)
                                  if child.tag == 'resource'])
        if resources:
            for resource in resources:
                locations.extend([child for child in list(resource)
                                  if child.tag == 'location'])

        # Validate & build failures list

        if tree.tag != "suite":
            failures.append("Suite tag not at root")

        if not 'version' in tree.attrib:
            failures.append("Missing version attribute on suite")

        if not xforms:
            failures.append("Suite does not contain one or more xforms")

        if xforms:
            if len(xforms) != len(resources):
                    failures.append("Missing resource tags in xform")

        if resources:
            for resource in resources:
                if not 'id' in resource.attrib:
                    failures.append("Missing id attribute in resource")
                    raise CommCareResourceValidationError(build_error())
                if not 'version' in resource.attrib:
                    failures.append("Missing version attribute in resource")
                    raise CommCareResourceValidationError(build_error())

            for location in locations:
                if not 'authority' in location.attrib:
                    failures.append("Missing authority attribute in location")
                    raise CommCareResourceValidationError(build_error())
            # Now leave only remote items
            locations = [location for location in locations
                         if location.attrib['authority'] != 'remote']
            if len(resources) != len(locations):
                    failures.append("Missing remote location tags in resource")

        if not failures:
            return True
        else:
            raise CommCareResourceValidationError(build_error())

    @classmethod
    def get_xform_locations(cls, suite_xml):
        """
        Return a dictionary containing the id and the location
        """
        tree = parse_xml(suite_xml)
        xforms = [child for child in tree if child.tag == 'xform']
        resources = {}
        if xforms:
            for xform in xforms:
                for child in list(xform):
                    if child.tag == 'resource':
                        for location in list(child):
                            if location.attrib['authority'] == 'remote':
                                resource_unique_id = child.attrib['id'] + 'v' + child.attrib['version']
                                resources[resource_unique_id] = location.text
        return resources

    @classmethod
    def get_suite_version(cls, suite_xml):
        tree = parse_xml(suite_xml)
        return tree.attrib['version']

    def get_xform_definition(self, resource_snippet):
        url = self.download_url + resource_snippet.lstrip('.')
        form_definition = urllib2.urlopen(url).read()
        return form_definition
