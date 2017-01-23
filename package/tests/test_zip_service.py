from unittest import TestCase
from zipfile import ZipFile

from io import BytesIO
from mock import patch, Mock

from cloudshell.cm.ansible.domain.zip_service import ZipService
from tests.helpers import Any


class TestZipService(TestCase):
    def setUp(self):
        self.zip_file = ZipFile(BytesIO(), 'w')
        self.zip_file.extractall = Mock()
        self.zip_file.extract = Mock()
        self.zip_patcher = patch('cloudshell.cm.ansible.domain.zip_service.ZipFile')
        self.zip_patcher.start().return_value = self.zip_file
        self.zip_service = ZipService()

    def tearDown(self):
        self.zip_patcher.stop()

    def test_regulsr_zip(self):
        self.zip_file.writestr('playbook.yml', 'some yml code')
        self.zip_file.writestr('Roles/', 'some yml code')
        self.zip_file.writestr('Roles/a.yml', 'some yml code')

        self.zip_service.extract_all('')

        self.zip_file.extractall.assert_called_once()

    def test_inner_folder_zip(self):
        self.zip_file.writestr('myzip/', '')
        self.zip_file.writestr('myzip/playbook.yml', 'some yml code')
        self.zip_file.writestr('myzip/Roles/', '')
        self.zip_file.writestr('myzip/Roles/a.yml', 'some yml code')

        self.zip_service.extract_all('')

        self.assertEqual(self.zip_file.extract.call_count, 2)
        self.zip_file.extract.assert_any_call(Any(lambda x: x.filename == 'playbook.yml'))
        self.zip_file.extract.assert_any_call(Any(lambda x: x.filename == 'Roles/a.yml'))

