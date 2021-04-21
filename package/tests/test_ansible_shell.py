import os
from unittest import TestCase

from cloudshell.cm.ansible.ansible_shell import AnsibleShell
from cloudshell.cm.ansible.domain.Helpers.ansible_connection_helper import AnsibleConnectionHelper
from cloudshell.cm.ansible.domain.exceptions import AnsibleException
from cloudshell.cm.ansible.domain.ansible_configuration import AnsibleConfiguration, HostConfiguration
from mock import Mock, patch
from .helpers import mock_enter_exit, mock_enter_exit_self, Any


class TestAnsibleShell(TestCase):
    def setUp(self):
        #self.context = ResourceCommandContext()
        self.context = Mock()
        #self.context.resource = ResourceContextDetails()
        self.context.resource = Mock()
        self.context.resource.name = 'resource'
        self.context.reservation = Mock()
        self.context.reservation.reservation_id = 'e34aa58a-468e-49a1-8a1d-0da1d2cc5b41'

        self.file_system = Mock()
        self.file_system.create_file = Mock(return_value=mock_enter_exit(Mock()))
        self.downloader = Mock()
        self.executor = Mock()
        self.executor.execute_playbook = Mock(return_value=['', ''])
        self.logger = mock_enter_exit(Mock())
        session = Mock()
        session_context = Mock()
        session_context.__enter__ = Mock(return_value=session)
        session_context.__exit__ = Mock()
        self.session_provider = Mock()
        self.session_provider.get = Mock(return_value=session_context)

        self.conf = AnsibleConfiguration()
        self.conf.timeout_minutes = "0.0"
        self.shell = AnsibleShell(self.file_system, self.downloader, self.executor)
        self.shell.connection_service.check_connection = Mock()

        self.ansible_result_patcher = patch('cloudshell.cm.ansible.ansible_shell.AnsibleResult')
        self.ansible_result = Mock()
        self.ansible_result.success = True
        self.ansible_result.ctor = self.ansible_result_patcher.start()
        self.ansible_result.ctor.return_value = self.ansible_result

    def tearDown(self):
        self.ansible_result_patcher.stop()

    # Helper

    def _execute_playbook(self):
        with patch('cloudshell.cm.ansible.ansible_shell.LoggingSessionContext'):
            with patch('cloudshell.cm.ansible.ansible_shell.ErrorHandlingContext'):
                with patch('cloudshell.cm.ansible.ansible_shell.AnsibleConfigurationParser') as parser:
                    parser.return_value.json_to_object = Mock(return_value=self.conf)
                    with patch('cloudshell.cm.ansible.ansible_shell.CloudShellSessionContext'):
                        self.shell.execute_playbook(self.context, '', Mock())

    # General

    def test_temp_folder_is_created(self):
        self._execute_playbook()

        self.file_system.create_temp_folder.assert_called_once()
        self.file_system.delete_temp_folder.assert_called_once()

    # Ansible Configuration

    def test_ansible_config_file(self):
        with patch('cloudshell.cm.ansible.ansible_shell.AnsibleConfigFile') as file:
            m = mock_enter_exit_self()
            file.return_value = m

            self._execute_playbook()

            m.ignore_ssh_key_checking.assert_called_once()
            m.force_color.assert_called_once()
            m.set_retry_path.assert_called_once_with("." + os.pathsep)

    # Inventory File

    def test_inventory_file(self):
        with patch('cloudshell.cm.ansible.ansible_shell.InventoryFile') as file:
            m = mock_enter_exit_self()
            file.return_value = m
            host1 = HostConfiguration()
            host1.ip = 'host1'
            host1.groups = ['group1']
            host1.connection_method = AnsibleConnectionHelper.CONNECTION_METHOD_SSH
            host2 = HostConfiguration()
            host2.ip = 'host2'
            host2.connection_method = AnsibleConnectionHelper.CONNECTION_METHOD_WIN_RM
            host2.groups = ['group2']
            self.conf.hosts_conf.append(host1)
            self.conf.hosts_conf.append(host2)

            self._execute_playbook()

            m.add_host_and_groups.assert_any_call('host1', ['group1'])
            m.add_host_and_groups.assert_any_call('host2', ['group2'])

    # Host Vars File

    def test_host_vars_file_with_access_key(self):
        with patch('cloudshell.cm.ansible.ansible_shell.HostVarsFile') as file:
            m = mock_enter_exit_self()
            file.return_value = m
            host1 = HostConfiguration()
            host1.ip = 'host1'
            host1.access_key = 'data1234'
            self.conf.hosts_conf.append(host1)
            host1.connection_method = AnsibleConnectionHelper.CONNECTION_METHOD_WIN_RM
            self._execute_playbook()

            self.file_system.create_file.assert_any_call('host1_access_key.pem', 0o400)
            m.add_conn_file.assert_called_once_with('host1_access_key.pem')
            m.add_username.assert_called_once()
            m.add_password.assert_not_called()

    def test_host_vars_file_with_username_and_password(self):
        with patch('cloudshell.cm.ansible.ansible_shell.HostVarsFile') as file:
            m = mock_enter_exit_self()
            file.return_value = m
            host1 = HostConfiguration()
            host1.ip = 'host1'
            host1.connection_method = AnsibleConnectionHelper.CONNECTION_METHOD_WIN_RM
            host1.username = 'admin'
            host1.password = '1234'
            self.conf.hosts_conf.append(host1)

            self._execute_playbook()

            m.add_conn_file.assert_not_called()
            m.add_username.assert_called_once_with('admin')
            m.add_password.assert_called_once_with('1234')

    def test_host_vars_file_with_ssh(self):
        with patch('cloudshell.cm.ansible.ansible_shell.HostVarsFile') as file:
            m = mock_enter_exit_self()
            file.return_value = m
            host1 = HostConfiguration()
            host1.ip = 'host1'
            host1.connection_method = 'ssh'
            self.conf.hosts_conf.append(host1)

            self._execute_playbook()

            m.add_connection_type.assert_called_once_with('ssh')

    def test_host_vars_file_with_winrm_http(self):
        with patch('cloudshell.cm.ansible.ansible_shell.HostVarsFile') as file:
            m = mock_enter_exit_self()
            file.return_value = m
            host1 = HostConfiguration()
            host1.ip = 'host1'
            host1.connection_method = 'winrm'
            host1.connection_secured = False
            self.conf.hosts_conf.append(host1)

            self._execute_playbook()

            m.add_connection_type.assert_called_once_with('winrm')
            m.add_port.assert_called_once_with('5985')

    def test_host_vars_file_with_winrm_http(self):
        with patch('cloudshell.cm.ansible.ansible_shell.HostVarsFile') as file:
            m = mock_enter_exit_self()
            file.return_value = m
            host1 = HostConfiguration()
            host1.ip = 'host1'
            host1.connection_method = 'winrm'
            host1.connection_secured = True
            self.conf.hosts_conf.append(host1)

            self._execute_playbook()

            m.add_connection_type.assert_called_once_with('winrm')
            m.add_port.assert_called_once_with('5986')
            m.add_ignore_winrm_cert_validation.assert_called_once()

    def test_host_vars_file_with_custom_vars(self):
        with patch('cloudshell.cm.ansible.ansible_shell.HostVarsFile') as file:
            m = mock_enter_exit_self()
            file.return_value = m
            host1 = HostConfiguration()
            host1.ip = 'host1'
            host1.connection_method = AnsibleConnectionHelper.CONNECTION_METHOD_WIN_RM
            self.conf.hosts_conf.append(host1)

            self._execute_playbook()

            m.add_vars.assert_called_once()

    # Playbook Downloader

    def test_download_playbook_without_auth(self):
        self.conf.playbook_repo.url = 'someurl'

        self._execute_playbook()

        self.downloader.get.assert_called_once_with('someurl', Any(), Any(), Any(), True)

    def test_download_playbook_with_auth(self):
        self.conf.playbook_repo.url = 'someurl'
        self.conf.playbook_repo.username = 'user'
        self.conf.playbook_repo.password = 'pass'

        self._execute_playbook()

        self.downloader.get.assert_called_once_with('someurl',
                                                    Any(lambda x: x.username == 'user' and x.password == 'pass'), Any(),
                                                    Any(), True)

    # Playbook Executor

    def test_execute_playbook_end_when_no_errors(self):
        self._execute_playbook()

    def test_execute_playbook_throws_exception_on_error(self):
        json = Mock()
        self.ansible_result.success = False
        self.ansible_result.to_json = Mock(return_value=json)

        with self.assertRaises(AnsibleException) as e:
            self._execute_playbook()
        self.assertEqual(str(json), str(e.exception))

    def test_ansible_result_is_created_with_output_and_error_and_ips(self):
        host1 = HostConfiguration()
        host1.ip = 'some ip'
        host1.connection_method = AnsibleConnectionHelper.CONNECTION_METHOD_WIN_RM
        self.conf.hosts_conf.append(host1)
        self.executor.execute_playbook = Mock(return_value=['some output', 'some error'])

        self._execute_playbook()

        self.ansible_result.ctor.assert_called_once_with('some output', 'some error', ['some ip'])
