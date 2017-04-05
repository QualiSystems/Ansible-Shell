class AnsibleConnectionHelper(object):
    WIN_RM_SECURED_PORT = '5986'
    WIN_RM_PORT = '5985'
    CONNECTION_METHOD_WIN_RM = 'winrm'
    CONNECTION_METHOD_SSH = 'ssh'
    SSH_PORT = '22'

    def __init__(self):
        pass

    def get_ansible_port(self, host):
        ansible_port = None
        if host.connection_method == self.CONNECTION_METHOD_WIN_RM:
            if host.connection_secured:
                ansible_port = self.WIN_RM_SECURED_PORT
            else:
                ansible_port = self.WIN_RM_PORT
        if host.connection_method == self.CONNECTION_METHOD_SSH:
            ansible_port = self.SSH_PORT
        return ansible_port
