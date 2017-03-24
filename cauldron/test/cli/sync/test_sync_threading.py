from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron import environ
from cauldron.cli.sync import threads
from cauldron.test.support import scaffolds


class TestSyncThreading(scaffolds.ResultsTest):
    """ Tests for the cauldron.cli.sync.sync_comm module """

    @patch('cauldron.cli.sync.comm.send_request')
    def test_remote_command(self, send_request: MagicMock):
        """ should execute the command and finish the thread """

        response = environ.Response().update(
            run_status='complete'
        )
        send_request.return_value = response

        thread = threads.send_remote_command('fake_command_name')
        thread.join()

        self.assertEqual(thread.responses[0], response)

    @patch('cauldron.cli.sync.comm.send_request')
    def test_remote_command_error(self, send_request: MagicMock):
        """ should error while trying to send request """

        send_request.side_effect = ValueError('Fake Error')

        thread = threads.send_remote_command('fake_command_name')
        thread.join()

        response = thread.responses[0]
        self.assert_has_error_code(response, 'COMM_EXECUTION_ERROR')

    @patch('cauldron.cli.sync.comm.send_request')
    def test_long_remote_command(self, send_request: MagicMock):
        """ should successfully handle running longer commands """

        running_response = environ.Response().update(run_status='running')
        done_response = environ.Response().update(run_status='complete')

        send_request.return_value = running_response
        thread = threads.send_remote_command('fake_command_name')
        thread.join(1)
        send_request.return_value = done_response
        thread.join()

        self.assertGreater(len(thread.responses), 1)
        last_response = thread.responses[-1]
        self.assertEqual(last_response.data['run_status'], 'complete')
        first_response = thread.responses[0]
        self.assertEqual(first_response.data['run_status'], 'running')
