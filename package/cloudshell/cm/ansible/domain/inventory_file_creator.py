import os
from file_system_service import FileSystemService


class InventoryFileCreator(object):

    def __init__(self, file_system, root_folder):
        """
        :param FileSystemServicefile_system:
        :param str root_folder:
        """
        file_path = os.path.join(root_folder, 'hosts')
        self.file = file_system.createFile(file_path)

    def __enter__(self):
        """
        :param FileSystemService file_system:
        """
        return self

    def __exit__(self, type, value, traceback):
        file.flush()
        file.close()

    def add_groups(self, groups):
        """
        Add groups hierarchy to inventory.
        :param str[] groups: Array of groups as strings (example: ['servers/web', 'servers/db']
        """
        pass

    def add_host(self, host, group):
        """
        Add host to inventory.
        :param str host: The host name/ip to add.
        :param str group: The group of the host (optional).
        """
        pass

    def add_vars(self, host, parameters):
        """
        Add host parameters to inventory.
        :param Dictionary paramters:
        :return:
        """
        pass