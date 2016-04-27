import unittest

from cauldron.cli import commands


class TestCliCommands(unittest.TestCase):

    def test_explode_line(self):
        """
        """

        src = 'run "my name" --force --help --test 1'
        parts = commands.explode_line(src)

        print(src)
        print(parts)
        self.assertEqual(len(parts), 6)

################################################################################
################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCliCommands)
    unittest.TextTestRunner(verbosity=2).run(suite)




