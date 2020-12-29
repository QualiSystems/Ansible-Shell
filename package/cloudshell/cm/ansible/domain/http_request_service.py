import requests
from requests import Response
from cloudshell.cm.ansible.domain.gitlab_api_url_validator import is_gitlab_rest_url


class HttpRequestService(object):
    def get_response(self, url, auth, logger=None):
        """
        :param url:
        :param auth:
        :param logging.Logger logger:
        :return:
        """
        is_gitlab_url = is_gitlab_rest_url(url)
        if is_gitlab_url:
            response = self._get_gitlab_response(url, auth, logger)
            self._validate_response_status_code(response)
            self._invalidate_gitlab_login_page(response)
        else:
            auth = (auth.username, auth.password) if auth else None
            response = requests.get(url, auth=auth, stream=True, verify=False)
            self._validate_response_status_code(response)
            self._invalidate_html(response.content)
        return response

    @staticmethod
    def _get_gitlab_response(url, auth, logger=None):
        """
        :param url:
        :param auth:
        :param logging.Logger logger:
        :return:
        """
        # GITLAB REST API CALL - ADDING TOKEN HEADER
        if logger:
            logger.info("downloading script via Gitlab Rest API call: {}".format(url))
        if auth:
            headers = {"PRIVATE-TOKEN": auth.password}
            return requests.get(url, stream=True, verify=False, headers=headers)
        else:
            return requests.get(url, stream=True, verify=False)

    @staticmethod
    def _validate_response_status_code(response):
        if 200 > response.status_code > 300:
            raise Exception('Failed to download script file: ' + str(response.status_code) + ' ' + response.reason +
                            '. Please make sure the URL is valid, and the credentials are correct and necessary.')

    @staticmethod
    def _is_content_html(content):
        return content.lstrip('\n\r').lower().startswith('<!doctype html>')

    def _invalidate_html(self, content):
        if self._is_content_html(content):
            raise Exception('Failed to download script file: url points to an html file')

    def _invalidate_gitlab_login_page(self, response):
        """

        :param Response response: requests response object
        :return:
        """
        if self._is_content_html(response.content) and "users/sign_in" in response.url:
            raise Exception('Authentication failed. Reached Gitlab Login. Gitlab Access Token required.')


