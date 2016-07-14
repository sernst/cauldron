from cauldron.test import support
from cauldron.test.support import scaffolds


class TestVersion(scaffolds.ResultsTest):
    """

    """

    def test_version(self):
        """
        """

        r = support.run_command('version')
        self.assertFalse(r.failed, 'should not have failed')
