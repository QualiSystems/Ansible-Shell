from collections import OrderedDict
from unittest import TestCase
from cloudshell.cm.ansible.domain.inventory_file_creator import InventoryFileCreator
from mocks.file_system_service_mock import FileSystemServiceMock


class TestInventoryFileCreator(TestCase):
    def setUp(self):
        self.file_system = FileSystemServiceMock()

    def test_can_add_groups(self):
        with InventoryFileCreator(self.file_system, 'hosts') as f:
            f.add_groups(['servers/web', 'servers/db/windows', 'servers/db'])

        self.assertEquals('[servers:children]\nweb\ndb\n\n[db:children]\nwindows', self.file_system.read_all_lines('hosts'))

    def test_can_add_hosts(self):
        with InventoryFileCreator(self.file_system, 'hosts') as f:
            f.add_groups(['all'])
            f.add_host('host1', 'all')
            f.add_host('host2', 'all')

        self.assertEquals('[all]\nhost1\nhost2', self.file_system.read_all_lines('hosts'))
        
    def test_can_add_vars(self):
        with InventoryFileCreator(self.file_system, 'hosts') as f:
            f.add_groups(['all'])
            f.add_host('host1', 'all')
            f.add_vars('host1', OrderedDict(sorted({'var1':'aaa', 'var2':'bbb', 'var3':'ccc'}.items())))

        self.assertEquals('[all]\nhost1\n\n[host1:vars]\nvar1=aaa\nvar2=bbb\nvar3=ccc', self.file_system.read_all_lines('hosts'))