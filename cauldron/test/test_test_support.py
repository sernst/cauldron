import unittest

from cauldron.environ import Response
from cauldron.test.support import messages


class TestTestSupport(unittest.TestCase):

    def test_explode_line(self):
        """
        """

        r = Response('TEST').update(
            test_info='More test information'
        )

        m = messages.Message(
            'Some-Message',
            'This is a test',
            'Message that will be turned into a string',
            response=r
        )

        m = str(m)
        self.assertGreater(len(m), 0, messages.Message(
            'Message to String',
            'Unable to convert message to string'
        ))






