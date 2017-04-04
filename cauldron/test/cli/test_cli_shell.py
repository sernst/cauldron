import os
from unittest.mock import patch
from unittest.mock import MagicMock

from cauldron.environ import modes
from cauldron.environ.response import Response
from cauldron.cli import shell
from cauldron.test import support
from cauldron.test.support import scaffolds


class TestCliShell(scaffolds.ResultsTest):
    """ """

    def test_default_empty_line(self):
        """ should abort when an empty line is supplied """

        cmd = shell.CauldronShell()
        cmd.default('    ')

        # Won't be added to the command history if aborted
        self.assertEqual(len(cmd.history), 0)

    @patch('cauldron.cli.commander.show_help')
    def test_default_show_help(self, show_help: MagicMock):
        """ should show help if help command called """

        cmd = shell.CauldronShell()
        cmd.default('help')

        show_help.assert_called_once_with()

    @patch('cauldron.cli.commander.execute')
    def test_default_message_response(self, execute: MagicMock):
        """ should handle ResponseMessage returned from commander.execute """

        r = Response()
        execute.return_value = r.notify()

        cmd = shell.CauldronShell()
        cmd.default('run something')

        self.assertEqual(cmd.last_response, r)

    @patch('cauldron.cli.commander.execute')
    def test_default_none_response(self, execute: MagicMock):
        """ should handle None response returned from commander.execute """

        execute.return_value = None

        cmd = shell.CauldronShell()
        cmd.default('run something')

        self.assertIsNotNone(cmd.last_response)

    @patch('cauldron.cli.commander.show_help')
    def test_do_help(self, show_help: MagicMock):
        """ should show help if do_help command called """

        arg = 'this is my arg'
        cmd = shell.CauldronShell()
        cmd.do_help(arg)

        show_help.assert_called_once_with(arg)

    def test_completenames(self):
        """ should autocomplete names """

        cmd = shell.CauldronShell()
        results = cmd.completenames('ru')
        self.assertIn('run', results)

    @patch('cmd.Cmd.cmdloop')
    def test_command_loop(self, parent_cmdloop: MagicMock):
        """ should start the command loop """

        intro_arg = 'This is my intro'
        cmd = shell.CauldronShell()
        cmd.cmdloop(intro=intro_arg)

        parent_cmdloop.assert_called_once_with(intro=intro_arg)
        self.assertFalse(modes.has(modes.INTERACTIVE))
