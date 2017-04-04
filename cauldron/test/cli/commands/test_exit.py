from cauldron.test import support
from cauldron.test.support import scaffolds


class TestExit(scaffolds.ResultsTest):
    """

    """

    def test_exit(self):
        """
        """

        r = support.run_command('exit')
        self.assertTrue(r.ended, 'should have ended')
        self.assertFalse(r.failed, 'should not have failed')


