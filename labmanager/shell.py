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
    args = parser.parse_args()

    password = getpass.getpass('password: ')
    api_config = config.APIConfig(args.hostname, args.username, password,
                                  args.organization, args.workspace)
    client = api.create_soap_client(api_config)
    labmanager_api = api.LabManager(client)
    sh = LMShell(labmanager_api)
    sh.cmdloop()
