import os

from cloudshell.cm.ansible.domain.cancellation_sampler import CancellationSampler
from cloudshell.cm.ansible.domain.file_system_service import FileSystemService
from logging import Logger


class HttpAuth(object):
    def __init__(self, username, password, token):
        self.username = username
        self.password = password
        self.token = token

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

    def get(self, url, auth, logger, cancel_sampler, verify_certificate):
        """
        Download the file from the url (unzip if needed).
        :param str url: Http url of the file.
        :param HttpAuth auth: Authentication to the http server (optional).
        :param Logger logger:
        :param CancellationSampler cancel_sampler:
        :param boolean verify_certificate:
        :rtype [str,int]
        :return The downloaded playbook file name
        """
        file_name, file_size = self._download(url, auth, logger, cancel_sampler, verify_certificate)

        if file_name.endswith(".zip"):
            file_name = self._unzip(file_name, logger)

        return file_name

    def _download(self, url, auth, logger, cancel_sampler, verify_certificate):
        """
        Download the file from the url.
        :param str url: Http url of the file.
        :param HttpAuth auth: Authentication to the http server (optional).
        :param Logger logger:
        :param CancellationSampler cancel_sampler:
        :param boolean verify_certificate:
        :rtype [str,int]
        :return The downloaded file name
        """
        
        response_valid = False
        
        # assume repo is public, try to download without credentials
        logger.info('Starting download script as public... from \'%s\' ...'%url)
        response = self.http_request_service.get_response(url, auth, verify_certificate)
        response_valid = self._is_response_valid(logger ,response, "public")

        if response_valid:
            file_name = self.filename_extractor.get_filename(response)

        # if fails on public and no auth - no point carry on, user need to fix his URL or add credentials
        if not response_valid and auth is None:
            raise Exception('Please make sure the URL is valid, and the credentials are correct and necessary.')

        # repo is private and token provided
        if not response_valid and auth.token is not None:
            logger.info("Token provided. Starting download script with Token...")
            headers = {"Authorization": "Bearer %s" % auth.token }
            response = self.http_request_service.get_response_with_headers(url, headers, verify_certificate)
            
            response_valid = self._is_response_valid(logger, response, "Token")

            if response_valid:
                file_name = self.filename_extractor.get_filename(response)

        # try again with authorization {"Private-Token": "%s" % token}, since gitlab uses that pattern
        if not response_valid and auth.token is not None:
            logger.info("Token provided. Starting download script with Token (private-token pattern)...")
            headers = {"Private-Token": "Bearer %s" % auth.token }
            response = self.http_request_service.get_response_with_headers(url, headers, verify_certificate)
            
            response_valid = self._is_response_valid(logger, response, "Token")

            if response_valid:
                file_name = self.filename_extractor.get_filename(response)

        # repo is private and credentials provided, and Token did not provided or did not work. this will NOT work for github. github require Token
        if not response_valid and (auth.username is not None and auth.password is not None):
            logger.info("username\password provided, Starting download script with username\password...")
            response = self.http_request_service.get_response(url, auth, verify_certificate)

            response_valid = self._is_response_valid(logger, response, "username\password")

            if response_valid:
                file_name = self.filename_extractor.get_filename(response)

        if not response_valid:
            raise Exception('Failed to download script file. please check the logs for more details.')

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

    def _is_response_valid(self, logger, response, request_method):
        try:
            self._validate_response(response)
            response_valid = True
        except Exception as ex:
            failure_message = "failed to Authorize repository with %s" % request_method
            logger.error(failure_message + " :" + str(ex))
            response_valid = False

        return response_valid


    def _validate_response(self, response):
        if response.status_code < 200 or response.status_code > 300:            
            raise Exception('Failed to download script file: '+str(response.status_code)+' '+response.reason+
                                '. Please make sure the URL is valid, and the credentials are correct and necessary.')
