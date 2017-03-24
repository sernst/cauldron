from cauldron.test import support
from cauldron.test.support import scaffolds


class TestClose(scaffolds.ResultsTest):
    """ """

    def test_close_open_project(self):
        """ """

        support.run_command('open @examples:hello_cauldron')
        response = support.run_command('close')
        self.assertFalse(response.failed, 'should not have failed')

    def test_no_open_project(self):
        """ """
        response = support.run_command('close')
        self.assert_has_success_code(response, 'NO_OPEN_PROJECT')

    def test_remote(self):
        """ """

        response = support.run_remote_command('close')
        self.assert_has_success_code(response, 'NO_OPEN_PROJECT')
