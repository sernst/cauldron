import os

import cauldron
from cauldron.cli import sync
from cauldron.test import support
from cauldron.test.support.flask_scaffolds import FlaskResultsTest


class TestSyncFile(FlaskResultsTest):
    """ """

    def test_no_args(self):
        """ should error without arguments """

        opened = self.post('/sync-file')
        self.assertEqual(opened.flask.status_code, 200)

        response = opened.response
        self.assert_has_error_code(response, 'INVALID_ARGS')

    def test_missing_relative_path(self):
        """ should error without relative_path argument """

        opened = self.post('/sync-file', {'chunk': 'abc'})

        response = opened.response
        self.assert_has_error_code(response, 'INVALID_ARGS')

    def test_missing_chunk(self):
        """ should error without source directory argument """

        opened = self.post('/sync-file', {'relative_path': 'abc'})

        response = opened.response
        self.assert_has_error_code(response, 'INVALID_ARGS')

    def test_no_project(self):
        """ should error without source directory argument """

        opened = self.post('/sync-file', {
            'relative_path': 'abc',
            'chunk': 'abcdefg'
        })

        response = opened.response
        self.assert_has_error_code(response, 'NO_OPEN_PROJECT')

    def test_valid(self):
        """ should synchronize file remotely """

        support.create_project(self, 'peter')
        project = cauldron.project.get_internal_project()

        response = support.run_remote_command(
            'open "{}"'.format(project.source_directory)
        )
        self.assert_no_errors(response)
        project = cauldron.project.get_internal_project()

        posted = self.post('/sync-file', {
            'relative_path': 'test.md',
            'chunk': sync.io.pack_chunk(b'abcdefg')
        })
        self.assert_no_errors(posted.response)

        written_path = os.path.join(project.source_directory, 'test.md')
        self.assertTrue(os.path.exists(written_path))

        support.run_remote_command('close')

    def test_valid_shared(self):
        """Should synchronize file remotely to shared library location."""
        support.create_project(self, 'peter-2')
        project = cauldron.project.get_internal_project()

        response = support.run_remote_command(
            'open "{}" --forget'.format(project.source_directory)
        )
        self.assert_no_errors(response)
        project = cauldron.project.get_internal_project()

        posted = self.post('/sync-file', {
            'relative_path': 'library/test.md',
            'chunk': sync.io.pack_chunk(b'abcdefg'),
            'location': 'shared'
        })
        self.assert_no_errors(posted.response)

        written_path = os.path.join(
            project.source_directory,
            '..',
            '__cauldron_shared_libs',
            'library',
            'test.md'
        )
        self.assertTrue(os.path.exists(written_path))

        support.run_remote_command('close')
