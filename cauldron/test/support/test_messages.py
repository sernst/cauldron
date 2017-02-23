import os

from cauldron.environ.response import Response
from cauldron.test import support
from cauldron.test.support import scaffolds
from cauldron.test.support import messages


class TestMessages(scaffolds.ResultsTest):
    """ """

    def test_message(self):
        """ should echo message when printed """

        r = Response()
        m = messages.Message(
            'MESSAGE',
            'Test message',
            'with multiple args',
            data=dict(
                a=[1,2,3],
                b=True
            ),
            response=r
        )

        self.assertEqual(m.echo(), str(m))
