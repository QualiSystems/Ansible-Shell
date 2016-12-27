import zipfile

class ZipService(object):

    def extract_all(self, zip_file_name, path=None):
        try:
            zip = zipfile.ZipFile(zip_file_name, 'r')
            zip.extractall(path=path)
            return zip.infolist()
        finally:
            if zip:
                zip.close()