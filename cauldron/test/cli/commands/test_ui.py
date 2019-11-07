from unittest.mock import MagicMock
from unittest.mock import patch

from pytest import mark

from cauldron.test import support


@patch('cauldron.cli.commands.ui.ui.start')
def test_ui(ui_start: MagicMock):
    """Should retrieve version info."""
    response = support.run_command('ui')
    assert response.success, 'Expect command to succeed.'
    assert 1 == ui_start.call_count, 'Expect ui to be started.'


AUTOCOMPLETE_SCENARIOS = [
    ('ui --p', {'port', 'public'}),
    ('ui foo', set()),
    ('ui -', {'p', 'n', '-'}),
]


@mark.parametrize('command, expected', AUTOCOMPLETE_SCENARIOS)
def test_ui_autocomplete(command: str, expected: set):
    """Should return the expected autocomplete options."""
    results = support.autocomplete(command)
    assert expected == set(results)
