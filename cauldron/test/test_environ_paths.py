import os

from cauldron.environ import paths
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestEnvironPaths(scaffolds.ResultsTest):
    """ """

    def test_clean_current_directory(self):
        """ should clean path to be current directory """

        directory = os.path.realpath(os.path.abspath(os.curdir))
        self.assertEqual(paths.clean(None), directory)
        self.assertEqual(paths.clean('.'), directory)
