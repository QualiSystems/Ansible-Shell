from unittest import TestCase
from cloudshell.cm.ansible.domain.ansible_conflig_file import AnsibleConfigFile
from mocks.file_system_service_mock import FileSystemServiceMock
from mock import Mock
import os


class TestAnsibleConfigFile(TestCase):
    def setUp(self):
        self.file_system = FileSystemServiceMock()

    def test_can_add_ignore_ssh_key_checking(self):
        with AnsibleConfigFile(self.file_system, Mock()) as f:
            f.ignore_ssh_key_checking()
        self.assertEquals(os.linesep.join(['[defaults]','host_key_checking = False']), self.file_system.read_all_lines('ansible.cfg'))

    def test_can_add_force_color(self):
        with AnsibleConfigFile(self.file_system, Mock()) as f:
            f.force_color()
        self.assertEquals(os.linesep.join(['[defaults]', 'force_color = 1']), self.file_system.read_all_lines('ansible.cfg'))