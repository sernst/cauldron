from unittest.mock import patch

import cauldron
from cauldron.cli import server
from cauldron.test import support
from cauldron.test.support import scaffolds
from flask import Response as FlaskResponse


class TestServerStatus(scaffolds.ResultsTest):
    """ """

    def setUp(self):
        super(TestServerStatus, self).setUp()
        self.app = server.server_run.APPLICATION.test_client()

    def test_status_no_project(self):
        """
        """

        response = self.app.get('/status')  # type: FlaskResponse
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertTrue(payload['success'])
        self.assertIsNone(payload['data']['project'])

    @patch('cauldron.session.projects.Project.status')
    def test_failed_status(self, project_status):
        """ should fail if unable to test project status """

        support.create_project(self, 'mario')

        project_status.side_effect = ValueError('Fake Error')

        response = self.app.get('/status')  # type: FlaskResponse
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertFalse(payload['success'])
        self.assertEqual(payload['errors'][0]['code'], 'PROJECT_STATUS_ERROR')

        support.run_command('close')

    def test_clean_step_no_project(self):
        """ should fail when no project is open """

        response = self.app.get('/clean-step/fake')  # type: FlaskResponse
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertFalse(payload['success'])
        self.assertEqual(payload['errors'][0]['code'], 'PROJECT_FETCH_ERROR')

    def test_clean_step_no_step(self):
        """ should fail when no such step exists """

        support.create_project(self, 'luigi')

        response = self.app.get('/clean-step/fake')  # type: FlaskResponse
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertFalse(payload['success'])
        self.assertEqual(payload['errors'][0]['code'], 'STEP_FETCH_ERROR')

        support.run_command('close')

    def test_clean_step(self):
        """ should succeed in cleaning step """

        support.create_project(self, 'luigi')
        support.add_step(self)

        step = cauldron.project.internal_project.steps[0]

        response = self.app.get(
            '/clean-step/{}'.format(step.filename)
        )  # type: FlaskResponse
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertTrue(payload['success'])
        self.assertIsNotNone(payload['data']['project'])

        support.run_command('close')

    def test_no_project(self):
        """ """

        response = self.app.get('/project')  # type: FlaskResponse
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertTrue(payload['success'])
        self.assertIsNone(payload['data']['project'])

    @patch('cauldron.session.projects.Project.kernel_serialize')
    def test_project_error(self, kernel_serialize):
        """ """

        kernel_serialize.side_effect = ValueError('Fake Error')

        support.create_project(self, 'toadie')

        response = self.app.get('/project')  # type: FlaskResponse
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        payload = self.read_flask_response(response)
        self.assertFalse(payload['success'])
        self.assertEqual(payload['errors'][0]['code'], 'PROJECT_FETCH_ERROR')
