from unittest import TestCase
from cloudshell.cm.ansible.domain.ansible_config_file import AnsibleConfigFile
from .mocks.file_system_service_mock import FileSystemServiceMock
from mock import Mock
import os


class TestAnsibleConfigFile(TestCase):
    def setUp(self):
        self.file_system = FileSystemServiceMock()

    def test_can_add_ignore_ssh_key_checking(self):
        with AnsibleConfigFile(self.file_system, Mock()) as f:
            f.ignore_ssh_key_checking()
        self.assertEqual(os.linesep.join(['[defaults]', 'host_key_checking = False']), self.file_system.read_all_lines('ansible.cfg').decode())

    def test_can_add_force_color(self):
        with AnsibleConfigFile(self.file_system, Mock()) as f:
            f.force_color()
        self.assertEqual

    def test_can_add_set_retry_path(self):
        with AnsibleConfigFile(self.file_system, Mock()) as f:
            f.set_retry_path(678)
        self.assertEqual(os.linesep.join(['[defaults]', 'retry_files_save_path = 678']), self.file_system.read_all_lines('ansible.cfg').decode())