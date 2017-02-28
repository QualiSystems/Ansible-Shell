import os
from zipfile import ZipFile, ZipInfo

class ZipService(object):

    def extract_all(self, zip_file_name):
        zip = None
        try:
            zip = ZipFile(zip_file_name, 'r')
            if self._contain_sinlge_folder(zip):
                for file_info in self._get_files(zip):
                    file_info.filename = self._remove_first_folder(file_info.filename)
                    zip.extract(file_info)
            else:
                zip.extractall()
            return [f.filename for f in self._get_files(zip)]
        finally:
            if zip:
                zip.close()

    @staticmethod
    def _remove_first_folder(filename):
        '''
        :type filename: filename
        :rtype: filename
        '''
        return '/'.join(filename.split('/')[1:])

    @staticmethod
    def _get_files(zip):
        '''
        :type zip: ZipFile
        :rtype: list[ZipInfo]
        '''
        return [f for f in zip.infolist() if not ZipService._is_folder(f)]

    @staticmethod
    def _is_folder(zipped_item):
        '''
        :type zipped_item: ZipInfo
        :rtype: bool
        '''
        return zipped_item.filename[-1] == '/'

    @staticmethod
    def _contain_sinlge_folder(zip):
        '''
        :type zip: ZipFile
        :rtype: bool
        '''
        files = zip.namelist();
        folder = next((f for f in files if f[-1] == '/'), None)
        return folder and all(f.startswith(folder) for f in files)