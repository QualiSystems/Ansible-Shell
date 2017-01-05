import json
import os

from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.context import ResourceCommandContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from mock import Mock

from cloudshell.cm.ansible.domain.filename_extractor import FilenameExtractor
from cloudshell.cm.ansible.domain.http_request_service import HttpRequestService
from cloudshell.cm.ansible.domain.zip_service import ZipService
from cloudshell.cm.ansible.domain.file_system_service import FileSystemService
from cloudshell.cm.ansible.domain.inventory_file import InventoryFile
from cloudshell.cm.ansible.domain.playbook_downloader import PlaybookDownloader, HttpAuth
from cloudshell.cm.ansible.domain.ansible_configuration import AnsibleConfiguration
from cloudshell.cm.ansible.domain.ansible_command_executor import AnsibleCommandExecutor, ReservationOutputWriter
from cloudshell.cm.ansible.domain.ansible_config_file import AnsibleConfigFile
from cloudshell.cm.ansible.domain.temp_folder_scope import TempFolderScope
from cloudshell.cm.ansible.domain.ansible_configuration import AnsibleConfigurationParser
from cloudshell.cm.ansible.domain.host_vars_file import HostVarsFile
from cloudshell.cm.ansible.domain.output.ansible_result import AnsibleResult


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
        filename_extractor = FilenameExtractor();
        self.downloader = playbook_downloader or PlaybookDownloader(self.file_system, zip_service, http_request_service, filename_extractor)
        self.executor = playbook_executor or AnsibleCommandExecutor()

    def execute_playbook(self, command_context, ansi_conf_json):
        """
        :type command_context: ResourceCommandContext
        :type ansi_conf_json: str
        :rtype str
        """
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                logger.debug('\'execute_playbook\' is called with the configuration json: \n' + ansi_conf_json)
                ansi_conf = AnsibleConfigurationParser.json_to_object(ansi_conf_json)
                with TempFolderScope(self.file_system, logger) as root:
                    self._execute_playbook(command_context, ansi_conf, logger)

    def _execute_playbook(self, command_context, ansi_conf, logger):
        """
        :type command_context: ResourceCommandContext
        :type ansi_conf: AnsibleConfiguration
        :type logger: Logger
        :rtype str
        """
        with AnsibleConfigFile(self.file_system, logger) as file:
            file.ignore_ssh_key_checking()
            file.force_color()
            file.set_retry_path("." + os.pathsep)

        with InventoryFile(self.file_system, self.INVENTORY_FILE_NAME, logger) as inventory:
            for host_conf in ansi_conf.hosts_conf:
                inventory.add_host_and_groups(host_conf.ip, host_conf.groups)

        for host_conf in ansi_conf.hosts_conf:
            with HostVarsFile(self.file_system, host_conf.ip, logger) as file:
                file.add_vars(host_conf.parameters)
                file.add_connection_type(host_conf.connection_method)
                if host_conf.connection_method == 'winrm':
                    if host_conf.connection_secured == True:
                        file.add_port('5986')
                        file.add_ignore_winrm_cert_validation()
                    if host_conf.connection_secured == False:
                        file.add_port('5985')
                if host_conf.access_key is not None:
                    file_name = host_conf.ip + '_access_key.pem'
                    with self.file_system.create_file(file_name) as file_stream:
                        file_stream.write(host_conf.access_key)
                    file.add_conn_file(file_name)
                else:
                    file.add_username(host_conf.username)
                    file.add_password(host_conf.password)

        repo = ansi_conf.playbook_repo
        auth = HttpAuth(repo.username, repo.password) if repo.username else None
        playbook_name = self.downloader.get(ansi_conf.playbook_repo.url, auth, logger)

        logger.info('Running the playbook')
        with CloudShellSessionContext(command_context) as session:
            output_writer = ReservationOutputWriter(session, command_context)
            output, error = self.executor.execute_playbook(
                playbook_name, self.INVENTORY_FILE_NAME, ansi_conf.additional_cmd_args, output_writer, logger)
            ansible_result = AnsibleResult(output, error, [h.ip for h in ansi_conf.hosts_conf])
            if not ansible_result.success:
                raise AnsibleException(ansible_result.to_json())


class AnsibleException(Exception):
    pass


    # ansShell = AnsibleShell()
    # logger = Mock()
    #
    # ansShell.downloader._download('https://github.com/QualiSystems/Ansible-Shell/archive/develop.zip',None,logger)
# j = """
# {
#     "additionalArgs": "-vv",
#     "repositoryDetails" : {
#         "url": "http://192.168.30.108:8081/artifactory/ZipedPlaybooks/ApacheForLinux.zip"
#     },
#     "hostsDetails": [
#     {
#         "address": "192.186.85.11",
#         "username": "root",
#         "password": "qs1234",
#         "connectionMethod": "ssh",
#         "groups": [
#             "linux_servers"
#         ]
#     }]
# }
# """
# context = ResourceCommandContext()
# context.resource = ResourceContextDetails()
# context.resource.name = 'TEST Resource'
# shell = AnsibleShell()
# shell.execute_playbook(context, j)
# pass
