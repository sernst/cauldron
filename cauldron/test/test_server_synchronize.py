import json

from cauldron.cli import server
from cauldron.test import support
from cauldron.test.support import scaffolds
from flask import Response as FlaskResponse


class TestServerDisplay(scaffolds.ResultsTest):
    """

    """

    def setUp(self):
        super(TestServerDisplay, self).setUp()
        self.app = server.server_run.APPLICATION.test_client()

    def test_sync_status_no_project(self):
        """
        """

        response = self.app.get(
            '/sync-status',
            content_type='application/json'
        )  # type: FlaskResponse
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf8'))

        self.assertTrue('errors' in data)
        error = data['errors'][0]

        self.assertEqual(error['code'], 'NO_PROJECT')

    def test_sync_status_valid(self):
        """
        """

        support.create_project(self, 'angelica')

        response = self.app.get(
            '/sync-status',
            content_type='application/json'
        )  # type: FlaskResponse
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf8'))

        self.assertTrue('errors' in data)
        self.assertEqual(len(data['errors']), 0)

        status = data.get('data', {}).get('status')
        self.assertIsNotNone(status)
        self.assertTrue('project' in status)

        support.run_command('close')
