from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.cm.ansible.ansible_shell import AnsibleShell


class AnsibleShellDriver(ResourceDriverInterface):
    def cleanup(self):
        pass

    def __init__(self):
        self.ansible_shell = AnsibleShell()

    def initialize(self, context):
        pass

    def execute_playbook(self, command_context, ansible_configuration_json):
        return self.ansible_shell.execute_playbook(command_context, ansible_configuration_json)


