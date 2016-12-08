import os
import shutil
import tempfile

class FileSystemService(object):
    def __init__(self):
        pass

    def createTempFolder(self):
        """
        Create a temporary folder in the os tmp folder.
        :return: The path of the new folder.
        """
        return tempfile.mkdtemp()

    def deleteTempFolder(self, folder):
        """
        Delete a temporary folder from the os tmp folder.
        :param str folder: Folder path.
        """
        shutil.rmtree(folder)

    def createFile(self, path):
        """
        Create (or override) a new file.
        :param str path: The path of the new file (example: 'c:\tmp\file.txt}
        :return: The file.
        """
        return open(path, 'w+');