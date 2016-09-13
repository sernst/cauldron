import json

from cauldron.cli import server
from cauldron.test.support import scaffolds


class TestServer(scaffolds.ResultsTest):
    """

    """

    def setUp(self):
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
