from unittest.mock import patch

import cauldron
from cauldron.test import support
from cauldron.test.support import flask_scaffolds


class TestServerStatus(flask_scaffolds.FlaskResultsTest):
    """ """

    def test_status_no_project(self):
        """ """

        status = self.get('/status')
        self.assertEqual(status.flask.status_code, 200)

        response = status.response
        self.assertFalse(response.failed)
        self.assertIsNone(response.data['project'])

    @patch('cauldron.session.projects.Project.status')
    def test_failed_status(self, project_status):
        """ should fail if unable to test project status """

        support.create_project(self, 'mario')

        project_status.side_effect = ValueError('Fake Error')

        status = self.get('/status')
        self.assertEqual(status.flask.status_code, 200)

        response = status.response
        self.assertTrue(response.failed)
        self.assert_has_error_code(response, 'PROJECT_STATUS_ERROR')

    def test_clean_step_no_project(self):
        """ should fail when no project is open """

        cleaned = self.get('/clean-step/fake')
        self.assertEqual(cleaned.flask.status_code, 200)

        response = cleaned.response
        self.assertFalse(response.success)
        self.assert_has_error_code(response, 'PROJECT_FETCH_ERROR')

    def test_clean_step_no_step(self):
        """ should fail when no such step exists """

        support.create_project(self, 'luigi')

        cleaned = self.get('/clean-step/fake')
        self.assertEqual(cleaned.flask.status_code, 200)

        response = cleaned.response
        self.assertFalse(response.success)
        self.assert_has_error_code(response, 'STEP_FETCH_ERROR')

    def test_clean_step(self):
        """ should succeed in cleaning step """

        support.create_project(self, 'luigi')
        support.add_step(self)

        step = cauldron.project.get_internal_project().steps[0]

        cleaned = self.get('/clean-step/{}'.format(step.filename))
        self.assertEqual(cleaned.flask.status_code, 200)

        response = cleaned.response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.data['project'])

    def test_no_project(self):
        """ """

        project_status = self.get('/project')
        self.assertIsNotNone(project_status)
        self.assertEqual(project_status.flask.status_code, 200)

        response = project_status.response
        self.assertTrue(response.success)
        self.assertIsNone(response.data['project'])

    def test_project_error(self):
        """ """

        support.create_project(self, 'toadie')

        package = 'cauldron.session.projects.Project.kernel_serialize'
        with patch(package) as func:
            func.side_effect = ValueError('Fake Error')
            project_status = self.get('/project')

        self.assertIsNotNone(project_status)
        self.assertEqual(project_status.flask.status_code, 200)

        response = project_status.response
        self.assertFalse(response.success)
        self.assert_has_error_code(response, 'PROJECT_FETCH_ERROR')
