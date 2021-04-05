import os
from .file_system_service import FileSystemService
from logging import Logger


class TempFolderScope(object):
    def __init__(self, file_system, logger):
        """
        :type file_system: FileSystemService
        :type logger: Logger
        """
        self.file_system = file_system
        self.logger = logger

    def __enter__(self):
        """
        :rtype: str
        """
        self.logger.info('Creating temp folder and making it the working dir...')
        self.folder = self.file_system.create_temp_folder()
        self.prev_working_dir = self.file_system.get_working_dir()
        self.file_system.set_working_dir(self.folder)
        self.logger.info('Done (folder: %s)' % self.folder)
        return self.folder

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info('Deleting temp folder and restoring the previous working dir...')
        self.file_system.set_working_dir(self.prev_working_dir)
        self.file_system.delete_temp_folder(self.folder)
        self.logger.info('Done (folder: %s)' % self.folder)