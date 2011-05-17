from urlparse import urljoin


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
