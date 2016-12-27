from unittest import TestCase
from mock import Mock

from cloudshell.cm.ansible.domain.playbook_downloader import PlaybookDownloader, HttpAuth
from tests.mocks.file_system_service_mock import FileSystemServiceMock


class TestPlaybookDownloader(TestCase):

    def setUp(self):
        self.zip_service = Mock()
        self.http_request_serivce = Mock()
        self.file_system = FileSystemServiceMock()
        self.playbook_downloader = PlaybookDownloader(self.file_system, self.zip_service, self.http_request_serivce)
        self.logger = Mock()
        self.logger.info = lambda msg: ""
        self.reqeust = Mock()

    def _set_extract_all_zip(self, files_to_create):
        for file_to_create in files_to_create:
            self.file_system.create_file(file_to_create)
        return files_to_create

    def _test_playbook_downloader_zip_file_one_yaml(self):
        self.zip_service.extract_all = lambda zip_file_name: self._set_extract_all_zip(["lie.yaml"])
        auth = HttpAuth("user", "pass")
        self.reqeust.url = "blabla/lie.zip"
        dic = dict([('content-disposition', 'lie.zip')])
        self.reqeust.headers = dic
        self.reqeust.iter_content.return_value = ''
        self.http_request_serivce.get_request.return_value = self.reqeust
        file_name = self.playbook_downloader.get("", auth, self.logger)
        self.assertEquals(file_name, "lie.yaml")

    def _test_playbook_downloader_zip_file_two_yaml_correct(self):
        self.zip_service.extract_all = lambda zip_file_name: self._set_extract_all_zip(["lie.yaml", "site.yaml"])
        auth = HttpAuth("user", "pass")
        self.reqeust.url = "blabla/lie.zip"
        dic = dict([('content-disposition', 'lie.zip')])
        self.reqeust.headers = dic
        self.reqeust.iter_content.return_value = ''
        self.http_request_serivce.get_request.return_value = self.reqeust
        file_name = self.playbook_downloader.get("", auth, self.logger)
        self.assertEquals(file_name, "site.yaml")

    def _test_playbook_downloader_zip_file_two_yaml_incorrect(self):
        self.zip_service.extract_all = lambda zip_file_name: self._set_extract_all_zip(["lie.yaml", "lie2.yaml"])
        auth = HttpAuth("user", "pass")
        self.reqeust.url = "blabla/lie.zip"
        dic = dict([('content-disposition', 'lie.zip')])
        self.reqeust.headers = dic
        self.reqeust.iter_content.return_value = ''
        self.http_request_serivce.get_request.return_value = self.reqeust
        with self.assertRaises(Exception) as e:
            self.playbook_downloader.get("", auth, self.logger)
        self.assertEqual(e.exception.message,"Playbook file name was not found in zip file")

    def test_playbook_downloader_with_one_yaml(self):

        auth = HttpAuth("user","pass")
        self.reqeust.url = "blabla/lie.yaml"
        dic = dict([('content-disposition', 'lie.yaml')])
        self.reqeust.headers =dic
        self.reqeust.iter_content.return_value=''
        self.http_request_serivce.get_request.return_value=self.reqeust
        self.playbook_downloader.get("",auth, self.logger)



