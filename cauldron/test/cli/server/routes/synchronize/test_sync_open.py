import json
import os

import cauldron
from cauldron.test import support
from cauldron.test.support.flask_scaffolds import FlaskResultsTest

EXAMPLE_PROJECTS_DIRECTORY = os.path.realpath(os.path.join(
    os.path.dirname(os.path.realpath(cauldron.__file__)),
    'resources',
    'examples'
))


class TestSyncOpen(FlaskResultsTest):
    """ """

    def test_no_args(self):
        """ should error without arguments """

        opened = self.post('/sync-open')
        self.assertEqual(opened.flask.status_code, 200)

        response = opened.response
        self.assert_has_error_code(response, 'INVALID_ARGS')

    def test_missing_definition(self):
        """ should error without cauldron.json definition argument """

        opened = self.post('/sync-open', {'source_directory': 'abc'})

        response = opened.response
        self.assert_has_error_code(response, 'INVALID_ARGS')

    def test_missing_source_directory(self):
        """ should error without source directory argument """

        opened = self.post('/sync-open', {'definition': 'abc'})

        response = opened.response
        self.assert_has_error_code(response, 'INVALID_ARGS')

    def test_open(self):
        """ should open project remotely """

        source_directory = os.path.join(
            EXAMPLE_PROJECTS_DIRECTORY,
            'hello_text'
        )
        source_path = os.path.join(source_directory, 'cauldron.json')

        with open(source_path, 'r') as f:
            definition = json.load(f)

        opened = self.post('/sync-open', dict(
            definition=definition,
            source_directory=source_directory
        ))

        response = opened.response
        self.assert_has_success_code(response, 'PROJECT_OPENED')

        project = cauldron.project.get_internal_project()
        self.assertEqual(project.remote_source_directory, source_directory)
