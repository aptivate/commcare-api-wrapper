import os
import pytest
import json
import mock

from commcareapi.comm_care_data import (
        CommCareAPI,
        CommCareResources
    )

class TestCommCareFixture():
    
    def test_resources_has_fixture_api(self):
        api_mock = mock.Mock()
        CommCareResources(api_mock)
        api_mock.add_resource.assert_called_with('fixture')

    def test_fixture_resource_has_objects(self):
        api_mock = mock.Mock()
        
        data = mock.Mock(data=dict(objects="foo"))
        get = mock.Mock()
        get.return_value = data
        api_mock.fixture.get = get
        
        resource = CommCareResources(api_mock)
        fixture_data = resource.fixture()
        
        api_mock.fixture.get.assert_any_call()
        assert fixture_data == "foo" 
    