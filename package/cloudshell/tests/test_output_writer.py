from unittest import TestCase
from cloudshell.cm.ansible.domain.ansible_command_executor import OutputWriter, ReservationOutputWriter
from mock import Mock


class TestOutputWriter(TestCase):

    def test_contains_abstract_write_method(self):
        output_writer = OutputWriter()
        with self.assertRaises(NotImplementedError):
            output_writer.write('msg')


class TestReservationOutputWriter(TestCase):

    def test_writes_to_reservation_output(self):
        session = Mock()
        context = Mock()
        output_writer = ReservationOutputWriter(session, context)
        output_writer.write('msg')

        self.assertTrue(session.WriteMessageToReservationOutput.called_with('msg'))
