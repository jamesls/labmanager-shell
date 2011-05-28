import cmd


class LMShell(cmd.Cmd):
    def __init__(self, lmapi, completekey='tab', stdin=None, stdout=None):
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        self._lmapi = lmapi

    def do_list(self, line):
        configs = self._lmapi.list_library_configurations()
        print configs

    def do_EOF(self, line):
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
    args = parser.parse_args()

    api_config = config.load_config(parser, args)
    if api_config.password is None:
        api_config.password = getpass.getpass('password: ')
    client = api.create_soap_client(api_config)
    labmanager_api = api.LabManager(client)
    sh = LMShell(labmanager_api)
    sh.cmdloop()
