from collections import OrderedDict
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.cli.commands import version


class TestVersion(scaffolds.ResultsTest):
    """ """

    def test_version(self):
        """ should retrieve version info """

        r = support.run_command('version')
        self.assertFalse(r.failed, 'should not have failed')

    def test_version_args(self):
        """ should retrieve version info with additional args """

        r = support.run_command('version --verbose --json')
        self.assertFalse(r.failed, 'should not have failed')

    def test_pretty_print(self):
        """ should pretty print the source dictionary """

        data = dict(
            a=[False, 1, 'two', 3.000001, dict(a=1, b='tester')],
            b=OrderedDict(a=12, b='hello'),
            c=dict(a=1, b=2, c=3)
        )

        result = version.pretty_print(data)
        self.assertTrue(len(result))
        self.assertGreater(result.find('hello'), 0)
        self.assertGreater(result.find('two'), 0)
        self.assertGreater(result.find('tester'), 0)

    def test_version_remote(self):
        """ should retrieve version info """

        r = support.run_remote_command('version')
        self.assertFalse(r.failed, 'should not have failed')
