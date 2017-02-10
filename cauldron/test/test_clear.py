from cauldron.test import support
from cauldron.test.support import scaffolds


class TestClear(scaffolds.ResultsTest):
    """ """

    def test_clear(self):
        """
        """

        r = support.run_command('open @examples:hello_cauldron')
        r = support.run_command('clear')
        self.assertFalse(r.failed, 'should not have failed')
        support.run_command('close')

    def test_no_project(self):
        """
        """

        r = support.run_command('clear')
        self.assertTrue(r.failed, 'should not have failed')
        self.assertEqual(r.errors[0].code, 'NO_OPEN_PROJECT')

