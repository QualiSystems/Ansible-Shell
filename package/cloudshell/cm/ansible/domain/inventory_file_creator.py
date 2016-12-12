import os
from file_system_service import FileSystemService


class InventoryFileCreator(object):
    def __init__(self, file_system, root_folder):
        """
        :param FileSystemServicefile_system:
        :param str root_folder:
        """
        self.file_system = file_system
        self.file_path = os.path.join(root_folder, 'hosts')
        #self.file = file_system.createFile(file_path)

    def __enter__(self):
        """
        :param FileSystemService file_system:
        """
        self.inventory_file = InventoryFile()
        return self.inventory_file

    def __exit__(self, type, value, traceback):
        file_stream = self.file_system.createFile(self.file_path)
        self.inventory_file.write_to_file(file_stream)
        file_stream.flush()
        file_stream.close()


class InventoryFile(object):
    # def __str__(self):
    #     return self.name + ' Groups:' + ','.join((g.name for g in self.groups), []) + ' Hosts:' + ','.join(
    #         (h.name for h in self.hosts), [])

    def __init__(self):
        self.groups = []
        self.hosts = []

    def add_groups(self, group_paths):
        """
        Add groups hierarchy to inventory.
        :param list[str] group_paths: Array of groups as strings (example: ['servers/web', 'servers/db']
        """
        if group_paths is None or len(group_paths) == 0:
            return

        for group_path in group_paths:
            groups = self.groups
            for part in group_path.split('/'):
                child = next((g for g in groups if g.name == part), None)
                if child is None:
                    child = Group(part)
                    groups.append(child)
                    if groups != self.groups:
                        self.groups.append(child)
                groups = child.groups

    def add_host(self, host_name, group_path):
        """
        Add host to inventory.
        :param str host: The host name/ip to add.
        :param str group_path: The group of the host (optional).
        """
        groups = self.groups
        host = Host(host_name)
        if group_path is not None:
            for part in group_path.split('/'):
                group = next((g for g in groups if g.name == part), None)
                if group is None:
                    raise ValueError(
                        'Failed to add host \'%s\' to group \'%s\' because is not found.' % (host, group_path))
            group.hosts.append(host)
        if next((h for h in self.hosts if h.name == host_name), None) is None:
            self.hosts.append(host)

    def add_vars(self, host_name, parameters):
        """
        Add host parameters to inventory.
        :param Dictionary paramters:
        """
        host = next((h for h in self.hosts if h.name == host_name), None)
        if host is None:
            raise ValueError('Failed to add vars to host \'%s\' because is not found.' % (host_name))
        host.vars.update(parameters)

    def write_to_file(self, file):
        """
        Write inventory data to text file.
        :param file file: The target file.
        :return:
        """
        lines = []
        for group in self.groups:
            if len(group.groups) > 0:
                lines.append('\n[%s:children]'%group.name)
                for child in group.groups:
                    lines.append(child.name)
            if len(group.hosts) > 0:
                lines.append('\n[%s]' % group.name)
                for host in group.hosts:
                    lines.append(host.name)
        for host in self.hosts:
            if len(host.vars) > 0:
                lines.append('\n[%s:vars]' % host.name)
                for key, value in host.vars.iteritems():
                    lines.append(str(key) + '= ' + str(value))
        lines = [line+'\n' for line in lines]
        file.writelines(lines)


class Host(object):
    def __init__(self, name):
        self.name = name
        self.vars = {}


class Group(object):
    def __init__(self, name):
        self.name = name
        self.groups = []
        self.hosts = []


# with InventoryFileCreator(FileSystemService(), "c:\\") as i:
#     i.add_groups(["servers/web/windows", "servers/DB"])
#     i.add_host("x.x.x.x", "servers/web")
#     i.add_vars("x.x.x.x", {'a': 1, 'b': 2})
#     i.add_vars("x.x.x.x", {'c': 11, 'd': 22})
# print 'ds'