from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface

from cloudshell.cm.ansible.ansible_shell import AnsibleShell


class AnsibleShellDriver(ResourceDriverInterface):
    def cleanup(self):
        pass

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        self.ansible_shell = AnsibleShell()

    def initialize(self, context):
        pass

    def run_ansible_test(self, context):
        return self.ansible_shell.run_ansible_test(context)