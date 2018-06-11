import cauldron
from cauldron.test import support
from cauldron.test.support.flask_scaffolds import FlaskResultsTest


class TestSyncCreate(FlaskResultsTest):
    """ """

    def test_no_args(self):
        """ should error without arguments """

        opened = self.post('/sync-create')
        self.assertEqual(opened.flask.status_code, 200)

        response = opened.response
        self.assert_has_error_code(response, 'INVALID_ARGS')

    def test_missing_name(self):
        """ should error without name argument """

        opened = self.post('/sync-create', {'source_directory': 'abc'})

        response = opened.response
        self.assert_has_error_code(response, 'INVALID_ARGS')

    def test_missing_source_directory(self):
        """ should error without source directory argument """

        opened = self.post('/sync-create', {'name': 'abc'})

        response = opened.response
        self.assert_has_error_code(response, 'INVALID_ARGS')

    def test_create(self):
        """ should create project remotely """

        name = 'wyoming'
        source_directory = self.get_temp_path(name)

        created = self.post('/sync-create', dict(
            name=name,
            source_directory=source_directory
        ))
        self.assertEqual(created.flask.status_code, 200)

        response = created.response
        self.assert_has_success_code(response, 'PROJECT_CREATED')

        project = cauldron.project.get_internal_project()
        self.assertEqual(project.remote_source_directory, source_directory)
