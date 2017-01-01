import os
import sys

from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.session import buffering


class TestSessionBuffer(scaffolds.ResultsTest):

    def test_buffer_write(self):
        value = 'This is a test'
        b = buffering.RedirectBuffer(sys.stdout)
        sys.stdout = b
        print(value)
        sys.stdout = b.redirection_source

        contents = b.flush_all().strip()
        self.assertEqual(contents, value)
