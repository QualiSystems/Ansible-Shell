from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext


class CloudShellSessionProvider(object):
    def get(self, command_context):
        return CloudShellSessionContext(command_context)
