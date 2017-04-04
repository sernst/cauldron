from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.cli.commands.open import actions as open_actions
from cauldron.environ.response import Response
from cauldron.test.support import scaffolds


class TestOpenActions(scaffolds.ResultsTest):
    """ """

    @patch('cauldron.environ.configs.fetch')
    def test_no_last(self, configs_fetch: MagicMock):
        """ should fail if no last project exist """

        configs_fetch.return_value = []

        r = Response()
        result = open_actions.fetch_last(r)
        self.assertTrue(r.failed, 'should have failed')
        self.assertIsNone(result)

    @patch('cauldron.environ.configs.fetch')
    def test_last(self, configs_fetch: MagicMock):
        """ should return the last project """

        configs_fetch.return_value = ['b', 'a', 'c']

        r = Response()
        result = open_actions.fetch_last(r)
        self.assertFalse(r.failed, 'should have failed')
        self.assertEqual(result, 'b')

    @patch('cauldron.environ.configs.fetch')
    def test_no_recent(self, configs_fetch: MagicMock):
        """ should fail if no recent projects exist """

        configs_fetch.return_value = []

        r = Response()
        result = open_actions.fetch_recent(r)
        self.assertTrue(r.failed, 'should have failed')
        self.assertIsNone(result)

    @patch('cauldron.environ.configs.fetch')
    @patch('cauldron.cli.interaction.query.choice')
    def test_cancel_recent(
            self,
            query_choice: MagicMock,
            configs_fetch: MagicMock
    ):
        """ should cancel if indicated by user query response """

        configs_fetch.return_value = ['a', 'b', 'c']
        query_choice.return_value = (3, None)

        r = Response()
        result = open_actions.fetch_recent(r)
        self.assertFalse(r.failed, 'should not have failed')
        self.assertIsNone(result)

    @patch('cauldron.environ.configs.fetch')
    @patch('cauldron.cli.interaction.query.choice')
    def test_recent_choice(
            self,
            query_choice: MagicMock,
            configs_fetch: MagicMock
    ):
        """ should return path chosen by user query response """

        configs_fetch.return_value = ['a', 'b', 'c']
        query_choice.return_value = (1, 'b')

        r = Response()
        result = open_actions.fetch_recent(r)
        self.assertFalse(r.failed, 'should not have failed')
        self.assertEqual(result, 'b')
