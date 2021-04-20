import os
from logging import Logger
from .file_system_service import FileSystemService


class HostVarsFile(object):
    FOLDER_NAME = 'host_vars'
    ANSIBLE_USER = 'ansible_user'
    ANSIBLE_PASSWORD = 'ansible_ssh_pass'
    ANSIBLE_CONNECTION = 'ansible_connection'
    ANSIBLE_PORT = 'ansible_port'
    ANSIBLE_CONNECTION_FILE = 'ansible_ssh_private_key_file'
    ANSIBLE_WINRM_CERT_VALIDATION = 'ansible_winrm_server_cert_validation'

    def __init__(self, file_system, host_name, logger):
        """
        :type file_system: FileSystemService
        :type host_name: str
        :type logger: Logger
        """
        self.file_system = file_system
        self.logger = logger
        self.file_path = os.path.join(HostVarsFile.FOLDER_NAME, host_name)
        self.vars = {}

    def __enter__(self):
        self.logger.info('Creating \'%s\' vars file ...' % self.file_path)
        return self

    def __exit__(self, type, value, traceback):
        if not self.file_system.exists(HostVarsFile.FOLDER_NAME):
            self.file_system.create_folder(HostVarsFile.FOLDER_NAME)
        with self.file_system.create_file(self.file_path) as file_stream:
            lines = ['---']
            for key, value in sorted(self.vars.items()):
                lines.append(str(key) + ': "' + str(value) + '"')
            file_stream.write(bytes(os.linesep.join(lines), 'utf-8'))
            self.logger.debug(os.linesep.join(lines))
        self.logger.info('Done.')

    def add_vars(self, vars):
        self.vars.update(vars)

    def add_connection_type(self, connection_type):
        self.vars[HostVarsFile.ANSIBLE_CONNECTION] = connection_type

    def add_conn_file(self, file_path):
        self.vars[HostVarsFile.ANSIBLE_CONNECTION_FILE] = file_path

    def add_username(self, username):
        self.vars[HostVarsFile.ANSIBLE_USER] = username

    def add_password(self, password):
        self.vars[HostVarsFile.ANSIBLE_PASSWORD] = password

    def add_port(self, port):
        if HostVarsFile.ANSIBLE_PORT not in list(self.vars.keys()) or \
                (self.vars[HostVarsFile.ANSIBLE_PORT] == '') or \
                        self.vars[HostVarsFile.ANSIBLE_PORT] is None:
            self.vars[HostVarsFile.ANSIBLE_PORT] = port

    def add_ignore_winrm_cert_validation(self):
        self.vars[HostVarsFile.ANSIBLE_WINRM_CERT_VALIDATION] = 'ignore'
