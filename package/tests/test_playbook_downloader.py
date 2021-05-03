from unittest import TestCase
from mock import Mock, patch

from cloudshell.cm.ansible.domain.filename_extractor import FilenameExtractor
from cloudshell.cm.ansible.domain.http_request_service import HttpRequestService
from cloudshell.cm.ansible.domain.playbook_downloader import PlaybookDownloader, HttpAuth
from tests.mocks.file_system_service_mock import FileSystemServiceMock


class TestPlaybookDownloader(TestCase):

    def setUp(self):
        self.zip_service = Mock()
        self.http_request_serivce = HttpRequestService()
        self.file_system = FileSystemServiceMock()
        self.filename_extractor = FilenameExtractor()
        self.playbook_downloader = PlaybookDownloader(self.file_system, self.zip_service, self.http_request_serivce, self.filename_extractor)
        self.logger = Mock()
        self.logger.info = lambda msg: ""
        self.reqeust = Mock()

    def _set_extract_all_zip(self, files_to_create):
        for file_to_create in files_to_create:
            self.file_system.create_file(file_to_create)
        return files_to_create

    def test_playbook_downloader_zip_file_one_yaml(self):
        self.zip_service.extract_all = lambda zip_file_name: self._set_extract_all_zip(["lie.yaml"])
        auth = HttpAuth("user", "pass", "token")
        self.reqeust.url = "blabla/lie.zip"
        dic = dict([('content-disposition', 'lie.zip')])
        self.reqeust.headers = dic
        self.reqeust.iter_content.return_value = ''
        self.http_request_serivce.get_response=Mock(return_value=self.reqeust)
        self.http_request_serivce.get_response_with_headers = Mock(return_value=self.reqeust)
        self.playbook_downloader._is_response_valid = Mock(return_value=True)

        file_name = self.playbook_downloader.get("", auth, self.logger, Mock(), True)
        self.assertEqual(file_name, "lie.yaml")


    def test_playbook_downloader_zip_file_two_yaml_correct(self):
        self.zip_service.extract_all = lambda zip_file_name: self._set_extract_all_zip(["lie.yaml", "site.yaml"])
        auth = HttpAuth("user", "pass", "token")
        self.reqeust.url = "blabla/lie.zip"
        dic = dict([('content-disposition', 'lie.zip')])
        self.reqeust.headers = dic
        self.reqeust.iter_content.return_value = ''
        self.http_request_serivce.get_response = Mock(return_value=self.reqeust)
        self.http_request_serivce.get_response_with_headers = Mock(return_value=self.reqeust)
        self.playbook_downloader._is_response_valid = Mock(return_value=True)

        file_name = self.playbook_downloader.get("", auth, self.logger, Mock(), True)

        self.assertEqual(file_name, "site.yaml")

    def test_playbook_downloader_zip_file_two_yaml_incorrect(self):
        self.zip_service.extract_all = lambda zip_file_name: self._set_extract_all_zip(["lie.yaml", "lie2.yaml"])
        auth = HttpAuth("user", "pass", "token")  
        self.reqeust.url = "blabla/lie.zip"
        dic = dict([('content-disposition', 'lie.zip')])
        self.reqeust.headers = dic
        self.reqeust.iter_content.return_value = ''
        self.http_request_serivce.get_response = Mock(return_value=self.reqeust)
        self.http_request_serivce.get_response_with_headers = Mock(return_value=self.reqeust)
        self.playbook_downloader._is_response_valid = Mock(return_value=True)
        with self.assertRaises(Exception) as e:
            self.playbook_downloader.get("", auth, self.logger, Mock(), True)
        self.assertEqual(str(e.exception),"Playbook file name was not found in zip file")

    def test_playbook_downloader_with_one_yaml(self):
        auth = HttpAuth("user", "pass", "token")        
        self.reqeust.url = "blabla/lie.yaml"
        dic = dict([('content-disposition', 'lie.yaml')])
        self.reqeust.headers = dic
        self.reqeust.iter_content.return_value = 'hello'
        self.http_request_serivce.get_response = Mock(return_value=self.reqeust)
        self.http_request_serivce.get_response_with_headers = Mock(return_value=self.reqeust)
        self.playbook_downloader._is_response_valid = Mock(return_value=True)

        file_name = self.playbook_downloader.get("", auth, self.logger, Mock(), True)

        self.assertEqual(file_name, "lie.yaml")

    def test_playbook_downloader_no_parsing_from_rfc(self):
        auth = HttpAuth("user", "pass", "token")
        self.reqeust.url = "blabla/lie.yaml"
        dic = dict([('content-disposition', 'lie.yaml')])
        self.reqeust.headers = dic
        self.reqeust.iter_content.return_value = ''
        self.http_request_serivce.get_response = Mock(return_value=self.reqeust)
        self.http_request_serivce.get_response_with_headers = Mock(return_value=self.reqeust)
        self.playbook_downloader._is_response_valid = Mock(return_value=True)
        
        file_name = self.playbook_downloader.get("", auth, self.logger, Mock(), True)

        self.assertEqual(file_name, "lie.yaml")
    
    def test_playbook_downloader_with_one_yaml_only_credentials(self):
        auth = HttpAuth("user", "pass", None)        
        self.reqeust.url = "blabla/lie.yaml"
        dic = dict([('content-disposition', 'lie.yaml')])
        self.reqeust.headers = dic
        self.reqeust.iter_content.return_value = 'hello'
        self.http_request_serivce.get_response = Mock(return_value=self.reqeust)
        self.http_request_serivce.get_response_with_headers = Mock(return_value=self.reqeust)
        self.playbook_downloader._is_response_valid = Mock(side_effect=self.mock_response_valid_for_credentials)

        file_name = self.playbook_downloader.get("", auth, self.logger, Mock(), True)

        self.assertEqual(file_name, "lie.yaml")

    def test_playbook_downloader_with_one_yaml_only_token(self):
            auth = HttpAuth(None, None, "Token")        
            self.reqeust.url = "blabla/lie.yaml"
            dic = dict([('content-disposition', 'lie.yaml')])
            self.reqeust.headers = dic
            self.reqeust.iter_content.return_value = 'hello'
            self.http_request_serivce.get_response = Mock(return_value=self.reqeust)
            self.http_request_serivce.get_response_with_headers = Mock(return_value=self.reqeust)
            self.playbook_downloader._is_response_valid = Mock(side_effect=self.mock_response_valid_for_not_public)

            file_name = self.playbook_downloader.get("", auth, self.logger, Mock(), True)

            self.assertEqual(file_name, "lie.yaml")
    
    def test_playbook_downloader_with_one_yaml_only_token_with_auth_private_token(self):
            auth = HttpAuth(None, None, "Token")        
            self.reqeust.url = "blabla/lie.yaml"
            dic = dict([('content-disposition', 'lie.yaml'), ('Private-Token', 'Token')])
            self.reqeust.headers = dic
            self.reqeust.iter_content.return_value = 'hello'
            self.http_request_serivce.get_response = Mock(return_value=self.reqeust)
            self.http_request_serivce.get_response_with_headers = Mock(return_value=self.reqeust)
            self.playbook_downloader._is_response_valid = Mock(side_effect=self.mock_response_valid_for_private_token)

            file_name = self.playbook_downloader.get("", auth, self.logger, Mock(), True)

            self.assertEqual(file_name, "lie.yaml")
    
    def test_playbook_downloader_fails_on_public_and_no_credentials(self):
        auth = None
        self.reqeust.url = "blabla/lie.zip"
        dic = dict([('content-disposition', 'lie.zip')])
        self.reqeust.headers = dic
        self.reqeust.iter_content.return_value = ''
        self.http_request_serivce.get_response = Mock(return_value=self.reqeust)
        self.http_request_serivce.get_response_with_headers = Mock(return_value=self.reqeust)
        self.playbook_downloader._is_response_valid = Mock(return_value=False)

        with self.assertRaises(Exception) as e:
            self.playbook_downloader.get("", auth, self.logger, Mock(), True)

        self.assertEqual(str(e.exception),"Please make sure the URL is valid, and the credentials are correct and necessary.")


    # helpers method to mock the request according the request in order to test the right flow for Token\Cred
    def mock_response_valid_for_not_public(self, logger, response, request_method):
        return request_method != "public"
            
    def mock_response_valid_for_credentials(self, logger, response, request_method):
        return request_method == "username\password"

    def mock_response_valid_for_private_token(self, logger, response, request_method):
        return 'Private-Token' in response.headers