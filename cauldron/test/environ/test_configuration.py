import unittest
from unittest.mock import patch
from unittest.mock import mock_open

from cauldron.environ.configuration import Configuration


class TestConfiguration(unittest.TestCase):

    def test_no_such_path(self):
        """ should assign empty dictionary if path does not exist """
        c = Configuration()
        c.load('~/fake_path')
        self.assertIsInstance(c._persistent, dict)
        self.assertEqual(len(list(c._persistent.keys())), 0)

    def test_invalid_config_file(self):
        c = Configuration()

        invalid = '{ a: "hello" }'
        with patch('__main__.open', mock_open(read_data=invalid)) as m:
            c.load(__file__)

        self.assertEqual(c._persistent, c.NO_VALUE)
