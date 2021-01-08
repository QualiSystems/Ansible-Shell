import json


class AnsibleConfiguration(object):
    def __init__(self, playbook_repo=None, hosts_conf=None, additional_cmd_args=None, timeout_minutes = None):
        """
        :type playbook_repo: PlaybookRepository
        :type hosts_conf: list[HostConfiguration]
        :type additional_cmd_args: str
        :type timeout_minutes: float
        """
        self.timeoutMinutes = timeout_minutes or 0.0
        self.repositoryDetails = playbook_repo or PlaybookRepository()
        self.hostsDetails = hosts_conf or []
        self.additionalArgs = additional_cmd_args
        self.isSecondGenService = True
        self.printOutput = True

    def get_pretty_json(self):
        return json.dumps(self, default=lambda o: getattr(o, '__dict__', str(o)), indent=4)


class PlaybookRepository(object):
    def __init__(self):
        self.url = None
        self.username = None
        self.password = None


class HostConfiguration(object):
    def __init__(self):
        self.ip = None
        self.connectionMethod = None
        self.connectionSecured = None
        self.username = None
        self.password = None
        self.accessKey = None
        self.groups = None
        self.parameters = None

