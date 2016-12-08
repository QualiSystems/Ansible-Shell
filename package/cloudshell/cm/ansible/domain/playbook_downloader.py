import os
from file_system_service import FileSystemService


class PlaybookDownloader(object):
    def __init__(self, file_system):
        """
        :param FileSystemServicefile_system:
        """
        self.file_system = file_system

    def get(self, url, auth, target_folder):
        """
        Download the file from the url (unzip if needed) to the target folder.
        :param str url: Http url of the file.
        :param HttpAuth auth: Authentication to the http server (optional).
        :param str target_folder: The target folder to download the files to.
        """
        pass


class HttpAuth(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
