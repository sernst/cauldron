from cauldron.test import support
from cauldron.test.support import flask_scaffolds


class TestSyncStatus(flask_scaffolds.FlaskResultsTest):
    """ """

    def test_sync_status_no_project(self):
        """ """

        sync_status = self.get('/sync-status')
        self.assertEqual(sync_status.flask.status_code, 200)

        response = sync_status.response
        self.assert_has_error_code(response, 'NO_PROJECT')

    def test_sync_status_valid(self):
        """ """

        support.create_project(self, 'angelica')

        sync_status = self.get('/sync-status')
        self.assertEqual(sync_status.flask.status_code, 200)

        response = sync_status.response
        self.assertEqual(len(response.errors), 0)

        status = response.data.get('status')
        self.assertIsNotNone(status)
        self.assertTrue('project' in status)
