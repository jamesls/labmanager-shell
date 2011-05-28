from suds.client import Client


def create_soap_client(config):
    # config is an instance of config.APIConfig
    client = Client(config.url, timeout=config.timeout)
    headers = client.factory.create('AuthenticationHeader')
    headers.username = config.username
    headers.password = config.password
    headers.organizationname = config.organization
    headers.workspacename = config.workspace
    client.set_options(soapheaders=headers)
    return client


def suds_to_dict_type(suds_type):
    # sudsobject is magic.  Let's give the user
    # something that's simpler to work with.  Hopefully
    # they don't miss the types.
    return dict(list(iter(suds_type)))


def list_of_dicts(func):
    def _convert_to_list_of_dicts(*args, **kwargs):
        collection_suds_type = func(*args, **kwargs)
        simple_list = []
        for suds_type in collection_suds_type:
            simple_list.append(suds_to_dict_type(suds_type))
        return simple_list
    return _convert_to_list_of_dicts


def single_dict(func):
    def _convert_to_dict(*args, **kwargs):
        suds_type = func(*args, **kwargs)
        return suds_to_dict_type(suds_type)
    return _convert_to_dict


class LabManager(object):
    WORKSPACE_CONFIGURATION = 1
    LIBRARY_CONFIGURATIONS = 2
    def __init__(self, client):
        self._client = client

    @list_of_dicts
    def list_library_configurations(self):
        rval = self._client.service.ListConfigurations(
            self.LIBRARY_CONFIGURATIONS)[0]
        return rval

    @list_of_dicts
    def list_workspace_configurations(self):
        return self._client.service.ListConfigurations(
            self.WORKSPACE_CONFIGURATION)[0]

    @list_of_dicts
    def list_all_configurations(self):
        workspace = self._client.service.ListConfigurations(
            self.WORKSPACE_CONFIGURATION)[0]
        library = self._client.service.ListConfigurations(
            self.LIBRARY_CONFIGURATIONS)[0]
        return workspace + library

    @single_dict
    def show_configuration(self, config_id):
        return self._client.service.GetConfiguration(config_id)

    @list_of_dicts
    def list_machines(self, config_id):
        return self._client.service.ListMachines(config_id)[0]
