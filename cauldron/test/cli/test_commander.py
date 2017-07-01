import os
import builtins
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron import environ
from cauldron.cli import commander


class TestCommander(unittest.TestCase):
    """Test suite for the commander module"""

    def test_fetch(self):
        """Should fetch the command"""

        commands_directory = environ.paths.package('cli', 'commands')
        items = [x for x in os.listdir(commands_directory) if x[0] != '_']
        command_count = len(items)

        commands = commander.fetch()

        self.assertEqual(
            len(list(commands.keys())),
            command_count,
            'The number of commands does not match the expected value'
        )

        commands_again = commander.fetch()
        self.assertEqual(
            commands, commands_again,
            'Command dictionaries should be the same'
        )

    def test_print_module_help(self):
        """Should print help for the specified module"""

        target = 'cauldron.environ.response.ResponseMessage.console'
        with patch(target) as console_func:
            r = commander.print_module_help()
            self.assertEqual(1, console_func.call_count)

    def test_execute_invalid(self):
        """Should fail when executing an unknown module"""

        result = commander.execute('fake-module', '')
        self.assertTrue(result.failed)

    def test_show_help_invalid(self):
        """Should show help when an unknown command module is specified"""

        result = commander.show_help('fake-module')
        self.assertTrue(result.failed)

    def test_show_help(self):
        """Should show the help display"""

        result = commander.show_help('open')
        self.assertFalse(result.failed)

    @patch('matplotlib.use')
    def test_preload_fail_matplotlib(self, use: MagicMock):
        """Should preload even if matplotlib fails"""
        use.side_effect = ValueError('Fake')
        commander.preload()

    def test_preload_fail_plotly(self, ):
        """Should preload even if plotly is not available"""

        real_import = builtins.__import__

        def fake_import(*args, **kwargs):
            if args and args[0].startswith('plotly'):
                raise ImportError('Fake Error')
            return real_import(*args, **kwargs)

        with patch('builtins.__import__') as import_func:
            import_func.side_effect = fake_import
            commander.preload()

    def test_autocomplete_unknown(self):
        """Should return no autocompletes for an unknown command"""

        result = commander.autocomplete('fake', '', '', 0, 0)
        self.assertIsInstance(result, list)
        self.assertEqual(0, len(result))

    @patch('cauldron.cli.commands.run.autocomplete')
    def test_autocomplete_error(self, run_autocomplete: MagicMock):
        """Should return empty even if the autocomplete encounters an error"""

        run_autocomplete.side_effect = ValueError('Fake')

        result = commander.autocomplete('run', '', '', 0, 0)
        self.assertIsInstance(result, list)
        self.assertEqual(0, len(result))

    def test_execute_help(self):
        """Should show help and return"""
        response = commander.execute('run', '--help')
        self.assertTrue(response.success)
