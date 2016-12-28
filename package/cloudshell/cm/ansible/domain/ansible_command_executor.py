from subprocess import Popen, PIPE
import time
import os
from Queue import Queue, Empty
from logging import Logger
from threading import Thread, RLock
from xml.sax.saxutils import escape
from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.cm.ansible.domain.output.unixToHtmlConverter import UnixToHtmlColorConverter
from cloudshell.cm.ansible.domain.file_system_service import FileSystemService
from cloudshell.shell.core.context import ResourceCommandContext


class AnsibleCommandExecutor(object):
    def __init__(self, output_parser):
        """
        :type output_parser: AnsiblePlaybookParser
        """
        self.output_parser = output_parser

    def execute_playbook(self, playbook_file, inventory_file, args, output_writer, logger):
        """
        :type playbook_file: str
        :type inventory_file: str
        :type args: list[str]
        :type logger: Logger
        :type output_writer: OutputWriter
        :return:
        """
        shell_command = self._create_shell_command(playbook_file, inventory_file, args)

        logger.info('Running cmd \'%s\' ...' % shell_command)
        start_time = time.time()
        process = Popen(shell_command, shell=True, stdout=PIPE)
        output = ''

        with StdoutAccumulator(process.stdout) as ac:
            while True:
                txt = ac.read_all_txt()
                if txt:
                    output += txt
                    txt = UnixToHtmlColorConverter().convert(txt)
                    try:
                        output_writer.write(txt)
                    except Exception as e:
                        output_writer.write('failed to write text of %s characters (%s)'%(len(txt),e))
                        logger.debug("failed to write:" + txt)
                        logger.debug("failed to write.")
                if process.poll() is not None:
                    break
                time.sleep(2)

        elapsed = time.time() - start_time
        line_count = len(output.split(os.linesep))
        logger.info('Done (after \'%s\' sec, with %s lines of output).' % (elapsed, line_count))
        logger.debug(output)

        return self.output_parser.parse(output, playbook_file)

    def _create_shell_command(self, playbook_file, inventory_file, args):
        command = "ansible"

        if playbook_file:
            command += "-playbook " + playbook_file
        if inventory_file:
            command += " -i " + inventory_file
        if args:
            command += " " + args
        return command


class StdoutAccumulator(object):
    def __init__(self, stdout):
        self.queue = Queue()
        self.stdout = stdout
        self.thread = Thread(target=self._push_to_queue)
        self.thread.daemon = True
        self.lock = RLock()

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.lock:
            self.stdout.close()
        self.thread.join()

    def _push_to_queue(self):
        is_closed = False
        while not is_closed:
            with self.lock:
                is_closed = self.stdout.closed
                if not is_closed:
                    line = self.stdout.readline()
                    if line:
                        self.queue.put(line)

    def read_all_txt(self):
        try:
            lines = []
            while True:
                lines.append(self.queue.get_nowait())
        except Empty:
            pass
        finally:
            return os.linesep.join(lines)


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
