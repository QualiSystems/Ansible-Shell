from unittest import TestCase
from mock import Mock

from cloudshell.cm.ansible.domain.playbook_downloader import PlaybookDownloader, HttpAuth
from cloudshell.tests.mocks.file_system_service_mock import FileSystemServiceMock

class TestPlaybookDownloader(TestCase):

    def setUp(self):
        self.zip_service = Mock()
        self.http_request_serivce = Mock()
        self.file_system = FileSystemServiceMock()
        self.playbook_downloader = PlaybookDownloader(self.file_system, self.zip_service, self.http_request_serivce)

    def test_playbook_downloader_with_one_yaml(self):

        auth = HttpAuth("user","pass")
        self.zip_service.extract_all = lambda: self.file_system.create_file("lie.yaml")
        logger = Mock()
        request = Mock()
        request.url = "blabla/lie.yaml"
        request.headers = dict(('content-disposition','lie.yaml'))
        self.http_request_serivce.get_request.return_value=request
        self.playbook_downloader.get("",auth, logger)



