import os
from file_system_service import FileSystemService
from requests.auth import HTTPBasicAuth
import requests
import rfc6266
import urllib


class HttpAuth(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class PlaybookDownloader(object):
    CHUNK_SIZE = 1024 * 1024

    def __init__(self, file_system):
        """
        :param FileSystemService file_system:
        """
        self.file_system = file_system

    def get(self, url, auth, target_folder):
        """
        Download the file from the url (unzip if needed) to the target folder.
        :param str url: Http url of the file.
        :param HttpAuth auth: Authentication to the http server (optional).
        :param str target_folder: The target folder to download the files to.
        :rtype [str,int]
        :return The downloaded file name
        """
        req = requests.get(url, auth=(auth.username, auth.password), stream=True)

        parse = rfc6266.parse_requests_response(req, relaxed=True)
        file_name = parse.filename_unsafe

        if not file_name:
            file_name = urllib.unquote(req.url[req.url.rfind('/'):])

        with self.file_system(os.path.join(target_folder, file_name)) as file:
            for chunk in req.iter_content(PlaybookDownloader.CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
            file_size = file.tell()
        return file_name, file_size
