from collections import namedtuple
from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.environ.response import Response
from cauldron.test.support import flask_scaffolds


class TestServerExecution(flask_scaffolds.FlaskResultsTest):
    """..."""

    def test_execute_sync(self):
        """Should execute command synchronously."""
        opened = self.post('/command-sync', {'command': 'open', 'args': ''})
        self.assertEqual(opened.flask.status_code, 200)

    def test_execute_get(self):
        """Should execute using get passed data """
        opened = self.get('/command-sync?&command=open')
        self.assertEqual(opened.flask.status_code, 200)

    def test_execute_wait(self):
        """Should wait for execution to complete when synchronous."""
        FakeThread = namedtuple('FakeThread_NT', ['uid', 'join', 'is_alive'])
        thread = FakeThread(
            uid='FAKE-UID',
            join=MagicMock(),
            is_alive=MagicMock(return_value=False)
        )

        def execute_replacement(name, args, response: Response):
            response.thread = thread

        patch_target = 'cauldron.cli.commander.execute'
        with patch(patch_target, wraps=execute_replacement) as execute:
            opened = self.get('/command-sync?&command=open')
            self.assertEqual(execute.call_count, 1)

        self.assertEqual(opened.flask.status_code, 200)
        self.assertGreater(thread.join.call_count, 0)
        self.assertGreater(thread.is_alive.call_count, 0)
        self.assertFalse(opened.response.failed)

    def test_shutdown_not_running(self):
        """Should abort shutdown of non-running server."""
        shutdown = self.get('/shutdown')
        self.assert_has_error_code(shutdown.response, 'NOT_RUNNING_ERROR')

    @patch('cauldron.cli.commander.execute')
    def test_execute_failure(self, execute: MagicMock):
        """Should fail when execution fails."""
        execute.side_effect = RuntimeError('FAKE ERROR')
        opened = self.get('/command-sync?&command=open&args=+')
        self.assertEqual(opened.flask.status_code, 200)
        self.assert_has_error_code(opened.response, 'KERNEL_EXECUTION_FAILURE')

    def test_shutdown(self):
        """Should abort the running server."""
        shutdown_func = MagicMock()
        shutdown = self.get(
            '/shutdown',
            environ_base={'werkzeug.server.shutdown': shutdown_func}
        )
        shutdown_func.assert_called_once_with()
        self.assertFalse(shutdown.response.failed)

    def test_shutdown_failed(self):
        """Should abort the running server."""
        shutdown_func = MagicMock()
        shutdown_func.side_effect = RuntimeError('FAKE ERROR')
        shutdown = self.get(
            '/shutdown',
            environ_base={'werkzeug.server.shutdown': shutdown_func}
        )
        shutdown_func.assert_called_once_with()

        self.assert_has_error_code(shutdown.response, 'SHUTDOWN_ERROR')

    @patch('cauldron.cli.server.routes.execution.server_runner')
    def test_abort_not_a_response(
            self,
            server_runner: MagicMock,
    ):
        """Should ignore non-response entries during abort."""
        server_runner.active_execution_responses = {'foo': None}
        self.get('/abort')

    @patch('cauldron.cli.server.routes.execution.server_runner')
    def test_abort_no_thread(
            self,
            server_runner: MagicMock,
    ):
        """Should work when no thread for active response."""
        active_response = MagicMock()
        active_response.thread = None
        server_runner.active_execution_responses = {'foo': active_response}
        self.get('/abort')

    @patch('cauldron.cli.server.routes.execution.server_runner')
    def test_abort_cannot_stop(
            self,
            server_runner: MagicMock,
    ):
        """Should succeed even when thread could not be stopped."""
        active_response = MagicMock()
        active_response.thread.abort_running.side_effect = ValueError
        server_runner.active_execution_responses = {'foo': active_response}
        self.get('/abort')
