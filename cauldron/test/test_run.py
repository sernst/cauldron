import unittest

from cauldron import environ
from cauldron.cli import commander
from cauldron.test import scaffolds


class TestRun(scaffolds.ResultsTest):

    def test_run_example(self):
        """
        """

        commander.execute('open', '@examples:hello_cauldron')

        r = environ.Response()
        commander.execute('run', '', r)

        self.assertFalse(r.failed)


################################################################################
################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRun)
    unittest.TextTestRunner(verbosity=2).run(suite)





