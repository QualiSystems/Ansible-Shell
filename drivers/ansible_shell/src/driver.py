import json
from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.cm.ansible.ansible_shell import AnsibleShell
from cloudshell.cm.ansible.domain.ansible_configutarion import AnsibleConfiguration
from cloudshell.cm.ansible.domain.ansible_configutarion import HostConfiguration
from cloudshell.cm.ansible.domain.ansible_configutarion import PlaybookRepository
from cloudshell.shell.core.session.logging_session import LoggingSessionContext


class AnsibleShellDriver(ResourceDriverInterface):
    def cleanup(self):
        pass

    def __init__(self):
        self.ansible_shell = AnsibleShell()

    def initialize(self, context):
        pass

    def execute_playbook(self, command_context, ansible_configuration_json):
        with LoggingSessionContext(command_context) as logger:
            logger.debug('\'execute_playbook\' is called with the configuration json: \n'+ansible_configuration_json)

        ansible_configuration_object = self.decode(ansible_configuration_json)
        return self.ansible_shell.execute_playbook(command_context, ansible_configuration_object)

    def decode(self, json_str):
        """
        Decodes a json string to an AnsibleConfiguration instance.
        :param str json_str: The json to decode.
        :return AnsibleConfiguration instance.
        :rtype AnsibleConfiguration
        """
        json_obj = json.loads(json_str)

        ansi_conf = AnsibleConfiguration()
        ansi_conf.additional_cmd_args = json_obj['additionalArgs']
        ansi_conf.playbook_repo.url = json_obj['repositoryDetails']['url']
        ansi_conf.playbook_repo.username = json_obj['repositoryDetails']['username']
        ansi_conf.playbook_repo.password = json_obj['repositoryDetails']['password']

        for json_host in json_obj['hostsDetails']:
            host_conf = HostConfiguration()
            host_conf.ip = json_host['address']
            host_conf.connection_method = json_host['connectionMethod']
            host_conf.username = json_host['userName']
            host_conf.password = json_host['password']
            host_conf.access_key = json_host['accessKey']
            host_conf.groups = json_host['groups']
            if json_host['parameters'] is not None:
                host_conf.parameters = dict((i['name'], i['value']) for i in json_host['parameters'])
            ansi_conf.hosts_conf.append(host_conf)

        return ansi_conf
