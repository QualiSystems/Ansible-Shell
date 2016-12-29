from unittest import TestCase
from mock import Mock, MagicMock, patch
from subprocess import PIPE
from cloudshell.cm.ansible.domain.ansible_command_executor import AnsibleCommandExecutor
from helpers import mock_enter_exit_self


class TestAnsibleCommandExecutor(TestCase):

    def setUp(self):
        self.process_mock = Mock()
        self.stdout_mock = mock_enter_exit_self()
        self.convert_mock = Mock()
        self.sleep_mock = Mock()
        self.output_parser_mock = Mock()
        self.output_writer_mock = Mock()

        self.popen_patcher = patch('cloudshell.cm.ansible.domain.ansible_command_executor.Popen')
        self.stdout_patcher = patch('cloudshell.cm.ansible.domain.ansible_command_executor.StdoutAccumulator')
        self.convert_patcher = patch('cloudshell.cm.ansible.domain.ansible_command_executor.UnixToHtmlColorConverter.convert')
        self.sleep_patcher = patch('cloudshell.cm.ansible.domain.ansible_command_executor.time.sleep')

        self.popen_patcher.start().return_value = self.process_mock
        self.stdout_patcher.start().return_value = self.stdout_mock
        self.convert_mock = self.convert_patcher.start()
        self.sleep_mock = self.sleep_patcher.start()

        self.convert_mock.side_effect = (lambda x: x)
        self.sleep_mock.side_effect = (lambda x: 0)

        self.executor = AnsibleCommandExecutor(self.output_parser_mock)

    def tearDown(self):
        self.popen_patcher.stop()
        self.stdout_mock.stop()
        self.convert_mock.stop()
        self.sleep_mock.stop()

    def test_run_prcess_with_corrent_command_line(self):
        with patch('cloudshell.cm.ansible.domain.ansible_command_executor.Popen') as popen:
            self.executor.execute_playbook('playbook1','inventory1','-arg1 -args2',Mock(),Mock())

            popen.assert_called_once_with('ansible-playbook playbook1 -i inventory1 -arg1 -args2',shell=True,stdout=PIPE)

    def test_sample_in_interval_of_2_seconds(self):
        self.stdout_mock.read_all_txt.side_effect = ['1','2']
        self.process_mock.poll = MagicMock(side_effect=[None, '0'])

        self.executor.execute_playbook('p', 'i', '', self.output_writer_mock, Mock())

        self.sleep_mock.assert_any_call(2)

    def test_all_results_are_parsed(self):
        self.stdout_mock.read_all_txt.side_effect = ['1', '2']
        self.process_mock.poll = MagicMock(side_effect=[None, '0'])

        self.executor.execute_playbook('p', 'i', '', self.output_writer_mock, Mock())

        self.output_parser_mock.parse.assert_called_once_with('12', 'p')

    def test_parsed_results_are_returned(self):
        self.output_parser_mock.parse = Mock(return_value='parsedresults')

        results = self.executor.execute_playbook('p', 'i', '', self.output_writer_mock, Mock())

        self.assertEqual('parsedresults', results)

    def test_every_output_bulk_is_written_to_outputwriter(self):
        self.stdout_mock.read_all_txt.side_effect = ['123', '456', '789']
        self.process_mock.poll = MagicMock(side_effect=[None, None, '0'])

        self.executor.execute_playbook('p', 'i', '', self.output_writer_mock, Mock())

        self.output_writer_mock.write.assert_any_call('123')
        self.output_writer_mock.write.assert_any_call('456')
        self.output_writer_mock.write.assert_any_call('789')

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