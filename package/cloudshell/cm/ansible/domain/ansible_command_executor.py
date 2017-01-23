from subprocess import Popen, PIPE
import time
import os
from logging import Logger
from cloudshell.api.cloudshell_api import CloudShellAPISession

from cloudshell.cm.ansible.domain.cancellation_sampler import CancellationSampler
from cloudshell.cm.ansible.domain.output.unixToHtmlConverter import UnixToHtmlColorConverter
from cloudshell.cm.ansible.domain.output.ansible_result import AnsibleResult
from cloudshell.shell.core.context import ResourceCommandContext
from cloudshell.cm.ansible.domain.stdout_accumulator import StdoutAccumulator, StderrAccumulator


class AnsibleCommandExecutor(object):
    def __init__(self):
        pass

    def execute_playbook(self, playbook_file, inventory_file, args, output_writer, logger, cancel_sampler):
        """
        :type playbook_file: str
        :type inventory_file: str
        :type args: list[str]
        :type logger: Logger
        :type output_writer: OutputWriter
        :type cancel_sampler: CancellationSampler
        :rtype: AnsibleResult
        """
        shell_command = self._create_shell_command(playbook_file, inventory_file, args)

        logger.info('Running cmd \'%s\' ...' % shell_command)
        start_time = time.time()
        process = Popen(shell_command, shell=True, stdout=PIPE, stderr=PIPE)
        all_txt_err = ''
        all_txt_out = ''

        with StdoutAccumulator(process.stdout) as stdout:
            with StderrAccumulator(process.stderr) as stderr:
                while True:
                    txt_lines = []
                    txt_err = stderr.read_all_txt()
                    txt_out = stdout.read_all_txt()
                    if txt_err:
                        all_txt_err += txt_err
                        txt_lines.append(txt_err)
                    if txt_out:
                        all_txt_out += txt_out
                        txt_lines.append(txt_out)
                    if txt_lines:
                        txt_html = UnixToHtmlColorConverter().convert(os.linesep.join(txt_lines))
                        try:
                            output_writer.write(txt_html)
                        except Exception as e:
                            output_writer.write('failed to write text of %s characters (%s)'%(len(txt_html),e))
                            logger.debug("failed to write:" + txt_html)
                            logger.debug("failed to write.")
                    if process.poll() is not None:
                        break
                    if cancel_sampler.is_cancelled():
                        process.kill()
                        cancel_sampler.throw()
                    time.sleep(2)

        elapsed = time.time() - start_time
        err_line_count = len(all_txt_err.split(os.linesep))
        out_line_count = len(all_txt_out.split(os.linesep))
        logger.info('Done (after \'%s\' sec, with %s lines of output, with %s lines of error).' % (elapsed, out_line_count, err_line_count))
        logger.debug('Err: '+all_txt_err)
        logger.debug('Out: '+all_txt_out)
        logger.debug('Code: '+str(process.returncode))

        return all_txt_out, all_txt_err


    def _create_shell_command(self, playbook_file, inventory_file, args):
        command = "ansible"

        if playbook_file:
            command += "-playbook " + playbook_file
        if inventory_file:
            command += " -i " + inventory_file
        if args:
            command += " " + args
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
