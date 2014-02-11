import mock

from commcareapi.comm_care_data import (
    CommCareResources
)

from mock_api import get_mock_api_resource


class TestCommCareFixture():

    def test_resources_has_fixture_api(self):
        api_mock = mock.Mock()
        CommCareResources(api_mock)
        api_mock.add_resource.assert_any_call('fixture')

    def test_fixture_resource_has_objects(self):
        resource = get_mock_api_resource(
            'fixture',
            {
                'objects': ['foo'],
                'meta': {}
            }
        )

        fixture_data = resource.fixture()

        assert fixture_data == ['foo']

    def test_fixture_resource_concatenates_paged_data(self):
        def get_data(params):
            
            data = [{
                'objects': ['foo'],
                'meta': {
                    'total_count': 2,
                }
            },
            {
                'objects': ['bar'],
                'meta': {
                    'total_count': 2,
                }
            }]
            
            return mock.Mock(data=data[params['offset']])
        
        resource_mock = mock.Mock()
        resource_mock.get = get_data
    
        api_mock = mock.Mock()
        setattr(api_mock, 'fixture', resource_mock)
        resources = CommCareResources(api_mock)

        fixture_data = resources.fixture()

        assert fixture_data == ['foo', 'bar']
