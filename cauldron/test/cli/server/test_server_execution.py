from collections import namedtuple
from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.environ.response import Response
from cauldron.test.support import flask_scaffolds


class TestServerExecution(flask_scaffolds.FlaskResultsTest):
    """ """

    def test_execute_sync(self):
        """ should execute command synchronously """

        opened = self.post('/command-sync', {'command': 'open', 'args': ''})
        self.assertEqual(opened.flask.status_code, 200)

    def test_execute_get(self):
        """ should execute using get passed data """

        opened = self.get('/command-sync?&command=open')
        self.assertEqual(opened.flask.status_code, 200)

    def test_execute_wait(self):
        """ should wait for execution to complete when synchronous """

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
        """ should abort shutdown of non-running server """

        shutdown = self.get('/shutdown')
        self.assert_has_error_code(shutdown.response, 'NOT_RUNNING_ERROR')

    @patch('cauldron.cli.commander.execute')
    def test_execute_failure(self, execute: MagicMock):
        """ should fail when execution fails """

        execute.side_effect = RuntimeError('FAKE ERROR')
        opened = self.get('/command-sync?&command=open&args=+')
        self.assertEqual(opened.flask.status_code, 200)
        self.assert_has_error_code(opened.response, 'KERNEL_EXECUTION_FAILURE')

    def test_shutdown(self):
        """ should abort the running server """

        shutdown_func = MagicMock()
        shutdown = self.get(
            '/shutdown',
            environ_base={'werkzeug.server.shutdown': shutdown_func}
        )
        shutdown_func.assert_called_once_with()
        self.assertFalse(shutdown.response.failed)

    def test_shutdown_failed(self):
        """ should abort the running server """

        shutdown_func = MagicMock()
        shutdown_func.side_effect = RuntimeError('FAKE ERROR')
        shutdown = self.get(
            '/shutdown',
            environ_base={'werkzeug.server.shutdown': shutdown_func}
        )
        shutdown_func.assert_called_once_with()

        self.assert_has_error_code(shutdown.response, 'SHUTDOWN_ERROR')
