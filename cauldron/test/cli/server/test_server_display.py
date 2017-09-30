from cauldron.test import support
from cauldron.test.support import flask_scaffolds


class TestServerDisplay(flask_scaffolds.FlaskResultsTest):
    """ """

    def test_view_no_project(self):
        """ should fail if no project is open for viewing """

        viewed = self.get('/view/fake-file.html')
        self.assertEqual(viewed.flask.status_code, 204)

    def test_view(self):
        """ should return file data if file exists """

        support.create_project(self, 'renee')

        viewed = self.get('/view/project.html')
        self.assertEqual(viewed.flask.status_code, 200)

    def test_view_no_file(self):
        """ should fail if the file does not exist """

        support.create_project(self, 'reginald')

        viewed = self.get('/view/fake-file.html')
        self.assertEqual(viewed.flask.status_code, 204)
