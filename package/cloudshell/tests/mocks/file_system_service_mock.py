import random
import string
import os


class FileSystemServiceMock(object):

    def __init__(self):
        self.folders = []
        self.files = []
        self.working_dir = '\\'

    def create_temp_folder(self):
        path = 'temp\\' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.folders.append(path)
        return path

    def create_folder(self, folder):
        self.folders.append(folder)

    def exists(self, path):
        return (path in self.folders) or len([f for f in self.files if f.path == path]) > 0

    def delete_temp_folder(self, folder):
        self.folders.remove(folder)

    def create_file(self, path):
        f = FileMock(path)
        self.files.append(f)
        return f

    def get_working_dir(self):
        return self.working_dir

    def set_working_dir(self, path):
        self.working_dir = path

    def read_all_lines(self, path):
        f = next((f for f in self.files if f.path == path), None)
        if not f:
            raise ValueError("file '%s' could not be found."%path)
        return f.data


class FileMock(object):
    def __init__(self, path):
        self.path = path
        self.data = ''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def writelines(self, lines):
        self.data += os.linesep.join(lines)