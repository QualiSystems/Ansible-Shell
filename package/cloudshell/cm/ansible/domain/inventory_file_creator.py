from collections import OrderedDict
from file_system_service import FileSystemService


class InventoryFileCreator(object):
    def __init__(self, file_system, file_path):
        """
        :param FileSystemService file_system:
        :param str root_folder:
        """
        self.file_system = file_system
        self.file_path = file_path  # os.path.join(root_folder, 'hosts')

    def __enter__(self):
        """
        :param FileSystemService file_system:
        """
        self.inventory_file = InventoryFile()
        return self.inventory_file

    def __exit__(self, type, value, traceback):
        with self.file_system.create_file(self.file_path) as file_stream:
            file_stream.writelines(self.inventory_file.to_file_content())


class InventoryFile(object):
    ANSIBLE_USER = 'ansible_user'
    ANSIBLE_PASSWORD = 'ansible_ssh_pass'
    ANSIBLE_CONNECTION = 'ansible_connection'
    ANSIBLE_CONNECTION_FILE = 'ansible_ssh_private_key_file'

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

    def add_host(self, host_name, set_default_group=False):
        """
        Add host to inventory.
        :param str host_name: The host name/ip to add.
        :param bool set_default_group: If set to True, this host will be added to group 'all'
        """
        if len([h for h in self.hosts if h.name == host_name]) > 0:
            raise ValueError('Failed to add host \'%s\'. Host with the same name already exists.' % host_name)
        host = Host(host_name)
        self.hosts.append(host)
        if set_default_group:
            self.get_or_add_group("all").hosts.append(host)

    def set_host_groups(self, host_name, group_paths):
        """
        Add host to inventory.
        :param str host_name: The host name/ip to add.
        :param list[str] group_paths: The groups of the host.
        """
        host = self.get_host(host_name)
        for group_path in group_paths:
            group = self.get_or_add_group(group_path)
            group.hosts.append(host)

    def set_host_vars(self, host_name, parameters):
        """
        Add host parameters to inventory.
        :param Dictionary paramters:
        """
        host = self.get_host(host_name);
        host.vars.update(parameters)


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

    def get_host(self, host_name):
        """
        :type host_name: str
        :rtype: Host
        """
        host = next((h for h in self.hosts if h.name == host_name), None)
        if host is None:
            raise ValueError('Failed to add vars to host \'%s\' because is not found.' % (host_name))
        return host

    def to_file_content(self):
        """
        Write inventory data to text file.
        :rtype: list[str]
        """
        lines = []
        for group in self.groups:
            if len(group.groups) > 0:
                lines.append('\n\n[%s:children]' % group.name)
                for child in group.groups:
                    lines.append('\n' + child.name)
            if len(group.hosts) > 0:
                lines.append('\n\n[%s]' % group.name)
                for host in group.hosts:
                    lines.append('\n' + host.name)
        for host in self.hosts:
            if len(host.vars) > 0:
                lines.append('\n\n[%s:vars]' % host.name)
                for key, value in host.vars.iteritems():
                    lines.append('\n' + str(key) + '=' + str(value))
        if len(lines) > 0:
            lines[0] = lines[0].strip('\n')
        return lines


class Host(object):
    def __init__(self, name):
        self.name = name
        self.vars = OrderedDict()


class Group(object):
    def __init__(self, name):
        self.name = name
        self.groups = []
        self.hosts = []