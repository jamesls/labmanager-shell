import os
from ConfigParser import SafeConfigParser


USER_CONFIG_FILE = os.path.expanduser('~/.lmshrc')
SECRET_KEYS = ['password']


def load_config(parser, args, cfgparser=None):
    """Load lab manager configuration.

    The loading process works like this:

        - the default command line options are loaded
        - next a config file is looked for
        - if it's found, then we load the config file.
        - the there's no section specified in the args,
          the default section is loaded.
        - otherwise the section specified in args is loaded.
        - command line arguments override anything loaded
          so far.

    An instance of APIConfig is returned.
    There's one caveat:  If you do not have a password in your
    config file, then the password field will be filled in
    with a None value.  It is then up to the caller to get
    the password from the user somehow and assign it's value
    to the returned APIConfig object.

    """
    if cfgparser is None:
        cfgparser = SafeConfigParser()
    full_config = _default_cmd_line_options(parser, args)
    cfg_values = load_config_from_config_file(cfgparser, args.section,
                                              vars(args).keys()+ SECRET_KEYS)
    cmd_line_cfg_values = _non_default_cmd_line_options(parser, args)
    full_config.update(cfg_values)
    full_config.update(cmd_line_cfg_values)
    timeout = full_config.get('timeout')
    if timeout:
        timeout = int(timeout)
    return APIConfig(full_config['hostname'], full_config['username'],
                     full_config.get('password'), full_config['organization'],
                     full_config['workspace'], timeout)


def load_config_from_config_file(cfgparser, section, valid_keys):
    """Load config values from the user config file.

    - cfgparser is an instance of ConfigParser
    - section is the section name in the config file
    - valid_keys are a list of config keys to load.

    If the config file could not be loaded then an empty
    dictionary is returned.

    """
    loaded_cfg = {}
    if cfgparser.read(USER_CONFIG_FILE) and cfgparser.has_section(section):
        valid_values = [v for v in cfgparser.options(section) if v in
                        valid_keys]
        for value in valid_values:
            loaded_cfg[value] = cfgparser.get(section, value)
    return loaded_cfg


def _default_cmd_line_options(parser, args):
    return dict([(k, v) for k, v in vars(args).items()
                 if parser.get_default(k) == v])


def _non_default_cmd_line_options(parser, args):
    # Return anything that the user explicitly specifies
    # on the command line.
    return dict([(k, v) for k, v in vars(args).items()
                 if parser.get_default(k) != v])


class APIConfig(object):
    def __init__(self, hostname, username, password,
                 organization, workspace, timeout=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.organization = organization
        self.workspace = workspace
        self.timeout = timeout

    @property
    def url(self):
        return 'https://%s/LabManager/SOAP/LabManager.asmx?WSDL' % \
            self.hostname
