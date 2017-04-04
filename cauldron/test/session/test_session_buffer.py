import sys

from cauldron.session import buffering
from cauldron.test.support import scaffolds


class TestSessionBuffer(scaffolds.ResultsTest):

    def test_buffer_write(self):
        value = 'This is a test'
        b = buffering.RedirectBuffer(sys.stdout)
        b.active = True
        sys.stdout = b

        # This print statement is needed for this test
        print(value)

        sys.stdout = b.redirection_source

        contents = b.flush_all().strip()
        self.assertEqual(contents, value)
