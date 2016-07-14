from cauldron.test import support
from cauldron.test.support import scaffolds


class TestStatus(scaffolds.ResultsTest):
    """

    """

    def test_status_fail(self):
        """
        """

        r = support.run_command('status')
        self.assertTrue(r.failed, 'should have failed without open project')

    def test_status(self):
        """
        """

        support.run_command('open @examples:seaborn')
        r = support.run_command('status')
        self.assertFalse(r.failed, 'should not have failed')

        support.run_command('close')

    def test_status_with_data(self):
        """
        """

        support.run_command('open @examples:hello_text')
        r = support.run_command('run')
        r = support.run_command('status')
        self.assertFalse(r.failed, 'should not have failed')

        support.run_command('close')
