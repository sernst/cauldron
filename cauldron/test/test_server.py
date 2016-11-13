import json
from unittest import mock

from cauldron import cli
from cauldron.cli import server
from cauldron.cli.server import run as server_run
from cauldron.test.support import scaffolds
from cauldron.test import support


class TestServer(scaffolds.ResultsTest):
    """

    """

    def setUp(self):
        super(TestServer, self).setUp()
        self.app = server.server_run.APPLICATION.test_client()

    def test_execute(self):
        """
        """

        response = self.app.post(
            '/',
            data=json.dumps(dict(
                command='open',
                args=''
            )),
            content_type='application/json'
        )

        self.assertIsNotNone(response)

    def test_execute_invalid_command(self):
        """
        """

        response = self.app.post(
            '/',
            data=json.dumps(dict(
                command='fake-command',
                args=''
            )),
            content_type='application/json'
        )

        self.assertIsNotNone(response)

    def test_execute_fail(self):
        """
        """

        response = self.app.post(
            '/',
            data=json.dumps(dict(
                command='open',
                args=1234
            )),
            content_type='application/json'
        )

        self.assertIsNotNone(response)

    def test_ping(self):
        """

        :return:
        """

        response = self.app.post('/ping')
        self.assertIsNotNone(response)

    def test_status(self):
        """

        :return:
        """

        self.app.post(
            '/',
            data=json.dumps(dict(
                command='open',
                args='@examples:hello_cauldron'
            )),
            content_type='application/json'
        )

        response = self.app.post('/status')
        self.assertIsNotNone(response)

    def test_project(self):
        """

        :return:
        """

        self.app.post(
            '/',
            data=json.dumps(dict(
                command='open',
                args='@examples:hello_cauldron'
            )),
            content_type='application/json'
        )

        response = self.app.post('/project')
        self.assertIsNotNone(response)

    def test_run_status(self):
        """

        :return:
        """

        response = self.app.post(
            '/run-status/fake-uid',
            content_type='application/json'
        )

        self.assertIsNotNone(response)

    def test_abort_invalid(self):
        """

        :return:
        """

        response = self.app.post(
            '/abort/fake-uid',
            content_type='application/json'
        )

        self.assertIsNotNone(response)

    def test_start_server(self):
        """

        :return:
        """

        kwargs = dict(
            port=9999,
            debug=True,
            host='TEST'
        )

        with mock.patch('cauldron.cli.server.run.APPLICATION.run') as func:
            server_run.execute(**kwargs)
            func.assert_called_once_with(**kwargs)

    def test_start_server_version(self):
        """

        :return:
        """

        with mock.patch('cauldron.cli.server.run.APPLICATION.run') as func:
            try:
                server_run.execute(version=True)
            except SystemExit:
                pass
            func.assert_not_called()

    def test_parse(self):
        """

        :return:
        """

        args = server_run.parse(['--port=9999', '--version', '--debug'])
        self.assertTrue(args.get('version'))
        self.assertTrue(args.get('debug'))
        self.assertEqual(args.get('port'), 9999)

    def test_abort_nothing(self):
        response = self.app.get('/abort')
        self.assertIsNotNone(response)

    def test_abort_running(self):
        support.create_project(self, 'walter')
        support.add_step(
            self,
            contents=cli.reformat(
                """
                import time
                time.sleep(10)
                """
            )
        )

        response = self.read_flask_response(self.app.post(
            '/command-async',
            data=json.dumps(dict(
                command='run',
                args=''
            )),
            content_type='application/json'
        ))
        self.assertIsNotNone(response)

        run_uid = response['data']['run_uid']
        self.app.get('/run-status/{}'.format(run_uid))
        response = self.app.get('/abort')
        self.assertIsNotNone(response)

        support.run_command('close')

    def test_long_running_print_buffering(self):
        support.create_project(self, 'walter2')
        support.add_step(
            self,
            contents=cli.reformat(
                """
                import time
                print('Printing to step print buffer...')
                for i in range(100):
                    print(i)
                    time.sleep(0.25)
                """
            )
        )

        response = self.read_flask_response(self.app.post(
            '/command-async',
            data=json.dumps(dict(
                command='run',
                args=''
            )),
            content_type='application/json'
        ))
        run_uid = response['data']['run_uid']
        self.app.get('/run-status/{}'.format(run_uid))
        self.app.get('/abort')

        support.run_command('close')
