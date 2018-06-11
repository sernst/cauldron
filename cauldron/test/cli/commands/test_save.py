import os
from unittest.mock import patch
from unittest.mock import MagicMock

import cauldron
from cauldron.cli.commands import save
from cauldron.environ.response import Response
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestSave(scaffolds.ResultsTest):

    def test_fails_no_project(self):
        """ should fail if there is no open project """

        path = self.get_temp_path('save-fail-1')
        r = support.run_command('save "{}"'.format(path))
        self.assertTrue(r.failed)
        self.assertGreater(len(r.errors), 0)
        self.assertEqual(r.errors[0].code, 'NO_PROJECT')

    @patch('cauldron.cli.commands.save.write_file')
    def test_fails_write(self, write_func):
        """ should fail when the write function raises an exception """
        write_func.side_effect = IOError('Write failed')

        support.create_project(self, 'rex')
        path = self.get_temp_path('save-fail-2')
        r = support.run_command('save "{}"'.format(path))
        self.assertTrue(r.failed)
        self.assertGreater(len(r.errors), 0)
        self.assertEqual(r.errors[0].code, 'WRITE_SAVE_ERROR')

    def test_save_directory_success(self):
        """ should write a cauldron file """

        support.create_project(self, 'triceratops')
        path = self.get_temp_path('save-success-1')
        r = support.run_command('save "{}"'.format(path))
        self.assertFalse(r.failed)
        self.assertTrue(os.path.exists(r.data['path']))

        project = cauldron.project.get_internal_project()
        self.assertTrue(
            r.data['path'].endswith('{}.cauldron'.format(project.title))
        )

    def test_save_file_no_extension_success(self):
        """ should write a cauldron file """

        support.create_project(self, 'tyrannosaurus')
        path = self.get_temp_path('save-success-2', 'project')
        r = support.run_command('save "{}"'.format(path))
        self.assertFalse(r.failed)
        self.assertTrue(os.path.exists(r.data['path']))
        self.trace('PATH:', r.data['path'])
        self.assertTrue(r.data['path'].endswith('project.cauldron'))

    def test_save_file_success(self):
        """ should write a cauldron file """

        support.create_project(self, 'apatosaurus')
        path = self.get_temp_path(
            'save-success-3',
            'folder',
            'project.cauldron'
        )
        r = support.run_command('save "{}"'.format(path))
        self.assertFalse(r.failed)
        self.assertTrue(os.path.exists(r.data['path']))
        self.assertTrue(r.data['path'].endswith('project.cauldron'))

    def test_remote_save_no_project(self):
        """ """

        response = support.run_remote_command('save')
        self.assertTrue(response.failed)

    @patch('cauldron.cli.sync.comm.download_file')
    def test_remote_download_error(self, download_file: MagicMock):
        """ """

        download_file.return_value = Response().fail().response

        support.create_project(self, 'apophis')
        project = cauldron.project.get_internal_project()

        support.run_remote_command('open "{}"'.format(project.source_directory))

        response = support.run_remote_command('save')
        self.assertTrue(response.failed)

    @patch('cauldron.cli.sync.comm.download_file')
    def test_remote(self, download_file: MagicMock):
        """ """

        download_file.return_value = Response()

        support.create_project(self, 'apophis')
        project = cauldron.project.get_internal_project()

        support.run_remote_command('open "{}"'.format(project.source_directory))

        response = support.run_remote_command('save')
        self.assert_has_success_code(response, 'DOWNLOAD_SAVED')

    def test_get_default_path_no_project(self):
        """ """

        path = save.get_default_path()
        self.assertTrue(os.path.exists(path))
