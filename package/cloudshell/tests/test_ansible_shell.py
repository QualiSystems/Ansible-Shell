import os
from unittest import TestCase
from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails
from cloudshell.cm.ansible.ansible_shell import AnsibleShell
from cloudshell.cm.ansible.domain.ansible_configutarion import AnsibleConfiguration, HostConfiguration
from mocks.file_system_service_mock import FileSystemServiceMock
from mock import Mock


class TestAnsibleShell(TestCase):
    def setUp(self):
        self.context = ResourceCommandContext()
        self.context.resource = ResourceContextDetails()
        self.context.resource.name = 'resource'
        self.context.reservation = Mock()
        self.context.reservation.reservation_id = 'sdfsdfsdfdsf'

        self.file_system = FileSystemServiceMock()
        self.downloader = Mock()
        self.executor = Mock()
        session = Mock()
        session_context = Mock()
        session_context.__enter__ = Mock(return_value=session)
        session_context.__exit__ = Mock(return_value=session)
        self.session_provider = Mock()
        self.session_provider.get = Mock(return_value=session_context)

        self.conf = AnsibleConfiguration()
        self.shell = AnsibleShell(self.file_system, self.downloader, self.executor, self.session_provider)

    def execute_playbook(self):
        return self.shell.execute_playbook(self.context, self.conf)

    def test_configuration_file_is_created(self):
        self.execute_playbook()
        self.assertIsNotNone(self.file_system.read_deleted_file('ansible.cfg'))

    def test_inventory_file_is_created(self):
        self.execute_playbook()
        self.assertIsNotNone(self.file_system.read_deleted_file('hosts'))
        pass

    def test_host_with_access_key(self):
        host1 = HostConfiguration()
        host1.ip = 'host1'
        host1.access_key = 'data1234'
        self.conf.hosts_conf.append(host1)

        self.execute_playbook()

        host1_var_file = self.file_system.read_deleted_file('hosts_vars', 'host1')
        host1_pem_file = self.file_system.read_deleted_file('host1_access_key.pem')
        self.assertTrue('ansible_ssh_private_key_file: host1_access_key.pem' in host1_var_file)
        self.assertEquals('data1234', host1_pem_file)

    def test_host_with_username_and_password(self):
        host1 = HostConfiguration()
        host1.ip = 'host1'
        host1.username = 'admin'
        host1.password = '1234'
        self.conf.hosts_conf.append(host1)

        self.execute_playbook()

        host1_var_file = self.file_system.read_deleted_file('hosts_vars', 'host1')
        self.assertTrue('ansible_user: admin' in host1_var_file)
        self.assertTrue('ansible_ssh_pass: 1234' in host1_var_file)

    def test_host_connection_method(self):
        host1 = HostConfiguration()
        host1.ip = 'host1'
        host1.connection_method = 'winrm'
        self.conf.hosts_conf.append(host1)

        self.execute_playbook()

        host1_var_file = self.file_system.read_deleted_file('hosts_vars', 'host1')
        self.assertTrue('ansible_connection: winrm' in host1_var_file)

    def test_download_playbook_without_auth(self):
        self.conf.playbook_repo.url = 'someurl'

        self.execute_playbook()

        self.assertTrue(self.downloader.get.called)
        self.assertEquals('someurl', self.downloader.get.call_args[0][0])
        self.assertEquals(None, self.downloader.get.call_args[0][1])

    def test_download_playbook_with_auth(self):
        self.conf.playbook_repo.url = 'someurl'
        self.conf.playbook_repo.username = 'user'
        self.conf.playbook_repo.password = 'pass'

        self.execute_playbook()

        self.assertTrue(self.downloader.get.called)
        self.assertEquals('someurl', self.downloader.get.call_args[0][0])
        self.assertEquals('user', self.downloader.get.call_args[0][1].username)
        self.assertEquals('pass', self.downloader.get.call_args[0][1].password)

    def test_execute_playbook_returns_executor_value(self):
        return_obj = Mock()
        self.executor.execute_playbook = Mock(return_value=return_obj)

        returned_value = self.execute_playbook()

        self.assertEqual(return_obj, returned_value)