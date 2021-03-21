import os
from unittest import TestCase
from mock import Mock, MagicMock, patch
from subprocess import PIPE
from cloudshell.cm.ansible.domain.ansible_command_executor import AnsibleCommandExecutor
from .helpers import mock_enter_exit_self


class TestAnsibleCommandExecutor(TestCase):

    def setUp(self):
        self.process_mock = Mock()
        self.stdout_mock = mock_enter_exit_self()
        self.stderr_mock = mock_enter_exit_self()
        self.convert_mock = Mock()
        self.sleep_mock = Mock()
        self.output_writer_mock = Mock()

        self.popen_patcher = patch('cloudshell.cm.ansible.domain.ansible_command_executor.Popen')
        self.stdout_patcher = patch('cloudshell.cm.ansible.domain.ansible_command_executor.StdoutAccumulator')
        self.stderr_patcher = patch('cloudshell.cm.ansible.domain.ansible_command_executor.StderrAccumulator')
        self.convert_patcher = patch('cloudshell.cm.ansible.domain.ansible_command_executor.UnixToHtmlColorConverter.convert')
        self.sleep_patcher = patch('cloudshell.cm.ansible.domain.ansible_command_executor.time.sleep')

        self.popen_patcher.start().return_value = self.process_mock
        self.stdout_patcher.start().return_value = self.stdout_mock
        self.stderr_patcher.start().return_value = self.stderr_mock
        self.convert_mock = self.convert_patcher.start()
        self.sleep_mock = self.sleep_patcher.start()

        self.convert_mock.side_effect = (lambda x: x)
        self.sleep_mock.side_effect = (lambda x: 0)

        self.executor = AnsibleCommandExecutor()

    def tearDown(self):
        self.popen_patcher.stop()
        self.stdout_patcher.stop()
        self.stderr_patcher.stop()
        self.convert_patcher.stop()
        self.sleep_patcher.stop()

    def test_run_prcess_with_corrent_command_line(self):
        with patch('cloudshell.cm.ansible.domain.ansible_command_executor.Popen') as popen:
            self.executor.execute_playbook('playbook1','inventory1','-arg1 -args2',Mock(),Mock(), Mock())

            popen.assert_called_once_with('ansible-playbook playbook1 -i inventory1 -arg1 -args2',shell=True,stdout=PIPE,stderr=PIPE)

    def test_sample_in_interval_of_2_seconds(self):
        self.stdout_mock.read_all_txt.side_effect = ['1','2']
        self.stderr_mock.read_all_txt.return_value = ''
        self.process_mock.poll = MagicMock(side_effect=[None, '0'])

        self.executor.execute_playbook('p', 'i', '', self.output_writer_mock, Mock(), Mock())

        self.sleep_mock.assert_any_call(2)

    def test_result_contains_output_and_error_texts(self):
        self.stdout_mock.read_all_txt.side_effect = ['1', '2']
        self.stderr_mock.read_all_txt.side_effect = ['3', '4']
        self.process_mock.poll = MagicMock(side_effect=[None, '0'])

        output,error = self.executor.execute_playbook('p', 'i', '', self.output_writer_mock, Mock(), Mock())

        self.assertEqual('12', output)
        self.assertEqual('34', error)

    def test_every_output_bulk_is_written_to_outputwriter(self):
        self.stdout_mock.read_all_txt.side_effect = ['123', '456', '789']
        self.stderr_mock.read_all_txt.side_effect = ['a', 'b', '']
        self.stderr_mock.read_all_txt.return_value = ''
        self.process_mock.poll = MagicMock(side_effect=[None, None, '0'])

        self.executor.execute_playbook('p', 'i', '', self.output_writer_mock, Mock(), Mock())

        self.output_writer_mock.write.assert_any_call('a'+os.linesep+'123'+os.linesep+'b'+os.linesep+'456'+os.linesep+'789')

    # def test_reads_all_output(self):
    #     self.output_parser_mock.parse = Mock(return_value='parsedresults')
    #     self.stdout_mock.read_all_txt.side_effect = ['123','456','789']
    #     self.process_mock.poll = MagicMock(side_effect=[None, None, '0'])
    #
    #     results = self.executor.execute_playbook('p', 'i', '', self.output_writer_mock, Mock())
    #
    #     self.output_writer_mock.write.assert_any_call('123')
    #     self.output_writer_mock.write.assert_any_call('456')
    #     self.output_writer_mock.write.assert_any_call('789')
    #     self.sleep_mock.assert_any_call(2)
    #     self.assertEqual('parsedresults',results)
    #     self.output_parser_mock.parse.assert_called_once_with('123456789','p')