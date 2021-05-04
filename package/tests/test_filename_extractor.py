from unittest import TestCase

from mock import Mock

from cloudshell.cm.ansible.domain.filename_extractor import FilenameExtractor


class TestFilenameExtractor(TestCase):
    def setUp(self):
        self.filename_extractor = FilenameExtractor()
        self.response = Mock()


    def test_filename_from_header_RFC_content_disposition_(self):
        filename = "  my_file.yaml  "
        header = {'content-disposition': 'attachment ;  filename=' + filename}
        self.response.headers = header
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename.strip(),extracted_filename)

    def test_filename_from_header_RFC_content_disposition_no_spcaces(self):
        filename = "my_file.yaml"
        header = {'content-disposition': 'attachment ;  filename=' + filename}
        self.response.headers = header
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename,extracted_filename)

    def test_filename_from_header_artifactory(self):
        filename = "  my_file.yml  "
        header = {'x-artifactory-filename': filename}
        self.response.headers = header
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename.strip(), extracted_filename)

    def test_filename_from_header_artifactory_no_spaces(self):
        filename = "my_file.yml"
        header = {'x-artifactory-filename': filename}
        self.response.headers = header
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename, extracted_filename)

    def test_filename_from_url(self):
        filename = "  my_file.zip  "
        header = {}
        self.response.headers = header
        self.response.url = "http://www.template.myurl/a/b/c/" + filename
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename.strip(), extracted_filename)

    def test_filename_from_url_from_bitbucket(self):
        filename = "simple.yml"
        header = {}
        self.response.headers = header
        self.response.url = "http://192.168.30.96:7990/rest/api/1.0/projects/TEST/repos/test/raw/simple.yml"
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename, extracted_filename)

    def test_filename_from_url_no_spaces(self):
        filename = "my_file.zip"
        header = {}
        self.response.headers = header
        self.response.url = "http://www.template.myurl/a/b/c/" + filename
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename, extracted_filename)

    def test_filename_from_url_gitlab_structure(self):
        filename = "  my_file.zip  "
        header = {}
        self.response.headers = header
        self.response.url = "http://www.template.myurl/a/b/my_file%2Ezip/raw?ref=master"
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename.strip(), extracted_filename)

    def test_filename_from_url_gitlab_structure_speciel_chars(self):
        filename = "a-b@c=d.yml"
        header = {}
        self.response.headers = header
        self.response.url = "https://gitlab.com/api/v4/projects/25386685/repository/files/a-b%40c%3Dd.yml/raw?ref=master"
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename, extracted_filename)

    def test_unsupported_playbook_file(self):
        filename = "  my_file.exe  "
        header = {}
        self.response.headers = header
        self.response.url = "http://www.template.myurl/a/b/c/" + filename
        with self.assertRaises(Exception) as unsupportedExc:
            self.filename_extractor.get_filename(self.response)
        self.assertEqual(str(unsupportedExc.exception),"playbook file of supported types: '.yml', '.yaml', '.zip' was not found")

    def test_unsupported_playbook_file_no_spaces(self):
        filename = "my_file.exe"
        header = {}
        self.response.headers = header
        self.response.url = "http://www.template.myurl/a/b/c/" + filename
        with self.assertRaises(Exception) as unsupportedExc:
            self.filename_extractor.get_filename(self.response)
        self.assertEqual(str(unsupportedExc.exception),"playbook file of supported types: '.yml', '.yaml', '.zip' was not found")