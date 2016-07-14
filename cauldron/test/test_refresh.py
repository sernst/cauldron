from cauldron.test import support
from cauldron.test.support import scaffolds


class TestRefresh(scaffolds.ResultsTest):
    """

    """

    def test_refresh(self):
        """
        """

        r = support.run_command('open @examples:hello_cauldron')
        r = support.run_command('refresh')
        self.assertFalse(r.failed, 'should not have failed')
        support.run_command('close')

