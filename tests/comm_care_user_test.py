from mock_api import get_mock_api_resource


class TestCommCareUser():

    def test_list_users_resource_has_objects(self):
        resources = get_mock_api_resource(
            'user',
            {'objects': 'bar'}
        )
        users = resources.list_users()
        assert users == "bar"
