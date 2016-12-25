import json
import os

from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from domain.cloudshell_session_provider import CloudShellSessionProvider
from domain.file_system_service import FileSystemService
from domain.inventory_file import InventoryFile
from domain.playbook_downloader import PlaybookDownloader, HttpAuth
from domain.ansible_configutarion import AnsibleConfiguration, HostConfiguration, PlaybookRepository
from domain.ansible_command_executor import AnsibleCommandExecutor, ReservationOutputWriter
from domain.ansible_conflig_file import AnsibleConfigFile
from domain.host_vars_file import HostVarsFile
from domain.output.ansibleResult import AnsiblePlaybookParser
from domain.temp_folder_scope import TempFolderScope


class AnsibleShell(object):
    INVENTORY_FILE_NAME = 'hosts'

    def __init__(self, file_system=None, playbook_downloader=None, playbook_executor=None, session_provider=None):
        """
        :type file_system: FileSystemService
        :type playbook_downloader: PlaybookDownloader
        :type playbook_executor: AnsibleCommandExecutor
        :type session_provider: CloudShellSessionProvider
        """
        self.file_system = file_system or FileSystemService()
        self.downloader = playbook_downloader or PlaybookDownloader(self.file_system)
        self.executor = playbook_executor or AnsibleCommandExecutor(AnsiblePlaybookParser(self.file_system))
        self.session_provider = session_provider or CloudShellSessionProvider()

    def execute_playbook(self, command_context, ansi_conf_json):
        """
        :type command_context: ResourceCommandContext
        :type ansi_conf_json: str
        :rtype str
        """
        with LoggingSessionContext(command_context) as logger:
            logger.debug('\'execute_playbook\' is called with the configuration json: \n'+ansi_conf_json)

        ansi_conf = self._json_to_object(ansi_conf_json)
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                with TempFolderScope(self.file_system, logger) as root:
                    result = self._execute_playbook(command_context, ansi_conf, logger)
                    return result

    def _execute_playbook(self,command_context, ansi_conf, logger):
        """
        :type command_context: ResourceCommandContext
        :type ansi_conf: AnsibleConfiguration
        :type logger: Logger
        :rtype str
        """
        with AnsibleConfigFile(self.file_system, logger) as file:
            file.ignore_ssh_key_checking()
            file.force_color()
            file.set_retry_path("."+os.pathsep)

        with InventoryFile(self.file_system, self.INVENTORY_FILE_NAME, logger) as inventory:
            for host_conf in ansi_conf.hosts_conf:
                inventory.add_host_and_groups(host_conf.ip, host_conf.groups)

        for host_conf in ansi_conf.hosts_conf:
            with HostVarsFile(self.file_system, host_conf.ip, logger) as file:
                file.add_vars(host_conf.parameters)
                file.add_connection_type(host_conf.connection_method)
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
        with self.session_provider.get(command_context) as session:
            output_writer = ReservationOutputWriter(session, command_context)
            ansible_result = self.executor.execute_playbook(
                playbook_name, self.INVENTORY_FILE_NAME, ansi_conf.additional_cmd_args,
                output_writer, logger)
            return ansible_result #TODO: parse to json

    def _json_to_object(self, json_str):
        """
        Decodes a json string to an AnsibleConfiguration instance.
        :type json_str: str
        :rtype AnsibleConfiguration
        """
        json_obj = json.loads(json_str)

        ansi_conf = AnsibleConfiguration()
        ansi_conf.additional_cmd_args = json_obj['additionalArgs']
        ansi_conf.playbook_repo.url = json_obj['repositoryDetails']['url']
        ansi_conf.playbook_repo.username = json_obj['repositoryDetails']['username']
        ansi_conf.playbook_repo.password = json_obj['repositoryDetails']['password']

        for json_host in json_obj['hostsDetails']:
            host_conf = HostConfiguration()
            host_conf.ip = json_host['address']
            host_conf.connection_method = json_host['connectionMethod']
            host_conf.username = json_host['userName']
            host_conf.password = json_host['password']
            host_conf.access_key = json_host['accessKey']
            host_conf.groups = json_host['groups']
            if json_host['parameters'] is not None:
                host_conf.parameters = dict(
                    (i['name'], i['value']) for i in json_host['parameters'])
            ansi_conf.hosts_conf.append(host_conf)

        return ansi_conf

# conf = AnsibleConfiguration()
# conf.playbook_repo.url = 'http://192.168.30.108:8081/artifactory/ZipedPlaybooks/ApacheForLinux.zip'
# host = HostConfiguration()
# host.ip = '192.168.85.11'
# host.groups = ['linux_servers']
# host.username = 'root'
# host.password = 'qs1234'
# host.connection_method = 'ssh'
# host.parameters['params'] = '1234'
# conf.hosts_conf.append(host)
# context = ResourceCommandContext()
# context.resource = ResourceContextDetails()
# context.resource.name = 'TEST Resource'
# shell = AnsibleShell()
# shell.execute_playbook(context, conf)
# pass