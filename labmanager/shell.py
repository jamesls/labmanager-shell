import cmd
from texttable import Texttable


# A mapping from the SOAP returned names
# to the nicer to display names.
DISPLAY_TYPE_MAP = {
    'dateCreated': 'created',
    'fenceMode': 'fencemode',
    'isDeployed': 'deployed',
    'isPublic': 'public',
    'bucketName': 'bucket',
}


class LMShell(cmd.Cmd):
    prompt = '(lmsh) '
    DONT_SHOW_COLUMN = ['autoDeleteInMilliSeconds', 'autoDeleteDateTime',
                        'description', 'mustBeFenced', 'fenceMode',
                        'dateCreated']

    def __init__(self, lmapi, completekey='tab', stdin=None, stdout=None):
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        self._lmapi = lmapi

    def do_list(self, line):
        configs = self._lmapi.list_library_configurations()[0]
        if not configs:
            return
        columns = [c for c in configs[0].__keylist__ if c not in
                   self.DONT_SHOW_COLUMN]

        table = Texttable(max_width=120)
        table.set_deco(Texttable.HEADER | Texttable.VLINES)
        table.set_cols_align(['l' for l in columns])
        table.set_cols_width([6, 30, 6, 8, 4, 10, 15])
        table.header([DISPLAY_TYPE_MAP.get(c, c) for c in columns])
        for config in configs:
            row = [getattr(config, col) for col in columns]
            table.add_row(row)
        print table.draw()

    def do_EOF(self, line):
        print
        return True

    def do_quit(self, line):
        return True



def main():
    from labmanager import api
    from labmanager import config
    import argparse
    import getpass
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostname')
    parser.add_argument('--username')
    parser.add_argument('--organization')
    parser.add_argument('--workspace', default='Main')
    parser.add_argument('--timeout', default=None)
    parser.add_argument('--section', default='default')
    parser.add_argument('onecmd', nargs='?', default=None)
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
