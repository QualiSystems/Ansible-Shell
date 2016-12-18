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
import zipfile



class AnsibleShell(object):
    def __init__(self):
        self.file_system = FileSystemService()
        self.downloader = PlaybookDownloader(self.file_system)

    def _getPlaybooknameFromZip(self, zipFileName, extractDir, logger):
        logger.info('Zip file was found, extracting file:%s' % (zipFileName))
        zip = zipfile.ZipFile(zipFileName, 'r')
        try:
            zip.extractall(extractDir)
        except Exception as e:
            logger.info('Failed to extract zip\n\t %s' % (e.message))
        finally:
            zip.close()
        yamlFiles = []
        for yamlFile in os.listdir(extractDir):
            if yamlFile.endswith(".yaml") or yamlFile.endswith(".yml"):
                yamlFiles.append(yamlFile)
                break;
        if yamlFiles.count() > 1:
            playbook_name = next((pName for pName in yamlFiles if pName == "site.yaml" or pName == "site.yml"), None)
            for fileName in yamlFiles:
                if fileName == "site.yaml" or fileName == "site.yaml":
                    playbook_name = fileName;
                    break;
        else:
            playbook_name = yamlFiles[0]
        if not playbook_name:
            raise Exception("playbook file name was not found in zip file")
        logger.info('Found playbook: \'%s\' in zip file' % (playbook_name))
        return playbook_name

    def execute_playbook(self, command_context, ansi_conf):
        """
        :param ResourceCommandContext command_context:
        :param AnsibleConfiguration ansi_conf:
        """
        with LoggingSessionContext(command_context) as logger:
            logger.info('Creating temp ansible root folder')
            root = self.file_system.createTempFolder()
            logger.info('Done.\n\t root=%s'%root)

            logger.info('Creating inventory file')
            inventoryFileName = 'hosts'
            with InventoryFileCreator(self.file_system, os.path.join(root, inventoryFileName)) as inventory:
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
                logger.info('Done.\n\t hosts=%s' % inventory.to_file_content())

            logger.info('Downloading playbook file')
            auth = None
            if ansi_conf.playbook_repo.username is not None:
                auth = HttpAuth(ansi_conf.playbook_repo.username, ansi_conf.playbook_repo.password)
            playbook_name,playbook_size = self.downloader.get(ansi_conf.playbook_repo.url, auth, root)
            logger.info('Done.\n\t file=%s(%s bytes)' % (playbook_name, playbook_size))

            if playbook_name.endswith(".zip"):
                playbook_name = self._getPlaybooknameFromZip(playbook_name,root,logger)

            logger.info('Running the playbook')
            ansibleParser = AnsiblePlaybookParser()
            ansibleResult = AnsibleCommandExecutor(ansibleParser,playbook_name,inventoryFileName).executeCommand()

            logger.info('Deleting the temp folder')
            self.file_system.deleteTempFolder(root)
            logger.info('Done.')