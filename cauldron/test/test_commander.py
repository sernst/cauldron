import os
import unittest
from unittest import mock

from cauldron import environ
from cauldron.cli import commander
from cauldron.environ import Response


class TestCommander(unittest.TestCase):

    def test_fetch(self):
        """
        """

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
        """

        :return:
        """

        target = 'cauldron.environ.response.ResponseMessage.console'
        with mock.patch(target) as console_func:
            r = Response()
            environ.output = r
            commander.print_module_help()
            self.assertEqual(1, console_func.call_count)




