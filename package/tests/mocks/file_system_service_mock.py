import random
import string
import os
import tempfile

from cloudshell.cm.ansible.domain.file_system_service import FileSystemService


class FileSystemServiceMock(FileSystemService):

    def __init__(self):
        self.folders = []
        self.files = []
        self.deleted_files = []
        self.working_dir = os.sep

    def create_temp_folder(self):
        path = os.path.join(tempfile.gettempdir(), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
        self.folders.append(path)
        return path

    def create_folder(self, folder):
        self.folders.append(folder)

    def exists(self, path):
        return (path in self.folders) or len([f for f in self.files if f.path == path]) > 0

    def delete_temp_folder(self, folder):
        for file in [f for f in self.files if f.full_path.startswith(folder) or f.path.startswith(folder)]:
            self.files.remove(file)
            self.deleted_files.append(file)
        self.folders.remove(folder)

    def create_file(self, path):
        f = FileMock(path, os.path.join(self.working_dir, path))
        self.files.append(f)
        return f

    def get_working_dir(self):
        return self.working_dir

    def set_working_dir(self, path):
        self.working_dir = path

    def read_all_lines(self, *path):
        f = next((f for f in self.files if f.path == os.path.join(*path) or f.full_path == os.path.join(*path)), None)
        if not f:
            raise ValueError("File '%s' could not be found."%path)
        return f.data

    def read_deleted_file(self, *path):
        f = next((f for f in self.deleted_files if f.path == os.path.join(*path) or f.full_path == os.path.join(*path)), None)
        if not f:
            raise ValueError("Deleted file '%s' could not be found." % path)
        return f.data

    def get_entries(self, path):
        file_entries = []
        for file in self.files:
            file_entries.append(file.path)
        return self.folders + file_entries

class FileMock(object):
    def __init__(self, path, full_path):
        self.path = path
        self.data = ''
        self.full_path = full_path


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def writelines(self, lines):
        self.data += ''.join(lines)

    def write(self, line):
        self.data = line

    def tell(self):
        return len(self.data)
