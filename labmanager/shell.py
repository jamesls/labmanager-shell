import argparse
import getpass
import cmd
import sys
from pprint import pprint
import textwrap
import rlcompleter
import readline
import logging
import ConfigParser

from texttable import Texttable
import suds

from labmanager import api
from labmanager import config
from labmanager.loghandler import NullHandler

# A mapping from the SOAP returned names
# to the nicer to display names.
DISPLAY_TYPE_MAP = {
    'dateCreated': 'created',
    'fenceMode': 'fencemode',
    'isDeployed': 'deployed',
    'isPublic': 'public',
    'bucketName': 'bucket',
    'internalIP': 'internal',
    'externalIP': 'external',
    'macAddress': 'MAC',
    'OwnerFullName': 'owner',
    'configID': 'config',
}
SOAP_API_EXCEPTION = (
    suds.MethodNotFound,
    suds.PortNotFound,
    suds.ServiceNotFound,
    suds.TypeNotFound,
    suds.BuildError,
    suds.SoapHeadersNotPermitted,
    suds.WebFault,
    suds.transport.TransportError,
)


class LMShell(cmd.Cmd):
    prompt = '(lmsh) '
    LIST_CFG_COLUMNS = ['id', 'name', 'isDeployed', 'type', 'owner']
    LIST_MACHINES_COLUMNS = ['id', 'name', 'internalIP', 'externalIP',
                             'macAddress', 'memory', 'configID']
    ENUM_TYPES = {
        'type': {
            1: 'workspace',
            2: 'library',
        },
        'status': {
            1: 'off',
            2: 'on',
            3: 'suspended',
            4: 'stuck',
            128: 'invalid',
        }
    }

    def __init__(self, lmapi, stdin=None, stdout=None):
        cmd.Cmd.__init__(self, '', stdin, stdout)
        self._lmapi = lmapi

    def complete_list(self, text, line, begidx, endidx):
        subcommands = ['library', 'workspace']
        if not text:
            return subcommands
        return [c for c in subcommands if c.startswith(text)]

    def do_list(self, line):
        """
        List configurations.
        Syntax:

        list [library | workspace]

        List all library and workspace configurations:

            list

        There are several subcommands that can optionally be used.
        List only library configurations:

            list library

        List only workspace configurations:

            list workspace

        """
        configs = self._get_configs(line.strip())
        if not configs:
            return
        columns = self.LIST_CFG_COLUMNS

        table = Texttable(max_width=120)
        table.set_deco(Texttable.HEADER | Texttable.VLINES)
        table.set_cols_align(['l' for l in columns])
        table.set_cols_width([6, 30, 8, 10, 15])
        table.header([DISPLAY_TYPE_MAP.get(c, c) for c in columns])
        rows = self._get_rows(configs, columns)
        table.add_rows(rows, header=False)
        print table.draw()

    def _get_configs(self, config_type):
        if config_type == 'library':
            configs = self._lmapi.list_library_configurations()
        elif config_type == 'workspace':
            configs = self._lmapi.list_workspace_configurations()
        else:
            configs = self._lmapi.list_all_configurations()
        return configs

    def do_show(self, line):
        """
        Show all information for a single configuration.
        Syntax:

        show <configid>

        The config ID can be obtained from the 'list' command.
        """
        configuration = self._lmapi.show_configuration(line.strip())
        pprint(configuration)

    def do_machines(self, line):
        """
        List all machines in a configuration.
        Syntax:

        machines <configid>

        The config ID can be obtained from the 'list' command.

        """
        machines = self._lmapi.list_machines(line.strip())
        if not machines:
            return
        columns = self._get_machine_output_columns(machines)
        table = Texttable(max_width=140)
        table.set_deco(Texttable.HEADER | Texttable.VLINES)
        table.set_cols_align(['l' for l in columns])
        table.header([DISPLAY_TYPE_MAP.get(c, c) for c in columns])
        rows = self._get_rows(machines, columns)
        table.add_rows(rows, header=False)
        print table.draw()

    def _get_machine_output_columns(self, machines):
        return [c for c in self.LIST_MACHINES_COLUMNS if
                c in machines[0]]

    def _get_rows(self, objects, columns):
        rows = []
        for obj in objects:
            row = []
            for col in columns:
                if col in self.ENUM_TYPES:
                    # Using .get() here because sometimes
                    # labmanager returned non documented
                    # types/statuses/etc.
                    row.append(self.ENUM_TYPES[col].get(
                        obj[col], obj[col]))
                elif col in obj:
                    row.append(obj[col])
            rows.append(row)
        return rows

    def do_undeploy(self, line):
        """
        Undeploying a configuration.
        Syntax:

        undeploy <configid>

        """
        config_id = line.strip()
        print "Undeploying config..."
        self._lmapi.undeploy_configuration(config_id)

    def complete_deploy(self, text, line, begidx, endidx):
        subcommands = ['unfenced', 'fenced']
        if not text:
            return subcommands
        return [c for c in subcommands if c.startswith(text)]

    def do_deploy(self, line):
        """
        Deploy a configuration in a workspace.
        Syntax:

        deploy <fenced|unfenced> <configid>

        After the configuration has been deployed, you
        can use the 'machines' command to get a list of
        the IP addresses of the machines.

        """
        args = line.split()
        if len(args) != 2:
            print "wrong number of args"
            return
        fence_mode = self._get_fence_mode_from(args[0])
        config_id = args[1]
        print "Deploying config..."
        self._lmapi.deploy_configuration(config_id, fence_mode)

    def _get_fence_mode_from(self, mode):
        if mode == 'fenced':
            return self._lmapi.FENCE_ALLOW_IN_AND_OUT
        elif mode == 'unfenced':
            return self._lmapi.NON_FENCED

    def do_checkout(self, line):
        """
        Checkout a configuration from the library to the workspace.
        Syntax:

        checkout <configid> <workspacename>

        Where the configid is the ID of the configuration as it
        currently exists in the library, and workspacename is the
        name you'd like the configuration to have in the workspace.
        After a configuration has been checked out, it can then
        be deployed (though keep in mind the newly checked out
        workspace configuration will have a different configid that
        you'll need to use to deploy it.

        Due to bug's in Lab Manager 4.x, this command will fail
        if multiple organizations have the same workspace name
        (this is likely if your workspace name is 'Main').  It
        might be possible to work around this using the internal
        SOAP api, but this is currently not implemented.

        Another way to work around this is to create a unique
        workspace name (you will need admin privileges to do so).

        """
        args = line.split()
        if len(args) != 2:
            print "wrong number of args"
        config_id = args[0]
        workspace_name = args[1]
        print "Checking out config..."
        checkout_id = self._lmapi.checkout_configuration(config_id,
                                                         workspace_name)
        print "Config ID of checked out configuration:", checkout_id

    def do_delete(self, line):
        """
        Delete a configuration.
        Syntax:

        delete <configid>

        """
        print "Deleting config..."
        self._lmapi.delete_configuration(line.strip())

    def do_EOF(self, line):
        print
        return True

    def do_quit(self, line):
        return True

    def do_help(self, line):
        if line:
            try:
                func = getattr(self, 'help_' + line)
            except AttributeError:
                try:
                    doc = getattr(self, 'do_' + line).__doc__
                    if doc:
                        self.stdout.write("%s\n" % textwrap.dedent(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % (self.nohelp % (line,)))
                return
            func()
        else:
            cmd.Cmd.do_help(self, line)

    def onecmd(self, line):
        try:
            return cmd.Cmd.onecmd(self, line)
        except SOAP_API_EXCEPTION, e:
            sys.stderr.write("ERROR: %s\n" % e)
            return ReturnCode(1)

    def postcmd(self, stop, line):
        if isinstance(stop, ReturnCode):
            return None
        return stop


class ReturnCode(object):
    def __init__(self, return_code):
        self.return_code = return_code

    def __nonzero__(self):
        return False


def get_cmd_line_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostname', help="The hostname of the "
                        "Lab Manager server.")
    parser.add_argument('--username', help="The Lab Manager username.")
    parser.add_argument('--organization', help="The organization name that "
                        "contains the objects on which you want to perform "
                        "operations.")
    parser.add_argument('--workspace', default='Main', help="The workspace "
                        "name that contains the objects on which you want to "
                        "perform operations.")
    parser.add_argument('--timeout', default=None, type=int,
                        help="The default timeout  to use with all SOAP "
                        "calls.  If this is not specified, then no timeout "
                        "will be used.")
    parser.add_argument('--section', default='default', help="What section "
                        "name to load config values from (if loading values "
                        "from a config file).")
    parser.add_argument('-l', '--list-sections', action="store_true", help="Show "
                        "available sections in the .lmshrc file.")
    parser.add_argument('onecmd', nargs='*', default=None)
    return parser


def main():
    parser = get_cmd_line_parser()
    args = parser.parse_args()

    config_parser = ConfigParser.SafeConfigParser()
    # If the user explicitly specifies a section but it does
    # not exist, we should let them know and exit.
    api_config = config.load_config(parser, args, config_parser)
    if not args.section == parser.get_default('section') \
            and not config_parser.has_section(args.section):
        sys.stderr.write("section does not exist: %s\n" % args.section)
        sys.exit(1)
    if args.list_sections:
        print '\n'.join(config_parser.sections())
        sys.exit(0)
    if api_config.password is None:
        api_config.password = getpass.getpass('password: ')
    logging.getLogger('suds').addHandler(NullHandler())
    client = api.create_soap_client(api_config)
    labmanager_api = api.LabManager(client)
    lmsh = LMShell(labmanager_api)
    if args.onecmd:
        result = lmsh.onecmd(' '.join(args.onecmd))
        if isinstance(result, ReturnCode):
            sys.exit(result.return_code)
        sys.exit(0)
    else:
        readline.set_completer(lmsh.complete)
        readline.parse_and_bind("tab: complete")
        lmsh.cmdloop()
