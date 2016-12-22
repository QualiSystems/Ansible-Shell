import os
from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from domain.file_system_service import FileSystemService
from domain.inventory_file import InventoryFile
from domain.playbook_downloader import PlaybookDownloader
from domain.playbook_downloader import HttpAuth
from domain.ansible_configutarion import AnsibleConfiguration
from domain.ansible_configutarion import HostConfiguration
from domain.ansible_command_executor import AnsibleCommandExecutor, ReservationOutputWriter
from domain.ansible_conflig_file import AnsibleConfigFile
from domain.host_vars_file import HostVarsFile
from domain.output.ansibleResult import AnsiblePlaybookParser
from domain.temp_folder_scope import TempFolderScope


class AnsibleShell(object):
    def __init__(self, file_system=None, playbook_downloader=None, playbook_executor=None):
        """
        :type file_system: FileSystemService
        :type playbook_downloader: PlaybookDownloader
        :type playbook_executor: AnsibleCommandExecutor
        """
        self.file_system = file_system or FileSystemService()
        self.downloader = playbook_downloader or PlaybookDownloader(self.file_system)
        self.executor = playbook_executor or AnsibleCommandExecutor(AnsiblePlaybookParser())

    def execute_playbook(self, command_context, ansi_conf):
        """
        :type command_context: ResourceCommandContext
        :type ansi_conf: AnsibleConfiguration
        :rtype str
        """
        with LoggingSessionContext(command_context) as logger:
            with TempFolderScope(self.file_system, logger) as root:

                inventory_file_name = 'hosts'

                with AnsibleConfigFile(self.file_system, logger) as file:
                    file.ignore_ssh_key_checking()
                    file.force_color()

                with InventoryFile(self.file_system, inventory_file_name, logger) as inventory:
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
                with CloudShellSessionContext(command_context) as session:
                    output_writer = ReservationOutputWriter(session, command_context)
                    ansible_result = self.executor.execute_playbook(
                        playbook_name, inventory_file_name, ansi_conf.additional_cmd_args,
                    return ansible_result #TODO: parse to json
                    # print ansible_result.Success
                    # print ansible_result.Result



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