import rfc6266
import urllib
import re

class FilenameExtractor(object):
    def __init__(self):
        self.filename_pattern = "(?P<filename>\s*[\w,\s-]+\.[A-Za-z]{3}\s*)"
        self.filename_patterns = {
                "content-disposition": "\s*((?i)inline|attachment|extension-token)\s*;\s*filename=" + self.filename_pattern,
                "x-artifactory-filename": self.filename_pattern
        }


    def get_filename(self,response):
        file_name = None;
        for header_value, pattern in self.filename_patterns.iteritems():
            matching = re.match(pattern, response.headers.get(header_value,""))
            if matching:
                file_name = matching.group('filename')
                break
        #fallback, couldn't find file name from header, get it from url
        if not file_name:
            file_name = urllib.unquote(response.url[response.url.rfind('/') + 1:])
        return file_name

