from cauldron.test import support
from cauldron.test.support import scaffolds


class TestPurge(scaffolds.ResultsTest):
    """

    """

    def test_purge(self):
        """
        """

        r = support.run_command('purge --force')
        self.assertFalse(r.failed, 'should not have failed')
