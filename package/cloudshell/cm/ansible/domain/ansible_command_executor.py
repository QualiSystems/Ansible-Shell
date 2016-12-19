import subprocess
import time
import os
from logging import Logger
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.shell.core.context import ResourceCommandContext

class AnsibleCommandExecutor(object):
    def __init__(self, output_parser, output_writer):
        """
        :type output_parser: AnsiblePlaybookParser
        :type output_writer: OutputWriter
        """
        self.output_parser = output_parser
        self.output_writer = output_writer

    def execute_playbook(self, playbook_file, inventory_file, logger, args = None):
        """
        :type playbook_file: str
        :type inventory_file: str
        :type logger: Logger
        :type args: list[str]
        :return:
        """
        shellCommand = self._createShellCommand(playbook_file, inventory_file, args)

        logger.info('Running cmd \'%s\' ...'%shellCommand)
        start_time = time.time()
        process = subprocess.Popen(shellCommand, shell=True, stdout=subprocess.PIPE)
        output=''
        CUNK_TO_READ = 512

        while True:
            # line = process.stdout.readline()
            # if not line:
            #     break;
            pOut = process.stdout.read(CUNK_TO_READ)
            if process.poll() is not None:
               break
            self.output_writer.write(pOut)
            output += pOut
            #TODO: write to output window. via api command
        # output = subprocess.check_output(shellCommand)
        elapsed = time.time()-start_time
        line_count = len(output.split(os.linesep))
        logger.info('Done (after \'%s\' sec, with %s lines of output).' % (elapsed, line_count))
        logger.debug(output)
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