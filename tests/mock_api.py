import mock

from commcareapi.comm_care_data import CommCareResources


def get_mock_api_resource(resource_name, data):
    """
        CommCareResources takes a drest API instance and attaches resources
        using api.add_resource(resource_name).

        This mock api will return data for '.get()' on the given resource
    """

    # a mock resource.get() returning 'data'
    get_mock = mock.Mock(return_value=mock.Mock(data=data))

    resource_mock = mock.Mock()
    resource_mock.get = get_mock

    api_mock = mock.Mock()
    setattr(api_mock, resource_name, resource_mock)
    resources = CommCareResources(api_mock)
    api_mock.add_resource.assert_any_call(resource_name)
    return resources
