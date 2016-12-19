import os
from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.context import ResourceCommandContext, ResourceRemoteCommandContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from domain.file_system_service import FileSystemService
from domain.inventory_file_creator import InventoryFileCreator
from domain.playbook_downloader import PlaybookDownloader
from domain.playbook_downloader import HttpAuth
from domain.ansible_configutarion import AnsibleConfiguration
from domain.ansible_command_executor import AnsibleCommandExecutor
from domain.output.ansibleResult import AnsiblePlaybookParser
from domain.TempFolderScope import TempFolderScope


class AnsibleShell(object):
    def __init__(self):
        self.file_system = FileSystemService()
        self.downloader = PlaybookDownloader(self.file_system)
        self.executer = AnsibleCommandExecutor(AnsiblePlaybookParser())

    def execute_playbook(self, command_context, ansi_conf):
        """
        :param ResourceCommandContext command_context:
        :param AnsibleConfiguration ansi_conf:
        """
        with LoggingSessionContext(command_context) as logger:
            with TempFolderScope(self.file_system, logger) as root:

                logger.info('Creating inventory file...')
                inventory_file_name = 'hosts'
                with InventoryFileCreator(self.file_system, os.path.join(root, inventory_file_name)) as inventory:
                    for host_conf in ansi_conf.hosts_conf:
                        inventory.add_host(host_conf.ip)
                        inventory.set_host_groups(host_conf.ip, host_conf.groups)
                        inventory.set_host_vars(host_conf.ip, host_conf.parameters)
                        inventory.set_host_conn(host_conf.ip, host_conf.connection_method)
                        if host_conf.access_key is not None:
                            file_name = host_conf.ip + '_access_key.pem'
                            with self.file_system.create_file(os.path.join(root, file_name)) as file_stream:
                                file_stream.write(host_conf.access_key)
                            inventory.set_host_conn_file(host_conf.ip, file_name)
                        else:
                            inventory.set_host_user(host_conf.ip, host_conf.username)
                            inventory.set_host_pass(host_conf.ip, host_conf.password)
                    logger.debug(inventory.to_file_content())
                logger.info('Done.\n\t hosts=%s' % inventory.to_file_content())

                auth = None
                if ansi_conf.playbook_repo.username is not None:
                    auth = HttpAuth(ansi_conf.playbook_repo.username, ansi_conf.playbook_repo.password)
                playbook_name = self.downloader.get(ansi_conf.playbook_repo.url, auth, root)

                logger.info('Running the playbook')
                ansible_result = self.executer.execute_playbook(playbook_name,inventory_file_name)
                print ansible_result.Success
                print ansible_result.Result