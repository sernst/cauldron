import unittest

from cauldron import environ
from cauldron.cli import commander
from cauldron.test import scaffolds


class TestOpen(scaffolds.ResultsTest):

    def test_open_example(self):
        """
        """

        r = environ.Response()
        commander.execute('open', '@examples:hello_cauldron', r)
        self.assertFalse(r.failed, 'should have opened successfully')
        self.assertIn(
            'project', r.data,
            'missing project data from response'
        )
        self.assertEqual(
            len(r.messages), 1,
            'success response message?'
        )




################################################################################
################################################################################

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOpen)
    unittest.TextTestRunner(verbosity=2).run(suite)




