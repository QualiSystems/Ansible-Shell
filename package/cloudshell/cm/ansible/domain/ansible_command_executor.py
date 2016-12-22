import subprocess
import time
import os
from logging import Logger
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.cm.ansible.domain.output.unixToHtmlConverter import UnixToHtmlColorConverter
from cloudshell.cm.ansible.domain.file_system_service import FileSystemService
from cloudshell.shell.core.context import ResourceCommandContext


class AnsibleCommandExecutor(object):
    def __init__(self, output_parser, filesystem_service):
        """
        :type output_parser: AnsiblePlaybookParser
        :type filesystem_service: FileSystemService
        """
        self.output_parser = output_parser
        self.filesystem_service = filesystem_service

    def execute_playbook(self, playbook_file, inventory_file, args, output_writer, logger):
        """
        :type playbook_file: str
        :type inventory_file: str
        :type args: list[str]
        :type logger: Logger
        :type output_writer: OutputWriter
        :return:
        """
        max_chunk_read = 512
        shellCommand = self._createShellCommand(playbook_file, inventory_file, args)

        logger.info('Running cmd \'%s\' ...' % shellCommand)
        start_time = time.time()
        process = subprocess.Popen(shellCommand, shell=True, stdout=subprocess.PIPE)
        output = ''
        while True:
            pOut = process.stdout.read(max_chunk_read)
            if process.poll() is not None:
                break
            html_converted = UnixToHtmlColorConverter().convert(pOut)
            output_writer.write(html_converted)

        elapsed = time.time() - start_time
        line_count = len(output.split(os.linesep))
        logger.info('Done (after \'%s\' sec, with %s lines of output).' % (elapsed, line_count))
        logger.debug(output)

        return self.output_parser.parse(output,playbook_file, self.filesystem_service)

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


class ReservationOutputWriter(OutputWriter):
    def __init__(self, session, command_context):
        """
        :type session: CloudShellAPISession
        :type command_context: ResourceCommandContext
        """
        self.session = session
        self.resevation_id = command_context.reservation.reservation_id

    def write(self, msg):
        self.session.WriteMessageToReservationOutput(self.resevation_id, msg)
