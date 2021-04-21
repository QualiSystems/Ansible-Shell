import json

from cloudshell.api.cloudshell_api import CloudShellAPISession


class AnsibleConfiguration(object):
    def __init__(self, playbook_repo=None, hosts_conf=None, additional_cmd_args=None, timeout_minutes = None):
        """
        :type playbook_repo: PlaybookRepository
        :type hosts_conf: list[HostConfiguration]
        :type additional_cmd_args: str
        :type timeout_minutes: float
        """
        self.timeout_minutes = timeout_minutes or 0.0
        self.playbook_repo = playbook_repo or PlaybookRepository()
        self.hosts_conf = hosts_conf or []
        self.additional_cmd_args = additional_cmd_args
        self.verify_certificate = True


class PlaybookRepository(object):
    def __init__(self):
        self.url = None
        self.username = None
        self.password = None
        self.token = None


class HostConfiguration(object):
    def __init__(self):
        self.ip = None
        self.connection_method = None
        self.connection_secured = None
        self.username = None
        self.password = None
        self.access_key = None
        self.groups = []
        self.parameters = {}


class AnsibleConfigurationParser(object):

    def __init__(self, api):
        """
        :type api: CloudShellAPISession
        """
        self.api = api

    def json_to_object(self, json_str):
        """
        Decodes a json string to an AnsibleConfiguration instance.
        :type json_str: str
        :rtype AnsibleConfiguration
        """
        json_obj = json.loads(json_str)
        AnsibleConfigurationParser._validate(json_obj)

        ansi_conf = AnsibleConfiguration()
        ansi_conf.additional_cmd_args = json_obj.get('additionalArgs')
        ansi_conf.timeout_minutes = json_obj.get('timeoutMinutes', 0.0)
        ansi_conf.verify_certificate = json_obj.get('verifyCertificate', 'true').lower()=='true'

        if json_obj.get('repositoryDetails'):
            ansi_conf.playbook_repo.url = json_obj['repositoryDetails'].get('url')
            ansi_conf.playbook_repo.username = json_obj['repositoryDetails'].get('username')
            ansi_conf.playbook_repo.password = json_obj['repositoryDetails'].get('password')
            ansi_conf.playbook_repo.token = json_obj['repositoryDetails'].get('token')

        for json_host in json_obj.get('hostsDetails',[]):
            host_conf = HostConfiguration()
            host_conf.ip = json_host.get('ip')
            host_conf.connection_method = json_host.get('connectionMethod').lower()
            host_conf.connection_secured = bool_parse(json_host.get('connectionSecured'))
            host_conf.username = json_host.get('username')
            host_conf.password = self._get_password(json_host)
            host_conf.access_key = self._get_access_key(json_host)
            host_conf.groups = json_host.get('groups')
            if json_host.get('parameters'):
                host_conf.parameters = dict((i['name'], i['value']) for i in json_host['parameters'])
            ansi_conf.hosts_conf.append(host_conf)

        return ansi_conf

    def _get_password(self, json_host):
        pw = json_host.get('password')
        if pw:
            return self.api.DecryptPassword(pw).Value
        else:
            return pw

    def _get_access_key(self, json_host):
        key = json_host.get('accessKey')
        if key:
            return self.api.DecryptPassword(key).Value
        else:
            return key

    @staticmethod
    def _validate(json_obj):
        """
        :type json_obj: json
        :rtype bool
        """
        basic_msg = 'Failed to parse ansible configuration input json: '

        if json_obj.get('repositoryDetails') is None:
            raise SyntaxError(basic_msg + 'Missing "repositoryDetails" node.')

        if json_obj['repositoryDetails'].get('url') is None:
            raise SyntaxError(basic_msg + 'Missing "repositoryDetails.url" node.')

        if not json_obj['repositoryDetails'].get('url'):
            raise SyntaxError(basic_msg + '"repositoryDetails.url" node cannot be empty.')

        if json_obj.get('hostsDetails') is None:
            raise SyntaxError(basic_msg + 'Missing "hostsDetails" node.')

        if len(json_obj['hostsDetails']) == 0:
            raise SyntaxError(basic_msg + '"hostsDetails" node cannot be empty.')

        hosts_without_ip = [h for h in json_obj['hostsDetails'] if not h.get('ip')]
        if hosts_without_ip:
            raise SyntaxError(basic_msg + 'Missing "ip" node in ' + str(len(hosts_without_ip)) + ' hosts.')

        hosts_without_conn = [h for h in json_obj['hostsDetails'] if not h.get('connectionMethod')]
        if hosts_without_conn:
            raise SyntaxError(basic_msg + 'Missing "connectionMethod" node in ' + str(len(hosts_without_conn)) + ' hosts.')


def bool_parse(b):
    if b is None:
        return False
    else:
        return str(b).lower() == 'true'
