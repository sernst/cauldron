import typing
from collections import namedtuple
from unittest.mock import patch

from flask import Response as FlaskResponse

from cauldron.cli import server
from cauldron.cli.server import run as server_runner
from cauldron.environ.response import Response
from cauldron.test.support import scaffolds

FakeThread = namedtuple('FakeThread_NT', ['is_alive', 'uid'])


class TestServerRunStatus(scaffolds.ResultsTest):
    """ """

    def setUp(self):
        super(TestServerRunStatus, self).setUp()
        self.app = server.server_run.APPLICATION.test_client()
        self.active_responses = {} # type: typing.Dict[str, Response]

    def activate_execution(
            self,
            uid: str,
            is_alive: bool = True
    ) -> Response:
        r = Response(identifier=uid)

        def is_thread_alive():
            return is_alive

        r.thread = FakeThread(
            is_alive=is_thread_alive,
            uid=uid
        )

        self.deactivate_execution(uid)
        self.active_responses[uid] = r
        server_runner.active_execution_responses[uid] = r
        return r

    def deactivate_execution(self, uid: str) -> Response:
        response = server_runner.active_execution_responses.get(uid)
        if response:
            del server_runner.active_execution_responses[uid]

        if response and response == self.active_responses.get(uid):
            del self.active_responses[uid]

        return response

    def test_no_uid(self):
        """ """

        response = self.app.get('/run-status/test-1')  # type: FlaskResponse
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertTrue(payload['success'])
        self.assertEqual(payload['data']['run_status'], 'unknown')

    @patch('cauldron.cli.server.run.get_running_step_changes')
    def test_failed_step_changes(self, get_running_step_changes):
        """ should fail if unable to get changes for the running step """

        get_running_step_changes.side_effect = ValueError('Fake Error')

        active_response = self.activate_execution('failed-step-changes')

        response = self.app.get('/run-status/{}'.format(
            active_response.identifier
        ))  # type: FlaskResponse
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertTrue(payload['success'])
        self.assertEqual(payload['data']['run_status'], 'running')
        self.assertIsNone(payload['data']['step_changes'])

        self.deactivate_execution(active_response.identifier)

    @patch('cauldron.cli.server.run.get_running_step_changes')
    def test_no_step_changes(self, get_running_step_changes):
        """ should succeed even without any changes for the running step """

        get_running_step_changes.return_value = None
        active_response = self.activate_execution('no-step-changes')

        response = self.app.get('/run-status/{}'.format(
            active_response.identifier
        ))  # type: FlaskResponse
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertTrue(payload['success'])
        self.assertEqual(payload['data']['run_status'], 'running')
        self.assertIsNone(payload['data']['step_changes'])

        self.deactivate_execution(active_response.identifier)

    def test_not_running(self):
        """ should succeed even if the step is no longer running """

        active_response = self.activate_execution('no-step-running', False)

        response = self.app.get('/run-status/{}'.format(
            active_response.identifier
        ))  # type: FlaskResponse
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertTrue(payload['success'])
        self.assertEqual(payload['data']['run_status'], 'complete')

        self.assertNotIn(
            active_response.identifier,
            server_runner.active_execution_responses
        )

        self.deactivate_execution(active_response.identifier)

    @patch('cauldron.cli.server.run.get_server_data')
    def test_error(self, get_server_data):
        """ should succeed even if the step is no longer running """

        get_server_data.side_effect = ValueError('Fake Error')

        response = self.app.get('/run-status/test-error')  # type: FlaskResponse
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertFalse(payload['success'])
        self.assertEqual(
            payload['errors'][0]['code'],
            'COMMAND_RUN_STATUS_FAILURE'
        )
