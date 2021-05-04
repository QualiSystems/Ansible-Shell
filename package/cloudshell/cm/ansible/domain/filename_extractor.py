import urllib.request, urllib.parse, urllib.error
import re

from cloudshell.cm.ansible.domain.exceptions import AnsibleException


class FilenameExtractor(object):
    def __init__(self):
        self._filename_pattern = r"(?P<filename>\s*([\w,\s-]*|^.*\.?[^/\\&\?]+)\.(yaml|yml|zip)\s*(?=([\?&].*$|$)))"
        self.filename_patterns = {
                "content-disposition": "\s*((?i)inline|attachment|extension-token)\s*;\s*filename=" + self._filename_pattern,
                "x-artifactory-filename": self._filename_pattern
        }

    def get_filename(self,response):
        file_name = None;
        for header_value, pattern in self.filename_patterns.items():
            matching = re.match(pattern, response.headers.get(header_value,""))
            if matching:
                file_name = matching.group('filename')
                break
        #fallback, couldn't find file name from header, get it from url
        if not file_name:
            file_name_from_url = urllib.parse.unquote(response.url[response.url.rfind('/') + 1:])
            matching = re.match(self._filename_pattern, file_name_from_url)
            if matching:
                file_name = matching.group('filename')        
        
        # fallback, couldn't find file name regular URL, check gitlab structure (filename in [-2] position)
        if not file_name:
            file_name_from_url = urllib.parse.unquote(response.url.split('/')[-2])
            matching = re.match(self._filename_pattern, file_name_from_url)
            if matching:
                file_name = matching.group('filename')

        if not file_name:
            raise AnsibleException("playbook file of supported types: '.yml', '.yaml', '.zip' was not found")
        return file_name.strip()

