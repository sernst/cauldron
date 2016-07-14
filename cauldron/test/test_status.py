from cauldron.test import support
from cauldron.test.support import scaffolds


class TestStatus(scaffolds.ResultsTest):
    """

    """

    def test_status(self):
        """
        """

        r = support.run_command('status')
        self.assertFalse(r.failed, 'should not have failed')

