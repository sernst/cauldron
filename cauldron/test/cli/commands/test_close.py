import cauldron
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestClose(scaffolds.ResultsTest):
    """Test suite for the close CLI command"""

    def test_close_open_project(self):
        """Should close open project"""
        support.run_command('open @examples:hello_cauldron')
        response = support.run_command('close')
        self.assertTrue(response.success, 'should not have failed')
        self.assertIsNone(cauldron.project.get_internal_project())

    def test_no_open_project(self):
        """Should not close when no project is open"""
        response = support.run_command('close')
        self.assert_has_success_code(response, 'NO_OPEN_PROJECT')

    def test_remote(self):
        """Should not close remotely when no project is open"""
        response = support.run_remote_command('close')
        self.assert_has_success_code(response, 'NO_OPEN_PROJECT')
