from cauldron.test import support
from cauldron.test.support import flask_scaffolds


class TestSyncTouch(flask_scaffolds.FlaskResultsTest):
    """ """

    def test_no_project(self):
        """ should fail if no project is open """

        touch_response = self.get('/sync-touch')
        self.assertEqual(touch_response.flask.status_code, 200)

        response = touch_response.response
        self.assert_has_error_code(response, 'NO_PROJECT')

    def test_valid(self):
        """ should refresh the project """

        support.create_project(self, 'hammer')

        touched = self.get('/sync-touch')
        self.assertEqual(touched.flask.status_code, 200)

        response = touched.response
        self.assertEqual(len(response.errors), 0)
