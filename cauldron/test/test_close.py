from cauldron.test import support
from cauldron.test.support import scaffolds


class TestClose(scaffolds.ResultsTest):
    """

    """

    def test_reload(self):
        """
        """

        r = support.run_command('open @examples:hello_cauldron')
        r = support.run_command('close')
        self.assertFalse(r.failed, 'should not have failed')



