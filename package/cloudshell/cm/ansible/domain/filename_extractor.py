import urllib
import re

from cloudshell.cm.ansible.domain.exceptions import AnsibleException


class FilenameExtractor(object):
    def __init__(self):
        self._filename_pattern = "(?P<filename>\s*[\w,\s-]+\.(yaml|yml|zip)\s*)"
        self.filename_patterns = {
            "content-disposition": "\s*((?i)inline|attachment|extension-token)\s*;\s*filename=" +
                                   self._filename_pattern,
            "x-artifactory-filename": self._filename_pattern,
            "X-Gitlab-File-Name": self._filename_pattern
        }

    def get_filename(self, response):
        file_name = None
        for header_value, pattern in self.filename_patterns.iteritems():
            matching = re.match(pattern, response.headers.get(header_value, ""))
            if matching:
                file_name = matching.group('filename')
                if file_name:
                    return file_name.strip()

        # Fallback, couldn't find file name from header, get it from url

        # === raw url search ===
        # ex. - https://raw.githubusercontent.com/QualiSystemsLab/master/my_playbook.yml
        if not file_name:
            file_name_from_url = urllib.unquote(response.url[response.url.rfind('/') + 1:])
            matching = re.match(self._filename_pattern, file_name_from_url)
            if matching:
                file_name = matching.group('filename')
                if file_name:
                    return file_name.strip()

        # === Gitlab REST url search ===
        # ex. - 'http://192.168.85.62/api/v4/projects/2/repository/files/my_playbook.yml/raw?ref=master'
        url_split = response.url.split("/")
        if url_split >= 2:
            file_name_from_url = url_split[-2]
            matching = re.match(self._filename_pattern, file_name_from_url)
            if matching:
                file_name = matching.group('filename')
                if file_name:
                    return file_name.strip()

        raise AnsibleException("playbook file of supported types: '.yml', '.yaml', '.zip' was not found")

