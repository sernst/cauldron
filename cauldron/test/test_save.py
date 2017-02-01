import os
from unittest.mock import patch

import cauldron
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestSave(scaffolds.ResultsTest):

    def test_fails_no_project(self):
        """ should fail if there is no open project """

        support.run_command('close')

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

        support.run_command('close')

    def test_save_directory_success(self):
        """ should write a cdf file """

        support.create_project(self, 'triceratops')
        path = self.get_temp_path('save-success-1')
        r = support.run_command('save "{}"'.format(path))
        self.assertFalse(r.failed)
        self.assertTrue(os.path.exists(r.data['path']))

        project = cauldron.project.internal_project
        self.assertTrue(r.data['path'].endswith('{}.cdf'.format(project.title)))

        support.run_command('close')

    def test_save_file_no_extension_success(self):
        """ should write a cdf file """

        support.create_project(self, 'tyrannosaurus')
        path = self.get_temp_path('save-success-2', 'project')
        r = support.run_command('save "{}"'.format(path))
        self.assertFalse(r.failed)
        self.assertTrue(os.path.exists(r.data['path']))
        self.trace('PATH:', r.data['path'])
        self.assertTrue(r.data['path'].endswith('project.cdf'))

        support.run_command('close')

    def test_save_file_success(self):
        """ should write a cdf file """

        support.create_project(self, 'apatosaurus')
        path = self.get_temp_path('save-success-3', 'folder', 'project.cdf')
        r = support.run_command('save "{}"'.format(path))
        self.assertFalse(r.failed)
        self.assertTrue(os.path.exists(r.data['path']))
        self.assertTrue(r.data['path'].endswith('project.cdf'))

        support.run_command('close')
