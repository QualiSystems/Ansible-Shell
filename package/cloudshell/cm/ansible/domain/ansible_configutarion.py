class AnsibleConfiguration(object):
    def __init__(self, playbook_repo=None, hosts_conf=None, additional_cmd_args=None):
        """
        :type playbook_repo: PlaybookRepository
        :type hosts_conf: list[HostConfiguration]
        :type additional_cmd_args: str
        """
        self.playbook_repo = playbook_repo or PlaybookRepository()
        self.hosts_conf = hosts_conf or []
        self.additional_cmd_args = additional_cmd_args


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