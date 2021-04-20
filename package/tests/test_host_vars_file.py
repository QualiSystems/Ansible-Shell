from unittest import TestCase
from cloudshell.cm.ansible.domain.host_vars_file import HostVarsFile
from .mocks.file_system_service_mock import FileSystemServiceMock
from mock import Mock
from collections import OrderedDict
import os


class TestHostVarsFile(TestCase):
    def setUp(self):
        self.file_system = FileSystemServiceMock()

    def test_first_call_creates_the_folder(self):
        with HostVarsFile(self.file_system, 'host1', Mock()) as f:
            pass
        self.assertIn('host_vars', self.file_system.folders)

    def test_can_add_connection_type(self):
        with HostVarsFile(self.file_system, 'host1', Mock()) as f:
            f.add_connection_type('winrm')
        self.assertEqual(os.linesep.join(['---', 'ansible_connection: "winrm"']),
                          self.file_system.read_all_lines('host_vars', 'host1').decode())

    def test_can_add_connection_type(self):
        with HostVarsFile(self.file_system, 'host1', Mock()) as f:
            f.add_username('admin')
        self.assertEqual(os.linesep.join(['---', 'ansible_user: "admin"']),
                          self.file_system.read_all_lines('host_vars', 'host1').decode())

    def test_can_add_connection_type(self):
        with HostVarsFile(self.file_system, 'host1', Mock()) as f:
            f.add_password('1234')
        self.assertEqual(os.linesep.join(['---', 'ansible_ssh_pass: "1234"']),
                          self.file_system.read_all_lines('host_vars', 'host1').decode())

    def test_can_add_connection_key_file(self):
        with HostVarsFile(self.file_system, 'host1', Mock()) as f:
            f.add_conn_file('mycert.pem')
        self.assertEqual(os.linesep.join(['---', 'ansible_ssh_private_key_file: "mycert.pem"']),
                          self.file_system.read_all_lines('host_vars', 'host1').decode())

    def test_can_add_port(self):
        with HostVarsFile(self.file_system, 'host1', Mock()) as f:
            f.add_port('1234')
        self.assertEqual(os.linesep.join(['---', 'ansible_port: "1234"']),
                          self.file_system.read_all_lines('host_vars', 'host1').decode())

    def test_can_add_custom_vars(self):
        with HostVarsFile(self.file_system, 'host1', Mock()) as f:
            f.add_vars({'param1': 'abc', 'param2': '123'})
            f.add_vars({'param3': 'W'})
        self.assertEqual(os.linesep.join(['---', 'param1: "abc"', 'param2: "123"', 'param3: "W"']),
                          self.file_system.read_all_lines('host_vars', 'host1').decode())
