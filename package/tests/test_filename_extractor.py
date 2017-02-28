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


    def test_filename_from_header_artifactory(self):
        filename = "  my_file.yml  "
        header = {'x-artifactory-filename': filename}
        self.response.headers = header
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename.strip(), extracted_filename)

    def test_filename_from_url(self):
        filename = "  my_file.zip  "
        header = {}
        self.response.headers = header
        self.response.url = "http://www.template.myurl/a/b/c/" + filename
        extracted_filename = self.filename_extractor.get_filename(self.response)
        self.assertEqual(filename.strip(), extracted_filename)

    def test_unsupported_playbook_file(self):
        filename = "  my_file.exe  "
        header = {}
        self.response.headers = header
        self.response.url = "http://www.template.myurl/a/b/c/" + filename
        with self.assertRaises(Exception) as unsupportedExc:
            self.filename_extractor.get_filename(self.response)
        self.assertEqual(unsupportedExc.exception.message,"playbook file of supported types: '.yml', '.yaml', '.zip' was not found")

