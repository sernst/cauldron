from unittest.mock import patch

from cauldron.test import support
from cauldron.test.support import scaffolds


class TestReload(scaffolds.ResultsTest):
    """ """

    def test_reload(self):
        """ should reload the currently opened project """
        support.run_command('open @examples:hello_cauldron')
        r = support.run_command('reload')
        self.assertFalse(r.failed, 'should not have failed')

    def test_no_open_project(self):
        """ should fail when no project is open """
        r = support.run_command('reload')
        self.assertTrue(r.failed, 'should have failed')
        self.assertEqual(r.errors[0].code, 'NO_PROJECT_FOUND')

    @patch('time.sleep')
    def test_missing_project_path(self, *args):
        """ should fail if the project directory does not exist """
        support.run_command('open @examples:hello_cauldron')

        with patch('os.path.exists') as path_exists:
            path_exists.return_value = False
            r = support.run_command('reload')

        self.assertTrue(r.failed, 'should have failed')
        self.assertEqual(r.errors[0].code, 'MISSING_PROJECT_PATH')

    @patch('time.sleep')
    def test_initialize_failure(self, *args):
        """ should fail if cannot initialize project """
        support.run_command('open @examples:hello_cauldron')

        with patch('cauldron.runner.initialize') as runner_initialize:
            runner_initialize.side_effect = FileNotFoundError('Fake Error')
            r = support.run_command('reload')

        self.assertTrue(r.failed, 'should have failed')
        self.assertEqual(r.errors[0].code, 'PROJECT_INIT_FAILURE')

    def test_reload_remote(self):
        """ should reload the currently opened project """
        support.run_command('open @examples:hello_cauldron')
        r = support.run_remote_command('reload')
        self.assertFalse(r.failed, 'should not have failed')
