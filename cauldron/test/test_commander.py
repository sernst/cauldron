import unittest

import os
from cauldron.cli import commander
from cauldron import environ


class TestCommander(unittest.TestCase):

    def test_fetch(self):
        """
        """

        commands_directory = environ.paths.package(
            'cauldron', 'cli', 'commands'
        )
        items = [x for x in os.listdir(commands_directory) if x[0] != '_']
        command_count = len(items)

        commands = commander.fetch()

        self.assertEqual(
            len(list(commands.keys())),
            command_count,
            'The number of commands does not match the expected value'
        )

        commands_again = commander.fetch()
        self.assertEqual(commands, commands_again)


################################################################################
################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCommander)
    unittest.TextTestRunner(verbosity=2).run(suite)




