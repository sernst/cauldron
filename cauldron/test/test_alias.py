import os

from cauldron.test import support
from cauldron.test.support import scaffolds


class TestAlias(scaffolds.ResultsTest):
    """

    """

    def test_list(self):
        """
        """

        r = support.run_command('alias list')
        self.assertFalse(r.failed, 'should not have failed')

    def test_add(self):
        """
        """

        p = self.get_temp_path('aliaser')
        r = support.run_command('alias add test "{}" --temporary'.format(p))
        self.assertFalse(r.failed, 'should not have failed')

    def test_remove(self):
        """
        """

        directory = self.get_temp_path('aliaser')
        path = os.path.join(directory, 'test.text')
        with open(path, 'w+') as f:
            f.write('This is a test')

        support.run_command('alias add test "{}" --temporary'.format(path))
        r = support.run_command('alias remove test')
        self.assertFalse(r.failed, 'should not have failed')

