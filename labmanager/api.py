from suds.client import Client
from suds.sudsobject import asdict

# TODO: These are the API calls not yet implemented.
# ConfigurationCapture
# ConfigurationClone
# ConfigurationSetPublicPrivate
# GetCurrentOrganizationName
# GetCurrentWorkspaceName

# These are the API calls that I don't plan on supporting.
# GetConfigurationByName
# LiveLink
# SetCurrentOrganizationByName
# SetCurrentWorkspaceByName
# ConfigurationPerformAction - doesn't work. Well, the API
#   call succeeds, but it doesn't actually do anything.
#   I can go into the gui and perform actions on the
#   configuration, so the feature is working, but there
#   seems to be an issue with trying to do this via the API.


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
    return asdict(suds_type)


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
    NON_FENCED = 1
    FENCE_BLOCK_IN_AND_OUT = 2
    FENCE_ALLOW_OUT_ONLY = 3
    FENCE_ALLOW_IN_AND_OUT = 4
    # These are the actions that can be used with
    # perform_machine_action
    POWER_ON = 1
    POWER_OFF = 2
    SUSPEND = 3
    RESUME = 4
    RESET = 5
    SNAPSHOT = 6
    REVERT = 7
    SHUTDOWN = 8

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

    @single_dict
    def show_configuration_by_name(self, name):
        # I am assuming that by calling this API your'e looking
        # for a specific configuration by name, not all configurations
        # matching this name.
        return self._client.service.GetSingleConfigurationByName(name)

    @list_of_dicts
    def list_machines(self, config_id):
        return self._client.service.ListMachines(config_id)[0]

    @single_dict
    def get_machine(self, machine_id):
        return self._client.service.GetMachine(machine_id)

    @single_dict
    def get_machine_by_name(self, config_id, name):
        return self._client.service.GetMachineByName(config_id, name)

    def undeploy_configuration(self, config_id):
        self._client.service.ConfigurationUndeploy(config_id)

    def deploy_configuration(self, config_id, fence_mode):
        self._client.service.ConfigurationDeploy(config_id, False, fence_mode)

    def checkout_configuration(self, config_id, name):
        # This is likely not to be terribly useful.  If you keep
        # the default workspace of "Main", you'll run into errors
        # that look something like:
        # "Expecting single row, got multiple rows for: SELECT * FROM
        # BucketWithParent WHERE  name = N'Main'"
        # You can either bribe the labmanager admins to create a unique
        # workspace name for you, or I can try to make this work
        # with the internal API.

        # Return type is an int so we don't need to do any custom
        # conversions.
        return self._client.service.ConfigurationCheckout(config_id, name)

    def delete_configuration(self, config_id):
        self._client.service.ConfigurationDelete(config_id)

    def perform_machine_action(self, action, machine_id):
        """Perform an action on a machine.

        @param action: The action to perform.  Use one of the
            class attributes POWER_ON, POWER_OFF,
            SUSPEND, RESUME, RESET, SNAPSHOT, REVERT,
            SHUTDOWN.
        @param machine_id: The id of the machine.

        """
        # This is not a typo, the pdf docs are wrong, the args
        # are actually switched.
        self._client.service.MachinePerformAction(machine_id, action)
