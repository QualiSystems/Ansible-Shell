import os

from cloudshell.cm.ansible.domain.cancellation_sampler import CancellationSampler
from file_system_service import FileSystemService
from logging import Logger


class HttpAuth(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class PlaybookDownloader(object):
    CHUNK_SIZE = 1024 * 1024

    def __init__(self, file_system, zip_service, http_request_service, filename_extractor):
        """
        :param FileSystemService file_system:
        """
        self.file_system = file_system
        self.zip_service = zip_service
        self.http_request_service = http_request_service
        self.filename_extractor = filename_extractor

    def get(self, url, auth, logger, cancel_sampler):
        """
        Download the file from the url (unzip if needed).
        :param str url: Http url of the file.
        :param HttpAuth auth: Authentication to the http server (optional).
        :param Logger logger:
        :param CancellationSampler cancel_sampler:
        :rtype [str,int]
        :return The downloaded playbook file name
        """
        file_name, file_size = self._download(url, auth, logger, cancel_sampler)

        if file_name.endswith(".zip"):
            file_name = self._unzip(file_name, logger)

        return file_name

    def _download(self, url, auth, logger, cancel_sampler):
        """
        Download the file from the url.
        :param str url: Http url of the file.
        :param HttpAuth auth: Authentication to the http server (optional).
        :param Logger logger:
        :param CancellationSampler cancel_sampler:
        :rtype [str,int]
        :return The downloaded file name
        """
        logger.info('Downloading file from \'%s\' ...'%url)
        response = self.http_request_service.get_response(url, auth)
        file_name = self.filename_extractor.get_filename(response)

        with self.file_system.create_file(file_name) as file:
            for chunk in response.iter_content(PlaybookDownloader.CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
                cancel_sampler.throw_if_canceled()
            file_size = file.tell()

        logger.info('Done (file: %s, size: %s bytes)).' % (file_name, file_size))
        return file_name, file_size

    def _unzip(self, file_name, logger):
        """
        :type file_name: str
        :type logger: Logger
        :return: Playbook file name
        :rtype str
        """
        logger.info('Zip file was found, extracting file: %s ...' % (file_name))
        zip_files = self.zip_service.extract_all(file_name)
        logger.info('Done (extracted %s files).'%len(zip_files))
        logger.info('Files: ' + os.linesep + (os.linesep+'\t').join(zip_files))

        yaml_files = [file_name for file_name in self.file_system.get_entries(self.file_system.get_working_dir()) if file_name.endswith(".yaml") or file_name.endswith(".yml")]
        playbook_name = None
        if len(yaml_files) > 1:
            playbook_name = next((file_name for file_name in yaml_files if file_name == "site.yaml" or file_name == "site.yml"), None)
        if len(yaml_files) == 1:
            playbook_name = yaml_files[0]
        if not playbook_name:
            raise Exception("Playbook file name was not found in zip file")
        logger.info('Found playbook: \'%s\' in zip file' % (playbook_name))

        return playbook_name
