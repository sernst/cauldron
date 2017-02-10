import os

from cauldron.test import support
from cauldron.test.support import scaffolds


class TestAlias(scaffolds.ResultsTest):
    """ """

    def test_unknown_command(self):
        """ should fail if the command is not recognized """

        r = support.run_command('alias fake')
        self.assertTrue(r.failed, 'should have failed')
        self.assertEqual(r.errors[0].code, 'UNKNOWN_COMMAND')

    def test_list(self):
        """ """

        r = support.run_command('alias list')
        self.assertFalse(r.failed, 'should not have failed')

    def test_add(self):
        """ """

        p = self.get_temp_path('aliaser')
        r = support.run_command('alias add test "{}" --temporary'.format(p))
        self.assertFalse(r.failed, 'should not have failed')

    def test_remove(self):
        """ """

        directory = self.get_temp_path('aliaser')
        path = os.path.join(directory, 'test.text')
        with open(path, 'w+') as f:
            f.write('This is a test')

        support.run_command('alias add test "{}" --temporary'.format(path))
        r = support.run_command('alias remove test --temporary')
        self.assertFalse(r.failed, 'should not have failed')
        self.assertFalse(r.failed, 'should not have failed')

    def test_empty(self):
        """ """

        r = support.run_command('alias add')
        self.assertTrue(r.failed, 'should have failed')
        self.assertEqual(r.errors[0].code, 'MISSING_ARG')

    def test_autocomplete_command(self):
        """ """

        result = support.autocomplete('alias ad')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 'add')

    def test_autocomplete_alias(self):
        """ """

        result = support.autocomplete('alias add fake-alias-not-real')
        self.assertEqual(len(result), 0)

    def test_autocomplete_path(self):
        """ """

        path = os.path.dirname(os.path.realpath(__file__))
        result = support.autocomplete('alias add test {}'.format(path))
        self.assertIsNotNone(result)
