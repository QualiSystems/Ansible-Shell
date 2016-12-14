import random
import string
from StringIO import StringIO


class FileSystemServiceMock(object):

    def __init__(self):
        self.folders = []
        self.files = []

    def create_temp_folder(self):
        path = 'temp\\' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.folders.append(path)
        return self.path

    def delete_temp_folder(self, folder):
        self.folders.remove(folder)

    def create_file(self, path):
        file = FileMock(path)
        self.files.append(file)

    def open_file(self, path):
        for f in self.files:
            if f.path == path:
                io = StringIO(f.data)
                oldclose = io.close
                def newclose():
                    f.data = io.getvalue()
                    oldclose()
                io.close = newclose
                return io
        raise ValueError("file '%s' could not be found."%path)

    def read_all_lines(self, path):
        f = self.open_file(path)
        lines = f.getvalue()
        f.close()
        return lines

class FileMock(object):
    def __init__(self, path):
        self.path = path
        self.data = ''
