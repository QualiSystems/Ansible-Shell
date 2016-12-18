class AnsibleConfiguration(object):
    def __init__(self, playbook_repo=None, hosts_conf=None):
        """
        :type playbook_repo: PlaybookRepository
        :type hosts_conf: list[HostConfiguration]
        """
        self.playbook_repo = playbook_repo or PlaybookRepository
        self.hosts_conf = hosts_conf or []


class PlaybookRepository(object):
    def __init__(self):
        self.url = None
        self.username = None
        self.password = None


class HostConfiguration(object):
    def __init__(self):
        self.ip = None
        self.connection_method = 'ssh'
        self.username = None
        self.password = None
        self.access_key = None
        self.groups = []
        self.parameters = {}
