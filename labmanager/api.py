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


class LabManager(object):
    LIBRARY_CONFIGURATIONS = 1
    def __init__(self, client):
        self._client = client

    def list_library_configurations(self):
        return self._client.service.ListConfigurations(
            self.LIBRARY_CONFIGURATIONS)
