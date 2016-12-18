import os
import shutil
import tempfile

class FileSystemService(object):
    def __init__(self):
        pass

    def create_temp_folder(self):
        """
        Create a temporary folder in the os tmp folder.
        :return: The path of the new folder.
        """
        return tempfile.mkdtemp()

    def delete_temp_folder(self, folder):
        """
        Delete a temporary folder from the os tmp folder.
        :param str folder: Folder path.
        """
        shutil.rmtree(folder)

    def create_file(self, path):
        """
        Create (or override) a new file.
        :param str path: The path of the new file (example: 'c:\tmp\file.txt}
        """
        open(path, 'wb')

    # def open_file(self, path):
    #     """
    #     Open file for write
    #     :param str path: The path of the new file (example: 'c:\tmp\file.txt}
    #     :rtype: file
    #     """
    #     return open(path, 'a')