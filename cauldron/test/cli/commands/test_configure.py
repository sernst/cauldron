from cauldron.test import support
from cauldron.test.support.messages import Message
from cauldron.test.support import scaffolds


class TestConfigure(scaffolds.ResultsTest):
    """..."""

    def test_list_all(self):
        """Should list configurations."""

        response = support.run_command('configure --list')
        self.assertFalse(response.failed, Message(
            'Failed To List Configurations'
            'should not have failed',
            response=response
        ))

    def test_print_help(self):
        """Should print configure help."""

        r = support.run_command('configure')
        self.assertFalse(r.failed, 'should not have failed')

    def test_echo_missing(self):
        """Should echo does not exist setting """

        r = support.run_command('configure __test__')
        self.assertFalse(r.failed, 'should not have failed')

    def test_echo_exists(self):
        """Should echo does not exist setting """

        r = support.run_command('configure __test__ hello --forget')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('configure __test__')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('configure __test__ --remove')
        self.assertFalse(r.failed, 'should not have failed')

    def test_set_forget(self):
        """Should echo does not exist setting """

        r = support.run_command('configure __test__ abc --forget')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('configure __test__ --remove')
        self.assertFalse(r.failed, 'should not have failed')

    def test_set_persists(self):
        """Should echo does not exist setting """

        r = support.run_command('configure __test__ abc')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('configure __test__ --remove')
        self.assertFalse(r.failed, 'should not have failed')

    def test_set_path(self):
        """Should set a cleaned path"""

        r = support.run_command('configure __test_path ~/abc --forget')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('configure __test_path --remove')
        self.assertFalse(r.failed, 'should not have failed')

    def test_set_paths(self):
        """Should set multiple clean paths."""

        r = support.run_command('configure __test_paths ~/abc ~/def --forget')
        self.assertFalse(r.failed, 'should not have failed')

        r = support.run_command('configure __test_paths --remove')
        self.assertFalse(r.failed, 'should not have failed')
