import subprocess
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.cm.ansible.domain.output.unixToHtmlConverter import UnixToHtmlColorConverter
from cloudshell.shell.core.context import ResourceCommandContext

class AnsibleCommandExecutor(object):
    def __init__(self, output_parser, output_writer):
        """
        :type output_parser: AnsiblePlaybookParser
        :type output_writer: OutputWriter
        """
        self.output_parser = output_parser
        self.output_writer = output_writer

    def execute_playbook(self, playbook_file, inventory_file, args = None):
        """
        :type playbook_file: str
        :type inventory_file: str
        :type args: list[str]
        :return:
        """
        max_chunk_read = 512
        shellCommand = self._createShellCommand(playbook_file, inventory_file, args)
        process = subprocess.Popen(shellCommand, shell=True, stdout=subprocess.PIPE)
        output=''
        while True:
            pOut = process.stdout.read(max_chunk_read)
            if process.poll() is not None:
               break
            html_converted = UnixToHtmlColorConverter(pOut).convert()
            self.output_writer.write(html_converted)
            output += pOut
        return self.output_parser.parse(output)

    def _createShellCommand(self, playbook_file, inventory_file, args):
        command = "ansible"

        if playbook_file:
            command += "-playbook " + playbook_file
        if inventory_file:
            command += " -i " + inventory_file
        if args:
            command += " " + args
        command += " -v"
        return command


class OutputWriter(object):
    def write(self, msg):
        """
        :type msg: str
        """
        raise NotImplementedError()


class ReservationOutputWriter(object):
    def __init__(self, session, command_context):
        """
        :type session: CloudShellAPISession
        :type command_context: ResourceCommandContext
        """
        self.session = session
        self.resevation_id = command_context.reservation.reservation_id

    def write(self, msg):
        self.session.WriteMessageToReservationOutput(self.resevation_id, msg)