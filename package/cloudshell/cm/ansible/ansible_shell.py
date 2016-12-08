from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.context import ResourceCommandContext, ResourceRemoteCommandContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from domain.file_system_service import FileSystemService
from domain.inventory_file_creator import InventoryFileCreator
from domain.playbook_downloader import PlaybookDownloader
from domain.playbook_downloader import HttpAuth


class AnsibleShell(object):
    def __init__(self):
        self.fileSystem = FileSystemService()

    def run_ansible_test(self, command_context):
        """
        Will delete the reservation vpc and all related resources including all remaining instances
        :param ResourceCommandContext command_context:
        :return: json string response
        :rtype: str
        """
        with LoggingSessionContext(command_context) as logger:
            logger.info('Creating temp ansible root folder')
            root = self.fileSystem.createTempFolder()

            logger.info('Creating inventory file')
            with InventoryFileCreator(self.fileSystem, root) as creator:
                creator.add_groups(['servers/web', 'windows/web'])
                creator.add_host('192.168.23.45', 'web')
                creator.add_vars('192.168.23.45', {'ram': '1GB', 'win': 'true', 'quick': 'true'})

            logger.info('Downloading playbook file')
            downloader = PlaybookDownloader(self.fileSystem)
            downloader.get('http:\\blabla.com\playbook123.zip', HttpAuth('admin', 'password1'), root)

            logger.info('Running the playbook')


            logger.info('Delete the temp folder')
            self.fileSystem.deleteTempFolder(root)