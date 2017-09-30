from cauldron.test import support
from cauldron.test.support import scaffolds


class TestClear(scaffolds.ResultsTest):
    """ """

    def test_clear(self):
        """ should clear variables successfully """

        support.run_command('open @examples:hello_cauldron')
        response = support.run_command('clear')
        self.assertFalse(response.failed, 'should not have failed')

    def test_no_project(self):
        """ should error when no project is open """

        response = support.run_command('clear')
        self.assertTrue(response.failed, 'should not have failed')
        self.assert_has_error_code(response, 'NO_OPEN_PROJECT')

    def test_remote(self):
        """ should error when no remote project is open """

        response = support.run_remote_command('clear')
        self.assert_has_error_code(response, 'NO_OPEN_PROJECT')
