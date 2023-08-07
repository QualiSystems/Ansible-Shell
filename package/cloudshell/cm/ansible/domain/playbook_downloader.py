import logging
import os
import re
from urllib import parse

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
    GITLAB_API_TEMPLATE_MAP = {
        "file":   "{protocol}://{domain}/api/v4/projects/{project}/repository/files/{file_path}/raw",
        "folder": "{protocol}://{domain}/api/v4/projects/{project}/repository/archive.zip",
    }
    URL_SEPARATOR = "#"

    def __init__(
            self,
            file_system,
            zip_service,
            http_request_service,
            filename_extractor
    ):
        self.file_system = file_system
        self.zip_service = zip_service
        self.http_request_service = http_request_service
        self.filename_extractor = filename_extractor

    def get(self, url, auth, logger, cancel_sampler, verify_certificate):
        """Download the file from the url (unzip if needed).

        :param str url: Http url of the file.
        :param HttpAuth auth: Authentication to the http server (optional).
        :param Logger logger:
        :param CancellationSampler cancel_sampler:
        :param boolean verify_certificate:
        :rtype [str,int]
        :return The downloaded playbook file name
        """
        if self.URL_SEPARATOR in url:
            url, playbook_path = url.split(self.URL_SEPARATOR, 1)
        else:
            playbook_path = None

        file_name, file_size = self._download(
            url=url,
            auth=auth,
            logger=logger,
            cancel_sampler=cancel_sampler,
            verify_certificate=verify_certificate
        )

        if file_name.endswith(".zip"):
            playbook_path = self._unzip(file_name, logger, playbook_path)

        if not playbook_path:
            playbook_path = file_name

        return playbook_path

    def _download(self, url, auth, logger, cancel_sampler, verify_certificate):
        """Download the file from the url.

        :param str url: Http url of the file.
        :param HttpAuth auth: Authentication to the http server (optional).
        :param Logger logger:
        :param CancellationSampler cancel_sampler:
        :param boolean verify_certificate:
        :rtype [str,int]
        :return The downloaded file name
        """
        logger.debug("URL: {}".format(url))
        logger.debug("Verify Certificate: {}".format(verify_certificate))
        logger.debug("Username: {}".format(auth.username))
        logger.debug("Password: {}".format(auth.password))
        logger.debug("Token: {}".format(auth.token))

        if not verify_certificate:
            logger.info("Skipping server certificate")

        if auth and auth.token:
            # GitLab uses {"Private-Token": token}
            logger.info(
                "Token provided. Starting download script with Private-Token ..."
            )
            gitlab_api_url = self._convert_gitlab_url(url=url, logger=logger)
            if gitlab_api_url:

                headers = {"Private-Token": auth.token}
                response = self.http_request_service.get_response_with_headers(
                    url=gitlab_api_url,
                    headers=headers,
                    verify_certificate=verify_certificate
                )

                response_valid = self._is_response_valid(logger, response, "Token")
            else:
                # cannot assemble GitLab API URL that means it's not GitLab
                response_valid = False

            if not response_valid and auth.token is not None:
                logger.info(
                    "Token provided. Starting download script with Bearer Token..."
                )
                headers = {"Authorization": "Bearer {}".format(auth.token)}
                response = self.http_request_service.get_response_with_headers(
                    url=url,
                    headers=headers,
                    verify_certificate=verify_certificate
                )
                response_valid = self._is_response_valid(logger, response, "Token")

        elif auth and auth.username and auth.password is not None:
            logger.info(
                "Username and Password provided. "
                "Starting download script with username/password..."
            )
            response = self.http_request_service.get_response(
                url=url,
                auth=auth,
                verify_certificate=verify_certificate)
            response_valid = self._is_response_valid(
                logger,
                response,
                "Username/Password"
            )

        else:
            logger.info("Starting download script as public...")
            response = self.http_request_service.get_response(
                url=url,
                auth=None,
                verify_certificate=verify_certificate
            )
            response_valid = self._is_response_valid(
                logger,
                response,
                "Public")

        if response_valid:
            file_name = self.filename_extractor.get_filename(response)
        else:
            raise Exception(
                "Failed to download script file. "
                "Please make sure the URL is valid, "
                "and the credentials are correct and necessary."
            )

        with self.file_system.create_file(file_name) as file:
            for chunk in response.iter_content(PlaybookDownloader.CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
                cancel_sampler.throw_if_canceled()
            file_size = file.tell()

        logger.info(
            "Done (file: {file}, size: {size} bytes)).".format(
                file=file_name,
                size=file_size
            )
        )
        return file_name, file_size

    def _unzip(self, archive_name, logger, playbook_name=None):
        """Unzip archive and determine playbook name."""
        logger.info(
            "Zip file was found, extracting file: {arch_name} ...".format(
                arch_name=archive_name
            )
        )
        zip_files = self.zip_service.extract_all(archive_name)
        logger.info("Done (extracted {} files).".format(len(zip_files)))
        logger.info("Files: {sep}{files}".format(
            sep=os.linesep,
            files=(os.linesep+"\t").join(zip_files))
        )
        # if playbook_name:
        #     for filename in zip_files:

        if not playbook_name:
            # yaml_files = [
            #     file_name for file_name in self.file_system.get_entries(
            #         self.file_system.get_working_dir()
            #     ) if file_name.endswith(".yaml") or file_name.endswith(".yml")
            # ]
            yaml_files = [
                file_name for file_name in zip_files if
                file_name.endswith(".yaml") or file_name.endswith(".yml")
            ]
            if len(yaml_files) > 1:
                playbook_name = next(
                    (
                        file_name for file_name in yaml_files if
                        "site.yaml" in file_name or "site.yml" in file_name
                    ), None
                )

            if len(yaml_files) == 1:
                playbook_name = yaml_files[0]

        if not playbook_name:
            raise Exception("Playbook file name was not found in zip file")
        logger.info("Found playbook: '{}' in zip file".format(playbook_name))

        return playbook_name

    def _convert_gitlab_url(self, url, logger):
        """Try to convert URL to Gitlab API URL.

        Input examples:
        - Single file
            http://192.168.85.27/api/v4/projects/root%2Fmy_project/repository/files/bash_scripts%2Fsimple%2Ebash/raw?ref=main
            http://192.168.85.27/api/v4/projects/root%2Fmy_project/repository/files/bash_scripts%2Fsimple%2Ebash/raw
            http://192.168.85.27/root/my_project/-/raw/main/bash_scripts/simple.bash
            http://192.168.85.27/root/my_project/-/blob/main/bash_scripts/simple.bash

        - Folder
            http://192.168.65.22/api/v4/projects/root%2Fmy_project/repository/archive.zip?ref=main&path=ansible_scripts
            http://192.168.65.22/root/my_project/-/archive/main/my_project-main.zip?path=ansible_scripts#pl1.yaml

        - Repo
            http://192.168.65.22/api/v4/projects/root%2Fmy_project/repository/archive.zip?ref=main
            http://192.168.65.22/root/my_project/-/archive/main/my_project-main.zip#pl1.yaml

        Output examples:
        - Single file
            http://192.168.85.27/api/v4/projects/root%2Fmy_project/repository/files/bash_scripts%2Fsimple%2Ebash/raw?ref=main

        - Folder
            http://192.168.65.22/api/v4/projects/root%2Fmy_project/repository/archive.zip?ref=main&path=ansible_scripts

        - Repo
            http://192.168.65.22/api/v4/projects/root%2Fmy_project/repository/archive.zip?ref=main

        """
        logger.debug("URL to convert: {}".format(url))
        parsed_url = parse.urlsplit(url=url)
        queries = dict(parse.parse_qsl(parsed_url.query))

        if "api/v4/projects" in parsed_url.path:
            regex = r"/api/v4/projects/(?P<project>.+)/repository/files/(?P<file>.+(yml|yaml|zip))"
        else:
            regex = r"/(?P<project>.+)/-/(blob|raw|archive)/(?P<branch>[^/]+)/(?P<file>.+\.(yml|yaml|zip))"

        match = re.search(
            regex,
            parsed_url.path,
            re.IGNORECASE
        )

        if match:
            branch = queries.get("ref") or match.groupdict().get("branch")
            filename = match.groupdict().get("file")
            logger.debug("Protocol: {}".format(parsed_url.scheme))
            logger.debug("Domain: {}".format(parsed_url.netloc))
            logger.debug("Project: {}".format(match.groupdict().get("project")))
            logger.debug("Path: {}".format(queries.get("path")))
            logger.debug("Branch: {}".format(branch))
            logger.debug("File: {}".format(filename))

            if queries.get("path") or filename.endswith(".zip"):
                url_template = self.GITLAB_API_TEMPLATE_MAP.get("folder")
            else:
                url_template = self.GITLAB_API_TEMPLATE_MAP.get("file")

            converted_url = url_template.format(
                protocol=parsed_url.scheme,
                domain=parsed_url.netloc,
                project=match.group("project").replace("/", "%2F").replace(".", "%2E"),
                file_path=match.group("file").replace("/", "%2F").replace(".", "%2E")
            )

            if queries:
                params = "?"
                for k, v in queries.items():
                    params += "{key}={value}".format(key=k, value=v)
                converted_url += params
        else:
            converted_url = url

        logger.debug("Possible GitLab API URL: {}".format(converted_url))
        return converted_url

    def _is_response_valid(self, logger, response, request_method):
        try:
            self._validate_response(response)
            response_valid = True
        except Exception as ex:
            logger.error(
                "Failed to Authorize repository with '{method}': {error}".format(
                    method=request_method,
                    error=str(ex)
                )
            )
            response_valid = False

        return response_valid

    def _validate_response(self, response):
        if response.status_code < 200 or response.status_code > 300:
            raise Exception(
                "Failed to download script file: {code} {reason}."
                "Please make sure the URL is valid,"
                "and the credentials are correct and necessary.".format(
                    code=str(response.status_code),
                    reason=response.reason
                )
            )
