from unittest import TestCase
from cloudshell.cm.ansible.domain.inventory_file import InventoryFile
from .mocks.file_system_service_mock import FileSystemServiceMock
from mock import Mock
import os


class TestInventoryFile(TestCase):
    def setUp(self):
        self.file_system = FileSystemServiceMock()

    def test_adding_hosts_without_groups_add_them_to_all(self):
        with InventoryFile(self.file_system, 'hosts', Mock()) as f:
            f.add_host_and_groups('host1')
            f.add_host_and_groups('host2')
        self.assertEqual(os.linesep.join(['[all]','host1','host2']), self.file_system.read_all_lines('hosts').decode())

    def test_cannot_add_same_host_twice(self):
        with InventoryFile(self.file_system, 'hosts', Mock()) as f:
            f.add_host_and_groups("host1")
            with self.assertRaises(ValueError):
                f.add_host_and_groups("host1")

    def test_can_add_host_with_multiple_root_groups(self):
        with InventoryFile(self.file_system, 'hosts', Mock()) as f:
            f.add_host_and_groups('host1', ['group1','group2'])
        self.assertEqual(os.linesep.join(['[group1]','host1','','[group2]','host1']), self.file_system.read_all_lines('hosts').decode())

    def test_can_add_host_with_multiple_sub_groups(self):
        with InventoryFile(self.file_system, 'hosts', Mock()) as f:
            f.add_host_and_groups('host1', ['group1/sub1', 'group1/sub2'])
        self.assertEqual(os.linesep.join(['[group1:children]','sub1','sub2','','[sub1]','host1','','[sub2]','host1']), self.file_system.read_all_lines('hosts').decode())