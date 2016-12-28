from unittest import TestCase
from mock import Mock, MagicMock, patch
from subprocess import Popen, PIPE
from cloudshell.cm.ansible.domain.ansible_command_executor import AnsibleCommandExecutor
from helpers import mock_enter_exit, mock_enter_exit_self

class TestAnsibleCommandExecutor(TestCase):
    def setUp(self):
        self.output_parser = Mock()
        self.executor = AnsibleCommandExecutor(self.output_parser)

    def test_run_prcess_with_corrent_command_line(self):
        with patch('cloudshell.cm.ansible.domain.ansible_command_executor.Popen') as popen:
            self.executor.execute_playbook('playbook1','inventory1','-arg1 -args2',Mock(),Mock())

            popen.assert_called_once_with('ansible-playbook playbook1 -i inventory1 -arg1 -args2',shell=True,stdout=PIPE)

    def test_reads_all_output(self):
        self.output_parser.parse = Mock(return_value='parsedresults')
        with patch('cloudshell.cm.ansible.domain.ansible_command_executor.Popen') as popen:
            process_mock = Mock()
            popen.return_value = process_mock
            with patch('cloudshell.cm.ansible.domain.ansible_command_executor.StdoutAccumulator') as accumulator:
                stdout_mock = mock_enter_exit_self()
                accumulator.return_value = stdout_mock
                with patch('cloudshell.cm.ansible.domain.ansible_command_executor.UnixToHtmlColorConverter.convert') as convert_mock:
                    with patch('cloudshell.cm.ansible.domain.ansible_command_executor.time.sleep') as sleep_mock:
                        stdout_mock.read_all_txt.side_effect = ['123','456','789']
                        process_mock.poll = MagicMock(side_effect=[None, None, '0'])
                        convert_mock.side_effect = (lambda x: x)
                        sleep_mock.side_effect = (lambda x: 0)
                        output_writer_mock = Mock()

                        results = self.executor.execute_playbook('p', 'i', '', output_writer_mock, Mock())

                        output_writer_mock.write.assert_any_call('123')
                        output_writer_mock.write.assert_any_call('456')
                        output_writer_mock.write.assert_any_call('789')
                        sleep_mock.assert_any_call(2)
                        self.assertEqual('parsedresults',results)
                        self.output_parser.parse.assert_called_once_with('123456789','p')