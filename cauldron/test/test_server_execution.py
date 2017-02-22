import json
from collections import namedtuple
from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron import cli
from cauldron.environ.response import Response
from cauldron.cli import server
from cauldron.cli.server import run as server_run
from cauldron.test.support import scaffolds
from cauldron.test import support


class TestServerExecution(scaffolds.ResultsTest):
    """ """

    def setUp(self):
        super(TestServerExecution, self).setUp()
        self.app = server.server_run.APPLICATION.test_client()

    def test_execute_sync(self):
        """ should execute command synchronously """

        response = self.app.post(
            '/command-sync',
            data=json.dumps(dict(
                command='open',
                args=''
            )),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

    def test_execute_get(self):
        """ should execute using get passed data """

        response = self.app.get('/command-sync?&command=open')
        self.assertEqual(response.status_code, 200)

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
            res = self.app.get('/command-sync?&command=open')
            self.assertEqual(execute.call_count, 1)

        self.assertEqual(res.status_code, 200)
        self.assertGreater(thread.join.call_count, 0)
        self.assertGreater(thread.is_alive.call_count, 0)

        r = Response.deserialize(self.read_flask_response(res))
        self.assertFalse(r.failed)

    def test_shutdown_not_running(self):
        """ should abort shutdown of non-running server """

        response = self.app.get('/shutdown')
        data = self.read_flask_response(response)
        r = Response.deserialize(data)

        self.assert_has_error_code(r, 'NOT_RUNNING_ERROR')

    @patch('cauldron.cli.commander.execute')
    def test_execute_failure(self, execute: MagicMock):
        """ should fail when execution fails """

        execute.side_effect = RuntimeError('FAKE ERROR')
        response = self.app.get('/command-sync?&command=open&args=+')
        self.assertEqual(response.status_code, 200)
        data = self.read_flask_response(response)
        r = Response.deserialize(data)
        self.assert_has_error_code(r, 'KERNEL_EXECUTION_FAILURE')

    def test_shutdown(self):
        """ should abort the running server """

        shutdown_func = MagicMock()
        response = self.app.get(
            '/shutdown',
            environ_base={'werkzeug.server.shutdown': shutdown_func}
        )

        data = self.read_flask_response(response)
        r = Response.deserialize(data)

        shutdown_func.assert_called_once_with()
        self.assertFalse(r.failed)

    def test_shutdown_failed(self):
        """ should abort the running server """

        shutdown_func = MagicMock()
        shutdown_func.side_effect = RuntimeError('FAKE ERROR')

        response = self.app.get(
            '/shutdown',
            environ_base={'werkzeug.server.shutdown': shutdown_func}
        )

        data = self.read_flask_response(response)
        r = Response.deserialize(data)

        shutdown_func.assert_called_once_with()
        self.assert_has_error_code(r, 'SHUTDOWN_ERROR')
