from .file_system_service import FileSystemService
from logging import Logger
import os


class AnsibleConfigFile(object):
    FILE_NAME = 'ansible.cfg'

    def __init__(self, file_system, logger):
        """
        :type file_system: FileSystemService
        :type logger: Logger
        """
        self.file_system = file_system
        self.logger = logger
        self.config_keys = {}

    def __enter__(self):
        self.logger.info('Creating \'%s\' configuration file ...'%AnsibleConfigFile.FILE_NAME)
        return self

    def __exit__(self, type, value, traceback):
        with self.file_system.create_file(AnsibleConfigFile.FILE_NAME) as file_stream:
            lines = ['[defaults]']
            for key, value in self.config_keys.items():
                lines.append(key + ' = ' + value)
            file_stream.write(os.linesep.join(lines).encode('utf-8'))
            self.logger.debug(os.linesep.join(lines))
        self.logger.info('Done.')

    def ignore_ssh_key_checking(self):
        self.config_keys['host_key_checking'] = 'False'

    def force_color(self):
        self.config_keys['force_color'] = '1'

    def set_retry_path(self, save_path):
        self.config_keys['retry_files_save_path'] = str(save_path)
