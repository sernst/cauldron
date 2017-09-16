import typing
from collections import namedtuple
from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron.cli.server import run as server_runner
from cauldron.environ.response import Response
from cauldron.test.support.messages import Message
from cauldron.test.support import flask_scaffolds

FakeThread = namedtuple('FakeThread_NT', ['is_alive', 'uid'])


class TestServerRunStatus(flask_scaffolds.FlaskResultsTest):
    """ """

    def setUp(self):
        super(TestServerRunStatus, self).setUp()
        self.active_responses = {}  # type: typing.Dict[str, Response]

    def activate_execution(
            self,
            uid: str,
            is_alive: bool = True
    ) -> Response:
        """
        Adds a fake running command execution to the run status list for use
        in testing
        """

        r = Response(identifier=uid)

        def is_thread_alive():
            return is_alive

        r.thread = MagicMock()
        r.thread.uid = uid
        r.thread.is_alive = is_thread_alive
        r.thread.is_running = is_alive
        r.thread.logs = []

        self.deactivate_execution(uid)
        self.active_responses[uid] = r
        server_runner.active_execution_responses[uid] = r
        return r

    def deactivate_execution(self, uid: str) -> Response:
        """
        Removes a fake running command execution from the run status list for
        tearing down a test
        """

        response = server_runner.active_execution_responses.get(uid)
        if response:
            del server_runner.active_execution_responses[uid]

        if response and response == self.active_responses.get(uid):
            del self.active_responses[uid]

        return response

    def test_no_uid(self):
        """ should do nothing if the run uid is unknown """

        run_status = self.get('/run-status/test-1')
        self.assertEqual(run_status.flask.status_code, 200)

        response = run_status.response
        self.assertFalse(response.failed)
        self.assertEqual(response.data['run_status'], 'unknown')

    @patch('cauldron.cli.server.run.get_running_step_changes')
    def test_failed_step_changes(self, get_running_step_changes):
        """ should fail if unable to get changes for the running step """

        get_running_step_changes.side_effect = ValueError('Fake Error')

        active_response = self.activate_execution('failed-step-changes')

        run_status = self.get('/run-status/{}'.format(
            active_response.identifier
        ))
        self.assertEqual(run_status.flask.status_code, 200)

        response = run_status.response
        self.assertFalse(
            response.failed,
            Message('Failed Response', response=response)
        )
        self.assertEqual(response.data['run_status'], 'running')
        self.assertIsNone(response.data['step_changes'])

        self.deactivate_execution(active_response.identifier)

    @patch('cauldron.cli.server.run.get_running_step_changes')
    def test_no_step_changes(self, get_running_step_changes):
        """ should succeed even without any changes for the running step """

        get_running_step_changes.return_value = None
        active_response = self.activate_execution('no-step-changes')

        run_status = self.get('/run-status/{}'.format(
            active_response.identifier
        ))
        self.assertEqual(run_status.flask.status_code, 200)

        response = run_status.response
        self.assertFalse(response.failed)
        self.assertEqual(response.data['run_status'], 'running')
        self.assertIsNone(response.data['step_changes'])

        self.deactivate_execution(active_response.identifier)

    def test_not_running(self):
        """ should succeed even if the step is no longer running """

        active_response = self.activate_execution('no-step-running', False)

        run_status = self.get('/run-status/{}'.format(
            active_response.identifier
        ))
        self.assertEqual(run_status.flask.status_code, 200)

        response = run_status.response
        self.assertFalse(
            response.failed,
            Message('Response Failed', response=response)
        )
        self.assertEqual(response.data['run_status'], 'complete')

        self.assertNotIn(
            active_response.identifier,
            server_runner.active_execution_responses
        )

        self.deactivate_execution(active_response.identifier)

    @patch('cauldron.cli.server.run.get_server_data')
    def test_error(self, get_server_data):
        """ should succeed even if the step is no longer running """

        get_server_data.side_effect = ValueError('Fake Error')

        run_status = self.get('/run-status/test-error')
        self.assertEqual(run_status.flask.status_code, 200)

        response = run_status.response
        self.assertTrue(response.failed)
        self.assert_has_error_code(response, 'COMMAND_RUN_STATUS_FAILURE')
