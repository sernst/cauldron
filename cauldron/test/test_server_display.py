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

    def test_view_no_project(self):
        """
        """

        response = self.app.get('/view/fake-file.html')  # type: FlaskResponse
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 204)

    def test_view_no_file(self):
        """
        """

        support.create_project(self, 'renee')

        response = self.app.get('/view/project.html')  # type: FlaskResponse
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        support.run_command('close')

    def test_view(self):
        """
        """

        support.create_project(self, 'reginald')

        response = self.app.get('/view/fake-file.html')  # type: FlaskResponse
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 204)

        support.run_command('close')
