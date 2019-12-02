import os
from unittest.mock import MagicMock
from unittest.mock import patch

from cauldron.cli.commands.open import actions as open_actions
from cauldron.environ.response import Response
from cauldron.test.support import scaffolds

MY_DIRECTORY = os.path.realpath(os.path.dirname(__file__))


class TestOpenActions(scaffolds.ResultsTest):
    """..."""

    @patch('cauldron.environ.configs.fetch')
    def test_no_last(self, configs_fetch: MagicMock):
        """Should fail if no last project exist."""

        configs_fetch.return_value = []

        r = Response()
        result = open_actions.fetch_last(r)
        self.assertTrue(r.failed, 'should have failed')
        self.assertIsNone(result)

    @patch('cauldron.environ.configs.fetch')
    def test_last(self, configs_fetch: MagicMock):
        """Should return the last project."""

        configs_fetch.return_value = ['b', 'a', 'c']

        r = Response()
        result = open_actions.fetch_last(r)
        self.assertFalse(r.failed, 'should have failed')
        self.assertEqual(result, 'b')

    @patch('cauldron.environ.configs.fetch')
    def test_no_recent(self, configs_fetch: MagicMock):
        """Should fail if no recent projects exist."""

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
        """Should cancel if indicated by user query response."""

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
        """Should return path chosen by user query response."""

        configs_fetch.return_value = ['a', 'b', 'c']
        query_choice.return_value = (1, 'b')

        r = Response()
        result = open_actions.fetch_recent(r)
        self.assertFalse(r.failed, 'should not have failed')
        self.assertEqual(result, 'b')


def test_fetch_location_home():
    """Should return a home path."""
    result = open_actions.fetch_location('@home:foo/bar')
    assert result.endswith('foo{}bar'.format(os.path.sep))


@patch('cauldron.cli.commands.open.actions.environ.configs.fetch')
def test_fetch_location_alias(fetch: MagicMock):
    """Should return an alias-based path."""
    fetch.return_value = {'foo': {'path': MY_DIRECTORY}}
    result = open_actions.fetch_location('@foo:bar')
    assert os.path.join(MY_DIRECTORY, 'bar') == result


@patch('cauldron.cli.commands.open.actions.environ.configs.fetch')
def test_fetch_location_none(fetch: MagicMock):
    """Should return None if unable to convert location into a path."""
    fetch.return_value = {'bar': {'path': MY_DIRECTORY}}
    result = open_actions.fetch_location('@foo:bar')
    assert result is None


@patch('cauldron.cli.commands.open.actions.discovery.echo_known_projects')
def test_select_from_available(
    echo_known_projects: MagicMock,
):
    """Should select from available projects."""
    response = Response().update(specs=[
        {'directory': {'absolute': 'foo'}}
    ])

    with patch('builtins.input', return_value='1'):
        result = open_actions.select_from_available(response)

    assert 'foo' == result
    assert echo_known_projects.called


@patch('cauldron.cli.commands.open.actions.discovery.echo_known_projects')
def test_select_from_available_failed(
    echo_known_projects: MagicMock,
):
    """Should fail to select when selection is out of range."""
    response = Response().update(specs=[
        {'directory': {'absolute': 'foo'}}
    ])

    with patch('builtins.input', return_value='100'):
        result = open_actions.select_from_available(response)

    assert result is None
    assert echo_known_projects.called
