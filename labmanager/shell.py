import argparse
import getpass
import cmd
from pprint import pprint

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

    def __init__(self, lmapi, completekey='tab', stdin=None, stdout=None):
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        self._lmapi = lmapi

    def do_list(self, line):
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
        config = self._lmapi.show_configuration(line.strip())
        pprint(config)

    def do_machines(self, line):
        machines = self._lmapi.list_machines(line.strip())
        columns = self.LIST_MACHINES_COLUMNS
        table = Texttable(max_width=140)
        table.set_deco(Texttable.HEADER | Texttable.VLINES)
        table.set_cols_align(['l' for l in columns])
        table.header([DISPLAY_TYPE_MAP.get(c, c) for c in columns])
        rows = self._get_rows(machines, columns)
        table.add_rows(rows, header=False)
        print table.draw()

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
                else:
                    row.append(obj[col])
            rows.append(row)
        return rows

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
