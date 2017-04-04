import unittest

from cauldron.cli import parse


class TestCliCommands(unittest.TestCase):

    def test_explode_line(self):
        """
        """

        src = 'run "my name" --force --help --test 1'
        parts = parse.explode_line(src)

        self.assertEqual(len(parts), 6)





