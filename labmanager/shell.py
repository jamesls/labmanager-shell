import argparse
import getpass
import cmd
from texttable import Texttable

from labmanager import api
from labmanager import config

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


class LMShell(cmd.Cmd):
    prompt = '(lmsh) '
    DONT_SHOW_COLUMN = ['autoDeleteInMilliSeconds', 'autoDeleteDateTime',
                        'description', 'mustBeFenced', 'fenceMode',
                        'dateCreated', 'DatastoreNameResidesOn',
                        'HostNameDeployedOn', 'OwnerFullName']

    def __init__(self, lmapi, completekey='tab', stdin=None, stdout=None):
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        self._lmapi = lmapi

    def do_list(self, line):
        if line.strip() == 'library':
            configs = self._lmapi.list_library_configurations()
        elif line.strip() == 'workspace':
            configs = self._lmapi.list_workspace_configurations()
        else:
            configs = self._lmapi.list_all_configurations()
        if not configs:
            return
        columns = [c for c in configs[0].__keylist__ if c not in
                   self.DONT_SHOW_COLUMN]

        table = Texttable(max_width=120)
        table.set_deco(Texttable.HEADER | Texttable.VLINES)
        table.set_cols_align(['l' for l in columns])
        table.set_cols_width([6, 30, 6, 8, 4, 15, 15])
        table.header([DISPLAY_TYPE_MAP.get(c, c) for c in columns])
        for config in configs:
            row = [getattr(config, col) for col in columns]
            table.add_row(row)
        print table.draw()

    def do_show(self, line):
        config = self._lmapi.show_configuration(line.strip())
        print config

    def do_machines(self, line):
        machines = self._lmapi.list_machines(line.strip())
        columns = [c for c in machines[0].__keylist__ if c not in
                   self.DONT_SHOW_COLUMN]
        table = Texttable(max_width=140)
        table.set_deco(Texttable.HEADER | Texttable.VLINES)
        table.set_cols_align(['l' for l in columns])
        table.header([DISPLAY_TYPE_MAP.get(c, c) for c in columns])
        for machine in machines:
            row = [getattr(machine, col) for col in columns]
            table.add_row(row)
        print table.draw()

    def do_EOF(self, line):
        print
        return True

    def do_quit(self, line):
        return True



def get_cmd_line_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostname')
    parser.add_argument('--username')
    parser.add_argument('--organization')
    parser.add_argument('--workspace', default='Main')
    parser.add_argument('--timeout', default=None)
    parser.add_argument('--section', default='default')
    parser.add_argument('onecmd', nargs='?', default=None)
    return parser


def main():
    parser = get_cmd_line_parser()
    args = parser.parse_args()

    api_config = config.load_config(parser, args)
    if api_config.password is None:
        api_config.password = getpass.getpass('password: ')
    client = api.create_soap_client(api_config)
    labmanager_api = api.LabManager(client)
    lmsh = LMShell(labmanager_api)
    if args.onecmd:
        lmsh.onecmd(args.onecmd)
    else:
        lmsh.cmdloop()
