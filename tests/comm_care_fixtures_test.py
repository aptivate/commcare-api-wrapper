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
            {'objects': 'foo'}
        )

        fixture_data = resource.fixture()

        # api_mock.fixture.get.assert_any_call()
        assert fixture_data == "foo"
