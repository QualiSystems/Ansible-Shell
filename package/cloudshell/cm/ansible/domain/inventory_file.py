import os
from collections import OrderedDict
from .file_system_service import FileSystemService


class InventoryFile(object):
    def __init__(self, file_system, file_path, logger):
        """
        :type file_system: FileSystemService
        :type file_path: str
        :type logger: Logger
        """
        self.file_system = file_system
        self.file_path = file_path
        self.logger = logger
        self.groups = []
        self.hosts = []

    def __enter__(self):
        self.logger.info('Creating \'%s\' inventory file ...' % self.file_path)
        return self

    def __exit__(self, type, value, traceback):
        with self.file_system.create_file(self.file_path) as file_stream:
            lines = []
            for group in self.groups:
                if len(group.groups) > 0:
                    lines.append('')
                    lines.append('[%s:children]' % group.name)
                    for child in group.groups:
                        lines.append(child.name)
                if len(group.hosts) > 0:
                    lines.append('')
                    lines.append('[%s]' % group.name)
                    for host in group.hosts:
                        lines.append(host.name)
            if len(lines) > 0 and lines[0] == '':
                del lines[0]
            file_stream.write(os.linesep.join(lines).encode('utf-8'))
            self.logger.debug(os.linesep.join(lines))
        self.logger.info('Done (%s groups, with %s hosts).'%(str(len(self.groups)), str(len(self.hosts))))

    def add_host_and_groups(self, host_name, group_paths = None):
        """
        Add host to inventory.
        :param str host_name: The host name/ip to add.
        :param list[str] group_paths: The groups of the host (If empty, this host will be added to group 'all').
        """
        if len([h for h in self.hosts if h.name == host_name]) > 0:
            raise ValueError('Failed to add host \'%s\'. Host with the same name already exists.' % host_name)
        if not group_paths or len(group_paths) == 0:
            group_paths = ['all']
        host = Host(host_name)
        self.hosts.append(host)
        for group_path in group_paths:
            group = self.get_or_add_group(group_path)
            group.hosts.append(host)

    def get_or_add_group(self, group_path):
        """
        :type group_path: str
        :rtype: Group
        """
        groups = self.groups
        for part in group_path.split('/'):
            group = next((g for g in groups if g.name == part), None)
            if group is None:
                group = Group(part)
                groups.append(group)
                if groups != self.groups:
                    self.groups.append(group)
            groups = group.groups
        return group


class Host(object):
    def __init__(self, name):
        self.name = name


class Group(object):
    def __init__(self, name):
        self.name = name
        self.groups = []
        self.hosts = []