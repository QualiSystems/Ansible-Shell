from unittest import TestCase
from cloudshell.cm.ansible.domain.temp_folder_scope import TempFolderScope
from .mocks.file_system_service_mock import FileSystemServiceMock
from mock import Mock


class TestTempFolderScope(TestCase):
    def setUp(self):
        self.file_system = FileSystemServiceMock()

    def test_create_and_delete_temp_folder(self):
        with TempFolderScope(self.file_system, Mock()) as f:
            self.assertIn(f, self.file_system.folders)
        self.assertEqual([], self.file_system.folders)

    def test_set_and_restore_the_working_directory(self):
        dir = self.file_system.get_working_dir()
        with TempFolderScope(self.file_system, Mock()) as f:
            self.assertEqual(f, self.file_system.get_working_dir())
        self.assertEqual(dir, self.file_system.get_working_dir())