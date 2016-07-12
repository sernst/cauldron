import os
import unittest

from cauldron.test import scaffolds
from cauldron.cli import commander
from cauldron import environ


class TestCreate(scaffolds.ResultsTest):

    def test_create_no_args(self):
        """
        """

        r = environ.Response()
        commander.execute('create', '', r)

        self.assertTrue(r.failed, 'should have failed')

    def test_create_simple_success(self):
        """
        """

        name = 'test_create'
        path = self.get_temp_path('project')

        r = environ.Response()
        args = [name, path]
        commander.execute('create', ' '.join(args), r)

        self.assertFalse(r.failed, 'create command failed')
        self.assertTrue(
            os.path.exists(os.path.join(path, name, 'cauldron.json')),
            'no cauldron.json found'
        )

################################################################################
################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCreate)
    unittest.TextTestRunner(verbosity=2).run(suite)




