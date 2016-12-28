import os
from unittest import TestCase
from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails
from cloudshell.cm.ansible.ansible_shell import AnsibleShell
from cloudshell.cm.ansible.domain.ansible_configuration import AnsibleConfiguration, HostConfiguration
from mock import Mock, patch


def _create_file_mock():
    f = Mock()
    f.__enter__ = Mock(return_value=Mock())
    f.__exit__ = Mock()
    return f


class TestAnsibleShell(TestCase):
    def setUp(self):
        self.context = ResourceCommandContext()
        self.context.resource = ResourceContextDetails()
        self.context.resource.name = 'resource'
        self.context.reservation = Mock()
        self.context.reservation.reservation_id = 'e34aa58a-468e-49a1-8a1d-0da1d2cc5b41'

        self.file_system = Mock()
        self.file_system.create_file = Mock(return_value=_create_file_mock())
        self.downloader = Mock()
        self.executor = Mock()
        self.logger = Mock()
        session = Mock()
        session_context = Mock()
        session_context.__enter__ = Mock(return_value=session)
        session_context.__exit__ = Mock()
        self.session_provider = Mock()
        self.session_provider.get = Mock(return_value=session_context)

        self.conf = AnsibleConfiguration()
        self.shell = AnsibleShell(self.file_system, self.downloader, self.executor, self.session_provider)

    # Helper

    @patch('cloudshell.cm.ansible.domain.ansible_configuration.AnsibleConfigurationParser.json_to_object')
    @patch('cloudshell.shell.core.session.logging_session.LoggingSessionContext.get_logger_for_context')
    def _execute_playbook(self, get_logger_for_context, json_to_object):
        json_to_object.return_value = self.conf
        get_logger_for_context.return_value = self.logger
        return self.shell.execute_playbook(self.context, '')

    # Ansible Configuration

    @patch('cloudshell.cm.ansible.domain.ansible_config_file.AnsibleConfigFile.ignore_ssh_key_checking')
    def test_config_ssh_key_checking(self, ignore_ssh_key_checking):
        self._execute_playbook()

        ignore_ssh_key_checking.assert_called_once()

    @patch('cloudshell.cm.ansible.domain.ansible_config_file.AnsibleConfigFile.force_color')
    def test_config_force_color(self, force_color):
        self._execute_playbook()

        force_color.assert_called_once()

    @patch('cloudshell.cm.ansible.domain.ansible_config_file.AnsibleConfigFile.set_retry_path')
    def test_config_retry_path(self, set_retry_path):
        self._execute_playbook()

        set_retry_path.assert_called_once_with("."+os.pathsep)

    # Inventory File

    @patch('cloudshell.cm.ansible.domain.inventory_file.InventoryFile.add_host_and_groups')
    def test_inventory_add_host_and_groups(self, add_host_and_groups):
        host1 = HostConfiguration()
        host1.ip = 'host1'
        host1.groups = ['group1']
        self.conf.hosts_conf.append(host1)

        self._execute_playbook()

        add_host_and_groups.assert_called_once_with('host1', ['group1'])

    # Host Vars File

    @patch('cloudshell.cm.ansible.domain.host_vars_file.HostVarsFile.add_conn_file')
    def test_host_with_access_key(self, add_conn_file):
        host1 = HostConfiguration()
        host1.ip = 'host1'
        host1.access_key = 'data1234'
        self.conf.hosts_conf.append(host1)

        self._execute_playbook()

        add_conn_file.assert_called_once_with('host1_access_key.pem')
        self.file_system.create_file.assert_any_call('host_vars\\host1')
        self.file_system.create_file.assert_any_call('host1_access_key.pem')

    @patch('cloudshell.cm.ansible.domain.host_vars_file.HostVarsFile.add_username')
    @patch('cloudshell.cm.ansible.domain.host_vars_file.HostVarsFile.add_password')
    def test_host_with_username_and_password(self, add_password, add_username):
        host1 = HostConfiguration()
        host1.ip = 'host1'
        host1.username = 'admin'
        host1.password = '1234'
        self.conf.hosts_conf.append(host1)

        self._execute_playbook()

        self.file_system.create_file.assert_any_call('host_vars\\host1')
        add_username.assert_called_once_with('admin')
        add_password.assert_called_once_with('1234')

    @patch('cloudshell.cm.ansible.domain.host_vars_file.HostVarsFile.add_vars')
    def test_host_with_custom_vars(self, add_vars):
        host1 = HostConfiguration()
        host1.ip = 'host1'
        self.conf.hosts_conf.append(host1)

        self._execute_playbook()

        add_vars.assert_called_once()

    # Playbook Downloader

    def test_download_playbook_without_auth(self):
        self.conf.playbook_repo.url = 'someurl'

        self._execute_playbook()

        self.downloader.get.assert_called_once_with('someurl', None, self.logger)

    def test_download_playbook_with_auth(self):
        self.conf.playbook_repo.url = 'someurl'
        self.conf.playbook_repo.username = 'user'
        self.conf.playbook_repo.password = 'pass'

        self._execute_playbook()

        self.assertEquals('someurl', self.downloader.get.call_args[0][0])
        self.assertEquals('user', self.downloader.get.call_args[0][1].username)
        self.assertEquals('pass', self.downloader.get.call_args[0][1].password)

    def test_execute_playbook_returns_executor_value(self):
        return_obj = Mock()
        self.executor.execute_playbook = Mock(return_value=return_obj)

        returned_value = self._execute_playbook()

        self.assertEqual(return_obj, returned_value)