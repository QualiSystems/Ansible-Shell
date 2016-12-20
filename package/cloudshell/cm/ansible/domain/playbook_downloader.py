import os
import zipfile

from file_system_service import FileSystemService
from requests.auth import HTTPBasicAuth
import requests
import rfc6266
import urllib
from logging import Logger


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

    def get(self, url, auth, logger):
        """
        Download the file from the url (unzip if needed).
        :param str url: Http url of the file.
        :param HttpAuth auth: Authentication to the http server (optional).
        :param Logger logger:
        :rtype [str,int]
        :return The downloaded playbook file name
        """
        file_name, file_size = self._download(url, auth, logger)

        if file_name.endswith(".zip"):
            file_name = self._unzip(file_name, logger)

        return file_name

    def _download(self, url, auth, logger):
        """
        Download the file from the url.
        :param str url: Http url of the file.
        :param HttpAuth auth: Authentication to the http server (optional).
        :param Logger logger:
        :rtype [str,int]
        :return The downloaded file name
        """
        logger.info('Downloading file from \'%s\' ...'%url)
        req = requests.get(url, auth=(auth.username, auth.password) if auth else None, stream=True)

        parse = rfc6266.parse_requests_response(req, relaxed=True)
        file_name = parse.filename_unsafe
        if not file_name:
            file_name = urllib.unquote(req.url[req.url.rfind('/'):])

        with self.file_system.create_file(file_name) as file:
            for chunk in req.iter_content(PlaybookDownloader.CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
            file_size = file.tell()

        logger.info('Done (%s(%s bytes)).' % (file_name, file_size))
        return file_name, file_size

    def _unzip(self, file_name, logger):
        """
        :type file_name: str
        :type logger: Logger
        :return: Playbook file name
        :rtype str
        """
        try:
            logger.info('Zip file was found, extracting file: %s ...' % (file_name))
            zip = zipfile.ZipFile(file_name, 'r')
            zip.extractall("")
            logger.info('Done (extracted %s files).'%len(zip.infolist()))
        # except Exception as e:
        #     logger.info('Failed to extract zip\n\t %s.' % (e.message))  <= we want the driver to stop when zip file failes to be extracted
        finally:
            if zip:
                zip.close()

        yaml_files = [file_name for file_name in os.listdir(".") if file_name.endswith(".yaml") or file_name.endswith(".yml")]
        if len(yaml_files) > 1:
            playbook_name = next((file_name for file_name in yaml_files if file_name == "site.yaml" or file_name == "site.yml"), None)
        if len(yaml_files) == 1:
            playbook_name = yaml_files[0]
        if not playbook_name:
            raise Exception("Playbook file name was not found in zip file")
        logger.info('Found playbook: \'%s\' in zip file' % (playbook_name))

        return playbook_name