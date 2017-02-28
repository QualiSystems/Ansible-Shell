import os

from cloudshell.cm.ansible.domain.cancellation_sampler import CancellationSampler
from cloudshell.cm.ansible.domain.exceptions import AnsibleException
from cloudshell.cm.ansible.domain.ansible_command_executor import AnsibleCommandExecutor, ReservationOutputWriter
from cloudshell.cm.ansible.domain.ansible_config_file import AnsibleConfigFile
from cloudshell.cm.ansible.domain.ansible_configuration import AnsibleConfigurationParser
from cloudshell.cm.ansible.domain.file_system_service import FileSystemService
from cloudshell.cm.ansible.domain.filename_extractor import FilenameExtractor
from cloudshell.cm.ansible.domain.host_vars_file import HostVarsFile
from cloudshell.cm.ansible.domain.http_request_service import HttpRequestService
from cloudshell.cm.ansible.domain.inventory_file import InventoryFile
from cloudshell.cm.ansible.domain.output.ansible_result import AnsibleResult
from cloudshell.cm.ansible.domain.playbook_downloader import PlaybookDownloader, HttpAuth
from cloudshell.cm.ansible.domain.temp_folder_scope import TempFolderScope
from cloudshell.cm.ansible.domain.zip_service import ZipService
from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext


class AnsibleShell(object):
    INVENTORY_FILE_NAME = 'hosts'

    def __init__(self, file_system=None, playbook_downloader=None, playbook_executor=None, session_provider=None,
                 http_request_service=None, zip_service=None):
        """
        :type file_system: FileSystemService
        :type playbook_downloader: PlaybookDownloader
        :type playbook_executor: AnsibleCommandExecutor
        :type session_provider: CloudShellSessionProvider
        """
        http_request_service = http_request_service or HttpRequestService()
        zip_service = zip_service or ZipService()
        self.file_system = file_system or FileSystemService()
        filename_extractor = FilenameExtractor()
        self.downloader = playbook_downloader or PlaybookDownloader(self.file_system, zip_service, http_request_service, filename_extractor)
        self.executor = playbook_executor or AnsibleCommandExecutor()

    def execute_playbook(self, command_context, ansi_conf_json, cancellation_context):
        """
        :type command_context: ResourceCommandContext
        :type ansi_conf_json: str
        :type cancellation_context: CancellationContext
        :rtype str
        """
        with LoggingSessionContext(command_context) as logger:
            logger.debug('\'execute_playbook\' is called with the configuration json: \n' + ansi_conf_json)

            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(command_context) as api:
                    ansi_conf = AnsibleConfigurationParser(api).json_to_object(ansi_conf_json)
                    output_writer = ReservationOutputWriter(api, command_context)
                    cancellation_sampler = CancellationSampler(cancellation_context)

                    with TempFolderScope(self.file_system, logger):
                        self._add_ansible_config_file(logger)
                        self._add_host_vars_files(ansi_conf, logger)
                        self._add_inventory_file(ansi_conf, logger)
                        playbook_name = self._download_playbook(ansi_conf, cancellation_sampler, logger)
                        self._run_playbook(ansi_conf, playbook_name, output_writer, cancellation_sampler, logger)

    def _add_ansible_config_file(self, logger):
        """
        :type logger: Logger
        """
        with AnsibleConfigFile(self.file_system, logger) as file:
            file.ignore_ssh_key_checking()
            file.force_color()
            file.set_retry_path("." + os.pathsep)

    def _add_inventory_file(self, ansi_conf, logger):
        """
        :type ansi_conf: AnsibleConfiguration
        :type logger: Logger
        """
        with InventoryFile(self.file_system, self.INVENTORY_FILE_NAME, logger) as inventory:
            for host_conf in ansi_conf.hosts_conf:
                inventory.add_host_and_groups(host_conf.ip, host_conf.groups)

    def _add_host_vars_files(self, ansi_conf, logger):
        """
        :type ansi_conf: AnsibleConfiguration
        :type logger: Logger
        """
        for host_conf in ansi_conf.hosts_conf:
            with HostVarsFile(self.file_system, host_conf.ip, logger) as file:
                file.add_vars(host_conf.parameters)
                file.add_connection_type(host_conf.connection_method)
                if host_conf.connection_method == 'winrm':
                    if host_conf.connection_secured == True:
                        file.add_port('5986')
                        file.add_ignore_winrm_cert_validation()
                    else:
                        file.add_port('5985')
                file.add_username(host_conf.username)
                if host_conf.password:
                    file.add_password(host_conf.password)
                else:
                    file_name = host_conf.ip + '_access_key.pem'
                    with self.file_system.create_file(file_name, 0400) as file_stream:
                        file_stream.write(host_conf.access_key)
                    file.add_conn_file(file_name)

    def _download_playbook(self, ansi_conf, cancellation_sampler, logger):
        """
        :type ansi_conf: AnsibleConfiguration
        :type cancellation_sampler: CancellationSampler
        :type logger: Logger
        :rtype str
        """
        repo = ansi_conf.playbook_repo
        auth = HttpAuth(repo.username, repo.password) if repo.username else None
        playbook_name = self.downloader.get(ansi_conf.playbook_repo.url, auth, logger, cancellation_sampler)
        return playbook_name

    def _run_playbook(self, ansi_conf, playbook_name, output_writer, cancellation_sampler, logger):
        """
        :type ansi_conf: AnsibleConfiguration
        :type playbook_name: str
        :type output_writer: OutputWriter
        :type cancellation_sampler: CancellationSampler
        :type logger: Logger
        """
        logger.info('Running the playbook')

        output, error = self.executor.execute_playbook(
            playbook_name, self.INVENTORY_FILE_NAME, ansi_conf.additional_cmd_args, output_writer, logger,
            cancellation_sampler)
        ansible_result = AnsibleResult(output, error, [h.ip for h in ansi_conf.hosts_conf])

        if not ansible_result.success:
            raise AnsibleException(ansible_result.to_json())